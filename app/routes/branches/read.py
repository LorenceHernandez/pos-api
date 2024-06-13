from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import branches

get_branches = Blueprint("/branches", __name__)

@get_branches.route('/branches', methods=['GET'])
def _get_branches():

   res = branches.find()

   ret = []
   for record in res:

         ret.append({
            "_id": str(record["_id"]),
            "name": record["name"],
            "address": record["address"],
            "isActive": record["is_active"],
          })
   return {
          'data': ret,
        }, 200
      
