
import os

import jwt
from flask import Blueprint, request

JWT_SECRET = os.getenv('JWT_SECRET_KEY')

route_constraints = [
  { 'route': '/login', 'params': ['email_address', 'password'], 'method': 'POST' },
  { 'route': '/user/register', 'params': ['email_address', 'password'], 'method': 'POST' },
  { 'route': '/user/edit', 'params': ['role_id', 'user_id'], 'method': 'POST' },
  { 'route': '/product/create', 'params': ['sku', 'price', 'name'], 'method': 'POST' },
  { 'route': '/product/edit', 'params': ['id'], 'method': 'POST' },
  { 'route': '/product', 'params': ['id'], 'method': 'GET' },
  { 'route': '/user', 'params': ['id'], 'method': 'GET' },
]

def request_validator():
 for i in route_constraints:
  if i['route'] == request.path:
    for p in i['params']:
     if i['method'] == 'POST': 
      if p not in request.form:
       return { 
        'message': p + ' field is required' 
       }, 400
     elif i['method'] == 'GET':
      if p not in request.args:
       return { 
        'message': p + ' field is required' 
       }, 400
      


      

  