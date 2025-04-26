import os

from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

if(JWT_SECRET_KEY is None):
    raise Exception('JWT_SECRET_KEY is null')


LOCAL_DATABASE_URL = os.getenv('LOCAL_DATABASE_URL')
DATABASE = os.getenv('DATABASE')
REMOTE_DATABASE_URL = os.getenv('REMOTE_DATABASE_URL')

CLOUD_SERVER_URL = os.getenv('CLOUD_SERVER_URL')
BRANCH_ID = os.getenv('BRANCH_ID')
BRANCH_SECRET_KEY = os.getenv('BRANCH_SECRET_KEY')


ENVIRONMENT = os.getenv('APP_ENV') 
print('CURRENT_ENVIRONMENT: ', ENVIRONMENT)

if ENVIRONMENT is None:
    raise Exception('APP_ENV is None')

IS_DEVELOPMENT = ENVIRONMENT == 'development'
IS_LOCAL_DEVELOPMENT = ENVIRONMENT == 'local-development'
IS_INTERNAL_PRODUCTION = ENVIRONMENT == 'internal-production'
IS_PRODUCTION = ENVIRONMENT == 'production'


if IS_PRODUCTION is not True:
    if LOCAL_DATABASE_URL is None:
        raise Exception('LOCAL_DATABASE_URL is None')
else:
    if REMOTE_DATABASE_URL is None:
        raise Exception('REMOTE_DATABASE_URL is None')