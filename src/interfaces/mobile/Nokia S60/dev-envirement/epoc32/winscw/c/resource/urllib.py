# Portions Copyright (c) 2005 Nokia Corporation 
"""Open an arbitrary URL."""

import string
import socket
import os
import stat
import time
import sys
import types

__all__ = ["urlopen", "URLopener", "FancyURLopener", "urlretrieve",
           "urlcleanup", "quote", "quote_plus", "unquote", "unquote_plus",
           "urlencode", "url2pathname", "pathname2url", "splittag",
           "localhost", "thishost", "ftperrors", "basejoin", "unwrap",
           "splittype", "splithost", "splituser", "splitpasswd", "splitport",
           "splitnport", "splitquery", "splitattr", "splitvalue",
           "splitgophertype", "getproxies"]

__version__ = '1.15'    # XXX This version is not always updated :-(

MAXFTPCACHE = 10        # Trim the ftp cache beyond this size

# Helper for non-unix systems
if os.name == 'mac':
    from macurl2path import url2pathname, pathname2url
elif os.name == 'nt':
    from nturl2path import url2pathname, pathname2url
elif os.name == 'riscos':
    from rourl2path import url2pathname, pathname2url
else:
    def url2pathname(pathname):
        return unquote(pathname)
    def pathname2url(pathname):
        return quote(pathname)

_urlopener = None
def urlopen(url, data=None):
    global _urlopener
    if not _urlopener:
        _urlopener = FancyURLopener()
    if data is None:
        return _urlopener.open(url)
    else:
        return _urlopener.open(url, data)
def urlretrieve(url, filename=None, reporthook=None, data=None):
    global _urlopener
    if not _urlopener:
        _urlopener = FancyURLopener()
    return _urlopener.retrieve(url, filename, reporthook, data)
def urlcleanup():
    if _urlopener:
        _urlopener.cleanup()


