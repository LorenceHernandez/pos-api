
from datetime import date, datetime
from bson import ObjectId
from flask import Blueprint, g, request
from pydash import omit

from app.database.config import cashier_reports
from app.models.CashierReport import CashierReport
from app.utils.filter_values import filterValues


from app.database.config import sales

time_out_cashier_report = Blueprint("/cashier-report/time-out", __name__)

@time_out_cashier_report.route('/cashier-report/time-out', methods=['POST'])
def _update_cashier_report():
   request_data = request.get_json()
   id = request_data['id']

   data = cashier_reports.find_one({ '_id': ObjectId(id) })

   report = CashierReport.fromDict(data)
   report.time_out = str(datetime.now().time())
   report.ending_cash_count = request_data['endingCashCount']
   report.cash_sales = _compute_cash_sale(report)

  
   
   filter = { '_id': ObjectId(id) }
   new_val = { "$set": filterValues(omit(report.toDict(), 'id')) }
   res = cashier_reports.update_one(filter, new_val)

   updated_value = cashier_reports.find_one({ '_id': ObjectId(id) })

   if res.modified_count > 0:
      return {
         'message': 'Report successfully updated',
         'data': { **omit(updated_value, '_id'), "id": str(updated_value["_id"]) },
         'code': 15,
      }, 200
   else:
      return {
         'message': 'Unable to update report.',
         'code': 30,
      }, 200


def _compute_cash_sale(report: CashierReport):
   cash_sale = 0.0

   sale_list = sales.find({ 
      "branch": report.branch_id, 
      'cashierId': report.cashier_id, 
      'date': report.date
   })

   for sale in sale_list:
      cash_sale += float(sale['amount'])
   
   return cash_sale