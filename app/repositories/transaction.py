


from bson import ObjectId
from app.new_models.Transaction import CreateTransaction, Transaction
from app.repositories.base import BackupRepository
from app.utils.invoice_setting import generate_invoice_str
from app.database.config import counters
from app.utils.utils import getLocalDateStr, getLocalTimeStr


class TransactionRepository(BackupRepository):
    _collection = 'new_transactions'

    def find(self, query={}, *args):
        try: 
            data = list(self._db[self._collection].aggregate([
                { '$match': query },
                {
                    '$addFields': {
                        'cashierId': {'$toObjectId': '$cashierId' },
                        'customerId': {'$toObjectId': '$customerId' },
                        'branchId': {'$toObjectId': '$branchId' },
                        'referredById': {'$toObjectId': '$referredById' },
                        'requestedById': {'$toObjectId': '$requestedById' },
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
                        'from': 'customers',
                        'localField': 'customerId',
                        'foreignField': '_id',
                        'as': 'customer'
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
                        'localField': 'referredById',
                        'foreignField': '_id',
                        'as': 'referredBy'
                    }, 
                },
                { 
                    '$lookup': {
                        'from': 'doctors',
                        'localField': 'requestedById',
                        'foreignField': '_id',
                        'as': 'requestedBy'
                    }, 
                },
                { "$unwind": "$cashier" },
                { "$unwind": "$customer" },
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
                        "customer._id": { "$toString": "$customer._id" },
                        "branch._id": { "$toString": "$branch._id" },
                        'referredBy._id': {'$toString': '$referredBy._id' },
                        'requestedBy._id': {'$toString': '$requestedBy._id' },
                    },
                },
                {
                    '$project': {
                        'cashierId': 0,
                        'branchId': 0,
                        'referredById': 0,
                        'requestedById': 0,
                        'customerId': 0,
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
                transactions.append(Transaction(**item).model_dump(by_alias=True))
            return transactions
        except:
            raise
    def find_active(self, user_id):
        
        return self.find_one({
          "status": "active",
          "cashierId": user_id,
           "date": getLocalDateStr(),
        })

    def insert_one(self, data: CreateTransaction):
        data.invoiceNumber = self._get_next_sequence('invoice')
        data = data.model_dump(by_alias=True)
        result = super().insert_one(data)
        return self.find_one({ '_id': ObjectId(result.inserted_id) })