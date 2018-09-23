import socket
import argparse
import sys

# When using telnet some sites require 'Host:'(httpbin.org) while others don't(google.ca)

host = 'httpbin.org'
port = 80

def get(host, path='/'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, 80))
        #request = 'GET /status/418 HTTP/1.0\r\nHost: httpbin.org\r\n\r\n'
        s.sendall('GET /status/418 HTTP/1.0\r\n'.encode("utf-8"))
        s.sendall(('Host: '+host+'\r\n\r\n').encode("utf-8"))
        #response = s.recv(len(request), socket.MSG_WAITALL)
        response = s.recv(4096, socket.MSG_WAITALL)
        response2 = s.recv(2)
        sys.stdout.write( response.decode("utf-8"))
    finally:
        s.close()
#get(host)
