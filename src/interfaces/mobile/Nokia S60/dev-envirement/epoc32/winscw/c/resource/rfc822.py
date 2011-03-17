# Portions Copyright (c) 2005 Nokia Corporation 
"""RFC 2822 message manipulation."""
# Cleanup and extensions by Eric S. Raymond <esr@thyrsus.com>

import time

__all__ = ["Message","AddressList","parsedate","parsedate_tz","mktime_tz"]

_blanklines = ('\r\n', '\n')            # Optimization for islast()


class Message:
    """Represents a single RFC 2822-compliant message."""

    def __init__(self, fp, seekable = 1):
        if seekable == 1:
            # Exercise tell() to make sure it works
            # (and then assume seek() works, too)
            try:
                fp.tell()
            except (AttributeError, IOError):
                seekable = 0
            else:
                seekable = 1
        self.fp = fp
        self.seekable = seekable
        self.startofheaders = None
        self.startofbody = None
        #
        if self.seekable:
            try:
                self.startofheaders = self.fp.tell()
            except IOError:
                self.seekable = 0
        #
        self.readheaders()
        #
        if self.seekable:
            try:
                self.startofbody = self.fp.tell()
            except IOError:
                self.seekable = 0

    def rewindbody(self):
        if not self.seekable:
            raise IOError, "unseekable file"
        self.fp.seek(self.startofbody)

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
                x = (self.dict[headerseen] + "\n " + line.strip())
                self.dict[headerseen] = x.strip()
                continue
            elif self.iscomment(line):
                continue
            elif self.islast(line):
                break
            headerseen = self.isheader(line)
            if headerseen:
                list.append(line)
                self.dict[headerseen] = line[len(headerseen)+1:].strip()
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

    def isheader(self, line):
        i = line.find(':')
        if i > 0:
            return line[:i].lower()
        else:
            return None

    def islast(self, line):
        return line in _blanklines

    def iscomment(self, line):
        return None

    def getallmatchingheaders(self, name):
        name = name.lower() + ':'
        n = len(name)
        list = []
        hit = 0
        for line in self.headers:
            if line[:n].lower() == name:
                hit = 1
            elif not line[:1].isspace():
                hit = 0
            if hit:
                list.append(line)
        return list

    def getfirstmatchingheader(self, name):
        name = name.lower() + ':'
        n = len(name)
        list = []
        hit = 0
        for line in self.headers:
            if hit:
                if not line[:1].isspace():
                    break
            elif line[:n].lower() == name:
                hit = 1
            if hit:
                list.append(line)
        return list

    def getrawheader(self, name):
        list = self.getfirstmatchingheader(name)
        if not list:
            return None
        list[0] = list[0][len(name) + 1:]
        return ''.join(list)

    def getheader(self, name, default=None):
        try:
            return self.dict[name.lower()]
        except KeyError:
            return default
    get = getheader

    def getheaders(self, name):
        result = []
        current = ''
        have_header = 0
        for s in self.getallmatchingheaders(name):
            if s[0].isspace():
                if current:
                    current = "%s\n %s" % (current, s.strip())
                else:
                    current = s.strip()
            else:
                if have_header:
                    result.append(current)
                current = s[s.find(":") + 1:].strip()
                have_header = 1
        if have_header:
            result.append(current)
        return result

    def getaddr(self, name):
        # New, by Ben Escoto
        alist = self.getaddrlist(name)
        if alist:
            return alist[0]
        else:
            return (None, None)

    def getaddrlist(self, name):
        raw = []
        for h in self.getallmatchingheaders(name):
            if h[0] in ' \t':
                raw.append(h)
            else:
                if raw:
                    raw.append(', ')
                i = h.find(':')
                if i > 0:
                    addr = h[i+1:]
                raw.append(addr)
        alladdrs = ''.join(raw)
        a = AddrlistClass(alladdrs)
        return a.getaddrlist()

    def getdate(self, name):
        try:
            data = self[name]
        except KeyError:
            return None
        return parsedate(data)

    def getdate_tz(self, name):
        try:
            data = self[name]
        except KeyError:
            return None
        return parsedate_tz(data)


    # Access as a dictionary (only finds *last* header of each type):

    def __len__(self):
        return len(self.dict)

    def __getitem__(self, name):
        return self.dict[name.lower()]

    def __setitem__(self, name, value):
        del self[name] # Won't fail if it doesn't exist
        self.dict[name.lower()] = value
        text = name + ": " + value
        lines = text.split("\n")
        for line in lines:
            self.headers.append(line + "\n")

    def __delitem__(self, name):
        name = name.lower()
        if not self.dict.has_key(name):
            return
        del self.dict[name]
        name = name + ':'
        n = len(name)
        list = []
        hit = 0
        for i in range(len(self.headers)):
            line = self.headers[i]
            if line[:n].lower() == name:
                hit = 1
            elif not line[:1].isspace():
                hit = 0
            if hit:
                list.append(i)
        list.reverse()
        for i in list:
            del self.headers[i]

    def setdefault(self, name, default=""):
        lowername = name.lower()
        if self.dict.has_key(lowername):
            return self.dict[lowername]
        else:
            text = name + ": " + default
            lines = text.split("\n")
            for line in lines:
                self.headers.append(line + "\n")
            self.dict[lowername] = default
            return default

    def has_key(self, name):
        return self.dict.has_key(name.lower())

    def keys(self):
        return self.dict.keys()

    def values(self):
        return self.dict.values()

    def items(self):
        return self.dict.items()

    def __str__(self):
        str = ''
        for hdr in self.headers:
            str = str + hdr
        return str


