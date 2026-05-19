import json
from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.bancos.redis_cache import cache_redis
from app.bancos.mongo import colecao_produtos
from app.bancos.postgres import pegar_sessao
from app.modelos.cliente import Cliente
from app.modelos.pedido import Pedido

rotas_carrinho = APIRouter(prefix="/carrinho", tags=["carrinho"])

# Carrinho expira em 30 minutos de inatividade
TTL_CARRINHO_SEGUNDOS = 30 * 60


def chave_carrinho(id_cliente: int) -> str:
    return f"carrinho:{id_cliente}"


def ler_carrinho_do_redis(id_cliente: int) -> dict:
    dados = cache_redis.get(chave_carrinho(id_cliente))
    if not dados:
        return {"itens": [], "atualizado_em": None}
    return json.loads(dados)


def salvar_carrinho_no_redis(id_cliente: int, carrinho: dict):
    carrinho["atualizado_em"] = datetime.utcnow().isoformat()
    cache_redis.set(
        chave_carrinho(id_cliente),
        json.dumps(carrinho),
        ex=TTL_CARRINHO_SEGUNDOS
    )


def montar_carrinho_detalhado(id_cliente: int) -> dict:
    """Lê o carrinho do Redis e enriquece com dados atuais do MongoDB."""
    carrinho = ler_carrinho_do_redis(id_cliente)
    itens_detalhados = []
    total = 0

    for item in carrinho["itens"]:
        produto = colecao_produtos.find_one({"_id": ObjectId(item["id_produto"])})
        if not produto:
            # produto foi removido do catálogo: ignora silenciosamente
            continue

        preco = float(produto["preco"])
        subtotal = preco * item["quantidade"]

        itens_detalhados.append({
            "id_produto": item["id_produto"],
            "nome": produto["nome"],
            "preco": preco,
            "quantidade": item["quantidade"],
            "subtotal": subtotal
        })
        total += subtotal

    return {
        "id_cliente": id_cliente,
        "itens": itens_detalhados,
        "total": total,
        "atualizado_em": carrinho.get("atualizado_em")
    }


@rotas_carrinho.get("/{id_cliente}")
def ver_carrinho(id_cliente: int):
    return montar_carrinho_detalhado(id_cliente)


@rotas_carrinho.post("/{id_cliente}/itens")
def adicionar_item(id_cliente: int, dados: dict):
    id_produto = dados.get("id_produto")
    quantidade = int(dados.get("quantidade", 1))

    if quantidade <= 0:
        return {"erro": "Quantidade deve ser maior que zero"}

    produto = colecao_produtos.find_one({"_id": ObjectId(id_produto)})
    if not produto:
        return {"erro": "Produto nao encontrado"}

    carrinho = ler_carrinho_do_redis(id_cliente)

    # se o item já existe no carrinho, soma a quantidade
    item_existente = None
    for item in carrinho["itens"]:
        if item["id_produto"] == id_produto:
            item_existente = item
            break

    if item_existente:
        item_existente["quantidade"] += quantidade
    else:
        carrinho["itens"].append({
            "id_produto": id_produto,
            "quantidade": quantidade
        })

    salvar_carrinho_no_redis(id_cliente, carrinho)
    return montar_carrinho_detalhado(id_cliente)


@rotas_carrinho.put("/{id_cliente}/itens/{id_produto}")
def atualizar_quantidade(id_cliente: int, id_produto: str, dados: dict):
    quantidade = int(dados.get("quantidade", 0))

    carrinho = ler_carrinho_do_redis(id_cliente)

    if quantidade <= 0:
        # quantidade zero ou negativa: remove o item
        carrinho["itens"] = [
            i for i in carrinho["itens"] if i["id_produto"] != id_produto
        ]
    else:
        encontrou = False
        for item in carrinho["itens"]:
            if item["id_produto"] == id_produto:
                item["quantidade"] = quantidade
                encontrou = True
                break
        if not encontrou:
            return {"erro": "Item nao esta no carrinho"}

    salvar_carrinho_no_redis(id_cliente, carrinho)
    return montar_carrinho_detalhado(id_cliente)


@rotas_carrinho.delete("/{id_cliente}/itens/{id_produto}")
def remover_item(id_cliente: int, id_produto: str):
    carrinho = ler_carrinho_do_redis(id_cliente)
    carrinho["itens"] = [
        i for i in carrinho["itens"] if i["id_produto"] != id_produto
    ]
    salvar_carrinho_no_redis(id_cliente, carrinho)
    return montar_carrinho_detalhado(id_cliente)


@rotas_carrinho.delete("/{id_cliente}")
def esvaziar_carrinho(id_cliente: int):
    cache_redis.delete(chave_carrinho(id_cliente))
    return {"mensagem": "Carrinho esvaziado"}


@rotas_carrinho.post("/{id_cliente}/finalizar")
def finalizar_carrinho(id_cliente: int, sessao: Session = Depends(pegar_sessao)):
    """Converte o carrinho do Redis em um pedido no PostgreSQL e esvazia o carrinho."""
    cliente = sessao.query(Cliente).filter(
        Cliente.id_cliente == id_cliente
    ).first()

    if not cliente:
        return {"erro": "Cliente nao encontrado"}

    detalhado = montar_carrinho_detalhado(id_cliente)

    if not detalhado["itens"]:
        return {"erro": "Carrinho vazio"}

    resumo = ", ".join(
        f'{i["nome"]} ({i["quantidade"]}x)' for i in detalhado["itens"]
    )
    quantidade_total = sum(i["quantidade"] for i in detalhado["itens"])

    novo_pedido = Pedido(
        id_cliente=cliente.id_cliente,
        nome_cliente=cliente.nome,
        produtos=json.dumps(detalhado["itens"]),
        resumo_produtos=resumo,
        quantidade_total=quantidade_total,
        total=detalhado["total"],
        status="criado"
    )

    sessao.add(novo_pedido)
    sessao.commit()
    sessao.refresh(novo_pedido)

    # esvazia o carrinho depois de virar pedido
    cache_redis.delete(chave_carrinho(id_cliente))

    return {
        "mensagem": "Pedido criado a partir do carrinho",
        "id_pedido": novo_pedido.id_pedido,
        "total": detalhado["total"]
    }
