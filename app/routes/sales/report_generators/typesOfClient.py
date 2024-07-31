from bson.objectid import ObjectId

from app.database.config import (branches, customers, product_categories,
                                 transactions)


def typesOfClient(args):
   branchIds = args.getlist('branchIds')

   _branches = []
   objectIds = []
   types = []
   
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

   total = 0
   customer_types = customers.distinct("customer_type")
   

   if customer_types:
      customer_types.append('corporates')
      for customer_type in customer_types:
         types.append({"name": customer_type, "count": 0, "amount": 0})
      types.append({"name": 'NO. OF CLIENTS', "count": 0, "amount": 0})
   if res_branch:
      for branch in res_branch:
         _branches.append({
            'id': str(branch['_id']),
            'name': branch['name'],
            'types': types,
         })
   
   if res:
      for transaction in res:
        total += 1
        for branch in _branches:
           if branch['id'] == transaction['branchId']:
              for type in branch['types']:
                 if type['name'] == transaction['customerData']['customerType']:
                    type['count'] += 1
                    type['amount'] += transaction['paymentDetails']['paymentDue']
                    index = len(branch['types']) - 1
                    branch['types'][index]['count'] += 1
                    branch['types'][index]['amount'] += transaction['paymentDetails']['paymentDue']      

   return _branches


