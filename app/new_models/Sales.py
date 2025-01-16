
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

from app.utils.utils import getLocalDateStr, getLocalTimeStr


class GetBranchReportQuery(BaseModel): 
    date: Optional[str] = None
    branchIds: Optional[list[str]] = None
    
class GenerateBranchReport(BaseModel): 
    date: str = Field(default_factory=getLocalDateStr)
    cashierId: str
    branchId: str