ftpcache = {}
class URLopener:

    __tempfiles = None

    version = "Python-urllib/%s" % __version__

    def __init__(self, proxies=None, **x509):
        if proxies is None:
            proxies = getproxies()
        assert hasattr(proxies, 'has_key'), "proxies must be a mapping"
        self.proxies = proxies
        self.key_file = x509.get('key_file')
        self.cert_file = x509.get('cert_file')
        self.addheaders = [('User-agent', self.version)]
        self.__tempfiles = []
        self.__unlink = os.unlink
        self.tempcache = None
        self.ftpcache = ftpcache

    def __del__(self):
        self.close()

    def close(self):
        self.cleanup()

    def cleanup(self):
        if self.__tempfiles:
            for file in self.__tempfiles:
                try:
                    self.__unlink(file)
                except OSError:
                    pass
            del self.__tempfiles[:]
        if self.tempcache:
            self.tempcache.clear()

    def addheader(self, *args):
        self.addheaders.append(args)

    def open(self, fullurl, data=None):
        fullurl = unwrap(toBytes(fullurl))
        if self.tempcache and self.tempcache.has_key(fullurl):
            filename, headers = self.tempcache[fullurl]
            fp = open(filename, 'rb')
            return addinfourl(fp, headers, fullurl)
        urltype, url = splittype(fullurl)
        if not urltype:
            urltype = 'file'
        if self.proxies.has_key(urltype):
            proxy = self.proxies[urltype]
            urltype, proxyhost = splittype(proxy)
            host, selector = splithost(proxyhost)
            url = (host, fullurl)
        else:
            proxy = None
        name = 'open_' + urltype
        self.type = urltype
        if '-' in name:
            name = '_'.join(name.split('-'))
        if not hasattr(self, name):
            if proxy:
                return self.open_unknown_proxy(proxy, fullurl, data)
            else:
                return self.open_unknown(fullurl, data)
        try:
            if data is None:
                return getattr(self, name)(url)
            else:
                return getattr(self, name)(url, data)
        except socket.error, msg:
            raise IOError, ('socket error', msg), sys.exc_info()[2]

    def open_unknown(self, fullurl, data=None):
        type, url = splittype(fullurl)
        raise IOError, ('url error', 'unknown url type', type)

    def open_unknown_proxy(self, proxy, fullurl, data=None):
        type, url = splittype(fullurl)
        raise IOError, ('url error', 'invalid proxy for %s' % type, proxy)

    def retrieve(self, url, filename=None, reporthook=None, data=None):
        url = unwrap(toBytes(url))
        if self.tempcache and self.tempcache.has_key(url):
            return self.tempcache[url]
        type, url1 = splittype(url)
        if not filename and (not type or type == 'file'):
            try:
                fp = self.open_local_file(url1)
                hdrs = fp.info()
                del fp
                return url2pathname(splithost(url1)[1]), hdrs
            except IOError, msg:
                pass
        fp = self.open(url, data)
        headers = fp.info()
        if not filename:
            import tempfile
            garbage, path = splittype(url)
            garbage, path = splithost(path or "")
            path, garbage = splitquery(path or "")
            path, garbage = splitattr(path or "")
            suffix = os.path.splitext(path)[1]
            filename = tempfile.mktemp(suffix)
            self.__tempfiles.append(filename)
        result = filename, headers
        if self.tempcache is not None:
            self.tempcache[url] = result
        tfp = open(filename, 'wb')
        bs = 1024*8
        size = -1
        blocknum = 1
        if reporthook:
            if headers.has_key("content-length"):
                size = int(headers["Content-Length"])
            reporthook(0, bs, size)
        block = fp.read(bs)
        if reporthook:
            reporthook(1, bs, size)
        while block:
            tfp.write(block)
            block = fp.read(bs)
            blocknum = blocknum + 1
            if reporthook:
                reporthook(blocknum, bs, size)
        fp.close()
        tfp.close()
        del fp
        del tfp
        return result


    def open_http(self, url, data=None):
        import httplib
        user_passwd = None
        if type(url) is types.StringType:
            host, selector = splithost(url)
            if host:
                user_passwd, host = splituser(host)
                host = unquote(host)
            realhost = host
        else:
            host, selector = url
            urltype, rest = splittype(selector)
            url = rest
            user_passwd = None
            if urltype.lower() != 'http':
                realhost = None
            else:
                realhost, rest = splithost(rest)
                if realhost:
                    user_passwd, realhost = splituser(realhost)
                if user_passwd:
                    selector = "%s://%s%s" % (urltype, realhost, rest)
                if proxy_bypass(realhost):
                    host = realhost

        if not host: raise IOError, ('http error', 'no host given')
        if user_passwd:
            import base64
            auth = base64.encodestring(user_passwd).strip()
        else:
            auth = None
        h = httplib.HTTP(host)
        if data is not None:
            h.putrequest('POST', selector)
            h.putheader('Content-type', 'application/x-www-form-urlencoded')
            h.putheader('Content-length', '%d' % len(data))
        else:
            h.putrequest('GET', selector)
        if auth: h.putheader('Authorization', 'Basic %s' % auth)
        if realhost: h.putheader('Host', realhost)
        for args in self.addheaders: apply(h.putheader, args)
        h.endheaders()
        if data is not None:
            h.send(data)
        errcode, errmsg, headers = h.getreply()
        fp = h.getfile()
        if errcode == 200:
            return addinfourl(fp, headers, "http:" + url)
        else:
            if data is None:
                return self.http_error(url, fp, errcode, errmsg, headers)
            else:
                return self.http_error(url, fp, errcode, errmsg, headers, data)

    def http_error(self, url, fp, errcode, errmsg, headers, data=None):
        name = 'http_error_%d' % errcode
        if hasattr(self, name):
            method = getattr(self, name)
            if data is None:
                result = method(url, fp, errcode, errmsg, headers)
            else:
                result = method(url, fp, errcode, errmsg, headers, data)
            if result: return result
        return self.http_error_default(url, fp, errcode, errmsg, headers)

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        void = fp.read()
        fp.close()
        raise IOError, ('http error', errcode, errmsg, headers)

    if hasattr(socket, "ssl"):
        def open_https(self, url, data=None):
            import httplib
            user_passwd = None
            if type(url) is types.StringType:
                host, selector = splithost(url)
                if host:
                    user_passwd, host = splituser(host)
                    host = unquote(host)
                realhost = host
            else:
                host, selector = url
                urltype, rest = splittype(selector)
                url = rest
                user_passwd = None
                if urltype.lower() != 'https':
                    realhost = None
                else:
                    realhost, rest = splithost(rest)
                    if realhost:
                        user_passwd, realhost = splituser(realhost)
                    if user_passwd:
                        selector = "%s://%s%s" % (urltype, realhost, rest)
            if not host: raise IOError, ('https error', 'no host given')
            if user_passwd:
                import base64
                auth = base64.encodestring(user_passwd).strip()
            else:
                auth = None
            h = httplib.HTTPS(host, 0,
                              key_file=self.key_file,
                              cert_file=self.cert_file)
            if data is not None:
                h.putrequest('POST', selector)
                h.putheader('Content-type',
                            'application/x-www-form-urlencoded')
                h.putheader('Content-length', '%d' % len(data))
            else:
                h.putrequest('GET', selector)
            if auth: h.putheader('Authorization: Basic %s' % auth)
            if realhost: h.putheader('Host', realhost)
            for args in self.addheaders: apply(h.putheader, args)
            h.endheaders()
            if data is not None:
                h.send(data)
            errcode, errmsg, headers = h.getreply()
            fp = h.getfile()
            if errcode == 200:
                return addinfourl(fp, headers, "https:" + url)
            else:
                if data is None:
                    return self.http_error(url, fp, errcode, errmsg, headers)
                else:
                    return self.http_error(url, fp, errcode, errmsg, headers,
                                           data)

    def open_gopher(self, url):
        import gopherlib
        host, selector = splithost(url)
        if not host: raise IOError, ('gopher error', 'no host given')
        host = unquote(host)
        type, selector = splitgophertype(selector)
        selector, query = splitquery(selector)
        selector = unquote(selector)
        if query:
            query = unquote(query)
            fp = gopherlib.send_query(selector, query, host)
        else:
            fp = gopherlib.send_selector(selector, host)
        return addinfourl(fp, noheaders(), "gopher:" + url)

    def open_file(self, url):
        if url[:2] == '//' and url[2:3] != '/' and url[2:12].lower() != 'localhost/':
            return self.open_ftp(url)
        else:
            return self.open_local_file(url)

    def open_local_file(self, url):
        import mimetypes, mimetools, rfc822, StringIO
        host, file = splithost(url)
        localname = url2pathname(file)
        try:
            stats = os.stat(localname)
        except OSError, e:
            raise IOError(e.errno, e.strerror, e.filename)
        size = stats[stat.ST_SIZE]
        modified = rfc822.formatdate(stats[stat.ST_MTIME])
        mtype = mimetypes.guess_type(url)[0]
        headers = mimetools.Message(StringIO.StringIO(
            'Content-Type: %s\nContent-Length: %d\nLast-modified: %s\n' %
            (mtype or 'text/plain', size, modified)))
        if not host:
            urlfile = file
            if file[:1] == '/':
                urlfile = 'file://' + file
            return addinfourl(open(localname, 'rb'),
                              headers, urlfile)
        host, port = splitport(host)
        if not port \
           and socket.gethostbyname(host) in (localhost(), thishost()):
            urlfile = file
            if file[:1] == '/':
                urlfile = 'file://' + file
            return addinfourl(open(localname, 'rb'),
                              headers, urlfile)
        raise IOError, ('local file error', 'not on local host')

    def open_ftp(self, url):
        import mimetypes, mimetools, StringIO
        host, path = splithost(url)
        if not host: raise IOError, ('ftp error', 'no host given')
        host, port = splitport(host)
        user, host = splituser(host)
        if user: user, passwd = splitpasswd(user)
        else: passwd = None
        host = unquote(host)
        user = unquote(user or '')
        passwd = unquote(passwd or '')
        host = socket.gethostbyname(host)
        if not port:
            import ftplib
            port = ftplib.FTP_PORT
        else:
            port = int(port)
        path, attrs = splitattr(path)
        path = unquote(path)
        dirs = path.split('/')
        dirs, file = dirs[:-1], dirs[-1]
        if dirs and not dirs[0]: dirs = dirs[1:]
        if dirs and not dirs[0]: dirs[0] = '/'
        key = user, host, port, '/'.join(dirs)
        if len(self.ftpcache) > MAXFTPCACHE:
            for k in self.ftpcache.keys():
                if k != key:
                    v = self.ftpcache[k]
                    del self.ftpcache[k]
                    v.close()
        try:
            if not self.ftpcache.has_key(key):
                self.ftpcache[key] = \
                    ftpwrapper(user, passwd, host, port, dirs)
            if not file: type = 'D'
            else: type = 'I'
            for attr in attrs:
                attr, value = splitvalue(attr)
                if attr.lower() == 'type' and \
                   value in ('a', 'A', 'i', 'I', 'd', 'D'):
                    type = value.upper()
            (fp, retrlen) = self.ftpcache[key].retrfile(file, type)
            mtype = mimetypes.guess_type("ftp:" + url)[0]
            headers = ""
            if mtype:
                headers += "Content-Type: %s\n" % mtype
            if retrlen is not None and retrlen >= 0:
                headers += "Content-Length: %d\n" % retrlen
            headers = mimetools.Message(StringIO.StringIO(headers))
            return addinfourl(fp, headers, "ftp:" + url)
        except ftperrors(), msg:
            raise IOError, ('ftp error', msg), sys.exc_info()[2]

    def open_data(self, url, data=None):
        import StringIO, mimetools, time
        try:
            [type, data] = url.split(',', 1)
        except ValueError:
            raise IOError, ('data error', 'bad data URL')
        if not type:
            type = 'text/plain;charset=US-ASCII'
        semi = type.rfind(';')
        if semi >= 0 and '=' not in type[semi:]:
            encoding = type[semi+1:]
            type = type[:semi]
        else:
            encoding = ''
        msg = []
        msg.append('Date: %s'%time.strftime('%a, %d %b %Y %T GMT',
                                            time.gmtime(time.time())))
        msg.append('Content-type: %s' % type)
        if encoding == 'base64':
            import base64
            data = base64.decodestring(data)
        else:
            data = unquote(data)
        msg.append('Content-length: %d' % len(data))
        msg.append('')
        msg.append(data)
        msg = '\n'.join(msg)
        f = StringIO.StringIO(msg)
        headers = mimetools.Message(f, 0)
        f.fileno = None
        return addinfourl(f, headers, url)


