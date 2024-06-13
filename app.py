
import json
import os

import jwt
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

load_dotenv()

from app.middlewares.request_validator import request_validator
from app.middlewares.token_validator import token_validator
from app.routes.doctors.create import create_doctor
from app.routes.doctors.read import get_doctors
from app.routes.doctors.read_one import get_doctor
from app.routes.doctors.update import update_doctor
from app.routes.product_categories.create import create_product_category
from app.routes.product_categories.read import get_product_categories
from app.routes.product_categories.read_one import get_product_category
from app.routes.product_categories.update import update_product_category
from app.routes.products.create import create_product
from app.routes.products.read import get_products
from app.routes.products.read_one import get_product
from app.routes.products.update import update_product
from app.routes.roles.read import get_roles
from app.routes.users.auth import login
from app.routes.users.read import get_users
from app.routes.users.read_one import get_user
from app.routes.users.register import register
from app.routes.users.update import update_role

PORT = os.getenv('PORT')
HOST = os.getenv('HOST')
JWT_SECRET = os.getenv('JWT_SECRET_KEY')

app = Flask(__name__)
cors = CORS(app, origins=["*", "*"])

@app.before_request
def hook():
   token_validator_result = token_validator()
   if token_validator_result is not None:
      return token_validator_result
   request_validator_result = request_validator()
   if request_validator_result is not None:
      return request_validator_result
   
   


@app.route('/', methods=['GET'])
def home():
  return 'hello world'

app.register_blueprint(login)
app.register_blueprint(register)
app.register_blueprint(update_role)
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
 
if __name__ == '__main__':
   app.run(HOST, PORT, debug=True)