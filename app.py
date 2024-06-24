
import json
import os

import jwt
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

load_dotenv()

from app.middlewares.authorization_validator import authorization_validator
from app.middlewares.request_validator import request_validator
from app.middlewares.token_validator import token_validator
from app.routes.branches.create import create_branch
from app.routes.branches.read import get_branches
from app.routes.branches.read_one import get_branch
from app.routes.branches.update import update_branch
from app.routes.corporates.create import create_company
from app.routes.corporates.read import get_companies
from app.routes.corporates.read_one import get_company
from app.routes.corporates.update import update_company
from app.routes.customers.create import create_customer
from app.routes.customers.read import get_customers
from app.routes.customers.read_one import get_customer
from app.routes.customers.update import update_customer
from app.routes.doctors.create import create_doctor
from app.routes.doctors.read import get_doctors
from app.routes.doctors.read_one import get_doctor
from app.routes.doctors.update import update_doctor
from app.routes.packages.create import create_package
from app.routes.packages.read import get_packages
from app.routes.packages.read_one import get_package
from app.routes.packages.update import update_package
from app.routes.product_categories.create import create_product_category
from app.routes.product_categories.read import get_product_categories
from app.routes.product_categories.read_one import get_product_category
from app.routes.product_categories.update import update_product_category
from app.routes.products.create import create_product
from app.routes.products.read import get_products
from app.routes.products.read_one import get_product
from app.routes.products.update import update_product
from app.routes.roles.create import create_role
from app.routes.roles.read import get_roles
from app.routes.roles.read_one import get_role
from app.routes.roles.read_resources import get_resources
from app.routes.roles.update import update_role
from app.routes.transaction.create import create_transaction
from app.routes.transaction.read import get_transactions
from app.routes.transaction.read_one import get_transaction
from app.routes.transaction.update import update_transaction
from app.routes.users.auth import login
from app.routes.users.read import get_users
from app.routes.users.read_one import get_user
from app.routes.users.register import register
from app.routes.users.update import update_user

PORT = os.getenv('PORT')
HOST = os.getenv('HOST')
JWT_SECRET = os.getenv('JWT_SECRET_KEY')

app = Flask(__name__)
cors = CORS(app, origins=["*", "*"])
@app.before_request
def hook():
   validators = [token_validator, request_validator]
   for validator in validators:
      res = validator()
      if res is not None:
         return res 
   
   

@app.route('/', methods=['GET'])
def home():
  return 'hello world'

app.register_blueprint(login)
app.register_blueprint(register)
app.register_blueprint(get_users)
app.register_blueprint(create_product)
app.register_blueprint(update_product)
app.register_blueprint(get_products)
app.register_blueprint(get_product)
app.register_blueprint(get_user)
app.register_blueprint(get_roles)
app.register_blueprint(create_doctor)
app.register_blueprint(get_doctor)
app.register_blueprint(get_doctors)
app.register_blueprint(update_doctor)
app.register_blueprint(create_product_category)
app.register_blueprint(get_product_category)
app.register_blueprint(get_product_categories)
app.register_blueprint(update_product_category)
app.register_blueprint(create_branch)
app.register_blueprint(get_branch)
app.register_blueprint(get_branches)
app.register_blueprint(update_branch)
app.register_blueprint(get_companies)
app.register_blueprint(get_company)
app.register_blueprint(create_company)
app.register_blueprint(update_company)
app.register_blueprint(create_customer)
app.register_blueprint(get_customer)
app.register_blueprint(get_customers)
app.register_blueprint(update_customer)
app.register_blueprint(create_package)
app.register_blueprint(get_package)
app.register_blueprint(get_packages)
app.register_blueprint(update_package)
app.register_blueprint(create_role)
app.register_blueprint(get_role)
app.register_blueprint(update_role)
app.register_blueprint(update_user)
app.register_blueprint(get_resources)
app.register_blueprint(create_transaction)
app.register_blueprint(get_transaction)
app.register_blueprint(get_transactions)
app.register_blueprint(update_transaction)

get_resources
if __name__ == '__main__':
   app.run(HOST, PORT, debug=True)