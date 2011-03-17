# Copyright (c) 2005 Nokia Corporation
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


import sys
import os
import socket
import e32
import thread

class socket_stdio:
    def __init__(self,sock):
        self.socket=sock
        self.writebuf=[]
        self.readbuf=[]
        self.history=['pr()']
        self.histidx=0
        self.socket_thread_id=thread.get_ident()
        self.terminal_encoding='latin1'
    def _read(self,n=1):
        if thread.get_ident() != self.socket_thread_id:
            raise IOError("read() from thread that doesn't own the socket")
        try:
            return self.socket.recv(n)
        except socket.error:
            raise EOFError("Socket error: %s %s"%(sys.exc_info()[0:2]))
    def _write(self,data):
        try:
            # If given unicode data, encode it according to the
            # current terminal encoding. Default encoding is latin1.
            if type(data) is unicode:
                data=data.encode(self.terminal_encoding,'replace')
            return self.socket.send(data.replace('\n','\r\n'))
        except socket.error:
            raise IOError("Socket error: %s %s"%(sys.exc_info()[0:2]))
    def read(self,n=1):
        # if read buffer is empty, read some characters.
        # try to read at least 32 characters into the buffer.
        if len(self.readbuf)==0:
            chars=self._read(max(32,n))
            self.readbuf=chars
        readchars,self.readbuf=self.readbuf[0:n],self.readbuf[n:]
        return readchars
    def _unread(self,str):
        self.readbuf=str+self.readbuf
    def write(self,str):
        self.writebuf.append(str)
        if '\n' in self.writebuf:
            self.flush()
    def flush(self):
        if thread.get_ident() == self.socket_thread_id:
            self._write(''.join(self.writebuf))
            self.writebuf=[]
    def readline(self,n=None):
        buffer=[]
        while 1:
            chars=self.read(32)
            for i in xrange(len(chars)):
                ch=chars[i]
            	if ch == '\n' or ch == '\r':   # return
            	    buffer.append('\n')
            	    self.write('\n')
                    self._unread(chars[i+1:]) #leave
                    line=''.join(buffer)
                    histline=line.rstrip()
                    if len(histline)>0:
                        self.history.append(histline)
                        self.histidx=0
            	    return line
            	elif ch == '\177' or ch == '\010': # backspace
                    if len(buffer)>0:
                        self.write('\010 \010') # erase character from the screen
                        del buffer[-1:] # and from the buffer
                elif ch == '\004': # ctrl-d
                    raise EOFError
                elif ch == '\020' or ch == '\016': # ctrl-p, ctrl-n                  
                    self.histidx=(self.histidx+{
                        '\020':-1,'\016':1}[ch])%len(self.history)
                    #erase current line from the screen
                    self.write(('\010 \010'*len(buffer)))
                    buffer=list(self.history[self.histidx])
                    self.write(''.join(buffer))
                    self.flush()
                elif ch == '\025':
                    self.write(('\010 \010'*len(buffer)))
                    buffer=[]
            	else:
            	    self.write(ch)
            	    buffer.append(ch)
            	if n and len(buffer)>=n:
            	    return ''.join(buffer)
            self.flush()

def _readfunc(prompt=""):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    return sys.stdin.readline().rstrip()