# Utility functions
# -----------------

def unquote(str):
    if len(str) > 1:
        if str[0] == '"' and str[-1:] == '"':
            return str[1:-1]
        if str[0] == '<' and str[-1:] == '>':
            return str[1:-1]
    return str


def quote(str):
    return str.replace('\\', '\\\\').replace('"', '\\"')


def parseaddr(address):
    a = AddressList(address)
    list = a.addresslist
    if not list:
        return (None, None)
    else:
        return list[0]


class AddrlistClass:

    def __init__(self, field):
        self.specials = '()<>@,:;.\"[]'
        self.pos = 0
        self.LWS = ' \t'
        self.CR = '\r\n'
        self.atomends = self.specials + self.LWS + self.CR
        self.phraseends = self.atomends.replace('.', '')
        self.field = field
        self.commentlist = []

    def gotonext(self):
        while self.pos < len(self.field):
            if self.field[self.pos] in self.LWS + '\n\r':
                self.pos = self.pos + 1
            elif self.field[self.pos] == '(':
                self.commentlist.append(self.getcomment())
            else: break

    def getaddrlist(self):
        result = []
        while 1:
            ad = self.getaddress()
            if ad:
                result += ad
            else:
                break
        return result

    def getaddress(self):
        self.commentlist = []
        self.gotonext()

        oldpos = self.pos
        oldcl = self.commentlist
        plist = self.getphraselist()

        self.gotonext()
        returnlist = []

        if self.pos >= len(self.field):
            if plist:
                returnlist = [(' '.join(self.commentlist), plist[0])]

        elif self.field[self.pos] in '.@':
            self.pos = oldpos
            self.commentlist = oldcl
            addrspec = self.getaddrspec()
            returnlist = [(' '.join(self.commentlist), addrspec)]

        elif self.field[self.pos] == ':':
            returnlist = []

            fieldlen = len(self.field)
            self.pos = self.pos + 1
            while self.pos < len(self.field):
                self.gotonext()
                if self.pos < fieldlen and self.field[self.pos] == ';':
                    self.pos = self.pos + 1
                    break
                returnlist = returnlist + self.getaddress()

        elif self.field[self.pos] == '<':
            routeaddr = self.getrouteaddr()

            if self.commentlist:
                returnlist = [(' '.join(plist) + ' (' + \
                         ' '.join(self.commentlist) + ')', routeaddr)]
            else: returnlist = [(' '.join(plist), routeaddr)]

        else:
            if plist:
                returnlist = [(' '.join(self.commentlist), plist[0])]
            elif self.field[self.pos] in self.specials:
                self.pos = self.pos + 1

        self.gotonext()
        if self.pos < len(self.field) and self.field[self.pos] == ',':
            self.pos = self.pos + 1
        return returnlist

    def getrouteaddr(self):
        if self.field[self.pos] != '<':
            return

        expectroute = 0
        self.pos = self.pos + 1
        self.gotonext()
        adlist = ""
        while self.pos < len(self.field):
            if expectroute:
                self.getdomain()
                expectroute = 0
            elif self.field[self.pos] == '>':
                self.pos = self.pos + 1
                break
            elif self.field[self.pos] == '@':
                self.pos = self.pos + 1
                expectroute = 1
            elif self.field[self.pos] == ':':
                self.pos = self.pos + 1
            else:
                adlist = self.getaddrspec()
                self.pos = self.pos + 1
                break
            self.gotonext()

        return adlist

    def getaddrspec(self):
        aslist = []

        self.gotonext()
        while self.pos < len(self.field):
            if self.field[self.pos] == '.':
                aslist.append('.')
                self.pos = self.pos + 1
            elif self.field[self.pos] == '"':
                aslist.append('"%s"' % self.getquote())
            elif self.field[self.pos] in self.atomends:
                break
            else: aslist.append(self.getatom())
            self.gotonext()

        if self.pos >= len(self.field) or self.field[self.pos] != '@':
            return ''.join(aslist)

        aslist.append('@')
        self.pos = self.pos + 1
        self.gotonext()
        return ''.join(aslist) + self.getdomain()

    def getdomain(self):
        sdlist = []
        while self.pos < len(self.field):
            if self.field[self.pos] in self.LWS:
                self.pos = self.pos + 1
            elif self.field[self.pos] == '(':
                self.commentlist.append(self.getcomment())
            elif self.field[self.pos] == '[':
                sdlist.append(self.getdomainliteral())
            elif self.field[self.pos] == '.':
                self.pos = self.pos + 1
                sdlist.append('.')
            elif self.field[self.pos] in self.atomends:
                break
            else: sdlist.append(self.getatom())
        return ''.join(sdlist)

    def getdelimited(self, beginchar, endchars, allowcomments = 1):
        if self.field[self.pos] != beginchar:
            return ''

        slist = ['']
        quote = 0
        self.pos = self.pos + 1
        while self.pos < len(self.field):
            if quote == 1:
                slist.append(self.field[self.pos])
                quote = 0
            elif self.field[self.pos] in endchars:
                self.pos = self.pos + 1
                break
            elif allowcomments and self.field[self.pos] == '(':
                slist.append(self.getcomment())
            elif self.field[self.pos] == '\\':
                quote = 1
            else:
                slist.append(self.field[self.pos])
            self.pos = self.pos + 1

        return ''.join(slist)

    def getquote(self):
        return self.getdelimited('"', '"\r', 0)

    def getcomment(self):
        return self.getdelimited('(', ')\r', 1)

    def getdomainliteral(self):
        return '[%s]' % self.getdelimited('[', ']\r', 0)

    def getatom(self, atomends=None):
        atomlist = ['']
        if atomends is None:
            atomends = self.atomends

        while self.pos < len(self.field):
            if self.field[self.pos] in atomends:
                break
            else: atomlist.append(self.field[self.pos])
            self.pos = self.pos + 1

        return ''.join(atomlist)

    def getphraselist(self):
        plist = []

        while self.pos < len(self.field):
            if self.field[self.pos] in self.LWS:
                self.pos = self.pos + 1
            elif self.field[self.pos] == '"':
                plist.append(self.getquote())
            elif self.field[self.pos] == '(':
                self.commentlist.append(self.getcomment())
            elif self.field[self.pos] in self.phraseends:
                break
            else:
                plist.append(self.getatom(self.phraseends))

        return plist

