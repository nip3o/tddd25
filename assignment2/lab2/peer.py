#!/usr/bin/env python

# ------------------------------------------------------------------------------
# Distributed Systems (TDDD25)
# ------------------------------------------------------------------------------
# Author: Sergiu Rafiliu (sergiu.rafiliu@liu.se)
# Modified: 01 December 2012
#
# Copyright 2012 Linkoping University
# ------------------------------------------------------------------------------

""" A simple peer implementation.

    This implementation simply connects to the name service and asks for the
    list of peers.
"""

import sys
import random
import socket
from optparse import OptionParser

sys.path.append("../modules")
from Common import orb
from Common.nameServiceLocation import name_service_address
from Common.objectType import object_type

# ------------------------------------------------------------------------------
# Initialize and read the command line arguments
# ------------------------------------------------------------------------------

arg_parser = OptionParser()
arg_parser.add_option("-p", "--port", metavar="PORT", dest="port",
    help="Set the port to listen to. Must be in the range 40001 .. 50000."
           "The default value is chosen at random.")
arg_parser.add_option("-t", "--type", metavar="TYPE", dest="type",
    help="Set the type of the client.")
opts, args = arg_parser.parse_args()

if opts.port is None:
        rand = random.Random()
        rand.seed()
        local_port = rand.randint(1, 10000) + 40000
else:
    local_port = opts.port

if opts.type is None:
    client_type = object_type
else:
    client_type = opts.type

assert client_type != "object", "Change the object type to something unique!"


# ------------------------------------------------------------------------------
# Auxiliary classes
# ------------------------------------------------------------------------------

class Client(orb.Peer):
    """Chat client class."""

    def __init__(self, local_address, ns_address, cient_type):
        """Initialize the client."""
        orb.Peer.__init__(self, local_address, ns_address, client_type)
        orb.Peer.start(self)

    # Public methods

    def destroy(self):
        orb.Peer.destroy(self)

    def display_peers(self):
        """Display all the peers in the list."""
        peers = self.name_service.require_all(self.type)
        print "List of peers of type '{0}':".format(self.type)
        for pid, paddr in peers:
            print "    id: {0:>2}, address: {1}".format(pid, tuple(paddr))

# ------------------------------------------------------------------------------
# The main program
# ------------------------------------------------------------------------------

# Initialize the client object.
local_address = (socket.gethostname(), local_port)
p = Client(local_address, name_service_address, client_type)

print "This peer:"
print "    id: {0:>2}, address: {1}".format(p.id, p.address)

# Print the list of peers.
p.display_peers()

# Waiting for a key press.
sys.stdout.write("Waiting for a key press...")
raw_input()

# Kill our peer object.
p.destroy()
