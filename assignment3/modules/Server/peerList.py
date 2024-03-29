# ------------------------------------------------------------------------------
# Distributed Systems (TDDD25)
# ------------------------------------------------------------------------------
# Author: Sergiu Rafiliu (sergiu.rafiliu@liu.se)
# Modified: 01 December 2012
#
# Copyright 2012 Linkoping University
# ------------------------------------------------------------------------------

"""Package for handling a list of objects of the same type as a given one."""

import threading
from Common import orb

class PeerList(object):
    """Class that builds a list of objects of the same type as this one."""

    def __init__(self, owner):
        self.owner = owner
        self.lock = threading.Condition()
        self.peers = {}

    # Public methods

    def initialize(self):
        """ Populates the list of existing peers and registers the current
            peer at each of the discovered peers.

            It only adds the peers with lower ids than this one or else
            deadlocks may occur. This method must be called after the owner
            object has been registered with the name service.
        """
        self.lock.acquire()
        try:
            name_service_peers = self.owner.name_service.require_all(self.owner.type)

            for pid, paddr in name_service_peers:
                if pid < self.owner.id:
                    self.register_peer(pid, paddr)

            for _, peer in self.peers.iteritems():
                peer.register_peer(self.owner.id, self.owner.address)

        finally:
            self.lock.release()

    def destroy(self):
        """Unregister this peer from all others in the list."""
        self.lock.acquire()
        try:
            for pid in self.peers:
                self.peer(pid).unregister_peer(self.owner.id)
        finally:
            self.lock.release()

    def register_peer(self, pid, paddr):
        """Register a new peer joining the network."""
        # Synchronize access to the peer list as several peers might call
        # this method in parallel.
        self.lock.acquire()
        try:
            self.peers[pid] = orb.Stub(paddr)
            print "Peer {0} has joined the system.".format(pid)
        finally:
            self.lock.release()

    def unregister_peer(self, pid):
        """Unregister a peer leaving the network."""
        # Synchronize access to the peer list as several peers might call
        # this method in parallel.
        self.lock.acquire()
        try:
            if pid in self.peers:
                    del self.peers[pid]
                    print "Peer {0} has left the system.".format(pid)
            else:   raise Exception("No peer with id: '{0}'".format(pid))
        finally:
            self.lock.release()

    def display_peers(self):
        """Display all the peers in the list."""
        self.lock.acquire()
        try:
            pids = self.peers.keys()
            pids.sort()
            print "List of peers of type '{0}':".format(self.owner.type)
            for pid in pids:
                print "    id: {0:>2}, address: {1}".format(pid, self.peers[pid].address)
        finally:
            self.lock.release()

    def peer(self, pid):
        """Return the object with the given id."""
        self.lock.acquire()
        try:
            return self.peers[pid]
        finally:
            self.lock.release()

    def get_peers(self):
        """Return all registered objects."""
        self.lock.acquire()
        try:
            return self.peers
        finally:
            self.lock.release()
