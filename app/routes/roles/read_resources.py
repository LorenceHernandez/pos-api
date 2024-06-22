from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import roles

apis = ['branches', 'corporates', 'customer', 'doctors' , 'packages', 'products', 'product_categories', 'users']
permission = ['update', 'read', 'create', 'delete']

get_resources = Blueprint("/resources", __name__)

@get_resources.route('/resources', methods=['GET'])
def _get_resources():

   return {
          'data': apis,
        }, 200
      
