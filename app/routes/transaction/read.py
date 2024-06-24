from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import transactions

get_transactions = Blueprint("/transactions", __name__)

@get_transactions.route('/transactions', methods=['GET'])
def _get_transactions():

   res = transactions.find()

   ret = []
   for record in res:
         ret.append({
            "_id": str(record["_id"]),
            "transactionNo": record["transaction_no"],
            "transactionDate": record["transaction_date"],
            "status": record["status"],
            "branchId": record["branch_id"],
            "customerId": record.get('customer_id'),
            "requestedBy": record.get('requested_by'),
            "referredBy": record.get('referred_by'),
            "tenderType": record.get('tender_type'),
            "tenderAmount": record.get('tender_amount'),
            "change": record.get('change'),
          })
   return {
          'data': ret,
        }, 200
      
