# Portions Copyright (c) 2005 Nokia Corporation 
"""Wichman-Hill random number generator."""

class whrandom:
    def __init__(self, x = 0, y = 0, z = 0):
        self.seed(x, y, z)

    def seed(self, x = 0, y = 0, z = 0):
        if not type(x) == type(y) == type(z) == type(0):
            raise TypeError, 'seeds must be integers'
        if not (0 <= x < 256 and 0 <= y < 256 and 0 <= z < 256):
            raise ValueError, 'seeds must be in range(0, 256)'
        if 0 == x == y == z:
            import time
            t = long(time.time() * 256)
            t = int((t&0xffffff) ^ (t>>24))
            t, x = divmod(t, 256)
            t, y = divmod(t, 256)
            t, z = divmod(t, 256)
        self._seed = (x or 1, y or 1, z or 1)

    def random(self):
        # This part is thread-unsafe:
        # BEGIN CRITICAL SECTION
        x, y, z = self._seed
        #
        x = (171 * x) % 30269
        y = (172 * y) % 30307
        z = (170 * z) % 30323
        #
        self._seed = x, y, z
        # END CRITICAL SECTION
        #
        return (x/30269.0 + y/30307.0 + z/30323.0) % 1.0

    def uniform(self, a, b):
        return a + (b-a) * self.random()

    def randint(self, a, b):
        return self.randrange(a, b+1)

    def choice(self, seq):
        return seq[int(self.random() * len(seq))]

    def randrange(self, start, stop=None, step=1, int=int, default=None):
        istart = int(start)
        if istart != start:
            raise ValueError, "non-integer arg 1 for randrange()"
        if stop is default:
            if istart > 0:
                return int(self.random() * istart)
            raise ValueError, "empty range for randrange()"
        istop = int(stop)
        if istop != stop:
            raise ValueError, "non-integer stop for randrange()"
        if step == 1:
            if istart < istop:
                return istart + int(self.random() *
                                   (istop - istart))
            raise ValueError, "empty range for randrange()"
        istep = int(step)
        if istep != step:
            raise ValueError, "non-integer step for randrange()"
        if istep > 0:
            n = (istop - istart + istep - 1) / istep
        elif istep < 0:
            n = (istop - istart + istep + 1) / istep
        else:
            raise ValueError, "zero step for randrange()"

        if n <= 0:
            raise ValueError, "empty range for randrange()"
        return istart + istep*int(self.random() * n)


# Initialize from the current time
_inst = whrandom()
seed = _inst.seed
random = _inst.random
uniform = _inst.uniform
randint = _inst.randint
choice = _inst.choice
randrange = _inst.randrange
