import sys
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, g, request
from app.database.config import transactions, branches, customers

get_active_transaction = Blueprint("/transaction/active", __name__)

def get_pending_transaction():
     record = transactions.find_one({
          "status": "active",
          "created_by": g.user_id
     })

     if record is None:
        return None
   

     user_branch = None
     transaction_customer = None
     try: 
               customer = customers.find_one({"_id": ObjectId(record["customer_id"])})
               if customer:
                    transaction_customer = {
                         "_id": str(customer["_id"]),
                         "firstName": customer["first_name"],
                         "middleName": customer["middle_name"],
                         "lastName": customer["last_name"],
                         "age": customer["age"],
                         "gender": customer["gender"],
                         "address": customer["address"],
                         "customerType": customer["customer_type"],
                         "discount": customer["discount"],
                         "discountType": customer["discount_type"],
                         "isCorporate": customer["is_corporate"]
                    }
     except Exception as e: 
          transaction_customer = None
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
     except:
          user_branch = None

     return {
          "id": str(record["_id"]),
          "transactionNo": record["transaction_no"],
          "transactionDate": record["transaction_date"],
          "status": record["status"],
          "branch": user_branch,
          "customer": transaction_customer,
          "services": record.get('services'),
          "requestedBy": record.get('requested_by'),
          "referredBy": record.get('referred_by'),
          "tenderType": record.get('tender_type'),
          "tenderAmount": record.get('tender_amount'),
          "change": record.get('change'),
     },

@get_active_transaction.route('/transaction/active', methods=['GET'])
def _get_active_transaction():
   record = get_pending_transaction()

   if record:
     return { 'data': record }, 200
   else:
     return {
          'data': None,
          'message': 'No active transaction found',
          'code': 20
     }, 200
