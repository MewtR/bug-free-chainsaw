import socket
import argparse
import sys
import re
import threading
import os

def run_server(host, port, directory = './', verbose = False):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.bind((host, port))
        listener.listen(5)
        print('Listening on port '+ str(port))
        while True:
            conn, addr = listener.accept()
            handle_client(conn, addr, directory, verbose)
    finally:
        listener.close()
        
def generate_headers(status):
    if status == 500:
        message = 'Internal Server Error'
    elif status == 400:
        message = 'Bad Request'
    elif status == 403:
        message = 'Forbidden'
    elif status == 404:
        message = 'Not Found'
    else:
        status = 200
        message = 'OK'
    headers = 'HTTP/1.0 '+ str(status)+' '+message+'\r\n'
    headers += 'Connection: close'
    headers +='\r\n\r\n'
    return headers.encode("utf-8")

def handle_client(conn, addr, directory, verbose):
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
        received_data = received_data.decode("utf-8")
        if (verbose):
            print (received_data)
        if 'GET' in received_data:
            response = do_GET(received_data, conn, addr, directory, verbose)
        elif 'POST' in received_data:
            response = do_POST(received_data, conn, addr, directory, verbose)
        else:
            response = 'Bad Request'
            #conn.sendall(data)
        if 'access' in response:
            conn.sendall(generate_headers(403))
        elif 'exist' in response:
            conn.sendall(generate_headers(404))
        elif 'Request' in response:
            conn.sendall(generate_headers(400))
        elif 'Unable' in response:
            conn.sendall(generate_headers(500))
        else:
            conn.sendall(generate_headers(200))
        conn.sendall(response.encode("utf-8"))
        conn.sendall('\r\n'.encode("utf-8"))
    finally:
        if (verbose):
            print ("Closing connection with client")
        conn.close()

def do_POST(received_data, conn, addr, directory, verbose):
    response = ''
    file_requested = received_data.split(' ')[1]
    files_in_working_dir = os.listdir(directory)
    if (verbose):
        print ("Files in working directory are: ")
        print (files_in_working_dir)
    body = received_data.split('\r\n\r\n')[1]
    if file_requested == '/':
        response = 'Bad Request'
        return response
    else:
        check_permissions = file_requested.split('/')
        if len(check_permissions) > 2:
            response = 'You do not have access to this directory'
            return response
        f = re.findall('/(.*)', file_requested)[0]
        if (verbose):
            print ("file requested is : ")
            print (f)
        if (os.path.isfile(directory+'/'+f) and (f in files_in_working_dir)):
            try:
                #open file for writing
                with open(directory+'/'+f, 'w') as myfile:
                    myfile.write(body)
                    response = 'Write to file was successful'
            except Exception as e:
                response = 'Unable to write to file'
                response += '\n'
                response += str(e)
            return response
        elif (os.path.isdir(directory+'/'+f)):
            response = 'Bad Request'
            return response
        else:
            try:
                #open file for writing
                with open(directory+'/'+f, 'w') as myfile:
                    myfile.write(body)
                    response = 'Write to file was successful'
            except Exception as e:
                response = 'Unable to write to file'
                response += '\n'
                response += str(e)
            return response

def do_GET(received_data, conn, addr, directory, verbose):
    response = ''
    file_requested = received_data.split(' ')[1]
    files_in_working_dir = os.listdir(directory)
    if (verbose):
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
            response = 'You do not have access to this directory'
            return response
        f = re.findall('/(.*)', file_requested)[0]
        if (verbose):
            print ("file requested is : ")
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
