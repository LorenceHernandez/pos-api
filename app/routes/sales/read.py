from bson import ObjectId
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import sales

get_sales = Blueprint("/sales", __name__)

@get_sales.route('/sales', methods=['GET'])
def _get_sales():
  
   res = sales.find({
      "branch": request.args.get('branchId'),
      "cashierId": request.args.get('cashierId')
   })
   total = 0
   ret = []
   if res:
      for sale in res:
        total += sale["amount"]
        ret.append({
          "customerName": sale["customerName"],
          "labExams": sale["labExams"],
          "orNo": sale["orNo"],
          "amount": sale["amount"],
          "categories": sale["categories"],
          "discount": sale["discount"],
          "referrer": sale["referrer"]
        })

   
   return {
      "data": {
         "cols": ret,
         "total": total
      }
   }, 200
