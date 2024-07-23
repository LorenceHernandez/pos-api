
from datetime import datetime
from flask import Blueprint, g, request
from pydash import omit

from app.database.config import balances
from app.models.Balance import Balance

create_balance = Blueprint("/balance/create", __name__)

@create_balance.route('/balance/create', methods=['POST'])
def _create_balance():
   request_data = request.get_json()
  
   balance = Balance.fromDict(request_data)
   balance.created_at = datetime.now()
   balance.created_by = g.user_id
   
   doc = balances.insert_one(omit(balance.toDict(), 'id'))
   
   if doc.inserted_id:
      return {
         'message': 'Balance successfully created',
         'code': 15,
      }, 200
   else:
      return {
         'message': 'Unable to add balance.',
         'code': 30,
      }, 200


