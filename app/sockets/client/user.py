

namespace = "/users"
def listen_user_created(user):
    event = {
        'name': 'create-user',
        'data': user,
        'namespace': namespace
    }
    