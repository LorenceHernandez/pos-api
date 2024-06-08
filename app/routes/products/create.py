
import os

import bcrypt
import jwt
from flask import Blueprint, request

from app.database.config import products

create_product = Blueprint("/product/create", __name__)

@create_product.route('/product/create', methods=['POST'])
def _create_product():
   name = request.form['name']
   price = request.form['price']
   sku = request.form['sku']

   doc = list(products.find({"sku": sku}))

   if len(doc) > 1:
      return {
         'message': 'Duplicate SKU is not allowed',
         'code': 17
      }, 200
   
   doc = products.insert_one({
      "name": name,
      "price": price,
      "sku": sku
   })
   
   if doc.inserted_id:
      return {
         'message': 'successfully added',
         'code': 15,
      }, 200
   else:
      return {
         'message': 'unable to add product',
         'code': 16,
      }, 200