class FancyURLopener(URLopener):

    def __init__(self, *args):
        apply(URLopener.__init__, (self,) + args)
        self.auth_cache = {}
        self.tries = 0
        self.maxtries = 10

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        return addinfourl(fp, headers, "http:" + url)

    def http_error_302(self, url, fp, errcode, errmsg, headers, data=None):
        self.tries += 1
        if self.maxtries and self.tries >= self.maxtries:
            if hasattr(self, "http_error_500"):
                meth = self.http_error_500
            else:
                meth = self.http_error_default
            self.tries = 0
            return meth(url, fp, 500,
                        "Internal Server Error: Redirect Recursion", headers)
        result = self.redirect_internal(url, fp, errcode, errmsg, headers,
                                        data)
        self.tries = 0
        return result

    def redirect_internal(self, url, fp, errcode, errmsg, headers, data):
        if headers.has_key('location'):
            newurl = headers['location']
        elif headers.has_key('uri'):
            newurl = headers['uri']
        else:
            return
        void = fp.read()
        fp.close()
        newurl = basejoin(self.type + ":" + url, newurl)
        if data is None:
            return self.open(newurl)
        else:
            return self.open(newurl, data)

    def http_error_301(self, url, fp, errcode, errmsg, headers, data=None):
        return self.http_error_302(url, fp, errcode, errmsg, headers, data)

    def http_error_401(self, url, fp, errcode, errmsg, headers, data=None):
        if not headers.has_key('www-authenticate'):
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        stuff = headers['www-authenticate']
        import re
        match = re.match('[ \t]*([^ \t]+)[ \t]+realm="([^"]*)"', stuff)
        if not match:
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        scheme, realm = match.groups()
        if scheme.lower() != 'basic':
            URLopener.http_error_default(self, url, fp,
                                         errcode, errmsg, headers)
        name = 'retry_' + self.type + '_basic_auth'
        if data is None:
            return getattr(self,name)(url, realm)
        else:
            return getattr(self,name)(url, realm, data)

    def retry_http_basic_auth(self, url, realm, data=None):
        host, selector = splithost(url)
        i = host.find('@') + 1
        host = host[i:]
        user, passwd = self.get_user_passwd(host, realm, i)
        if not (user or passwd): return None
        host = quote(user, safe='') + ':' + quote(passwd, safe='') + '@' + host
        newurl = 'http://' + host + selector
        if data is None:
            return self.open(newurl)
        else:
            return self.open(newurl, data)

    def retry_https_basic_auth(self, url, realm, data=None):
        host, selector = splithost(url)
        i = host.find('@') + 1
        host = host[i:]
        user, passwd = self.get_user_passwd(host, realm, i)
        if not (user or passwd): return None
        host = quote(user, safe='') + ':' + quote(passwd, safe='') + '@' + host
        newurl = '//' + host + selector
        return self.open_https(newurl, data)

    def get_user_passwd(self, host, realm, clear_cache = 0):
        key = realm + '@' + host.lower()
        if self.auth_cache.has_key(key):
            if clear_cache:
                del self.auth_cache[key]
            else:
                return self.auth_cache[key]
        user, passwd = self.prompt_user_passwd(host, realm)
        if user or passwd: self.auth_cache[key] = (user, passwd)
        return user, passwd

    def prompt_user_passwd(self, host, realm):
        import getpass
            
        try:
            user = getpass.getuser("Enter username for %s at %s: " % (realm,
                                                                host))
            passwd = getpass.getpass("Enter password for %s in %s at %s: " %
                (user, realm, host))
            return user, passwd
        except KeyboardInterrupt:
            print
            return None, None


