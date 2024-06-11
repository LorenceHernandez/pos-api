import os

from pymongo import MongoClient

MONGO_PORT = os.getenv('MONGO_PORT')
MONGO_HOST_PY = os.getenv('MONGO_HOST_PY')
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASS = os.getenv('MONGO_PASS')

host = 'mongodb://' + MONGO_USER + ':' + MONGO_PASS + '@' + MONGO_HOST_PY + ':' + MONGO_PORT + '/?authSource=pos'

client = MongoClient(host)                
db = client.pos
users = db.users
products = db.products