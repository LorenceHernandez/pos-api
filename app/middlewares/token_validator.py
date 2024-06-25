
import os

import jwt
from flask import Blueprint, g, request

JWT_SECRET = os.getenv('JWT_SECRET_KEY')

excluded_routes_for_validator = [
  '/login',  
]

def token_validator(): 
   if request.path not in excluded_routes_for_validator:
       headers = request.headers
       bearer = headers.get('Authorization')

       if bearer:
          auth = bearer.split(' ')
          if len(auth) > 1:
            token = auth[1]
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            
            if decoded_token['user_id'] is None:
                return {
                    'message': 'Unauthorized',
                    'code': 9
                }, 200
            else:
               print(decoded_token['user_id'] + ' authorized')
               g.user_id = decoded_token['user_id']
               return None
       else:
         return {
             'message': 'Unauthorized',
             'code': 9
          }, 200