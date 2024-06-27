
import os

import bcrypt
from bson import ObjectId
import jwt
from flask import Blueprint, request

from app.database.config import roles, users, branches

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
    
    user_role = None
    user_branch = None
    try:
        role = roles.find_one({"_id": ObjectId(user[0]["role"])})
        user_role = {
            "_id": str(role["_id"]),
            "name": role["name"],
            "authorizations": role['authorizations']
        }
    except:
        user_role = None

    try: 
            branch = branches.find_one({"_id": ObjectId(user[0]["branch"])})
            if branch:
                user_branch = {
                    "_id": str(branch["_id"]),
                    "name": branch["name"],
                    "streetAddress": branch["street_address"],
                    "city": branch["city"],
                    "state": branch["state"],
                    'tin': branch.get('tin'),
                    "postalCode": branch["postal_code"],
                    "contactNumber": branch["contact_number"],
                    "emailAddress": branch["email_address"],
                    "isActive": branch["is_active"],
                }
    except Exception as e:
        print(e)
        user_branch = None
    return {
      'token': token,
      'data': {
        'id': str(user[0]['_id']) ,
        'username': user[0]['username'],
        'first_name': user[0]['first_name'],
        'last_name': user[0]['last_name'],
        'role': user_role,
        'branch': user_branch
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