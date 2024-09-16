


from bson import ObjectId
from flask import Blueprint, jsonify, request

from app.filters.date_filter import DateFilter
from app.middlewares.authorized_attribute import authorized
from app.new_models.CashierReport import TimeInCashierReport, TimeOutCashierReport
from app.repositories.cashier_report import CashierReportRepository
from app.utils.utils import getLocalDateStr, getLocalTimeStr

api = '/api/cas/items'
item_bp = Blueprint('items', __name__)


@item_bp.route(api)
@authorized
def get_items(user_id):
    print('get item ' + user_id)

