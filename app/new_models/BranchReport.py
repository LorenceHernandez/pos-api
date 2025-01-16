
from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field, computed_field
from pydash import omit

from app.new_models.CashCount import CashCount
from app.utils.utils import getLocalDateStr, getLocalTimeStr


class RecordBranchReportGeneration(BaseModel):
    branchId: str
    timeOut: Optional[str] = None
    openingFund: Optional[CashCount] = None
    # endingCashCount: Optional[str] = None
    cashierId: str = None
    timeIn: str = Field(default_factory=getLocalTimeStr)
    datetime: str = Field(default_factory=getLocalDateStr)
