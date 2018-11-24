import socket
import argparse
import sys
import re
import threading
import os
import ipaddress
from packet import Packet

expected_sequence_number = 0
sequence_number_to_send = 1

def run_server(host, port, directory = './', verbose = False):
    global expected_sequence_number 
    global sequence_number_to_send 
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        conn.bind((host, port))
        print('Listening on port '+ str(port))
        while True:
            #Three way start
            data, sender = conn.recvfrom(1024)
            three_way(conn, sender, data, 5)
            conn.settimeout(None)
            #Actual data
            data, sender = conn.recvfrom(1024)
            handle_client(conn, sender, directory, verbose, data)
            expected_sequence_number = 0
            sequence_number_to_send = 1
    finally:
        conn.close()
        
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
    return headers
    #return headers.encode("utf-8")

def handle_client(conn, sender, directory, verbose, data):
    global expected_sequence_number
    global sequence_number_to_send 
    try:
        p = Packet.from_bytes(data)
        #Extract client address and port from packet received
        #When router receives packet changes destination address
        #to source address so receiver can reply
        peer_ip = p.peer_ip_addr
        peer_port = p.peer_port
        received_data = p.payload.decode("utf-8")
        if (verbose):
            print (received_data)
        if 'GET' in received_data:
            response = do_GET(received_data, conn, directory, verbose)
        elif 'POST' in received_data:
            response = do_POST(received_data, conn, directory, verbose)
        else:
            response = 'Bad Request'
        if 'access' in response:
            response = generate_headers(403)+response
        elif 'exist' in response:
            response = generate_headers(404)+response+'\r\n'
        elif 'Request' in response:
            response = generate_headers(400)+response+'\r\n'
        elif 'Unable' in response:
            response = generate_headers(500)+response+'\r\n'
        else:
            response = generate_headers(200)+response+'\r\n'
        while True:
            try:
                send_packet(conn, peer_ip,peer_port, 4, sequence_number_to_send, response, sender)
                conn.settimeout(5)
                #Three way end
                tempdata, sender = conn.recvfrom(1024)
                z = Packet.from_bytes(tempdata)
                if (z.seq_num == 4): #Means client did not get response
                    print ('Resending response')
                    continue # Send it again
                expected_sequence_number = 0
                sequence_number_to_send = 1
                three_way(conn, sender, tempdata, 5)
                conn.settimeout(None)
                expected_sequence_number = 0
                sequence_number_to_send = 1
                break
            except socket.timeout:
                pass
    except Exception as e:
        print("Error: ", e)

def do_POST(received_data, conn, directory, verbose):
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

def do_GET(received_data, conn, directory, verbose):
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


def send_packet(s, peer_ip, port, packet_type, seq_num, message, sender):
    p = Packet(packet_type=packet_type,
                   seq_num=seq_num,
                   peer_ip_addr=peer_ip,
                   peer_port=port,
                   payload=message.encode("utf-8"))
    s.sendto(p.to_bytes(), sender)


def three_way(s, sender, data, timeout):
    global expected_sequence_number 
    global sequence_number_to_send 
    p = Packet.from_bytes(data)
    peer_ip = p.peer_ip_addr
    peer_port = p.peer_port
    if (p.packet_type != 0):
        print('Router: ', sender)
        print('Packet: ', p)
        print('Payload: ' + p.payload.decode("utf-8"))
        print ("Need to initiate communcation with three_way!")
        return
    if (p.seq_num != expected_sequence_number):
        print ("Wrong packet received")
        print('sequence_number_to_send : ', sequence_number_to_send)
        print('expected_sequence_number : ', expected_sequence_number)
        return
    expected_sequence_number =+2
    print('Router: ', sender)
    print('Packet: ', p)
    print('Payload: ' + p.payload.decode("utf-8"))
    while True:
        try:
            #Send SYN-ACK
            send_packet(s, peer_ip, peer_port, 1, sequence_number_to_send, '', sender)
            print('Sending packet')
            s.settimeout(timeout)
            response, sender = s.recvfrom(1024)
            p = Packet.from_bytes(response)
            if (p.packet_type == 2 and p.seq_num == expected_sequence_number):
                # Received ACK -> done
                print('Three way handshake complete !')
                sequence_number_to_send +=2
                return
            else:
                continue
                print('Reject this packet somehow')
        except socket.timeout:
            pass
            #print('No response after {}s'.format(timeout))
