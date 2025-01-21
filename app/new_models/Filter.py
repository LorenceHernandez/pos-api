


from datetime import date
from typing import Optional
from pydantic import BaseModel


class DateFilter(BaseModel):
    startDate: Optional[date] = None
    endDate: Optional[date] = None

    def transform(self):
        return {
            "date": {
                "$gte": str(self.startDate),
                "$lte": str(self.endDate)
            }
        }