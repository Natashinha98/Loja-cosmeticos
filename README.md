# Sistema de Gerenciamento de Loja de Cosmeticos virtual

---

## 1. Tema 

O tema é um **Sistema de Gerenciamento de Loja de Cosmeticos virtual**. O sistema permite gerenciar clientes, produtos e pedidos por meio de uma API REST com interface web.

A aplicação segue a arquitetura exigida:

```
Frontend (HTML + JS)
       ↕
   Backend (FastAPI)
    ↙    ↓    ↘
Postgres  MongoDB  Redis
(RDB)    (DB1)   (DB2)
```

- **Frontend** : interface web para criar, visualizar, editar e remover clientes, produtos e pedidos
- **Backend** : API REST em FastAPI com três módulos de rotas independentes: `/clientes`, `/produtos` e `/pedidos`
- **RDB (PostgreSQL)** : banco relacional para clientes e pedidos
- **DB1 (MongoDB)** : banco de documentos para o catálogo de produtos
- **DB2 (Redis)** : banco chave-valor para cache da listagem de produtos

---

## 2. Justificativa dos bancos e implementação do backend

### PostgreSQL (RDB)

**O que armazena:** clientes e pedidos.

Clientes têm estrutura bem definida e estável. Pedidos, por sua vez, têm uma relação direta com clientes todo pedido pertence a um cliente cadastrado o que torna o modelo relacional a escolha natural para garantir integridade dos dados.

Além disso, pedidos e clientes são entidades críticas para o negócio: consistência e transações ACID são essenciais para evitar dados corrompidos (ex: pedido criado para um cliente inexistente).

### MongoDB (DB1)

**O que armazena:** catálogo de produtos.

Produtos de cosméticos têm características que variam bastante por categoria: um batom tem "tom" e "acabamento", um hidratante tem "tipo de pele" e "fragrância", uma máscara de cílios tem "tipo de escova". Um esquema rígido de tabela relacional exigiria muitas colunas opcionais ou tabelas auxiliares para cobrir essa variação.

O MongoDB armazena cada produto como um documento JSON flexível, permitindo que cada categoria tenha seus próprios campos sem alterar o esquema do banco. Isso torna o cadastro de novos tipos de produtos muito mais simples e adaptável.

### Redis (DB2)

**O que armazena:** cache da listagem de produtos.

A listagem de produtos (`GET /produtos`) é a operação mais consultada da loja toda vez que um cliente abre a página, ela é chamada. Consultar o MongoDB a cada requisição gera latência desnecessária, especialmente com catálogos grandes.

O Redis armazena o resultado da listagem completa sob a chave `lista_produtos` com expiração de 60 segundos. Quando a cache está válida, a resposta é instantânea. Quando um produto é criado, editado ou removido, a chave é invalidada e a próxima consulta atualiza o cache automaticamente. O modelo chave-valor do Redis é perfeito para esse padrão de cache: simples, extremamente rápido e com suporte nativo a TTL (tempo de expiração).

###  Implementação do Backend

O backend é implementado em **FastAPI** com três módulos de rotas independentes:

| Módulo | Arquivo | Banco(s) usado(s) |
|---|---|---|
| Clientes | `app/rotas/clientes.py` | PostgreSQL |
| Produtos | `app/rotas/produtos.py` | MongoDB + Redis |
| Pedidos | `app/rotas/pedidos.py` | PostgreSQL + MongoDB |

O módulo de pedidos cruza os dois bancos: valida o cliente no PostgreSQL e busca os dados de cada produto no MongoDB para montar o pedido (calculando subtotais e total), salvando o resultado no PostgreSQL.

---

## 3. Como executar o projeto
**É necessario ter Docker Desktop instalado na maquina.**
O projeto roda via **GitHub Codespaces** 

### Passo a passo

**1. Abra o repositório no Codespace pelo GitHub.**

**2. No terminal do Codespace, rode:**

```bash
docker compose up --build
```

**3. Na primeira execução o backend vai falhar** enquanto aguarda os bancos subirem. Isso é esperado. Quando isso acontecer:

- Pressione `Ctrl + C` para parar
- Rode novamente:

```bash
docker compose up --build
```

Na segunda vez todos os serviços já estarão prontos e a aplicação vai iniciar corretamente.

**4. Abra a aba "Portas" no Codespace** (ao lado do terminal), localize a porta `8000`, clique com o botão direito e defina a visibilidade como **Pública**.

**5. Clique no ícone de abrir no navegador** ao lado da porta `8000` para acessar a loja.

> Na primeira execução, o sistema popula automaticamente o MongoDB com 3 produtos de exemplo para que a loja já tenha dados visíveis.

### Serviços e portas

| Container | Tecnologia | Porta exposta |
|---|---|---|
| `loja_backend` | FastAPI + Python 3.12 | `8000` |
| `banco_postgres_loja` | PostgreSQL 16 | `5432` |
| `banco_mongo_loja` | MongoDB 7 | `27017` |
| `banco_redis_loja` | Redis 7 | `6379` |

Os dados são persistidos em volumes Docker e sobrevivem a reinicializações.

---

## Endpoints disponíveis

### Clientes 
| Método | Rota | Ação |
|---|---|---|
| `POST` | `/clientes/` | Cadastrar cliente |
| `GET` | `/clientes/` | Listar clientes |
| `PUT` | `/clientes/{id}` | Editar cliente |
| `DELETE` | `/clientes/{id}` | Remover cliente |

### Produtos 
| Método | Rota | Ação |
|---|---|---|
| `POST` | `/produtos/` | Cadastrar produto |
| `GET` | `/produtos/` | Listar produtos |
| `GET` | `/produtos/{id}` | Buscar produto por ID |
| `PUT` | `/produtos/{id}` | Editar produto |
| `DELETE` | `/produtos/{id}` | Remover produto |

### Pedidos 
| Método | Rota | Ação |
|---|---|---|
| `POST` | `/pedidos/` | Criar pedido |
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
│   │   ├── produtos.py       # CRUD de produtos (MongoDB + Redis)
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


