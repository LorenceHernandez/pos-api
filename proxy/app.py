import datetime
from itertools import groupby
import numbers
import os
import platform
import time
from flask import Flask, request, Response
from flask_cors import CORS
from pydash import get, start_case, upper_case
import pytz
import requests
import socket
from pydash.strings import to_lower
import serial
from escpos.printer import Network
from serial.tools import list_ports

MAX_CHAR_PER_ROW = 40
app = Flask(__name__)

from dotenv import load_dotenv

load_dotenv('../.env')
# Replace with your local and cloud server URLs
LOCAL_SERVER_URL = os.getenv('LOCAL_SERVER_URL')
CLOUD_SERVER_URL = os.getenv('CLOUD_SERVER_URL')

print('LOCAL_SERVER_URL', LOCAL_SERVER_URL)
print('CLOUD_SERVER_URL', CLOUD_SERVER_URL)


def list_serial_ports():
  """Lists available serial ports on the system."""
  ports = list_ports.comports()
  if ports:
    for port in ports:
      print(f"Port: {port.device}")
      print(f"  Description: {port.description}")
      print(f"  Manufacturer: {port.manufacturer}")
      print("-" * 20)
  else:
    print("No serial ports found.")

list_serial_ports()

def get_local_time():
    return datetime.datetime.now(pytz.timezone('Asia/Manila'))

def check_os_windows():
  system = platform.system()
  return system == 'Windows'

def get_display_device():
    if(check_os_windows()):
        return serial.Serial(port='COM3', baudrate=9600)
    else:
        return serial.Serial(port='/dev/ttyACM1', baudrate=9600)
   
def display_welcome():
    vfd = None
    try:
        vfd = get_display_device()
    except:
        pass
    
    if(vfd is None):
        return

    vfd.write("\x0C".encode())
    vfd.write('WELCOME TO'.center(20).encode())
    vfd.write("MMG-ALBAY!!".center(20).encode())

display_welcome()

def is_internet_connected():
    return False
    # try:
    #     socket.create_connection(("www.google.com", 80))
    #     return True
    # except OSError:
    #     return False

cors = CORS(app, origins=["*", "*"])
@app.before_request
def hook():
    if request.method.lower() == 'options':
      return Response()

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    connected = is_internet_connected()

    print('Connection: ', connected)
    path = request.full_path

    if connected:
        target_url = CLOUD_SERVER_URL + path
    else:
        target_url = LOCAL_SERVER_URL + path
    # target_url = LOCAL_SERVER_URL + path
    # print('Target URL: ', target_url)

    print('Request: ', target_url)

    try:
        response = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for (key, value) in request.headers.items() if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        resp = Response(response.content, response.status_code)
        for key, value in response.headers.items():
            if key not in excluded_headers:
                resp.headers[key] = value
        return resp
    except requests.exceptions.RequestException as e:
        return f"Error proxying request: {e}", 500
    
@app.route('/check-connection', methods=['GET'])
def check_connection():
    connection = is_internet_connected()
    return { 'is_connected': connection }

def row(p, label: str, value):
    if(isinstance(value, numbers.Number) and not isinstance(value, bool)):
        value = "{:.2f}".format(value)

    if(not isinstance(value, str)):
        value = str(value)

    p.textln(label + value.rjust(MAX_CHAR_PER_ROW - len(label)))

def line(p):
    p.textln('-' * MAX_CHAR_PER_ROW)

