
from bson import ObjectId


class ChartAccount:
    _id = None
    accountNumber = None
    accountName = None
    accountType = None
    accountGroup = None
    description = None
    @staticmethod
    def fromDict(data: dict):
        item = ChartAccount()
        if data.get('_id') is not None:
            item._id = str(data.get('_id'))
        item.accountName = data.get('accountName')
        item.accountType = data.get('accountType')
        item.description = data.get('description')
        item.accountNumber = data.get('accountNumber')
        item.accountGroup = data.get('accountGroup')
    
        return item
    
    def toDict(self):
        return {
            "_id": self._id,
            "accountName": self.accountName,
            "accountType": self.accountType,
            "description": self.description,
            "accountNumber": self.accountNumber,
            "accountGroup": self.accountGroup,
        }
