
import abc
import pymongo
from app.config import BACKUP_DATABASE, LOCAL_DATABASE, LOCAL_DATABASE_URL, REMOTE_DATABASE, REMOTE_DATABASE_URL

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
        self._connection = pymongo.MongoClient(self.config['uri'])
        db = self._connection[self.config['database']]

        print('CONNECTED_DB: ', self.config['database'], self._connection)
        return db

    def close(self):
        self._connection.close()


dev_database = MongoDB({ 
    "uri": LOCAL_DATABASE_URL, 
    "database": REMOTE_DATABASE, 
})

remote_database = MongoDB({ 
    "uri": REMOTE_DATABASE_URL, 
    "database": REMOTE_DATABASE, 
})

backup_database = MongoDB({ 
    "uri": LOCAL_DATABASE_URL, 
    "database": BACKUP_DATABASE, 
})

internal_prod_database = MongoDB({ 
    "uri": LOCAL_DATABASE_URL, 
    "database": LOCAL_DATABASE, 
})
