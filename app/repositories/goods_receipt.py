
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
                    }
                },
                { 
                    '$lookup': {
                        'from': 'goods_receipt_items',
                        'localField': 'purchaseOrderId',
                        'foreignField': 'purchaseOrderId',
                        'as': 'items'
                    }, 
                },
                { '$sort': {"_id":-1} },
                *args,
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
