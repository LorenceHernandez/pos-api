
import os
import uuid
from datetime import datetime
from operator import itemgetter

import bcrypt
import jwt
from bson import ObjectId
from flask import Blueprint, g, request

from app.database.config import transactions

create_transaction = Blueprint("/transaction/create", __name__)

@create_transaction.route('/transaction/create', methods=['POST'])
def _create_transaction():
   request_data = request.get_json()
   branch_id = request_data['branchId']
   created_by = g.user_id
   created_at = datetime.now()
   try:
      ObjectId(branch_id)
   except: 
      return {
         'message': 'data format is invalid',
         'code': 23
   }, 401
   transaction_no = str(uuid.uuid4())
   status = 'active'

   doc = transactions.insert_one({
      "transaction_no": transaction_no,
      "transaction_date": created_at,
      "status": status,
      "branch_id": branch_id,
      "created_by": created_by,
      "created_at": created_at
   })
   
   if doc.inserted_id:
      return {
         'data': {
            "id": str(doc.inserted_id),
            "transactionNo": transaction_no,
            "transactionDate": created_at,
            "status": status,
            "branch_id": branch_id,
         },
         'code': 15,
      }, 200
   else:
      return {
         'message': 'Unable to create transaction',
         'code': 30,
      }, 200


