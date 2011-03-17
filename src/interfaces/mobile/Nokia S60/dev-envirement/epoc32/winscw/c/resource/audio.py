#
# audio.py
#
# Copyright (c) 2005 - 2008 Nokia Corporation
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
import _recorder

ENotReady = _recorder.ENotReady
EOpen = _recorder.EOpen
EPlaying = _recorder.EPlaying
ERecording = _recorder.ERecording
KMdaRepeatForever = _recorder.KMdaRepeatForever

TTS_PREFIX = "(tts)"

class Sound(object):
    def __init__(self):
        self._player=_recorder.Player()
    def open(filename):
        def open_cb(previous, current, err):
            callback_error[0]=err
            lock.signal()
        player=Sound()
        lock=e32.Ao_lock()
        callback_error=[0]
        player._player.bind(open_cb)
        player._player.open_file(unicode(filename))
        lock.wait()
        if callback_error[0]:
            raise SymbianError,(callback_error[0],
                                "Error opening file: "+e32.strerror(callback_error[0]))
        return player
    open=staticmethod(open)
    def _say(text):
        def say_cb(previous, current, err):
            callback_error[0]=err
            lock.signal()
        player=Sound()
        lock=e32.Ao_lock()
        callback_error=[0]
        player._player.bind(say_cb)
        player._player.say(text)
        lock.wait()
        if callback_error[0]:
            raise SymbianError,(callback_error[0],
                                "Error: "+e32.strerror(callback_error[0]))
    _say=staticmethod(_say)
    def play(self, times=1, interval=0, callback=None):
        def play_cb(previous, current, err):
            #This is called first with EPlaying meaning that the playing started
            #and with EOpen meaning that the playing stopped.
            callback_error[0]=err
            if callback!=None:
                if (current==EPlaying or current==EOpen):
                    lock.signal()
                callback(previous, current, err)
            elif (current==EPlaying or current==EOpen) and callback==None:
                lock.signal()
        if self.state()!=EOpen:
            raise RuntimeError,("Sound not in correct state, state: %d" % (self.state()))
        lock=e32.Ao_lock()
        callback_error=[0]
        self._player.bind(play_cb)
        if not times==KMdaRepeatForever:
            times=times-1
        self._player.play(times, interval)
        lock.wait()
        if callback_error[0]:
            raise SymbianError,(callback_error[0],
                                "Error playing file: "+e32.strerror(callback_error[0]))
    def record(self):
        def rec_cb(previous, current, err):
            callback_error[0]=err
            lock.signal()
        if self.state()!=EOpen:
            raise RuntimeError,("Sound not in correct state, state: %d" % (self.state()))
        lock=e32.Ao_lock()
        callback_error=[0]
        self._player.bind(rec_cb)
        self._player.record()
        lock.wait()
        if callback_error[0]:
            raise SymbianError,(callback_error[0],
                                "Error while recording: "+e32.strerror(callback_error[0]))
    def stop(self):
        self._player.stop()
    def close(self):
        self._player.close_file()
    def state(self):
        return self._player.state()
    def max_volume(self):
        return self._player.max_volume()
    def set_volume(self, volume):
        if volume<0:
            volume=0
        elif volume>self._player.max_volume():
            volume=self._player.max_volume()
        return self._player.set_volume(volume)
    def current_volume(self):
        return self._player.current_volume()
    def duration(self):
        return self._player.duration()
    def set_position(self, position):
        self._player.set_position(position)
    def current_position(self):
        return self._player.current_position()

def say(text, prefix=TTS_PREFIX):
    if type(text) is unicode:
        text = text.encode('utf8')
    return Sound._say(prefix+text)
