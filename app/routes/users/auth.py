
import os

import bcrypt
from bson import ObjectId
import jwt
from flask import Blueprint, request

from app.database.config import roles, users

JWT_KEY = os.getenv('JWT_SECRET_KEY')

login = Blueprint("login", __name__)

@login.route('/login', methods=['POST'])
def _authenticate():
 user = list(users.find({"username": request.form['username']}))

 if len(user) > 0:   
   if user[0]['role'] == None:
    return {
     'message': 'User has no role',
     'code': 10,
    }, 200
  
   splitpw = user[0]['password'].split(' ')
   pwd_bytes = request.form['password'].encode('utf-8')

   salt = splitpw[1].encode('utf-8')

   hashed = bcrypt.hashpw(pwd_bytes, salt)
   string_password = hashed.decode('utf8')

   if string_password == splitpw[0]: 
    token = jwt.encode({"user_id": str(user[0]['_id'])}, JWT_KEY, algorithm="HS256")
    role = roles.find_one({"_id": ObjectId(user[0]["role"])})

    return {
      'token': token,
      'data': {
        'id': str(user[0]['_id']) ,
        'username': user[0]['username'],
        'first_name': user[0]['first_name'],
        'last_name': user[0]['last_name'],
        'role': {
          "_id": str(role["_id"]),
          "name": role["name"],
        }
      }
    }, 200
   else: 
    return {
      'message': 'wrong username or password',
      'code': 11
    }, 200
 else: 
    return {
      'message': 'wrong username or password',
      'code': 11
    }, 200