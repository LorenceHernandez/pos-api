
from flask import Blueprint, request
from app.database.config import users
import jwt
import os
import bcrypt

JWT_KEY = os.getenv('JWT_SECRET_KEY')

login = Blueprint("login", __name__)

@login.route('/login', methods=['POST'])
def _authenticate():
 user = list(users.find({"email_address": request.form['email_address']}))
 
 if len(user) > 0:   
   splitpw = user[0]['password'].split(' ')
   pwd_bytes = request.form['password'].encode('utf-8')
   salt = splitpw[1].encode('utf-8')

   hashed = bcrypt.hashpw(pwd_bytes, salt)
   string_password = hashed.decode('utf8')

   if string_password == splitpw[0]: 
    token = jwt.encode({"user_id": str(user[0]['_id'])}, JWT_KEY, algorithm="HS256")
    return {
      'token': token
    }, 200
   else: 
    return {
      'error': 'wrong username or password'
    }, 200
 else: 
    return {
      'error': 'wrong username or password'
    }, 200