


from app.repositories.base import BackupRepository
from app.utils.invoice_setting import generate_invoice_str


class CashierReportRepository(BackupRepository):
    _collection = 'cashier_reports'

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
                                    "total": { "$sum": "$amount" },
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
                item['cashGain'] = None
                item['cashLoss'] = None

                cashSales = item['cashSales']['total'] if item.get('cashSales') is not None else 0
                cashOnHand = item['endingCashOnHand']['total'] if item.get('endingCashOnHand') is not None else 0
                
                difference = cashOnHand - cashSales 
                item['cashGain'] = difference if difference > 0 else 0
                item['cashLoss'] = difference * -1 if difference < 0 else 0

                if(item.get('cashSales') is not None):
                    item['cashSales'] = item['cashSales']['total']
                
                item['invoiceNumberStr'] = generate_invoice_str(
                    item['branch']['code'],
                    ''
                )
                reports.append(item)
            return reports
        except Exception as e:
            raise Exception(f"MongoDB find error: {e}")