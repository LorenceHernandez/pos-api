
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import users

update_role = Blueprint("/user/edit", __name__)

@update_role.route('/user/edit', methods=['POST'])
def _update_role():
   try: 
      ObjectId(request.form['user_id'])
      int(role_id)
   except:
    return {
      'message': 'data format is invalid',
      'code': 23
    }, 401
   
   update_val = {}
   if 'role_id' in request.form:
      update_val['role_id'] = role_id
   role_id = request.form['role_id']
   user_id = request.form['user_id']

   if not update_val:
        return {
            'message': 'atleast one field is required when updating a product',
            'code': 24
        }, 200
   filter = { '_id': ObjectId(user_id) }
   new_val = { "$set": { 'role': int(role_id) } }

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

