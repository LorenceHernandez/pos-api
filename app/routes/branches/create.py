
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
   name, street_address, city, state, postal_code, contact, email = request_data['name'], request_data['streetAddress'], request_data['city'], request_data['state'], request_data['postalCode'], request_data['contactNo'], request_data['emailAddress']
   tin = request_data = ['tin']
   created_by = g.user_id
   created_at = datetime.now()
   
   doc = branches.insert_one({
      "name": name,
      "street_address": street_address,
      "city": city,
      "state": state,
      "postal_code": postal_code,
      "is_active": True,
      "contact_number": contact,
      "email_address": email,
      "tin": tin,
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


