

from enum import IntEnum


class DateFilter(IntEnum):
    ALL = 0    
    TODAY = 1
    YESTERDAY = 2
    THIS_WEEK = 3
    THIS_MONTH = 4
    THIS_YEAR = 5
    LAST_WEEK = 6
    LAST_MONTH = 7
    LAST_YEAR = 8
    CUSTOM_FILTER = 9
    CUSTOM_DATE = 10
