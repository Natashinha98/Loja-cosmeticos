from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.bancos.postgres import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    telefone: Mapped[str] = mapped_column(String(30), nullable=True)
