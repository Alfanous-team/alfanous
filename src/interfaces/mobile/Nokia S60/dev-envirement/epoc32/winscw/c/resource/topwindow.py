#
# topwindow.py
#
# Copyright (c) 2006 - 2007  Nokia Corporation
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


import e32
import graphics
import _topwindow
    
_corners = {"square":_topwindow.corner_type_square, 
            "corner1":_topwindow.corner_type_corner1,
            "corner2":_topwindow.corner_type_corner2,
            "corner3":_topwindow.corner_type_corner3,
            "corner5":_topwindow.corner_type_corner5}
               

class TopWindow(object):
    def __init__(self):
        self._window = _topwindow.window()
        self._position = (0,0)
        self._bg_color=0xffffff
        self._window.bg_color(self._bg_color)
        self._window.fading(0)
        self._fading = 0
        self._image_position_items = [] # image-position items.
        self._image_ids = [] # ids of image-positions items.
        self._visible = 0
        self._shadow = 0
        self._corner_type = _corners["square"]
    def _position(self):
        return self._position
    def _set_position(self,pos):
        self._window.set_position(pos[0],pos[1])
        self._position = (pos[0],pos[1])
    position=property(_position,_set_position)
    def _size(self):
        return self._window.size()
    def _set_size(self,size):
        self._window.set_size(size[0],size[1])
    size=property(_size,_set_size)
    def _shadow(self):
        return self._shadow
    def _set_shadow(self,shadow):
        self._window.set_shadow(shadow)
        self._shadow=shadow
    shadow=property(_shadow,_set_shadow)
    def _corner_type(self):
        return self._corner_type
    def _set_corner_type(self,corner_type):
        self._window.set_corner_type(_corners[corner_type])
        self._corner_type=corner_type 
    corner_type=property(_corner_type,_set_corner_type)
    def _maxsize(self):
        return self._window.max_size()
    maximum_size=property(_maxsize)
    def _bg_color(self):
        return self._bg_color
    def _set_bg_color(self,bg_color):
        self._window.bg_color(bg_color)
        self._bg_color = (bg_color)
    background_color=property(_bg_color,_set_bg_color)
    def add_image(self,image,position):
        if len(position) == 2:
            width = image.size[0]
            height = image.size[1]
        elif len(position) == 4:
            width = position[2] - position[0]
            height = position[3] - position[1]
        else:
            raise TypeError('position must contain 2 or 4 integer values')
        image_id = self._window.put_image(image._bitmapapi(),position[0],position[1],width,height)   
        self._image_position_items.append((image,(position[0],position[1],position[0]+width,position[1]+height)))
        self._image_ids.append(image_id)
    def remove_image(self,image,position=None): 
        found = 0
        if (position is not None):
            if len(position) == 2:
                pos = (position[0],position[1],position[0]+image.size[0],position[1]+image.size[1])
            else:
                pos = position
        indices = range(len(self._image_position_items))
        if indices is None:
            raise ValueError('no such image')
        indices.reverse()
        for index in indices:            
            if (self._image_position_items[index][0] == image) and \
               ((position is None) or (pos == self._image_position_items[index][1])):
                found = 1
                self._window.remove_image(self._image_ids[index])
                del self._image_position_items[index]
                del self._image_ids[index]
        if found == 0:
            raise ValueError('no such image')
    def _images(self):
        return list(self._image_position_items)
    def _set_images(self,image_data):
        for id in self._image_ids:
            self._window.remove_image(id)
        self._image_ids = []
        self._image_position_items = []
        for item in image_data:
            self.add_image(item[0],item[1])    
    images=property(_images,_set_images)
    def _visible(self):
        return self._visible
    def _set_visible(self,visibility):
        if visibility:
            self._window.show()
            self._visible = 1
        else:
            self._window.hide()
            self._visible = 0             
    visible=property(_visible,_set_visible)
    def show(self):
        self.visible = 1
    def hide(self):
        self.visible = 0
    def _fading(self):
        return self._fading
    def _set_fading(self,fading):
        self._window.fading(fading)
        self._fading = fading
    fading=property(_fading,_set_fading)
    
    
    