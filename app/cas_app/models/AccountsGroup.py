
from bson import ObjectId


class AccountsGroup:
    _id = None
    name = None
    description = None
    
    @staticmethod
    def fromDict(data: dict):
        item = AccountsGroup()
        if data.get('_id') is not None:
            item._id = str(data.get('_id'))
        item.name = data.get('name')
        item.description = data.get('description')
    
        return item
    
    def toDict(self):
        return {
            "_id": self._id,
            "name": self.name,
            "description": self.description,
        }
