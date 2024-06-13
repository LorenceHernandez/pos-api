
import os

import jwt
from flask import Blueprint, request

JWT_SECRET = os.getenv('JWT_SECRET_KEY')

route_constraints = [
  { 'route': '/login', 'params': ['username', 'password'], 'content-type': 'urlencoded', 'method': 'POST' },
  { 'route': '/user/register', 'params': ['username', 'password', 'first_name', 'last_name', 'role_id'], 'content-type': 'urlencoded', 'method': 'POST' },
  { 'route': '/user/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/product/create', 'params': ['sku', 'price', 'name', 'inventoryPrerequisite', 'category', 'description'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/product/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/product', 'params': ['id'], 'content-type': 'urlencoded', 'method': 'GET' },
  { 'route': '/doctor/create', 'params': ['firstName', 'lastName', 'middleName', 'age', 'gender', "address", "isMember"], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/doctor', 'params': ['id'], 'content-type': 'urlencoded', 'method': 'GET' },
  { 'route': '/doctor/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/product/category/create', 'params': ['name', 'description'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/product/category', 'params': ['id'], 'content-type': 'urlencoded', 'method': 'GET' },
  { 'route': '/product/category/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/branch/create', 'params': ['name', 'address'], 'content-type': 'json', 'method': 'GET' },
  { 'route': '/branch', 'params': ['id'], 'content-type': 'json', 'method': 'GET' },
  { 'route': '/branch/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
]

field_constraints = [
  { 'field': ['price'], 'type': 'float' },
  { 'field': ['id'], 'type': 'string', 'min': 24, max: '24' }, #for ObjectId
  { 'field': ['id'], 'type': 'string', 'length': 24 }
]

def request_validator():
 for i in route_constraints:
  if i['route'] == request.path:
    for p in i['params']:
     if i['method'] == 'POST': 
      if i['content-type'] == 'urlencoded':
        if p not in request.form:
          return { 
            'message': p + ' field is required' 
          }, 400
      elif i['content-type'] == 'json':
        if p not in request.get_json():
          return { 
            'message': p + ' field is required' 
          }, 400
     elif i['method'] == 'GET':
      if p not in request.args:
       return { 
        'message': p + ' field is required' 
       }, 400
      


      

  