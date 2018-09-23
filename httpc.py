import argparse
import libhttpc

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
parser_get.add_argument('-h',nargs=1, metavar='key:value',help='Associates headers to HTTP Request with the format \'key:value\'.')
parser_get.add_argument('URL')

# create the parser for the post command
parser_post = subparsers.add_parser('post', prog='httpc post')
parser_post.add_argument('--opt3', action='store_true')
parser_post.add_argument('--opt4', action='store_true')

# create the parser for the help command
parser_help = subparsers.add_parser('help', help=argparse.SUPPRESS)
parser_help.add_argument('method', choices=['get','post',''], default='', nargs='?')


args = parser.parse_args()
print (args)
if args.command == 'help':
    if args.method == 'get':
        parser_get.print_help()
    elif args.method == 'post':
        parser_post.print_help()
    else:
        parser.print_help()
elif args.command == 'get':
    print ("GET used")
    #parser_get.print_help()
elif args.command == 'post':
    print ("POST used")
    #parser_post.print_help()

