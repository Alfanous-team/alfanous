# Portions Copyright (c) 2005 - 2007 Nokia Corporation 
"""HTTP/1.1 client library"""

import errno
import mimetools
import socket
import e32
from urlparse import urlsplit

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

__all__ = ["HTTP", "HTTPResponse", "HTTPConnection", "HTTPSConnection",
           "HTTPException", "NotConnected", "UnknownProtocol",
           "UnknownTransferEncoding", "UnimplementedFileMode",
           "IncompleteRead", "InvalidURL", "ImproperConnectionState",
           "CannotSendRequest", "CannotSendHeader", "ResponseNotReady",
           "BadStatusLine", "error"]

HTTP_PORT = 80
HTTPS_PORT = 443

_UNKNOWN = 'UNKNOWN'

# connection states
_CS_IDLE = 'Idle'
_CS_REQ_STARTED = 'Request-started'
_CS_REQ_SENT = 'Request-sent'

class HTTPMessage(mimetools.Message):

    def addheader(self, key, value):
        prev = self.dict.get(key)
        if prev is None:
            self.dict[key] = value
        else:
            combined = ", ".join((prev, value))
            self.dict[key] = combined

    def addcontinue(self, key, more):
        prev = self.dict[key]
        self.dict[key] = prev + "\n " + more

    def readheaders(self):

        self.dict = {}
        self.unixfrom = ''
        self.headers = list = []
        self.status = ''
        headerseen = ""
        firstline = 1
        startofline = unread = tell = None
        if hasattr(self.fp, 'unread'):
            unread = self.fp.unread
        elif self.seekable:
            tell = self.fp.tell
        while 1:
            if tell:
                try:
                    startofline = tell()
                except IOError:
                    startofline = tell = None
                    self.seekable = 0
            line = self.fp.readline()
            if not line:
                self.status = 'EOF in headers'
                break
            if firstline and line.startswith('From '):
                self.unixfrom = self.unixfrom + line
                continue
            firstline = 0
            if headerseen and line[0] in ' \t':
                list.append(line)
                x = self.dict[headerseen] + "\n " + line.strip()
                self.addcontinue(headerseen, line.strip())
                continue
            elif self.iscomment(line):
                continue
            elif self.islast(line):
                break
            headerseen = self.isheader(line)
            if headerseen:
                list.append(line)
                self.addheader(headerseen, line[len(headerseen)+1:].strip())
                continue
            else:
                if not self.dict:
                    self.status = 'No headers'
                else:
                    self.status = 'Non-header line where header expected'
                if unread:
                    unread(line)
                elif tell:
                    self.fp.seek(startofline)
                else:
                    self.status = self.status + '; bad seek'
                break

