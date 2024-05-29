
import json
from flask import Flask, jsonify, request
from pymongo import MongoClient
import jwt
import os
from dotenv import load_dotenv

load_dotenv()



JWT_KEY = os.getenv('JWT_SECRET_KEY')
PORT = os.getenv('PORT')
HOST = os.getenv('HOST')
MONGO_PORT = os.getenv('MONGO_PORT')
MONGO_HOST = os.getenv('MONGO_HOST')

app = Flask(__name__)
client = MongoClient(MONGO_HOST, int(MONGO_PORT))
db = client.pos
users = db.users

@app.route('/login', methods=['POST'])
def login():
 user = list(users.find({"username": request.form['username']}))

 if len(user) > 0:   
   if user[0]['password'] == request.form['password']: 
    token = jwt.encode({"user_id": str(user[0]['_id'])}, JWT_KEY,algorithm="HS256")
    return {
      'token': token
    }, 200
 else: 
    return {
      'error': 'wrong username or password'
    }, 200
 

@app.route('/', methods=['GET'])
def home():
  return {
    'api is running'
  }, 200
 
if __name__ == '__main__':
   app.run(HOST, PORT)