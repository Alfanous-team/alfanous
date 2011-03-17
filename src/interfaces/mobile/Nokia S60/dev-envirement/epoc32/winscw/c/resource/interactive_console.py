#
# interactive_console.py
#
# An implementation of a trivial interactive Python console for
# Series 60 Python environment. Based on 'code' module and
# 'series60_console'.
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

import appuifw
from key_codes import EKeyDevice3

class Py_console:
    def __init__(self, console):
        self.co = console
        self.co.control.bind(EKeyDevice3, self.handle_ok_press)
        self.history = ['','','','','']
        self.history_item = 4

    def handle_ok_press(self):
        self.co.write(u'\n')
        self.co.input_wait_lock.signal()

    def readfunc(self, prompt):
        self.co.write(unicode(prompt))
        user_input = self.co.readline()
        self.history.append(user_input)
        self.history.pop(0)
        self.history_item = 4
        return user_input

    def previous_input(self):
        if self.history_item == -1:
            return
        elif self.history_item == 4:
            self.line_beg = self.co.control.len()
        else:
            self.co.control.delete(self.line_beg,
                                   self.line_beg+\
                                   len(self.history[self.history_item]))
        self.co.control.set_pos(self.line_beg)
        self.co.write(self.history[self.history_item])
        self.history_item -= 1

    def interactive_loop(self, scope = locals()):
        import code
        appuifw.app.menu.append((u"Previous command", self.previous_input))
        self.co.clear()
        code.interact(None, self.readfunc, scope)
        self.co.control.bind(EKeyDevice3, None)
        self.history = []
        appuifw.app.menu = []

if __name__ == '__main__':
    try:
        console = my_console
    except NameError:
        import series60_console
        console = series60_console.Console()
    appuifw.app.body = console.control
    Py_console(console).interactive_loop()
