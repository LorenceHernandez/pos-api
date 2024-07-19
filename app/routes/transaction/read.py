from pydash import merge, omit
import pymongo
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import branches, customers, doctors, transactions
from app.models.Transaction import Transaction

get_transactions = Blueprint("/transactions", __name__)

@get_transactions.route('/transactions', methods=['GET'])
def _get_transactions():

   data = transactions.find().sort({"transaction_date":-1})

   transaction_list = []
   for transaction in data:
         transaction_customer = None
         try: 
            customer_id = transaction.get('customerId')

            if customer_id:
               customer = customers.find_one({"_id": ObjectId(customer_id)})

               if customer:
                    transaction_customer = {
                         "_id": str(customer.get('_id')),
                         "firstName": customer.get("first_name"),
                         "middleName": customer.get("middle_name"),
                         "lastName": customer.get("last_name"),
                         "age": customer.get("age"),
                         "gender": customer.get("gender"),
                         "address": customer.get("address"),
                         "customerType": customer.get("customer_type"),
                         "discount": customer.get("discount"),
                         "discountType": customer.get("discount_type"),
                         "isCorporate": customer.get("is_corporate")
                    }
         except Exception as e: 
              print(e)
              transaction_customer = None
         user_branch = None
         
         try: 
            branch = branches.find_one({"_id": ObjectId(transaction["branchId"])})
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


     #     referred_by = None
     #     requested_by = None
     #     try: 
     #           doctor = doctors.find_one({"_id": ObjectId(record["referred_by"])})
     #           if doctor:
     #                referred_by = {
     #                     "_id": str(doctor["_id"]),
     #                     "firstName": doctor["firstName"],
     #                     "middleName": doctor["middleName"],
     #                     "lastName": doctor["lastName"],
     #                     "age": doctor["age"],
     #                     "gender": doctor["gender"],
     #                     "address": doctor["address"],
     #                     "isMember": doctor["isMember"],
     #                     "created_by": doctor["created_by"],
     #                     "created_at": doctor["created_at"]
     #                }
     #     except Exception as e: 
     #                referred_by = None
     #     try: 
     #                doctor = doctors.find_one({"_id": ObjectId(record["requested_by"])})
     #                if doctor:
     #                     requested_by = {
     #                          "_id": str(doctor["_id"]),
     #                          "firstName": doctor["firstName"],
     #                          "middleName": doctor["middleName"],
     #                          "lastName": doctor["lastName"],
     #                          "age": doctor["age"],
     #                          "gender": doctor["gender"],
     #                          "address": doctor["address"],
     #                          "isMember": doctor["isMember"],
     #                          "created_by": doctor["created_by"],
     #                          "created_at": doctor["created_at"]
     #                     }
     #     except Exception as e: 
     #                requested_by = None
     
         new_transaction = merge(
             omit(transaction, '_id', 'customerId', 'branchId'),
             { 
               "id": str(transaction['_id']),
               "customer": transaction_customer,
               "branch": user_branch,
             },
          )
         transaction_list.append(new_transaction)
   return {
          'data': transaction_list,
        }, 200
      
