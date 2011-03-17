#
# camera.py
#
# Copyright (c) 2005 - 2007 Nokia Corporation
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

import _camera
import graphics

_my_camera=_camera.Camera(0)
number_of_devices = _my_camera.cameras_available()
device=[]
for dev_index in range(number_of_devices):
    device.append(_camera.Camera(dev_index)) #used only for image size checking
_my_call_back=None
_backlight_on=0

EOpenComplete=_camera.EOpenComplete
EPrepareComplete=_camera.EPrepareComplete
ERecordComplete=_camera.ERecordComplete

modemap={'RGB':_camera.EColor16M,
         'RGB16':_camera.EColor64K,
         'RGB12':_camera.EColor4K,
         'JPEG_Exif':_camera.EFormatExif,
         'JPEG_JFIF':_camera.EFormatJpeg}

flashmap={'none':_camera.EFlashNone,
          'auto':_camera.EFlashAuto,
          'forced':_camera.EFlashForced,
          'fill_in':_camera.EFlashFillIn,
          'red_eye_reduce':_camera.EFlashRedEyeReduce}

whitebalancemap={'auto':_camera.EWBAuto,
                 'daylight':_camera.EWBDaylight,
                 'cloudy':_camera.EWBCloudy,
                 'tungsten':_camera.EWBTungsten,
                 'fluorescent':_camera.EWBFluorescent,
                 'flash':_camera.EWBFlash}

exposuremap={'auto':_camera.EExposureAuto,
             'night':_camera.EExposureNight,
             'backlight':_camera.EExposureBacklight,
             'center':_camera.EExposureCenter}

def _finder_call_back(image_frame):
    global _backlight_on
    global _my_call_back
    if(_backlight_on):
        e32.reset_inactivity()
    _my_call_back(graphics.Image.from_cfbsbitmap(image_frame))
def _main_pane_size():
    try:
        if e32.s60_version_info>=(2,8):
            import appuifw
            return appuifw.app.layout(appuifw.EMainPane)[0]
    except:
        pass
    return (176, 144) # hard coded default

def take_photo(mode='RGB16',size=(640, 480),zoom=0,flash='none',
               exposure='auto',white_balance='auto',position=0):
    s=-1
    if (position>=number_of_devices):
        raise ValueError, "Camera position not supported"  
    for i in range(device[position].max_image_size()):
        if device[position].image_size(modemap[mode], i)==size:
            s=i
            break
    if s==-1:
        raise ValueError, "Size not supported for camera"   
                            
    if _my_camera.taking_photo():
        raise RuntimeError, "Photo request ongoing"

    if mode=='JPEG_Exif' or mode=='JPEG_JFIF':
        return _my_camera.take_photo(modemap[mode],s,
                                     zoom,flashmap[flash],
                                     exposuremap[exposure],
                                     whitebalancemap[white_balance],
                                     position)
    else:        
        return graphics.Image.from_cfbsbitmap(_my_camera.take_photo(modemap[mode],s,
                                                                    zoom,flashmap[flash],
                                                                    exposuremap[exposure],
                                                                    whitebalancemap[white_balance],
                                                                    position))
def start_finder(call_back, backlight_on=1, size=_main_pane_size()):
    global _my_camera
    if _my_camera.finder_on():
        raise RuntimeError, "View finder is started already"
    global _my_call_back
    global _backlight_on
    if not callable(call_back):
        raise TypeError("'%s' is not callable"%call_back)
    _my_call_back=call_back
    _backlight_on=backlight_on
    _my_camera.start_finder(_finder_call_back, size)
def stop_finder():
    global _my_camera
    global _my_call_back
    _my_camera.stop_finder()
    _my_call_back=None
def image_modes():
    ret=[]
    modes=_my_camera.image_modes()
    for key in modemap:
        if (modes&modemap[key]):
            ret.append(key)
    return ret
def image_sizes(mode='RGB16'):
    sizes=[]
    for i in range(_my_camera.max_image_size()):
        s=_my_camera.image_size(modemap[mode], i)
        if s!=(0,0):
            sizes.append(s)
    return sizes
def max_zoom():
    return _my_camera.max_zoom()
def flash_modes():
    ret = []
    modes = _my_camera.flash_modes()
    for key in flashmap:
        if (modes&flashmap[key]):
            ret.append(key)
        if (flashmap[key]==0):
            ret.append(key)
    return ret
def exposure_modes():
    ret = []
    modes = _my_camera.exposure_modes()
    for key in exposuremap:
        if (modes&exposuremap[key]):
            ret.append(key)
        if (exposuremap[key]==0):
            ret.append(key)
    return ret
def white_balance_modes():
    ret = []
    modes = _my_camera.white_balance_modes()
    for key in whitebalancemap:
        if (modes&whitebalancemap[key]):
            ret.append(key)
        if (whitebalancemap[key]==0):
            ret.append(key)
    return ret
def cameras_available():
    return _my_camera.cameras_available()
def release():
    global _my_camera
    global number_of_devices
    global device
    _my_camera.release()
    for dev_index in range(number_of_devices):
        device[dev_index].release()
def _handle():
    return _my_camera.handle()

_my_video=_camera.Video()

def start_record(filename, cb):
    if not _my_camera.finder_on():
        raise RuntimeError, "View finder is not started"    
    if not callable(cb):
        raise TypeError("'%s' is not callable"%cb)
    _my_video.start_record(_handle(), unicode(filename), cb)
    
def stop_record():
    _my_video.stop_record()
