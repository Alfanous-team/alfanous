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


import appuifw, e32, os
from graphics import *
import key_codes

appuifw.app.screen='full'
appuifw.app.body=canvas=appuifw.Canvas()
backup_image=Image.new(canvas.size)
canvas.clear(0)
center=[0,0]
zoom=1
zoomstepindex=0
screensize=canvas.size
screenrect=(0,0,screensize[0],screensize[1])
step=30
textloc=(screensize[0]*0.3,screensize[1]*.5)

if e32.in_emulator():
    imagedir=u'c:\\images'
else:
    imagedir=u'e:\\images'
files=map(unicode,os.listdir(imagedir))

index=appuifw.selection_list(files)

lock=e32.Ao_lock()

def fullupdate():
    backup_image.clear(bgcolor)
    update()
    
def nextpic():
    global index,finished
    index=(index+1)%len(files)
    finished=1
    loaded_image.stop()
    lock.signal()

def prevpic():
    global index,finished
    index=(index-1)%len(files)
    finished=1
    loaded_image.stop()
    lock.signal()

def zoomin():
    global zoomstepindex,zoom
    if zoomstepindex < (len(zoomsteps)-1):
        zoomstepindex+=1
    zoom=zoomsteps[zoomstepindex]
    fullupdate()

def zoomout():
    global zoomstepindex
    if zoomstepindex > 0:
        zoomstepindex-=1
    zoom=zoomsteps[zoomstepindex]
    backup_image.clear(bgcolor)
    fullupdate()


def isvalidcenter(c):
    iw,ih=(loaded_image.size[0],loaded_image.size[1])
    srcsize=(int(screensize[0]/zoom),int(screensize[1]/zoom))
    vw,vh=(srcsize[0]/2,srcsize[1]/2)    
    return (c[0]+vw<iw and c[0]-vw>=0 and
            c[1]+vh<ih and c[1]-vh>=0)
def move(delta):
    global center
    c=center
    for k in range(1,4):
        t=[c[0]+int(delta[0]*k*20/zoom),
           c[1]+int(delta[1]*k*20/zoom)]
        center=t
        update()

bgcolor=0

canvas.bind(key_codes.EKey3,nextpic)
canvas.bind(key_codes.EKey1,prevpic)
canvas.bind(key_codes.EKey5,zoomin)
canvas.bind(key_codes.EKey0,zoomout)
canvas.bind(key_codes.EKeyLeftArrow,lambda:move((-1,0)))
canvas.bind(key_codes.EKeyRightArrow,lambda:move((1,0)))
canvas.bind(key_codes.EKeyUpArrow,lambda:move((0,-1)))
canvas.bind(key_codes.EKeyDownArrow,lambda:move((0,1)))

def rect_intersection(r1,r2):
    return (max(r1[0],r2[0]),max(r1[1],r2[1]),
            min(r1[2],r2[2]),min(r1[3],r2[3]))
    
def update():
    global zoom
    zoom=zoomsteps[zoomstepindex]
    # We convert the screen rect into image coordinates, compute its
    # intersection with the image rect and transform it back to screen
    # coordinates.
    imgrect=(0,0,loaded_image.size[0],loaded_image.size[1])    
    ss=(int(screensize[0]/zoom),int(screensize[1]/zoom))
    screenrect_imgcoords=(center[0]-ss[0]/2,center[1]-ss[1]/2,
                          center[0]+ss[0]/2,center[1]+ss[1]/2)
    sourcerect=rect_intersection(screenrect_imgcoords,imgrect)
    targetrect=(int((sourcerect[0]-center[0])*zoom+screensize[0]/2),
                int((sourcerect[1]-center[1])*zoom+screensize[1]/2),
                int((sourcerect[2]-center[0])*zoom+screensize[0]/2),
                int((sourcerect[3]-center[1])*zoom+screensize[1]/2))
    backup_image.clear(bgcolor)
    backup_image.blit(loaded_image,source=sourcerect,target=targetrect,scale=1)
    if not finished:
        backup_image.text(textloc,u'Loading....',(255,255,0))
    backup_image.text((0,10),files[index],(0,255,0))
    canvas.blit(backup_image)

global finished
finished=0
def finishload(err):
    global finished
    finished=1

running=1
def quit():
    global running,lock
    running=0
    lock.signal()
    
appuifw.app.exit_key_handler=quit
backup_image.clear(bgcolor)

selected_file=imagedir+"\\"+files[index]
imginfo=Image.inspect(selected_file)
imgsize=imginfo['size']
loaded_image=Image.new(imgsize)

im=None
while running:
    selected_file=imagedir+"\\"+files[index]
    imgsize=Image.inspect(selected_file)['size']
    backup_image.text(textloc,u'Loading.',(255,255,0))
    finished=0
    if imgsize != loaded_image.size:
        loaded_image=Image.new(imgsize)
    loaded_image.load(selected_file, callback=finishload)
    backup_image.text(textloc,u'Loading..',(255,255,0))
    zoomsteps=[1.*screensize[0]/loaded_image.size[0],.25,.5,1]
    zoomstepindex=0
    center=[loaded_image.size[0]/2,loaded_image.size[1]/2]    
    backup_image.text(textloc,u'Loading...',(255,255,0))
    while not finished:
        update()
        e32.ao_sleep(0.5)
    fullupdate()
    lock.wait()
loaded_image=None
backup_image=None
