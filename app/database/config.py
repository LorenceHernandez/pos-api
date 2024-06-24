import os

from pymongo import MongoClient

MONGO_PORT = os.getenv('MONGO_PORT')
MONGO_HOST_PY = os.getenv('MONGO_HOST_PY')
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASS = os.getenv('MONGO_PASS')
LOCAL = os.getenv('LOCAL')

if LOCAL: 
 client = client = MongoClient(MONGO_HOST_PY, int(MONGO_PORT)) 
else:  
  host = 'mongodb://' + MONGO_USER + ':' + MONGO_PASS + '@' + MONGO_HOST_PY + ':' + MONGO_PORT + '/?authSource=pos'
  client = MongoClient(host)   

db = client.pos
users = db.users
products = db.products
doctors = db.doctors
product_categories = db.product_categories
branches = db.branches
corporates = db.corporates
customers = db.customers
packages = db.packages
roles = db.roles
transactions = db.transactions