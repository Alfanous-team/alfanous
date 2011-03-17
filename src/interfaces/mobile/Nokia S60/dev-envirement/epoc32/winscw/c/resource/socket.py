# Copyright (c) 2005 - 2007 Nokia Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Wrapper module for e32socket (_socket), providing some additional
# facilities implemented in Python.

from e32socket import *

import os
import e32

_default_access_point = None

__all__ = ["getfqdn","getservbyname","getaddrinfo","gethostname"]
import e32socket
__all__.extend(os._get_exports_list(e32socket))
__all__ += ('_socketobject','_fileobject')

# Release 1.0 wanted the e32socket.socket object as the
# argument for some methods. To preserve compatibility,
# we accept both that and the proper type (_socketobject).
def _unwrap(sock):
    if isinstance(sock,_socketobject):
        return sock._sock
    else:
        return sock
def bt_advertise_service(name, socket, flag, class_):
    return e32socket.bt_advertise_service(name,_unwrap(socket),flag,class_)
def bt_obex_receive(socket, filename):
    return e32socket.bt_obex_receive(_unwrap(socket), filename)
def bt_rfcomm_get_available_server_channel(socket):
    return e32socket.bt_rfcomm_get_available_server_channel(_unwrap(socket)) 
def set_security(socket,mode):
    return e32socket.set_security(_unwrap(socket),mode) 
def gethostname():
    return "localhost"

def gethostbyaddr(addr):
    if not _isnumericipaddr(addr):
        addr = gethostbyname(addr)
    (hostname, aliaslist, ipaddrlist) = e32socket.gethostbyaddr(addr)
    return (str(hostname), aliaslist, ipaddrlist)

_realsocketcall = e32socket.socket

def socket(family, type, proto=0, apo=None):
    return _socketobject(_realsocketcall(family, type, proto, apo), family)

try:
    _realsslcall = e32socket.ssl
except AttributeError:
    pass # No ssl
else:
    def ssl(sock, keyfile=None, certfile=None, hostname=None):
        realsock=getattr(sock, "_sock", sock)
        if e32.s60_version_info>=(3,0):
            # On S60 3rd Ed secure sockets must be given the expected
            # hostname before connecting or error -7547 occurs. This
            # is not needed on 2nd edition. See known issue KIS000322.
            if hostname is None:
                # To make things convenient, if a hostname was given
                # to .connect it is stored in the socket object.
                if hasattr(sock, "_getconnectname"):
                    hostname=sock._getconnectname()
                if hostname is None:
                    raise RuntimeError("Expected hostname must be given either to socket .connect() or as 4th parameter of ssl() call. See S60 known issue KIS000322.")
        return _realsslcall(realsock, keyfile, certfile, hostname)
    # Note: this is just a stopgap hack while waiting for proper SSL error handling.
    # Until that time, SSL operations _will not_ raise sslerror properly as they should.
    SSL_ERROR_NONE=0
    SSL_ERROR_SSL=1
    SSL_ERROR_WANT_READ=2
    SSL_ERROR_WANT_WRITE=3
    SSL_ERROR_WANT_X509_LOOKUP=4 
    SSL_ERROR_SYSCALL=5
    SSL_ERROR_ZERO_RETURN=6
    SSL_ERROR_WANT_CONNECT=7
    SSL_ERROR_EOF=8
    SSL_ERROR_INVALID_ERROR_CODE=9
    class sslerror(Exception):
        pass

del os

AF_UNSPEC = 0

GAI_ANY = 0

EAI_ADDRFAMILY = 1
EAI_AGAIN = 2
EAI_BADFLAGS = 3
EAI_FAIL = 4
EAI_FAMILY = 5
EAI_MEMORY = 6
EAI_NODATA = 7
EAI_NONAME = 8
EAI_SERVICE = 9
EAI_SOCKTYPE = 10
EAI_SYSTEM = 11
EAI_BADHINTS = 12
EAI_PROTOCOL = 13
EAI_MAX = 14

AI_PASSIVE = 0x00000001
AI_CANONNAME = 0x00000002
AI_NUMERICHOST = 0x00000004

def _isnumeric(value):
    try:
        tmp = int(value)
    except:
        return False
    return True

