import argparse
import libhttpc

parser = argparse.ArgumentParser(prog='httpc', usage='httpc command [arguments]', description='httpc is a curl like application but supports HTTP protocol only.')
parser.add_argument('command', default='help', nargs='?', choices=['help', 'get', 'post'])
args = parser.parse_args()
if args.command == 'help':
    parser.print_help()
elif args.command == 'get':
    print ("GET used")

