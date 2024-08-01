from flask import Blueprint, g, request
from pydash import merge, omit, pick

from app.database.config import cashier_reports
from app.utils.compare_date import compareDateYearMonth, compareDateRange, compareDateToday
from app.utils.utils import ToStringId
from app.filters.date_filter import DateFilter


get_cashier_reports = Blueprint("/cashier-reports", __name__)

@get_cashier_reports.route('/cashier-reports', methods=['GET'])
def _get_cashier_reports():


     try:
          query = request.args.to_dict()
          filters = pick(query, ['dateFilter', 'customDate', 'startDate', 'endDate'])
          query = omit(query, ['dateFilter', 'customDate', 'startDate', 'endDate'])

          reports = cashier_reports.aggregate([
              { '$match': query },
              {
                    "$addFields": {
                         "cashierId": {"$toObjectId": "$cashierId"},
                         "branchId": {"$toObjectId": "$branchId"}
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
                    "$addFields": {
                         "branch": { "$arrayElemAt": ["$branch", 0] },
                         "cashier": { "$arrayElemAt": ["$cashier", 0] }
                    }
               },
               {
                   '$project': {
                       'cashierId': 0,
                       'branchId': 0,
                       'cashier': {
                           'password': 0,
                           'branches': 0
                       }
                   }
               }
          ])

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
               
               report = ToStringId(report)
               report['branch'] = ToStringId(report['branch'])
               report['cashier'] = ToStringId(report['cashier'])
               report_list.append(report)

          return { 'data': report_list, }, 200
     except Exception as e:
      return {
            'message': 'Unable to get cashier reports.',
            'error': repr(e),
         }, 500