def _isnumericipaddr(addr):
    for x in addr.split('.'):
        if not _isnumeric(x):
            return False
    return True

service_db = {'echo':[('tcp',7),('udp',7)],
              'ftp-data':[('tcp',20),('udp',20)],
              'ftp':[('tcp',21),('udp',21)],
              'ssh':[('tcp',22),('udp',22)],
              'telnet':[('tcp',23),('udp',23)],
              'smtp':[('tcp',25),('udp',25)],
              'time':[('tcp',37),('udp',37)],
              'domain':[('tcp',53),('udp',53)],
              'tftp':[('tcp',69),('udp',69)],
              'http':[('tcp',80),('udp',80)],
              'www-http':[('tcp',80),('udp',80)],
              'pop2':[('tcp',109),('udp',109)],
              'pop3':[('tcp',110),('udp',110)],
              'sftp':[('tcp',115),('udp',115)],
              'nntp':[('tcp',119),('udp',119)]}

def getservbyname(service, proto):
    service_record = service_db[service.lower()]
    for x in service_record:
        if x[0] == proto:
            return x[1]
    raise error("service/proto not found")

def getaddrinfo(host, port, fam=AF_UNSPEC, socktype=GAI_ANY, proto=0, flags=0):
    if host == None and port == None:
        raise gaierror(EAI_NONAME)

    if fam not in [AF_UNSPEC, AF_INET]:
        raise gaierror(EAI_FAMILY)

    if flags & AI_NUMERICHOST and host and not _isnumericipaddr(host):
        raise gaierror(EAI_NONAME)

    r_family = AF_INET
    r_socktype = GAI_ANY
    r_proto = GAI_ANY
    r_canonname = None
    r_host = None
    r_port = GAI_ANY
        
    if socktype == GAI_ANY:
        if proto == IPPROTO_UDP:
            r_socktype = SOCK_DGRAM
        elif proto == IPPROTO_TCP:
            r_socktype = SOCK_STREAM
    elif socktype == SOCK_DGRAM:
        if not proto in [IPPROTO_UDP, GAI_ANY]:
            raise gaierror(EAI_BADHINTS)
        r_socktype = SOCK_DGRAM
        r_proto = IPPROTO_UDP
    elif socktype == SOCK_STREAM:
        if not proto in [IPPROTO_TCP, GAI_ANY]:
            raise gaierror(EAI_BADHINTS)
        r_socktype = SOCK_STREAM
        r_proto = IPPROTO_TCP
    else:
        raise gaierror(EAI_SOCKTYPE)

    if port:
        if _isnumeric(port):
            if r_socktype == GAI_ANY:
                r_socktype = SOCK_DGRAM
                r_proto = IPPROTO_UDP
            r_port = port
        else:
            if r_socktype == GAI_ANY:
                r_port = getservbyname(port, 'tcp')
                if r_port:
                    r_socktype = SOCK_STREAM
                    r_proto = IPPROTO_TCP
                else:
                    r_port = getservbyname(port, 'udp')
                    if r_port:
                        r_socktype = SOCK_DGRAM
                        r_proto = IPPROTO_UDP
                        
            elif  r_socktype == SOCK_DGRAM:
                r_port = getservbyname(port, 'udp')
            elif  r_socktype == SOCK_STREAM:
                r_port = getservbyname(port, 'tcp')

            if not r_port:
                raise gaierror(EAI_SERVICE)

    if not host:
        if flags & AI_PASSIVE:
            r_host = '0.0.0.0'
        else:
            r_host = '127.0.0.1'
    elif _isnumericipaddr(host):
        r_host = host
        if flags & AI_CANONNAME:
            if flags & AI_NUMERICHOST:
                r_canonname = host
            else:
                r_canonname, aliases, ipaddrs = gethostbyaddr(host)
    else:
        r_host = gethostbyname(host)
        if flags & AI_CANONNAME:
            r_canonname = host   # hmmm...

    return [(r_family, r_socktype, r_proto, r_canonname, (r_host, r_port))]

def getfqdn(name=''):
    name = name.strip()
    if not name or name == '0.0.0.0':
        name = gethostname()
    try:
        hostname, aliases, ipaddrs = gethostbyaddr(name)
    except error:
        pass
    else:
        aliases.insert(0, hostname)
        for name in aliases:
            if '.' in name:
                break
        else:
            name = hostname
    return name

