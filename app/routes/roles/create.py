
import os
from datetime import datetime
from operator import itemgetter

import bcrypt
import jwt
from flask import Blueprint, g, request

from app.database.config import roles

create_role = Blueprint("/role/create", __name__)


@create_role.route('/role/create', methods=['POST'])
def _create_role():
   request_data = request.get_json()
   name, authorizations = request_data['name'], request_data['authorizations']
   
   created_by = g.user_id
   created_at = datetime.now()
   
   doc = roles.insert_one({
      "name": name,
      "authorizations": authorizations,
      "created_by": created_by,
      "created_at": created_at
   })
   
   if doc.inserted_id:
      return {
         'message': 'Role successfully created',
         'code': 15,
      }, 200
   else:
      return {
         'message': 'Unable to add role.',
         'code': 30,
      }, 200