@app.post('/print')
def print_receipt():
    request_data = request.get_json()
    p = None
    try:
        p = Network("192.168.192.168")

    except Exception as e:
        return {
            'message': 'Unable to print the request',
            'error': repr(e)
        }, 500
    
    # p = escpos.printer(Usb(0x04b8, 0x0202))  # For USB connection
    # p = escpos.Network("192.168.1.100")  # For network connection
    
    print(f'PRINTING... {repr(p)}')

    transaction = request_data['transaction']
    branch = transaction['branch']
    cashier = transaction['cashier']
    dvote = request_data['dvoteDetails'][0]
    customer = transaction['customer']
    reprint = request_data.get('reprint') 
    reprintLabel = '(RE-PRINT)' if reprint else ''

    companyCopy = request_data.get('companyCopy')
    companyLabel = '(COMPANY\'S COPY)' if companyCopy else ''

    dt = datetime.datetime.fromisoformat(transaction['transactionDate'])
    dateNow = get_local_time()

    try:
        p.set(align='center', bold=True)
        p.text(f'MMG-ALBAY {companyLabel}\n\n')
        p.set(align='center', bold=False)
        p.text('Operated By:\n')
        p.set(align='center', bold=True)
        p.text('MEDICAL MISSION GROUP MULTIPURPOSE COOPERATIVE-ALBAY\n')
        p.set(align='center', bold=False)
        p.text('NON-VAT REG TIN ' + branch['tin'] + '\n')
        p.text(upper_case(branch['streetAddress']) + '\n\n')

        p.set(align='center', bold=True)
        p.text(f'INVOICE {reprintLabel}\n')
        p.set(align='left', bold=False)
        # p.textln('-' * MAX_CHAR_PER_ROW)
        line(p)

        if(reprint):
            row(p, "Reprint: ", dateNow.strftime("%Y-%m-%d %I:%M%p"))
            # text(p, "Reprint: ":<9}{dateNow.strftime("%Y-%m-%d %I:%M%p"):>31}')

        
        row(p, "MIN: ", "---")
        row(p, "SN: ", "---")
        row(p, "Date & Time: ", dt.strftime("%Y-%m-%d %I:%M%p"))
        row(p, "Cashier: ", start_case(cashier["first_name"] + " " + cashier["last_name"]))
        row(p, "Invoice #: ", str(transaction["invoiceNumber"]).zfill(6))

        line(p)
        p.set(align='center', bold=True)
        p.text('SOLD TO\n')
        p.set(align='left', bold=False)

        row(p, "Name: ", start_case(to_lower(customer["name"])))
        row(p, "Address: ", start_case(to_lower(customer["address"])))
        row(p, "TIN: ", customer.get("tin_number") or "---")

        if(companyCopy):
            row(p, "Age: ", customer["age"])
            row(p, "Birth Date: ", str(customer["birthDate"]).split("T")[0])
        else:
            row(p, "Age: ", "---")
            row(p, "Birth Date: ", "---")
            
        row(p, "Requested By: ", transaction.get("requestedByName", "---"))
        # text(p, 'SC/PWD/Other ID No.: ':<21}{customer.get('customerTypeId') or '---':>19}')

        line(p)
        p.set(align='center', bold=True)
        row(p, "ITEM ", "|QTY|PRICE|AMOUNT")
        p.set(align='left', bold=False)
        line(p)

        for key, items in groupby(transaction['transactionItems'], lambda i: i.get('package')):
            package = key

            indented = ''
            if(package is not None):
                indented = '  '
                p.text(f'> {package["name"]} \n')

            for item in list(items):
                # is_labtest = item['source'] == 'labTest'

                # if(is_labtest):
                #     amount = item['amount'] if transaction['status'] == 'Completed' else item['amount'] * -1
                #     p.textln(str(item["name"][:17]).ljust(18) + f'({item["qty"]})'.center(7) + str(amount).center(7) + str(amount).rjust(8))
                #     continue
                
                
                amount = item['price'] if transaction['status'] == 'completed' else item['price'] * -1
                p.textln(str(indented + item["name"][:22]).ljust(23) + f'({item["quantity"]})'.center(5) + str(amount).center(6) + str(amount).rjust(6))
            
            if(package is not None):
                discounts = list(filter(lambda i: i.get('packageId') == package['_id'] and i['memberType'] is None, transaction['discounts']))
                if(len(discounts) > 0):
                    discount = discounts[0]
                    totalDiscount = discount['value'] if discount['type'] == 'fixed' else (transaction['totalGrossSales'] * (discount['value'] / 100))
                    row(p, f'  - Less: {discount["name"]}', f'- {"{:.2f}".format(totalDiscount)}')
                    # p.textln(f'  - Less: {discount["name"]}'[:30].ljust(31) + f'- {"{:.2f}".format(totalDiscount)}'.rjust(9))

                # p.set(bold=False)
                # for test in item['labTest']:
                #     indented = '  '
                #     amount = test['amount'] if transaction['status'] == 'Completed' else test['amount'] * -1
                #     p.textln(indented + start_case(test["name"][:17]).ljust(18) + f'({test["qty"]})'.center(7) + str(amount).center(7) + str(amount).rjust(8))
                #     # text(p, (indented + start_case(test["name"]))[:17]:<18}{f'({test["qty"]})':^7}{amount:^7}{amount:>8}')

                # discount = item['discount']
                # if(transaction['status'] == 'Completed' and item['packageForMemberType'] != 'seniorcitizenpwd' and discount != None):
                #     totalDiscount = discount['value'] if discount['type'] == 'fixed' else (transaction['subTotal'] * (discount['value'] / 100))
                #     p.textln(f'  - Less: {discount["name"]}'.ljust(31) + f'- {totalDiscount}'.rjust(9))
                    
                
                # if(service['source'] == 'promo'):
                #     serviceDiscount = service.get('discount')
                #     serviceDiscountAmount = service.get('totalPackagePrice', 0) - service.get('totalDiscountedPrice', 0)
                #     text(p, (indented + 'Discount: ' + serviceDiscount['name'])[:31]:<31}{'- ' + str(serviceDiscountAmount):>9}')



        line(p)
        if (transaction['status'] == 'cancelled'):
            p.set(align='center', bold=True)
            p.text('*** CANCELLED TRANSACTION ***\n\n')
            p.set(align='left', bold=False)

            row(p, "Reason: ", transaction.get("reasonCancelled") or "---")
            p.set(align='left', bold=True)
            row(p, "Total Sales: ", transaction["totalSalesWithoutMemberDiscount"])
            p.set(bold=False)

            row(p, "Less: SC/PWD/NAAC/MOV/SP ", f'({transaction["totalMemberDiscount"]})')
            row(p, "Less: Withholding Tax ", "(0)")
            
            p.set(bold=True)
            row(p, "TOTAL AMOUNT DUE: ", transaction["totalNetSales"])
            
            p.set(bold=False)
            row(p, "Tender Amount: ", transaction["tenderAmount"])
            row(p, "Tender Type: ", upper_case(transaction["tenderType"]))
            row(p, "Change: ", transaction["change"])

        elif(transaction['status'] == 'refunded'):
            # text(p, 'Number of Items: ':<20}{request_data['totalQuantity']:>20}')
            p.set(align='center', bold=True)
            p.text('*** REFUNDED TRANSACTION ***\n\n')
            p.set(align='left', bold=False)
            row(p, "Refunded Amount: ", transaction["totalNetSales"])
            row(p, "Previous Invoice Number: ", str(transaction["invoiceNumber"]).zfill(6))
            row(p, "Reason: ", transaction.get("reason") or "---")
        else:
            p.set(align='left', bold=True)
            row(p, "Total Sales: ", transaction["totalSalesWithoutMemberDiscount"])
            p.set(bold=False)

            row(p, "Less: SC/PWD/NAAC/MOV/SP ", f'({transaction["totalMemberDiscount"]})')
            row(p, "Less: Withholding Tax ", "(0)")
            
            p.set(bold=True)
            row(p, "TOTAL AMOUNT DUE: ", transaction["totalNetSales"])
            
            p.set(bold=False)
            row(p, "Tender Amount: ", transaction["tenderAmount"])
            row(p, "Tender Type: ", upper_case(transaction["tenderType"]))
            row(p, "Change: ", transaction["change"])


        line(p)

        p.set(align='center', bold=True)
        p.text('*THIS DOCUMENT IS NOT VALID FOR CLAIM OF INPUT TAX*\n')
        line(p)
        p.textln()
        p.set(align='left', bold=False)

        customerTypeId = customer.get('customer_type_id') or ('_' * 10) 

        row(p, "ID (SC/PWD/NAAC/MOV/SP): ", f'{customerTypeId}\n')
        row(p, "Signature: ", f'{("_" * 10)}\n')

        p.set(align="center", bold=True)
        p.text('SUPPLIER\n')
        p.text(dvote['name'].upper() + '\n')
        p.set(align="center", bold=False)
        p.text('Address: ' + dvote['address'] + '\n')
        p.text('Vat Reg. TIN: ' + dvote['tin'] + '\n')
        p.text('Accred No: ' + dvote['accredNo'] + '\n')
        p.text('Date Issued: ' + dvote['dateIssued'] + '\n')
        p.text('Valid Until: ' + '---' + '\n')
        p.text('PTU No: ' + dvote.get('PTUno', '---') + '\n\n\n\n')
        p.cut()
        p.close()
    except Exception as e: 
        p.text('\n\n')
        p.cut()
        p.close()
        return {
            'message': 'Unable to print the request',
            'error': repr(e)
        }, 500
    return { 'message': 'Printed successfully' }, 200

