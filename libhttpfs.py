import socket
import argparse
import sys
import re
import threading
import os

def run_server(host, port, directory = './'):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.bind((host, port))
        listener.listen(5)
        print('Listening on port '+ str(port))
        while True:
            conn, addr = listener.accept()
            #threading.Thread(target=handle_client, args=(conn, addr)).start()
            handle_client(conn, addr, directory)
    finally:
        listener.close()
        
def generate_headers(status):
    headers = 'HTTP/1.0 '+ status+'\r\n'
    headers += 'Connection: close'
    headers +='\r\n\r\n'
    return headers.encode("utf-8")

def handle_client(conn, addr, directory):
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
            response = do_GET(received_data, conn, addr, directory)
        print (received_data)
            #conn.sendall(data)
        conn.sendall(generate_headers(str(200)))
        conn.sendall(response.encode("utf-8"))
        conn.sendall('\r\n'.encode("utf-8"))
    finally:
        print ("Closing connection with client")
        conn.close()

def do_GET(received_data, conn, addr, directory):
    response = ''
    file_requested = received_data.split(' ')[1]
    files_in_working_dir = os.listdir(directory)
    print ("Files in working directory are: ")
    print (files_in_working_dir)
    #List files in current working directory
    if file_requested == '/':
        for f in files_in_working_dir:
            response+=f
            response+='\n'
        return response
    #Read from a file in the current working directory
    else:
        check_permissions = file_requested.split('/')
        if len(check_permissions) > 2:
            print (check_permissions)
            response = 'You do not have access to this directory'
            return response
        f = re.findall('/(.*)', file_requested)[0]
        print ("file is : ")
        print (f)
        if (os.path.isfile(directory+'/'+f) and (f in files_in_working_dir)):
            try:
                with open(directory+'/'+f, 'r') as myfile:
                    response = myfile.read()
            except Exception as e:
                response = 'Unable to read file'
                response += '\n'
                response += str(e)
            return response
        elif (os.path.isdir(directory+'/'+f)):
            response = 'You do not have access to this directory'
            return response
        else:
            response = 'File does not exist'
            return response
       # else:
       #     requested_dir = os.listdir(directory+'/'+f)
       #     for f in requested_dir:
       #         response+=f
       #         response+='\n'
       #     return response
