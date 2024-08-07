
import os
from datetime import date, datetime

import bcrypt
import jwt
from bson import ObjectId
from flask import Blueprint, request
from pydash import omit

from app.database.config import (customers, doctors, packages,
                                 product_categories, products, sales,
                                 transactions, users)
from app.database.store import insert_one
from app.models.Transaction import Transaction
from app.utils.filter_values import filterValues
from app.utils.utils import getLocalTime

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
   
   if res.modified_count > 0:
      updated_trans = transactions.find_one({"_id": ObjectId(id)})
      # FOR REFACTORING
      if transaction_dict['status'].lower() == 'completed':
         categories = product_categories.find()
         services = updated_trans.get('services')
         orNo = updated_trans.get('invoiceNo')
         amount = updated_trans.get('paymentDetails').get('paymentDue')
         branch = updated_trans.get('branchId')
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
            if service['source'] == "package": 
               for item in service['items']:
                  name.append(item['name'])
            else:
               name.append(service['name'])
         
         for service in services:
            if service['source'] == "package":  
                  for category in _categories:  
                     if category['name'].lower() == 'package':
                        for item in service['items']:
                           category['price'] +=  item['amount']
            else:
                  for category in _categories:
                     if category['id'] == service['category']['id']:
                        category['price'] += service['amount']

         sale = insert_one('sales', {
            'customerData': updated_trans.get('customerData'),
            'labExams': ', '.join(name),
            'orNo': orNo,
            'amount': amount,
            'categories': _categories,
            'discount': discount,
            'referrer': doctor_full_name,
            'branch': branch,
            'cashierId': updated_trans['createBy'],
            'transactionId': str(updated_trans['_id']),
            'date': str(date.today()),
            'created_at': getLocalTime()
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


