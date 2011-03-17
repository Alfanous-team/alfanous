# Portions Copyright (c) 2005 Nokia Corporation 
""" codecs -- Python Codec Registry, API and helpers.


Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""#"

import struct, __builtin__

### Registry and builtin stateless codec functions

try:
    from _codecs import *
except ImportError, why:
    raise SystemError,\
          'Failed to load the builtin codecs: %s' % why

__all__ = ["register", "lookup", "open", "EncodedFile", "BOM", "BOM_BE",
           "BOM_LE", "BOM32_BE", "BOM32_LE", "BOM64_BE", "BOM64_LE"]

### Constants

#
# Byte Order Mark (BOM) and its possible values (BOM_BE, BOM_LE)
#
BOM = struct.pack('=H', 0xFEFF)
#
BOM_BE = BOM32_BE = '\376\377'
#       corresponds to Unicode U+FEFF in UTF-16 on big endian
#       platforms == ZERO WIDTH NO-BREAK SPACE
BOM_LE = BOM32_LE = '\377\376'
#       corresponds to Unicode U+FFFE in UTF-16 on little endian
#       platforms == defined as being an illegal Unicode character

#
# 64-bit Byte Order Marks
#
BOM64_BE = '\000\000\376\377'
#       corresponds to Unicode U+0000FEFF in UCS-4
BOM64_LE = '\377\376\000\000'
#       corresponds to Unicode U+0000FFFE in UCS-4


### Codec base classes (defining the API)

class Codec:

    def encode(self, input, errors='strict'):
        
        raise NotImplementedError

    def decode(self, input, errors='strict'):
        
        raise NotImplementedError

#
# The StreamWriter and StreamReader class provide generic working
# interfaces which can be used to implement new encoding submodules
# very easily. See encodings/utf_8.py for an example on how this is
# done.
#

class StreamWriter(Codec):

    def __init__(self, stream, errors='strict'):
        
        self.stream = stream
        self.errors = errors

    def write(self, object):
        
        data, consumed = self.encode(object, self.errors)
        self.stream.write(data)

    def writelines(self, list):
        
        self.write(''.join(list))

    def reset(self):
        
        pass

    def __getattr__(self, name,
                    getattr=getattr):
        
        return getattr(self.stream, name)

###

class StreamReader(Codec):

    def __init__(self, stream, errors='strict'):
        
        self.stream = stream
        self.errors = errors

    def read(self, size=-1):
        
        # Unsliced reading:
        if size < 0:
            return self.decode(self.stream.read(), self.errors)[0]

        # Sliced reading:
        read = self.stream.read
        decode = self.decode
        data = read(size)
        i = 0
        while 1:
            try:
                object, decodedbytes = decode(data, self.errors)
            except ValueError, why:
                # This method is slow but should work under pretty much
                # all conditions; at most 10 tries are made
                i = i + 1
                newdata = read(1)
                if not newdata or i > 10:
                    raise
                data = data + newdata
            else:
                return object

    def readline(self, size=None):
        
        if size is None:
            line = self.stream.readline()
        else:
            line = self.stream.readline(size)
        return self.decode(line, self.errors)[0]


    def readlines(self, sizehint=None):
        
        if sizehint is None:
            data = self.stream.read()
        else:
            data = self.stream.read(sizehint)
        return self.decode(data, self.errors)[0].splitlines(1)

    def reset(self):
        
        pass

    def __getattr__(self, name,
                    getattr=getattr):

        return getattr(self.stream, name)

###

class StreamReaderWriter:

    
    # Optional attributes set by the file wrappers below
    encoding = 'unknown'

    def __init__(self, stream, Reader, Writer, errors='strict'):
        
        self.stream = stream
        self.reader = Reader(stream, errors)
        self.writer = Writer(stream, errors)
        self.errors = errors

    def read(self, size=-1):

        return self.reader.read(size)

    def readline(self, size=None):

        return self.reader.readline(size)

    def readlines(self, sizehint=None):

        return self.reader.readlines(sizehint)

    def write(self, data):

        return self.writer.write(data)

    def writelines(self, list):

        return self.writer.writelines(list)

    def reset(self):

        self.reader.reset()
        self.writer.reset()

    def __getattr__(self, name,
                    getattr=getattr):
        
        return getattr(self.stream, name)

###

class StreamRecoder:

    
    # Optional attributes set by the file wrappers below
    data_encoding = 'unknown'
    file_encoding = 'unknown'

    def __init__(self, stream, encode, decode, Reader, Writer,
                 errors='strict'):
        
        self.stream = stream
        self.encode = encode
        self.decode = decode
        self.reader = Reader(stream, errors)
        self.writer = Writer(stream, errors)
        self.errors = errors

    def read(self, size=-1):

        data = self.reader.read(size)
        data, bytesencoded = self.encode(data, self.errors)
        return data

    def readline(self, size=None):

        if size is None:
            data = self.reader.readline()
        else:
            data = self.reader.readline(size)
        data, bytesencoded = self.encode(data, self.errors)
        return data

    def readlines(self, sizehint=None):

        if sizehint is None:
            data = self.reader.read()
        else:
            data = self.reader.read(sizehint)
        data, bytesencoded = self.encode(data, self.errors)
        return data.splitlines(1)

    def write(self, data):

        data, bytesdecoded = self.decode(data, self.errors)
        return self.writer.write(data)

    def writelines(self, list):

        data = ''.join(list)
        data, bytesdecoded = self.decode(data, self.errors)
        return self.writer.write(data)

    def reset(self):

        self.reader.reset()
        self.writer.reset()

    def __getattr__(self, name,
                    getattr=getattr):

        
        return getattr(self.stream, name)

### Shortcuts

def open(filename, mode='rb', encoding=None, errors='strict', buffering=1):
    
    if encoding is not None and \
       'b' not in mode:
        # Force opening of the file in binary mode
        mode = mode + 'b'
    file = __builtin__.open(filename, mode, buffering)
    if encoding is None:
        return file
    (e, d, sr, sw) = lookup(encoding)
    srw = StreamReaderWriter(file, sr, sw, errors)
    # Add attributes to simplify introspection
    srw.encoding = encoding
    return srw

def EncodedFile(file, data_encoding, file_encoding=None, errors='strict'):
    
    if file_encoding is None:
        file_encoding = data_encoding
    encode, decode = lookup(data_encoding)[:2]
    Reader, Writer = lookup(file_encoding)[2:]
    sr = StreamRecoder(file,
                       encode, decode, Reader, Writer,
                       errors)
    # Add attributes to simplify introspection
    sr.data_encoding = data_encoding
    sr.file_encoding = file_encoding
    return sr

### Helpers for codec lookup

def getencoder(encoding):
    
    return lookup(encoding)[0]

def getdecoder(encoding):
    
    return lookup(encoding)[1]

def getreader(encoding):
    
    return lookup(encoding)[2]

def getwriter(encoding):
    
    return lookup(encoding)[3]

### Helpers for charmap-based codecs

def make_identity_dict(rng):
    
    res = {}
    for i in rng:
        res[i]=i
    return res

def make_encoding_map(decoding_map):
    
    m = {}
    for k,v in decoding_map.items():
        if not m.has_key(v):
            m[v] = k
        else:
            m[v] = None
    return m

# Tell modulefinder that using codecs probably needs the encodings
# package
_false = 0
if _false:
    import encodings

### Tests

if __name__ == '__main__':

    import sys

    # Make stdout translate Latin-1 output into UTF-8 output
    sys.stdout = EncodedFile(sys.stdout, 'latin-1', 'utf-8')

    # Have stdin translate Latin-1 input into UTF-8 input
    sys.stdin = EncodedFile(sys.stdin, 'utf-8', 'latin-1')
