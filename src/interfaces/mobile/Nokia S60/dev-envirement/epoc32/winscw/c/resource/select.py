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


import socket
import e32
import thread

def select(in_objs,out_objs,exc_objs,timeout=None):
    if len(out_objs)>0 or len(exc_objs)>0:
        raise NotImplementedError('selecting for output and exception not supported')
    for k in in_objs:
        if not isinstance(k,socket._socketobject):
            raise NotImplementedError('select supports only socket objects')
    lock=e32.Ao_lock()
    if timeout is not None and timeout > 0:
        e32.ao_sleep(timeout, lock.signal)
    (ready_in,ready_out,ready_exc)=([],[],[])
    for sock in in_objs:
        if sock._recv_will_return_data_immediately():
            ready_in.append(sock)
    # If we have readable sockets or we just want to poll, return now.
    if len(ready_in)>0 or timeout==0:
        return (ready_in,ready_out,ready_exc)
    # Ok, so we want to wait for it...
    def callback(sock):
        ready_in.append(sock)
        lock.signal()
    for sock in in_objs:
        sock._set_recv_listener(lambda sock=sock:callback(sock))
    lock.wait()
    return (ready_in,ready_out,ready_exc)
    
