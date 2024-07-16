from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import corporates, customers

get_customer = Blueprint("/customer", __name__)

@get_customer.route('/customer', methods=['GET'])
def _get_customer():
   try: 
        ObjectId(request.args.get('id'))
   except:
        return {
            'message': 'data format is invalid',
            'code': 23
        }, 401

   record = customers.find_one({"_id": ObjectId(request.args.get('id'))})

   if record: 
       corporate = None
       try: 
           corp_record = corporates.find_one({"_id": ObjectId(record["corporate_id"])})
           if corp_record: 
               corporate = {
                   "id": str(corp_record['_id']),
                   "name": corp_record['name']
                }
       except: 
            corporate = None
       return {
          'data': {
            "_id": str(record["_id"]),
            "firstName": record["first_name"],
            "middleName": record["middle_name"],
            "lastName": record["last_name"],
            "age": record["age"],
            "gender": record["gender"],
            "tinNumber": record.get('tin_number'),
            "contactNumber": record.get('contact_number'),
            "address": record["address"],
            "customerType": record["customer_type"],
            "discount": record["discount"],
            "discountType": record["discount_type"],
            "corporate": corporate,
            "isCorporate": record["is_corporate"]
          },
       }, 200 
   else:
        return {
            'message': 'Customer not found',
            'code': 20
        }, 200
   
