import os

from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

if(JWT_SECRET_KEY is None):
    raise Exception('JWT_SECRET_KEY is null')


LOCAL_DATABASE_URL = os.getenv('LOCAL_DATABASE_URL')
LOCAL_DATABASE = os.getenv('LOCAL_DATABASE')

REMOTE_DATABASE_URL = os.getenv('REMOTE_DATABASE_URL')
REMOTE_DATABASE = os.getenv('REMOTE_DATABASE')

BACKUP_DATABASE = os.getenv('BACKUP_DATABASE')

ENVIRONMENT = os.getenv('APP_ENV', 'development') 

IS_DEVELOPMENT = ENVIRONMENT == 'development'
IS_INTERNAL_PRODUCTION = ENVIRONMENT == 'internal-production'
IS_PRODUCTION = ENVIRONMENT == 'production'

if LOCAL_DATABASE_URL is None:
    raise Exception('LOCAL_DATABASE_URL is None')
print('CURRENT_ENVIRONMENT: ', ENVIRONMENT)