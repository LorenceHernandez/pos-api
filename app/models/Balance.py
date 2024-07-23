
from bson import ObjectId


class Balance:
    _id = None
    _item_keys = ['1000', '500', '200', '100', '50', '20', '10', '5', '1', '0.5', '0.25']

    _items = {}
    created_by = None
    created_at = None
    
    @staticmethod
    def fromDict(data: dict):
        balance = Balance()
        
        balance.id = data.get('id')
        balance.items = data.get('items')
        balance.created_by = data.get('createdBy')
        balance.created_at = data.get('createdAt')
        return balance
    
    def toDict(self):
        return {
            "id": self.id,
            "items": self.items,
            "total": self.total,
            "createdBy": self.created_by,
            "createdAt": self.created_at
        }

    @property
    def id(self): 
        if(self._id is not None):
            return str(self._id)

    @id.setter
    def id(self, value): 
        if value is not None:
            self._id = ObjectId(value)
    
    @property
    def items(self): 
        return self._items

    @items.setter
    def items(self, value): 
        if not isinstance(value, dict):
            raise Exception('The items must be dictionary or object')
        
        if len(value) == 0:
            raise Exception('The items must have atleast one item')

        _new_items = {}
        for key, occurence in value.items():
            if key in self._item_keys and occurence > 0:
                _new_items[key] = occurence
        
        self._items = _new_items
        
        

    @property
    def total(self): 
        sum = 0.0
        for key, value in self._items.items():
            sum += float(key) * value
        return sum