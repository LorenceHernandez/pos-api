import pprint

from bson import ObjectId
from flask import Blueprint, jsonify, request
from pydash import omit

from app.cas_app.models.ChartAccount import ChartAccount
from app.cas_app.models.new_models.PurchaseInvoice import PurchaseInvoice
from app.cas_app.models.new_models.SalesInvoice import SalesInvoice
from app.cas_app.models.Payment import Payment
from app.cas_app.models.Receipt import Receipt
from app.database.config import (chart_of_accounts, payments,
                                 purchase_invoices, receipts, sales_invoices)
from app.database.store import insert_one
from app.middlewares.authorized_attribute import authorized
from app.utils.filter_values import filterValues

api = '/api/cas/reports'
reports_bp = Blueprint('reports', __name__)

def toArray(list, totalKey):
    ret = []
    for l in list:
        try:
            ret.append({
                'accounting': l['accounting'],
                'totalAmountPaid': l[totalKey],
                '_id': l['_id'],
            })
        except Exception as e:
            print(e)
    
    return ret

@reports_bp.get(api + '/trial-balance')
@authorized
def get_receipts(user_id):
    account_code_credit = 'account_code_credit'
    account_code_debit = 'account_code_debit'
    ret = []
    try:

        chart_of_accounts_data = chart_of_accounts.find()
        for chart_of_account_data in chart_of_accounts_data:
            chart = ChartAccount.fromDict(chart_of_account_data).toDict()
            ret.append({
                '_id': chart['_id'],
                'account_number': chart['accountNumber'],
                'account_name': chart['accountName'],
                'debit': 0,
                'credit': 0
            })
        

        merged_sources = toArray(receipts.find(), 'totalAmountPaid') + toArray(payments.find(), 'totalAmountPaid')  + toArray(sales_invoices.find(), 'total')  + toArray(purchase_invoices.find(), 'totalAmount') 
        
        for data in merged_sources:
            accounting = data['accounting']
            totalAmountPaid = data['totalAmountPaid']
            for accounting_item in accounting:
                code_credit = accounting_item[account_code_credit]
                code_debit = accounting_item[account_code_debit]
                for chart_of_account_data in ret:
                    if chart_of_account_data['_id'] == code_credit:
                        chart_of_account_data['credit'] += totalAmountPaid
                    if chart_of_account_data['_id'] == code_debit:
                        chart_of_account_data['debit'] += totalAmountPaid

        return {'data': ret }

    except Exception as e:
        return {'message': repr(e) }, 500
