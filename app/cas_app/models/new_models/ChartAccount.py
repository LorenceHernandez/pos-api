from enum import Enum

from pydantic import BaseModel


class AccountType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EXPENSE = "EXPENSE"
    EQUITY = "EQUITY"
   

class EditChartAccount(BaseModel):
    accountNumber = None
    accountName: str = None
    accountType: AccountType = None
    accountGroup = None
    description: str = None
    