_localhost = None
def localhost():
    global _localhost
    if not _localhost:
        _localhost = socket.gethostbyname('localhost')
    return _localhost

_thishost = None
def thishost():
    global _thishost
    if not _thishost:
        _thishost = socket.gethostbyname(socket.gethostname())
    return _thishost

_ftperrors = None
def ftperrors():
    global _ftperrors
    if not _ftperrors:
        import ftplib
        _ftperrors = ftplib.all_errors
    return _ftperrors

_noheaders = None
def noheaders():
    global _noheaders
    if not _noheaders:
        import mimetools
        import StringIO
        _noheaders = mimetools.Message(StringIO.StringIO(), 0)
        _noheaders.fp.close()
    return _noheaders


class ftpwrapper:

    def __init__(self, user, passwd, host, port, dirs):
        self.user = user
        self.passwd = passwd
        self.host = host
        self.port = port
        self.dirs = dirs
        self.init()

    def init(self):
        import ftplib
        self.busy = 0
        self.ftp = ftplib.FTP()
        self.ftp.connect(self.host, self.port)
        self.ftp.login(self.user, self.passwd)
        for dir in self.dirs:
            self.ftp.cwd(dir)

    def retrfile(self, file, type):
        import ftplib
        self.endtransfer()
        if type in ('d', 'D'): cmd = 'TYPE A'; isdir = 1
        else: cmd = 'TYPE ' + type; isdir = 0
        try:
            self.ftp.voidcmd(cmd)
        except ftplib.all_errors:
            self.init()
            self.ftp.voidcmd(cmd)
        conn = None
        if file and not isdir:
            try:
                self.ftp.nlst(file)
            except ftplib.error_perm, reason:
                raise IOError, ('ftp error', reason), sys.exc_info()[2]
            self.ftp.voidcmd(cmd)
            try:
                cmd = 'RETR ' + file
                conn = self.ftp.ntransfercmd(cmd)
            except ftplib.error_perm, reason:
                if str(reason)[:3] != '550':
                    raise IOError, ('ftp error', reason), sys.exc_info()[2]
        if not conn:
            # Set transfer mode to ASCII!
            self.ftp.voidcmd('TYPE A')
            # Try a directory listing
            if file: cmd = 'LIST ' + file
            else: cmd = 'LIST'
            conn = self.ftp.ntransfercmd(cmd)
        self.busy = 1
        return (addclosehook(conn[0].makefile('rb'),
                             self.endtransfer), conn[1])
    def endtransfer(self):
        if not self.busy:
            return
        self.busy = 0
        try:
            self.ftp.voidresp()
        except ftperrors():
            pass

    def close(self):
        self.endtransfer()
        try:
            self.ftp.close()
        except ftperrors():
            pass

