from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import corporates

get_companies = Blueprint("/corporates", __name__)

@get_companies.route('/corporates', methods=['GET'])
def _get_companies():

   res = corporates.find()

   ret = []
   for record in res:

         ret.append({
            "_id": str(record["_id"]),
            "name": record["name"]
          })
   return {
          'data': ret,
        }, 200
      
