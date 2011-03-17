#
# default.py
#
# The default script run by the "Python" application in Series 60 Python
# environment. Offers menu options for running scripts that are found in
# application's directory, or in the \my -directory below it (this is
# where the application manager copies the plain Python scripts sent to
# device's inbox), as well as for launching interactive Python console. 
#     
# Copyright (c) 2005-2007 Nokia Corporation
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
import appuifw
import series60_console
import e32

class SelfClearingNamespace:
    def __init__(self):
        self.namespace={'__builtins__': __builtins__,
                        '__name__': '__main__'}
    def __del__(self):
        # Here's a subtle case. The default namespace is deleted at interpreter exit, 
        # but these namespaces aren't since all but the most trivial scripts create 
        # reference cycles between the functions defined in the script and the namespace of 
        # the script. To avoid this we explicitly clear the old namespace to break these 
        # reference cycles.    
        self.namespace.clear()
    
script_namespace = SelfClearingNamespace()

def query_and_exec():
    
    def is_py(x):
        ext=os.path.splitext(x)[1].lower()
        return ext == '.py' or ext == '.pyc' or ext == '.pyo'
    script_list = []
    for nickname,path in script_dirs:
        if os.path.exists(path):
            script_list += map(lambda x: (nickname+x,path+'\\'+x),\
                               map(lambda x: unicode(x,'utf-8'),
                                   filter(is_py, os.listdir(path))))
           
    index = appuifw.selection_list(map(lambda x: unicode(x[0]), script_list))
    # We make a fresh, clean namespace every time we run a new script, but 
    # use the old namespace for the interactive console and btconsole sessions.
    # This allows you to examine the script environment in a console
    # session after running a script. 
    global script_namespace
    
    script_namespace = SelfClearingNamespace()
    if index >= 0:
        execfile(script_list[index][1].encode('utf-8'), script_namespace.namespace)

def exec_interactive():
    import interactive_console
    interactive_console.Py_console(my_console).interactive_loop(script_namespace.namespace)

def exec_btconsole():
    import btconsole
    btconsole.main(script_namespace.namespace)

def menu_action(f):
    appuifw.app.menu = []
    saved_exit_key_handler = appuifw.app.exit_key_handler

    try:
        try:
            f()
        finally:
            appuifw.app.exit_key_handler = saved_exit_key_handler
            appuifw.app.title = u'Python'
            init_options_menu()
            appuifw.app.body = my_console.text
            appuifw.app.screen='normal'
            sys.stderr = sys.stdout = my_console
    except:
        import traceback
        traceback.print_exc()

def init_options_menu():
    appuifw.app.menu = [(u"Run script",\
                         lambda: menu_action(query_and_exec)),
                        (u"Interactive console",\
                         lambda: menu_action(exec_interactive)),\
                        (u"Bluetooth console",\
                         lambda: menu_action(exec_btconsole)),\
                        (u"About Python",\
                         lambda: appuifw.note(u"See www.python.org for more information.", "info"))]
if(e32.s60_version_info>=(3,0)):
    script_dirs = [(u'c:','c:\\python'),
                   (u'e:','e:\\python')]
    for path in ('c:\\python\\lib','e:\\python\\lib'):
        if os.path.exists(path):
            sys.path.append(path)
else:
    scriptshell_dir = os.path.split(appuifw.app.full_name())[0]
    script_dirs = [(u'', scriptshell_dir),
                   (u'my\\', scriptshell_dir+'\\my')]
my_console = series60_console.Console()
appuifw.app.body = my_console.text
sys.stderr = sys.stdout = my_console
from e32 import _stdo
_stdo(u'c:\\python_error.log')         # low-level error output
init_options_menu()
print str(copyright)+"\nVersion "+e32.pys60_version
