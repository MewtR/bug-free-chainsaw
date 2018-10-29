import socket
import argparse
import sys
import re
import threading
import os

def run_server(host, port, directory):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.bind((host, port))
        listener.listen(5)
        print('Listening on port '+ str(port))
        while True:
            conn, addr = listener.accept()
            #threading.Thread(target=handle_client, args=(conn, addr)).start()
            handle_client(conn, addr)
            print ("HELLOOOOOOOOO")
    finally:
        listener.close()
        
def generate_headers(status):
    headers = 'HTTP/1.0 '+ status+'\r\n'
    headers += 'Connection: close'
    headers +='\r\n\r\n'
    return headers.encode("utf-8")

def handle_client(conn, addr):
    data = b''
    received_data = b''
    response = ''
    try:
        while True:
            data = conn.recv(1024)
            received_data+=data
            if not data:
                break
            if '\r\n\r\n' in received_data.decode("utf-8"):
                break
            #print (data.decode("utf-8"))
        if 'GET' in received_data.decode("utf-8"):
            received_data = received_data.decode("utf-8")
            response = do_GET(received_data, conn, addr)
        print (received_data)
            #conn.sendall(data)
        conn.sendall(generate_headers(str(200)))
        conn.sendall(response.encode("utf-8"))
        conn.sendall('\r\n'.encode("utf-8"))
    finally:
        print ("Closing connection with client")
        conn.close()

def do_GET(received_data, conn, addr):
    response = ''
    file_requested = received_data.split(' ')[1]
    files_in_current_dir = os.listdir()
    if file_requested == '/':
        for f in files_in_current_dir:
            response+=f
            response+='\n'
        return response
    else:
        f = re.findall('/(.*)', file_requested)[0]
        if (os.path.isfile(f)):
            try:
                with open(f, 'r') as myfile:
                    response = myfile.read()
            except:
                response = 'Unable to read file'
            return response
        else:
            requested_dir = os.listdir(f)
            for f in requested_dir:
                response+=f
                response+='\n'
            return response
