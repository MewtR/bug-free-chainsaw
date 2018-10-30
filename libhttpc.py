import socket
import argparse
import sys
import re

def makeRequest(host, port, path, verbose, headers=[], data=''):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        request = path +' HTTP/1.0\r\n'
        request += 'Host: '+ host +'\r\n'
        request += 'Content-length: '+ str(len(data))+'\r\n'
        if headers:
            for h in headers:
                #was list because of nargs in h option
                request+= h+'\r\n'
        #End of request
        request+='\r\n'
        if 'POST' in request:
            if (data):
                request+=data
        s.sendall((request).encode("utf-8"))
        #response = s.recv(4096, socket.MSG_WAITALL)
        response = recv_all(s)
        response = response.decode("utf-8")
        try:
            (header, body) = response.split('\r\n\r\n')
            #body = response.split('\r\n\r\n')
            if (verbose):
                sys.stdout.write(request+'\n')
                sys.stdout.write(header)
                sys.stdout.write('\r\n\r\n')
            sys.stdout.write(body)
        except ValueError as e:
            sys.stdout.write(str(e))
            sys.stdout.write(response)
    finally:
        s.close()


def recv_all(s):
    #socket.settimeout(2)
    response = b''
    data = b''
    while True:
        data = s.recv(4096)
        response+=data
        if not data:
            break
    return response