class AddressList(AddrlistClass):
    def __init__(self, field):
        AddrlistClass.__init__(self, field)
        if field:
            self.addresslist = self.getaddrlist()
        else:
            self.addresslist = []

    def __len__(self):
        return len(self.addresslist)

    def __str__(self):
        return ", ".join(map(dump_address_pair, self.addresslist))

    def __add__(self, other):
        newaddr = AddressList(None)
        newaddr.addresslist = self.addresslist[:]
        for x in other.addresslist:
            if not x in self.addresslist:
                newaddr.addresslist.append(x)
        return newaddr

    def __iadd__(self, other):
        for x in other.addresslist:
            if not x in self.addresslist:
                self.addresslist.append(x)
        return self

    def __sub__(self, other):
        newaddr = AddressList(None)
        for x in self.addresslist:
            if not x in other.addresslist:
                newaddr.addresslist.append(x)
        return newaddr

    def __isub__(self, other):
        for x in other.addresslist:
            if x in self.addresslist:
                self.addresslist.remove(x)
        return self

    def __getitem__(self, index):
        return self.addresslist[index]

def dump_address_pair(pair):
    if pair[0]:
        return '"' + pair[0] + '" <' + pair[1] + '>'
    else:
        return pair[1]

# Parse a date field

_monthnames = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul',
               'aug', 'sep', 'oct', 'nov', 'dec',
               'january', 'february', 'march', 'april', 'may', 'june', 'july',
               'august', 'september', 'october', 'november', 'december']
