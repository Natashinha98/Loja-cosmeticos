# Loja de Cosméticos - Projeto Polyglot Persistence

Este projeto é uma loja de cosméticos simples, feita em **Python com FastAPI**, usando três bancos de dados diferentes:

- **PostgreSQL**: banco relacional;
- **MongoDB**: banco NoSQL orientado a documentos;
- **Redis**: sistema de cache.

A ideia foi deixar o projeto o mais simples possível para rodar com Docker, sem precisar instalar PostgreSQL, MongoDB ou Redis manualmente.

---

## 1. Tema escolhido

O tema escolhido foi uma **loja virtual de cosméticos**.

O sistema permite:

- cadastrar clientes;
- cadastrar produtos;
- listar clientes;
- listar produtos;
- criar pedidos;
- listar pedidos;
- visualizar tudo por uma página HTML simples.

---

## 2. Divisão dos bancos de dados

### PostgreSQL

O PostgreSQL foi usado para guardar dados mais estruturados, ou seja, dados que têm formato fixo.

Neste projeto ele guarda:

- clientes;
- pedidos.

Motivo da escolha: clientes e pedidos combinam com banco relacional porque possuem campos bem definidos, como nome, email, telefone, id do cliente, id do pedido e total.

---

### MongoDB

O MongoDB foi usado para guardar os produtos da loja.

Neste projeto ele guarda:

- nome do produto;
- categoria;
- preço;
- estoque;
- descrição.

Motivo da escolha: produtos podem ter descrições e campos mais flexíveis. Em uma loja real, cada tipo de cosmético poderia ter informações diferentes, então o modelo de documento do MongoDB combina bem.

---

### Redis

O Redis foi usado como cache.

Neste projeto ele guarda temporariamente:

- a lista de produtos.

Motivo da escolha: como produtos são consultados várias vezes pela tela da loja, o Redis ajuda a guardar essa lista por alguns segundos e evita buscar toda hora no MongoDB.

---

## 3. Backend e Frontend

### Backend

O backend foi feito com:

- Python;
- FastAPI.

Ele possui rotas para fazer CRUD de:

- clientes;
- produtos;
- pedidos.

### Frontend

O frontend é bem simples e foi feito com:

- HTML;
- CSS;
- JavaScript.

A tela permite cadastrar e visualizar os dados da loja funcionando.

---

## 4. Estrutura das pastas

```text
loja_cosmeticos_simples/
│
├── app/
│   ├── bancos/
│   │   ├── postgres.py
│   │   ├── mongo.py
│   │   └── redis_cache.py
│   │
│   ├── modelos/
│   │   ├── cliente.py
│   │   └── pedido.py
│   │
│   ├── rotas/
│   │   ├── clientes.py
│   │   ├── produtos.py
│   │   └── pedidos.py
│   │
│   ├── static/
│   │   ├── estilo.css
│   │   └── script.js
│   │
│   ├── templates/
│   │   └── index.html
│   │
│   └── principal.py
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## 5. Como rodar o projeto

### Passo 1

Abra o terminal dentro da pasta do projeto.

### Passo 2

Rode:

```bash
docker compose up --build
```

### Passo 3

Abra no navegador:

```text
http://localhost:8000
```

Pronto. A tela da loja vai abrir.

---

## 6. Como parar o projeto

No terminal, aperte:

```bash
CTRL + C
```

Depois rode:

```bash
docker compose down
```

---

## 7. Como apagar todos os dados e começar do zero

Se quiser apagar os dados dos bancos também, rode:

```bash
docker compose down -v
```

Depois suba de novo:

```bash
docker compose up --build
```

---

## 8. Rotas principais da API

Também dá para testar pelo navegador em:

```text
http://localhost:8000/docs
```

Rotas criadas:

### Clientes

- `GET /clientes/`
- `POST /clientes/`
- `PUT /clientes/{id_cliente}`
- `DELETE /clientes/{id_cliente}`

### Produtos

- `GET /produtos/`
- `POST /produtos/`
- `GET /produtos/{id_produto}`
- `PUT /produtos/{id_produto}`
- `DELETE /produtos/{id_produto}`

### Pedidos

- `GET /pedidos/`
- `POST /pedidos/`
- `PUT /pedidos/{id_pedido}`
- `DELETE /pedidos/{id_pedido}`

---

## 9. Resumo do funcionamento

O navegador abre a interface HTML.

A interface chama o backend FastAPI.

O backend usa:

- PostgreSQL para clientes e pedidos;
- MongoDB para produtos;
- Redis para cache da lista de produtos.

Assim o projeto segue o modelo pedido:

```text
Frontend <-> Backend <-> PostgreSQL
Frontend <-> Backend <-> MongoDB
Frontend <-> Backend <-> Redis
```
