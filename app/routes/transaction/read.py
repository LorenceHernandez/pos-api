from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request
import pymongo
from app.database.config import transactions, branches, customers

get_transactions = Blueprint("/transactions", __name__)

@get_transactions.route('/transactions', methods=['GET'])
def _get_transactions():

   res = transactions.find().sort({"transaction_date":-1})

   ret = []
   for record in res:
         transaction_customer = None
         try: 
            customer = customers.find_one({"_id": ObjectId(record["customer_id"])})
            if branch:
              transaction_customer = {
                          "_id": str(branch["_id"]),
                          "name": branch["name"],
                          "streetAddress": branch["street_address"],
                          "city": branch["city"],
                          "state": branch["state"],
                          'tin': branch.get('tin'),
                          "postalCode": branch["postal_code"],
                          "contactNumber": branch["contact_number"],
                          "emailAddress": branch["email_address"],
                          "isActive": branch["is_active"]
              }
         except Exception as e: 
              transaction_customer = None
         user_branch = None
         try: 
            branch = branches.find_one({"_id": ObjectId(record["branch_id"])})
            if branch:
              user_branch = {
                          "_id": str(branch["_id"]),
                          "name": branch["name"],
                          "streetAddress": branch["street_address"],
                          "city": branch["city"],
                          "state": branch["state"],
                          'tin': branch.get('tin'),
                          "postalCode": branch["postal_code"],
                          "contactNumber": branch["contact_number"],
                          "emailAddress": branch["email_address"],
                          "isActive": branch["is_active"]
              }
         except Exception as e: 
              user_branch = None
         ret.append({
            "_id": str(record["_id"]),
            "transactionNo": record["transaction_no"],
            "transactionDate": record["transaction_date"],
            "status": record["status"],
            "branch": user_branch,
            "customer": transaction_customer,
            "requestedBy": record.get('requested_by'),
            "referredBy": record.get('referred_by'),
            "tenderType": record.get('tender_type'),
            "tenderAmount": record.get('tender_amount'),
            "change": record.get('change'),
          })
   return {
          'data': ret,
        }, 200
      
