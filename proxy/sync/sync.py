import os
import os
import pymongo
import time
import schedule

REMOTE_DATABASE_URL = os.getenv('REMOTE_DATABASE_URL') 
LOCAL_DATABASE_URL = os.getenv('LOCAL_DATABASE_URL')  

print('REMOTE_DATABASE_URL: ', REMOTE_DATABASE_URL)
print('LOCAL_DATABASE_URL: ', LOCAL_DATABASE_URL)

def sync_data(source_client: pymongo.MongoClient, source_db_name, dest_client: pymongo.MongoClient, dest_db_name, drop_dest_collection=False, drop_source_collection=False):
  try:
    source_db = source_client[source_db_name]
    dest_db = dest_client[dest_db_name]

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



def downstream_sync_data():
  source_client = pymongo.MongoClient(REMOTE_DATABASE_URL)
  dest_client = pymongo.MongoClient(LOCAL_DATABASE_URL)

  print('\n=========================================================================')
  print(f'Downstream-Sync data from remote to backup...')
  sync_data(source_client, "pos", dest_client, "internal-pos", True)

  print(f'Downstream-Sync was sucessfully done...')

def upstream_sync_data():
  source_client = pymongo.MongoClient(LOCAL_DATABASE_URL)
  dest_client = pymongo.MongoClient(REMOTE_DATABASE_URL)

def upstream_backup_to_remote():
  print('\n=========================================================================')
  print(f'Upstream-Sync data from local to remote...')
  sync_data(source_client, "pos-cache", dest_client, "pos", False, True)
  
  print(f'Upstream-Sync was sucessfully done...')

print('Auto-Sync starting...')
schedule.every(3).minutes.do(downstream_sync_data)
schedule.every(20).seconds.do(upstream_sync_data)

downstream_sync_data()
while True:
  schedule.run_pending()
  time.sleep(1)
