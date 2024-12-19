from bson import ObjectId
from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.filters.date_filter import DateFilter, compare_date_filter
from app.middlewares.authorized_attribute import authorized
from app.new_models.Transaction import CreateTransaction
from app.new_models.Transaction import CreateRefundTransaction, CreateTransaction, CreateVoidTransaction, TransactionStatus
from app.repositories.transaction import TransactionRepository
from app.repositories.transaction_discount import TransactionDiscountRepository
from app.services.Transaction import TransactionService

api = '/v2/transactions'
transaction_bp = Blueprint('transactions', __name__)
transactionRepository = TransactionRepository()
discountRepository = TransactionDiscountRepository()

@transaction_bp.get(api)
@authorized
def get_transactions(user_id):
    date_filter = int(request.args.get('dateFilter', DateFilter.ALL))
    custom_date = request.args.get('customDate')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    cashierId = request.args.get('cashierId')

    try:
        query = {} if cashierId is None else { 'cashierId': cashierId }

        transaction = transactionRepository.find(query)

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
    except ValidationError as e:
        return jsonify({'message': 'Unable to get transactions', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to get transactions', 'error': repr(e)}), 500
    

@transaction_bp.post(api)
@authorized
def create_transaction(user_id):
    try:
        request_data = request.get_json()
        active_transaction = transactionRepository.find_active(user_id)

        if active_transaction is not None:
            return { 
                'data': active_transaction, 
                'message': 'Return active transaction' 
            }, 200
            
        transaction = CreateTransaction(
            **request_data,
            cashierId=user_id,
        )

        result = transactionRepository.insert_one(transaction.model_dump())
        if result is None:
            raise Exception()
        
        return jsonify({'message': 'Transaction created successfully', 'data': result })
    except ValidationError as e:
        return jsonify({'message': 'Unable to process data', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to create transaction', 'error': repr(e)}), 500


@transaction_bp.get(api + '/<id>')
@authorized
def get_transaction(user_id, id):
    try:
        data = transactionRepository.find_one({ '_id': ObjectId(id) })
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'message': 'Unable to get transaction', 'error': repr(e)}), 500

@transaction_bp.get(api + '/active')
@authorized
def get_active_transaction(user_id):
    try:
        data = transactionRepository.find_active(user_id)
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'message': 'Unable to get active transaction', 'error': repr(e)}), 500

@transaction_bp.get(api + '/<id>/print')
@authorized
def print_transaction(user_id, id):
    service = TransactionService()

    try:
        data = transactionRepository.find_one({ '_id': ObjectId(id) })
        service.print(data)
        return jsonify({'message': 'Transaction printed successfully'})
    except Exception as e:
        return jsonify({'message': 'Unable to get transaction', 'error': repr(e)}), 500


@transaction_bp.post('/v3/transactions')
@authorized
def v3_create_transaction(user_id):
    try:
        request_data = request.get_json()
        args = { **request_data, "cashierId": user_id }
        model = CreateTransaction(**args)

        if(model.status == TransactionStatus.VOIDED):
            model = CreateVoidTransaction(**args)
        if(model.status == TransactionStatus.REFUNDED):
            model = CreateRefundTransaction(**args)
       
        result = transactionRepository.insert_one(model)

        discounts = list(map(
            lambda i: { 
                **i.model_dump(exclude='id'),
                'discountId': i.id, 
                'transactionId': result['_id'],
                'customerId': result['customer']['_id'],
                'memberId': result['customer']['customer_type_id'],
                **model.model_dump(
                    include={
                        'cashierId', 
                        'branchId', 
                        'date',
                        'status'
                    }
                )
            }, 
            model.discounts
        ))
        if(len(discounts) > 0):
            discountRepository.insert_many(discounts)

        result = transactionRepository.find_one({ '_id': ObjectId(result['_id']) })
        return jsonify({'message': 'Transaction created successfully', 'data': result })
    except ValidationError as e:
        return jsonify({'message': 'Unable to process data', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to create transaction', 'error': repr(e)}), 500

