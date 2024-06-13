
import os
from datetime import datetime
from operator import itemgetter

import bcrypt
import jwt
from flask import Blueprint, g, request

from app.database.config import branches

create_branch = Blueprint("/branch/create", __name__)

@create_branch.route('/branch/create', methods=['POST'])
def _create_branch():
   request_data = request.get_json()
   name, address = request_data['name'], request_data['address']
   created_by = g.user_id
   created_at = datetime.now()
   
   doc = branches.insert_one({
      "name": name,
      "address": address,
      "is_active": True,
      "created_by": created_by,
      "created_at": created_at
   })
   
   if doc.inserted_id:
      return {
         'message': 'Branch successfully created',
         'code': 15,
      }, 200
   else:
      return {
         'message': 'Unable to add branch.',
         'code': 30,
      }, 200


