from app.sockets.client.index import socket_client

@socket_client.on('create-user')
def handle_user_created(data):
    print(f"Receive data: {data}")
    