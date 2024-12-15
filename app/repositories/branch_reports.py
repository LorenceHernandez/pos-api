


from app.filters.date_filter import DateFilter, compare_date_filter
from app.new_models.CashierReport import CashierReport
from app.new_models.Transaction import TransactionStatus
from app.repositories.base import BackupRepository
from app.repositories.cashier_report import CashierReportRepository
from app.repositories.transaction import TransactionRepository


class BranchReportRepository(BackupRepository):
    _collection = 'branch_reports'
    _transaction_collection = TransactionRepository()._collection
    _cashier_report_collection = CashierReportRepository()._collection

    def find(self, query={}, *args):
        try:
            data = list(self._db[self._collection].aggregate([
                { '$match': query },
                {
                    "$addFields": {
                        "cashierId": {"$toObjectId": "$cashierId"},
                        "branchId": {"$toObjectId": "$branchId"}
                    }
                },
                { 
                    '$lookup': {
                        'from': 'users',
                        'localField': 'cashierId',
                        'foreignField': '_id',
                        'as': 'cashier'
                    }, 
                },
                { "$unwind": "$cashier" },
                { 
                    '$lookup': {
                        'from': 'branches',
                        'localField': 'branchId',
                        'foreignField': '_id',
                        'as': 'branch'
                    }, 
                },
                { "$unwind": "$branch" },
                {
                    "$addFields": {
                        "branchId": {"$toString": "$branchId"}
                    }
                },
                {
                    "$lookup": {
                        "from": self._transaction_collection,
                        "let": {
                            "branchIds": "$cashier.branches",
                            "date": "$date"
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            { "$in": ['$branchId', '$$branchIds'] },
                                            { "$eq": ["$date", "$$date"] },
                                            { "$eq": ["$status", TransactionStatus.COMPLETED.value] }
                                        ]
                                    },
                                }
                            },
                            { 
                                '$group': {
                                    "_id": None,
                                    "totalGrossSales": { "$sum": "$totalGrossSales" },
                                    "totalNetSales": { "$sum": "$totalNetSales" },
                                    "totalDiscount": { "$sum": '$totalDiscount' } ,
                                    "totalSalesWithoutMemberDiscount": { "$sum": '$totalSalesWithoutMemberDiscount' } ,
                                    "totalMemberDiscount": { "$sum": '$totalMemberDiscount' } ,
                                    "invoiceStartNumber": { '$min': "$invoiceNumber" },
                                    "invoiceEndNumber": { '$max': "$invoiceNumber" },
                                }
                            },
                        ],
                        "as": "sales"
                    }
                },
                {
                    "$lookup": {
                        "from": 'transaction_discount',
                        "let": {
                            "branchIds": "$cashier.branches",
                            "date": "$date"
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            { "$in": ['$branchId', '$$branchIds'] },
                                            { "$eq": ["$date", "$$date"] },
                                            { "$eq": ["$status", TransactionStatus.COMPLETED.value] }
                                        ]
                                    },
                                },
                            },
                            { 
                                '$group': {
                                    "_id": "$status",
                                    "totalGrossSales": { "$sum": "$totalGrossSales" },
                                    "totalNetSales": { "$sum": "$totalNetSales" },
                                    "totalDiscount": { "$sum": '$totalDiscount' } ,
                                    "totalSalesWithoutMemberDiscount": { "$sum": '$totalSalesWithoutMemberDiscount' } ,
                                    "totalMemberDiscount": { "$sum": '$totalMemberDiscount' } ,
                                    "invoiceStartNumber": { '$min': "$invoiceNumber" },
                                    "invoiceEndNumber": { '$max': "$invoiceNumber" },
                                }
                            },
                        ],
                        "as": "discounts"
                    }
                },
                { "$unwind": {
                    'path': "$sales",
                    'preserveNullAndEmptyArrays': True    
                }},
                {
                    '$project': {
                        "discounts._id": 0,
                        "sales._id": 0,
                        'cashierId': 0,
                        'branchId': 0,
                        'cashier': 0
                    }
                },
                { "$sort": { "_id": -1 }},
                *args,
                {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        "branch._id": { "$toString": "$branch._id" },
                    }
                }
            ]))

            reports = []
            for item in data:
                reports.append(item)
            return reports
        except Exception as e:
            raise e

    def find_sales(self, query={}, *args):
        try:
            data = list(self._db[self._cashier_report_collection].aggregate([
                { '$match': query },
                {
                    "$lookup": {
                        "from": self._transaction_collection,
                        "let": {
                            "branchId": "$branchId",
                            "date": "$date"
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            { "$eq": ["$branchId", "$$branchId"] },
                                            { "$eq": ["$date", "$$date"] },
                                        ]
                                    }
                                }
                            },
                            { 
                                '$group': {
                                    "_id": None,
                                    "totalGrossSales": { "$sum": "$totalGrossSales" },
                                    "totalNetSales": { "$sum": "$totalNetSales" },
                                    "totalDiscount": { "$sum": '$totalDiscount' } ,
                                    "totalSalesWithoutMemberDiscount": { "$sum": '$totalSalesWithoutMemberDiscount' } ,
                                    "totalMemberDiscount": { "$sum": '$totalMemberDiscount' } ,
                                    "invoiceStartNumber": { '$min': "$invoiceNumber" },
                                    "invoiceEndNumber": { '$max': "$invoiceNumber" },
                                }
                            },
                        ],
                        "as": "sales"
                    }
                },
                { "$unwind": {
                    'path': "$sales",
                    'preserveNullAndEmptyArrays': True    
                }},
                {
                    "$group": {
                        "_id": None,
                        'date': { '$first': '$date' },
                        'branchId': { '$first': '$branchId' },
                        "beginningCashOnHandTotal": { "$sum": "$beginningCashOnHand.total" },
                        "beginningCashOnHandCount": { "$push": "$beginningCashOnHand.count" },
                        "endingCashOnHandCount": { "$push": "$endingCashOnHand.count" },
                        "endingCashOnHandTotal": { "$sum": "$endingCashOnHand.total" },
                        "totalGrossSales": { "$sum": "$sales.totalGrossSales" },
                        "totalNetSales": { "$sum": "$sales.totalNetSales" },
                        "totalDiscount": { "$sum": "$sales.totalDiscount" },
                        "totalSalesWithoutMemberDiscount": { "$sum": '$sales.totalSalesWithoutMemberDiscount' } ,
                        "totalMemberDiscount": { "$sum": '$sales.totalMemberDiscount' } ,
                        "invoiceStartNumber": { '$min': "$sales.invoiceStartNumber" },
                        "invoiceEndNumber": { '$max': "$sales.invoiceEndNumber" }
                    }
                },
                {
                    "$addFields": {
                        "branchId": {"$toObjectId": "$branchId"}
                    }
                },
                { 
                    '$lookup': {
                        'from': 'branches',
                        'localField': 'branchId',
                        'foreignField': '_id',
                        'as': 'branch'
                    }, 
                },
                { "$unwind": "$branch" },
                {
                    "$addFields": {
                        "branchId": {"$toString": "$branchId"}
                    }
                },
                {
                    "$lookup": {
                        "from": 'transaction_discount',
                        "let": {
                            "branchId": "$branchId",
                            "date": "$date"
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            { "$eq": ["$branchId", "$$branchId"] },
                                            { "$eq": ["$date", "$$date"] },
                                        ]
                                    }
                                },
                            },
                            {
                                "$addFields": {
                                    "_id": { "$toString": "$_id" },
                                }
                            }
                        ],
                        "as": "discounts"
                    }
                },
                {
                    '$project': {
                        "_id": 0,
                        'branchId': 0,
                    }
                },
                {
                    "$addFields": {
                        "branch._id": { "$toString": "$branch._id" },
                    }
                }
            ]))

            if(len(data) > 0):
                return data[0]
            return None
        except Exception as e:
            raise e
        
    def find_by_date_and(self, date_filter: DateFilter, start_date=None, end_date=None, custom_date=None, query={}):
        reports = self.find(query)

        if(date_filter == DateFilter.CUSTOM_DATE and custom_date is None):
            return []
        
        if(date_filter == DateFilter.CUSTOM_FILTER and start_date is None and end_date is None):
            return []


        filtered_reports = [
            report for report in reports 
            if compare_date_filter(
                date_filter, 
                report['date'],
                custom_date,
                start_date,
                end_date
            )
        ]

        return filtered_reports