
from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field, computed_field

from app.new_models.CashCount import CashCount


class TimeInCashierReport(BaseModel):
    branchId: str
    timeOut: Optional[str] = None
    beginningCashOnHand: Optional[CashCount] = None
    cashierId: str = None
    timeIn: str = None
    date: str = None

class TimeOutCashierReport(BaseModel):
    id: str
    endingCashOnHand: CashCount
    timeOut: str


class CashierReport(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    branch: object
    cashier: object
    cashSales: object
    beginningCashOnHand: CashCount = None
    endingCashOnHand: CashCount = None
    timeIn: str
    timeOut: str
    date: str

    # @computed_field
    def difference(self) -> float:
        totalSales = self.cashSales['totalNetSales'] if self.cashSales is not None else 0
        cashOnHand = self.endingCashOnHand['total'] if self.endingCashOnHand is not None else 0
        return cashOnHand - totalSales
    
    @computed_field
    def cashGain(self) -> float:
        diff = self.difference()
        return diff if diff > 0 else 0
    
    @computed_field
    def cashLoss(self) -> float:
        diff = self.difference()
        return diff * -1 if diff < 0 else 0