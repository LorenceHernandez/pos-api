
from pydash import omit
from app.repositories.base import Repository


class GoodsReceiptRepository(Repository):
    _collection = 'goods_receipt'

    def find(self, query={}, *args):
        try: 
            data = list(self._db[self._collection].aggregate([
                { '$match': query },
                {
                    '$addFields': {
                        '_id': {'$toString': '$_id' },
                        'purchaseOrderId': {'$toObjectId': '$purchaseOrderId' },
                    }
                },
                { 
                    '$lookup': {
                        'from': 'goods_receipt_items',
                        'localField': '_id',
                        'foreignField': 'receiptId',
                        'as': 'items'
                    }, 
                },
                {
                    '$lookup': {
                        'from': 'purchase_orders',
                        'localField': 'purchaseOrderId',
                        'foreignField': '_id',
                        'as': 'purchaseOrder'
                    }
                },
                { "$unwind": "$purchaseOrder" },
                { '$sort': {"_id":-1} },
                *args,
                {
                    '$addFields': {
                        'purchaseOrderId': {'$toString': '$purchaseOrderId' },
                        'purchaseOrder._id': {'$toString': '$purchaseOrder._id' },
                    }
                },
                {
                    '$project': {
                        'purchaseOrderId': 0
                    }
                }
            ]))
            items = []
            for order in data:
                order['items'] = list(map(lambda i: { **omit(i, '_id') }, order['items']))
                items.append(order)
            return items
        except Exception as e:
            raise Exception(f"MongoDB find error: {e}")

    def insert_one(self, data):
        result = super().insert_one(data)
        return self.find_one({ "_id": result.inserted_id })
    
    def update_one(self, query, data, *args, **kwargs):
        result = super().update_one(query, data, *args, **kwargs)
        return self.find_one({ "_id": result['_id'] })