_socketmethods = (
        'bind', 'connect_ex', 'fileno', 'listen',
        'getpeername', 'getsockname', 'getsockopt', 'setsockopt',
        'sendall', 'sendto', 'shutdown')
    
def raise_error(*args,**kwargs):
    raise error(9, 'Bad file descriptor')

class _socketobject(object):
    def __init__(self, sock, family):
        self._internalsocket=_internalsocketobject(sock,family)
        self._sock=sock
        for k in dir(self._internalsocket):
            if not k.startswith('__') and k != 'close':
                value=getattr(self._internalsocket,k)
                if callable(value):
                    setattr(self,k,value)
    def close(self):
        for k in dir(self._internalsocket):
            if not k.startswith('__') and k != 'close':
                value=getattr(self._internalsocket,k)
                if callable(value):
                    setattr(self,k,raise_error)
        self._internalsocket=None
        self._sock=None

class _internalsocketobject:
    class _closedsocket:
        def __getattr__(self, name):
            raise error(9, 'Bad file descriptor')
    def __init__(self, sock, family=AF_UNSPEC):
        self._sock = sock
        self._blocking=True
        self._recvbuf=''
        self._sendbuf=''
        self._recv_callback_pending=False
        self._send_callback_pending=False
        self._recv_listener=None
        self._recvsizehint=8
        self._sendflags=0
        self._recvlock=e32.Ao_lock()
        self._family=family
        self._error=None
        self._connectname=None
        
    def close(self):
        self._sock = self.__class__._closedsocket()
        
    def setblocking(self, flag):
        self._blocking=flag
            
    def accept(self, cb=None):
        if cb == None:
            sock, addr = self._sock.accept()
            return _socketobject(sock, self._family), addr
        else:
            return self._sock.accept(cb)

    def connect(self, addr, cb=None):
        if not self._family == AF_INET or _isnumericipaddr(addr[0]):
            return self._sock.connect(addr, cb)
        else:
            # Store hostname so that it can be given to ssl().
            self._connectname=addr[0] 
            return self._sock.connect((gethostbyname(addr[0]), addr[1]), cb)

    def _getconnectname(self):
        return self._connectname

    def dup(self):
        return _socketobject(self._sock, self._family)

    def makefile(self, mode='r', bufsize=-1):
        return _fileobject(self.dup(), mode, bufsize)

    def read(self, n=1, cb=None):
        return self.recv(n,0,cb)

    def read_all(self, blocksize=1024):
        self._checkerror()
        data = ''
        while 1:
            fragment = self._sock.recv(blocksize)
            if not fragment:
                break
            data += fragment
        return data

    def recv(self, n, f=0, cb=None):
        self._recvsizehint=n
        self._checkerror()
        # if there's data in recvbuf, return data from there.
        if len(self._recvbuf)>0: 
            (data,self._recvbuf)=(self._recvbuf[:n], self._recvbuf[n:])
            return data
        # recvbuf is empty. try to receive some data.
        if self._blocking:
            if self._recv_callback_pending:
                self._recvlock.wait()
                (data,self._recvbuf)=(self._recvbuf[:n], self._recvbuf[n:])
            else:
                data=self._sock.recv(n, f, cb)
            return data
        else:
            if cb is not None:
                raise RuntimeError('Callback not supported in non-blocking mode')
            if not self._recv_callback_pending:
                self._sock.recv(n,f,self._recv_callback)
                self._recv_callback_pending=True
            return ''

    def _checkerror(self):
        if self._error:
            raise self._error[0],self._error[1]
        
    def _seterror(self,errortuple):
        self._error=errortuple

    def _recv_callback(self,data):
        if isinstance(data,tuple):
            print "error %s %s"%data
            self._seterror(data)
            return
        self._recvbuf += data
        self._recv_callback_pending=False
        if self._recv_listener:
            t=self._recv_listener
            self._recv_listener=None
            t()

    def _set_recv_listener(self,callback):
        self._recv_listener=callback

    def _recv_will_return_data_immediately(self):
        if len(self._recvbuf)>0:
            return True
        if not self._recv_callback_pending:
            # Here this function starts a recv as a side effect so
            # that some time in the future we may have data in the
            # buffer. This is done so that the typical select-recv
            # idiom will work properly with this implementation.
            # self._recvsizehint is used as a guess for the receive
            # block size so that the most common case where the read
            # after the select is always the same size will cause the
            # same size blocks to be used while doing the recv
            # here. (Except of course for the very first pass when
            # the default size is used)
            self._recv_callback_pending=True
            self._sock.recv(self._recvsizehint,0,self._recv_callback)
        return False

    def recvfrom(self, n, f=0, cb=None):
        return self._sock.recvfrom(n, f, cb)
                
    def send(self, data, f=0, cb=None):
        self._checkerror()
        if self._blocking:
            return self._sock.send(data, f, cb)
        else:
            if cb is not None:
                raise RuntimeError('Callback not supported in non-blocking mode')
            if self._send_callback_pending:
                self._sendbuf += data
            else:
                self._send_callback_pending=True
                self._sendflags=f
                self._sock.send(data,f,self._send_callback)
            return len(data)

    def _send_callback(self,n):
        if isinstance(n,tuple):
            print "error %s %s"%data
            self._seterror(n)
            return
        if len(self._sendbuf)>0:
            # More data was put in the sendbuf while we were waiting
            # for this callback to be called. Send that too.
            self._sock.send(self._sendbuf,self._sendflags,self._send_callback)
            self._sendbuf=''
        else:
            self._send_callback_pending=False
        
    _s = "def %s(self, *args): return self._sock.%s(*args)\n\n"
    for _m in _socketmethods:
        exec _s % (_m, _m)


