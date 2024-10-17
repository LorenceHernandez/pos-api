
from bson import ObjectId


class JournalEntry:
    _id = None
    date = None
    description = None
    entries = []
    @staticmethod
    def fromDict(data: dict):
        item = JournalEntry()
        if data.get('_id') is not None:
            item._id = str(data.get('_id'))
        item.date = data.get('date')
        item.description = data.get('description')
        item.entries = data.get('entries')
    
        return item
    
    def toDict(self):
        return {
            "_id": self._id,
            "date": self.date,
            "description": self.description,
            "entries": self.entries,
        }
