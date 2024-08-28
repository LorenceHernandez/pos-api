


from datetime import datetime, date
from bson import ObjectId
from flask import Blueprint, jsonify, request
from pydash import omit

from app.filters.date_filter import DateFilter, compare_date_filter
from app.middlewares.authorized_attribute import authorized
from app.new_models.CashCount import CashCount
from app.new_models.CashierReport import TimeInCashierReport, TimeOutCashierReport
from app.repositories.cashier_report import CashierReportRepository
from app.utils.filter_values import filterValues
from app.utils.utils import getTimeZone

api = '/v2/cashier-reports'
cashier_report_bp = Blueprint('cashier-reports', __name__)
repository = CashierReportRepository()

@cashier_report_bp.route(api)
@authorized
def get_reports(user_id):
    date_filter = int(request.args.get('dateFilter', DateFilter.ALL))
    custom_date = request.args.get('customDate')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    cashierId = request.args.get('cashierId')

    previous_report = repository.find_one({ 
        'cashierId': user_id, 
        'timeOut': { '$ne': None } 
    })

    query = {} if cashierId is None else { 'cashierId': cashierId }
    reports = repository.find_by_date_and(date_filter, start_date, end_date, custom_date, query)

    return jsonify({
        'data': {
            'previousReports': previous_report,
            'reports': reports
        }
    })

@cashier_report_bp.post(api + '/time-in')
@authorized
def time_in_report(user_id):
    request_data = request.get_json()

    date_today = str(datetime.now(getTimeZone()).date())
    report = repository.find_one({ 
        'cashierId': user_id, 
        'date': date_today,
        'branchId': request_data['branchId']
    })

    if(report is not None):
        return jsonify({ 'data': report, 'message': 'Report today returned' })
    
    report = TimeInCashierReport(**request_data)
    report.timeIn = datetime.now(getTimeZone()).isoformat()
    report.cashierId = user_id
    report.date = date_today

    result = repository.insert_one(report.dict())

    if result is not None:
        return jsonify({'message': 'Report created successfully'})
    else:
        return jsonify({'error': 'Unable to create report'}), 500

@cashier_report_bp.post(api + '/time-out')
@authorized
def time_out_report(user_id):
    request_data = request.get_json()
    id = request_data['_id']

    report = TimeOutCashierReport(**request_data)
    report.timeOut = datetime.now(getTimeZone()).isoformat()
    report.endingCashOnHand = CashCount(**request_data['endingCashOnHand'])

    query = { '_id': ObjectId(id) }
    new_val = { "$set": filterValues(report.dict()) }
    result = repository.update_one(query, new_val)
    
    updated_value = repository.find_one({ '_id': ObjectId(id) })

    if result is not None:
        return jsonify({'message': 'Report updated successfully', 'data': updated_value })
    else:
        return jsonify({'error': 'Unable to update report'}), 500
    

