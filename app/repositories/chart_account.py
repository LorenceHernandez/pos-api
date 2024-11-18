


from app.repositories.base import Repository


class ChartAccountRepository(Repository):
    _collection = 'chart_of_accounts'


    def find(self, query={}, *args):
        try: 
            data = list(self._db[self._collection].aggregate([
                { '$match': query },
                {
                    '$addFields': {
                        '_id': {'$toString': '$_id' },
                    }
                },
                { '$sort': {"_id":-1} },
                *args,
            ]))
            return data
        except Exception as e:
            raise e