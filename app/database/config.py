
from pymongo import MongoClient

from app.config import IS_INTERNAL_PRODUCTION, IS_PRODUCTION
from .database import get_current_database, remote_database, internal_prod_database

# MONGO_PORT = os.getenv('MONGO_PORT')
# MONGO_HOST_PY = os.getenv('MONGO_HOST_PY')
# MONGO_USER = os.getenv('MONGO_USER')
# MONGO_PASS = os.getenv('MONGO_PASS')
# LOCAL = os.getenv('LOCAL')

# if IS_DEVELOPMENT:
database = get_current_database().connect()
users = database.users
products = database.products
doctors = database.doctors
product_categories = database.product_categories
branches = database.branches
corporates = database.corporates
customers = database.customers
packages = database.packages
roles = database.roles
transactions = database.transactions
discounts = database.discounts
sales = database.sales
bookings = database.bookings
cashier_reports = database.cashier_reports
sales_deposits = database.sales_deposits  
branch_reports = database.branch_reports  
counters = database.counters