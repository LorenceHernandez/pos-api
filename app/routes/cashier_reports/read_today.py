from datetime import date
from bson.objectid import ObjectId
from flask import Blueprint, g
from pydash import omit

from app.database.config import cashier_reports

get_latest_cashier_report = Blueprint("/cashier-report", __name__)

@get_latest_cashier_report.route('/cashier-report', methods=['GET'])
def _get_cashier_report():
   
   previous_report = None

   try:
     previous_report = cashier_reports.find({ 
        'cashierId': g.user_id, 
        'date': { '$ne': str(date.today()) }
     }).sort({ '_id': -1 }).limit(1)[0]
   except:
     pass

   report = cashier_reports.find_one({ 
        'cashierId': g.user_id, 
        'date': str(date.today()) 
   })
   if report is None:
        return {
            'message': 'No report is available',
            'data': None,
            'previous': {
               **omit(previous_report, '_id'), 
                    "id": str(previous_report["_id"]) 
               }
        }, 200
 

   return { 
          'data': { 
               **omit(report, '_id'), 
               "id": str(report["_id"]) 
          },
          
     }, 200 


