
import os
from datetime import datetime

import bcrypt
import jwt
from bson import ObjectId
from flask import Blueprint, request

from app.database.config import transactions

update_transaction = Blueprint("/transaction/edit", __name__)

@update_transaction.route('/transaction/edit', methods=['POST'])
def _update_transaction():
   request_data = request.get_json()
   update_val = {}
   id = request_data['id']

   try:
        ObjectId(id)
        if 'referredBy' in request_data:
          ObjectId(request_data['referredBy'])
        if 'requestedBy' in request_data:
          ObjectId(request_data['requestedBy'])
        if 'customerId' in request_data:
          ObjectId(request_data['customerId'])
        if 'tenderAmount' in request_data:
         float(request_data['tenderAmount'])
        if 'change' in request_data:
         float(request_data['change'])
   except:
      return {
         'message': 'data format is invalid',
         'code': 23
   }, 200

   if 'status' in request_data:
      update_val['status'] = request_data['status']
   if 'customerId' in request_data:
      update_val['customer_id'] = request_data['customerId']
   if 'requestedBy' in request_data:
      update_val['requested_by'] = request_data['requestedBy']
   if 'referredBy' in request_data:
      update_val['referred_by'] = request_data['referredBy']
   if 'tenderType' in request_data:
      update_val['tender_type'] = request_data['tenderType']
   if 'tenderAmount' in request_data:
      update_val['tender_amount'] = request_data['tenderAmount']
   if 'change' in request_data:
      update_val['change'] = request_data['change']
   
   if not update_val:
        return {
            'message': 'atleast one field is required when updating a user',
            'code': 25
        }, 200
   filter = { '_id': ObjectId(id) }
   new_val = { "$set": update_val }
   #array_filt = {"arrayFilters": [{'[0].id': '1'}]}

   print(new_val)
   res = transactions.update_one(filter, new_val)
   if res.modified_count > 0:
      return {
         'message': 'Transaction update success',
         'code': 18
      }, 200
   else:
      return {
         'message': 'Unable to update transaction',
         'code': 16
      }