def connect(address=None):
    """Form an RFCOMM socket connection to the given address. If
    address is not given or None, query the user where to connect. The
    user is given an option to save the discovered host address and
    port to a configuration file so that connection can be done
    without discovery in the future.

    Return value: opened Bluetooth socket or None if the user cancels
    the connection.
    """
    
    # Bluetooth connection
    sock=socket.socket(socket.AF_BT,socket.SOCK_STREAM)

    if not address:
        import appuifw
        CONFIG_DIR='c:/system/apps/python'
        CONFIG_FILE=os.path.join(CONFIG_DIR,'btconsole_conf.txt')
        try:
            f=open(CONFIG_FILE,'rt')
            try:
                config=eval(f.read())
            finally:
                f.close()
        except:
            config={}
    
        address=config.get('default_target','')
    
        if address:
            choice=appuifw.popup_menu([u'Default host',
                                       u'Other...'],u'Connect to:')
            if choice==1:
                address=None
            if choice==None:
                return None # popup menu was cancelled.    
        if not address:
            print "Discovering..."
            try:
                addr,services=socket.bt_discover()
            except socket.error, err:
                if err[0]==2: # "no such file or directory"
                    appuifw.note(u'No serial ports found.','error')
                elif err[0]==4: # "interrupted system call"
                    print "Cancelled by user."
                elif err[0]==13: # "permission denied"
                    print "Discovery failed: permission denied."
                else:
                    raise
                return None
            print "Discovered: %s, %s"%(addr,services)
            if len(services)>1:
                import appuifw
                choices=services.keys()
                choices.sort()
                choice=appuifw.popup_menu([unicode(services[x])+": "+x
                                           for x in choices],u'Choose port:')
                port=services[choices[choice]]
            else:
                port=services[services.keys()[0]]
            address=(addr,port)
            choice=appuifw.query(u'Set as default?','query')
            if choice:
                config['default_target']=address
                # make sure the configuration file exists.
                if not os.path.isdir(CONFIG_DIR):
                    os.makedirs(CONFIG_DIR)
                f=open(CONFIG_FILE,'wt')
                f.write(repr(config))
                f.close()
                
    print "Connecting to "+str(address)+"...",
    try:
        sock.connect(address)
    except socket.error, err:
        if err[0]==54: # "connection refused"
            appuifw.note(u'Connection refused.','error')
            return None
        raise
    print "OK."
    return sock

class _printer:
    def __init__(self,message):
        self.message=message
    def __repr__(self):
        return self.message
    def __call__(self):
        print self.message

_commandhelp=_printer('''Commands:
    Backspace   erase
    C-p, C-n    command history prev/next
    C-u         discard current line
    C-d         quit

If the Pyrepl for Series 60 library is installed, you can start the
full featured Pyrepl line editor by typing "pr()".

execfile commands for scripts found in /system/apps/python/my are
automatically entered into the history at startup, so you can run a
script directly by just selecting the start command with ctrl-p/n.''')

def pr(names=None):    
    try:
        import pyrepl.socket_console
        import pyrepl.python_reader
    except ImportError:
        print "Pyrepl for Series 60 library is not installed."
        return
    if names is None:
        names=locals()
    print '''Starting Pyrepl. Type "prhelp()" for a list of commands.'''
    socketconsole=pyrepl.socket_console.SocketConsole(sys.stdin.socket)
    readerconsole=pyrepl.python_reader.ReaderConsole(socketconsole,names)
    readerconsole.run_user_init_file()
    readerconsole.interact()

STARTUPFILE='c:\\startup.py'

DEFAULT_BANNER='''Python %s on %s
Type "copyright", "credits" or "license" for more information.
Type "commands" to see the commands available in this simple line editor.''' % (sys.version, sys.platform)

def interact(banner=None,readfunc=None,names=None):
    """Thin wrapper around code.interact that will
    - load a startup file ("""+STARTUPFILE+""") if it exists.
    - add the scripts in script directories to command history, if
      the standard input has the .history attribute.
    - call code.interact
    - all exceptions are trapped and all except SystemExit are re-raised."""
    if names is None:
        names=locals()
    if readfunc is None:
        readfunc=_readfunc
    names.update({'pr': lambda: pr(names),
                  'commands': _commandhelp,
                  'exit': 'Press Ctrl-D on an empty line to exit',
                  'quit': 'Press Ctrl-D on an empty line to exit'})
    if os.path.exists(STARTUPFILE):
        print "Running %s..."%STARTUPFILE
        execfile(STARTUPFILE,globals(),names)
    if hasattr(sys.stdin,"history"):
        # Add into command history the start commands for Python scripts
        # found in these directories.
        PYTHONDIRS=['c:\\system\\apps\\python\\my','e:\\system\\apps\\python\\my']
        for k in PYTHONDIRS:
            if os.path.isdir(k):
                sys.stdin.history+=["execfile("+repr(os.path.join(k,x))+")"
                                    for x in os.listdir(k)
                                    if x.endswith('.py')]            
    try:
        import code
        # If banner is None, code.interact would print its' own default
        # banner. In that case it makes sense for us to print our help.
        if banner is None:
            banner=DEFAULT_BANNER
        code.interact(banner,readfunc,names)
    except SystemExit:
        print "SystemExit raised."
    except:
        print "Interpreter threw an exception:"
        import traceback
        traceback.print_exc()
        raise
    print "Interactive interpreter finished."


