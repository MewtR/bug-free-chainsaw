import socket
import argparse
import sys
import re
import ipaddress
from packet import Packet

def makeRequest(host, port, path, verbose, headers=[], router_addr='localhost', router_port=3000, data=''):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    peer_ip = ipaddress.ip_address(socket.gethostbyname(host))
    timeout = 5
    try:
        message = path +' HTTP/1.0\r\n'
        message += 'Host: '+ host +'\r\n'
        message += 'Content-length: '+ str(len(data))+'\r\n'
        if headers:
            for h in headers:
                #was list because of nargs in h option
                message+= h+'\r\n'
        #End of message
        message+='\r\n'
        if 'POST' in message:
            if (data):
                message+=data
        p = Packet(packet_type=0,
                   seq_num=1,
                   peer_ip_addr=peer_ip,
                   peer_port=port,
                   payload=message.encode("utf-8"))
        s.sendto(p.to_bytes(), (router_addr, router_port))
        s.settimeout(timeout)
        print('Waiting for a response')
        response, sender = s.recvfrom(1024)
        p = Packet.from_bytes(response)
        print('Router: ', sender)
        print('Packet: ', p)
        print('Payload: ' + p.payload.decode("utf-8"))

    except socket.timeout:
        print('No response after {}s'.format(timeout))
        #response = recv_all(s)
        #response = response.decode("utf-8")
        #try:
        #    (header, body) = response.split('\r\n\r\n')
        #    if (verbose):
        #        sys.stdout.write(request+'\n')
        #        sys.stdout.write(header)
        #        sys.stdout.write('\r\n\r\n')
        #    sys.stdout.write(body)
        #except ValueError as e:
        #    sys.stdout.write(str(e))
        #    sys.stdout.write(response)
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
