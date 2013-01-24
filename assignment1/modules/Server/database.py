# ------------------------------------------------------------------------------
# Distributed Systems (TDDD25)
# ------------------------------------------------------------------------------
# Author: Sergiu Rafiliu (sergiu.rafiliu@liu.se)
# Modified: 01 December 2012
#
# Copyright 2012 Linkoping University
# ------------------------------------------------------------------------------

"""Implementation of a simple database class."""

import random


class Database(object):
    """Class containing a database implementation."""

    def __init__(self, db_file):
        self.db_file = db_file
        self.rand = random.Random()
        self.rand.seed()
        self.fortunes = []

        with open(db_file) as f:
            fortune = ''
            for line in f:
                if line[0] == '%':
                    self.fortunes.append(fortune)
                    fortune = ''
                else:
                    fortune = ''.join([fortune, line])

    def read(self):
        """Read a random location in the database."""
        try:
            return self.rand.choice(self.fortunes)
        except IndexError:
            return ''

    def write(self, fortune):
        """Write a new fortune to the database."""
        with open(self.db_file, 'a') as f:
            f.write(fortune)
            f.write('\n%\n')
