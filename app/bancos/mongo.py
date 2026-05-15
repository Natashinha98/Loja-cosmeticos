import os
from pymongo import MongoClient

url_mongo = os.getenv("MONGO_URL", "mongodb://localhost:27017")

cliente_mongo = MongoClient(url_mongo)
banco_mongo = cliente_mongo["loja_cosmeticos"]

colecao_produtos = banco_mongo["produtos"]
