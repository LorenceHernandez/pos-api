import datetime
import os
from flask import Flask, request, Response
from flask_cors import CORS
from pydash import start_case, upper_case
import requests
import socket
from pydash.strings import to_lower
from escpos import *


app = Flask(__name__)

from dotenv import load_dotenv

load_dotenv('../.env')
# Replace with your local and cloud server URLs
LOCAL_SERVER_URL = os.getenv('LOCAL_SERVER_URL')
CLOUD_SERVER_URL = os.getenv('CLOUD_SERVER_URL')

print('LOCAL_SERVER_URL', LOCAL_SERVER_URL)
print('CLOUD_SERVER_URL', CLOUD_SERVER_URL)


def is_internet_connected():
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
        p = printer.Usb(0x04B8,0x0202, 0, profile="TM-U220")
        # p = printer.Network("192.168.5.200")
        # p = printer.Usb(0x04B8, 0x0202)

    except Exception as e:
        try:
            p = printer.Network("192.168.5.200")

            if p is None:
                raise
        except Exception as e:
            return {
                'message': 'Unable to print the request',
                'error': repr(e)
            }, 500
    
    # p = escpos.printer(Usb(0x04b8, 0x0202))  # For USB connection
    # p = escpos.Network("192.168.1.100")  # For network connection
    
    print(f'PRINTING... {repr(p)}')

    data = request_data['combinedData']
    branch = data['branch']
    cashier = data['cashier']
    dvote = request_data['dvoteDetails'][0]
    customer = data['customerData']
    companyCopy = request_data.get('companyCopy')
    companyLabel = '(COMPANY\'S COPY)' if companyCopy else ''

    dt = datetime.datetime.fromisoformat(data['transactionDate'])

    # discount = data.get('discountApplied') or {}
    # discountAmount = discount.get('value', '---') if discount.get('type') == 'fixed' else discount.get('totalDiscount', '---')

    try:
        p.set(align='center', bold=True)
        p.text(f'MMG-ALBAY {companyLabel}\n\n')
        p.set(bold=False)
        p.text(f'Operated By: \n')
        p.set(bold=True)
        p.text(f'MEDICAL MISSION GROUP MULTIPURPOSE COOPERATIVE-ALBAY\n')
        p.set(bold=False)
        p.text('NON-VAT REG TIN ' + branch['tin'] + '\n')
        p.text(upper_case(branch['streetAddress']) + '\n\n')

        p.set(align='center', bold=True)
        p.text(f'INVOICE\n')

        p.textln('-' * 40)
        p.set(align='left', bold=False)

        p.textln(f'{'Invoice No.: ':<13}{str(data['invoiceNumber']).zfill(5):>27}')
        p.textln(f'{'MIN: ':<5}{'---':>35}')
        p.textln(f'{'SN: ':<4}{'---':>36}')
        p.textln(f'{'Date & Time: ':<13}{dt.strftime("%m-%d-%Y %I:%M:%S%p"):>27}')
        p.textln(f'{'Cashier: ':<14}{start_case(cashier['first_name'] + ' ' + cashier['last_name']):>26}')

        p.textln('-' * 40)

        p.set(align='center', bold=True)
        p.text('SOLD TO\n')
        p.set(align='left', bold=False)

        p.textln(f'{'Name: ':<6}{start_case(to_lower(customer['name'])):>34}')
        p.textln(f'{'Address: ':<9}{start_case(to_lower(customer['address'])):>31}')
        p.textln(f'{'TIN: ':<5}{customer['tin']:>35}')

        if(companyCopy):
            p.textln(f'{'Age: ':<5}{customer['age']:>35}')
            p.textln(f'{'Birth Date: ':<12}{customer['birthDate']:>28}')
        else:
            p.textln(f'{'Age: ':<5}{'---':>35}')
            p.textln(f'{'Birth Date: ':<12}{'---':>28}')
            
        p.textln(f'{'Requested By: ':<14}{data.get('requestedByName', '---'):>26}')
        # p.textln(f'{'SC/PWD/Other ID No.: ':<21}{customer.get('customerTypeId') or '---':>19}')

        p.textln('-' * 40)
        p.set(bold=True)
        p.textln(f'{'ITEM DESCRIPTION':<18}| QTY | PRICE | AMOUNT')
        p.set(bold=False)
        p.textln('-' * 40)

        for service in data['items']:
            is_labtest = service['source'] == 'labTest'

            if(is_labtest):
                amount = service['amount'] if data['status'] == 'Completed' else service['amount'] * -1
                p.textln(f'{service['name'][:17]:<18}{f'({service['qty']})':^7}{amount:^7}{amount:>8}')
                continue

            p.set(align='left', bold=True)
            p.text(f'> {service['name']} \n')
        
            p.set(bold=False)
            for test in service['labTest']:
                indented = '  '
                amount = test['amount'] if data['status'] == 'Completed' else test['amount'] * -1
                p.textln(f'{(indented + start_case(test['name']))[:17]:<18}{f'({test['qty']})':^7}{amount:^7}{amount:>8}')

            discount = service['discount']
            if(data['status'] == 'Completed' and service['packageForMemberType'] != 'seniorcitizenpwd' and discount != None):
                totalDiscount = discount['value'] if discount['type'] == 'fixed' else (data['subTotal'] * (discount['value'] / 100))
                p.textln(f'{f'  - Less: {discount['name']}':<31}{f'- {totalDiscount}':>9}')
                
            
            # if(service['source'] == 'promo'):
            #     serviceDiscount = service.get('discount')
            #     serviceDiscountAmount = service.get('totalPackagePrice', 0) - service.get('totalDiscountedPrice', 0)
            #     p.textln(f'{(indented + 'Discount: ' + serviceDiscount['name'])[:31]:<31}{'- ' + str(serviceDiscountAmount):>9}')


        paymentDue = data['paymentDue']

        p.textln('-' * 40)
        if (data['status'] == 'Cancelled'):
            p.set(align='center', bold=True)
            p.text('*** VOIDED TRANSACTION ***\n\n')
            p.set(align='left', bold=False)

            p.textln(f'{'Total Amount: ':<20}{data['paymentDetails']['subTotal']:>20}')
            p.textln(f'{'Reason: ':<8}{data.get('reason') or '---':>32}')
        elif(data['status'] == 'Refunded'):
            # p.textln(f'{'Number of Items: ':<20}{request_data['totalQuantity']:>20}')
            p.set(align='center', bold=True)
            p.text('*** REFUNDED TRANSACTION ***\n\n')
            p.set(align='left', bold=False)
            p.textln(f'{'Refunded Amount: ':<20}{paymentDue:>20}')
            p.textln(f'{'Previous Invoice Number: ':<25}{str(data['previousInvoiceNumber']).zfill(5):>15}')
            p.textln(f'{'Reason: ':<8}{data.get('refundedReason') or '---':>32}')
        else:
            p.set(align='left', bold=True)
            p.textln(f'{'Total Sales: ':<20}{data['subTotal']:>20}')

            p.set(bold=False)
            # for discount in data['discounts']:
            #     indented = '    '

            #     discountAmount = discount.get('value', '---') if discount.get('type') == 'fixed' else discount.get('totalDiscount', '---')
            #     p.textln(f'{(discount.get('name', '---') + ' Discount')[:29]:<30}{f'- {discountAmount}':<10}')
            
            p.textln(f'{'Less: Discount(SC/PWD/NAAC/MOV/SP) ':<35}{f'({data['totalMemberDiscount']})':>5}')
            p.textln(f'{'Less: Withholding Tax ':<22}{'(0)':>18}')
            
            p.set(bold=True)
            p.textln(f'{'TOTAL AMOUNT DUE: ':<20}{data['paymentDue']:>20}\n')
            
            p.set(bold=False)
            p.textln(f'{'Tender Amount: ':<20}{request_data['amountGiven']:>20}')
            p.textln(f'{'Tender Type: ':<20}{upper_case(request_data['tenderType']):>20}')
            p.textln(f'{'Change: ':<20}{request_data['change']:>20}')
            # p.textln(f'{'Number of Items: ':<20}{data.get('totalQuantity', 0):>20}')

        p.textln('-' * 40)

        p.set(align='center', bold=True)
        p.text('*THIS DOCUMENT IS NOT VALID FOR CLAIM OF INPUT TAX*\n')
        p.textln('-' * 40)
        p.textln()
        p.set(align='left', bold=False)

        totalMemberDiscount = data['totalMemberDiscount']
        customerTypeId = customer.get('customerTypeId') or ('_' * 8) 

        p.text(f'{'ID No. (SC/PWD/NAAC/MOV/SP): ':<29}{customerTypeId:>11}\n\n')
        p.text(f'{'Signature (SC/PWD/NAAC/MOV/SP): ':<32}{('_' * 8):>8}\n\n')
        p.textln()

        p.set(align="center", bold=True)
        p.text('SUPPLIER\n')
        p.text(dvote['name'].upper() + '\n')
        p.set(bold=False)
        p.text('Address' + dvote['address'] + '\n')
        p.text('Vat Reg. TIN: ' + dvote['tin'] + '\n')
        p.text('Accred No: ' + dvote['accredNo'] + '\n')
        p.text('Date Issued: ' + dvote['dateIssued'] + '\n')
        p.text('Valid Until: ' + '---' + '\n')
        p.text('PTU No: ' + dvote.get('PTUno', '---') + '\n\n')
        p.cut()
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


