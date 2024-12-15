


from datetime import datetime
import io
from itertools import groupby
import os
from bson import ObjectId
from flask import Blueprint, jsonify, request, send_file
import openpyxl
from pydantic import ValidationError
from pydash import start_case 

from app.middlewares.authorized_attribute import authorized
from app.new_models.Discount import MemberType
from app.new_models.Sales import GetBranchSalesQuery
from app.repositories.branch_reports import BranchReportRepository
from app.database.config import users
from app.utils.reports import export_sales_reports, load_sheet
from app.utils.utils import getLocalDateStr

api = '/v2/sales'
sales_bp = Blueprint('sales', __name__)
repository = BranchReportRepository()


@sales_bp.get(api + '/today')
@authorized
def get_today_sales(user_id):
    params = request.args.to_dict()

    try:
        model = GetBranchSalesQuery(**params, date=getLocalDateStr())
        query = model.model_dump()
        sales = repository.find_sales(query)
        return jsonify({ 'data': sales })
    except ValidationError as e:
        return jsonify({'message': 'Unable to get sales', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to get sales', 'error': repr(e)}), 500


@sales_bp.get(api)
@authorized
def get_sales(user_id):
    params = request.args.to_dict()

    try:
        model = GetBranchSalesQuery(**params)
        query = model.model_dump(exclude_unset=True)
        sales = repository.find(query)
        return jsonify({ 'data': sales })
    except ValidationError as e:
        return jsonify({'message': 'Unable to get sales', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to get sales', 'error': repr(e)}), 500

@sales_bp.get(api + '/download')
@authorized
def download_sales(user_id):
    params = request.args.to_dict()

    try:
        model = GetBranchSalesQuery(**params)
        query = model.model_dump(exclude_unset=True)
        sales = repository.find(query)
        
        fileName = 'annex_template.xlsx'
        workbook = load_sheet(fileName)
        output = export_sales_reports(sales, user_id)

        return send_file(
            output, 
            download_name=fileName, 
            as_attachment=True, 
            mimetype=workbook.mime_type
        )

    except ValidationError as e:
        return jsonify({'message': 'Unable to get sales', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to get sales', 'error': repr(e)}), 500
