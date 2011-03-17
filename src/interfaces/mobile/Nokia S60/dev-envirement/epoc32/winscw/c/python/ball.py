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

import appuifw
from graphics import *
import e32
from key_codes import *

class Keyboard(object):
    def __init__(self,onevent=lambda:None):
        self._keyboard_state={}
        self._downs={}
        self._onevent=onevent
    def handle_event(self,event):
        if event['type'] == appuifw.EEventKeyDown:
            code=event['scancode']
            if not self.is_down(code):
                self._downs[code]=self._downs.get(code,0)+1
            self._keyboard_state[code]=1
        elif event['type'] == appuifw.EEventKeyUp:
            self._keyboard_state[event['scancode']]=0
        self._onevent()
    def is_down(self,scancode):
        return self._keyboard_state.get(scancode,0)
    def pressed(self,scancode):
        if self._downs.get(scancode,0):
            self._downs[scancode]-=1
            return True
        return False
keyboard=Keyboard()

appuifw.app.screen='full'
img=None
def handle_redraw(rect):
    if img:
        canvas.blit(img)
appuifw.app.body=canvas=appuifw.Canvas(
    event_callback=keyboard.handle_event,
    redraw_callback=handle_redraw)
img=Image.new(canvas.size)

running=1
def quit():
    global running
    running=0
appuifw.app.exit_key_handler=quit

location=[img.size[0]/2,img.size[1]/2]
speed=[0.,0.]
blobsize=16
xs,ys=img.size[0]-blobsize,img.size[1]-blobsize
gravity=0.03
acceleration=0.05

import time
start_time=time.clock()
n_frames=0
# To speed things up, we prerender the text.
labeltext=u'Use arrows to move ball'
textrect=img.measure_text(labeltext, font='normal')[0]
text_img=Image.new((textrect[2]-textrect[0],textrect[3]-textrect[1]))
text_img.clear(0)
text_img.text((-textrect[0],-textrect[1]),labeltext,fill=0xffffff,font='normal')

while running:
    img.clear(0)
    img.blit(text_img, (0,0))
    img.point((location[0]+blobsize/2,location[1]+blobsize/2),
              0x00ff00,width=blobsize)
    handle_redraw(())
    e32.ao_yield()
    speed[0]*=0.999
    speed[1]*=0.999
    speed[1]+=gravity
    location[0]+=speed[0]
    location[1]+=speed[1]
    if location[0]>xs:
        location[0]=xs-(location[0]-xs)
        speed[0]=-0.80*speed[0]
        speed[1]=0.90*speed[1]
    if location[0]<0:
        location[0]=-location[0]
        speed[0]=-0.80*speed[0]
        speed[1]=0.90*speed[1]
    if location[1]>ys:
        location[1]=ys-(location[1]-ys)
        speed[0]=0.90*speed[0]
        speed[1]=-0.80*speed[1]
    if location[1]<0:
        location[1]=-location[1]
        speed[0]=0.90*speed[0]
        speed[1]=-0.80*speed[1]
        
    if keyboard.is_down(EScancodeLeftArrow):  speed[0] -= acceleration
    if keyboard.is_down(EScancodeRightArrow): speed[0] += acceleration
    if keyboard.is_down(EScancodeDownArrow):  speed[1] += acceleration
    if keyboard.is_down(EScancodeUpArrow):    speed[1] -= acceleration
    if keyboard.pressed(EScancodeHash):
        filename=u'e:\\screenshot.png'
        canvas.text((0,32),u'Saving screenshot to:',fill=0xffff00)
        canvas.text((0,48),filename,fill=0xffff00)
        img.save(filename)

    n_frames+=1
end_time=time.clock()
total=end_time-start_time

print "%d frames, %f seconds, %f FPS, %f ms/frame."%(n_frames,total,
                                                     n_frames/total,
                                                     total/n_frames*1000.)
