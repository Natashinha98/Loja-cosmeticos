from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.bancos.postgres import Base, motor_banco
from app.bancos.mongo import colecao_produtos
from app.rotas.clientes import rotas_clientes
from app.rotas.produtos import rotas_produtos
from app.rotas.pedidos import rotas_pedidos
from app.rotas.carrinho import rotas_carrinho

app = FastAPI(title="Loja de Cosmeticos Simples")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(rotas_clientes)
app.include_router(rotas_produtos)
app.include_router(rotas_pedidos)
app.include_router(rotas_carrinho)

@app.on_event("startup")
def iniciar_bancos():
    Base.metadata.create_all(bind=motor_banco)

    if colecao_produtos.count_documents({}) == 0:
        colecao_produtos.insert_many([
            {
                "nome": "Gloss Moranguinho",
                "categoria": "Boca",
                "preco": 19.90,
                "estoque": 20,
                "descricao": "Gloss simples com cheirinho doce"
            },
            {
                "nome": "Hidratante Florzinha",
                "categoria": "Corpo",
                "preco": 34.90,
                "estoque": 15,
                "descricao": "Hidratante corporal basico"
            },
            {
                "nome": "Mascara de Cilios Preta",
                "categoria": "Olhos",
                "preco": 29.90,
                "estoque": 12,
                "descricao": "Mascara para deixar os cilios destacados"
            }
        ])

@app.get("/", response_class=HTMLResponse)
def abrir_loja(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/saude")
def testar_sistema():
    return {"mensagem": "Sistema da loja funcionando"}