_daynames = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

_timezones = {'UT':0, 'UTC':0, 'GMT':0, 'Z':0,
              'AST': -400, 'ADT': -300,  # Atlantic (used in Canada)
              'EST': -500, 'EDT': -400,  # Eastern
              'CST': -600, 'CDT': -500,  # Central
              'MST': -700, 'MDT': -600,  # Mountain
              'PST': -800, 'PDT': -700   # Pacific
              }


def parsedate_tz(data):
    if not data:
        return None
    data = data.split()
    if data[0][-1] in (',', '.') or data[0].lower() in _daynames:
        del data[0]
    if len(data) == 3: # RFC 850 date, deprecated
        stuff = data[0].split('-')
        if len(stuff) == 3:
            data = stuff + data[1:]
    if len(data) == 4:
        s = data[3]
        i = s.find('+')
        if i > 0:
            data[3:] = [s[:i], s[i+1:]]
        else:
            data.append('') # Dummy tz
    if len(data) < 5:
        return None
    data = data[:5]
    [dd, mm, yy, tm, tz] = data
    mm = mm.lower()
    if not mm in _monthnames:
        dd, mm = mm, dd.lower()
        if not mm in _monthnames:
            return None
    mm = _monthnames.index(mm)+1
    if mm > 12: mm = mm - 12
    if dd[-1] == ',':
        dd = dd[:-1]
    i = yy.find(':')
    if i > 0:
        yy, tm = tm, yy
    if yy[-1] == ',':
        yy = yy[:-1]
    if not yy[0].isdigit():
        yy, tz = tz, yy
    if tm[-1] == ',':
        tm = tm[:-1]
    tm = tm.split(':')
    if len(tm) == 2:
        [thh, tmm] = tm
        tss = '0'
    elif len(tm) == 3:
        [thh, tmm, tss] = tm
    else:
        return None
    try:
        yy = int(yy)
        dd = int(dd)
        thh = int(thh)
        tmm = int(tmm)
        tss = int(tss)
    except ValueError:
        return None
    tzoffset = None
    tz = tz.upper()
    if _timezones.has_key(tz):
        tzoffset = _timezones[tz]
    else:
        try:
            tzoffset = int(tz)
        except ValueError:
            pass
    if tzoffset:
        if tzoffset < 0:
            tzsign = -1
            tzoffset = -tzoffset
        else:
            tzsign = 1
        tzoffset = tzsign * ( (tzoffset//100)*3600 + (tzoffset % 100)*60)
    tuple = (yy, mm, dd, thh, tmm, tss, 0, 0, 0, tzoffset)
    return tuple


def parsedate(data):
    t = parsedate_tz(data)
    if type(t) == type( () ):
        return t[:9]
    else: return t


def mktime_tz(data):
    if data[9] is None:
        return time.mktime(data[:8] + (-1,))
    else:
        t = time.mktime(data[:8] + (0,))
        return t - data[9] - time.timezone

def formatdate(timeval=None):
    if timeval is None:
        timeval = time.time()
    timeval = time.gmtime(timeval)
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][timeval[6]],
            timeval[2],
            ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][timeval[1]-1],
                                timeval[0], timeval[3], timeval[4], timeval[5])

if __name__ == '__main__':
    pass
