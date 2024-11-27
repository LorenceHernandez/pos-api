
from enum import Enum
from typing import Optional, Self
from pydantic import BaseModel, Field, computed_field, field_validator, model_validator, validator

from app.new_models.Package import PackageType

class CustomerDiscountType(str, Enum):
    # MEMBER = "MEMBER"
    # NON_MEMBER = "NON_MEMBER"
    GOVERNMENT_BENEFICIARY = "seniorcitizenpwd"

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
    packageType: Optional[PackageType] = Field(default=PackageType.PACKAGE)
    packageId: Optional[str] = None
    customerDiscountType: Optional[CustomerDiscountType] = None

    @model_validator(mode='after')
    def requirePackageIdWhenPromo(self) -> Self:
        if(self.packageType == PackageType.PROMO and self.packageId is None):
            raise ValueError(f'PackageId should not be none when package type is {PackageType.PROMO}')
        return self