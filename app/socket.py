

from flask_socketio import SocketIO, disconnect
from flask import Flask, request
import socketio
from app import config


socket = SocketIO(debug=True, cors_allowed_origins='*')

def handle_connected(id):
   print(f'\nClient ID {id}')
   print(f'Client API ID {request.headers.get("api-id")}')
   print(f'Client IP {request.headers.get('referer')}')

   apiId = request.headers.get("api-id")
   apiKey = request.headers.get("api-key")

   if(not apiId or not apiKey):
      disconnect(id)

def create_socket_instance(app: Flask):
   socket.init_app(app)
   socket.on_event('connect', handle_connected)

   return socket

def connect_cloud_socket():
   try:
      socket = socketio.SimpleClient()
      
      socket.connect(config.CLOUD_SERVER_URL, headers={
         'api-id': config.BRANCH_ID,
         'api-key': config.BRANCH_SECRET_KEY
      })

      def on_connect():
         print('Server connected to Cloud Server')

      socket.call('connect', on_connect)

   except Exception as e:
        print(f"Error connecting to Cloud Server: {e}")
   