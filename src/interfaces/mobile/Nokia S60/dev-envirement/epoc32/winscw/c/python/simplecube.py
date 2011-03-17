#
# simplecube.py
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

import appuifw, sys, e32
from glcanvas import *
from gles import *
from key_codes import *

class SimpleCube:
  vertices = array(GL_BYTE, 3, (
     [-1,  1,  1.0],
     [ 1,  1,  1],
     [ 1, -1,  1],
     [-1, -1,  1],

     [-1,  1, -1],
     [ 1,  1, -1],
     [ 1, -1, -1],
     [-1, -1, -1]
    )
  )
  
  triangles = array(GL_UNSIGNED_BYTE, 3, (
    # front
    [1,0,3],
    [1,3,2],
    
    # right
    [2,6,5],
    [2,5,1],
    
    # back
    [7,4,5],
    [7,5,6],
    
    # left
    [0,4,7],
    [0,7,3],
    
    # top
    [5,4,0],
    [5,0,1],
    
    # bottom
    [3,7,6],
    [3,6,2]
    )
  )
  
  fanOne = array(GL_UNSIGNED_BYTE, 3, (
    [1,0,3],
    [1,3,2],
    [1,2,6],
    [1,6,5],
    [1,5,4],
    [1,4,0]
    )
  )
  fanTwo = array(GL_UNSIGNED_BYTE, 3, (
    [7,4,5],
    [7,5,6],
    [7,6,2],
    [7,2,3],
    [7,3,0],
    [7,0,4]
    )
  )
  
  colors = array(GL_UNSIGNED_BYTE, 4, (
    [0  ,255,  0,255],
    [0  ,  0,255,255],
    [0  ,255,  0,255],
    [255,  0,  0,255],

    [0  ,  0,255,255],
    [255,  0,  0,255],
    [0  ,  0,255,255],
    [0  ,255,  0,255]
  ))
  
  ETriangles=0
  ETriangleFans=1
  
  def __init__(self):
    """Initializes OpenGL ES, sets the vertex and color arrays and pointers, 
and selects the shading mode."""
    
    # It's best to set these before creating the GL Canvas
    self.iDrawingMode=self.ETriangles
    self.iFrame=0
    self.exitflag = False
    self.render=0
    self.canvas = None
    
    self.old_body=appuifw.app.body
    try:
      self.canvas=GLCanvas(redraw_callback=self.redraw, event_callback=self.event, resize_callback=self.resize)
      appuifw.app.body=self.canvas
    except Exception,e:
      appuifw.note(u"Exception: %s" % (e))
      self.set_exit()
      return
    
    # binds are exactly same as with normal Canvas objects
    self.canvas.bind(EKey1,lambda:self.FullScreen(0))
    self.canvas.bind(EKey2,lambda:self.FullScreen(1))
    self.canvas.bind(EKey3,lambda:self.FullScreen(2))
    
    appuifw.app.menu = [
      (
        u"Shading mode",
        (
          (u"Flat", self.FlatShading),
          (u"Smooth", self.SmoothShading)
        )
      ),
      (
        u"Drawing mode",
        (
          (u"Triangles", self.TriangleMode),
          (u"Triangle fans", self.TriangleFanMode)
        )
      ),
      (
        u"Screen",
        (
          (u"Normal", lambda:self.FullScreen(0)),
          (u"Large", lambda:self.FullScreen(1)),
          (u"Full", lambda:self.FullScreen(2)),
        )
      ),
      (u"Exit", self.set_exit)
    ]
    
    try:
      self.initgl()
    except Exception,e:
      appuifw.note(u"Exception: %s" % (e))
      self.set_exit()
    
  def event(self, ev):
    """Event handler"""
    pass
  
  def resize(self):
    """Resize handler"""
    # This may get called before the canvas is created, so check that the canvas exists
    if self.canvas:
      glViewport(0, 0, self.canvas.size[0], self.canvas.size[1])
      aspect = float(self.canvas.size[1]) / float(self.canvas.size[0])
      glMatrixMode( GL_PROJECTION )
      glLoadIdentity()
      glFrustumf( -1.0, 1.0, -1.0*aspect, 1.0*aspect, 3.0, 1000.0 )
    
  def initgl(self):
    """Initializes OpenGL and sets up the rendering environment"""
    # Set the screen background color. 
    glClearColor( 0.0, 0.0, 0.0, 1.0 )
    
    # Enable back face culling. 
    glEnable( GL_CULL_FACE  )
    
    # Initialize viewport and projection. 
    self.resize()
    
    glMatrixMode( GL_MODELVIEW )
    
    # Enable vertex arrays. 
    glEnableClientState( GL_VERTEX_ARRAY )
    
    # Set array pointers. 
    glVertexPointerb(self.vertices)
    
    # Enable color arrays.
    glEnableClientState( GL_COLOR_ARRAY )
    
    # Set color pointers. 
    glColorPointerub(self.colors )
    
    # Set the initial shading mode 
    glShadeModel( GL_FLAT )
    
    # Do not use perspective correction 
    glHint( GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST )
    self.render=1
    
  def FlatShading(self):
    """Sets the GL shading model to flat."""
    glShadeModel( GL_FLAT )
    
  def SmoothShading(self):
    """Sets the GL shading model to smooth."""
    glShadeModel( GL_SMOOTH )
    
  def TriangleMode(self):
    """Sets the rendering mode to triangles."""
    self.iDrawingMode = self.ETriangles
    
  def TriangleFanMode(self):
    """Sets the rendering mode to triangle fans."""
    self.iDrawingMode = self.ETriangleFans
    
  def FullScreen(self,mode):
    if mode == 0:
      appuifw.app.screen = 'normal'
    elif mode == 1:
      appuifw.app.screen = 'large'
    elif mode == 2:
      appuifw.app.screen = 'full'
    
  def drawbox(self, aSizeX, aSizeY, aSizeZ):
    """Draws a box with triangles or triangle fans depending on the current rendering mode.
Scales the box to the given size using glScalef."""
    glScalef( aSizeX, aSizeY, aSizeZ )
    
    if self.iDrawingMode == self.ETriangles:
      glDrawElementsub( GL_TRIANGLES, self.triangles )
    elif self.iDrawingMode == self.ETriangleFans:
      glDrawElementsub( GL_TRIANGLE_FAN, self.fanOne )
      glDrawElementsub( GL_TRIANGLE_FAN, self.fanTwo )
  
  def redraw(self,frame):
    """Draws and animates the objects.
The frame number determines the amount of rotation."""
    self.iFrame = frame
    
    if self.render == 0:
      return
    glMatrixMode( GL_MODELVIEW )
    
    cameraDistance = 100
    glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
    
    # Animate and draw box
    glLoadIdentity()
    glTranslatex( 0 , 0 , -cameraDistance << 16 )
    glRotatex( self.iFrame << 16, 1 << 16,    0   ,    0    )
    glRotatex( self.iFrame << 15,    0   , 1 << 16,    0    )
    glRotatex( self.iFrame << 14,    0   ,    0   , 1 << 16 )
    self.drawbox( 15.0, 15.0, 15.0 )
    
  def close_canvas(self): # break reference cycles
    appuifw.app.body=self.old_body
    self.canvas=None
    self.draw=None
    appuifw.app.exit_key_handler=None
  
  def set_exit(self):
    self.exitflag = True
    
  def run(self):
    appuifw.app.exit_key_handler=self.set_exit
    while not self.exitflag:
      self.canvas.drawNow()
      e32.ao_sleep(0.0001)
    self.close_canvas()
    
appuifw.app.screen='full'
try:
  app=SimpleCube()
except Exception,e:
  appuifw.note(u'Exception: %s' % (e))
else:
  app.run()
  del app
#sys.exit(0)