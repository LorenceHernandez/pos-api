
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

from app.utils.utils import getLocalDateStr


class GetBranchReportQuery(BaseModel): 
    date: Optional[str] = None
    branchIds: Optional[list[str]] = None
    