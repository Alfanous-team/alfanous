#
# telephone.py
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
import _telephone

_phone=_telephone.Phone()
_answering_supported=0

if e32.s60_version_info>=(3,0):
    _answering_supported=1
    EStatusUnknown=_telephone.EStatusUnknown
    EStatusIdle=_telephone.EStatusIdle
    EStatusDialling=_telephone.EStatusDialling
    EStatusRinging=_telephone.EStatusRinging
    EStatusAnswering=_telephone.EStatusAnswering
    EStatusConnecting=_telephone.EStatusConnecting
    EStatusConnected=_telephone.EStatusConnected
    EStatusReconnectPending=_telephone.EStatusReconnectPending
    EStatusDisconnecting=_telephone.EStatusDisconnecting
    EStatusHold=_telephone.EStatusHold
    EStatusTransferring=_telephone.EStatusTransferring
    EStatusTransferAlerting=_telephone.EStatusTransferAlerting

    _phone_incoming=_telephone.Phone()
    _phone_answer=_telephone.Phone()

    _my_call_back=None    

_is_closed=1

def dial(number):
    global _is_closed
    if _is_closed:
        _phone.open()
        _is_closed=0
    _phone.set_number(number)
    _phone.dial()
def hang_up():
    try:
        _phone.hang_up()
    except:
        if _answering_supported:
            try:
                _phone_answer.hang_up()
            except:
                raise
        
if _answering_supported:
    def call_state(cb):
        global _my_call_back
        _my_call_back=cb
        _phone_incoming.incoming_call(_telephone_call_back)
    def _answer(arg):
        # XXX state checking here?
        pass
    def incoming_call():
        _phone_answer.incoming_call(_answer)
    def answer():
        _phone_answer.answer()
    def cancel():
        _phone.cancel()
        _phone_incoming.cancel()
        _phone_answer.cancel()
    def _telephone_call_back(arg):
        global _my_call_back
        _phone_incoming.incoming_call(_telephone_call_back)
        _my_call_back(arg)
