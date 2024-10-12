
from bson import ObjectId


class Entry:
    invoiceNumber = None
    contactName = None
    total = None
    description = None
    account = None

    def __init__(self, invoiceNumber, contactName, total, description, account):
        self.invoiceNumber = invoiceNumber
        self.contactName = contactName
        self.total = total
        self.description = description
        self.account = account

    @staticmethod
    def fromDict(data: dict):
        if data is None:
            return None
        
        return Entry( 
            data.get('invoiceNumber'),
            data.get('contactName'),
            data.get('total'),
            data.get('description'),
            data.get('account')
        )


    def toDict(self): 
        return {
            "invoiceNumber": self.invoiceNumber,
            "contactName": self.contactName,
            "total": self.total,
            "description": self.description,
            "account": self.account,
        } 
class Receipt:
    _id = None
    paymentDate = None
    paymentMethod = None
    totalAmountPaid = None
    notes = None
    isAccountMode = None
    entries = None
    @staticmethod
    def fromDict(data: dict):
        item = Receipt()
        if data.get('_id') is not None:
            item._id = str(data.get('_id'))
        item.paymentDate = data.get('paymentDate')
        item.paymentMethod = data.get('paymentMethod')
        item.totalAmountPaid = data.get('totalAmountPaid')
        item.notes = data.get('notes')
        item.isAccountMode = data.get('isAccountMode')
        e = []
        for entry in data.get('entries'):
            e.append(Entry.fromDict(entry))
        item.entries = e
        return item
        
    def toDict(self):
        dict = {
            "_id": self._id,
            "paymentDate": self.paymentDate,
            "paymentMethod": self.paymentMethod,
            "totalAmountPaid": self.totalAmountPaid,
            "notes": self.notes,
            "isAccountMode": self.isAccountMode,
           
        }
        e = []
        for entry in self.entries:
            e.append(entry.toDict())
        dict['entries'] = e
        return dict
