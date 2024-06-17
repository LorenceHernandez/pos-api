
import os
from datetime import datetime

import bcrypt
import jwt
from bson import ObjectId
from flask import Blueprint, request

from app.database.config import customers

update_customer = Blueprint("/customer/edit", __name__)

@update_customer.route('/customer/edit', methods=['POST'])
def _update_customer():
   request_data = request.get_json()
   update_val = {}
   id = request_data['id']

   try:
        ObjectId(id)
        if 'corporateId' in request_data:
            update_val['corporate_id'] = request_data['corporateId']
        if 'isActive' in request_data:
            update_val['is_active'] = bool(request_data['isActive'])
        if 'discount' in request_data:
           update_val['discount'] = float(request_data['discount'])
   except:
      return {
         'message': 'data format is invalid',
         'code': 23
   }, 200

   if 'firstName' in request_data:
      update_val['first_name'] = request_data['firstName']
   if 'middleName' in request_data:
      update_val['middle-name'] = request_data['middleName']
   if 'lastName' in request_data:
      update_val['last_name'] = request_data['lastName']
   if 'age' in request_data:
      update_val['age'] = request_data['age']
   if 'gender' in request_data:
      update_val['gender'] = request_data['gender']
   if 'address' in request_data:
      update_val['address'] = request_data['address']
   if 'customerType' in request_data:
      update_val['customer_type'] = request_data['customerType']
   if 'discountType' in request_data:
      update_val['discount_type'] = request_data['discountType']
   if 'isCorporate' in request_data:
      update_val['is_corporate'] = request_data['isCorporate']
   
   if not update_val:
        return {
            'message': 'atleast one field is required when updating a user',
            'code': 25
        }, 200
   filter = { '_id': ObjectId(id) }
   new_val = { "$set": update_val }
   #array_filt = {"arrayFilters": [{'[0].id': '1'}]}

   print(new_val)
   res = customers.update_one(filter, new_val)
   if res.modified_count > 0:
      return {
         'message': 'Customer update success',
         'code': 18
      }, 200
   else:
      return {
         'message': 'Unable to update customer',
         'code': 16
      }


