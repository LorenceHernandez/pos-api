
from bson import ObjectId


class AccountsType:
    _id = None
    name = None
    description = None
    accountGroup = None
    @staticmethod
    def fromDict(data: dict):
        item = AccountsType()
        if data.get('_id') is not None:
            item._id = str(data.get('_id'))
        item.name = data.get('name')
        item.description = data.get('description')
        item.accountGroup = data.get('accountGroup')
    
        return item
    
    def toDict(self):
        return {
            "_id": self._id,
            "name": self.name,
            "description": self.description,
            "accountGroup": self.accountGroup,
        }
