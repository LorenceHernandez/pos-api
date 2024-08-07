import multiprocessing
import os
import time
from flask import Flask, request, Response
from flask_cors import CORS
import requests
import socket
from escpos import *
import schedule

from sync.sync import downstream_remote_to_internal, upstream_backup_to_remote

app = Flask(__name__)

from dotenv import load_dotenv

load_dotenv('../.env')
# Replace with your local and cloud server URLs
LOCAL_SERVER_URL = os.getenv('LOCAL_URL')
CLOUD_SERVER_URL = os.getenv('CLOUD_URL')


# schedule.every().second.do(downstream_remote_to_internal)
# schedule.every().second.do(upstream_backup_to_remote)


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

@app.route('/print')
def print_text():
    request_data = request.get_json()

    p = None
    try:
        p = printer.Usb(0x04b8,0x0202, 0, profile="TM-U220")
    except Exception as e:
        return {
            'message': 'Unable to print the request',
            'error': repr(e)
        }, 500
    
    # p = escpos.printer(Usb(0x04b8, 0x0202))  # For USB connection
    # p = escpos.Network("192.168.1.100")  # For network connection
    data = request_data['combinedData']
    dvote = request_data['dvoteDetails'][0]
    customer = data['customerData']

    p.set(align='center', bold=True)
    p.text(data['branchName'] + '\n')
    p.set(align='left', bold=False)
    p.text(data['branchTIN'] + '\n')
    p.set(align='center', bold=True)
    p.text('Customer Information\n')
    p.set(align='left')

    p.text('Name: ' + customer['name'] +  '\n')
    p.text('Address: ' + customer['address'] +  '\n')
    p.text('TIN: ' + customer['tin'] +  '\n\n')

    if(request_data['showAddress'] and customer['type'] == 'customer'):
        p.text('Age: ' + customer['age'] +  '\n')
        p.text('Birth Date: ' + customer['birthDate'] +  '\n')
    
    p.text('Referred By: ' + data.get('referredByName', '---') +  '\n\n')


    p.set(align='center')
    p.text('Items\n')
    p.set(align='left', bold=False)
    for item in data['items']:
        p.text(f'{item['name']} ({'Package' if item['source'] == 'package' else 'Lab Test' }) \n')
        p.text(f'{item['qty']} x {item['price']} = {item['amount']} \n')

    p.set(align='left', bold=True)

    p.text('Details\n')
    p.set(bold=False)
    p.text('Sub-Total: ' + data['subTotal'] +  '\n')
    p.text('Discount Applied: ' + data['discountApplied']['totalDiscount'] +  '\n')
    p.text('Amount Due: ' + data['paymentDue'] +  '\n')
    p.text('Tender Type: ' + request_data['tenderType'] +  '\n')
    p.text('Tender Amount: ' + request_data['amountGiven'] +  '\n')
    p.text('Change: ' + request_data['change'] +  '\n')
    p.text('Number of Items: ' + request_data['totalQuantity'] +  '\n\n')

    p.set(align='center')
    p.text('Invoice No.: ' + data['invoiceNo'] +  '\n')
    p.text('Cashier: ' + data['cashierName'] +  '\n')
    p.text('Date: ' + data['transactionDate'] +  '\n\n')

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
    p.text('\n\n')
    p.cut()

    return { 'message': 'Printed successfully' }, 200


# def run_schedule():
#     while True:
#         downstream_remote_to_internal()
#         upstream_backup_to_remote()
#         time.sleep(10)

if __name__ == '__main__':
    # p = multiprocessing.Process(target=run_schedule)
    # p.start()

    app.run(host="0.0.0.0", debug=True, port=8080)

