

import socketio
from app import config

socket_client = socketio.Client(logger=True, reconnection=True)

@socket_client.event
def connect():
   print('Server connected to Cloud Server')

def connect_cloud_socket():
   try:
      socket_client.connect(config.CLOUD_SERVER_URL, headers={ 'api-key': config.BRANCH_SECRET_KEY }, retry=True)
      socket_client.wait()
   except Exception as e:
        print(f"Error connecting to Cloud Server: {e}")
   