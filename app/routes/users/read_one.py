
import os

import bcrypt
import jwt
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, g, request

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
    
    id = g.user_id
    if 'id' in request.args:
        id = request.args.get('id')

    record = users.find_one({"_id": ObjectId(id)})
    if record:
        return {
            'data': {
                "_id": str(record["_id"]),
                "username": record["username"],
                "role": record["role"],
                "first_name": record["first_name"],
                "last_name": record["last_name"],
                "is_active": record["is_active"],
                "created_by": record["created_by"],
                "created_at": record["created_at"],
            },
        }, 200
    else:
        return {
            'message': 'User not found',
            'code': 21
        }, 200
    
