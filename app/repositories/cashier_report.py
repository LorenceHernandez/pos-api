


from app.filters.date_filter import DateFilter, compare_date_filter
from app.new_models.CashierReport import CashierReport
from app.repositories.base import BackupRepository


class CashierReportRepository(BackupRepository):
    _collection = 'cashier_reports'

    def find(self, query={}, *args):
        try:
            data = list(self._db[self._collection].aggregate([
                { '$match': query },
                { 
                    '$lookup': {
                        'from': 'transactions',
                        'localField': 'cashierId',
                        'foreignField': 'cashierId',
                        'as': 'transactions'
                    }, 
                },
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
                        "from": "sales",
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
                                                { "$eq": ["$branch", "$$branchId"] },
                                                { "$eq": ["$cashierId", "$$cashierId"] },
                                                { "$eq": ["$date", "$$date"] }
                                            ]
                                        }
                                }
                            },
                            {
                                "$group": {
                                    "_id": "$cashierId",
                                    "totalGrossSales": { "$sum": "$paymentDetails.subTotal" },
                                    "totalNetSales": { "$sum": "$paymentDetails.paymentDue" },
                                    "totalDiscount": { "$sum": { "$subtract": ["$paymentDetails.subTotal", "$paymentDetails.paymentDue"] } },
                                    "invoiceStartNumber": { '$min': "$invoiceNumber" },
                                    "invoiceEndNumber": { '$max': "$invoiceNumber" }
                                }
                            },
                        ],
                        "as": "sales"
                    }
                },
                {
                    "$addFields": {
                        "cashSales": { 
                            "$cond": [
                                { "$gt": [ { "$size": "$sales" }, 0 ] },
                                { "$arrayElemAt": ["$sales", 0] },
                                None
                            ]
                        },
                        "invoiceStartNumber": "$cashSales.invoiceStartNumber",
                        "invoiceEndNumber": "$cashSales.invoiceEndNumber",
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
                    "$addFields": {
                        "invoiceStartNumber": "$cashSales.invoiceStartNumber",
                        "invoiceEndNumber": "$cashSales.invoiceEndNumber",
                    }
                },
                {
                    '$project': {
                        'cashierId': 0,
                        'branchId': 0,
                        'sales': 0,
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
                report = CashierReport.model_construct(**item)
                reports.append(report.model_dump(exclude={'transactions'}))
            return reports
        except Exception as e:
            raise Exception(f"MongoDB find error: {e}")
        
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