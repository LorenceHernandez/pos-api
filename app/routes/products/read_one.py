from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import products

get_product = Blueprint("/product", __name__)

@get_product.route('/product', methods=['GET'])
def _get_product():
   try: 
        ObjectId(request.args.get('id'))
   except:
        return {
            'message': 'data format is invalid',
            'code': 23
        }, 401

   product = products.find_one({"_id": ObjectId(request.args.get('id'))})

   if product: 
       return {
          'data': {
            "_id": str(product["_id"]),
            "sku": product["sku"],
            "price": product["price"],
            "name": product["name"]
          },
       }, 200 
   else:
        return {
            'message': 'Product not found',
            'code': 20
        }, 200
   