def compute_sum(discounts, key, fn):
    _sum = 0
    values = discounts.get(key)

    if(values is None):
        return 0

    for item in discounts.get(key):
        _sum += float(fn(item))
    return _sum

@app.post('/print-report')
def print_report():
    data = request.get_json()
    p = None
    try:
        p = Network("192.168.192.168")
        if p is None:
            raise
    except Exception as e:
        return {
            'message': 'Unable to print the request',
            'error': repr(e)
        }, 500

    # p = escpos.printer(Usb(0x04b8, 0x0202))  # For USB connection
    # p = escpos.Network("192.168.1.100")  # For network connection
    
    print('printing...')

    branch = data['branch']
    cashier = data['cashier']
    dvote = data['dvoteDetails'][0]
    # title = data['title']
    type = data['type']

    timeInDate = None
    timeOutDate = None
    if(type == 'X_REPORT'):
        timeInDate = datetime.datetime.fromisoformat(data['timeIn'])
        if(data.get('timeOut') is not None):
            timeOutDate = datetime.datetime.fromisoformat(data['timeOut'])

    # beginningCashTotal = data['beginningCashOnHand']['total'] if data['beginningCashOnHand'] is not None else 0
    beginningCashTotal = get(data, 'beginningCashOnHand.total', 0)
    endingCashTotal = get(data, 'endingCashOnHand.total', 0)
    sales = data['sales']
    salesAdjustment = data['salesAdjustment']
    discountSummary = data['discountSummary']
    # endingCashOnHand = data.get('endingCashOnHand') or {}

    reprint = data.get('reprint') 
    reprintLabel = '(RE-PRINT)' if reprint else ''
    dateNow = get_local_time()

    try:
        p.set(align='center', bold=True)
        p.text(f'MMG-ALBAY\n\n')
        p.set(align='center', bold=False)
        p.text(f'Operated By: \n')
        p.set(align='center', bold=True)
        p.text(f'MEDICAL MISSION GROUP MULTIPURPOSE COOPERATIVE-ALBAY\n')
        p.set(align='center', bold=False)
        p.text('NON-VAT REG TIN ' + branch['tin'] + '\n')
        p.text(upper_case(branch['streetAddress']) + '\n\n')

        p.set(align='center', bold=True)

        if(type == 'X_REPORT'):
            p.textln(f'X-READING REPORT {reprintLabel}')
        else:
            p.textln(f'Z-READING REPORT {reprintLabel}')

        p.set(align='left', bold=False)
        line(p)

        if(reprint):
            row(p, "Reprint: ", dateNow.strftime("%Y-%m-%d %I:%M%p"))

        row(p, "MIN: ", "---")
        row(p, "SN: ", "---")
        
        if(type == 'X_REPORT'):
            row(p, "Cashier: ", start_case(cashier["first_name"] + " " + cashier["last_name"]))
        else:
            row(p, "Z-Counter #: ", str(1))
            
        row(p, "Date: ", data["date"])
                
        if(type == 'X_REPORT'):
            timeOutDate = ' - '+ timeOutDate.strftime("%I:%M%p") if timeOutDate is not None else ''
            row(p, "Time In & Out: ", f'{timeInDate.strftime("%I:%M%p")}{timeOutDate}')
            row(p, "Beginning Balance: ", beginningCashTotal)
            row(p, "Ending Cash On Hand: ", endingCashTotal)
        else:
            row(p, "Reset Counter #: ", 0)
            
        row(p, "Invoice #: ", f'{sales["invoiceStartNumber"]} - {sales["invoiceEndNumber"]}')
        line(p)

        row(p, "Gross Sales: ", "{:.2f}".format(sales["totalSalesWithoutMemberDiscount"]))
        row(p, "Less Discount: ", "{:.2f}".format(sales["totalMemberDiscount"]))
        row(p, "Less Cancelled: ", salesAdjustment.get('cancelled', 0))
        row(p, "Less Refunded: ", salesAdjustment.get('refunded', 0))
        row(p, "Less VAT Adjustment: ", 0)
        row(p, "Net Sales: ", "{:.2f}".format(sales["totalNetSales"]))

        difference = (sales['totalNetSales']) - endingCashTotal
        cashLoss = difference if difference > 0 else 0
        cashGain = difference * -1 if difference < 0 else 0

        line(p)
        row(p, "Cash Gain: ", "{:.2f}".format(cashGain))
        row(p, "Cash Loss: ", "({:.2f})".format(cashLoss))

        line(p)
        p.set(align='center')
        p.textln('DISCOUNT SUMMARY')
        p.set(align='left')

        row(p, "SC Discount: ", discountSummary.get('senior_citizen', 0))
        row(p, "PWD Discount: ", discountSummary.get('pwd', 0))
        row(p, "NAAC Discount: ", discountSummary.get('naac', 0))
        row(p, "Solo Parent Discount: ", discountSummary.get('solo_parent', 0))

        line(p)
        p.set(align='center')
        p.textln('TRANSACTION SUMMARY')
        p.set(align='left')

        tenders = groupby(data['transactions'], lambda i: i['tenderType'])
        tendersDict = {}
        for key, value in tenders:
            tendersDict[key] = list(value)

        getValue = lambda i: i['totalNetSales']
        cashTender = compute_sum(tendersDict, 'cash', getValue)

        row(p, "CASH: ", "{:.2f}".format(cashTender))
        row(p, "CHEQUE: ", 0)
        row(p, "CREDIT CARD: ", 0)
        # text(p, 'Solo Parent Discount: ':<22}{totalDiscount:>18}')
        # text(p, 'Other Discount: ':<16}{totalDiscount:>24}')

        p.textln()

        p.set(bold=True, align='center')
        p.text('SUPPLIER\n')
        p.text(dvote['name'].upper() + '\n')
        p.set(bold=False, align='center')
        p.text('Address: ' + dvote['address'] + '\n')
        p.text('Vat Reg. TIN: ' + dvote['tin'] + '\n')
        p.text('Accred No: ' + dvote['accredNo'] + '\n')
        p.text('Date Issued: ' + dvote['dateIssued'] + '\n')
        p.text('Valid Until: ' + '---' + '\n')
        p.text('PTU No: ' + dvote.get('PTUno', '---') + '\n\n\n\n')
        p.cut()
        p.close()
    except Exception as e: 
        p.text('\n\n')
        p.cut()
        p.close()
        return {
            'message': 'Unable to print the request',
            'error': repr(e)
        }, 500
    return { 'message': 'Printed successfully' }, 200

