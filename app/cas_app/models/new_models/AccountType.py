from enum import Enum

from pydantic import BaseModel


class EditAccountType(BaseModel):
    name: str = None
    description = None