import copy

import moment
from bson.objectid import ObjectId

from app.database.config import branches, product_categories, transactions


def generateSummaryIncome(args):
   branchIds = args.getlist('branchIds')

   categories = []
   _branches = []
   objectIds = []
   min = moment.date(args.get('min'), 'MM/DD/YYYY 00:00:00')
   max = moment.date(args.get('max'), 'MM/DD/YYYY 00:00:00')
   res = transactions.find({
      "status": "Completed",
      "branchId": {"$in": branchIds},
   })
   res_copy = []
   if res:
      for transaction in res:

         if (str(moment.date(transaction['transactionDate'])) >= str(min)) and (str(moment.date(transaction['transactionDate'])) <= str(max)):
                res_copy.append(transaction)


   for branchId in branchIds:
      objectIds.append(ObjectId(branchId))
   
   res_branch = branches.find({
      "_id": {"$in": objectIds}
   })

   
   res_categories = product_categories.find()
   if res_categories:
      for category in res_categories:
         categories.append({
            'id': str(category['_id']),
            'name': category['name'],
            'total': 0,
            'cash': 0,
            'charge': 0
         })
      categories.append({
            'id': None,
            'name': 'Package',
            'total': 0,
            'cash': 0,
            'charge': 0
         })
      
   if res_branch:
      for branch in res_branch:
         _branches.append({
            'id': str(branch['_id']),
            'name': branch['name'],
            'categories': copy.deepcopy(categories),
            'total': 0,
            'totalCash': 0,
            'totalCharge': 0
         })
      _branches.append({
            'id': None,
            'name': 'Package',
            'categories': copy.deepcopy(categories),
            'total': 0,
            'totalCash': 0,
            'totalCharge': 0
         })


   if res_copy:
      for transaction in res_copy:
        for service in transaction['services']:
           if service['source'] == 'package':
                for item in service['items']:
                    for branch in _branches:
                       if transaction['branchId'] == branch['id']:
                          for category in branch['categories']:
                             
                             if category['name'].lower() == 'package':
                                if transaction['paymentDetails']['tenderType'].lower() == 'cash':
                                    category['cash'] += item['amount']
                                    category['total'] += item['amount']
                                    branch['totalCash'] += item['amount']
                                else: #charge
                                    category['charge'] += item['amount']
                                    category['total'] += item['amount']
                                    branch['totalCharge'] += item['amount']
           else: 
              for branch in _branches:
                if transaction['branchId'] == branch['id']:
                   for category in branch['categories']:
                      if category['id'] == service['category']['id']:
                        if transaction['paymentDetails']['tenderType'].lower() == 'cash':
                            category['cash'] += service['amount']
                            category['total'] += service['amount']
                            branch['totalCash'] += service['amount']
                        else:
                            category['charge'] += service['amount']
                            category['total'] += service['amount']
                            branch['totalCharge'] += service['amount']
   return _branches


