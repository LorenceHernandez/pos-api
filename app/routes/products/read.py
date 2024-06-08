from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import products

get_products = Blueprint("/products", __name__)

@get_products.route('/products', methods=['GET'])
def _get_products():
       #todo add more handling
       res = products.find()

       ret = []
       for record in res:
         ret.append({
          "_id": str(record["_id"]),
          "sku": record["sku"],
          "price": record["price"],
          "name": record["name"]
         })
       return {
          'data': ret,
        }, 200
   
