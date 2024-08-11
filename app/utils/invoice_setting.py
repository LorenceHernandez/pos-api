



from datetime import datetime
from app.utils.utils import getTimeZone


def generate_invoice_str(prefix, postfix):
    date = str(datetime.now(getTimeZone()).date())
    new_date_string = date.replace("-", "")
    return f'INV-{prefix}{new_date_string}{postfix}'