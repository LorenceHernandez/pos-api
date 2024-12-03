


from bson import ObjectId
from flask import Blueprint, jsonify, request,g
from pydantic import ValidationError 

from app.filters.date_filter import DateFilter
from app.middlewares.authorized_attribute import authorized
from app.new_models.AuditLog import AuditCode, AuditLog
from app.new_models.CashierReport import TimeInCashierReport, TimeOutCashierReport
from app.repositories.audit_log import AuditLogRepository
from app.repositories.branch_reports import BranchReportRepository
from app.utils.utils import getLocalDateStr, getLocalTimeStr

api = '/v2/branch-reports'
branch_report_bp = Blueprint('branch-reports', __name__)
repository = BranchReportRepository()
logger = AuditLogRepository()


@branch_report_bp.route(api)
@authorized
def get_reports(user_id):
    date_filter = int(request.args.get('dateFilter', DateFilter.ALL))
    custom_date = request.args.get('customDate')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')

    try:
        reports = repository.find_by_date_and(date_filter, start_date, end_date, custom_date)
        return jsonify({ 'data': { 'reports': reports } })
    except ValidationError as e:
        return jsonify({'message': 'Unable to get reports', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to get reports', 'error': repr(e)}), 500
