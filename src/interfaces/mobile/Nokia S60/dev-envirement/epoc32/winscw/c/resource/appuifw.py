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
import _appuifw
from _appuifw import *

class Canvas(object):
    def __init__(self,redraw_callback=None,event_callback=None, resize_callback=None):
        c=_appuifw.Canvas(redraw_callback,event_callback, resize_callback)
        self._canvas=c
        self._uicontrolapi=c._uicontrolapi
        self._drawapi=c._drawapi
        from graphics import _graphics
        self._draw=_graphics.Draw(self)
        self.bind=c.bind
        for k in _graphics._draw_methods:
            setattr(self,k,getattr(self._draw,k))
    size=property(lambda self: self._canvas.size)

# public API
__all__= ('Canvas',
          'Form',
          'Listbox',
          'Text',
          'Icon',
          'Content_handler',
          'app',
          'multi_query',
          'note',
          'popup_menu',
          'query',
          'selection_list',
          'multi_selection_list',
          'available_fonts',
          'EEventKeyUp',
          'EEventKeyDown',
          'EEventKey',
          'FFormAutoFormEdit',
          'FFormAutoLabelEdit',
          'FFormDoubleSpaced',
          'FFormEditModeOnly',
          'FFormViewModeOnly',
          'STYLE_BOLD',
          'STYLE_ITALIC',
          'STYLE_STRIKETHROUGH',
          'STYLE_UNDERLINE',
          'HIGHLIGHT_STANDARD',
          'HIGHLIGHT_ROUNDED',
          'HIGHLIGHT_SHADOW')

import e32
if e32.s60_version_info>=(2,8):
    __all__ += ('EScreen',
              'EApplicationWindow',
              'EStatusPane',
              'EMainPane',
              'EControlPane',
              'ESignalPane',
              'EContextPane',
              'ETitlePane',
              'EBatteryPane',
              'EUniversalIndicatorPane',
              'ENaviPane',
              'EFindPane',
              'EWallpaperPane',
              'EIndicatorPane',
              'EAColumn',
              'EBColumn',
              'ECColumn',
              'EDColumn',
              'EStaconTop',
              'EStaconBottom',
              'EStatusPaneBottom',
              'EControlPaneBottom',
              'EControlPaneTop',
              'EStatusPaneTop')
