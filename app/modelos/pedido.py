from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.bancos.postgres import Base

class Pedido(Base):
    __tablename__ = "pedidos"

    id_pedido: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    id_cliente: Mapped[int] = mapped_column(Integer, nullable=False)
    id_produto: Mapped[str] = mapped_column(String(80), nullable=False)
    nome_produto: Mapped[str] = mapped_column(String(120), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="criado")
