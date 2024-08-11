
import abc

from dotenv import load_dotenv
from app.config import IS_DEVELOPMENT, IS_INTERNAL_PRODUCTION, IS_PRODUCTION
from app.database.database import remote_database, backup_database, internal_prod_database

load_dotenv()
current_database = remote_database
current_backup_database = None

if IS_INTERNAL_PRODUCTION:
    current_database = internal_prod_database
    current_backup_database = backup_database
if IS_PRODUCTION:
    current_database = remote_database

class Repository(abc.ABC):
    _db = None
    _collection = None

    def __init__(self):
        self._db = current_database.connect()
    
    def find(self, query):
        try:
            data = list(self._db[self._collection].find(query))
            return data
        except Exception as e:
            raise Exception(f"MongoDB find error: {e}")
        
    def find_one(self, query):
        try:
            data = self.find(query)
            return data[0] if data else None
        except Exception as e:
            raise Exception(f"MongoDB find error: {e}")
        
    def insert_one(self, data):
        try:
            return self._db[self._collection].insert_one(data)
        except Exception as e:
            raise Exception(f"MongoDB insert_one error: {e}")
   
    def update_one(self, query, data):
        try:
            return self._db[self._collection].update_one(query, data)
        except Exception as e:
            raise Exception(f"MongoDB update_one error: {e}")
    
    def _get_next_sequence(self, name):
        counter = self._db['counters'].find_one_and_update(
            {"_id": name},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        return counter['seq']

class BackupRepository(Repository):
    _backup_db = None
    _db = None
    _collection = None
    _backup_db_client = None
    _db_client = None

    def __init__(self):
        self._db_client = current_database._connection
        self._db = current_database.connect()

        if(current_backup_database is not None):
            self._backup_db_client = current_backup_database._connection
            self._backup_db = current_backup_database.connect()

    def insert_one(self, data):
        with self._db_client.start_session() as session:
            with session.start_transaction():
                try:
                    self.backup_one(data)
                    result = self._db[self._collection].insert_one(data)
                    session.commit_transaction()
                    return result
                except Exception as e:
                    session.abort_transaction()
                    raise Exception(f"MongoDB insert_one error: {e}")
                

    def backup_one(self, data):
        if(self._backup_db is not None and IS_INTERNAL_PRODUCTION):
            self._backup_db[self._collection].insert_one(data)