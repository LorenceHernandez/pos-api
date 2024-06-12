
import os
from datetime import datetime

import bcrypt
import jwt
from flask import Blueprint, g, request

from app.database.config import products

create_product = Blueprint("/product/create", __name__)

@create_product.route('/product/create', methods=['POST'])
def _create_product():
   request_data = request.get_json()
   name = request_data['name']
   desc = request_data['description']
   price = request_data['price']
   category = request_data['category']
   inventory_prerequisite = request_data['inventoryPrerequisite']
   sku = request_data['sku']
   created_by = g.user_id
   create_at = datetime.now()

   try:
        float(price)
   except:
        return {
            'message': 'data format is invalid',
            'code': 23
        }, 200

   doc = list(products.find({"sku": sku}))

   if len(doc) > 0:
      return {
         'message': 'Duplicate SKU is not allowed',
         'code': 17
      }, 200
   
   doc = products.insert_one({
      "name": name,
      "description": desc,
      "category": category,
      "inventory_prerequisite": inventory_prerequisite,
      "price": price,
      "sku": sku,
      "created_by": created_by,
      "created_at": create_at,
   })
   
   if doc.inserted_id:
      return {
         'message': 'Product successfully added.',
         'code': 15,
      }, 200
   else:
      return {
         'message': 'Unable to add product',
         'code': 16,
      }, 200


