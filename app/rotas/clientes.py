from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.bancos.postgres import pegar_sessao
from app.modelos.cliente import Cliente

rotas_clientes = APIRouter(prefix="/clientes", tags=["clientes"])

@rotas_clientes.post("/")
def cadastrar_cliente(dados: dict, sessao: Session = Depends(pegar_sessao)):
    novo_cliente = Cliente(
        nome=dados.get("nome"),
        email=dados.get("email"),
        telefone=dados.get("telefone", "")
    )
    sessao.add(novo_cliente)
    sessao.commit()
    sessao.refresh(novo_cliente)
    return {
        "mensagem": "Cliente cadastrado com sucesso",
        "cliente": {
            "id_cliente": novo_cliente.id_cliente,
            "nome": novo_cliente.nome,
            "email": novo_cliente.email,
            "telefone": novo_cliente.telefone
        }
    }

@rotas_clientes.get("/")
def listar_clientes(sessao: Session = Depends(pegar_sessao)):
    clientes = sessao.query(Cliente).order_by(Cliente.id_cliente).all()
    return [
        {
            "id_cliente": cliente.id_cliente,
            "nome": cliente.nome,
            "email": cliente.email,
            "telefone": cliente.telefone
        }
        for cliente in clientes
    ]

@rotas_clientes.put("/{id_cliente}")
def editar_cliente(id_cliente: int, dados: dict, sessao: Session = Depends(pegar_sessao)):
    cliente = sessao.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
    if not cliente:
        return {"erro": "Cliente nao encontrado"}

    cliente.nome = dados.get("nome", cliente.nome)
    cliente.email = dados.get("email", cliente.email)
    cliente.telefone = dados.get("telefone", cliente.telefone)

    sessao.commit()
    return {"mensagem": "Cliente editado com sucesso"}

@rotas_clientes.delete("/{id_cliente}")
def apagar_cliente(id_cliente: int, sessao: Session = Depends(pegar_sessao)):
    cliente = sessao.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
    if not cliente:
        return {"erro": "Cliente nao encontrado"}

    sessao.delete(cliente)
    sessao.commit()
    return {"mensagem": "Cliente apagado com sucesso"}
