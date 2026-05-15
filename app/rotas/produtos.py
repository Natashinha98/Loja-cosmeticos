import json
from bson import ObjectId
from fastapi import APIRouter
from app.bancos.mongo import colecao_produtos
from app.bancos.redis_cache import cache_redis

rotas_produtos = APIRouter(prefix="/produtos", tags=["produtos"])

def arrumar_id(produto):
    produto["id_produto"] = str(produto["_id"])
    del produto["_id"]
    return produto

@rotas_produtos.post("/")
def cadastrar_produto(dados: dict):
    produto = {
        "nome": dados.get("nome"),
        "categoria": dados.get("categoria"),
        "preco": float(dados.get("preco", 0)),
        "estoque": int(dados.get("estoque", 0)),
        "descricao": dados.get("descricao", "")
    }

    resultado = colecao_produtos.insert_one(produto)
    cache_redis.delete("lista_produtos")

    return {
        "mensagem": "Produto cadastrado com sucesso",
        "id_produto": str(resultado.inserted_id)
    }

@rotas_produtos.get("/")
def listar_produtos():
    produtos_cache = cache_redis.get("lista_produtos")

    if produtos_cache:
        return json.loads(produtos_cache)

    produtos = [arrumar_id(produto) for produto in colecao_produtos.find().sort("nome", 1)]
    cache_redis.set("lista_produtos", json.dumps(produtos), ex=60)

    return produtos

@rotas_produtos.get("/{id_produto}")
def buscar_produto(id_produto: str):
    produto = colecao_produtos.find_one({"_id": ObjectId(id_produto)})
    if not produto:
        return {"erro": "Produto nao encontrado"}

    return arrumar_id(produto)

@rotas_produtos.put("/{id_produto}")
def editar_produto(id_produto: str, dados: dict):
    novos_dados = {}

    for campo in ["nome", "categoria", "descricao"]:
        if campo in dados:
            novos_dados[campo] = dados[campo]

    if "preco" in dados:
        novos_dados["preco"] = float(dados["preco"])

    if "estoque" in dados:
        novos_dados["estoque"] = int(dados["estoque"])

    colecao_produtos.update_one(
        {"_id": ObjectId(id_produto)},
        {"$set": novos_dados}
    )

    cache_redis.delete("lista_produtos")
    return {"mensagem": "Produto editado com sucesso"}

@rotas_produtos.delete("/{id_produto}")
def apagar_produto(id_produto: str):
    colecao_produtos.delete_one({"_id": ObjectId(id_produto)})
    cache_redis.delete("lista_produtos")
    return {"mensagem": "Produto apagado com sucesso"}