class HTTPResponse:

    def __init__(self, sock, debuglevel=0, strict=0):
        self.fp = sock.makefile('rb', 0)
        self.debuglevel = debuglevel
        self.strict = strict

        self.msg = None

        self.version = _UNKNOWN
        self.status = _UNKNOWN
        self.reason = _UNKNOWN

        self.chunked = _UNKNOWN
        self.chunk_left = _UNKNOWN
        self.length = _UNKNOWN
        self.will_close = _UNKNOWN

    def _read_status(self):
        line = self.fp.readline()
        if self.debuglevel > 0:
            print "reply:", repr(line)
        try:
            [version, status, reason] = line.split(None, 2)
        except ValueError:
            try:
                [version, status] = line.split(None, 1)
                reason = ""
            except ValueError:
                version = ""
        if not version.startswith('HTTP/'):
            if self.strict:
                self.close()
                raise BadStatusLine(line)
            else:
                self.fp = LineAndFileWrapper(line, self.fp)
                return "HTTP/0.9", 200, ""

        try:
            status = int(status)
            if status < 100 or status > 999:
                raise BadStatusLine(line)
        except ValueError:
            raise BadStatusLine(line)
        return version, status, reason

    def begin(self):
        if self.msg is not None:
            return

        while 1:
            version, status, reason = self._read_status()
            if status != 100:
                break
            while 1:
                skip = self.fp.readline().strip()
                if not skip:
                    break
                if self.debuglevel > 0:
                    print "header:", skip

        self.status = status
        self.reason = reason.strip()
        if version == 'HTTP/1.0':
            self.version = 10
        elif version.startswith('HTTP/1.'):
            self.version = 11
        elif version == 'HTTP/0.9':
            self.version = 9
        else:
            raise UnknownProtocol(version)

        if self.version == 9:
            self.chunked = 0
            self.will_close = 1
            self.msg = HTTPMessage(StringIO())
            return

        self.msg = HTTPMessage(self.fp, 0)
        if self.debuglevel > 0:
            for hdr in self.msg.headers:
                print "header:", hdr,

        self.msg.fp = None

        tr_enc = self.msg.getheader('transfer-encoding')
        if tr_enc and tr_enc.lower() == "chunked":
            self.chunked = 1
            self.chunk_left = None
        else:
            self.chunked = 0

        conn = self.msg.getheader('connection')
        if conn:
            conn = conn.lower()
            self.will_close = conn.find('close') != -1 or \
                              ( self.version != 11 and \
                                not self.msg.getheader('keep-alive') )
        else:
            self.will_close = self.version != 11 and \
                              not self.msg.getheader('keep-alive')

        length = self.msg.getheader('content-length')
        if length and not self.chunked:
            try:
                self.length = int(length)
            except ValueError:
                self.length = None
        else:
            self.length = None

        if (status == 204 or
            status == 304 or
            100 <= status < 200):
            self.length = 0

        if not self.will_close and \
           not self.chunked and \
           self.length is None:
            self.will_close = 1

    def close(self):
        if self.fp:
            self.fp.close()
            self.fp = None

    def isclosed(self):
        return self.fp is None

    def read(self, amt=None):
        if self.fp is None:
            return ''

        if self.chunked:
            return self._read_chunked(amt)

        if amt is None:
            if self.will_close:
                s = self.fp.read()
            else:
                s = self._safe_read(self.length)
            self.close()
            return s

        if self.length is not None:
            if amt > self.length:
                amt = self.length
            self.length -= amt

        s = self.fp.read(amt)

        return s

    def _read_chunked(self, amt):
        assert self.chunked != _UNKNOWN
        chunk_left = self.chunk_left
        value = ''

        while 1:
            if chunk_left is None:
                line = self.fp.readline()
                i = line.find(';')
                if i >= 0:
                    line = line[:i]
                chunk_left = int(line, 16)
                if chunk_left == 0:
                    break
            if amt is None:
                value += self._safe_read(chunk_left)
            elif amt < chunk_left:
                value += self._safe_read(amt)
                self.chunk_left = chunk_left - amt
                return value
            elif amt == chunk_left:
                value += self._safe_read(amt)
                self._safe_read(2)
                self.chunk_left = None
                return value
            else:
                value += self._safe_read(chunk_left)
                amt -= chunk_left

            self._safe_read(2)
            chunk_left = None

        while 1:
            line = self.fp.readline()
            if line == '\r\n':
                break

        self.close()

        return value

    def _safe_read(self, amt):
        s = ''
        while amt > 0:
            chunk = self.fp.read(amt)
            if not chunk:
                raise IncompleteRead(s)
            s = s + chunk
            amt = amt - len(chunk)
        return s

    def getheader(self, name, default=None):
        if self.msg is None:
            raise ResponseNotReady()
        return self.msg.getheader(name, default)


