# Sistema de Gerenciamento de Loja de Cosméticos Virtual

---

## 1. Tema

O tema é um **Sistema de Gerenciamento de Loja de Cosméticos Virtual**. O sistema permite gerenciar clientes, produtos, carrinhos de compra e pedidos por meio de uma API REST com interface web.

A aplicação segue a arquitetura exigida:

```text
Frontend (HTML + JS)
       ↕
   Backend (FastAPI)
    ↙    ↓    ↘
PostgreSQL  MongoDB  Redis
  (RDB)     (DB1)    (DB2)
```

- **Frontend**: interface web para criar, visualizar, editar e remover clientes, produtos, carrinhos e pedidos.
- **Backend**: API REST em FastAPI com quatro módulos de rotas independentes: `/clientes`, `/produtos`, `/carrinho` e `/pedidos`.
- **RDB (PostgreSQL)**: banco relacional para clientes e pedidos.
- **DB1 (MongoDB)**: banco de documentos para o catálogo de produtos.
- **DB2 (Redis)**: banco chave-valor para carrinhos de compra dos clientes e cache da listagem de produtos.

---

## 2. Justificativa dos bancos e implementação do backend

### PostgreSQL (RDB)

**O que armazena:** clientes e pedidos.

Clientes têm estrutura bem definida e estável. Pedidos, por sua vez, têm uma relação direta com clientes: todo pedido pertence a um cliente cadastrado, o que torna o modelo relacional a escolha natural para garantir integridade dos dados.

Além disso, pedidos e clientes são entidades críticas para o negócio. Consistência e transações ACID são importantes para evitar dados corrompidos, como um pedido criado para um cliente inexistente. A tabela de pedidos possui uma chave estrangeira (`ForeignKey`) para a tabela de clientes, reforçando a integridade referencial no próprio banco relacional.

### MongoDB (DB1)

**O que armazena:** catálogo de produtos.

Produtos de cosméticos têm características que variam bastante por categoria. Um batom pode ter "tom" e "acabamento", um hidratante pode ter "tipo de pele" e "fragrância", e uma máscara de cílios pode ter "tipo de escova". Um esquema rígido de tabela relacional exigiria muitas colunas opcionais ou tabelas auxiliares para cobrir essa variação.

O MongoDB armazena cada produto como um documento JSON flexível, permitindo que cada categoria tenha seus próprios campos sem alterar o esquema do banco. Isso torna o cadastro de novos tipos de produtos mais simples e adaptável.

### Redis (DB2)

**O que armazena:** dois tipos de dado, ambos chave-valor:

1. **Carrinho de compras de cada cliente** (dado primário): armazenado sob a chave `carrinho:{id_cliente}` com TTL de 30 minutos. O carrinho é a única fonte deste dado: enquanto não vira pedido, ele existe somente no Redis. O TTL nativo do Redis garante limpeza automática de carrinhos abandonados sem precisar de cron job ou processo de manutenção.

2. **Cache da listagem de produtos** (dado derivado): armazenado sob a chave `lista_produtos` com TTL de 60 segundos. A operação `GET /produtos` é uma das mais consultadas da loja. Em vez de buscar todos os produtos do MongoDB a cada requisição, a resposta fica cacheada no Redis. Toda escrita de produto (`POST`, `PUT` e `DELETE`) invalida o cache para garantir que a próxima leitura traga dados atualizados.

O modelo chave-valor do Redis encaixa bem nos dois usos: estrutura simples, leitura e escrita rápidas em memória e suporte nativo a TTL.

### Implementação do Backend

O backend é implementado em **FastAPI** com quatro módulos de rotas independentes:

| Módulo | Arquivo | Banco(s) usado(s) |
|---|---|---|
| Clientes | `app/rotas/clientes.py` | PostgreSQL |
| Produtos | `app/rotas/produtos.py` | MongoDB + Redis (cache) |
| Carrinho | `app/rotas/carrinho.py` | Redis (primário) + MongoDB (consulta) |
| Pedidos | `app/rotas/pedidos.py` | PostgreSQL + MongoDB |

O módulo de carrinho usa o Redis como armazenamento primário. Cada carrinho é uma chave independente com TTL, e o MongoDB é consultado apenas para enriquecer a resposta com nome e preço atualizados de cada produto.

O módulo de pedidos cruza PostgreSQL e MongoDB: valida o cliente no PostgreSQL e busca os dados de cada produto no MongoDB para montar o pedido. A finalização de um carrinho (`POST /carrinho/{id_cliente}/finalizar`) lê o Redis, monta o pedido com os dados atuais do MongoDB, salva no PostgreSQL e apaga a chave do carrinho.

---

## 3. Como executar o projeto

O projeto pode ser executado pelo **GitHub Codespaces**, sem necessidade de instalar Docker localmente.

### Passo a passo

**1. Abra o repositório no GitHub Codespaces.**

No GitHub, acesse o repositório, clique em **Code**, depois em **Codespaces** e crie um novo Codespace.

**2. No terminal do Codespace, rode:**

```bash
docker compose up --build
```

**3. Aguarde os serviços iniciarem.**

O Docker irá subir os seguintes serviços:

- Backend FastAPI;
- PostgreSQL;
- MongoDB;
- Redis.

Caso algum serviço falhe na primeira execução, pare com `Ctrl + C` e rode novamente:

```bash
docker compose up --build
```

**4. Abra a aplicação.**

No Codespaces, acesse a aba **Ports**, localize a porta `8000` e clique no ícone de abrir no navegador.

A loja será carregada pelo backend FastAPI.

> Na primeira execução, o sistema popula automaticamente o MongoDB com produtos de exemplo para que a loja já tenha dados visíveis.

### Serviços e portas

| Container | Tecnologia | Porta exposta |
|---|---|---|
| `loja_backend` | FastAPI + Python 3.12 | `8000` |
| `banco_postgres_loja` | PostgreSQL 16 | `5432` |
| `banco_mongo_loja` | MongoDB 7 | `27017` |
| `banco_redis_loja` | Redis 7 | `6379` |

Os dados são persistidos em volumes Docker e sobrevivem a reinicializações, exceto carrinhos, que expiram em 30 minutos por TTL.

---

## 4. Endpoints disponíveis

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
| `GET` | `/produtos/` | Listar produtos com cache Redis |
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
| `POST` | `/pedidos/` | Criar pedido diretamente, sem passar pelo carrinho |
| `GET` | `/pedidos/` | Listar pedidos |
| `PUT` | `/pedidos/{id}` | Editar pedido |
| `DELETE` | `/pedidos/{id}` | Remover pedido |

---

## 5. Estrutura do projeto

```text
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
│   │   ├── carrinho.py       # CRUD do carrinho (Redis primário + MongoDB)
│   │   └── pedidos.py        # CRUD de pedidos (PostgreSQL + MongoDB)
│   ├── static/               # CSS e JS da interface
│   ├── templates/
│   │   └── index.html        # HTML da interface
│   └── principal.py          # Inicialização da aplicação
```

---

## Autores

- Natasha Trindade — RA: 22.123.098-0
- Douglas Honda — RA: 22.123.006-3
