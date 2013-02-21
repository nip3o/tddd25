# ------------------------------------------------------------------------------
# Distributed Systems (TDDD25)
# ------------------------------------------------------------------------------
# Author: Sergiu Rafiliu (sergiu.rafiliu@liu.se)
# Modified: 01 December 2012
#
# Copyright 2012 Linkoping University
# ------------------------------------------------------------------------------

"""Class for implementing distributed mutual exclusion."""

import time

NO_TOKEN = 0
TOKEN_PRESENT = 1
TOKEN_HELD = 2


class DistributedLock(object):
    """ Implementation of distributed mutual exclusion for a list of peers.

        For simplicity, in this lock implementation we do not deal with cases
        where the peer holding the token dies without passing the token to
        someone else first.
    """

    def __init__(self, owner, peer_list):
        self.peer_list = peer_list
        self.owner = owner
        self.time = 0
        self.token = {}
        self.request = {}
        self.state = NO_TOKEN

    # Public methods

    def initialize(self):
        """ Initialize the state, request, and token vectors of the lock.

            Since the state of the distributed lock is linked with the
            number of peers among which the lock is distributed, we can
            utilize the lock of peer_list to protect the state of the
            distributed lock (strongly suggested).

            NOTE: peer_list must already be populated.
        """
        self.peer_list.lock.acquire()
        try:
            if len(self.peer_list.peers) == 0:
                self.state = TOKEN_PRESENT

            else:
                self.state = NO_TOKEN

            for peer in self.peer_list.peers:
                self.token[peer] = 0
                self.request[peer] = 0
        finally:
            self.peer_list.lock.release()

    def destroy(self):
        """ The object is being destroyed. If we have the token, we must
            give it to someone else.
        """
        if self.state in (TOKEN_HELD, TOKEN_PRESENT):
            pid = self.peer_list.peers.values()[0]
            self.peer_list.peer(pid).obtain_token()

    def register_peer(self, pid):
        """Called when a new peer joins the system."""
        self.peer_list.lock.acquire()

        try:
            self.request[pid] = 0

            if self.state in (TOKEN_HELD, TOKEN_PRESENT):
                self.token[pid] = 0

        finally:
            self.peer_list.lock.release()

    def unregister_peer(self, pid):
        """Called when a peer leaves the system."""
        self.peer_list.lock.acquire()

        try:
            del self.request[pid]

            if self.state in (TOKEN_HELD, TOKEN_PRESENT):
                del self.token[pid]

        finally:
            self.peer_list.lock.release()

    def acquire(self):
        """Called when this object tries to acquire the lock."""
        print "Trying to acquire the lock..."
        self.peer_list.lock.acquire()

        self.time += 1

        try:
            if self.state == NO_TOKEN:
                for pid, peer in self.peer_list.peers.iteritems():
                    peer.request_token(self.time, self.owner.id)

                self.peer_list.lock.release()

                while self.state == NO_TOKEN:
                    time.sleep(0.01)
            else:
                self.state = TOKEN_HELD

        finally:
            self.peer_list.lock.release()

    def _pass_token(self):
        def do_release():
            if self.request[pid] > self.token:
                self.state = NO_TOKEN
                self.token[pid] = self.time
                self.time += 1
                self.peer_list.peers[pid].obtain_token(self.token)
                return True

        for pid in [p for p in self.peer_list.peers if p > self.owner.id]:
            if do_release():
                return

        for pid in [p for p in self.peer_list.peers if p < self.owner.id]:
            if do_release():
                return

    def release(self):
        """Called when this object releases the lock."""
        print "Releasing the lock..."
        assert self.state == TOKEN_HELD

        self.state == TOKEN_PRESENT
        self.peer_list.lock.acquire()

        try:
            self._pass_token()
        finally:
            self.peer_list.lock.release()

    def request_token(self, time, pid):
        """Called when some other object requests the token from us."""
        self.peer_list.lock.acquire()

        try:
            if self.request[pid] < time:
                self.request[pid] = time

            if self.state == TOKEN_PRESENT:
                self._pass_token()

        finally:
            self.peer_list.lock.release()

    def obtain_token(self, token):
        """Called when some other object is giving us the token."""
        print "Receiving the token..."
        self.peer_list.lock.acquire()

        try:
            self.token = token
            self.state = TOKEN_PRESENT
            self.time = token[self.owner.id] + 1

        finally:
            self.peer_list.lock.release()

    def display_status(self):
        self.peer_list.lock.acquire()
        try:
            nt = self.state == NO_TOKEN
            tp = self.state == TOKEN_PRESENT
            th = self.state == TOKEN_HELD
            print "State   :: no token      : {0}".format(nt)
            print "           token present : {0}".format(tp)
            print "           token held    : {0}".format(th)
            print "Request :: {0}".format(self.request)
            print "Token   :: {0}".format(self.token)
            print "Time    :: {0}".format(self.time)
        finally:
            self.peer_list.lock.release()