class addbase:

    def __init__(self, fp):
        self.fp = fp
        self.read = self.fp.read
        self.readline = self.fp.readline
        if hasattr(self.fp, "readlines"): self.readlines = self.fp.readlines
        if hasattr(self.fp, "fileno"): self.fileno = self.fp.fileno

    def __repr__(self):
        return '<%s at %s whose fp = %s>' % (self.__class__.__name__,
                                             `id(self)`, `self.fp`)

    def close(self):
        self.read = None
        self.readline = None
        self.readlines = None
        self.fileno = None
        if self.fp: self.fp.close()
        self.fp = None

class addclosehook(addbase):

    def __init__(self, fp, closehook, *hookargs):
        addbase.__init__(self, fp)
        self.closehook = closehook
        self.hookargs = hookargs

    def close(self):
        addbase.close(self)
        if self.closehook:
            apply(self.closehook, self.hookargs)
            self.closehook = None
            self.hookargs = None

class addinfo(addbase):

    def __init__(self, fp, headers):
        addbase.__init__(self, fp)
        self.headers = headers

    def info(self):
        return self.headers

class addinfourl(addbase):

    def __init__(self, fp, headers, url):
        addbase.__init__(self, fp)
        self.headers = headers
        self.url = url

    def info(self):
        return self.headers

    def geturl(self):
        return self.url


