
import os

import bcrypt
import jwt
from flask import Blueprint, request

from app.database.config import users

register = Blueprint("/user/register", __name__)

@register.route('/user/register', methods=['POST'])
def _create_account():
   email = request.form['email_address']
   password = request.form['password']

   user = list(users.find({"email_address": email}))
   if len(user) > 0:  
    return {
        'message': 'email address already exist',
        'code': 1
    }, 200
   else:
     pwd_bytes = password.encode('utf-8')
     salt = bcrypt.gensalt()
     hashed = bcrypt.hashpw(pwd_bytes, salt)
     string_password = hashed.decode('utf8')
     doc = users.insert_one({
        "email_address": email,
        "password": string_password + " " + salt.decode('utf8'),
        "role": None
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

