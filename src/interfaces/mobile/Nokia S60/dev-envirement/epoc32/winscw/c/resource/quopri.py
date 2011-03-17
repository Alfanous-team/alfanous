# Portions Copyright (c) 2005 Nokia Corporation 
#! /usr/bin/env python

"""Conversions to/from quoted-printable transport encoding as per RFC 1521."""

# (Dec 1991 version).

__all__ = ["encode", "decode", "encodestring", "decodestring"]

ESCAPE = '='
MAXLINESIZE = 76
HEX = '0123456789ABCDEF'
EMPTYSTRING = ''

try:
    from binascii import a2b_qp, b2a_qp
except:
    a2b_qp = None
    b2a_qp = None


def needsquoting(c, quotetabs, header):
    if c in ' \t':
        return quotetabs
    if c == '_':
        return header
    return c == ESCAPE or not (' ' <= c <= '~')

def quote(c):
    i = ord(c)
    return ESCAPE + HEX[i//16] + HEX[i%16]



def encode(input, output, quotetabs, header = 0):
    if b2a_qp is not None:
        data = input.read()
        odata = b2a_qp(data, quotetabs = quotetabs, header = header)
        output.write(odata)
        return

    def write(s, output=output, lineEnd='\n'):
        if s and s[-1:] in ' \t':
            output.write(s[:-1] + quote(s[-1]) + lineEnd)
        elif s == '.':
            output.write(quote(s) + lineEnd)
        else:
            output.write(s + lineEnd)

    prevline = None
    while 1:
        line = input.readline()
        if not line:
            break
        outline = []
        stripped = ''
        if line[-1:] == '\n':
            line = line[:-1]
            stripped = '\n'
        for c in line:
            if needsquoting(c, quotetabs, header):
                c = quote(c)
            if header and c == ' ':
                outline.append('_')
            else:
                outline.append(c)
        if prevline is not None:
            write(prevline)
        thisline = EMPTYSTRING.join(outline)
        while len(thisline) > MAXLINESIZE:
            write(thisline[:MAXLINESIZE-1], lineEnd='=\n')
            thisline = thisline[MAXLINESIZE-1:]
        prevline = thisline
    if prevline is not None:
        write(prevline, lineEnd=stripped)

def encodestring(s, quotetabs = 0, header = 0):
    if b2a_qp is not None:
        return b2a_qp(s, quotetabs = quotetabs, header = header)
    from cStringIO import StringIO
    infp = StringIO(s)
    outfp = StringIO()
    encode(infp, outfp, quotetabs, header)
    return outfp.getvalue()



def decode(input, output, header = 0):
    if a2b_qp is not None:
        data = input.read()
        odata = a2b_qp(data, header = header)
        output.write(odata)
        return

    new = ''
    while 1:
        line = input.readline()
        if not line: break
        i, n = 0, len(line)
        if n > 0 and line[n-1] == '\n':
            partial = 0; n = n-1
            # Strip trailing whitespace
            while n > 0 and line[n-1] in " \t\r":
                n = n-1
        else:
            partial = 1
        while i < n:
            c = line[i]
            if c == '_' and header:
                new = new + ' '; i = i+1
            elif c != ESCAPE:
                new = new + c; i = i+1
            elif i+1 == n and not partial:
                partial = 1; break
            elif i+1 < n and line[i+1] == ESCAPE:
                new = new + ESCAPE; i = i+2
            elif i+2 < n and ishex(line[i+1]) and ishex(line[i+2]):
                new = new + chr(unhex(line[i+1:i+3])); i = i+3
            else: # Bad escape sequence -- leave it in
                new = new + c; i = i+1
        if not partial:
            output.write(new + '\n')
            new = ''
    if new:
        output.write(new)

def decodestring(s, header = 0):
    if a2b_qp is not None:
        return a2b_qp(s, header = header)
    from cStringIO import StringIO
    infp = StringIO(s)
    outfp = StringIO()
    decode(infp, outfp, header = header)
    return outfp.getvalue()

def ishex(c):
    return '0' <= c <= '9' or 'a' <= c <= 'f' or 'A' <= c <= 'F'

def unhex(s):
    bits = 0
    for c in s:
        if '0' <= c <= '9':
            i = ord('0')
        elif 'a' <= c <= 'f':
            i = ord('a')-10
        elif 'A' <= c <= 'F':
            i = ord('A')-10
        else:
            break
        bits = bits*16 + (ord(c) - i)
    return bits

if __name__ == '__main__':
    pass
