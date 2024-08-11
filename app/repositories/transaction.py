


from app.repositories.base import BackupRepository
from app.utils.invoice_setting import generate_invoice_str
from app.database.config import counters


class TransactionRepository(BackupRepository):
    _collection = 'transactions'

    def find(self, query={}, *args):
        try: 
            data = list(self._db[self._collection].aggregate([
                { '$match': query },
                {
                    '$addFields': {
                        'cashierId': {'$toObjectId': '$cashierId' },
                        'branchId': {'$toObjectId': '$branchId' },
                        'referredBy': {'$toObjectId': '$referredBy' },
                        'requestedBy': {'$toObjectId': '$requestedBy' },
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
                { 
                    '$lookup': {
                        'from': 'branches',
                        'localField': 'branchId',
                        'foreignField': '_id',
                        'as': 'branch'
                    }, 
                },
                { 
                    '$lookup': {
                        'from': 'doctors',
                        'localField': 'referredBy',
                        'foreignField': '_id',
                        'as': 'referredBy'
                    }, 
                },
                { 
                    '$lookup': {
                        'from': 'doctors',
                        'localField': 'requestedBy',
                        'foreignField': '_id',
                        'as': 'requestedBy'
                    }, 
                },
                { "$unwind": "$cashier" },
                { "$unwind": "$branch" },
                { "$unwind": {
                    'path': "$referredBy",
                    'preserveNullAndEmptyArrays': True    
                }},
                { "$unwind": {
                    'path': "$requestedBy",
                    'preserveNullAndEmptyArrays': True    
                }},
                { '$sort': {"_id":-1} },
                *args,
                {
                    '$addFields': {
                        '_id': {'$toString': '$_id' },
                        "cashier._id": { "$toString": "$cashier._id" },
                        "branch._id": { "$toString": "$branch._id" },
                        'referredBy._id': {'$toString': '$referredBy._id' },
                        'requestedBy._id': {'$toString': '$requestedBy._id' },
                    },
                },
                {
                    '$project': {
                        'cashierId': 0,
                        'branchId': 0,
                        'cashier': {
                            'password': 0,
                        }
                    }
                },
            ]))

            transactions = []
            for item in data:
                if item.get('referredBy') is None or item.get('referredBy').get('_id') is None:
                    item['referredBy'] = None
                
                if item.get('requestedBy') is None or item.get('requestedBy').get('_id') is None:
                    item['requestedBy'] = None

                item['invoiceNumberStr'] = generate_invoice_str(
                    item['branch']['code'], 
                    item['invoiceNumber']
                )
                transactions.append(item)
            return transactions
        except Exception as e:
            raise Exception(f"MongoDB find error: {e}")

    def find_active(self, user_id):
        return self.find_one({
          "status": "active",
          "cashierId": user_id,
        })

    def insert_one(self, data):
        data['invoiceNumber'] = self._get_next_sequence('invoice')
        result = super().insert_one(data)

        return self.find_one({ "_id": result.inserted_id })
