
import os
from datetime import datetime

import bcrypt
import jwt
from bson import ObjectId
from flask import Blueprint, request
from pydash import omit

from app.database.config import transactions
from app.models.Transaction import Transaction
from app.utils.filter_values import filterValues

update_transaction = Blueprint("/transaction/edit", __name__)

@update_transaction.route('/transaction/edit', methods=['POST'])
def _update_transaction():
   request_data = request.get_json()
   id = request_data['id']

   try:
      transaction = Transaction.fromDict(request_data)
   except:
      return {
         'message': 'data format is invalid',
         'code': 23
   }, 200

   
   filter = { '_id': ObjectId(id) }
   new_val = { "$set": filterValues(omit(transaction.toDict(), 'id')) }

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