def basejoin(base, url):
    type, path = splittype(url)
    if type:
        return url
    host, path = splithost(path)
    type, basepath = splittype(base)
    if host:
        if type: return type + '://' + host + path
        else:
            return url
    host, basepath = splithost(basepath) # inherit host
    basepath, basetag = splittag(basepath) # remove extraneous cruft
    basepath, basequery = splitquery(basepath) # idem
    if path[:1] != '/':
        if path[:1] in ('#', '?'):
            i = len(basepath)
        else:
            i = basepath.rfind('/')
        if i < 0:
            if host:
                basepath = '/'
            else:
                basepath = ''
        else:
            basepath = basepath[:i+1]
        while basepath and path[:3] == '../':
            path = path[3:]
            i = basepath[:-1].rfind('/')
            if i > 0:
                basepath = basepath[:i+1]
            elif i == 0:
                basepath = '/'
                break
            else:
                basepath = ''

        path = basepath + path
    if host and path and path[0] != '/':
        path = '/' + path
    if type and host: return type + '://' + host + path
    elif type: return type + ':' + path
    elif host: return '//' + host + path
    else: return path

def toBytes(url):
    if type(url) is types.UnicodeType:
        try:
            url = url.encode("ASCII")
        except UnicodeError:
            raise UnicodeError("URL " + repr(url) +
                               " contains non-ASCII characters")
    return url

