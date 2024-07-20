import sys

from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, g, request

from app.database.config import branches, customers, doctors, transactions

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
               customer = customers.find_one({"_id": ObjectId(record["customerId"])})
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
          branch = branches.find_one({"_id": ObjectId(record["branchId"])})

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
     referred_by = None
     requested_by = None
     try: 
               doctor = doctors.find_one({"_id": ObjectId(record["referredBy"])})
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
                    doctor = doctors.find_one({"_id": ObjectId(record["requestedBy"])})
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
    
     return {
          "id": str(record["_id"]),
          "transactionNo": record["transactionNo"],
          "transactionDate": record["transactionDate"],
          "status": record["status"],
          "branch": user_branch,
          "customer": transaction_customer,
          "services": record.get('services'),
          "requestedBy": requested_by,
          "referredBy": referred_by,
          "tenderType": record.get('tenderType'),
          "tenderAmount": record.get('tenderAmount'),
          "paymentDue": record.get('paymentDue'),
          "subTotal": record.get('subTotal'),
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
