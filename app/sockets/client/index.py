

import socketio
from app import config
from app.sockets.client.user import listen_user_created, namespace as user_namespace

def connect_cloud_socket():
   try:
      socket_client = socketio.Client()
      socket_client.connect(config.CLOUD_SERVER_URL, headers={
         'api-key': config.BRANCH_SECRET_KEY,
      })

      def on_connect():
         print('Server connected to Cloud Server')

      socket_client.on('create-user', listen_user_created, namespace=user_namespace)
      socket_client.on('connect', on_connect)

   except Exception as e:
        print(f"Error connecting to Cloud Server: {e}")
   