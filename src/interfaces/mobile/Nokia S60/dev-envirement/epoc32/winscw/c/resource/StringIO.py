# Portions Copyright (c) 2005 Nokia Corporation 
"""File-like objects that read from or write to a string buffer."""
import types
try:
    from errno import EINVAL
except ImportError:
    EINVAL = 22

__all__ = ["StringIO"]

class StringIO:
    def __init__(self, buf = ''):
        if type(buf) not in types.StringTypes:
            buf = str(buf)
        self.buf = buf
        self.len = len(buf)
        self.buflist = []
        self.pos = 0
        self.closed = 0
        self.softspace = 0

    def __iter__(self):
        return iter(self.readline, '')

    def close(self):
        if not self.closed:
            self.closed = 1
            del self.buf, self.pos

    def isatty(self):
        if self.closed:
            raise ValueError, "I/O operation on closed file"
        return 0

    def seek(self, pos, mode = 0):
        if self.closed:
            raise ValueError, "I/O operation on closed file"
        if self.buflist:
            self.buf += ''.join(self.buflist)
            self.buflist = []
        if mode == 1:
            pos += self.pos
        elif mode == 2:
            pos += self.len
        self.pos = max(0, pos)

    def tell(self):
        if self.closed:
            raise ValueError, "I/O operation on closed file"
        return self.pos

    def read(self, n = -1):
        if self.closed:
            raise ValueError, "I/O operation on closed file"
        if self.buflist:
            self.buf += ''.join(self.buflist)
            self.buflist = []
        if n < 0:
            newpos = self.len
        else:
            newpos = min(self.pos+n, self.len)
        r = self.buf[self.pos:newpos]
        self.pos = newpos
        return r

    def readline(self, length=None):
        if self.closed:
            raise ValueError, "I/O operation on closed file"
        if self.buflist:
            self.buf += ''.join(self.buflist)
            self.buflist = []
        i = self.buf.find('\n', self.pos)
        if i < 0:
            newpos = self.len
        else:
            newpos = i+1
        if length is not None:
            if self.pos + length < newpos:
                newpos = self.pos + length
        r = self.buf[self.pos:newpos]
        self.pos = newpos
        return r

    def readlines(self, sizehint = 0):
        total = 0
        lines = []
        line = self.readline()
        while line:
            lines.append(line)
            total += len(line)
            if 0 < sizehint <= total:
                break
            line = self.readline()
        return lines

    def truncate(self, size=None):
        if self.closed:
            raise ValueError, "I/O operation on closed file"
        if size is None:
            size = self.pos
        elif size < 0:
            raise IOError(EINVAL, "Negative size not allowed")
        elif size < self.pos:
            self.pos = size
        self.buf = self.getvalue()[:size]

    def write(self, s):
        if self.closed:
            raise ValueError, "I/O operation on closed file"
        if not s: return
        # Force s to be a string or unicode
        if type(s) not in types.StringTypes:
            s = str(s)
        if self.pos > self.len:
            self.buflist.append('\0'*(self.pos - self.len))
            self.len = self.pos
        newpos = self.pos + len(s)
        if self.pos < self.len:
            if self.buflist:
                self.buf += ''.join(self.buflist)
                self.buflist = []
            self.buflist = [self.buf[:self.pos], s, self.buf[newpos:]]
            self.buf = ''
            if newpos > self.len:
                self.len = newpos
        else:
            self.buflist.append(s)
            self.len = newpos
        self.pos = newpos

    def writelines(self, list):
        self.write(''.join(list))

    def flush(self):
        if self.closed:
            raise ValueError, "I/O operation on closed file"

    def getvalue(self):
        if self.buflist:
            self.buf += ''.join(self.buflist)
            self.buflist = []
        return self.buf

def test():
    pass

if __name__ == '__main__':
    test()
