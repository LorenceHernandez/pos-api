from bson import ObjectId
from app.repositories.branch import BranchRepository
from app.sockets.server.index import socket_server, append_event_queue, client_event_queues, connected_keys

namespace = "/users"
branch_repository = BranchRepository()

def notify_user_created(user):
    event = {
        'name': 'create-user',
        'data': user,
        'namespace': namespace
    }
    socket_server.emit(event['name'], event['data'], room=event['namespace'])
    
    ids = get_disconnected_branch_ids(connected_keys)
    print(client_event_queues)
    append_event_queue(ids, event)

def get_disconnected_branch_ids(connectedIds: set[str] = []) -> list:
    connectedIds = map(lambda i: ObjectId(i), connectedIds)
    return branch_repository.find({ '_id': { '$nin': connectedIds } })