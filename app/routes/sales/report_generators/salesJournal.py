import copy

import moment
from bson.objectid import ObjectId
from pydash import merge, omit

from app.database.config import (branches, customers, product_categories,
                                 transactions)
from app.models.Transaction import DiscountApplied

# 1.Sales Journal (All Payment Method)

# Ref No.
# Date
# Customer
# Address
# Gross Sales
# Discount
# Discount Type
# Net Sales Amount
def getSalesJournal(args, filter):
   branchIds = args.getlist('branchIds')
   _filter = None
   query = {
      "status": "Completed",
      "branchId": {"$in": branchIds}
   }
   if filter and filter['tenderType']:
       query['paymentDetails.tenderType'] = filter['tenderType']

   print(query)
   min = moment.date(args.get('min'), 'MM/DD/YYYY 00:00:00')
   max = moment.date(args.get('max'), 'MM/DD/YYYY 00:00:00').add(day = 1)
   res = transactions.find(query)
   ret = []

   
   res_copy = []
   if res:
      for transaction in res:
         if (str(moment.date(transaction['transactionDate'])) >= str(min)) and (str(moment.date(transaction['transactionDate'])) <= str(max)):
                res_copy.append(transaction)
   total = 0
   discount = 0
   if res_copy:
      for transaction in res_copy:
          discountApplied = DiscountApplied.toDict(DiscountApplied.fromDict(transaction.get('discountApplied')))
          discount += 0 if discountApplied["totalDiscount"] is None else discountApplied["totalDiscount"] 
          total += transaction["paymentDetails"]["subTotal"]
       
          ret.append({
              "RefNo": transaction['transactionNo'],
              "Date": transaction['transactionDate'],
              "Customer": transaction['customerData']['name'],
              "Address": transaction['customerData']['address'],
              "Discount": discountApplied["totalDiscount"],
              "Discount Type": discountApplied["type"],
              "Net Sales": transaction["paymentDetails"]["subTotal"] - (0 if discountApplied["totalDiscount"] is None else discountApplied["totalDiscount"]),
              "Gross Sales": transaction["paymentDetails"]["subTotal"],
              "id": str(transaction['_id'])
            },)
   
   return ret