def unwrap(url):
    url = url.strip()
    if url[:1] == '<' and url[-1:] == '>':
        url = url[1:-1].strip()
    if url[:4] == 'URL:': url = url[4:].strip()
    return url

_typeprog = None
def splittype(url):
    global _typeprog
    if _typeprog is None:
        import re
        _typeprog = re.compile('^([^/:]+):')

    match = _typeprog.match(url)
    if match:
        scheme = match.group(1)
        return scheme.lower(), url[len(scheme) + 1:]
    return None, url

_hostprog = None
def splithost(url):
    global _hostprog
    if _hostprog is None:
        import re
        _hostprog = re.compile('^//([^/]*)(.*)$')

    match = _hostprog.match(url)
    if match: return match.group(1, 2)
    return None, url

_userprog = None
def splituser(host):
    global _userprog
    if _userprog is None:
        import re
        _userprog = re.compile('^(.*)@(.*)$')

    match = _userprog.match(host)
    if match: return map(unquote, match.group(1, 2))
    return None, host

_passwdprog = None
def splitpasswd(user):
    global _passwdprog
    if _passwdprog is None:
        import re
        _passwdprog = re.compile('^([^:]*):(.*)$')

    match = _passwdprog.match(user)
    if match: return match.group(1, 2)
    return user, None

_portprog = None
def splitport(host):
    global _portprog
    if _portprog is None:
        import re
        _portprog = re.compile('^(.*):([0-9]+)$')

    match = _portprog.match(host)
    if match: return match.group(1, 2)
    return host, None

_nportprog = None
def splitnport(host, defport=-1):
    global _nportprog
    if _nportprog is None:
        import re
        _nportprog = re.compile('^(.*):(.*)$')

    match = _nportprog.match(host)
    if match:
        host, port = match.group(1, 2)
        try:
            if not port: raise ValueError, "no digits"
            nport = int(port)
        except ValueError:
            nport = None
        return host, nport
    return host, defport

_queryprog = None
def splitquery(url):
    global _queryprog
    if _queryprog is None:
        import re
        _queryprog = re.compile('^(.*)\?([^?]*)$')

    match = _queryprog.match(url)
    if match: return match.group(1, 2)
    return url, None

_tagprog = None
def splittag(url):
    global _tagprog
    if _tagprog is None:
        import re
        _tagprog = re.compile('^(.*)#([^#]*)$')

    match = _tagprog.match(url)
    if match: return match.group(1, 2)
    return url, None

def splitattr(url):
    words = url.split(';')
    return words[0], words[1:]

_valueprog = None
def splitvalue(attr):
    global _valueprog
    if _valueprog is None:
        import re
        _valueprog = re.compile('^([^=]*)=(.*)$')

    match = _valueprog.match(attr)
    if match: return match.group(1, 2)
    return attr, None

def splitgophertype(selector):
    if selector[:1] == '/' and selector[1:2]:
        return selector[1], selector[2:]
    return None, selector

def unquote(s):
    mychr = chr
    myatoi = int
    list = s.split('%')
    res = [list[0]]
    myappend = res.append
    del list[0]
    for item in list:
        if item[1:2]:
            try:
                myappend(mychr(myatoi(item[:2], 16))
                     + item[2:])
            except ValueError:
                myappend('%' + item)
        else:
            myappend('%' + item)
    return "".join(res)

def unquote_plus(s):
    if '+' in s:
        # replace '+' with ' '
        s = ' '.join(s.split('+'))
    return unquote(s)

always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')

_fast_safe_test = always_safe + '/'
_fast_safe = None

def _fast_quote(s):
    global _fast_safe
    if _fast_safe is None:
        _fast_safe = {}
        for c in _fast_safe_test:
            _fast_safe[c] = c
    res = list(s)
    for i in range(len(res)):
        c = res[i]
        if not _fast_safe.has_key(c):
            res[i] = '%%%02X' % ord(c)
    return ''.join(res)

