import os
from pymongo import MongoClient

MONGO_PORT = os.getenv('MONGO_PORT')
MONGO_HOST = os.getenv('MONGO_HOST')

client = MongoClient(MONGO_HOST, int(MONGO_PORT))
db = client.pos
users = db.users