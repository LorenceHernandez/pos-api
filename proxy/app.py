import datetime
import os
from flask import Flask, request, Response
from flask_cors import CORS
import requests
import socket
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

    print('Target URL: ', target_url)

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

@app.post('/print')
def print_text():
    print('printing...')
    request_data = request.get_json()
    p = None
    try:
        # p = printer.Usb(0x04B8,0x0202, 0, profile="TM-U220")
        p = printer.Usb(0x04B8,0x0202)

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
    # try:
    
    data = request_data['combinedData']
    branch = data['branch']
    cashier = data['cashier']
    dvote = request_data['dvoteDetails'][0]
    customer = data['customerData']

    try:
        p.set(align='center', bold=True)
        p.text(branch['name'] + '\n')
        p.text(branch['city'] + ', ' + branch['state'] + '\n')
        p.text(branch['tin'] + '\n\n')
        p.set(align='center', bold=True)
        p.text('Customer Information\n')
        p.set(align='left')

        p.text('Name: ' + customer['name'] +  '\n')
        p.text('Address: ' + customer['address'] +  '\n')
        p.text('TIN: ' + customer['tin'] +  '\n')

        if(request_data.get('showAddress') is not None and customer['type'] == 'customer'):
            p.text('Age: ' + customer['age'] +  '\n')
            p.text('Birth Date: ' + customer['birthDate'] +  '\n')
        
        p.text('Referred By: ' + data.get('referredByName', '---') +  '\n\n')

        p.set(align='center')
        p.text('Items\n')
        p.set(align='left', bold=False)
        for item_x in data['items']:
            p.set(align='left')
            p.text(f'{item_x['name']} ({'Package' if item_x['source'] == 'package' else 'Lab Test' }) \n')
            
            p.set(align='right')
            p.text(f'{item_x['qty']} x {item_x['price']} = {item_x['amount']} \n')


        p.set(align='center', bold=True)
        p.text('\nDetails\n')
        p.set(align='left', bold=False)
        p.text(f'Sub-Total: {data['subTotal']}\n')
        p.text(f'Discount Applied: {data['discountApplied']['totalDiscount']}\n')
        p.text(f'Amount Due: {data['paymentDue']}\n')
        p.text('Tender Type: ' + request_data['tenderType'] +  '\n')
        p.text(f'Tender Amount: {request_data['amountGiven']}\n')
        p.text(f'Change: {request_data['change']}\n')
        p.text(f'Number of Items: {request_data['totalQuantity']}\n\n')

        p.set(align='center')
        p.text('Invoice No.: ' + str(data['invoiceNumber']).zfill(6) +  '\n')
        p.text('Cashier: ' + cashier['first_name'] + ' ' + cashier['last_name'] +  '\n')

        dt = datetime.datetime.fromisoformat(data['transactionDate'])

        p.text('Date: ' + dt.strftime("%B-%d-%Y %I:%M:%S %p") +  '\n\n')

        p.text('This document is not valid for income tax\n\n')
        p.text('Signature of SC/PWD:\n\n\n\n')
        p.text('--------------------------\n')

        p.set(bold=True)
        p.text('Supplier\n')
        p.text(dvote['name'] + '\n')
        p.text(dvote['address'] + '\n')
        p.text(dvote['tin'] + '\n\n')
        p.text(dvote['accredNo'] + '\n')
        p.text(dvote['dateIssued'] + '\n\n')
        p.text('\n')
        p.cut()
    except Exception as e: 
        p.text('\n\n')
        p.cut()
        return {
            'message': 'Unable to print the request',
            'error': repr(e)
        }, 500
    return { 'message': 'Printed successfully' }, 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8080)
