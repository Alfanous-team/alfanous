# Portions Copyright (c) 2005 Nokia Corporation 
"""Various tools used by MIME-reading or MIME-writing programs."""

import rfc822

__all__ = ["Message","encode","decode","copyliteral","copybinary"]

class Message(rfc822.Message):
    """A derived class of rfc822.Message that knows about MIME headers and
    contains some hooks for decoding encoded and multipart messages."""

    def __init__(self, fp, seekable = 1):
        rfc822.Message.__init__(self, fp, seekable)
        self.encodingheader = \
                self.getheader('content-transfer-encoding')
        self.typeheader = \
                self.getheader('content-type')
        self.parsetype()
        self.parseplist()

    def parsetype(self):
        str = self.typeheader
        if str is None:
            str = 'text/plain'
        if ';' in str:
            i = str.index(';')
            self.plisttext = str[i:]
            str = str[:i]
        else:
            self.plisttext = ''
        fields = str.split('/')
        for i in range(len(fields)):
            fields[i] = fields[i].strip().lower()
        self.type = '/'.join(fields)
        self.maintype = fields[0]
        self.subtype = '/'.join(fields[1:])

    def parseplist(self):
        str = self.plisttext
        self.plist = []
        while str[:1] == ';':
            str = str[1:]
            if ';' in str:
                # XXX Should parse quotes!
                end = str.index(';')
            else:
                end = len(str)
            f = str[:end]
            if '=' in f:
                i = f.index('=')
                f = f[:i].strip().lower() + \
                        '=' + f[i+1:].strip()
            self.plist.append(f.strip())
            str = str[end:]

    def getplist(self):
        return self.plist

    def getparam(self, name):
        name = name.lower() + '='
        n = len(name)
        for p in self.plist:
            if p[:n] == name:
                return rfc822.unquote(p[n:])
        return None

    def getparamnames(self):
        result = []
        for p in self.plist:
            i = p.find('=')
            if i >= 0:
                result.append(p[:i].lower())
        return result

    def getencoding(self):
        if self.encodingheader is None:
            return '7bit'
        return self.encodingheader.lower()

    def gettype(self):
        return self.type

    def getmaintype(self):
        return self.maintype

    def getsubtype(self):
        return self.subtype

def decode(input, output, encoding):
    if encoding == 'base64':
        import base64
        return base64.decode(input, output)
    if encoding == 'quoted-printable':
        import quopri
        return quopri.decode(input, output)
    if encoding in ('uuencode', 'x-uuencode', 'uue', 'x-uue'):
        import uu
        return uu.decode(input, output)
    if encoding in ('7bit', '8bit'):
        return output.write(input.read())
    else:
        raise ValueError, \
              'unknown Content-Transfer-Encoding: %s' % encoding

def encode(input, output, encoding):
    if encoding == 'base64':
        import base64
        return base64.encode(input, output)
    if encoding == 'quoted-printable':
        import quopri
        return quopri.encode(input, output, 0)
    if encoding in ('uuencode', 'x-uuencode', 'uue', 'x-uue'):
        import uu
        return uu.encode(input, output)
    if encoding in ('7bit', '8bit'):
        return output.write(input.read())
    else:
        raise ValueError, \
              'unknown Content-Transfer-Encoding: %s' % encoding

def copyliteral(input, output):
    while 1:
        line = input.readline()
        if not line: break
        output.write(line)

def copybinary(input, output):
    BUFSIZE = 8192
    while 1:
        line = input.read(BUFSIZE)
        if not line: break
        output.write(line)
