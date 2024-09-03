from datetime import date
from bson.objectid import ObjectId
from flask import Blueprint, g, request
from pydash import merge, omit

from app.database.config import cashier_reports
from app.models.CashierReport import CashierReport
from app.utils.filter_values import filterValues
from app.utils.utils import ToStringId

get_generated_branch_reports = Blueprint("/branch-reports/generated", __name__)

@get_generated_branch_reports.route('/branch-reports/generated', methods=['GET'])
def _get_generated_branch_reports():

     try:
          branchId = request.args.get('branchId')
          today = str(date.today())
          
          report = generate_branch_report(branchId, today)
          return { 'data': report, }, 200
     except Exception as e:
      return {
            'message': 'Unable to get branch reports',
            'error': repr(e),
         }, 500

def generate_branch_report(branchId, date):
     data = cashier_reports.aggregate([
          { 
               '$match': {
                    'branchId': branchId,
                    'date': date
               } 
          },
          {
               "$group": {
                    "_id": "$branchId",
                    'date': { '$first': '$date' },
                    "totalBeginningCash": { "$sum": "$beginningCashOnHand.total" },
                    "totalEndingCash": { "$sum": "$endingCashOnHand.total" },
                    "totalCashSales": { "$sum": "$cashSales" },
                    "totalCashGain": { "$sum": "$cashGain" },
                    "totalCashLoss": { "$sum": "$cashLoss" }
               }
          },
          # { 
          #      '$lookup': {
          #           'from': 'sales_deposits',
          #           "let": {
          #                "date": "$date",
          #                "branchId": "$_id"
          #           },
          #           "pipeline": [
          #                {
          #                     "$match": {
          #                     "$expr": {
          #                               "$and": [
          #                                    { "$eq": ["$dateDeposited", "$$date"] },
          #                                    { "$eq": ["$branchId", "$$branchId"] }
          #                               ]
          #                          }
          #                     }
          #                }
          #           ],
          #           'as': 'salesDeposit'
          #      }, 
          # },
          {
               "$addFields": {
                    "branchId": {"$toObjectId": "$_id"},
               }
          },
          { 
               '$lookup': {
                    'from': 'branches',
                    'localField': 'branchId',
                    'foreignField': '_id',
                    'as': 'branch'
               }, 
          },
          {
               "$addFields": {
                    "branch": { "$arrayElemAt": ["$branch", 0] },
               }
          },
          {
               '$project': {
                    'branchId': 0,
               }
          }
     ])

     reports = list(data)

     if len(reports) == 0:
          return None

     report = reports[0]
     report['branch'] = ToStringId(report['branch'])
     # report['salesDeposit'] = ToStringId(report['salesDeposit'])
     report = ToStringId(report)
     return report