
import os
from datetime import datetime
from operator import itemgetter

import bcrypt
import jwt
from flask import Blueprint, g, request

from app.database.config import doctors

create_doctor = Blueprint("/doctor/create", __name__)

@create_doctor.route('/doctor/create', methods=['POST'])
def _create_doctor():
   firstName, middleName, lastName, age, gender, address = request.form['firstName'], request.form['middleName'], request.form['lastName'], request.form['age'] ,request.form['gender'] ,request.form['address']

   isMember = request.form['isMember']
   try:
        int(age)
        isMember = bool(int(isMember))
   except:
        return {
            'message': 'data format is invalid',
            'code': 23
        }, 200

   created_by = g.user_id
   create_at = datetime.now()

   
   doc = doctors.insert_one({
      "firstName": firstName,
      "middleName": middleName,
      "lastName": lastName,
      "age": int(age),
      "gender": gender,
      "address": address,
      "isMember": isMember,
      "created_by": created_by,
      "created_at": create_at,
   })
   
   if doc.inserted_id:
      return {
         'message': 'Doctor successfully created',
         'code': 15,
      }, 200
   else:
      return {
         'message': 'Unable to add doctor',
         'code': 30,
      }, 200


