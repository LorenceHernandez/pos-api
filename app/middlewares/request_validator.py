
import os

import jwt
from flask import Blueprint, request

JWT_SECRET = os.getenv('JWT_SECRET_KEY')

route_constraints = [
  { 'route': '/login', 'params': ['username', 'password'], 'content-type': 'urlencoded', 'method': 'POST' },
  { 'route': '/user/register', 'params': ['branchIds', 'username', 'password', 'firstName', 'lastName', 'roleId'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/user/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/product/create', 'params': ['sku', 'price', 'name', 'inventoryPrerequisite', 'categoryId', 'description'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/product/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/product', 'params': ['id'], 'content-type': 'urlencoded', 'method': 'GET' },
  { 'route': '/doctor/create', 'params': ['firstName', 'lastName', 'middleName', 'age', 'gender', "address", "isMember"], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/doctor', 'params': ['id'], 'content-type': 'urlencoded', 'method': 'GET' },
  { 'route': '/doctor/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/product/category/create', 'params': ['name', 'description'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/product/category', 'params': ['id'], 'content-type': 'urlencoded', 'method': 'GET' },
  { 'route': '/product/category/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/branch/create', 'params': ['tin', 'name', 'streetAddress', 'city', 'state', 'postalCode', 'contactNumber', 'emailAddress'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/branch', 'params': ['id'], 'content-type': 'json', 'method': 'GET' },
  { 'route': '/branch/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/corporate/create', 'params': ['name','streetAddress', 'city', 'state', 'postalCode', 'contactNo', 'emailAddress'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/corporate/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/corporate', 'params': ['id'], 'content-type': 'json', 'method': 'GET' },
  { 'route': '/customer/create', 'params': ['firstName', 'lastName', 'middleName', 'age', 'gender', 'address', 'customerType', 'contactNumber', 'birthDate'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/customer/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/customer', 'params': ['id'], 'content-type': 'json', 'method': 'GET' },
  { 'route': '/package/create', 'params': ['name', 'description', 'labTest', 'packageType'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/package/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/package', 'params': ['id'], 'content-type': 'json', 'method': 'GET' },
  { 'route': '/roles/create', 'params': ['name', 'authorizations'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/roles/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/role', 'params': ['id'], 'content-type': 'json', 'method': 'GET' },
  { 'route': '/transaction/create', 'params': ['branchId'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/transaction/active', 'params': [], 'content-type': 'json', 'method': 'GET' },
  { 'route': '/transaction/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/transaction', 'params': ['id'], 'content-type': 'json', 'method': 'GET' },
  { 'route': '/discount/create', 'params': ['name', 'description', 'value', 'type'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/discount/edit', 'params': ['id'], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/discount', 'params': ['id'], 'content-type': 'json', 'method': 'GET' },
  { 'route': '/sales', 'params': ['cashierId', 'branchId'], 'content-type': 'json', 'method': 'GET' },
  { 'route': '/balance/create', 'params': [], 'content-type': 'json', 'method': 'POST' },
  { 'route': '/balance', 'params': [], 'content-type': 'json', 'method': 'GET' },
]


field_constraints = [
  { 'fields': ['price', 'discount', ], 'type': 'float' },
  { 'fields': ['id'], 'type': 'objectId' }
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
      


      

  