
import os
from datetime import datetime
from operator import itemgetter

import bcrypt
import jwt
from bson import ObjectId
from flask import Blueprint, g, request

from app.database.config import customers

create_customer = Blueprint("/customer/create", __name__)

@create_customer.route('/customer/create', methods=['POST'])
def _create_customer():
   request_data = request.get_json()
   f_name = request_data['firstName']
   m_name = request_data['middleName']
   l_name = request_data['lastName']
   age = request_data['age']
   gender = request_data['gender']
   address = request_data['address']
   customer_type = request_data['customerType']
   contact_number = request_data['contactNumber']
   discount = 0
   discount_type = None
   corporate_id = None
   tin_number = None
   is_corporate = False 

   created_by = g.user_id
   created_at = datetime.now()
   
   if 'isCorporate' in request_data:
      is_corporate = request_data['isCorporate']
   if 'discount' in request_data:
      discount = request_data['discount']
   if 'discountType' in request_data:
      discount_type = request_data['discountType']
   if 'corporateId' in request_data:
      corporate_id = request_data['corporateId']
   if 'tinNumber' in request_data:
      tin_number = request_data['tinNumber']

   try: 
       float(discount)
       if 'corporateId' in request_data:
          ObjectId(corporate_id)

   except:
        return {
            'message': 'data format is invalid',
            'code': 23
        }, 401

   doc = customers.insert_one({
      "first_name": f_name,
      "middle_name": m_name,
      "last_name": l_name,
      "age": age,
      "gender": gender,
      "address": address,
      "customer_type": customer_type,
      "discount": float(discount),
      "discount_type": discount_type,
      "corporate_id": corporate_id,
      "tin_number": tin_number,
      "contact_number": contact_number,
      "is_corporate": is_corporate,
      "created_by": created_by,
      "created_at": created_at
   })
   
   if doc.inserted_id:
      return {
         'message': 'Customer successfully created',
         'code': 15,
      }, 200
   else:
      return {
         'message': 'Unable to add customer.',
         'code': 30,
      }, 200


