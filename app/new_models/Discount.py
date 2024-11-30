
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, computed_field

from app.new_models.Package import PackageType

class CustomerDiscountType(str, Enum):
    MEMBER = "MEMBER"
    NON_MEMBER = "NON_MEMBER"
    GOVERNMENT_BENEFICIARY = "GOVERNMENT_BENEFICIARY"

class DiscountType(str, Enum):
    FIXED = "fixed"
    PERCENTAGE = "percentage"

class Discount(BaseModel):
    id: Optional[str] = Field(alias="_id")
    type: DiscountType
    name: str
    value: float = Field(gt=1)

    def calculateTotalDiscount(self, total):
        if(self.type == DiscountType.FIXED):
            return self.value
        
        return total * (self.value / 100)

#TODO CUSTOM VALIDATION - IF PACKAGETYPE IS PROMO PACKAGE ID SHOULD BE REQUIRED, VISEVERSA
class TransactionDiscount(Discount):
    packageType: PackageType = Field(default=PackageType.PACKAGE)
    packageId: str = None
    customerDiscountType: CustomerDiscountType = None
