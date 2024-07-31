from bson.objectid import ObjectId

from app.database.config import branches, product_categories, transactions


def comparativeData(args):
   
   branchIds = args.getlist('branchIds')

   categories = []
   objectIds = []
   total = 0
   c2024 = 0

   res = transactions.find({
      "status": "Completed",
      "branchId": {"$in": branchIds},
      "transactionDate": {"$gte": args.get('min'), "$lte": args.get('max')}
   })


   for branchId in branchIds:
      objectIds.append(ObjectId(branchId))
   
   res_categories = product_categories.find()
   if res_categories:
      for category in res_categories:
         categories.append({
            'id': str(category['_id']),
            'name': category['name'],
            '2024': 0,
            'total': 0,
         })
   
   if res:
      c2024 = len(list(res))
      for transaction in res:
        for service in transaction['services']:
           if service['source'] == 'package':
                for item in service['items']:
                          for category in categories:
                             if category['id'] == item['category']['id']:
                                category['2024'] += 1
                                category['total'] += item['amount']
                                total += item['amount']
           else: 
                   for category in categories:
                      if category['id'] == service['category']['id']:
                          category['2024'] += 1
                          category['total'] += item['amount']
                          total += item['amount']
      
      categories.append({
         'id': None,
         'name': 'NO. OF CLIENTS',
         '2024': c2024,
         'total': total,
      })
   return categories