from datetime import datetime
import os
from bson import ObjectId
from flask import Blueprint, jsonify, request, send_file
import openpyxl
import io
from pydantic import ValidationError
from pydash import start_case

from app.filters.date_filter import DateFilter, compare_date_filter
from app.middlewares.authorized_attribute import authorized
from app.new_models.Transaction import TransactionDiscountQuery
from app.repositories.transaction_discount import TransactionDiscountRepository
from app.database.config import users
from app.utils.reports import export_discount_reports, get_template_name, load_sheet


api = '/v2/discount-reports'
discount_reports_bp = Blueprint('discount-reports', __name__)
discountRepository = TransactionDiscountRepository()

@discount_reports_bp.get(api)
@authorized
def get_discount_reports(user_id):
    date_filter = int(request.args.get('dateFilter', DateFilter.ALL))
    custom_date = request.args.get('customDate')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    
    try:
        query = TransactionDiscountQuery(**request.args.to_dict())
        discount = discountRepository.find({
            'memberType': {"$ne": None},
            **query.model_dump(exclude_unset=True)
        })

        filtered_reports = [
            transaction for transaction in discount 
            if compare_date_filter(
                date_filter, 
                transaction['date'],
                custom_date,
                start_date,
                end_date
            )
        ]

        return jsonify({'data': filtered_reports})
    except ValidationError as e:
        return jsonify({'message': 'Unable to get discount reports', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to get discount reports', 'error': repr(e)}), 500
    
@discount_reports_bp.route(api + '/download')
@authorized
def download_discount_reports(user_id):
    date_filter = int(request.args.get('dateFilter', DateFilter.ALL))
    custom_date = request.args.get('customDate')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    
    try:
        query = TransactionDiscountQuery(**request.args.to_dict())
        discount = discountRepository.find(query.model_dump(exclude_unset=True))

        filtered_reports = [
            transaction for transaction in discount 
            if compare_date_filter(
                date_filter, 
                transaction['date'],
                custom_date,
                start_date,
                end_date
            )
        ]

        type = query.memberType
        templateName = get_template_name(type)
        workbook = load_sheet(templateName)
        output = export_discount_reports(workbook, type, filtered_reports, user_id)

        return send_file(
            output, 
            download_name=templateName, 
            as_attachment=True, 
            mimetype=workbook.mime_type
        )
    
    except ValidationError as e:
        return jsonify({'message': 'Unable to get discount reports', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to get discount reports', 'error': repr(e)}), 500
    