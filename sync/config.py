import os

from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

if(JWT_SECRET_KEY is None):
    raise Exception('JWT_SECRET_KEY is null')


LOCAL_HOST = os.getenv('LOCAL_HOST')
LOCAL_PORT = int(os.getenv('LOCAL_PORT'))
LOCAL_DATABASE = os.getenv('LOCAL_DATABASE')

if not (LOCAL_HOST and LOCAL_PORT and LOCAL_DATABASE):
    raise Exception('LOCAL_CONFIG is null')

REMOTE_HOST = os.getenv('REMOTE_HOST')
REMOTE_PORT = int(os.getenv('REMOTE_PORT'))
REMOTE_DATABASE = os.getenv('REMOTE_DATABASE')

if not (REMOTE_HOST and REMOTE_PORT and REMOTE_DATABASE):
    raise Exception('REMOTE_CONFIG is null')

BACKUP_HOST = os.getenv('BACKUP_HOST')
BACKUP_PORT = int(os.getenv('BACKUP_PORT'))
BACKUP_DATABASE = os.getenv('BACKUP_DATABASE')

if not (BACKUP_HOST and BACKUP_PORT and BACKUP_DATABASE):
    raise Exception('BACKUP_CONFIG is null')

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development') 

IS_DEVELOPMENT = ENVIRONMENT == 'development'
IS_INTERNAL_PRODUCTION = ENVIRONMENT == 'internal-production'
IS_PRODUCTION = ENVIRONMENT == 'production'

print('CURRENT_ENVIRONMENT: ', ENVIRONMENT)