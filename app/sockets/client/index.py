

import socketio
from app import config
from app.sockets.client.user import listen_user_created, namespace as user_namespace

async def connect_cloud_socket():
   try:
      socket_client = socketio.AsyncSimpleClient()
      await socket_client.connect(config.CLOUD_SERVER_URL, headers={
         'api-id': config.BRANCH_ID,
         'api-key': config.BRANCH_SECRET_KEY
      })

      def on_connect():
         print('Server connected to Cloud Server')

      socket_client.client.on('create-user', listen_user_created, namespace=user_namespace)
      socket_client.client.on('connect', on_connect)

   except Exception as e:
        print(f"Error connecting to Cloud Server: {e}")
   