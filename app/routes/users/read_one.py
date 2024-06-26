
import os

import bcrypt
import jwt
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, g, request

from app.database.config import branches, users, roles

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
    user_branch = None
    user_role = None

    if record:
        try: 

            role = roles.find_one({"_id": ObjectId(record["role"])})
            user_role = {
                "_id": str(role["_id"]),
                "name": role["name"],
            }

            branch = branches.find_one({"_id": ObjectId(record["branch_id"])})
            if branch:
                user_branch = {
                    "_id": str(branch["_id"]),
                    "name": branch["name"],
                    "streetAddress": branch["street_address"],
                    "city": branch["city"],
                    "state": branch["state"],
                    "postalCode": branch["postal_code"],
                    "contactNumber": branch["contact_number"],
                    "emailAddress": branch["email_address"],
                    "isActive": branch["is_active"],
                }
        except: 
            user_branch = None
        return {
            'data': {
                "_id": str(record["_id"]),
                "username": record["username"],
                "role": user_role,
                "firstName": record["first_name"],
                "branch": user_branch,
                "lastName": record["last_name"],
                "isActive": record["is_active"],
                "createdBy": record["created_by"],
                "createdAt": record["created_at"],
            },
        }, 200
    else:
        return {
            'message': 'User not found',
            'code': 21
        }, 200
    
