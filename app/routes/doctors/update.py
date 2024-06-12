
import os
from datetime import datetime

import bcrypt
import jwt
from bson import ObjectId
from flask import Blueprint, request

from app.database.config import doctors

update_doctor = Blueprint("/doctor/edit", __name__)

@update_doctor.route('/doctor/edit', methods=['POST'])
def _update_doctor():
   id = request.form['id']
   update_val = {}

   try:
        if 'age' in request.form:
            update_val['age'] = int(request.form['age'])
        if 'isMember' in request.form:
            update_val['isMember'] = bool(int(request.form['isMember']))
   except:
      return {
         'message': 'data format is invalid',
         'code': 23
   }, 200

   if 'firstName' in request.form:
      update_val['firstName'] = request.form['firstName']
   if 'lastName' in request.form:
      update_val['lastName'] = request.form['lastName']
   if 'middleName' in request.form:
      update_val['middleName'] = request.form['middleName']
   if 'gender' in request.form:
      update_val['gender'] = request.form['gender']
   if 'address' in request.form:
      update_val['address'] = request.form['address']
   
   if not update_val:
        return {
            'message': 'atleast one field is required when updating a user',
            'code': 25
        }, 200
   filter = { '_id': ObjectId(id) }
   new_val = { "$set": update_val }
   #array_filt = {"arrayFilters": [{'[0].id': '1'}]}

   print(new_val)
   res = doctors.update_one(filter, new_val)
   if res.modified_count > 0:
      return {
         'message': 'Doctor update success',
         'code': 18
      }, 200
   else:
      return {
         'message': 'Unable to update doctor',
         'code': 16
      }


