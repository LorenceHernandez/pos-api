
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
   name, street_address, city, state, postal_code, contact, email = request_data['name'], request_data['streetAddress'], request_data['city'], request_data['state'], request_data['postalCode'], request_data['contactNo'], request_data['emailAddress']
   tin_id = request_data['tinId']
   created_by = g.user_id
   created_at = datetime.now()
   
   doc = corporates.insert_one({
      "name": name,
      "street_address": street_address,
      "city": city,
      "state": state,
      "postal_code": postal_code,
      "contact_number": contact,
      "email_address": email,
      "created_by": created_by,
      "created_at": created_at,
      "tin_id": tin_id
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