class HTTPConnection:

    _http_vsn = 11
    _http_vsn_str = 'HTTP/1.1'

    response_class = HTTPResponse
    default_port = HTTP_PORT
    auto_open = 1
    debuglevel = 0
    strict = 0

    def __init__(self, host, port=None, strict=None, hostname=None):
        self.sock = None
        self._buffer = []
        self.__response = None
        self.__state = _CS_IDLE

        self._set_hostport(host, port)
        if strict is not None:
            self.strict = strict
            
        if hostname is not None:
            self.hostname = hostname

    def _set_hostport(self, host, port):
        if port is None:
            i = host.find(':')
            if i >= 0:
                try:
                    port = int(host[i+1:])
                except ValueError:
                    raise InvalidURL("nonnumeric port: '%s'" % host[i+1:])
                host = host[:i]
            else:
                port = self.default_port
        self.host = host
        self.port = port

    def set_debuglevel(self, level):
        self.debuglevel = level

    def connect(self):
        msg = "getaddrinfo returns an empty list"
        for res in socket.getaddrinfo(self.host, self.port, 0,
                                      socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.sock = socket.socket(af, socktype, proto)
                if self.debuglevel > 0:
                    print "connect: (%s, %s)" % (self.host, self.port)
                self.sock.connect(sa)
            except socket.error, msg:
                if self.debuglevel > 0:
                    print 'connect fail:', (self.host, self.port)
                if self.sock:
                    self.sock.close()
                self.sock = None
                continue
            break
        if not self.sock:
            raise socket.error, msg

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
        if self.__response:
            self.__response.close()
            self.__response = None
        self.__state = _CS_IDLE

    def send(self, str):
        if self.sock is None:
            if self.auto_open:
                self.connect()
            else:
                raise NotConnected()

        if self.debuglevel > 0:
            print "send:", repr(str)
        try:
            self.sock.sendall(str)
        except socket.error, v:
            if v[0] == 32:
                self.close()
            raise

    def _output(self, s):
        self._buffer.append(s)

    def _send_output(self):
        self._buffer.extend(("", ""))
        msg = "\r\n".join(self._buffer)
        del self._buffer[:]
        self.send(msg)

    def putrequest(self, method, url, skip_host=0):

        if self.__response and self.__response.isclosed():
            self.__response = None

        if self.__state == _CS_IDLE:
            self.__state = _CS_REQ_STARTED
        else:
            raise CannotSendRequest()

        if not url:
            url = '/'
        str = '%s %s %s' % (method, url, self._http_vsn_str)

        self._output(str)

        if self._http_vsn == 11:
            if not skip_host:
                netloc = ''
                if url.startswith('http'):
                    nil, netloc, nil, nil, nil = urlsplit(url)

                if netloc:
                    self.putheader('Host', netloc)
                elif self.port == HTTP_PORT:
                    self.putheader('Host', self.host)
                else:
                    self.putheader('Host', "%s:%s" % (self.host, self.port))

            self.putheader('Accept-Encoding', 'identity')
        else:
            pass

    def putheader(self, header, value):
        if self.__state != _CS_REQ_STARTED:
            raise CannotSendHeader()

        str = '%s: %s' % (header, value)
        self._output(str)

    def endheaders(self):

        if self.__state == _CS_REQ_STARTED:
            self.__state = _CS_REQ_SENT
        else:
            raise CannotSendHeader()

        self._send_output()

    def request(self, method, url, body=None, headers={}):

        try:
            self._send_request(method, url, body, headers)
        except socket.error, v:
            if v[0] != 32 or not self.auto_open:
                raise
            self._send_request(method, url, body, headers)

    def _send_request(self, method, url, body, headers):
        if 'Host' in (headers
            or [k for k in headers.iterkeys() if k.lower() == "host"]):
            self.putrequest(method, url, skip_host=1)
        else:
            self.putrequest(method, url)

        if body:
            self.putheader('Content-Length', str(len(body)))
        for hdr, value in headers.items():
            self.putheader(hdr, value)
        self.endheaders()

        if body:
            self.send(body)

    def getresponse(self):
        if self.__response and self.__response.isclosed():
            self.__response = None

        if self.__state != _CS_REQ_SENT or self.__response:
            raise ResponseNotReady()

        if self.debuglevel > 0:
            response = self.response_class(self.sock, self.debuglevel,
                                           strict=self.strict)
        else:
            response = self.response_class(self.sock, strict=self.strict)

        response.begin()
        assert response.will_close != _UNKNOWN
        self.__state = _CS_IDLE

        if response.will_close:
            self.close()
        else:
            self.__response = response

        return response

class SharedSocket:

    def __init__(self, sock):
        self.sock = sock
        self._refcnt = 0

    def incref(self):
        self._refcnt += 1

    def decref(self):
        self._refcnt -= 1
        assert self._refcnt >= 0
        if self._refcnt == 0:
            self.sock.close()

    def __del__(self):
        self.sock.close()

class SharedSocketClient:

    def __init__(self, shared):
        self._closed = 0
        self._shared = shared
        self._shared.incref()
        self._sock = shared.sock

    def close(self):
        if not self._closed:
            self._shared.decref()
            self._closed = 1
            self._shared = None

class SSLFile(SharedSocketClient):

    BUFSIZE = 8192

    def __init__(self, sock, ssl, bufsize=None):
        SharedSocketClient.__init__(self, sock)
        self._ssl = ssl
        self._buf = ''
        self._bufsize = bufsize or self.__class__.BUFSIZE

    def _read(self):
        buf = ''
        while 1:
            try:
                buf = self._ssl.read(self._bufsize)
            except socket.sslerror, err:
                if (err[0] == socket.SSL_ERROR_WANT_READ
                    or err[0] == socket.SSL_ERROR_WANT_WRITE):
                    continue
                if (err[0] == socket.SSL_ERROR_ZERO_RETURN
                    or err[0] == socket.SSL_ERROR_EOF):
                    break
                raise
            except socket.error, err:
                if err[0] == errno.EINTR:
                    continue
                # UGLY HACK to make httplib work with the currently nonstandard socket.ssl exception
                # behaviour. SSL operations don't raise sslerror as they should.
                if err[0] == errno.EBADF or err[0] == 'Attempt to use a closed socket':
                    break
                raise
            else:
                break
        return buf

    def read(self, size=None):
        L = [self._buf]
        avail = len(self._buf)
        while size is None or avail < size:
            s = self._read()
            if s == '':
                break
            L.append(s)
            avail += len(s)
        all = "".join(L)
        if size is None:
            self._buf = ''
            return all
        else:
            self._buf = all[size:]
            return all[:size]

    def readline(self):
        L = [self._buf]
        self._buf = ''
        while 1:
            i = L[-1].find("\n")
            if i >= 0:
                break
            s = self._read()
            if s == '':
                break
            L.append(s)
        if i == -1:
            return "".join(L)
        else:
            all = "".join(L)
            i = all.find("\n") + 1
            line = all[:i]
            self._buf = all[i:]
            return line

class FakeSocket(SharedSocketClient):

    class _closedsocket:
        def __getattr__(self, name):
            raise error(9, 'Bad file descriptor')

    def __init__(self, sock, ssl):
        sock = SharedSocket(sock)
        SharedSocketClient.__init__(self, sock)
        self._ssl = ssl

    def close(self):
        SharedSocketClient.close(self)
        self._sock = self.__class__._closedsocket()

    def makefile(self, mode, bufsize=None):
        if mode != 'r' and mode != 'rb':
            raise UnimplementedFileMode()
        return SSLFile(self._shared, self._ssl, bufsize)

    def send(self, stuff, flags = 0):
        return self._ssl.write(stuff)

    sendall = send

    def recv(self, len = 1024, flags = 0):
        return self._ssl.read(len)

    def __getattr__(self, attr):
        return getattr(self._sock, attr)


class HTTPSConnection(HTTPConnection):

    default_port = HTTPS_PORT

    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 strict=None, hostname=None):
        HTTPConnection.__init__(self, host, port, strict, hostname)
        self.key_file = key_file
        self.cert_file = cert_file
        self.hostname = hostname

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        realsock=getattr(sock, "_sock", sock)
        if e32.s60_version_info>=(3,0):
            # On S60 3rd Ed secure sockets must be given the expected
            # hostname before connecting or error -7547 occurs. This
            # is not needed on 2nd edition. See known issue KIS000322.
            if self.hostname is None:
                # To make things convenient, if a hostname was given
                # to .connect it is stored in the socket object.
                if hasattr(sock, "_getconnectname"):
                    self.hostname=sock._getconnectname()
                if self.hostname is None:
                    raise RuntimeError("Expected hostname must be given either to socket .connect() or as 4th parameter of ssl() call. See S60 known issue KIS000322.")

        ssl = socket.ssl(realsock, self.key_file, self.cert_file, self.hostname)
        self.sock = FakeSocket(sock, ssl)


