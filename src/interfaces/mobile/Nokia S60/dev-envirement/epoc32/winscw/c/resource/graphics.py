#
# graphics.py
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
#

import e32
import _graphics
import sysinfo

Draw=_graphics.Draw

def _revdict(d):
    return dict([(d[k],k) for k in d.keys()])

SDK12=not hasattr(_graphics,'FLIP_LEFT_RIGHT')

if not SDK12:
    FLIP_LEFT_RIGHT=_graphics.FLIP_LEFT_RIGHT
    FLIP_TOP_BOTTOM=_graphics.FLIP_TOP_BOTTOM
    ROTATE_90=_graphics.ROTATE_90
    ROTATE_180=_graphics.ROTATE_180
    ROTATE_270=_graphics.ROTATE_270

class Image(object):
    _twips = sysinfo.display_twips()
    _pixels = sysinfo.display_pixels()
    _default_density = (float(_twips[0])/_pixels[0],
                        float(_twips[1])/_pixels[1])
    _modemap={'1': _graphics.EGray2,
              'L': _graphics.EGray256,
              'RGB12': _graphics.EColor4K,
              'RGB16': _graphics.EColor64K,
              'RGB': _graphics.EColor16M}
    _moderevmap=_revdict(_modemap)
    def __init__(self,img):
        self._image=img
        if img.twipsize == (0,0):
            img.twipsize = (self._default_density[0]*img.size[0],self._default_density[1]*img.size[1])
        self._drawapi=self._image._drawapi
        self._draw=_graphics.Draw(self._image)
        self._bitmapapi=self._image._bitmapapi
        self.getpixel=self._image.getpixel
        self._lock=None
        self._waiting=0
        self._resized_image=None
        for k in _graphics._draw_methods:
            setattr(self,k,getattr(self._draw,k))
    size=property(lambda self:self._image.size)
    mode=property(lambda self:self._moderevmap[self._image.mode])

    twipsize=property(lambda self: self._image.twipsize,
                      lambda self, value: setattr(self._image, 
                                                  "twipsize", 
                                                  value))
    def from_cfbsbitmap(bitmap):
        return Image(_graphics.ImageFromCFbsBitmap(bitmap))
    from_cfbsbitmap=staticmethod(from_cfbsbitmap)
    def from_icon(filename,image_id,size):
        if e32.s60_version_info>=(3,0):
            return Image(_graphics.ImageFromIcon(filename,image_id,size[0],size[1]))
        else:
            raise RuntimeError('not supported')
    from_icon=staticmethod(from_icon)
    def new(size,mode='RGB16'):
        if not Image._modemap.has_key(mode):
            raise ValueError('invalid mode')
        return Image(_graphics.ImageNew(size,Image._modemap[mode]))
    new=staticmethod(new)
    if not SDK12:
        def open(filename):
            def finish_load(errcode):
                img._errcode=errcode
                lock.signal()
            lock=e32.Ao_lock()
            img=Image(_graphics.ImageOpen(unicode(filename),finish_load))
            lock.wait()        
            if img._errcode != 0:
                raise SymbianError,(img._errcode,
                                    "Error loading image:"+e32.strerror(img._errcode))
            return img
        open=staticmethod(open)
        def inspect(filename):
            (size,mode)=_graphics.ImageInspect(unicode(filename))
            return {'size': size}
        inspect=staticmethod(inspect)
        def load(self,filename,callback=None):
            self._wait()
            self._filename=unicode(filename)
            self._usercallback=callback
            self._lock=e32.Ao_lock()
            self._image.load(self._filename,self._callback)
            if callback is None:
                self._wait()
                if self._errcode != 0:
                    err=self._errcode
                    self._errcode=0
                    raise SymbianError,(err, "Error loading image:"+e32.strerror(err))
        def save(self,filename,callback=None,format=None,quality=75,bpp=24,compression='default'):
            if format is None:
                if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                    format='JPEG'
                elif filename.lower().endswith('.png'):
                    format='PNG'
                else:
                    raise ValueError('unrecognized suffix and format not specified')
            self._wait()
            lock=e32.Ao_lock()
            self._image.save(unicode(filename),self._callback,format,quality,compression,bpp)
            # If the code above didn't raise an exception, this method
            # will succeed, so now it's safe to modify object state.
            self._usercallback=callback
            self._lock=lock
            if callback is None:
                self._wait()
                if self._errcode != 0:
                    err=self._errcode
                    self._errcode=0
                    raise SymbianError,(err, "Error loading image:"+e32.strerror(err))
        def resize(self,size,callback=None,keepaspect=0):
            self._wait()
            newimage=Image.new(size,self.mode) 
            lock=e32.Ao_lock()
            self._image.resize(newimage,keepaspect,self._callback)
            # If the code above didn't raise an exception, this method
            # will succeed, so now it's safe to modify object state.
            self._lock=lock
            self._usercallback=callback
            self._resized_image=newimage
            if callback is None:
                self._wait()
                if self._errcode != 0:
                    err=self._errcode
                    self._errcode=0
                    raise SymbianError,(err, "Error resizing image:"+e32.strerror(err))
                t=self._resized_image
                self._resized_image=None
                return t
        def transpose(self,direction,callback=None):
            self._wait()
            if direction == ROTATE_90 or direction == ROTATE_270:
                newsize=(self.size[1],self.size[0])
            else:
                newsize=self.size
            newimage=Image.new(newsize,self.mode) 
            lock=e32.Ao_lock()
            self._image.transpose(newimage,direction,self._callback)
            # If the code above didn't raise an exception, this method
            # will succeed, so now it's safe to modify object state.
            self._lock=lock
            self._usercallback=callback
            self._resized_image=newimage
            if callback is None:
                self._wait()
                if self._errcode != 0:
                    err=self._errcode
                    self._errcode=0
                    raise RuntimeError("Error resizing image:"+str(err))
                t=self._resized_image
                self._resized_image=None
                return t
        def _callback(self, errcode):
            self._errcode=errcode
            if self._lock:
                self._lock.signal()
            self._lock=None
            if self._usercallback is not None:
                t=self._usercallback
                self._usercallback=None
                if self._resized_image is not None: # resize in progress
                    if self._errcode == 0:
                        newimage=self._resized_image
                        self._resized_image=None
                        t(newimage)
                    else:
                        t(None)
                else:
                    t(self._errcode)
        def _wait(self):
            if self._lock:
                if self._waiting:
                    raise RuntimeError("Image object busy.")
                self._waiting=1
                self._lock.wait()
                self._waiting=0
        def stop(self):
            self._image.stop()
            if self._lock:
                self._errcode=0
                self._lock.signal()
                self._lock=None

def screenshot():
    return Image(_graphics.screenshot())


FONT_BOLD=1
FONT_ITALIC=2
FONT_SUBSCRIPT=4
FONT_SUPERSCRIPT=8
FONT_ANTIALIAS=16
FONT_NO_ANTIALIAS=32

__all__=('Draw',
         'Image',
         'screenshot',
         'FONT_BOLD',
         'FONT_ITALIC',
         'FONT_SUBSCRIPT',
         'FONT_SUPERSCRIPT',
         'FONT_ANTIALIAS',
         'FONT_NO_ANTIALIAS')

if not SDK12: 
    __all__+=(('FLIP_LEFT_RIGHT',
               'FLIP_TOP_BOTTOM',
               'ROTATE_90',
               'ROTATE_180',
               'ROTATE_270'))
    