@app.post('/display')
def display_message():
    vfd = get_display_device()
    vfd.write("\x0C".encode())
    vfd.write('WELCOME TO'.center(20).encode())
    vfd.write("MMG-ALBAY!!".center(20).encode())

    return { 'message': 'Displayed successfully' }, 200

@app.post('/display/item')
def display_item():
    data = request.get_json()
    item = data
    
    vfd = get_display_device()
    vfd.write("\x0C".encode())
    vfd.write('MMG-ALBAY'.ljust(20).encode())
    vfd.write(f'{item["name"][:11]:<12}{"{:.2f}".format(item["price"])[:8]:>8}'.encode())

    return { 'message': 'Displayed successfully' }, 200

@app.post('/display/total')
def display_total():
    data = request.get_json()
    total = data['total']
        
    vfd = get_display_device()
    vfd.write("\x0C".encode())
    vfd.write('TOTAL'.ljust(20).encode())
    vfd.write("{:.2f}".format(total).rjust(20).encode())

    return { 'message': 'Displayed successfully' }, 200

@app.post('/display/next')
def display_next():
    vfd = get_display_device()
    vfd.write("\x0C".encode())
    vfd.write('THANK YOU!'.center(20).encode())
    vfd.write('COME AGAIN!'.center(20).encode())
    time.sleep(5)

    vfd.write('WELCOME TO'.center(20).encode())
    vfd.write("MMG-ALBAY!!".center(20).encode())

    return { 'message': 'Displayed successfully' }, 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
