


from datetime import date as dateclass, datetime, timedelta
from typing import Optional
from pydantic import BaseModel, computed_field

from app.new_models.Discount import MemberType


class DateFilter(BaseModel):
    date: Optional[dateclass] = None

    def transform(self):
        if(not self.date):
            return {}

        return { "date": str(self.date) }
class DateRangeFilter(BaseModel):
    startDate: Optional[dateclass] = None
    endDate: Optional[dateclass] = None

    def transform(self):
        if(not self.startDate or not self.endDate):
            return {}

        return {
            "date": {
                "$gte": str(self.startDate),
                "$lte": str(self.endDate)
            }
        }

class BranchFilter(BaseModel):
    branchIds: Optional[list[str]] = None

    def __init__(self, **data):
        if "branchIds" in data:
            data["branchIds"] = data.get("branchIds", "").split(',')
        super().__init__(**data)

    def transform(self):
        if(not self.branchIds): 
            return {}
        return { "branchId": { "$in": self.branchIds } }

class ReportFilter(BranchFilter):
    dateRangeFilter: Optional[DateRangeFilter] = None

    def transform(self):
        return {
            **super().transform(),
            **self.dateRangeFilter.transform() 
        }

class DiscountsReportFilter(ReportFilter):
    memberType: MemberType

    def transform(self):
        return {
            **super().transform(),
            "memberType": self.memberType.value
        }

class ComparativeReportFilter(ReportFilter):
    dateRangeFilter: DateRangeFilter

    @property
    def date1Filter(self):
        startDate = self.dateRangeFilter.startDate.replace(day=1)
        endDate = self.getLastDateOfMonth(startDate)
        return DateRangeFilter(startDate=startDate, endDate=endDate)
    
    @property
    def date2Filter(self):
        startDate = self.dateRangeFilter.endDate.replace(day=1)
        endDate = self.getLastDateOfMonth(startDate)
        return DateRangeFilter(startDate=startDate, endDate=endDate)

    def getLastDateOfMonth(self, startDate: dateclass):
        nextMonthDate = startDate + timedelta(days=32)
        endDate = nextMonthDate - timedelta(days=nextMonthDate.day)
        return endDate