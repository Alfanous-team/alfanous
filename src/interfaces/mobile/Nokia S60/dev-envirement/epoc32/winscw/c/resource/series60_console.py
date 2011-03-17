#
# series60_console.py
#
# A simple console class for Series 60 Python environment.
# Based on 'appuifw.Text' widget.
#     
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
#

import sys
import appuifw
import e32

class Console:
    def __init__(self):
        from e32 import Ao_lock
        from key_codes import EKeyEnter
        self.input_wait_lock = Ao_lock()
        self.input_stopped = False
        self.control = self.text = appuifw.Text()
        self.text.bind(EKeyEnter, self.input_wait_lock.signal)
        self.savestderr = sys.stderr
        self.savestdout = sys.stdout
        self.savestdin = sys.stdin
        sys.stderr = self
        sys.stdout = self
        sys.stdin = self
        self.writebuf=[]
        def make_flusher(text,buf):    
            def doflush():
                text.add(unicode(''.join(buf)))
                del buf[:]
                if text.len() > 1500:
                    text.delete(0, text.len()-500)
            return doflush
        self._doflush=make_flusher(self.text,self.writebuf)
        self._flushgate=e32.ao_callgate(self._doflush)

    def __del__(self):
        sys.stderr = self.savestderr
        sys.stdout = self.savestdout
        sys.stdin = self.savestdin
        self.control = self.text = None

    def stop_input(self):
        self.input_stopped = True
        self.input_wait_lock.signal()

    def clear(self):
        self.text.clear()

    def write(self, obj):
        self.writebuf.append(obj)            
        self.flush()
        
    def writelines(self, list):
        self.write(''.join(list))

    def flush(self):
        if len(self.writebuf)>0:
            if e32.is_ui_thread():
                self._doflush()
            else:
                self._flushgate()
    def readline(self):
        if not e32.is_ui_thread():
            raise IOError('Cannot call readline from non-UI thread')
        pos = self.text.get_pos()
        len = self.text.len()
        save_exit_key_handler = appuifw.app.exit_key_handler
        appuifw.app.exit_key_handler = self.stop_input
        self.input_wait_lock.wait()
        appuifw.app.exit_key_handler = save_exit_key_handler
        if self.input_stopped:
            self.text.add(u'\n')
            self.input_stopped = False
            raise EOFError
        new_pos = self.text.get_pos()
        new_len = self.text.len()
        if ((new_pos <= pos) | ((new_len-len) != (new_pos-pos))):
            new_pos = self.text.len()
            self.text.set_pos(new_pos)
            self.text.add(u'\n')
            user_input = ''
        else:
            user_input = (self.text.get(pos, new_pos-pos-1))
        # Python 2.2's raw_input expects a plain string, not
        # a unicode object. Here we just assume utf8 encoding.
        return user_input.encode('utf8')
