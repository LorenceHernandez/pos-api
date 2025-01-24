


from itertools import groupby

from pydash import get
from app.new_models.Filter import DateRangeFilter
from app.new_models.Transaction import TransactionStatus
from app.repositories.base import Repository
from app.repositories.transaction import TransactionRepository
from app.repositories.transaction_item import TransactionItemRepository


class CategoryRepository(Repository):
    _collection = 'product_categories'
    _transaction_item_collection = TransactionItemRepository()._collection
    _transaction_collection = TransactionRepository()._collection


    def find_transactions(self, query={}, *args):
        try: 
            data = list(self._db[self._collection].aggregate([
                {
                    "$addFields": {
                        "_id": {"$toString": "$_id"}
                    }
                },
                {
                    "$lookup": {
                        "from": self._transaction_item_collection,
                        "let": {
                            "categoryId": "$_id",
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            { "$eq": ["$categoryId", "$$categoryId"] },
                                        ]
                                    }
                                }
                            },
                            { 
                                '$lookup': {
                                    'from': self._transaction_collection,
                                    "let": {
                                        "transactionId": "$transactionId",
                                    },
                                    "pipeline": [
                                        { '$match': query },
                                        {
                                            "$addFields": {
                                                "_id": {"$toString": "$_id"}
                                            }
                                        },
                                        {
                                            "$match": {
                                                "$expr": {
                                                    "$and": [
                                                        { "$eq": ["$_id", "$$transactionId"] },
                                                    ]
                                                }
                                            }
                                        },
                                    ],
                                    'as': 'transaction'
                                }, 
                            },
                            { "$unwind": {
                                'path': '$transaction',
                                'preserveNullAndEmptyArrays': True    
                            }},
                        ],
                        "as": "transactionItems"
                    }
                },
                {
                    '$project': {
                        'transactionItems._id': 0,
                        # 'transactionItems.transactionId': 0,
                    }
                },
                # { '$sort': {"_id":-1} },
                *args,
            ]))

            categories = []
            for item in data:
                transactionSummary = {}
                transactionItems = list(filter(lambda i: get(i, 'transaction.tender.type') is not None and get(i, 'transaction.status') == 'completed', item['transactionItems']))
                for key, value in groupby(transactionItems, lambda i: get(i, 'transaction.tender.type')):
                    total = sum(map(lambda i: get(i, 'price'), value))
                    total += transactionSummary.get(key, 0)
                    transactionSummary[key] = total

                item['transactionSummary'] = transactionSummary
                item['transactionSummary']['count'] = len(transactionItems)
                item['transactionSummary']['total'] = sum(map(lambda i: get(i, 'price'), transactionItems))
                item['totalNetSales'] = sum(map(lambda i: get(i, 'price'), transactionItems))

                categories.append(item)
            return categories
        except:
            raise

    def compare_category_sales(self, query, date1Filter: DateRangeFilter, date2Filter: DateRangeFilter, *args):
        try: 
            data = list(self._db[self._collection].aggregate([
                {
                    "$addFields": {
                        "_id": {"$toString": "$_id"}
                    }
                },
                *self._create_transaction_items_query("transactionItems1", { **query, **date1Filter.transform() }),
                *self._create_transaction_items_query("transactionItems2", { **query, **date2Filter.transform() }),
                *args,
            ]))

            categories = []
            for item in data:
                
                item['transactionSummary1'] = self._get_transaction_summary(item['transactionItems1'])
                item['transactionSummary2'] = self._get_transaction_summary(item['transactionItems2'])
                item['transactionSummaryDiff'] = self._calculate_percent_diff(item['transactionSummary1']['total'], item['transactionSummary2']['total'])
                # item['transactionSummaryDiff']['diff'] = item['transactionSummary1']['count'] + item['transactionSummary2']['count']

                categories.append(item)
            
 
            [count1, total1] = self._compute_overall_summary('transactionSummary1', categories)
            [count2, total2] = self._compute_overall_summary('transactionSummary2', categories)

            return {
                "reports": categories,
                "overall": {
                    "transactionSummary1": {
                        "count": count1,
                        "total": total1
                    },
                    "transactionSummary2": {
                        "count": count2,
                        "total": total2
                    },
                    "transactionSummaryDiff": self._calculate_percent_diff(total1, total2)
                }
            }
        except:
            raise

    
    def _get_transaction_summary(self, transactionItems):
        transactionSummary = {}
        transactionItems = list(filter(lambda i: get(i, 'transaction.tender.amount') is not None and get(i, 'transaction.status') == 'completed', transactionItems))
        transactionSummary['count'] = len(transactionItems)
        transactionSummary['total'] = sum(map(lambda i: get(i, 'price'), transactionItems))
        return transactionSummary

    def _compute_overall_summary(self, key, categories): 
        count = sum(map(lambda i: i[key]['count'], categories))
        total = sum(map(lambda i: i[key]['total'], categories))
        return [count, total]

    def _calculate_percent_diff(self, startValue, finalValue):
        if(startValue == 0 or startValue == None): 
            return finalValue * 100
        return ((finalValue - startValue) / startValue) * 100

    def _create_transaction_items_query(self, name, query):
        return [
            {
                "$lookup": {
                    "from": self._transaction_item_collection,
                    "let": {
                        "categoryId": "$_id",
                    },
                    "pipeline": [
                        # { '$match': query },
                        {
                            "$addFields": {
                                "_id": {"$toString": "$_id"}
                            }
                        },
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        { "$eq": ["$categoryId", "$$categoryId"] },
                                    ]
                                }
                            }
                        },
                        { 
                            '$lookup': {
                                'from': self._transaction_collection,
                                "let": {
                                    "transactionId": "$transactionId",
                                },
                                "pipeline": [
                                    { '$match': query },
                                    {
                                        "$addFields": {
                                            "_id": {"$toString": "$_id"}
                                        }
                                    },
                                    {
                                        "$match": {
                                            "$expr": {
                                                "$and": [
                                                    { "$eq": ["$_id", "$$transactionId"] },
                                                ]
                                            }
                                        }
                                    },
                                ],
                                'as': 'transaction'
                            }, 
                        },
                        { "$unwind": {
                            'path': '$transaction',
                            'preserveNullAndEmptyArrays': True    
                        }},
                    ],
                    "as": name
                }
            },
        ]