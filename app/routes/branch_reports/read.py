from flask import Blueprint, request
from pydash import omit, pick

from app.database.config import branch_reports
from app.filters.date_filter import DateFilter
from app.utils.compare_date import compareDateRange, compareDateToday, compareDateYearMonth
from app.utils.utils import ToStringId

get_branch_reports = Blueprint("/branch-reports", __name__)

@get_branch_reports.route('/branch-reports', methods=['GET'])
def _get_branch_reports():

     try:
          query = request.args.to_dict()
          filters = pick(query, ['dateFilter', 'customDate', 'startDate', 'endDate'])
          query = omit(query, ['dateFilter', 'customDate', 'startDate', 'endDate'])


          data = branch_reports.aggregate([
              { '$match': query },
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
               },
               { "$sort": { "_id": -1 }}
          ])
          reports = list(data)

          dateFilter = DateFilter.TODAY
          if(filters.get('dateFilter') is not None):
               dateFilter = int(filters.get('dateFilter'))

          report_list = []
          for report in reports:
               date = report['date']
               
               if(dateFilter != DateFilter.ALL):

                    if(dateFilter == DateFilter.CUSTOM_DATE and not compareDateYearMonth(date, filters.get('customDate'))):
                         continue
                    if(dateFilter == DateFilter.CUSTOM_FILTER and not compareDateRange(date, filters.get('startDate'),  filters.get('endDate'))):
                         continue
                    if(dateFilter < 9 and not compareDateToday(dateFilter, date)):
                         continue
               
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
