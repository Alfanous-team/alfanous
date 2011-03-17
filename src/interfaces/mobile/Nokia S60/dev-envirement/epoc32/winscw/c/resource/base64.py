# Portions Copyright (c) 2005 Nokia Corporation 
#! /usr/bin/env python

"""Conversions to/from base64 transport encoding as per RFC-1521."""

# Modified 04-Oct-95 by Jack to use binascii module

import binascii

__all__ = ["encode","decode","encodestring","decodestring"]

MAXLINESIZE = 76 # Excluding the CRLF
MAXBINSIZE = (MAXLINESIZE//4)*3

def encode(input, output):
    while 1:
        s = input.read(MAXBINSIZE)
        if not s: break
        while len(s) < MAXBINSIZE:
            ns = input.read(MAXBINSIZE-len(s))
            if not ns: break
            s = s + ns
        line = binascii.b2a_base64(s)
        output.write(line)

def decode(input, output):
    while 1:
        line = input.readline()
        if not line: break
        s = binascii.a2b_base64(line)
        output.write(s)

def encodestring(s):
    pieces = []
    for i in range(0, len(s), MAXBINSIZE):
        chunk = s[i : i + MAXBINSIZE]
        pieces.append(binascii.b2a_base64(chunk))
    return "".join(pieces)

def decodestring(s):
    return binascii.a2b_base64(s)

def test1():
    s0 = "Aladdin:open sesame"
    s1 = encodestring(s0)
    s2 = decodestring(s1)
    print s0, `s1`, s2

if __name__ == '__main__':
    test1()
