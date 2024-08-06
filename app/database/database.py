
import abc
import pymongo
from app.config import BACKUP_DATABASE, BACKUP_HOST, BACKUP_PORT, LOCAL_DATABASE, LOCAL_HOST, LOCAL_PORT, REMOTE_DATABASE, REMOTE_HOST, REMOTE_PORT

class Database(abc.ABC):
    def __init__(self, config):
        self.config = config

    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass


class MongoDB(Database):
    def connect(self):
        self._connection = pymongo.MongoClient(self.config['host'], self.config['port'])
        db = self._connection[self.config['database']]

        print('CONNECTED_DB: ', self._connection)
        return db

    def close(self):
        self._connection.close()


dev_database = MongoDB({ 
    "host": LOCAL_HOST, 
    "port": LOCAL_PORT,
    "database": REMOTE_DATABASE, 
})

remote_database = MongoDB({ 
    "host": REMOTE_HOST, 
    "port": REMOTE_PORT,
    "database": REMOTE_DATABASE, 
})

backup_database = MongoDB({ 
    "host": BACKUP_HOST, 
    "port": BACKUP_PORT,
    "database": BACKUP_DATABASE, 
})

internal_prod_database = MongoDB({ 
    "host": LOCAL_HOST, 
    "port": LOCAL_PORT,
    "database": LOCAL_DATABASE, 
})
