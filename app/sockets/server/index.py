

from datetime import datetime
from flask_socketio import SocketIO, disconnect
from flask import Flask, request, session

from app.repositories.base import EventQueueRepository
from app.utils.utils import getLocalTimeStr


socket_server = SocketIO(debug=True, cors_allowed_origins='*', logger=True)
client_event_queues: dict[list] = {}
event_queue_repository = EventQueueRepository()
connected_keys = set()

@socket_server.on('connect')
def handle_connected():
   id = get_client_sid()
   key = get_api_key()

   print()
   print(getLocalTimeStr())
   print(f'Client ID {id}')
   print(f'Client API ID {key} connected')

   if(not key):
      print(f'Disconnected Client ID {id}: Missing API ID and KEY\n')
      disconnect(id)
      return

   if(key not in connected_keys):
      connected_keys.add(key)

   print(f'Connected clients: {connected_keys}')
   events = get_event_queues(key)
   migrate_remaining_events(events, key)

@socket_server.on('disconnect')
def handle_disconnected():
   key = get_api_key()

   print(f'Client API ID {key} disconnected')

   if(key in connected_keys):
      connected_keys.remove(key)
   print(f'Connected clients: {connected_keys}')

def migrate_remaining_events(events, key):
   id = get_client_sid()
   for event in events:
      try:
         socket_server.emit(event['name'], event['data'], to=id)  # Use room=sid to send to the specific client
         print(f"Re-emitted event: {event['name']} to SID: {key}")
         remove_event_queue(event['_id'])
      except Exception as e:
         print(f"Error re-emitting event {event['name']}: {e}")

def append_event_queue(keys, event):
   for key in keys:
      event_queue_repository.insert_one({ 'key': key, **event })

def remove_event_queue(id):
   event_queue_repository.delete_one(id)

def get_event_queues(key):
   return event_queue_repository.find({ 'key': key })

def get_client_sid():
   if 'sid' in session:
      return session['sid']
   elif request:
      return request.sid
   else:
      return None

def get_api_key():
   return request.headers.get("api-key")

def init_socket_instance(app: Flask):
   socket_server.init_app(app)
   return socket_server
