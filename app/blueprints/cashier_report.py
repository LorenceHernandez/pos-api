


from bson import ObjectId
from flask import Blueprint, jsonify, request,g
from pydantic import ValidationError
from pydash import omit, pick 

from app.filters.date_filter import DateFilter
from app.middlewares.authorized_attribute import authorized
from app.new_models.AuditLog import AuditCode, AuditLog
from app.new_models.CashierReport import TimeInCashierReport, TimeOutCashierReport
from app.repositories.audit_log import AuditLogRepository
from app.repositories.cashier_report import CashierReportRepository
from app.utils.utils import getLocalDateStr, getLocalTimeStr

api = '/v2/cashier-reports'
cashier_report_bp = Blueprint('cashier-reports', __name__)
repository = CashierReportRepository()
logger = AuditLogRepository()


@cashier_report_bp.route(api)
@authorized
def get_reports(user_id):
    date_filter = int(request.args.get('dateFilter', DateFilter.ALL))
    custom_date = request.args.get('customDate')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    params = pick(request.args.to_dict(), ['date', 'cashierId'])

    try:
        previous_report = repository.find_one({ 
            'cashierId': user_id, 
        })

        # query = {} if cashierId is None else { 'cashierId': cashierId }
        reports = repository.find_by_date_and(date_filter, start_date, end_date, custom_date, params)

        return jsonify({
            'data': {
                'previousReports': previous_report,
                'reports': reports
            }
        })
    # except ValidationError as e:
    #     return jsonify({'message': 'Unable to get reports', 'error': e.errors(include_input=False)}), 500
    except Exception as e:
        return jsonify({'message': 'Unable to get reports', 'error': repr(e)}), 500

@cashier_report_bp.post(api + '/time-in')
@authorized
def time_in_report(user_id):
    request_data = request.get_json()

    date_today = getLocalDateStr()
    report = repository.find_one({ 
        'cashierId': user_id, 
        'date': date_today,
        'branchId': request_data['branchId']
    })

    if(report is not None):
        return jsonify({ 'data': report, 'message': 'Report today returned' })
    
    report = TimeInCashierReport(
        **request_data, 
        timeIn=getLocalTimeStr(),
        cashierId=user_id,
        date=date_today
    )
    result = repository.insert_one(report.model_dump())

    if result is not None:
        logger.insert_one(AuditLog(action=AuditCode.CASHIER_REPORT_TIME_IN, userId=g.user_id, data=report.model_dump()))
        return jsonify({'message': 'Report created successfully'})
    else:
        logger.insert_one(AuditLog(action=AuditCode.CASHIER_REPORT_TIME_IN_ERR, userId=g.user_id, error='Unable to time in report'))
        return jsonify({'error': 'Unable to create report'}), 500

@cashier_report_bp.post(api + '/time-out')
@authorized
def time_out_report(_):
    request_data = request.get_json()

    report = TimeOutCashierReport(
        **request_data,
        timeOut=getLocalTimeStr(),
    )

    query = { '_id': ObjectId(report.id) }
    # new_val = { "$set": report.model_dump(exclude_none=True, exclude={'id'}) }
    result = repository.update_one(query, report)    

    if result is not None:
        logger.insert_one(AuditLog(action=AuditCode.CASHIER_REPORT_TIME_OUT, userId=g.user_id, data=report.model_dump()))

        return jsonify({'message': 'Report updated successfully', 'data': result })
    else:
        logger.insert_one(AuditLog(action=AuditCode.CASHIER_REPORT_TIME_OUT_ERR, userId=g.user_id, data=report.model_dump(), error='Unable to time out report'))

        return jsonify({'error': 'Unable to update report'}), 500
    

