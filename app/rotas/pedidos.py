import json
from bson import ObjectId
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.bancos.postgres import pegar_sessao
from app.modelos.pedido import Pedido
from app.modelos.cliente import Cliente
from app.bancos.mongo import colecao_produtos

rotas_pedidos = APIRouter(prefix="/pedidos", tags=["pedidos"])


def montar_dados_dos_produtos(itens):
    produtos_do_pedido = []
    total = 0
    quantidade_total = 0
    nomes_produtos = []

    for item in itens:
        id_produto = item.get("id_produto")
        quantidade = int(item.get("quantidade", 1))

        if quantidade <= 0:
            quantidade = 1

        produto = colecao_produtos.find_one({"_id": ObjectId(id_produto)})

        if not produto:
            return None

        preco = float(produto["preco"])
        subtotal = preco * quantidade

        produtos_do_pedido.append({
            "id_produto": str(produto["_id"]),
            "nome": produto["nome"],
            "preco": preco,
            "quantidade": quantidade,
            "subtotal": subtotal
        })

        nomes_produtos.append(f'{produto["nome"]} ({quantidade}x)')
        quantidade_total += quantidade
        total += subtotal

    return {
        "produtos": produtos_do_pedido,
        "resumo_produtos": ", ".join(nomes_produtos),
        "quantidade_total": quantidade_total,
        "total": total
    }


@rotas_pedidos.post("/")
def criar_pedido(dados: dict, sessao: Session = Depends(pegar_sessao)):
    cliente = sessao.query(Cliente).filter(
        Cliente.id_cliente == int(dados.get("id_cliente"))
    ).first()

    if not cliente:
        return {"erro": "Cliente nao encontrado"}

    itens = dados.get("itens", [])

    if not itens:
        return {"erro": "Escolha pelo menos um produto"}

    dados_produtos = montar_dados_dos_produtos(itens)

    if not dados_produtos:
        return {"erro": "Um dos produtos nao foi encontrado"}

    novo_pedido = Pedido(
        id_cliente=cliente.id_cliente,
        nome_cliente=cliente.nome,
        produtos=json.dumps(dados_produtos["produtos"]),
        resumo_produtos=dados_produtos["resumo_produtos"],
        quantidade_total=dados_produtos["quantidade_total"],
        total=dados_produtos["total"],
        status=dados.get("status", "criado")
    )

    sessao.add(novo_pedido)
    sessao.commit()
    sessao.refresh(novo_pedido)

    return {
        "mensagem": "Pedido criado com sucesso",
        "pedido": transformar_pedido(novo_pedido)
    }


@rotas_pedidos.get("/")
def listar_pedidos(sessao: Session = Depends(pegar_sessao)):
    pedidos = sessao.query(Pedido).order_by(Pedido.id_pedido).all()
    return [transformar_pedido(pedido) for pedido in pedidos]


@rotas_pedidos.put("/{id_pedido}")
def editar_pedido(id_pedido: int, dados: dict, sessao: Session = Depends(pegar_sessao)):
    pedido = sessao.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()

    if not pedido:
        return {"erro": "Pedido nao encontrado"}

    if "id_cliente" in dados:
        cliente = sessao.query(Cliente).filter(
            Cliente.id_cliente == int(dados.get("id_cliente"))
        ).first()

        if not cliente:
            return {"erro": "Cliente nao encontrado"}

        pedido.id_cliente = cliente.id_cliente
        pedido.nome_cliente = cliente.nome

    if "itens" in dados:
        itens = dados.get("itens", [])

        if not itens:
            return {"erro": "Escolha pelo menos um produto"}

        dados_produtos = montar_dados_dos_produtos(itens)

        if not dados_produtos:
            return {"erro": "Um dos produtos nao foi encontrado"}

        pedido.produtos = json.dumps(dados_produtos["produtos"])
        pedido.resumo_produtos = dados_produtos["resumo_produtos"]
        pedido.quantidade_total = dados_produtos["quantidade_total"]
        pedido.total = dados_produtos["total"]

    if "status" in dados:
        pedido.status = dados.get("status")

    sessao.commit()

    return {
        "mensagem": "Pedido editado com sucesso",
        "pedido": transformar_pedido(pedido)
    }


@rotas_pedidos.delete("/{id_pedido}")
def apagar_pedido(id_pedido: int, sessao: Session = Depends(pegar_sessao)):
    pedido = sessao.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()

    if not pedido:
        return {"erro": "Pedido nao encontrado"}

    sessao.delete(pedido)
    sessao.commit()

    return {"mensagem": "Pedido apagado com sucesso"}


def transformar_pedido(pedido):
    return {
        "id_pedido": pedido.id_pedido,
        "id_cliente": pedido.id_cliente,
        "nome_cliente": pedido.nome_cliente,
        "produtos": json.loads(pedido.produtos),
        "resumo_produtos": pedido.resumo_produtos,
        "quantidade_total": pedido.quantidade_total,
        "total": pedido.total,
        "status": pedido.status
    }