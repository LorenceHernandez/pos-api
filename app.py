
import json
from flask import Flask, jsonify, request
from pymongo import MongoClient
import jwt
import os
from dotenv import load_dotenv
load_dotenv()
from app.routes.auth import login
from app.routes.register import register


PORT = os.getenv('PORT')
HOST = os.getenv('HOST')

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
  return 'hello world'

app.register_blueprint(login)
app.register_blueprint(register)



 
if __name__ == '__main__':
   app.run(HOST, PORT, debug=True)