
import os
from datetime import datetime

import bcrypt
import jwt
from bson import ObjectId
from flask import Blueprint, request

from app.database.config import corporates

update_company = Blueprint("/corporate/edit", __name__)

@update_company.route('/corporate/edit', methods=['POST'])
def _update_company():
   request_data = request.get_json()
   update_val = {}
   id = request_data['id']

   try:
        ObjectId(id)
   except:
      return {
         'message': 'data format is invalid',
         'code': 23
   }, 200

   if 'name' in request_data:
      update_val['name'] = request_data['name']
   
   if not update_val:
        return {
            'message': 'atleast one field is required when updating a corporate',
            'code': 25
        }, 200
   filter = { '_id': ObjectId(id) }
   new_val = { "$set": update_val }
   #array_filt = {"arrayFilters": [{'[0].id': '1'}]}

   print(new_val)
   res = corporates.update_one(filter, new_val)
   if res.modified_count > 0:
      return {
         'message': 'Corporate update success',
         'code': 18
      }, 200
   else:
      return {
         'message': 'Unable to update corporate',
         'code': 16
      }


