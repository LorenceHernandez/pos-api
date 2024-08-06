
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel

from app.new_models.CashCount import CashCount


class TimeInCashierReport(BaseModel):
    branchId: str
    beginningCashOnHand: Optional[CashCount] = None
    endingCashOnHand: Optional[CashCount] = None
    cashierId: Optional[str] = None
    timeIn: Optional[str] = None
    timeOut: Optional[str] = None
    date: Optional[str] = None

class TimeOutCashierReport(BaseModel):
    endingCashOnHand: CashCount
    timeOut: Optional[str] = None
