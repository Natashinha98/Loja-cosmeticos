# Sistema de Gerenciamento de Loja de Cosmeticos virtual

---

## 1. Tema 

O tema é um **Sistema de Gerenciamento de Loja de Cosmeticos virtual**. O sistema permite gerenciar clientes, produtos, carrinhos de compra e pedidos por meio de uma API REST com interface web.

A aplicação segue a arquitetura exigida:

```
Frontend (HTML + JS)
       ↕
   Backend (FastAPI)
    ↙    ↓    ↘
Postgres  MongoDB  Redis
(RDB)    (DB1)   (DB2)
```

- **Frontend** : interface web para criar, visualizar, editar e remover clientes, produtos, carrinhos e pedidos
- **Backend** : API REST em FastAPI com quatro módulos de rotas independentes: `/clientes`, `/produtos`, `/carrinho` e `/pedidos`
- **RDB (PostgreSQL)** : banco relacional para clientes e pedidos
- **DB1 (MongoDB)** : banco de documentos para o catálogo de produtos
- **DB2 (Redis)** : banco chave-valor para carrinhos de compra dos clientes e cache da listagem de produtos

---

## 2. Justificativa dos bancos e implementação do backend

### PostgreSQL (RDB)

**O que armazena:** clientes e pedidos.

Clientes têm estrutura bem definida e estável. Pedidos, por sua vez, têm uma relação direta com clientes  todo pedido pertence a um cliente cadastrado  o que torna o modelo relacional a escolha natural para garantir integridade dos dados.

Além disso, pedidos e clientes são entidades críticas para o negócio: consistência e transações ACID são essenciais para evitar dados corrompidos (ex: pedido criado para um cliente inexistente). A tabela de pedidos possui uma chave estrangeira (`ForeignKey`) para a tabela de clientes, reforçando a integridade referencial no próprio banco relacional.

### MongoDB (DB1)

**O que armazena:** catálogo de produtos.

Produtos de cosméticos têm características que variam bastante por categoria: um batom tem "tom" e "acabamento", um hidratante tem "tipo de pele" e "fragrância", uma máscara de cílios tem "tipo de escova". Um esquema rígido de tabela relacional exigiria muitas colunas opcionais ou tabelas auxiliares para cobrir essa variação.

O MongoDB armazena cada produto como um documento JSON flexível, permitindo que cada categoria tenha seus próprios campos sem alterar o esquema do banco. Isso torna o cadastro de novos tipos de produtos muito mais simples e adaptável.

### Redis (DB2)

**O que armazena:** dois tipos de dado, ambos chave-valor:

1. **Carrinho de compras de cada cliente** (dado primário) — armazenado sob a chave `carrinho:{id_cliente}` com TTL de 30 minutos. O carrinho é a única fonte deste dado: enquanto não vira pedido, ele existe somente no Redis. O TTL nativo do Redis garante limpeza automática de carrinhos abandonados sem precisar de cron job ou processo de manutenção.

2. **Cache da listagem de produtos** (dado derivado) — armazenado sob a chave `lista_produtos` com TTL de 60 segundos. A operação `GET /produtos` é a mais consultada da loja; ao invés de buscar tudo do MongoDB a cada requisição, a resposta fica cacheada. Toda escrita de produto (POST, PUT, DELETE) invalida o cache para garantir que a próxima leitura traga dados atualizados.

O modelo chave-valor do Redis encaixa perfeitamente nos dois usos: estrutura simples, leitura e escrita em memória (latência sub-milissegundo) e suporte nativo a TTL.

### Implementação do Backend

O backend é implementado em **FastAPI** com quatro módulos de rotas independentes:

| Módulo | Arquivo | Banco(s) usado(s) |
|---|---|---|
| Clientes | `app/rotas/clientes.py` | PostgreSQL |
| Produtos | `app/rotas/produtos.py` | MongoDB + Redis (cache) |
| Carrinho | `app/rotas/carrinho.py` | Redis (primário) + MongoDB (consulta) |
| Pedidos | `app/rotas/pedidos.py` | PostgreSQL + MongoDB |

O módulo de carrinho usa o Redis como armazenamento primário (cada carrinho é uma chave independente com TTL) e consulta o MongoDB apenas para enriquecer a resposta com nome e preço atualizados de cada produto.

O módulo de pedidos cruza Postgres + Mongo: valida o cliente no PostgreSQL e busca os dados de cada produto no MongoDB para montar o pedido. A finalização de um carrinho (`POST /carrinho/{id_cliente}/finalizar`) lê o Redis, monta o pedido com os dados atuais do Mongo, salva no Postgres e apaga a chave do carrinho.

---

## 3. Como executar o projeto

