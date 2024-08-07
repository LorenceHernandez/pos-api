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


schedule.every(2).minutes.do(downstream_remote_to_internal)
schedule.every(30).seconds.do(upstream_backup_to_remote)


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

    p = printer.Usb(0x04b8,0x0202, 0, profile="TM-U220")
    # p = escpos.printer(Usb(0x04b8, 0x0202))  # For USB connection
    # p = escpos.Network("192.168.1.100")  # For network connection

    p.set(align='center')
    p.set()
    p.text('Hello from Python!\n')
    p.cut()
    return 'Print job sent'


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    p = multiprocessing.Process(target=run_schedule)
    p.start()

    app.run(host="0.0.0.0", debug=True, port=8080)

