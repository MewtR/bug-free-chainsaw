import socket
import argparse
import sys
import re

# When using telnet some sites require 'Host:'(httpbin.org) while others don't(google.ca)

host = 'httpbin.org'
port = 80

def get(host, path, verbose, headers=[]):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, 80))
        request = 'GET /'+ path +' HTTP/1.0\r\n'
        #request += 'Host: '+ host +'\r\n\r\n'
        request += 'Host: '+ host +'\r\n'
        if headers:
            for h in headers:
                request+= h+'\r\n'
        #End of request
        request+='\r\n'
        print (request)
        s.sendall((request).encode("utf-8"))
        #response = s.recv(len(request), socket.MSG_WAITALL)
        response = s.recv(4096, socket.MSG_WAITALL)
        response = response.decode("utf-8")
        #print (response.split('\r\n\r\n'))
        (header, body) = response.split('\r\n\r\n')
        #print (body)
        #print (re.search('\r\n\r\n(.*)',response))
        if (verbose):
            sys.stdout.write(header)
            sys.stdout.write('\r\n\r\n')
        sys.stdout.write(body)
    finally:
        s.close()

def post(host, path, verbose, headers=[], data=''):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, 80))
        request = 'POST /'+ path +' HTTP/1.0\r\n'
        request += 'Host: '+ host +'\r\n'
        if headers:
            for h in headers:
                #was list becuase of nargs in h option
                request+= h+'\r\n'
        #End of request
        request+='\r\n'
        if (data):
            request+=data
        print (request)
        s.sendall((request).encode("utf-8"))
        response = s.recv(4096, socket.MSG_WAITALL)
        response = response.decode("utf-8")
        (header, body) = response.split('\r\n\r\n')
        if (verbose):
            sys.stdout.write(header)
            sys.stdout.write('\r\n\r\n')
        sys.stdout.write(body)
    finally:
        s.close()
