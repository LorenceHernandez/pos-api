
import os
from datetime import datetime
from operator import itemgetter

import bcrypt
import jwt
from flask import Blueprint, g, request

from app.database.config import corporates

create_company = Blueprint("/corporate/create", __name__)

@create_company.route('/corporate/create', methods=['POST'])
def _create_company():
   request_data = request.get_json()
   name = request_data['name']
   created_by = g.user_id
   created_at = datetime.now()
   
   doc = corporates.insert_one({
      "name": name,
      "created_by": created_by,
      "created_at": created_at
   })
   
   if doc.inserted_id:
      return {
         'message': 'Corporate successfully created',
         'code': 15,
      }, 200
   else:
      return {
         'message': 'Unable to add corporate.',
         'code': 30,
      }, 200


