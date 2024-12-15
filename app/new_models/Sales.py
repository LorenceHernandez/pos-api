
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

from app.utils.utils import getLocalDateStr


class GetBranchSalesQuery(BaseModel): 
    date: Optional[str] = None
    branchId: str
