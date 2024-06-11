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

   record = products.find_one({"_id": ObjectId(request.args.get('id'))})

   if record: 
       return {
          'data': {
          "_id": str(record["_id"]),
          "sku": record["sku"],
          "name": record["name"],
          "price": record["price"],
          "description": record["description"],
          "category": str(record["category"]),
          "inventory_prerequisite": record["inventory_prerequisite"],
          "created_by": record["created_by"],
          "created_at": record["created_at"]
          },
       }, 200 
   else:
        return {
            'message': 'Product not found',
            'code': 20
        }, 200
   
