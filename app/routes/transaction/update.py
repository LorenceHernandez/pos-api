
import os
from datetime import datetime

import bcrypt
import jwt
from bson import ObjectId
from flask import Blueprint, request
from pydash import omit

from app.database.config import (customers, doctors, packages,
                                 product_categories, products, sales,
                                 transactions, users)
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
   transaction_dict = transaction.toDict()
   
   
   filter = { '_id': ObjectId(id) }
   new_val = { "$set": filterValues(omit(transaction_dict, 'id')) }

   res = transactions.update_one(filter, new_val)
   print(res)
   if res.modified_count > 0:
      updated_trans = transactions.find_one({"_id": ObjectId(id)})
      # FOR REFACTORING
      if transaction_dict['status'].lower() == 'completed':
         categories = product_categories.find()
         customer = customers.find_one({"_id": ObjectId(updated_trans['customerId'])})
         customer_full_name = customer["first_name"] + " " + customer["middle_name"] + " " + customer["last_name"]
         services = updated_trans['services']
         orNo = updated_trans['invoiceNo']
         amount = updated_trans['tenderAmount'] - updated_trans['change']
         branch = updated_trans['branchId']
         customer_id = updated_trans['customerId']
         discount = 0
         applied = updated_trans.get('discountApplied')
         if applied: 
            discount = applied['totalDiscount']
         doctor_full_name = ''
         _categories = [{
            'id': None,
            'name': 'Package',
            'price': 0
         }]
         for category in categories:
             _categories.append({
               'id': str(category.get('_id')), 
               'name': category.get('name'),
               'price': 0
             })
             
         
         if updated_trans.get('referredBy'):
            doctor = doctors.find_one({"_id": ObjectId(updated_trans.get('referredBy'))})
            if doctor:
               doctor_full_name = doctor["firstName"] + " " + doctor["middleName"] + " " + doctor["lastName"]
         name = []
         for service in services: 
            name.append(service['name'])
            product = products.find_one({"_id": ObjectId(service['_id'])})
            if product:
               for category in _categories:
                  if service.get('source') == "package":
                     if category['name'].lower() == 'package':
                        category['price'] += service['amount']
                     continue
                  
                  elif category['id'] == product['category_id']: 
                     category['price'] += service['amount']

         sale = sales.insert_one({
            'customerName': customer_full_name,
            'customerId': customer_id,
            'labExams': ', '.join(name),
            'orNo': orNo,
            'amount': amount,
            'categories': _categories,
            'discount': discount,
            'referrer': doctor_full_name,
            'branch': branch,
            'cashierId': updated_trans['createBy']
         })   
         if sale.inserted_id is None:
            return {
               'message': 'Unable to create sale',
               'code': 16
            }
      return {
         'message': 'Transaction update success',
         'code': 18
      }, 200
   else:
      return {
         'message': 'Unable to update transaction',
         'code': 16
      }


