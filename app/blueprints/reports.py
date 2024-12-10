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

        fileName = os.path.join(os.getcwd(), 'app', 'templates', f'annex_{query.memberType.value}_template.xlsx')
        workbook = openpyxl.load_workbook(fileName)
        worksheet = workbook.active

        worksheet.cell(9, 1, datetime.now().isoformat())
        worksheet.cell(5, 1, os.getenv('APP_VERSION'))

        user = users.find_one({ '_id': ObjectId(user_id) })
        worksheet.cell(10, 1, start_case(f'{user['first_name']} {user['last_name']}'))
        

        default_row = 17
        for index, reports in enumerate(filtered_reports):
            default_col = 1
            worksheet.cell(column=default_col, row=default_row + index, value=reports['transaction']['transactionDate'])
            worksheet.cell(column=default_col + 1, row=default_row + index, value=reports['customer']['name'])
            worksheet.cell(column=default_col + 2, row=default_row + index, value=reports['customer']['customer_type_id'])
            worksheet.cell(column=default_col + 3, row=default_row + index, value=reports['customer']['tin_number'])
            worksheet.cell(column=default_col + 4, row=default_row + index, value=reports['transaction']['invoiceNumber'])
            worksheet.cell(column=default_col + 5, row=default_row + index, value=reports['transaction']['totalSalesWithoutMemberDiscount'])
            worksheet.cell(column=default_col + 9, row=default_row + index, value=reports['transaction']['totalMemberDiscount'])
            worksheet.cell(column=default_col + 10, row=default_row + index, value=reports['transaction']['totalNetSales'])

            # worksheet.cell(column=2, row=default_row + index, value=reports['transaction']['transactionDate'])
        
        output = io.BytesIO()
        workbook.save(output)
        output.seek(0)


        return send_file(
            output, 
            download_name='annex_naac_template.xlsx', 
            as_attachment=True, 
            mimetype=workbook.mime_type
        )
    
    except ValidationError as e:
        return jsonify({'message': 'Unable to get discount reports', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to get discount reports', 'error': repr(e)}), 500
    