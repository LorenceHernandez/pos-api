

from typing import Optional
from pydantic import BaseModel, ValidationError, field_validator, validator

_cash_keys = ['1000', '500', '200', '100', '50', '20', '10', '5', '1', '0.5', '0.25']
class CashCount(BaseModel):
    count: object
    total: Optional[float] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_count(kwargs['count'])

    def set_count(self, value):
        if value is None:
            return None
        
        _new_count = {}
        for cash, count in value.items():
            if cash in _cash_keys and count > 0:
                _new_count[cash] = count
        
        self.count = _new_count
        self.total = self._compute_cash_count_total(self.count)

    def _compute_cash_count_total(self, cash_count: dict | None): 
        if cash_count is None: 
            return 0.0
        
        sum = 0.0
        for cash, count in cash_count.items():
            sum += float(cash) * count
        return sum
    