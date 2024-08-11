


from datetime import datetime, date
import uuid
from bson import ObjectId
from flask import Blueprint, jsonify, request
from pydash import omit

from app.filters.date_filter import DateFilter, compare_date_filter
from app.middlewares.authorized_attribute import authorized
from app.new_models.CashCount import CashCount
from app.new_models.CashierReport import TimeInCashierReport, TimeOutCashierReport
from app.new_models.Transaction import CreateTransaction
from app.repositories.transaction import TransactionRepository
from app.utils.filter_values import filterValues
from app.utils.utils import getTimeZone

api = '/v2/transactions'
transaction_bp = Blueprint('transactions', __name__)
repository = TransactionRepository()

@transaction_bp.get(api)
@authorized
def get_transactions(user_id):
    date_filter = int(request.args.get('dateFilter', DateFilter.ALL))
    custom_date = request.args.get('customDate')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    cashierId = request.args.get('cashierId')

    query = {} if cashierId is None else { 'cashierId': cashierId }

    transaction = repository.find(query)

    filtered_transaction = [
        transaction for transaction in transaction 
        if compare_date_filter(
            date_filter, 
            transaction['date'],
            custom_date,
            start_date,
            end_date
        )
    ]

    return jsonify({'data': filtered_transaction})

@transaction_bp.post(api)
@authorized
def create_transaction(user_id):
    request_data = request.get_json()
    active_transaction = repository.find_active(user_id)

    if active_transaction is not None:
        return { 
            'data': active_transaction, 
            'message': 'Return active transaction' 
        }, 200
        
    transaction = CreateTransaction(
        branchId=request_data['branchId'],
        cashierId=user_id
    )

    result = repository.insert_one(transaction.dict())
    if result is not None:
        return jsonify({'message': 'Transaction created successfully', 'data': result })
    else:
        return jsonify({'error': 'Unable to create transaction'}), 500


@transaction_bp.get(api + '/<id>')
@authorized
def get_transaction(user_id, id):
    data = repository.find_one({ '_id': ObjectId(id) })
    return jsonify({'data': data})

@transaction_bp.get(api + '/active')
@authorized
def get_active_transaction(user_id):
    data = repository.find_active(user_id)
    return jsonify({'data': data})
