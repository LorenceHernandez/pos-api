
import json
import os

import jwt
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

load_dotenv()

from app.middlewares.request_validator import request_validator
from app.middlewares.token_validator import token_validator
from app.routes.auth import login
from app.routes.products.create import create_product
from app.routes.products.read import get_products
from app.routes.products.read_one import get_product
from app.routes.products.update import update_product
from app.routes.register import register
from app.routes.update_role import update_role
from app.routes.users.read import get_users
from app.routes.users.read_one import get_user

PORT = os.getenv('PORT')
HOST = os.getenv('HOST')
JWT_SECRET = os.getenv('JWT_SECRET_KEY')

app = Flask(__name__)
cors = CORS(app)

excluded_routes_for_validator = [
  '/login'
  '/user/register'   
]
from flask import Flask

app = Flask(__name__)
cors = CORS(app)
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


 
if __name__ == '__main__':
   app.run(HOST, PORT, debug=True)