O projeto roda via **GitHub Codespaces** (recomendado) ou localmente em qualquer máquina com Docker.

### Passo a passo (Codespaces)

**1. Abra o repositório no Codespace pelo GitHub.**

**2. No terminal do Codespace, rode:**

```bash
docker compose up --build
```

> O backend agora espera os bancos ficarem **saudáveis** antes de subir (via healthcheck do Postgres, Mongo e Redis). Diferente da versão anterior, **não é mais preciso rodar duas vezes** — a primeira execução já funciona corretamente.

**3. Abra a aba "Portas" no Codespace** (ao lado do terminal), localize a porta `8000`, clique com o botão direito e defina a visibilidade como **Pública**.

**4. Clique no ícone de abrir no navegador** ao lado da porta `8000` para acessar a loja.

> Na primeira execução, o sistema popula automaticamente o MongoDB com 3 produtos de exemplo para que a loja já tenha dados visíveis.

### Execução local (alternativa)

Se preferir rodar localmente, basta ter o Docker instalado (Docker Desktop no Windows/Mac, ou docker engine no Linux) e rodar `docker compose up --build` no diretório do projeto. A loja fica acessível em `http://localhost:8000`.

### Serviços e portas

| Container | Tecnologia | Porta exposta |
|---|---|---|
| `loja_backend` | FastAPI + Python 3.12 | `8000` |
| `banco_postgres_loja` | PostgreSQL 16 | `5432` |
| `banco_mongo_loja` | MongoDB 7 | `27017` |
| `banco_redis_loja` | Redis 7 | `6379` |

Os dados são persistidos em volumes Docker e sobrevivem a reinicializações (exceto carrinhos, que expiram em 30 minutos por TTL).

---

## Endpoints disponíveis

### Clientes 
| Método | Rota | Ação |
|---|---|---|
| `POST` | `/clientes/` | Cadastrar cliente |
| `GET` | `/clientes/` | Listar clientes |
| `PUT` | `/clientes/{id}` | Editar cliente |
| `DELETE` | `/clientes/{id}` | Remover cliente, desde que não possua pedidos vinculados |

### Produtos 
| Método | Rota | Ação |
|---|---|---|
| `POST` | `/produtos/` | Cadastrar produto |
| `GET` | `/produtos/` | Listar produtos (com cache Redis) |
| `GET` | `/produtos/{id}` | Buscar produto por ID |
| `PUT` | `/produtos/{id}` | Editar produto |
| `DELETE` | `/produtos/{id}` | Remover produto |

### Carrinho (Redis)
| Método | Rota | Ação |
|---|---|---|
| `GET` | `/carrinho/{id_cliente}` | Ver carrinho do cliente |
| `POST` | `/carrinho/{id_cliente}/itens` | Adicionar produto ao carrinho |
| `PUT` | `/carrinho/{id_cliente}/itens/{id_produto}` | Alterar quantidade |
| `DELETE` | `/carrinho/{id_cliente}/itens/{id_produto}` | Remover um item |
| `DELETE` | `/carrinho/{id_cliente}` | Esvaziar carrinho |
| `POST` | `/carrinho/{id_cliente}/finalizar` | Converter carrinho em pedido |

### Pedidos 
| Método | Rota | Ação |
|---|---|---|
| `POST` | `/pedidos/` | Criar pedido diretamente (sem passar pelo carrinho) |
| `GET` | `/pedidos/` | Listar pedidos |
| `PUT` | `/pedidos/{id}` | Editar pedido |
| `DELETE` | `/pedidos/{id}` | Remover pedido |

---

## Estrutura do projeto

```
Loja-cosmeticos/
├── app/
│   ├── bancos/
│   │   ├── postgres.py       # Conexão com PostgreSQL via SQLAlchemy
│   │   ├── mongo.py          # Conexão com MongoDB via PyMongo
│   │   └── redis_cache.py    # Conexão com Redis
│   ├── modelos/
│   │   ├── cliente.py        # Modelo ORM da tabela clientes
│   │   └── pedido.py         # Modelo ORM da tabela pedidos
│   ├── rotas/
│   │   ├── clientes.py       # CRUD de clientes (PostgreSQL)
│   │   ├── produtos.py       # CRUD de produtos (MongoDB + Redis cache)
│   │   ├── carrinho.py       # CRUD do carrinho (Redis primário + Mongo)
│   │   └── pedidos.py        # CRUD de pedidos (PostgreSQL + MongoDB)
│   ├── static/               # CSS, JS da interface
│   ├── templates/
│   │   └── index.html        # html da interface
│   └── principal.py          # Inicialização da aplicação

```
## Autores
> Natasha Trindade RA: 22.123.098-0
> 
> Douglas Honda RA: 22.123.006-3
