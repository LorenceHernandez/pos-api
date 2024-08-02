from bson.objectid import ObjectId

from app.database.config import branches, product_categories, transactions


def getMancomPaymentType(args):
   branchIds = args.getlist('branchIds')

   categories = []
   _branches = []
   objectIds = []

   res = transactions.find({
      "status": "Completed",
      "branchId": {"$in": branchIds},
      "transactionDate": {"$gte": args.get('min'), "$lte": args.get('max')}
   })

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
         
   if res_branch:
      for branch in res_branch:
         _branches.append({
            'id': str(branch['_id']),
            'name': branch['name'],
            'categories': categories,
            'totalCash': 0,
            'totalAr': 0
         })
   
   print(_branches)
#    return "test"
   if res:
      for transaction in res:
        for service in transaction['services']:
           if service['source'] == 'package':
                for item in service['items']:
                    for branch in _branches:
                       if transaction['branchId'] == branch['id']:
                          for category in branch['categories']:
                             if category['id'] == item['category']['id']:
                                if item['name'].lower() == 'account receivable':
                                    category['Cash'] += item['amount']
                                    category['Count'] += 1
                                    branch['totalCash'] += item['amount']
                                else:
                                    category['AR'] += item['amount']
                                    category['Count'] += 1
                                    branch['totalAr'] += item['amount']
           else: 
              for branch in _branches:
                if transaction['branchId'] == branch['id']:
                   for category in branch['categories']:
                      if category['id'] == service['category']['id']:
                        if transaction['paymentDetails']['tenderType'].lower() in ['cash', 'debit']:
                            category['Cash'] += service['amount']
                            category['Count'] += 1
                            branch['totalCash'] += item['amount']
                        else:
                            category['AR'] += service['amount']
                            category['Count'] += 1
                            branch['totalAr'] += item['amount']
   return _branches