class HTTP:

    _http_vsn = 10
    _http_vsn_str = 'HTTP/1.0'

    debuglevel = 0

    _connection_class = HTTPConnection

    def __init__(self, host='', port=None, strict=None):
        if port == 0:
            port = None
        self._setup(self._connection_class(host, port, strict))

    def _setup(self, conn):
        self._conn = conn

        self.send = conn.send
        self.putrequest = conn.putrequest
        self.endheaders = conn.endheaders
        self.set_debuglevel = conn.set_debuglevel

        conn._http_vsn = self._http_vsn
        conn._http_vsn_str = self._http_vsn_str

        self.file = None

    def connect(self, host=None, port=None):
        if host is not None:
            self._conn._set_hostport(host, port)
        self._conn.connect()

    def getfile(self):
        return self.file

    def putheader(self, header, *values):
        self._conn.putheader(header, '\r\n\t'.join(values))

    def getreply(self):
        try:
            response = self._conn.getresponse()
        except BadStatusLine, e:
            self.file = self._conn.sock.makefile('rb', 0)

            self.close()

            self.headers = None
            return -1, e.line, None

        self.headers = response.msg
        self.file = response.fp
        return response.status, response.reason, response.msg

    def close(self):
        self._conn.close()
        self.file = None

if hasattr(socket, 'ssl'):
    class HTTPS(HTTP):

        _connection_class = HTTPSConnection

        def __init__(self, host='', port=None, key_file=None, cert_file=None,
                     strict=None, hostname=None):
            if port == 0:
                port = None
            self._setup(self._connection_class(host, port, key_file,
                                               cert_file, strict))

            self.key_file = key_file
            self.cert_file = cert_file
            self.hostname = hostname


