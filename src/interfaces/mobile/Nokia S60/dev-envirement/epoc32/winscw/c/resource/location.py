#
# location.py
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

import _location

def gsm_location():  
    if e32.s60_version_info>=(3,0):
        ret = _location.gsm_location()
        if ret[4]==1: # relevant information ?
            return (int(ret[0]),int(ret[1]),ret[2],ret[3])
        else:
            return None # information returned by _location.gsm_location() not relevant
    else:
        return _location.gsm_location()
        