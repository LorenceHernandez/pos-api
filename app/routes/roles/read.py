from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import products
from app.utils.utils import roles

get_roles = Blueprint("/roles", __name__)

@get_roles.route('/roles', methods=['GET'])
def _get_roles():
       return {
          'data': roles,
        }, 200
   
