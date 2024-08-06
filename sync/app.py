import pymongo
import subprocess
import datetime
import schedule
import time
from datetime import datetime

from app.config import LOCAL_HOST, REMOTE_HOST

def sync_data(source_uri, source_db_name, dest_uri, dest_db_name, drop_dest_collection=False, drop_source_collection=False):
  try:
    source_client = pymongo.MongoClient(source_uri)
    dest_client = pymongo.MongoClient(dest_uri)

    source_db = source_client[source_db_name]
    dest_db = dest_client[dest_db_name]

    if(source_db_name not in source_client.list_database_names()):
      print(f'- Error: source db "{source_db_name}" does not exist.')
      return
    
    if(dest_db_name not in dest_client.list_database_names()):
      print(f'- Error: destination db "{dest_db_name}" does not exist.')
      return

    for collection_name in source_db.list_collection_names():
      print(f'- Collection: {collection_name}')
      source_collection = source_db[collection_name]
      dest_collection = dest_db[collection_name]

      if(drop_dest_collection):
        dest_collection.drop()

      for doc in source_collection.find():
        dest_collection.insert_one(doc)
      
      if(drop_source_collection):
        source_collection.drop()
  except Exception as e:
    print('Error: ', repr(e))

while True:
  print('\n=========================================================================')
  print(f'[{datetime.now()}] Downstream-Sync data from remote to backup...')
  sync_data(REMOTE_HOST, "pos", LOCAL_HOST, "internal-pos", True)

  print(f'[{datetime.now()}] Downstream-Sync was sucessfully done...')


  print('\n=========================================================================')
  print(f'[{datetime.now()}] Upstream-Sync data from local to remote...')
  sync_data(LOCAL_HOST, "pos-cache", REMOTE_HOST, "pos", False, True)
  
  print(f'[{datetime.now()}] Upstream-Sync was sucessfully done...')

  time.sleep(60)
