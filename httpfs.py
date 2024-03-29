#!/usr/bin/python3
import argparse
import libhttpfs


#parser = argparse.ArgumentParser(prog='httpfs', description='httpfs is a simple file server.', formatter_class=argparse.RawTextHelpFormatter)
parser = argparse.ArgumentParser(prog='httpfs', description='httpfs is a simple file server.')
parser.add_argument('-v','--verbose', action='store_true', help='Prints debugging messages.')
parser.add_argument('-d', '--directory',type=str, default='./', help='Specifies the directory that the server will use to read/write requested files. Default is the current directory when launching the application.')
parser.add_argument('-p', '--port', type=int, default=8080, help='Specifies the port number that the server will listen and serve at.')

args = parser.parse_args()

print (args)
libhttpfs.run_server('127.0.0.1', args.port, args.directory, args.verbose)

