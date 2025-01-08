import datetime
from itertools import groupby
import os
import platform
import time
from flask import Flask, request, Response
from flask_cors import CORS
from pydash import get, start_case, upper_case
import requests
import socket
from pydash.strings import to_lower
import serial
from escpos.printer import Network
from serial.tools import list_ports


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
    # return False
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False

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
    dateNow = datetime.datetime.now()

    # discount = data.get('discountApplied') or {}
    # discountAmount = discount.get('value', '---') if discount.get('type') == 'fixed' else discount.get('totalDiscount', '---')

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
        p.textln('-' * 33)

        if(reprint):
            p.textln(f'{"Reprint: ":<9}{dateNow.strftime("%Y-%m-%d %I:%M%p"):>24}')

        p.textln(f'{"MIN: ":<5}{"---":>28}')
        p.textln(f'{"SN: ":<4}{"---":>29}')
        p.textln(f'{"Date & Time: ":<13}{dt.strftime("%Y-%m-%d %I:%M%p"):>20}')
        p.textln(f'{"Cashier: ":<9}{start_case(cashier["first_name"] + " " + cashier["last_name"]):>24}')
        p.textln(f'{"Invoice #: ":<11}{str(transaction["invoiceNumber"]).zfill(6):>22}')

        p.textln('-' * 33)
        p.set(align='center', bold=True)
        p.text('SOLD TO\n')
        p.set(align='left', bold=False)

        p.textln(f'{"Name: ":<6}{start_case(to_lower(customer["name"])):>27}')
        p.textln(f'{"Address: ":<9}{start_case(to_lower(customer["address"])):>24}')
        p.textln(f'{"TIN: ":<5}{customer.get("tin_number") or "---":>28}')

        if(companyCopy):
            p.textln(f'{"Age: ":<5}{customer["age"]:>28}')
            p.textln(f'{"Birth Date: ":<12}{str(customer["birthDate"]).split("T")[0]:>21}')
        else:
            p.textln(f'{"Age: ":<5}{"---":>28}')
            p.textln(f'{"Birth Date: ":<12}{"---":>21}')
            
        p.textln(f'{"Requested By: ":<14}{transaction.get("requestedByName", "---"):>19}')
        # p.textln(f'{'SC/PWD/Other ID No.: ':<21}{customer.get('customerTypeId') or '---':>19}')

        p.textln('-' * 33)
        p.set(align='center', bold=True)
        p.textln(f'{"ITEM ":<16}|QTY|PRICE|AMOUNT')
        p.set(bold=False)
        p.textln('-' * 33)

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
                p.textln(str(indented + item["name"][:14]).ljust(16) + f'({item["quantity"]})'.center(5) + str(amount).center(6) + str(amount).rjust(6))
            
            if(package is not None):
                discounts = list(filter(lambda i: i.get('packageId') == package['_id'] and i['memberType'] is None, transaction['discounts']))
                if(len(discounts) > 0):
                    discount = discounts[0]
                    totalDiscount = discount['value'] if discount['type'] == 'fixed' else (transaction['totalGrossSales'] * (discount['value'] / 100))
                    p.textln(f'  - Less: {discount["name"]}'[:23].ljust(24) + f'- {"{:.2f}".format(totalDiscount)}'.rjust(9))

                # p.set(bold=False)
                # for test in item['labTest']:
                #     indented = '  '
                #     amount = test['amount'] if transaction['status'] == 'Completed' else test['amount'] * -1
                #     p.textln(indented + start_case(test["name"][:17]).ljust(18) + f'({test["qty"]})'.center(7) + str(amount).center(7) + str(amount).rjust(8))
                #     # p.textln(f'{(indented + start_case(test["name"]))[:17]:<18}{f'({test["qty"]})':^7}{amount:^7}{amount:>8}')

                # discount = item['discount']
                # if(transaction['status'] == 'Completed' and item['packageForMemberType'] != 'seniorcitizenpwd' and discount != None):
                #     totalDiscount = discount['value'] if discount['type'] == 'fixed' else (transaction['subTotal'] * (discount['value'] / 100))
                #     p.textln(f'  - Less: {discount["name"]}'.ljust(31) + f'- {totalDiscount}'.rjust(9))
                    
                
                # if(service['source'] == 'promo'):
                #     serviceDiscount = service.get('discount')
                #     serviceDiscountAmount = service.get('totalPackagePrice', 0) - service.get('totalDiscountedPrice', 0)
                #     p.textln(f'{(indented + 'Discount: ' + serviceDiscount['name'])[:31]:<31}{'- ' + str(serviceDiscountAmount):>9}')


        paymentDue = transaction.get('paymentDue')

        p.textln('-' * 33)
        if (transaction['status'] == 'Cancelled'):
            p.set(align='center', bold=True)
            p.text('*** VOIDED TRANSACTION ***\n\n')
            p.set(align='left', bold=False)

            p.textln(f'{"Total Amount: ":<20}{transaction["paymentDetails"]["subTotal"]:>20}')
            p.textln(f'{"Reason: ":<8}{transaction.get("reason") or "---":>32}')
        elif(transaction['status'] == 'Refunded'):
            # p.textln(f'{'Number of Items: ':<20}{request_data['totalQuantity']:>20}')
            p.set(align='center', bold=True)
            p.text('*** REFUNDED TRANSACTION ***\n\n')
            p.set(align='left', bold=False)
            p.textln(f'{"Refunded Amount: ":<20}{paymentDue:>20}')
            p.textln(f'{"Previous Invoice Number: ":<25}{str(transaction["previousInvoiceNumber"]).zfill(6):>15}')
            p.textln(f'{"Reason: ":<8}{transaction.get("refundedReason") or "---":>32}')
        else:
            p.set(align='left', bold=True)
            p.textln(f'{"Total Sales: ":<13}{transaction["totalSalesWithoutMemberDiscount"]:>20}')

            p.set(bold=False)
            # for discount in data['discounts']:
            #     indented = '    '

            #     discountAmount = discount.get('value', '---') if discount.get('type') == 'fixed' else discount.get('totalDiscount', '---')
            #     p.textln(f'{(discount.get('name', '---') + ' Discount')[:29]:<30}{f'- {discountAmount}':<10}')
            
            p.textln(f'{"Less: SC/PWD/NAAC/MOV/SP ":<25}' + f'({transaction["totalMemberDiscount"]})'.rjust(8))
            p.textln(f'{"Less: Withholding Tax ":<22}{"(0)":>11}')
            
            p.set(bold=True)
            p.textln(f'{"TOTAL AMOUNT DUE: ":<18}{transaction["totalNetSales"]:>15}')
            
            p.set(bold=False)
            p.textln(f'{"Tender Amount: ":<15}{transaction["tenderAmount"]:>18}')
            p.textln(f'{"Tender Type: ":<13}{upper_case(transaction["tenderType"]):>20}')
            p.textln(f'{"Change: ":<8}{transaction["change"]:>25}')
            # p.textln(f'{'Number of Items: ':<20}{data.get('totalQuantity', 0):>20}')

        p.textln('-' * 33)

        p.set(align='center', bold=True)
        p.text('*THIS DOCUMENT IS NOT VALID FOR CLAIM OF INPUT TAX*\n')
        p.textln('-' * 33)
        p.textln()
        p.set(align='left', bold=False)

        totalMemberDiscount = transaction['totalMemberDiscount']
        customerTypeId = customer.get('customer_type_id') or ('_' * 8) 

        p.text(f'{"ID (SC/PWD/NAAC/MOV/SP): ":<25}{customerTypeId:>8}\n\n')
        p.text(f'{"Signature: ":<11}{("_" * 8):>22}\n\n')

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
    # endingCashOnHand = data.get('endingCashOnHand') or {}

    reprint = data.get('reprint') 
    reprintLabel = '(RE-PRINT)' if reprint else ''
    dateNow = datetime.datetime.now()

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
        p.textln('-' * 33)

        if(reprint):
            p.textln(f'{"Reprint: ":<9}{dateNow.strftime("%Y-%m-%d %I:%M%p"):>24}')
        p.textln(f'{"MIN: ":<5}{"---":>28}')
        p.textln(f'{"SN: ":<4}{"---":>29}')
        
        if(type == 'X_REPORT'):
            p.textln(f'{"Cashier: ":<14}{start_case(cashier["first_name"] + " " + cashier["last_name"]):>19}')
        else:
            p.textln(f'{"Z-Counter #: ":<13}{1:>20}')
            
        p.textln(f'{"Date: ":<6}{data["date"]:>27}')
                
        if(type == 'X_REPORT'):
            timeOutDate = ' - '+ timeOutDate.strftime("%I:%M%p") if timeOutDate is not None else ''
            p.textln(f'{"Time In & Out: ":<15}' + f'{timeInDate.strftime("%I:%M%p")}{timeOutDate}'.rjust(18))
            p.textln(f'{"Beginning Balance: ":<19}{beginningCashTotal:>14}')
        else:
            p.textln(f'{"Reset Counter #: ":<17}{0:>16}')
            
        p.textln(f'{"Invoice #: ":<11}' + f'{sales["invoiceStartNumber"]} - {sales["invoiceEndNumber"]}'.rjust(22))
        p.textln('-' * 33)

        p.textln(f'{"Gross Sales: ":<13}{"{:.2f}".format(sales["totalGrossSales"]):>20}')
        p.textln(f'{"Less Discount: ":<16}{"{:.2f}".format(sales["totalMemberDiscount"]):>17}')
        p.textln(f'{"Less Return: ":<13}{0:>20}')
        p.textln(f'{"Less Void: ":<11}{0:>22}')
        p.textln(f'{"Less VAT Adjustment: ":<21}{0:>12}')
        p.textln(f'{"Net Sales: ":<11}{"{:.2f}".format(sales["totalNetSales"]):>22}')


        difference = (sales['totalNetSales']) - endingCashTotal
        cashLoss = difference if difference > 0 else 0
        cashGain = difference * -1 if difference < 0 else 0

        p.textln('-' * 33)
        p.textln(f'{"Cash Gain: ":<11}{"{:.2f}".format(cashGain):>22}')
        p.textln(f'{"Cash Loss: ":<11}{"({:.2f})".format(cashLoss):>22}')

        p.textln('-' * 33)
        p.set(align='center')
        p.textln('DISCOUNT SUMMARY')
        p.set(align='left')

        discounts = groupby(filter(lambda i: i['memberType'] is not None, data['discounts']), lambda i: i['memberType'])
        discountDict = {}
        for key, value in discounts:
            discountDict[key] = list(value)

        getValue = lambda i: i['transaction']['totalMemberDiscount']
        scDiscount = compute_sum(discountDict, 'senior_citizen', getValue)
        pwdDiscount = compute_sum(discountDict, 'pwd', getValue)
        naacDiscount = compute_sum(discountDict, 'naac', getValue)
        spDiscount = compute_sum(discountDict, 'solo_parent', getValue)

        p.textln(f'{"SC Discount: ":<13}{"{:.2f}".format(scDiscount):>20}')
        p.textln(f'{"PWD Discount: ":<14}{"{:.2f}".format(pwdDiscount):>19}')
        p.textln(f'{"NAAC Discount: ":<15}{"{:.2f}".format(naacDiscount):>18}')
        p.textln(f'{"Solo Parent Discount: ":<22}{"{:.2f}".format(spDiscount):>11}')
        p.textln(f'{"Other Discount: ":<16}{0:>17}')

        # for discount in discounts:
        #         indented = '    '

        #         discountAmount = discount.get('value', '---') if discount.get('type') == 'fixed' else discount.get('totalDiscount', '---')
        #         p.textln(f'{(discount['name'] + ' Discount')[:29]:<30}{f'- {totalDiscount}':<10}')

        p.textln('-' * 33)
        p.set(align='center')
        p.textln('SALES ADJUSTMENT')
        p.set(align='left')
        p.textln(f'{"VOID: ":<6}{0:>27}')
        p.textln(f'{"RETURN: ":<8}{0:>25}')
        

        p.textln('-' * 33)
        p.set(align='center')
        p.textln('TRANSACTION SUMMARY')
        p.set(align='left')

        tenders = groupby(data['transactions'], lambda i: i['tenderType'])
        tendersDict = {}
        for key, value in tenders:
            tendersDict[key] = list(value)

        getValue = lambda i: i['totalNetSales']
        cashTender = compute_sum(tendersDict, 'cash', getValue)

        p.textln(f'{"CASH: ":<6}{"{:.2f}".format(cashTender):>27}')
        p.textln(f'{"CHEQUE: ":<8}{0:>25}')
        p.textln(f'{"CREDIT CARD: ":<13}{0:>20}')
        # p.textln(f'{'Solo Parent Discount: ':<22}{totalDiscount:>18}')
        # p.textln(f'{'Other Discount: ':<16}{totalDiscount:>24}')

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
