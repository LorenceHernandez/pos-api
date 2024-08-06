import copy

import moment
from bson.objectid import ObjectId

from app.database.config import (branches, packages, product_categories,
                                 transactions)


def generatePackagesReports(args):
   branchIds = args.getlist('branchIds')

   categories = []
   _branches = []
   objectIds = []
   min = moment.date(args.get('min'), 'MM/YYYY').format('YYYY/MM')
   max = moment.date(args.get('max'), 'MM/YYYY').format('YYYY/MM')
   month_list = [i.strftime("%B %Y") for i in pd.date_range(start=args.get('min'), end=args.get('max'), freq='MS')]

   res = transactions.find({
      "services.source": 'package',
      "status": "Completed",
      "branchId": {"$in": branchIds},
   })
   res_copy = []
   if res:
        for transaction in res:
        
         if (str(moment.date(transaction['transactionDate']).format("YYYY/MM")) >= str(min)) and (str(moment.date(transaction['transactionDate']).format("YYYY/MM")) <= str(max)):
                res_copy.append(transaction)
   res_packages = packages.find()
   _packages = []
   table = dict()

   if res_packages:
        for package in res_packages:
            _packages.append({
                'id': str(package['_id']),
                'name': package['name'],
                'count': 0,
                'amount': 0
            })  

   for month in month_list:
      table[month] = {
        'packages': copy.deepcopy(_packages),
        "total": 0
      }
   
   _branches = []

   for branchId in branchIds:
      objectIds.append(ObjectId(branchId))
   
   res_branch = branches.find({
      "_id": {"$in": objectIds}
   })
   
   if res_branch:
      for branch in res_branch:
         _branches.append({
            'id': str(branch['_id']),
            'name': branch['name'],
            'table': copy.deepcopy(table),
            'total': 0
         })
   if res_copy:
      for transaction in res_copy:
        key = str(moment.date(transaction['transactionDate']).format("MMMM YYYY"))
        for branch in _branches:
          if branch['id'] == transaction['branchId']:
            for service in transaction['services']:
                if service['source'] == 'package':
                    for col in branch['table'][key]['packages']:
                        if col['id'] == service['_id']:
                            total = 0
                            for item in service['items']:
                                total += item['amount']
                            col['count'] += 1
                            col['amount'] += total
                            branch["total"] += total
                            break
   return _branches


