from sqlalchemy import Integer, String, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.bancos.postgres import Base

class Pedido(Base):
    __tablename__ = "pedidos"

    id_pedido: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    id_cliente: Mapped[int] = mapped_column(Integer, nullable=False)
    nome_cliente: Mapped[str] = mapped_column(String(120), nullable=False)

    produtos: Mapped[str] = mapped_column(Text, nullable=False)
    resumo_produtos: Mapped[str] = mapped_column(Text, nullable=False)

    quantidade_total: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="criado")