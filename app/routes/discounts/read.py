from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import discounts

get_discounts = Blueprint("/discounts", __name__)

@get_discounts.route('/discounts', methods=['GET'])
def _get_discounts():

   res = discounts.find()

   ret = []
   for record in res:

         ret.append({
            "_id": str(record["_id"]),
            "name": record["name"],
            "description": record["description"],
            "value": record["value"],
            "type": record["type"],
          })
   return {
          'data': ret,
        }, 200
      
