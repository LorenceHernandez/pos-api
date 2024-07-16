import pymongo
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import branches, customers, doctors, transactions

get_transactions = Blueprint("/transactions", __name__)

@get_transactions.route('/transactions', methods=['GET'])
def _get_transactions():

   res = transactions.find().sort({"transaction_date":-1})

   ret = []
   for record in res:
         transaction_customer = None
         try: 
            customer_id = record.get('customer_id')

            if customer_id:
               customer = customers.find_one({"_id": ObjectId(customer_id)})

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


         referred_by = None
         requested_by = None
         try: 
               doctor = doctors.find_one({"_id": ObjectId(record["referred_by"])})
               if doctor:
                    referred_by = {
                         "_id": str(doctor["_id"]),
                         "firstName": doctor["firstName"],
                         "middleName": doctor["middleName"],
                         "lastName": doctor["lastName"],
                         "age": doctor["age"],
                         "gender": doctor["gender"],
                         "address": doctor["address"],
                         "isMember": doctor["isMember"],
                         "created_by": doctor["created_by"],
                         "created_at": doctor["created_at"]
                    }
         except Exception as e: 
                    referred_by = None
         try: 
                    doctor = doctors.find_one({"_id": ObjectId(record["requested_by"])})
                    if doctor:
                         requested_by = {
                              "_id": str(doctor["_id"]),
                              "firstName": doctor["firstName"],
                              "middleName": doctor["middleName"],
                              "lastName": doctor["lastName"],
                              "age": doctor["age"],
                              "gender": doctor["gender"],
                              "address": doctor["address"],
                              "isMember": doctor["isMember"],
                              "created_by": doctor["created_by"],
                              "created_at": doctor["created_at"]
                         }
         except Exception as e: 
                    requested_by = None
     
         ret.append({
            "_id": str(record["_id"]),
            "transactionNo": record["transaction_no"],
            "transactionDate": record["transaction_date"],
            "status": record["status"],
            "branch": user_branch,
            "customer": transaction_customer,
            "requestedBy": requested_by,
            "referredBy": referred_by,
            "tenderType": record.get('tender_type'),
            "tenderAmount": record.get('tender_amount'),
            "change": record.get('change'),
          })
   return {
          'data': ret,
        }, 200
      