@app.post('/print-report')
def print_report():
    data = request.get_json()
    p = None
    try:
        p = printer.Usb(0x04B8,0x0202, 0, profile="TM-U220")
        # p = printer.Usb(0x04B8, 0x0202)

        if p is None:
            raise
    except Exception as e:
        try:
            p = printer.Network("192.168.5.200")

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
        timeOutDate = datetime.datetime.fromisoformat(data['timeOut'])

    beginningCashTotal = data['beginningCashOnHand']['total'] if data['beginningCashOnHand'] is not None else 0
    cashSales = data['cashSales']
    endingCashOnHand = data['endingCashOnHand'] or {}

    try:
        p.set(align='center', bold=True)
        p.text(f'MMG-ALBAY\n\n')
        p.set(bold=False)
        p.text(f'Operated By: \n')
        p.set(bold=True)
        p.text(f'MEDICAL MISSION GROUP MULTIPURPOSE COOPERATIVE-ALBAY\n')
        p.set(bold=False)
        p.text('NON-VAT REG TIN ' + branch['tin'] + '\n')
        p.text(upper_case(branch['streetAddress']) + '\n\n')

        # p.set(align='center', bold=True)
        # p.text(f'{title}\n')
        # p.text(f'MMG-ALBAY\n')
        # p.set(bold=False)
        # p.set(bold=True)
        # p.set(bold=False)
        # p.text(branch['streetAddress'] + ' ' + branch['city'] + ', ' + branch['state'] + '\n')
        # p.text(branch['tin'] + '\n')

        p.textln('-' * 40)
        p.set(align='left')

        p.textln(f'{'MIN: ':<5}{'---':>35}')
        p.textln(f'{'SN: ':<4}{'---':>36}')
        
        if(type == 'X_REPORT'):
            p.textln(f'{'Cashier Name: ':<14}{start_case(cashier['first_name'] + ' ' + cashier['last_name']):>26}')
        p.textln(f'{'Date: ':<6}{data['date']:>34}')
        
        if(type == 'X_REPORT'):
            p.textln(f'{'Time In & Out: ':<15}{f'{timeInDate.strftime("%I:%M%p")} - {timeOutDate.strftime("%I:%M%p")}':>25}')
        
        if(type == 'X_REPORT'):
            p.textln(f'{'Beginning Balance: ':<19}{beginningCashTotal:>21}')

        p.textln('-' * 40)

        p.textln(f'{'Invoice Numbers: ':<17}{f'{cashSales['invoiceStartNumber']} - {cashSales['invoiceEndNumber']}':>23}')
        
        if(type == 'X_REPORT'):
            p.textln('Cash Count: ')

        cash_count = endingCashOnHand.get('count')
        if(cash_count is not None):
            for key, value in dict(cash_count).items():
                p.textln(f'{f'{key} * {value}':>40}')
        p.textln(f'{'Total Cash Count: ':<18}{(endingCashOnHand.get('total', 0)):>22}')

        p.textln('-' * 40)

        discounts = [
            { 'name': 'SR/PWD 20%', 'value': 476 },
            # { 'name': 'Non-Member 7%', 'value': 277.55 },
        ]

        p.textln(f'{'Gross Sales: ':<13}{cashSales['totalGrossSales']:>27}')
        totalDiscount = cashSales['totalGrossSales'] - cashSales['totalNetSales']
        totalDiscount = "{:.2f}".format(totalDiscount)

        for discount in discounts:
                indented = '    '

                discountAmount = discount.get('value', '---') if discount.get('type') == 'fixed' else discount.get('totalDiscount', '---')
                p.textln(f'{(discount['name'] + ' Discount')[:29]:<30}{f'- {totalDiscount}':<10}')

        p.textln(f'{'Total Discount: ':<16}{totalDiscount:>24}')
        p.textln(f'{'Net Sales: ':<11}{cashSales['totalNetSales']:>29}')

        difference = (cashSales['totalNetSales']) - endingCashOnHand.get('total', 0)
        cashLoss = difference if difference > 0 else 0
        cashGain = difference * -1 if difference < 0 else 0

        if(type == 'X_REPORT'):
            p.textln(f'{'Cash Gain: ':<11}{"{:.2f}".format(cashGain):>29}')
            p.textln(f'{'Cash Loss: ':<11}{"({:.2f})".format(cashLoss):>29}')
        
        p.textln('-' * 40)

        p.set(bold=True, align='center')
        p.text('SUPPLIER\n')
        p.text(dvote['name'].upper() + '\n')
        p.set(bold=False)
        p.text('Address' + dvote['address'] + '\n')
        p.text('Vat Reg. TIN: ' + dvote['tin'] + '\n')
        p.text('Accred No: ' + dvote['accredNo'] + '\n')
        p.text('Date Issued: ' + dvote['dateIssued'] + '\n')
        p.text('Valid Until: ' + '---' + '\n')
        p.text('PTU No: ' + dvote.get('PTUno', '---') + '\n\n')
        p.cut()
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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
