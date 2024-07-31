
from datetime import date, datetime
from flask import Blueprint, g, request
from pydash import omit

from app.database.config import sales_deposits
from app.models.SalesDeposit import SalesDeposit

create_sales_deposit = Blueprint("/sales-deposits/create", __name__)

@create_sales_deposit.route('/sales-deposits/create', methods=['POST'])
def _create_sales_deposit():
   request_data = request.get_json()
   deposit = None
   today = str(date.today())

   try:
      existing_deposits = sales_deposits.find({ "branchId": request_data['branchId'], 'dateDeposited': today })

      if len(list(existing_deposits)) > 0:
         raise Exception('Only one sales deposit is allowed per day in any branch.')

      deposit = SalesDeposit.fromDict(request_data)
      deposit.created_at = datetime.now()
      deposit.date_deposited = today
      deposit.cashier_id = g.user_id
      
      doc = sales_deposits.insert_one(omit(deposit.toDict(), 'id'))
      
      if not doc.inserted_id:
         raise Exception('Document failed to create')

      deposit.id = doc.inserted_id
      return {
         'message': 'Sales deposit successfully created',
         'code': 15,
         'data': deposit.toDict()
      }, 200 
   except Exception as e:
      return {
            'message': 'Unable to add sales deposit.',
            'error': repr(e),
         }, 500
   