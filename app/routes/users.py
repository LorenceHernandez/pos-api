
from flask import Blueprint, request
from app.database.config import users
import jwt
import os
import bcrypt
from bson.objectid import ObjectId
from bson.json_util import dumps, loads 

JWT_SECRET = os.getenv('JWT_SECRET')

get_users = Blueprint("/users", __name__)

@get_users.route('/users', methods=['GET'])
def _get_users():
   headers = request.headers
   bearer = headers.get('Authorization')
# role_id = None
#    if 'role_id' in request.form:
#     role_id = request.form['role_id']
#     if role_id.isnumeric() == False:
#       return {
#         'message': 'invalid role id',
#         'code': 4
#       }, 200
   if bearer:
    auth = bearer.split(' ')
    if len(auth) > 1:
      token = auth[1]
      try:
       decoded_token = jwt.decode(token, options={"verify_signature": False})
       res = users.find()

       ret = []
       for record in res:
         ret.append({
          "_id": str(record["_id"]),
          "email_address": record["email_address"],
          "role": record["role"]
        })

       print(ret)
       return {
          'data': ret,
        }, 200
      except:
       return {
          'message': 'Invalid token',
          'code': 9
       }
      #todo verify signature
   
   else:
     return {
        'message': 'User unauthenticated',
        'code': 3,
     }, 401

