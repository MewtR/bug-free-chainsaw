#!/usr/bin/python3
import argparse
import libhttpc
import re

def commandDescriptions():
   return """
The commands are: 
   get           executes a HTTP GET request and prints the response. 
   post          executes a HTTP POST request and prints the response. 
   help          print this help screen.
"""

parser = argparse.ArgumentParser(prog='httpc', usage='httpc command [arguments]', description='httpc is a curl like application but supports HTTP protocol only.', formatter_class=argparse.RawTextHelpFormatter, epilog=commandDescriptions())
#parser.add_argument('command', default='help', nargs='?', choices=['help', 'get', 'post'], help=argparse.SUPPRESS)
subparsers = parser.add_subparsers(dest='command', help=argparse.SUPPRESS)

# create the parser for the get command
parser_get = subparsers.add_parser('get', prog='httpc get', add_help=False)
parser_get.add_argument('-v','--verbose', action='store_true', help='Prints the detail of the response such as protocol, status, and headers.')

#append option to allow the flage multiple times
#metavar changes the description of the argument for the flag
parser_get.add_argument('-h',  action='append', metavar='key:value',help='Associates headers to HTTP Request with the format \'key:value\'.')
parser_get.add_argument('URL')

# create the parser for the post command
parser_post = subparsers.add_parser('post', prog='httpc post', add_help=False)
parser_post.add_argument('-v','--verbose', action='store_true', help='Prints the detail of the response such as protocol, status, and headers.')
parser_post.add_argument('-h', action='append', metavar='key:value',help='Associates headers to HTTP Request with the format \'key:value\'.')
parser_post.add_argument('URL')

#Mutually exclusive group for post -d and -f options
post_group = parser_post.add_mutually_exclusive_group()
post_group.add_argument('-d', metavar='inline-data', help='Associates an inline data to the body HTTP POST request.')
post_group.add_argument('-f', metavar='file', help='Associates the content of a file to the body HTTP POST request.')

# create the parser for the help command
parser_help = subparsers.add_parser('help', help=argparse.SUPPRESS)
parser_help.add_argument('method', choices=['get','post',''], default='', nargs='?')


args = parser.parse_args()
#print (args)
if args.command == 'help':
    if args.method == 'get':
        parser_get.print_help()
    elif args.method == 'post':
        parser_post.print_help()
    else:
        parser.print_help()
if hasattr(args, 'URL'):
    #Match http(s) 0 or 1 times then match www 0 or 1 times
    #then match any char except : or / one or more times
    #then match one or 0 / followed by any char 0 or more times (match path group once or 0 times at end of string)
    regexp = '(?:https?://)?(?P<www>w{3}\.)?(?P<host>[^:/ ]+).?/?(?P<path>.*)?$'
    host = re.search(regexp, args.URL).group('host')
    path = re.search(regexp, args.URL).group('path')
    if args.command == 'get':
    #print (args.h[0].__class__)
        libhttpc.makeRequest(host, 'GET /'+path, args.verbose, args.h)
    #print ("GET used")
    #parser_get.print_help()
    elif args.command == 'post':
        try:
            with open(args.f, 'r') as myfile:
                data=myfile.read()
        except:
            data = args.d
        libhttpc.makeRequest(host, 'POST /'+path, args.verbose, args.h, data)
    #parser_post.print_help()
else:
    #print ("Exception caught")
    parser.print_help()
