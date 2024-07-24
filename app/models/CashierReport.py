
from bson import ObjectId


class CashierReport:
    _id = None
    _cash_count_keys = ['1000', '500', '200', '100', '50', '20', '10', '5', '1', '0.5', '0.25']
    # _status_keys = ['begin', 'end']

    _cashier_id = None
    _branch_id = None
    _beginning_cash_count = None
    _ending_cash_count = None
    time_in = None
    time_out = None
    cash_sales = None
    date = None
    
    @staticmethod
    def fromDict(data: dict):
        report = CashierReport()
        
        report.id = data.get('_id')
        report.cashier_id = data.get('cashierId')
        report.branch_id = data.get('branchId')
        report.time_in = data.get('timeIn')
        report.time_out = data.get('timeOut')
        report.beginning_cash_count = data.get('beginningCashCount')
        report.ending_cash_count = data.get('endingCashCount')
        report.cash_sales = data.get('cashSales')
        report.date = data.get('date')
        return report
    
    def toDict(self):
        return {
            "id": self.id,
            "timeIn": self.time_in,
            "timeOut": self.time_out,
            "cashierId": self.cashier_id,
            "branchId": self.branch_id,
            "beginningCashCount": self.beginning_cash_count,
            "beginningCashTotal": self._compute_cash_count_total(self.beginning_cash_count),
            "endingCashCount": self.ending_cash_count,
            "endingCashTotal": self._compute_cash_count_total(self.ending_cash_count),
            "cashSales": self.cash_sales,
            "cashGain": self.cash_gain,
            "cashLoss": self.cash_loss,
            "date": self.date
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
    def cashier_id(self): 
        if(self._cashier_id is not None):
            return str(self._cashier_id)

    @cashier_id.setter
    def cashier_id(self, value): 
        if value is not None:
            self._cashier_id = ObjectId(value)
    
    @property
    def branch_id(self): 
        if(self._branch_id is not None):
            return str(self._branch_id)

    @branch_id.setter
    def branch_id(self, value): 
        if value is not None:
            self._branch_id = ObjectId(value)
    
    @property
    def beginning_cash_count(self): 
        return self._beginning_cash_count

    @beginning_cash_count.setter
    def beginning_cash_count(self, value):
        if value is None:
            return None
        
        _new_cash_count = {}
        for cash, count in value.items():
            if cash in self._cash_count_keys and count > 0:
                _new_cash_count[cash] = count
        
        self._beginning_cash_count = _new_cash_count
    
    @property
    def ending_cash_count(self): 
        return self._ending_cash_count

    @ending_cash_count.setter
    def ending_cash_count(self, value):
        if value is None:
            return None
        
        _new_cash_count = {}
        for cash, count in value.items():
            if cash in self._cash_count_keys and count > 0:
                _new_cash_count[cash] = count
        
        self._ending_cash_count = _new_cash_count

    @property
    def cash_gain(self):
        if self.ending_cash_count is None or self.cash_sales is None:
            return None
        
        beginning_total = self._compute_cash_count_total(self.beginning_cash_count)
        ending_total = self._compute_cash_count_total(self.ending_cash_count)
        gain = ending_total - (beginning_total + self.cash_sales)
        if gain < 0: return 0
        return gain
    
    @property
    def cash_loss(self):
        if self.ending_cash_count is None or self.cash_sales is None:
            return None
        
        beginning_total = self._compute_cash_count_total(self.beginning_cash_count)
        ending_total = self._compute_cash_count_total(self.ending_cash_count)
        loss =  ending_total - (beginning_total + self.cash_sales)
        if loss > 0: return 0
        return loss * -1
    
    def _compute_cash_count_total(self, cash_count: dict): 
        if cash_count is None: 
            return 0.0
        
        sum = 0.0
        for cash, count in cash_count.items():
            sum += float(cash) * count
        return sum