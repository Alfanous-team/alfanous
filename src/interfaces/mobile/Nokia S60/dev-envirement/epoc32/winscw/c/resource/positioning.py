#
# positioning.py
#
# python interface for Location Acquisition API
#
# Copyright (c) 2007-2008 Nokia Corporation
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
import copy
import thread

if e32.s60_version_info>=(3,0):
    import imp
    _locationacq=imp.load_dynamic('_locationacq', 'c:\\sys\\bin\\_locationacq.pyd')
else:
    import _locationacq
from locationacq import *

class ThreadLocalStore(object):
    def __init__(self, constructor):
        self.objects = {}
        self.constructor = constructor
    def get(self):
        id = thread.get_ident()
        if id not in self.objects:
            self.objects[id] = self.constructor()
        return self.objects[id]
    def set(self, newobject):
        self.objects[thread.get_ident()] = newobject

_pos_serv_tls = ThreadLocalStore(_locationacq.position_server)
_get_pos_serv = _pos_serv_tls.get
_positioner_tls = ThreadLocalStore(lambda:_get_pos_serv().positioner())
_get_positioner = _positioner_tls.get
_set_positioner = _positioner_tls.set
_request_ongoing_tls = ThreadLocalStore(lambda:False)
_get_request_ongoing = _request_ongoing_tls.get
_set_request_ongoing = _request_ongoing_tls.set
_current_pos_tls = ThreadLocalStore(lambda:None)
_get_current_pos = _current_pos_tls.get
_set_current_pos = _current_pos_tls.set

POSITION_INTERVAL=1000000

def revdict(d):
    return dict([(d[k],k) for k in d.keys()])

_requestor_types={"service":_locationacq.req_type_service,
                  "contact":_locationacq.req_type_contact}                  
_reverse_requestor_types=revdict(_requestor_types)
                  
_requestor_formats={"application":_locationacq.req_format_app,
                    "telephone":_locationacq.req_format_tel,
                    "url":_locationacq.req_format_url,
                    "email":_locationacq.req_format_mail}
_reverse_requestor_formats=revdict(_requestor_formats)

# get information about available positioning modules
def modules():
  return _get_pos_serv().modules()

# get default module id
def default_module():
  return _get_pos_serv().default_module()

# get detailed information about the specified module  
def module_info(module_id):
  return _get_pos_serv().module_info(module_id)

# select a module
def select_module(module_id):
  _set_positioner(_get_pos_serv().positioner(module_id))
  
# set requestors of the service (at least one must be set)
def set_requestors(requestors):
  for item in requestors:
    item["type"]=_requestor_types[item["type"]]
    item["format"]=_requestor_formats[item["format"]]
    item["data"]=unicode(item["data"])    
  _get_positioner().set_requestors(requestors)

# stop the feed
def stop_position():
    if _get_request_ongoing():
        _get_positioner().stop_position()
        _set_request_ongoing(False)

# get the position information
def position(course=0,satellites=0,
             callback=None,interval=POSITION_INTERVAL,
             partial=0):
  def cb(event):
      _set_current_pos(copy.deepcopy(event))
      _lock.signal()
      
  if _get_request_ongoing():
    raise RuntimeError, "Position request ongoing"
    
  flags=0
  if(course):
    flags|=_locationacq.info_course
  if(satellites):
    flags|=_locationacq.info_satellites

  if callback!=None:
    if not callable(callback):
      raise TypeError("'%s' is not callable"%callback)
    _set_request_ongoing(True)
    return _get_positioner().position(flags, callback, interval, partial)
  else:
    _lock=e32.Ao_lock()
    _set_request_ongoing(True)
    _get_positioner().position(flags, cb, interval, partial)
    _lock.wait()
    stop_position()
    return _get_current_pos()

# get the last position information
def last_position():
  if _get_request_ongoing():
    raise RuntimeError, "Position request ongoing"
  _set_request_ongoing(True)
  last_pos=_get_positioner().last_position()
  _get_positioner().stop_position()
  _set_request_ongoing(False)
  return last_pos
  
