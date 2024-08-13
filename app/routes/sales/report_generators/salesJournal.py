import copy

import moment
from bson.objectid import ObjectId

from app.database.config import branches, product_categories, transactions

# 1.Sales Journal (All Payment Method)

# Ref No.
# Date
# Customer
# Address
# Gross Sales
# Discount
# Discount Type
# Net Sales Amount
def getSalesJournal(args):
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
            'Cash': 0,
            'AR': 0,
            'Count': 0
         })
   
      categories.append({
            'id': None,
            'name': 'Package',
            'Cash': 0,
            'AR': 0,
            'Count': 0
         })      
   if res_branch:
      for branch in res_branch:
         _branches.append({
            'id': str(branch['_id']),
            'name': branch['name'],
            'categories': copy.deepcopy(categories),
            'totalCash': 0,
            'totalAr': 0
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
                                if item['name'].lower() == 'account receivable' or transaction['paymentDetails']['tenderType'].lower() == 'charge':
                                    category['AR'] += item['amount']
                                    category['Count'] += 1
                                    branch['totalAr'] += item['amount']
                                else:
                                    category['Cash'] += item['amount']
                                    category['Count'] += 1
                                    branch['totalCash'] += item['amount']
           else: 
              for branch in _branches:
                if transaction['branchId'] == branch['id']:
                   for category in branch['categories']:
                      if category['id'] == service['category']['id']:
                        if service['name'].lower() == 'account receivable' or transaction['paymentDetails']['tenderType'].lower() == 'charge':
                            category['AR'] += service['amount']
                            category['Count'] += 1
                            branch['totalAr'] += service['amount']
                        else:
                            category['Cash'] += service['amount']
                            category['Count'] += 1
                            branch['totalCash'] += service['amount']
   return _branches


