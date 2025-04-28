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
    socket_server.emit(event['name'], event['data'], namespace=event['namespace'])
    
    ids = get_disconnected_branch_ids(connected_keys)
    append_event_queue(ids, event)

    print(f"Emitted event: {event['name']} to IDS: {connected_keys}")
    print(f"To process event: {event['name']} to IDS: {ids}")
    print()


def get_disconnected_branch_ids(connected_ids: set) -> list:
    connected_ids = list(map(lambda i: ObjectId(i), list(connected_ids)))
    branches = list(branch_repository.find({ '_id': { '$nin': connected_ids } }))
    return list(map(lambda i: str(i['_id']), branches))