import socket
import argparse
import sys
import re
import ipaddress
from packet import Packet

def send_packet(s, peer_ip, port, packet_type, seq_num, message, router_addr='localhost', router_port=3000):
    p = Packet(packet_type=packet_type,
                   seq_num=seq_num,
                   peer_ip_addr=peer_ip,
                   peer_port=port,
                   payload=message.encode("utf-8"))
    s.sendto(p.to_bytes(), (router_addr, router_port))

def three_way(s, peer_ip, port, timeout, router_addr, router_port):
    #Send SYN -> packet type is 0, no message
    packet_type = 0
    seq_num = 0
    while True:
        try:
            send_packet(s, peer_ip, port, packet_type, seq_num, '', router_addr, router_port)
            if (packet_type == 2 ):
                print('Three way handshake complete ! Communcation can start !')
                break # Just sent an ACK -> last packet in handshake -> break
            s.settimeout(timeout)
            response, sender = s.recvfrom(1024)
            p = Packet.from_bytes(response)
            print('Router: ', sender)
            print('Packet: ', p)
            print('Payload: ' + p.payload.decode("utf-8"))
            if (p.packet_type == 1):
                packet_type = 2 # Received SYN-ACK so set packet type to ACK
                continue
        except socket.timeout:
            print('No response after {}s'.format(timeout))


def makeRequest(host, port, path, verbose, headers=[], router_addr='localhost', router_port=3000, data=''):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    peer_ip = ipaddress.ip_address(socket.gethostbyname(host))
    timeout = 5
    three_way(s, peer_ip, port, timeout, router_addr, router_port)
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
        #Send data packet: type 4
        send_packet(s, peer_ip, port, 4, 1, message, router_addr, router_port)
        s.settimeout(timeout)
        print('Waiting for a response')
        response, sender = s.recvfrom(1024)
        p = Packet.from_bytes(response)
        print('Router: ', sender)
        print('Packet: ', p)
        print('Payload: ' + p.payload.decode("utf-8"))
    except socket.timeout:
        print('No response after {}s'.format(timeout))
    finally:
        s.close()
