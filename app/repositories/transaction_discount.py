


from app.repositories.base import Repository
from app.repositories.transaction import TransactionRepository


class TransactionDiscountRepository(Repository):
    _collection = 'transaction_discount'
    _transaction_collection = TransactionRepository()._collection


    def find(self, query={}, *args):
        try: 
            data = list(self._db[self._collection].aggregate([
                { '$match': query },
                {
                    '$addFields': {
                        'transactionId': {'$toObjectId': '$transactionId' },
                        'customerId': {'$toObjectId': '$customerId' },
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
                { 
                    '$lookup': {
                        'from': 'customers',
                        'localField': 'customerId',
                        'foreignField': '_id',
                        'as': 'customer'
                    }, 
                },
                { "$unwind": "$transaction" },
                { "$unwind": "$customer" },
                {
                    '$project': {
                        'transactionId': 0,
                        'customerId': 0,
                    }
                },
                { '$sort': {"_id":-1} },
                *args,
                {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        "transaction._id": { "$toString": "$transaction._id" },
                        "customer._id": { "$toString": "$customer._id" },
                        "customer.name": {
                            "$concat": [
                                "$customer.first_name",
                                " ",
                                "$customer.last_name"
                            ]
                        },
                    }
                }
            ]))
            return data
        except Exception as e:
            raise e