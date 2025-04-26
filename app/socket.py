

from flask_socketio import SocketIO
from flask import Flask, request

from app import config


socketio = SocketIO(debug=True, cors_allowed_origins='*')

def handle_connected():
   print(f'\nClient ID {request.headers.get("api-id")}')
   print(f'Client connected {request.headers}')

def create_socket_instance(app: Flask):
   
   socketio.init_app(app)
   socketio.on_event('connect', handle_connected)

   return socketio