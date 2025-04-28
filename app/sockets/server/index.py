

from datetime import datetime
from flask_socketio import SocketIO, disconnect
from flask import Flask, request, session

from app.utils.utils import getLocalTimeStr


socket_server = SocketIO(debug=True, cors_allowed_origins='*', logger=True)
client_event_queues: dict[list] = {}
connected_keys = set()

@socket_server.on('connect')
def handle_connected():
   id = get_client_sid()
   key = get_api_key()

   print()
   print(getLocalTimeStr())
   print(f'Client ID {id}')
   print(f'Client API ID {key}')

   if(not key):
      print(f'Disconnected Client ID {id}: Missing API ID and KEY\n')
      disconnect(id)
      return

   if(key not in connected_keys):
      connected_keys.add(key)

   print(f'Connected clients: {connected_keys}')

   if(key in client_event_queues):
      events = client_event_queues[key]
      print(f'Queue events before migration: {events}')

      for index, event in enumerate(events):
         try:
            socket_server.emit(event['name'], event['data'], room=event['namespace'], to=id)  # Use room=sid to send to the specific client
            print(f"Re-emitted event: {event['name']} to SID: {key}")
            client_event_queues[key].pop(index)
         except Exception as e:
            print(f"Error re-emitting event {event['name']}: {e}")
      print(f'Queue events after migration: {client_event_queues[key]}')

   print()


@socket_server.on('disconnect')
def handle_disconnected():
   key = get_api_key()

   if(key in connected_keys):
      connected_keys.remove(key)

def append_event_queue(keys, event):
   for key in keys:
      if(key not in client_event_queues):
         client_event_queues[key] = []
      client_event_queues[key].append(event)

def init_socket_instance(app: Flask):
   socket_server.init_app(app)
   return socket_server


def get_client_sid():
   if 'sid' in session:
      return session['sid']
   elif request:
      return request.sid
   else:
      return None

def get_api_key():
   return request.headers.get("api-key")

   