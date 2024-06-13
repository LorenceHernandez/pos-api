
import os
from datetime import datetime

import bcrypt
import jwt
from bson import ObjectId
from flask import Blueprint, request

from app.database.config import branches

update_branch = Blueprint("/branch/edit", __name__)

@update_branch.route('/branch/edit', methods=['POST'])
def _update_branch():
   request_data = request.get_json()
   update_val = {}
   id = request_data['id']

   try:
        if 'isActive' in request_data:
            update_val['is_active'] = bool(request_data['isActive'])
   except:
      return {
         'message': 'data format is invalid',
         'code': 23
   }, 200

   if 'name' in request_data:
      update_val['name'] = request_data['name']
   if 'address' in request_data:
      update_val['address'] = request_data['address']
   
   if not update_val:
        return {
            'message': 'atleast one field is required when updating a user',
            'code': 25
        }, 200
   filter = { '_id': ObjectId(id) }
   new_val = { "$set": update_val }
   #array_filt = {"arrayFilters": [{'[0].id': '1'}]}

   print(new_val)
   res = branches.update_one(filter, new_val)
   if res.modified_count > 0:
      return {
         'message': 'Branch update success',
         'code': 18
      }, 200
   else:
      return {
         'message': 'Unable to update branch',
         'code': 16
      }


