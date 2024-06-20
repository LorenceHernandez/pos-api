
import os

import bcrypt
import jwt
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import branches, users

JWT_SECRET = os.getenv('JWT_SECRET')

get_users = Blueprint("/users", __name__)

@get_users.route('/users', methods=['GET'])
def _get_users():
       #todo add more handling
       res = users.find()

        
       ret = []
       for record in res:
          user_branch = None
          try: 
              branch = branches.find_one({"_id": ObjectId(record["branch_id"])})
              print(branch)
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
          ret.append({
                "_id": str(record["_id"]),
                "username": record["username"],
                "role": record["role"],
                "branch": user_branch,
                "firstName": record["first_name"],
                "lastName": record["last_name"],
                "isActive": record["is_active"],
                "createdBy": record["created_by"],
                "createdAt": record["created_at"],

              })
       return {
          'data': ret,
        }, 200
   
