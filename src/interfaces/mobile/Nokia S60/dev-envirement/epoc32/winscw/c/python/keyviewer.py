#
# keyviewer.py
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
import graphics
import e32

keyboard_state={}
last_keycode=0

def draw_state():
    canvas.clear()
    canvas.text((0,12),u'Scancodes of pressed keys:',0x008000)
    canvas.text((0,24),u' '.join([unicode(k) for k in keyboard_state if keyboard_state[k]]))
    canvas.text((0,36),u' '.join([unicode(hex(k)) for k in keyboard_state if keyboard_state[k]]))
    canvas.text((0,48),u'Last received keycode:', 0x008000)    
    canvas.text((0,60),u'%s (0x%x)'%(last_keycode,last_keycode))
    
def callback(event):
    global last_keycode
    if event['type'] == appuifw.EEventKeyDown:
        keyboard_state[event['scancode']]=1
    elif event['type'] == appuifw.EEventKeyUp:
        keyboard_state[event['scancode']]=0
    elif event['type'] == appuifw.EEventKey:
        last_keycode=event['keycode']
    draw_state()

canvas=appuifw.Canvas(event_callback=callback,
                      redraw_callback=lambda rect:draw_state())
appuifw.app.body=canvas

lock=e32.Ao_lock()
appuifw.app.exit_key_handler=lock.signal
lock.wait()
