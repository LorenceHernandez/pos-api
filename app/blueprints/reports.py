from datetime import datetime
import os
from bson import ObjectId
from flask import Blueprint, jsonify, request, send_file
import openpyxl
import io
from pydantic import ValidationError
from pydash import omit, start_case

from app.filters.date_filter import compare_date_filter
from app.middlewares.authorized_attribute import authorized
from app.new_models.Filter import BranchFilter, ComparativeReportFilter, DateRangeFilter, DiscountsReportFilter, ReportFilter
from app.new_models.Transaction import TransactionDiscountQuery
from app.repositories.branch_reports import BranchReportRepository
from app.repositories.category import CategoryRepository
from app.repositories.transaction_discount import TransactionDiscountRepository
from app.database.config import users
from app.utils.reports import export_discount_reports, export_sales_reports, get_template_name, load_sheet


api = '/v2/reports'
v2_reports_bp = Blueprint('v2-reports', __name__)
discountRepository = TransactionDiscountRepository()
branchReportRepository = BranchReportRepository()
categoryRepository = CategoryRepository()


@v2_reports_bp.get(api + '/discounts')
@authorized
def get_discount_report(user_id):
    params = request.args.to_dict()
    
    try:
        filter = DiscountsReportFilter(dateRangeFilter=DateRangeFilter(**params), **params)
        reports = discountRepository.find(filter.transform())
        return jsonify({ 'data': reports })
    
    except ValidationError as e:
        return jsonify({'message': 'Unable to get discount reports', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to get discount reports', 'error': repr(e)}), 500
    
@v2_reports_bp.route(api + '/discounts/download')
@authorized
def download_discount_report(user_id):
    date_filter = int(request.args.get('dateFilter', DateRangeFilter.ALL))
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
        return jsonify({'message': 'Unable to get download reports', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to get download reports', 'error': repr(e)}), 500
    
@v2_reports_bp.route(api + '/sales')
@authorized
def get_sales_report(user_id):
    params = request.args.to_dict()

    try:
        filter = ReportFilter(dateRangeFilter=DateRangeFilter(**params), **params)
        reports = branchReportRepository.find(filter.transform())

        return jsonify({ 'data': reports })
    except ValidationError as e:
        return jsonify({'message': 'Unable to get reports', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to get reports', 'error': repr(e)}), 500

@v2_reports_bp.route(api + '/sales/download')
@authorized
def download_sales_report(user_id):
    date_filter = int(request.args.get('dateFilter', DateRangeFilter.ALL))
    custom_date = request.args.get('customDate')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')

    try:
        reports = branchReportRepository.find_by_date_and(date_filter, start_date, end_date, custom_date)
        workbook = load_sheet('annex_template.xlsx')
        output = export_sales_reports(workbook, reports, user_id)

        return send_file(
            output, 
            download_name='annex_sales_summary.xlsx', 
            as_attachment=True, 
            mimetype=workbook.mime_type
        )
    except ValidationError as e:
        return jsonify({'message': 'Unable to download sales', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to download sales', 'error': repr(e)}), 500

@v2_reports_bp.route(api + '/comparative')
@authorized
def get_comparative_report(user_id):
    params = request.args.to_dict()

    try:
        filter = ComparativeReportFilter(dateRangeFilter=DateRangeFilter(**params), **params)
        reports = categoryRepository.compare_category_sales(
            omit(filter.transform(), 'date'),
            filter.date1Filter,
            filter.date2Filter
        )
        return jsonify({ 'data': reports })
    except ValidationError as e:
        return jsonify({'message': 'Unable to get reports', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to get reports', 'error': repr(e)}), 500

@v2_reports_bp.route(api + '/payment')
@authorized
def get_payement_types_report(user_id):
    params = request.args.to_dict()

    try:
        filter = ReportFilter(dateRangeFilter=DateRangeFilter(**params), **params)
        reports = categoryRepository.find_payment_types(filter)
        return jsonify({ 'data': reports })
    except ValidationError as e:
        return jsonify({'message': 'Unable to get reports', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to get reports', 'error': repr(e)}), 500

