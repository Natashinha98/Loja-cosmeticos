from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.bancos.postgres import pegar_sessao
from app.modelos.pedido import Pedido
from app.bancos.mongo import colecao_produtos
from bson import ObjectId

rotas_pedidos = APIRouter(prefix="/pedidos", tags=["pedidos"])

@rotas_pedidos.post("/")
def criar_pedido(dados: dict, sessao: Session = Depends(pegar_sessao)):
    produto = colecao_produtos.find_one({"_id": ObjectId(dados.get("id_produto"))})

    if not produto:
        return {"erro": "Produto nao encontrado"}

    quantidade = int(dados.get("quantidade", 1))
    total = float(produto["preco"]) * quantidade

    novo_pedido = Pedido(
        id_cliente=int(dados.get("id_cliente")),
        id_produto=str(produto["_id"]),
        nome_produto=produto["nome"],
        quantidade=quantidade,
        total=total,
        status="criado"
    )

    sessao.add(novo_pedido)
    sessao.commit()
    sessao.refresh(novo_pedido)

    return {
        "mensagem": "Pedido criado com sucesso",
        "pedido": {
            "id_pedido": novo_pedido.id_pedido,
            "id_cliente": novo_pedido.id_cliente,
            "nome_produto": novo_pedido.nome_produto,
            "quantidade": novo_pedido.quantidade,
            "total": novo_pedido.total,
            "status": novo_pedido.status
        }
    }

@rotas_pedidos.get("/")
def listar_pedidos(sessao: Session = Depends(pegar_sessao)):
    pedidos = sessao.query(Pedido).order_by(Pedido.id_pedido).all()

    return [
        {
            "id_pedido": pedido.id_pedido,
            "id_cliente": pedido.id_cliente,
            "id_produto": pedido.id_produto,
            "nome_produto": pedido.nome_produto,
            "quantidade": pedido.quantidade,
            "total": pedido.total,
            "status": pedido.status
        }
        for pedido in pedidos
    ]

@rotas_pedidos.put("/{id_pedido}")
def editar_status_pedido(id_pedido: int, dados: dict, sessao: Session = Depends(pegar_sessao)):
    pedido = sessao.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()

    if not pedido:
        return {"erro": "Pedido nao encontrado"}

    pedido.status = dados.get("status", pedido.status)
    sessao.commit()

    return {"mensagem": "Status do pedido editado com sucesso"}

@rotas_pedidos.delete("/{id_pedido}")
def apagar_pedido(id_pedido: int, sessao: Session = Depends(pegar_sessao)):
    pedido = sessao.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()

    if not pedido:
        return {"erro": "Pedido nao encontrado"}

    sessao.delete(pedido)
    sessao.commit()

    return {"mensagem": "Pedido apagado com sucesso"}
