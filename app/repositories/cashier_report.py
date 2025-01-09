


from itertools import groupby

from pydash import get
from app.filters.date_filter import DateFilter, compare_date_filter
from app.new_models.CashierReport import CashierReport
from app.new_models.Transaction import TransactionStatus
from app.repositories.base import BackupRepository
from app.repositories.transaction import TransactionRepository


class CashierReportRepository(BackupRepository):
    _collection = 'cashier_reports'
    _transaction_collection = TransactionRepository()._collection

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
                        "cashierId": {"$toString": "$cashierId"},
                        "branchId": {"$toString": "$branchId"}
                    }
                },
                {
                    "$lookup": {
                        "from": self._transaction_collection,
                        "let": {
                            "branchId": "$branchId",
                            "cashierId": "$cashierId",
                            "date": "$date"
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            { "$eq": ["$branchId", "$$branchId"] },
                                            { "$eq": ["$cashierId", "$$cashierId"] },
                                            { "$eq": ["$date", "$$date"] },
                                        ]
                                    }
                                }
                            },
                        ],
                        "as": "transactions"
                    }
                },
                {
                    "$lookup": {
                        "from": self._transaction_collection,
                        "let": {
                            "branchId": "$branchId",
                            "cashierId": "$cashierId",
                            "date": "$date"
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            { "$eq": ["$branchId", "$$branchId"] },
                                            { "$eq": ["$cashierId", "$$cashierId"] },
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
                {
                    "$lookup": {
                        "from": 'transaction_discount',
                        "let": {
                            "branchId": "$branchId",
                            "cashierId": "$cashierId",
                            "date": "$date"
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            { "$eq": ["$branchId", "$$branchId"] },
                                            { "$eq": ["$cashierId", "$$cashierId"] },
                                            { "$eq": ["$date", "$$date"] },
                                        ]
                                    }
                                },
                            },
                            {
                                "$addFields": {
                                    "transactionId": {"$toObjectId": "$transactionId"}
                                }
                            },
                            { 
                                '$lookup': {
                                    'from': self._transaction_collection,
                                    'localField': 'transactionId',
                                    'foreignField': '_id',
                                    'as': 'transaction'
                                }, 
                            },
                            { "$unwind": "$transaction" },
                            {
                                '$project': {
                                    "_id": 0,
                                    "transactionId": 0,
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
                    "$addFields": {
                        "cashier.name": {
                            "$concat": [
                                "$cashier.first_name",
                                " ",
                                "$cashier.last_name"
                            ]
                        }
                    }
                },

                {
                    '$project': {
                        "discounts._id": 0,
                        "discounts.transaction._id": 0,
                        "discounts.transaction.transactionId": 0,
                        "discounts.transaction.transactionItems": 0,
                        "transactions._id": 0,
                        "transactions.transactionItems": 0,
                        "sales._id": 0,
                        'cashierId': 0,
                        'branchId': 0,
                        'cashier': {
                            'password': 0,
                            'branches': 0
                        }
                    }
                },
                { "$sort": { "_id": -1 }},
                *args,
                {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        "cashier._id": { "$toString": "$cashier._id" },
                        "branch._id": { "$toString": "$branch._id" },
                    }
                }
            ]))
            reports = []
            for item in data:
                discountSummary = {}
                discounts = filter(lambda i: i['memberType'] is not None, item['discounts'])
                for key, value in groupby(discounts, lambda i: i['memberType']):
                    discountSummary[key] = sum(map(lambda i: i['transaction']['totalMemberDiscount'], value))
                item['discountSummary'] = discountSummary


                salesAdjustment = {}
                for key, value in groupby(item['transactions'], lambda i: i['status']):
                    salesAdjustment[key] = sum(map(lambda i: i['totalNetSales'], value))
                item['salesAdjustment'] = salesAdjustment

                if(item.get('sales') is not None):
                    endingCashTotal = get(item, 'endingCashOnHand.total', 0)
                    difference = (item['sales']['totalNetSales']) - endingCashTotal
                    cashLoss = difference if difference > 0 else 0
                    cashGain = difference * -1 if difference < 0 else 0
                    item['sales']['cashGain'] = cashGain
                    item['sales']['cashLoss'] = cashLoss

                transactionSummary = {}
                transactions = filter(lambda i: i['tenderType'] is not None and i['status'] == 'completed', item['transactions'])
                for key, value in groupby(transactions, lambda i: i['tenderType']):
                    transactionSummary[key] = sum(map(lambda i: i['totalNetSales'], value))
                item['transactionSummary'] = transactionSummary                

                reports.append(item)
            return reports
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