def quote(s, safe = '/'):
    safe = always_safe + safe
    if _fast_safe_test == safe:
        return _fast_quote(s)
    res = list(s)
    for i in range(len(res)):
        c = res[i]
        if c not in safe:
            res[i] = '%%%02X' % ord(c)
    return ''.join(res)

def quote_plus(s, safe = ''):
    if ' ' in s:
        l = s.split(' ')
        for i in range(len(l)):
            l[i] = quote(l[i], safe)
        return '+'.join(l)
    else:
        return quote(s, safe)

def urlencode(query,doseq=0):

    if hasattr(query,"items"):
        query = query.items()
    else:
        try:
            x = len(query)
            if len(query) and type(query[0]) != types.TupleType:
                raise TypeError
        except TypeError:
            ty,va,tb = sys.exc_info()
            raise TypeError, "not a valid non-string sequence or mapping object", tb

    l = []
    if not doseq:
        for k, v in query:
            k = quote_plus(str(k))
            v = quote_plus(str(v))
            l.append(k + '=' + v)
    else:
        for k, v in query:
            k = quote_plus(str(k))
            if type(v) == types.StringType:
                v = quote_plus(v)
                l.append(k + '=' + v)
            elif type(v) == types.UnicodeType:
                v = quote_plus(v.encode("ASCII","replace"))
                l.append(k + '=' + v)
            else:
                try:
                    x = len(v)
                except TypeError:
                    v = quote_plus(str(v))
                    l.append(k + '=' + v)
                else:
                    for elt in v:
                        l.append(k + '=' + quote_plus(str(elt)))
    return '&'.join(l)

def getproxies_environment():
    proxies = {}
    for name, value in os.environ.items():
        name = name.lower()
        if value and name[-6:] == '_proxy':
            proxies[name[:-6]] = value
    return proxies

getproxies = getproxies_environment

def proxy_bypass(host):
    return 0

# Test and time quote() and unquote()
def test1():
    import time
    s = ''
    for i in range(256): s = s + chr(i)
    s = s*4
    t0 = time.time()
    qs = quote(s)
    uqs = unquote(qs)
    t1 = time.time()
    if uqs != s:
        print 'Wrong!'
    print `s`
    print `qs`
    print `uqs`
    print round(t1 - t0, 3), 'sec'


def reporthook(blocknum, blocksize, totalsize):
    print "Block number: %d, Block size: %d, Total size: %d" % (
        blocknum, blocksize, totalsize)

# Test program
def test(args=[]):
    if not args:
        args = [
            '/etc/passwd',
            'file:/etc/passwd',
            'file://localhost/etc/passwd',
            'ftp://ftp.python.org/pub/python/README',
##          'gopher://gopher.micro.umn.edu/1/',
            'http://www.python.org/index.html',
            ]
        if hasattr(URLopener, "open_https"):
            args.append('https://synergy.as.cmu.edu/~geek/')
    try:
        for url in args:
            print '-'*10, url, '-'*10
            fn, h = urlretrieve(url, None, reporthook)
            print fn
            if h:
                print '======'
                for k in h.keys(): print k + ':', h[k]
                print '======'
            fp = open(fn, 'rb')
            data = fp.read()
            del fp
            if '\r' in data:
                table = string.maketrans("", "")
                data = data.translate(table, "\r")
            print data
            fn, h = None, None
        print '-'*40
    finally:
        urlcleanup()

def main():
    import getopt, sys
    try:
        opts, args = getopt.getopt(sys.argv[1:], "th")
    except getopt.error, msg:
        print msg
        print "Use -h for help"
        return
    t = 0
    for o, a in opts:
        if o == '-t':
            t = t + 1
        if o == '-h':
            print "Usage: python urllib.py [-t] [url ...]"
            print "-t runs self-test;",
            print "otherwise, contents of urls are printed"
            return
    if t:
        if t > 1:
            test1()
        test(args)
    else:
        if not args:
            print "Use -h for help"
        for url in args:
            print urlopen(url).read(),

# Run test program when run as a script
if __name__ == '__main__':
    main()
