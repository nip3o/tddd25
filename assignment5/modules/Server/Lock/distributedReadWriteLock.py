# ------------------------------------------------------------------------------
# Distributed Systems (TDDD25)
# ------------------------------------------------------------------------------
# Author: Sergiu Rafiliu (sergiu.rafiliu@liu.se)
# Modified: 01 December 2012
#
# Copyright 2012 Linkoping University
# ------------------------------------------------------------------------------

"""Class implementing a distributed version of ReadWriteLock."""

import threading
from readWriteLock import ReadWriteLock
from distributedLock import DistributedLock


class DistributedReadWriteLock(ReadWriteLock):
    """Distributed version of ReadWriteLock."""

    def __init__(self, distributed_lock):
        super(DistributedReadWriteLock, self).__init__()
        # Create a distributed lock
        self.distributed_lock = distributed_lock

    # Public methods

    def write_acquire(self):
        """ Override the write_acquire method to include obtaining access
            to the rest of the peers.
        """
        super(DistributedReadWriteLock, self).write_acquire()
        self.distributed_lock.acquire()

    def write_release(self):
        """ Override the write_release method to include releasing access
            to the rest of the peers.
        """
        self.distributed_lock.release()
        super(DistributedReadWriteLock, self).write_release()
