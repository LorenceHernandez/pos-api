


from flask import Blueprint, jsonify, request
from pydantic import ValidationError 

from app.middlewares.authorized_attribute import authorized
from app.new_models.Sales import GetGeneratedSales
from app.repositories.branch_reports import BranchReportRepository

api = '/v2/sales'
sales_bp = Blueprint('sales', __name__)
repository = BranchReportRepository()


@sales_bp.route(api)
@authorized
def get_generated_sales(user_id):
    params = request.args.to_dict()

    try:
        model = GetGeneratedSales(**params)
        query = model.model_dump()
        sales = repository.find_sales(query)
        return jsonify({ 'data': { 'sales': sales } })
    except ValidationError as e:
        return jsonify({'message': 'Unable to get reports', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to get reports', 'error': repr(e)}), 500
