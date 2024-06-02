
from flask import Blueprint, request
from app.database.config import users
import jwt
import os
from app.database.config import users
import bcrypt

register = Blueprint("/user/register", __name__)

@register.route('/user/register', methods=['POST'])
def create_account():
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
        "password": string_password,
     })
     return {
        'message': 'successfully registered',
        'code': 2,
     }, 200

