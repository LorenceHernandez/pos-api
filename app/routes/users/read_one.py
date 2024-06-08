
import os

import bcrypt
import jwt
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import users

JWT_SECRET = os.getenv('JWT_SECRET')

get_user = Blueprint("/user", __name__)

@get_user.route('/user', methods=['GET'])
def _get_user():
    try: 
        ObjectId(request.args.get('id'))
    except:
        return {
            'message': 'data format is invalid',
            'code': 23
        }, 401
    
    user = users.find_one({"_id": ObjectId(request.args.get('id'))})
    if user:
        return {
            'data': {
                "_id": str(user["_id"]),
                "email_address": user["email_address"],
                "role": user["role"]
            },
        }, 200
    else:
        return {
            'message': 'User not found',
            'code': 21
        }, 200
    
