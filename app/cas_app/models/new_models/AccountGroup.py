from enum import Enum

from pydantic import BaseModel


class EditAccountGroup(BaseModel):
    name: str = None
    description = None
    accountType: str = None