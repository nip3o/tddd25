#!/usr/bin/env python

# ------------------------------------------------------------------------------
# Distributed Systems (TDDD25)
# ------------------------------------------------------------------------------
# Author: Sergiu Rafiliu (sergiu.rafiliu@liu.se)
# Modified: 01 December 2012
#
# Copyright 2012 Linkoping University
# ------------------------------------------------------------------------------

"""Client reader/writer for a fortune database."""

import sys
import socket
import json
from optparse import OptionParser

# ------------------------------------------------------------------------------
# Initialize and read the command line arguments
# ------------------------------------------------------------------------------

usage = """Usage: client.py [options] server_address:server_port"""
description = """
    Client for a fortune database. It reads a random fortune from the database.
"""
arg_parser = OptionParser(usage=usage, description=description)
arg_parser.add_option("-w", "--write", metavar="FORTUNE", dest="fortune",
    help="Write a new fortune to the database.")
arg_parser.add_option("-i", "--interactive",
    action="store_true", dest="interactive", default=False,
    help="Interactive session with the fortune database.")
opts, args = arg_parser.parse_args()

server_address = None
if len(args) < 1:
    raise Exception("Missing server address argument on the command line.")
else:
    addr = args[0].split(":")
    if len(addr) == 2 and addr[1].isdigit():
        server_address = (addr[0], int(addr[1]))
    else:
        raise Exception("Incorrect server address.")

# ------------------------------------------------------------------------------
# Auxiliary classes
# ------------------------------------------------------------------------------


class ComunicationError(Exception):
    pass


class DatabaseProxy(object):
    """Class that simulates the behavior of the database class."""

    def __init__(self, server_address):
        self.address = server_address

    # Public methods

    def read(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.address[0], self.address[1]))

            read_command = ''.join((json.dumps({'method': 'read', 'params': ''}), '\n'))
            s.send(read_command)

            buf = ''
            part = ''
            while True:
                part = s.recv(4096)
                if not part:
                    break

                buf = ''.join((buf, part))
                part = ''

            result = json.loads(buf).get('result')

            if not result:
                result = json.loads(buf).get('error')

        except socket.error as e:
            print e

        finally:
            s.close()

        return result

    def write(self, fortune):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.address[0], self.address[1]))

            write_command = ''.join((json.dumps({'method': 'write', 'params': fortune}), '\n'))
            total_sent = 0
            while total_sent < len(write_command):
                sent = s.send(write_command[total_sent:])

                if sent == 0:
                    raise RuntimeError("socket connection broken")

                total_sent += sent

            buf = s.recv(4096)

            result = json.loads(buf).get('error')

            if result:
                print result
            else:
                print 'Write successful'

        except socket.error as e:
            print e

        finally:
            s.close()
# ------------------------------------------------------------------------------
# The main program
# ------------------------------------------------------------------------------

# Create the database object.
db = DatabaseProxy(server_address)

if not opts.interactive:
    # Run in the normal mode.
    if opts.fortune is not None:
        db.write(opts.fortune)
    else:
        print db.read()

else:
    # Run in the interactive mode.
    def menu():
        print (
            "Choose one of the following commands:\n"
            "    r            ::  read a random fortune from the database,\n"
            "    w <FORTUNE>  ::  write a new fortune into the database,\n"
            "    h            ::  print this menu,\n"
            "    q            ::  exit.")

    command = ""
    menu()
    while command != "q":
        sys.stdout.write("Command> ")
        command = raw_input()
        if command == "r":
            print db.read()
        elif len(command) > 1 and command[0] == "w" and command[1] in [" ", "\t"]:
            db.write(command[2:].strip())
        elif command == "h":
            menu()
