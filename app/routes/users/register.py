
import os
from datetime import datetime

import bcrypt
import jwt
from flask import Blueprint, g, request

from app.database.config import users
from app.utils.utils import roles

register = Blueprint("/user/register", __name__)

@register.route('/user/register', methods=['POST'])
def _create_account():
   username = request.form['username']
   password = request.form['password']
   first_name = request.form['first_name']
   last_name = request.form['last_name']
   role_id = request.form['role_id']
   created_by = g.user_id
   create_at = datetime.now()

   try:
      int(role_id)
   except:
      return {
         'message': 'data format is invalid',
         'code': 23
      }, 401
   
   user = list(users.find({"username": username}))

   if len(user) > 0:  
    return {
        'message': 'username already exist',
        'code': 1
    }, 200
   else:
     pwd_bytes = password.encode('utf-8')
     salt = bcrypt.gensalt()
     hashed = bcrypt.hashpw(pwd_bytes, salt)
     string_password = hashed.decode('utf8')
     doc = users.insert_one({
        "username": username,
        "password": string_password + " " + salt.decode('utf8'),
        "first_name": first_name,
        "last_name": last_name,
        "role": roles[int(role_id) - 1],
        "created_by": created_by,
        "created_at": create_at,
        "is_active": 1
     })
     
     if doc.inserted_id:
         return {
            'message': 'successfully registered',
            'code': 2,
         }, 200
     else:
         return {
            'message': 'unable to register user',
            'code': 16,
         }

