
from bson import ObjectId


class Payment:
    _id = None
    paymentDate = None
    paymentMethod = None
    notes = None
    entries = []
    @staticmethod
    def fromDict(data: dict):
        item = Payment()
        if data.get('_id') is not None:
            item._id = str(data.get('_id'))
        item.paymentDate = data.get('paymentDate')
        item.paymentMethod = data.get('paymentMethod')
        item.notes = data.get('notes')
        item.entries = data.get('entries')
    
        return item
    
    def toDict(self):
        return {
            "_id": self._id,
            "paymentDate": self.paymentDate,
            "paymentMethod": self.paymentMethod,
            "notes": self.notes,
            "entries": self.entries,
        }
