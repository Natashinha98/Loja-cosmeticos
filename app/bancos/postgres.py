import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

usuario = os.getenv("POSTGRES_USER", "aluna")
senha = os.getenv("POSTGRES_PASSWORD", "senha123")
host = os.getenv("POSTGRES_HOST", "localhost")
nome_banco = os.getenv("POSTGRES_DB", "loja_cosmeticos")

url_banco = f"postgresql+psycopg2://{usuario}:{senha}@{host}:5432/{nome_banco}"

motor_banco = create_engine(url_banco)
SessaoBanco = sessionmaker(autocommit=False, autoflush=False, bind=motor_banco)

class Base(DeclarativeBase):
    pass

def pegar_sessao():
    sessao = SessaoBanco()
    try:
        yield sessao
    finally:
        sessao.close()
