
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import users
from app.utils.utils import roles

update_user = Blueprint("/user/edit", __name__)

@update_user.route('/user/edit', methods=['POST'])
def _update_user():
   request_data = request.get_json()
   id = request_data['id']

   update_val = {}
   try: 
      ObjectId(id)
      if 'roleId' in request_data:
         ObjectId(request_data['roleId'])
         update_val['role'] = request_data['roleId']
      if 'branchId' in request_data:
         ObjectId(request_data['branchId'])
         update_val['branch'] = request_data['branchId']
   except:
    return {
      'message': 'data format is invalid',
      'code': 23
    }, 401
   
   if 'username' in request_data:
      update_val['username'] = request_data['username']
   if 'firstName' in request_data:
      update_val['first_name'] = request_data['firstName']
   if 'lastName' in request_data:
      update_val['last_name'] = request_data['lastName']
   if 'isActive' in request_data:
      update_val['is_active'] = request_data['isActive']

   if not update_val: 
        return {
            'message': 'atleast one field is required when updating a user',
            'code': 24
        }, 200
   filter = { '_id': ObjectId(id) }
   new_val = { "$set": update_val }

   res = users.update_one(filter, new_val)
   if res.modified_count > 0:
      return {
         'message': 'user update success',
         'code': 6
      }, 200
   else:
      return {
         'message': 'unable to update user',
         'code': 16
      }

