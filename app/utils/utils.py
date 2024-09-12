

from datetime import datetime, timedelta

from pydash import omit
import pytz


def ToStringId(data):
    if(data is None): return
    return { **omit(data, '_id'), "id": str(data["_id"]) }

def getTimeZone():
    return pytz.timezone('Asia/Manila')

def getLocalTime():
    return datetime.now(getTimeZone())

def getLocalDateStr():
    return str(getLocalTime().date())

def getLocalTimeStr():
    return getLocalTime().isoformat()
