from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import transactions

get_transaction = Blueprint("/transaction", __name__)

@get_transaction.route('/transaction', methods=['GET'])
def _get_transaction():
   try: 
        ObjectId(request.args.get('id'))
   except:
        return {
            'message': 'data format is invalid',
            'code': 23
        }, 401

   record = transactions.find_one({"_id": ObjectId(request.args.get('id'))})

   if record: 
       return {
          'data': {
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
          },
       }, 200 
   else:
        return {
            'message': 'Branch not found',
            'code': 20
        }, 200
   
