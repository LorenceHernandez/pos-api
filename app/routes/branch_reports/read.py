from flask import Blueprint, request

from app.database.config import branch_reports
from app.utils.utils import ToStringId

get_branch_reports = Blueprint("/branch-reports", __name__)

@get_branch_reports.route('/branch-reports', methods=['GET'])
def _get_branch_reports():

     try:
          query = request.args
          data = branch_reports.aggregate([
              { '$match': query.to_dict() },
              {
                    "$addFields": {
                         "cashierId": {"$toObjectId": "$cashierId"},
                         "branchId": {"$toObjectId": "$branchId"},
                         "salesDepositId": {"$toObjectId": "$salesDepositId"}
                    }
               },
              { 
                    '$lookup': {
                         'from': 'users',
                         'localField': 'cashierId',
                         'foreignField': '_id',
                         'as': 'cashier'
                    }, 
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
                    '$lookup': {
                        'from': 'sales_deposits',
                        'localField': 'salesDepositId',
                        'foreignField': '_id',
                        'as': 'salesDeposit'
                    }, 
               },
               {
                    "$addFields": {
                         "branch": { "$arrayElemAt": ["$branch", 0] },
                         "cashier": { "$arrayElemAt": ["$cashier", 0] },
                         "salesDeposit": { "$arrayElemAt": ["$salesDeposit", 0] }
                    }
               },
               {
                   '$project': {
                       'cashierId': 0,
                       'branchId': 0,
                       'salesDepositId': 0,
                       'cashier': {
                           'password': 0,
                           'branches': 0
                       }
                   }
               }
          ])
          reports = list(data)

          report_list = []
          for report in reports:
               report['branch'] = ToStringId(report['branch'])
               report['cashier'] = ToStringId(report['cashier'])
               report['salesDeposit'] = ToStringId(report['salesDeposit'])
               report = ToStringId(report)
               report_list.append(report)

          return { 'data': report_list, }, 200
     except Exception as e:
      return {
            'message': 'Unable to get branch reports.',
            'error': repr(e),
         }, 500
