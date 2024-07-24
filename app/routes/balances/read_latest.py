from bson.objectid import ObjectId
from flask import Blueprint, g
from pydash import omit

from app.database.config import balances

get_latest_balance = Blueprint("/balance", __name__)

@get_latest_balance.route('/balance', methods=['GET'])
def _get_latest_balance():
   balance = None
   try: 
       balance = balances.find({ "createdBy": g.user_id }).sort({ '_id': -1 }).limit(1)[0]
       if not balance:
           raise
   except:
       return {
            'message': 'Balance not found',
            'data': None,
            'code': 20
        }, 200

   return { 'data': { **omit(balance, '_id'), "id": str(balance["_id"]) } }, 200 


