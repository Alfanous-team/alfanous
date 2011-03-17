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
import key_codes
from key_codes import *
import _keycapture
   
     
def _find_all_keys():
    all_keys = dir(key_codes)
    indexes = []
    for index in range(len(all_keys)):
        if str(all_keys[index])[0] == "_":
            indexes.append(index)
    indexes.reverse()
    for index in indexes:
        del all_keys[index]
    for index in range(len(all_keys)):
        all_keys[index] = eval("key_codes."+all_keys[index])        
    return all_keys
    
all_keys = _find_all_keys()



class KeyCapturer(object):
    def __init__(self,callback): 
        self._keys_listened={}
        self._forwarding=0
        self._listening=0
        self._callback=callback # incref needed since this is not in C code
        self._capturer=_keycapture.capturer(callback)
    def last_key(self):
        return self._capturer.last_key()
    def _add_key(self,key_code):
        if self._keys_listened.has_key(key_code):
            if self._keys_listened[key_code] is None:
                key_id = self._capturer.key(key_code)
                self._keys_listened[key_code] = key_id
        else:
            key_id = self._capturer.key(key_code)
            self._keys_listened[key_code] = key_id
    def _add_keys(self,key_codes):
        for code in key_codes:
            self._add_key(code)
    def _remove_all_keys(self):
        for key_code in self._keys_listened:
            if self._keys_listened[key_code] is not None:
                self._capturer.remove_key(self._keys_listened[key_code])
            self._keys_listened[key_code] = None
    def _set_keys(self,keys):
        self._remove_all_keys()
        self._keys_listened={}
        if  self._listening == 1:
            self._add_keys(keys)
        else:
            for item in keys:
                self._keys_listened[item] = None
    def _keys(self):
        return self._keys_listened.keys()
    keys=property(_keys,_set_keys)
    def _forwarding(self):
        return self._forwarding
    def _set_forwarding(self,forwarding):
        self._capturer.set_forwarding(forwarding)
        self._forwarding=forwarding        
    forwarding=property(_forwarding,_set_forwarding)
    def start(self):
        for key_code in self._keys_listened:
            if self._keys_listened[key_code] is None:
                key_id = self._capturer.key(key_code)
                self._keys_listened[key_code] = key_id
        self._capturer.start()
        self._listening=1
    def stop(self):
        self._remove_all_keys()
        self._capturer.stop()
        self._listening=0
    def __del__(self):
        self.stop()
        
