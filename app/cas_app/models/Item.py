
from bson import ObjectId


class Item:
    id = None
    name = None
    description = None
    category = None
    uom = None
    reorderLevel = None
    criticalLevel = None
    supplierId = None
    purchasePrice = None
    
    @staticmethod
    def fromDict(data: dict):
        item = Item()
        
        item.id = data.get('id')
        item.name = data['name']
        item.description = data.get('description')
        item.category = data.get('category')
        item.uom = data.get('uom')
        item.reorderLevel = data.get('reorderLevel')
        item.criticalLevel = data.get('criticalLevel')
        item.supplierId = data.get('supplierId')
        item.purchasePrice = data.get('purchasePrice')
    
        return branch
    
    def toDict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "uom": self.uom,
            "reorderLevel": self.reorderLevel,
            "criticalLevel": self.criticalLevel,
            "supplierId": self.supplierId,
            "purchasePrice": self.purchasePrice,
        }

    @property
    def id(self): 
        if(self._id is not None):
            return str(self._id)

    @id.setter
    def id(self, value): 
        if value is not None:
            self._id = ObjectId(value)