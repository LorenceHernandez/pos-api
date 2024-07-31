

class CashCount:
    _cash_count = None
    _cash_count_keys = ['1000', '500', '200', '100', '50', '20', '10', '5', '1', '0.5', '0.25']

    def __init__(self, count):
        self.cash_count = count

    @staticmethod
    def fromDict(data: dict):
        if data is None:
            return None
        
        return CashCount(data)

    def toDict(self): 
        return {
            "count": self.cash_count,
            "total": self.total
        } 

    @property
    def total(self):
        return self._compute_cash_count_total(self._cash_count)

    @property
    def cash_count(self): 
        return self._cash_count

    @cash_count.setter
    def cash_count(self, value):
        if value is None:
            return None
        
        _new_count = {}
        for cash, count in value.items():
            if cash in self._cash_count_keys and count > 0:
                _new_count[cash] = count
        
        self._cash_count = _new_count

    def _compute_cash_count_total(self, cash_count: dict): 
        if cash_count is None: 
            return 0.0
        
        sum = 0.0
        for cash, count in cash_count.items():
            sum += float(cash) * count
        return sum
    