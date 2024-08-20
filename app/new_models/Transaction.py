
from datetime import datetime
from typing import Optional
import uuid
from bson import ObjectId
from pydantic import BaseModel

from app.new_models.CashCount import CashCount
from app.utils.utils import getTimeZone


class CreateTransaction(BaseModel):
    branchId: str
    cashierId: str
    # date: Optional[str]
    # date: Optional[str] = str(datetime.now(getTimeZone()).date())
    # transactionDate: Optional[str]
    # transactionDate: Optional[str] = datetime.now(getTimeZone()).isoformat()
    status: Optional[str] = 'active'
    transactionNo: Optional[str] = str(uuid.uuid4())
