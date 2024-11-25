
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PackageType(str, Enum):
    PACKAGE = "PACKAGE"
    PROMO = "PROMO"


class Package(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: str = None
    type: PackageType = PackageType.PACKAGE
    forMemberType: str = None
