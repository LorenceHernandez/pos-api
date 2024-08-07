

from datetime import datetime, timedelta

from pydash import omit
import pytz


def ToStringId(data):
    if(data is None): return
    return { **omit(data, '_id'), "id": str(data["_id"]) }

def getLocalTime():
    return datetime.now() + timedelta(hours=8)

def getTimeZone():
    return pytz.timezone('Asia/Manila')
