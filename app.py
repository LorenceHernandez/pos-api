
import json
from flask import Flask, jsonify, request
from pymongo import MongoClient
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

from app.routes.auth import login
from app.routes.register import register
from app.routes.update_role import update_role
from app.routes.users import get_users


PORT = os.getenv('PORT')
HOST = os.getenv('HOST')

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
  return 'hello world'

app.register_blueprint(login)
app.register_blueprint(register)
app.register_blueprint(update_role)
app.register_blueprint(get_users)



 
if __name__ == '__main__':
   app.run(HOST, PORT, debug=True)