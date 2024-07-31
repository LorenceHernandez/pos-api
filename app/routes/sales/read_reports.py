from bson import ObjectId
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, request

from app.database.config import branches, product_categories, transactions
from app.models.Transaction import Transaction
from app.routes.sales.report_generators.comparativeData import comparativeData
from app.routes.sales.report_generators.mancomPaymentType import \
    getMancomPaymentType
from app.routes.sales.report_generators.typesOfClient import typesOfClient

get_reports = Blueprint("/reports", __name__)

@get_reports.route('/reports', methods=['GET'])
def _get_reports():
   type = request.args.get('type')
   if type == 'paymentType':
      return { 'data': getMancomPaymentType(request.args) }, 200
   if type == 'comparativeData':
      return { 'data': comparativeData(request.args) }, 200
   if type == 'typesOfClient':
      return { 'data': typesOfClient(request.args) }, 200
   return {
      'message': 'unkwown report type.'
   }, 401