def run_with_redirected_io(sock, func, *args, **kwargs):
    """Call func with sys.stdin, sys.stdout and sys.stderr redirected
    to the given socket, using a wrapper that implements a rudimentary
    line editor with command history. The streams are restored when
    the function exits. If this function is called from the UI thread,
    an exit key handler is installed for the duration of func's
    execution to close the socket.

    Any extra arguments are passed to the function. Return whatever
    the function returns."""
    # Redirect input and output to the socket.
    sockio=socket_stdio(sock)        
    real_io=(sys.stdin,sys.stdout,sys.stderr)
    real_rawinput=__builtins__['raw_input']
    if e32.is_ui_thread():
        import appuifw
        old_exit_key_handler=appuifw.app.exit_key_handler
        def my_exit_key_handler():
            # The standard output and standard error are redirected to
            # previous values already at this point so that we don't
            # miss any messages that the dying program may print.
            sys.stdout=real_io[1]
            sys.stderr=real_io[2]
            # Shutdown the socket to end any reads from stdin and make
            # them raise an EOFError.
            sock.shutdown(2)
            sock.close()
            if e32.is_ui_thread():
                appuifw.app.exit_key_handler=old_exit_key_handler
        appuifw.app.exit_key_handler=my_exit_key_handler
    try:
        (sys.stdin,sys.stdout,sys.stderr)=(sockio,sockio,sockio)
        # Replace the Python raw_input implementation with our
        # own. For some reason the built-in raw_input doesn't flush
        # the output stream after writing the prompt, and The Powers
        # That Be refuse to fix this. See Python bug 526382.
        __builtins__['raw_input']=_readfunc
        return func(*args,**kwargs)
    finally:
        (sys.stdin,sys.stdout,sys.stderr)=real_io
        __builtins__['raw_input']=real_rawinput
        if e32.is_ui_thread():
            appuifw.app.exit_key_handler=old_exit_key_handler

def inside_btconsole():
    return isinstance(sys.stdout,socket_stdio)

def run(banner=None,names=None):
    """Connect to a remote host via Bluetooth and run an interactive
    console over that connection. If sys.stdout is already connected
    to a Bluetooth console instance, use that connection instead of
    starting a new one. If names is given, use that as the local
    namespace, otherwise use namespace of module __main__."""
    if names is None:
        import __main__
        names=__main__.__dict__
    if inside_btconsole():
        # already inside btconsole, no point in connecting again.
        interact(banner,None,names)
    else:
        sock=None
        try:            
            sock=connect()
            if sock is None:
                print "Connection failed."
                return
            sock.send('\r\nConnected.\r\n')
            try:
                run_with_redirected_io(sock,interact,banner,None,names)
            except IOError, e:
                print "Disconnected: %s"%e                
        finally:
            if sock: sock.close()

def main(names=None):
    """The same as execfile()ing the btconsole.py script. Set the
    application title and run run() with the default banner."""
    if e32.is_ui_thread():
        import appuifw
        old_app_title=appuifw.app.title
        appuifw.app.title=u'BTConsole'
    try:
        run(None, names)
    finally:
        if e32.is_ui_thread():
            appuifw.app.title=old_app_title
    print "Done."

__all__=['connect','run','interact','main','run_with_redirected_io',
         'inside_btconsole']

if __name__ == "__main__":
    main()
