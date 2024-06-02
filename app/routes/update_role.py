
from flask import Blueprint, request
from app.database.config import users
import jwt
import os
import bcrypt
from bson.objectid import ObjectId

JWT_SECRET = os.getenv('JWT_SECRET')

update_role = Blueprint("/user/role/edit", __name__)

@update_role.route('/user/role/edit', methods=['POST'])
def _update_role():
   headers = request.headers
   bearer = headers.get('Authorization')
   role_id = request.form['role_id']
   if role_id.isnumeric() == False:
      return {
        'message': 'invalid role id',
        'code': 4
      }, 200
   if bearer:
    auth = bearer.split(' ')
    if len(auth) > 1:
      token = auth[1]
      decoded_token = jwt.decode(token, options={"verify_signature": False})
      #todo verify signature

      filter = { '_id': ObjectId(decoded_token['user_id']) }
      filter = { 'email_address': 'lghernandez' }
      new_val = { "$set": { 'role': int(role_id) } }
      res = users.update_one(filter, new_val)
      if res.modified_count > 0:
       return {
          'message': 'update success',
          'code': 6
       }, 200
      else:
       return {
          'message': 'something went wrong',
          'code': 5
       }
   else:
     return {
        'message': 'User unauthenticated',
        'code': 3,
     }, 401