class HTTPException(Exception):
    pass

class NotConnected(HTTPException):
    pass

class InvalidURL(HTTPException):
    pass

class UnknownProtocol(HTTPException):
    def __init__(self, version):
        self.args = version,
        self.version = version

class UnknownTransferEncoding(HTTPException):
    pass

class UnimplementedFileMode(HTTPException):
    pass

class IncompleteRead(HTTPException):
    def __init__(self, partial):
        self.args = partial,
        self.partial = partial

class ImproperConnectionState(HTTPException):
    pass

class CannotSendRequest(ImproperConnectionState):
    pass

class CannotSendHeader(ImproperConnectionState):
    pass

class ResponseNotReady(ImproperConnectionState):
    pass

class BadStatusLine(HTTPException):
    def __init__(self, line):
        self.args = line,
        self.line = line

# for backwards compatibility
error = HTTPException

class LineAndFileWrapper:

    def __init__(self, line, file):
        self._line = line
        self._file = file
        self._line_consumed = 0
        self._line_offset = 0
        self._line_left = len(line)

    def __getattr__(self, attr):
        return getattr(self._file, attr)

    def _done(self):
        self._line_consumed = 1
        self.read = self._file.read
        self.readline = self._file.readline
        self.readlines = self._file.readlines

    def read(self, amt=None):
        assert not self._line_consumed and self._line_left
        if amt is None or amt > self._line_left:
            s = self._line[self._line_offset:]
            self._done()
            if amt is None:
                return s + self._file.read()
            else:
                return s + self._file.read(amt - len(s))
        else:
            assert amt <= self._line_left
            i = self._line_offset
            j = i + amt
            s = self._line[i:j]
            self._line_offset = j
            self._line_left -= amt
            if self._line_left == 0:
                self._done()
            return s

    def readline(self):
        s = self._line[self._line_offset:]
        self._done()
        return s

    def readlines(self, size=None):
        L = [self._line[self._line_offset:]]
        self._done()
        if size is None:
            return L + self._file.readlines()
        else:
            return L + self._file.readlines(size)

if __name__ == '__main__':
    pass
