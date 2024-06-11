
import os

import bcrypt
import jwt
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import users

JWT_SECRET = os.getenv('JWT_SECRET')

get_users = Blueprint("/users", __name__)

@get_users.route('/users', methods=['GET'])
def _get_users():
       #todo add more handling
       res = users.find()

        
       ret = []
       for record in res:
         ret.append({
          "_id": str(record["_id"]),
          "username": record["username"],
          "role": record["role"],
          "first_name": record["first_name"],
          "last_name": record["last_name"],
          "is_active": record["is_active"],
          "created_by": record["created_by"],
          "created_at": record["created_at"],

        })
       return {
          'data': ret,
        }, 200
   
