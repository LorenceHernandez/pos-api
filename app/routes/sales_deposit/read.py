from flask import Blueprint, g, request
from pydash import merge, omit

from app.database.config import sales_deposits
from app.models.SalesDeposit import SalesDeposit
from app.utils.filter_values import filterValues
from app.utils.utils import ToStringId

get_sales_deposits = Blueprint("/sales-deposits", __name__)

@get_sales_deposits.route('/sales-deposits', methods=['GET'])
def _get_sales_deposits():
     request_data = request.args

     try:
          query = {}
          
          if(request_data is not None): 
               query = SalesDeposit.fromDict(request_data)
               query = filterValues(query.toDict())

          deposits = sales_deposits.aggregate([
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

          deposit_list = []
          for deposit in deposits:
               deposit = ToStringId(deposit)
               deposit['branch'] = ToStringId(deposit['branch'])
               deposit['cashier'] = ToStringId(deposit['cashier'])
               deposit_list.append(deposit)

          return { 'data': deposit_list, }, 200
     except Exception as e:
      return {
            'message': 'Unable to get sales deposits.',
            'error': repr(e),
         }, 500
