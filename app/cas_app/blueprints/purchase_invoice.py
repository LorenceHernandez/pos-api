from bson import ObjectId
from flask import Blueprint, jsonify, request
from pydash import omit

from app.cas_app.models.new_models.PurchaseInvoice import PurchaseInvoice
from app.database.config import purchase_invoices
from app.database.store import insert_one
from app.middlewares.authorized_attribute import authorized
from app.utils.filter_values import filterValues

api = '/api/cas/purchase_invoice'
purchase_invoice_bp = Blueprint('purchase_invoices', __name__)

@purchase_invoice_bp.get(api + 's')
@authorized
def get_purchase_invoices(user_id):
    ret = []
    try:

        data = purchase_invoices.find()
        for item in data: 
          ret.append(PurchaseInvoice.fromDict(item).toDict())
            
        return {'data': ret }

    except Exception as e:
        return {'message': repr(e) }, 500


@purchase_invoice_bp.get(api + 's-invoice/history')
@authorized
def get_purchase_invoices(user_id):
    ret = []
    try:

        data = purchase_invoices.find()
        for item in data: 
          ret.append(PurchaseInvoice.fromDict(item).toDict())
            
        return {'data': ret }

    except Exception as e:
        return {'message': repr(e) }, 500

    
@purchase_invoice_bp.post(api + '/create')
@authorized
def create_purchase_invoice(user_id):
    request_data = request.get_json()
    
    try:
        doc = insert_one('purchase_invoices', filterValues(PurchaseInvoice.fromDict(request_data).toDict()))
        if doc.inserted_id:
            return {'message': 'PurchaseInvoice successfully created.'}
        else:
            return {'message': 'Unable to create PurchaseInvoice.'}, 500
    except Exception as e:
        return {'message': repr(e)}, 500
    