class _fileobject(object):

    def __init__(self, sock, mode, bufsize):
        self._sock = sock
        self._mode = mode
        if bufsize < 0:
            bufsize = 512
        self._rbufsize = max(1, bufsize)
        self._wbufsize = bufsize
        self._wbuf = self._rbuf = ""

    def close(self):
        try:
            if self._sock:
                self.flush()
        finally:
            self._sock = 0

    def __del__(self):
        self.close()

    def flush(self):
        if self._wbuf:
            self._sock.sendall(self._wbuf)
            self._wbuf = ""

    def fileno(self):
        return self._sock._sock.fileno()

    def write(self, data):
        self._wbuf = self._wbuf + data
        if self._wbufsize == 1:
            if '\n' in data:
                self.flush()
        else:
            if len(self._wbuf) >= self._wbufsize:
                self.flush()

    def writelines(self, list):
        filter(self._sock.sendall, list)
        self.flush()

    def read(self, n=-1):
        if n >= 0:
            k = len(self._rbuf)
            if n <= k:
                data = self._rbuf[:n]
                self._rbuf = self._rbuf[n:]
                return data
            n = n - k
            L = [self._rbuf]
            self._rbuf = ""
            while n > 0:
                new = self._sock.recv(max(n, self._rbufsize))
                if not new: break
                k = len(new)
                if k > n:
                    L.append(new[:n])
                    self._rbuf = new[n:]
                    break
                L.append(new)
                n = n - k
            return "".join(L)
        k = max(512, self._rbufsize)
        L = [self._rbuf]
        self._rbuf = ""
        while 1:
            new = self._sock.recv(k)
            if not new: break
            L.append(new)
            k = min(k*2, 1024**2)
        return "".join(L)

    def readline(self, limit=-1):
        data = ""
        i = self._rbuf.find('\n')
        while i < 0 and not (0 < limit <= len(self._rbuf)):
            new = self._sock.recv(self._rbufsize)
            if not new: break
            i = new.find('\n')
            if i >= 0: i = i + len(self._rbuf)
            self._rbuf = self._rbuf + new
        if i < 0: i = len(self._rbuf)
        else: i = i+1
        if 0 <= limit < len(self._rbuf): i = limit
        data, self._rbuf = self._rbuf[:i], self._rbuf[i:]
        return data

    def readlines(self, sizehint = 0):
        total = 0
        list = []
        while 1:
            line = self.readline()
            if not line: break
            list.append(line)
            total += len(line)
            if sizehint and total >= sizehint:
                break
        return list
