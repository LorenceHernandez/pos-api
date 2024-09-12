
import uuid
from pydantic import BaseModel

from app.utils.utils import getLocalDateStr, getLocalTimeStr


class CreateTransaction(BaseModel):
    branchId: str
    cashierId: str
    date: str = getLocalDateStr()
    transactionDate: str = getLocalTimeStr()
    status: str = 'active'
    transactionNo: str = str(uuid.uuid4())
