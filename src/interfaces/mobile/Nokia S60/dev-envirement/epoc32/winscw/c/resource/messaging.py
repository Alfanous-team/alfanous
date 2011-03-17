#
# messaging.py
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
import _messaging

# states in sending
ECreated=_messaging.ECreated
EMovedToOutBox=_messaging.EMovedToOutBox
EScheduledForSend=_messaging.EScheduledForSend
ESent=_messaging.ESent
EDeleted=_messaging.EDeleted

# erros
EScheduleFailed=_messaging.EScheduleFailed
ESendFailed=_messaging.ESendFailed
ENoServiceCentre=_messaging.ENoServiceCentre
EFatalServerError=_messaging.EFatalServerError

encodingmap={'7bit':_messaging.EEncoding7bit,
            '8bit':_messaging.EEncoding8bit,
            'UCS2':_messaging.EEncodingUCS2}

_my_messaging=None
_sending=False
_signaled=False  

def sms_send(number,msg,encoding='7bit', callback=None,name=""):
    global _sending
    global _signaled
    global _my_messaging
    if _sending:
        raise RuntimeError, "Already sending"
    def signal_lock():
        global _signaled        
        if not _signaled:
            lock.signal()
            _signaled=True  
    def event_cb(arg):
        global _signaled
        global _sending
        if callback!=None:
            callback(arg)
            signal_lock()
        # The state received from 3.0 SDK under emulator:
        if e32.in_emulator():
            if arg==ENoServiceCentre:
                _sending=False
                signal_lock()
        # This is the default unlocking state,
        # the message was sent or sending failed
        if arg==EDeleted or arg==ESendFailed:
            _sending=False
            signal_lock()
        callback_error[0]=arg # XXX add error checking?
        
    if callback!=None:
        if not callable(callback):
            raise TypeError("'%s' is not callable"%callback)
   
    lock=e32.Ao_lock()
    _signaled=False
    callback_error=[0]
    
    _my_messaging=_messaging.Messaging(number,unicode(msg),unicode(name),encodingmap[encoding],event_cb)
    _sending=True
    lock.wait()
            
def mms_send(number,msg,attachment=None):
    if e32.s60_version_info>=(3,0):
        if attachment:
            _messaging.mms_send(unicode(number),unicode(msg),unicode(attachment))
        else:
            _messaging.mms_send(unicode(number),unicode(msg))
    else:
        pass # to be added later
        
        
        
        
