#
# gles_demo.py
#
# Copyright (c) 2006-2007 Nokia Corporation
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

import appuifw, sys, e32, time
from glcanvas import *
from gles import *
from key_codes import *

class GLESDemo:
  varray = array(GL_BYTE, 3, [
    -1,1,1,  1,1,1,  1,-1,1,  -1,-1,1,
    -1,1,-1, 1,1,-1, 1,-1,-1, -1,-1,-1
  ])

  indices = array(GL_UNSIGNED_BYTE, 3, [
    1,0,3, 1,3,2, 2,6,5, 2,5,1, 7,4,5, 7,5,6,
    0,4,7, 0,7,3, 5,4,0, 5,0,1, 3,7,6, 3,6,2
  ])

  colors = array(GL_UNSIGNED_BYTE, 4, [
    0,255,0,255, 0,0,255,255, 0,255,0,255, 255,0,0,255,
    0,0,255,255, 255,0,0,255, 0,0,255,255, 0,255,0,255
  ])

  texcoords = array(GL_BYTE, 2, [
    0,0, 0,1, 1,0, 1,1, 0,0, 0,1, 1,0, 1,1
  ] )
  
  # initialize texture array (just used for passing texture data to glTexImage2D or glTexSubImage2D...)
  texture = array(GL_UNSIGNED_BYTE, 4, [
    255,0,0,255, 255,0,0,255,  0,255,0,255,   0,255,0,255,
    255,0,0,255, 255,0,0,255,  0,255,0,255,   0,255,0,255,
    0,0,255,255, 0,0,255,255,  0,255,255,255, 0,255,255,255,
    0,0,255,255, 0,0,255,255,  0,255,255,255, 0,255,255,255,
  ] )
  
  def __init__(self):
    """Initializes OpenGL ES, sets the vertex and color arrays and pointers, 
and selects the shading mode."""
    # It's best to set these before creating the GL Canvas
    self.iFrame=0
    self.exitflag = False
    
    self.render=0
    
    self.old_body=appuifw.app.body
    try:
      self.canvas=GLCanvas(redraw_callback=self.redraw)
      appuifw.app.body=self.canvas
    except Exception,e:
      appuifw.note(u"Exception: %s" % (e))
      self.set_exit()
      return
    
    appuifw.app.menu = [
      (u"Exit", self.set_exit)
    ]
    
    self.initgl()
    self.render=1
  
  def initgl(self):
    # Initialize texture stuff
    self.texhandle = glGenTextures( 1 )
    glBindTexture(GL_TEXTURE_2D, self.texhandle)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 4, 4, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.texture)
    glTexEnvx(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    
    # Disable mip mapping
    glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
    glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
    
    # Initialize array pointers
    glVertexPointerb(self.varray)
    
    glColorPointerub(self.colors)
    glTexCoordPointerb(self.texcoords)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    
    # Set up state
    glEnable(GL_CULL_FACE)
    glEnable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)
    glClearColorx(0,0,0,65536)
    glClear(GL_COLOR_BUFFER_BIT)
    
    glViewport(0, 0, self.canvas.size[0], self.canvas.size[1])
    glMatrixMode( GL_PROJECTION )
    glFrustumf( -1.0, 1.0, -1.0, 1.0, 3.0, 1000.0 )
    glMatrixMode( GL_MODELVIEW )
    glLoadIdentity()
    glTranslatef(0,0,-100.0)
    glScalef(15,15,15)
    
    glLoadIdentity()
    glTranslatef(0,0,-100.0)
    glScalef(15,15,15)
    
  def redraw(self,frame=None):
    """Draws and animates the objects.
The frame number determines the amount of rotation."""
    if self.render != 1:
      return
    self.iFrame += 1
    
    glClear(GL_COLOR_BUFFER_BIT)
    
    glPushMatrix()
    glTranslatef(-2,-2,-2)
    glRotatef(self.iFrame/1.1, 5,2,3)
    glMatrixMode( GL_TEXTURE )
    glLoadIdentity()
    glRotatef(self.iFrame/0.7, 0.5, 0.7, 0.2)
    glScalef(10,10,10)
    glMatrixMode( GL_MODELVIEW )
    glDrawElementsub(GL_TRIANGLES, self.indices)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(2,3,-3)
    glRotatef(self.iFrame/1.8, 3,2,3)
    glMatrixMode( GL_TEXTURE )
    glLoadIdentity()
    glRotatef(self.iFrame/0.7, 0.1, 0.2, 0.3)
    glScalef(10,10,10)
    glMatrixMode( GL_MODELVIEW )
    glDrawElementsub(GL_TRIANGLES, self.indices)
    glPopMatrix()
    
    glPushMatrix()
    glRotatef(self.iFrame/1.5, 1,2,3)
    glMatrixMode( GL_TEXTURE )
    glLoadIdentity()
    glRotatef(self.iFrame/0.5, 0.5, 0.3, 0.2)
    glScalef(10,10,10)
    glMatrixMode( GL_MODELVIEW )
    glDrawElementsub(GL_TRIANGLES, self.indices)
    glPopMatrix()
    
  def close_canvas(self): # break reference cycles
    # Uninitializing OpenGL calls should be made before the GLCanvas is deleted
    glDeleteTextures([self.texhandle])
    appuifw.app.body=self.old_body
    self.canvas=None
    
    appuifw.app.exit_key_handler=None
    
  def set_exit(self):
    self.exitflag = True
    self.render = 0
    
  def run(self):
    appuifw.app.exit_key_handler=self.set_exit
    while not self.exitflag:
      self.canvas.drawNow()
      e32.ao_sleep(0.0001)
    self.close_canvas()
    
appuifw.app.screen='full'
try:
  app=GLESDemo()
except Exception,e:
  appuifw.note(u"Cannot start: %s" % (e))
else:
  app.run()
  del app
