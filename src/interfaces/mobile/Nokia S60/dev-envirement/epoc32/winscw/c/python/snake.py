#
# snake.py
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
import math
import e32
from key_codes import *
from graphics import *
import random

class SnakeGame:
    deltas=((1,0),(0,-1),(-1,0),(0,1))
    def __init__(self):
        self.direction=0
        self.step=5
        self.color=(0,128,0)
        self.fillarray={}
        self.exitflag=0
        self.score=0
        self.wormlocs=[]
        self.wormlength=10
        self.foodloc=None
        self.fieldcolor=(192,192,128)
        self.resboxoffset=2        
        self.state='init'        
        self.old_body=appuifw.app.body
        self.canvas=appuifw.Canvas(redraw_callback=self.redraw)
        self.draw=Draw(self.canvas)
        appuifw.app.body=self.canvas
        self.fieldsize=(self.canvas.size[0]/self.step,(self.canvas.size[1]-16)/self.step)        
        self.canvas.bind(EKeyRightArrow,lambda:self.turnto(0))
        self.canvas.bind(EKeyUpArrow,lambda:self.turnto(1))
        self.canvas.bind(EKeyLeftArrow,lambda:self.turnto(2))
        self.canvas.bind(EKeyDownArrow,lambda:self.turnto(3))
        self.loc=[self.fieldsize[0]/2,self.fieldsize[1]/2]        
        self.place_food()
        self.state='playing'
        self.redraw(())
    def turnto(self,direction):
        self.direction=direction
    def close_canvas(self): # break reference cycles
        appuifw.app.body=self.old_body
        self.canvas=None
        self.draw=None
        appuifw.app.exit_key_handler=None
    def redraw(self,rect):
        self.draw.clear(self.fieldcolor)
        for loc in self.fillarray.keys():
            self.draw_square(loc,self.color)
        self.draw_score()
        if self.foodloc:
            self.draw_food()        
    def draw_square(self,loc,color):
        self.draw.rectangle((loc[0]*self.step,
                             16+loc[1]*self.step,
                             loc[0]*self.step+self.step,
                             16+loc[1]*self.step+self.step),fill=color)
    def draw_score(self):
        scoretext=u"Score: %d"%self.score
        textrect=self.draw.measure_text(scoretext, font='title')[0]
        self.draw.rectangle((0,0,textrect[2]-textrect[0]+self.resboxoffset,
                             textrect[3]-textrect[1]+self.resboxoffset),fill=(0,0,0))      
        self.draw.text((-textrect[0],-textrect[1]),scoretext,(0,192,0),"title")
    def draw_food(self):
        self.draw_square(self.foodloc,(255,0,0))        
    def place_food(self):
        while 1:
            self.foodloc=(random.randint(0,self.fieldsize[0]-1),
                          random.randint(0,self.fieldsize[1]-1))
            if not self.fillarray.has_key(self.foodloc): break
        self.draw_food()
    def set_exit(self):
        self.exitflag=1
    def run(self):
        appuifw.app.exit_key_handler=self.set_exit
        while not self.exitflag:
            self.draw_square(self.loc,self.color)
            if (tuple(self.loc) in self.fillarray or
                self.loc[0]>=self.fieldsize[0] or self.loc[0]<0 or
                self.loc[1]>=self.fieldsize[1] or self.loc[1]<0):
                break
            if tuple(self.loc)==self.foodloc:
                self.score+=10
                self.draw_score()
                self.place_food()
                self.draw_food()
                self.wormlength+=10
            if len(self.wormlocs)>self.wormlength:
                loc=self.wormlocs[0]
                del self.wormlocs[0]
                del self.fillarray[loc]
                self.draw_square(loc,self.fieldcolor)
            self.fillarray[tuple(self.loc)]=1
            self.wormlocs.append(tuple(self.loc))
            e32.ao_sleep(0.08)
            self.loc[0]+=self.deltas[self.direction][0]
            self.loc[1]+=self.deltas[self.direction][1]
        self.close_canvas()
appuifw.app.screen='full'
playing=1
while playing:
    game=SnakeGame()
    game.run()
    playing=appuifw.query(u'Final score: %d - Play again?'%game.score,'query')    
