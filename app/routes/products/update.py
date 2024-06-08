
import os

import bcrypt
import jwt
from bson import ObjectId
from flask import Blueprint, request

from app.database.config import products

update_product = Blueprint("/product/edit", __name__)

@update_product.route('/product/edit', methods=['POST'])
def _update_product():
   id = request.form['id']
   update_val = {}
   if 'price' in request.form:
      try:
        update_val['price'] = format(float(request.form['price']), '.2f')
      except ValueError:
        return {
            'message': 'price format is not allowed',
            'code': 19
        }, 200
   if 'name' in request.form:
      update_val['name'] = request.form['name']
   if 'sku' in request.form:
      update_val['sku'] = request.form['sku']
   
   if not update_val:
        return {
            'message': 'atleast one field is required when updating a user',
            'code': 25
        }, 200
      
   filter = { '_id': ObjectId(id) }
   new_val = { "$set": update_val }

   res = products.update_one(filter, new_val)
   if res.modified_count > 0:
      return {
         'message': 'product update success',
         'code': 18
      }, 200
   else:
      return {
         'message': 'unable to update product',
         'code': 16
      }


