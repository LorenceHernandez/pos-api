from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import transactions, branches, customers

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

   if record: 
       return {
          'data': {
            "_id": str(record["_id"]),
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
       }, 200 
   else:
        return {
            'message': 'Branch not found',
            'code': 20
        }, 200
   
