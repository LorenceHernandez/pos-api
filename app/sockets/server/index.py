

from flask_socketio import SocketIO, disconnect
from flask import Flask, request, session


socket_server = SocketIO(debug=True, cors_allowed_origins='*')
client_event_queues: dict[list] = {}
connected_keys = set()

@socket_server.on('connect')
def handle_connected():
   id = get_client_sid()
   print(f'\nClient ID {id}')
   print(f'Client API ID {request.headers.get("api-id")}')
   print(f'Client IP {request.headers.get("origin")}')

   key = get_api_key()
   print(client_event_queues)
   print(connected_keys)


   if(not key):
      print(f'Disconnected Client ID {id}: Missing API ID and KEY\n')
      disconnect(id)
      return

   connected_keys.add(key)
   if(key in client_event_queues):
      events = client_event_queues[key]
      for event in events:
         try:
            socket_server.emit(event['name'], event['data'], room=event['namespace'], to=id)  # Use room=sid to send to the specific client
            print(f"Re-emitted event: {event} with data: {event['data']} to SID: {key}")
         except Exception as e:
            print(f"Error re-emitting event {event}: {e}")
      del client_event_queues[key]

@socket_server.on('disconnect')
def handle_disconnected():
   key = get_api_key()
   connected_keys.remove(key)

   if(key not in client_event_queues):
      client_event_queues[key] = []


def append_event_queue(keys, event):
   for key in keys:
      if(key not in client_event_queues):
         client_event_queues[key] = []
      client_event_queues[key].append(event)

def create_socket_instance(app: Flask):
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

   