
from flask import Blueprint, request
from app.database.config import users
import jwt
import os

JWT_KEY = os.getenv('JWT_SECRET_KEY')

login = Blueprint("login", __name__)

@login.route('/login', methods=['POST'])
def authenticate():
 user = list(users.find({"username": request.form['username']}))

 if len(user) > 0:   
   if user[0]['password'] == request.form['password']: 
    token = jwt.encode({"user_id": str(user[0]['_id'])}, JWT_KEY,algorithm="HS256")
    return {
      'token': token
    }, 200
 else: 
    return {
      'error': 'wrong username or password'
    }, 200