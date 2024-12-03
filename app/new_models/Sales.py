
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

from app.utils.utils import getLocalDateStr


class GetGeneratedSales(BaseModel): 
    date: str = Field(default=getLocalDateStr())
    branchId: str
