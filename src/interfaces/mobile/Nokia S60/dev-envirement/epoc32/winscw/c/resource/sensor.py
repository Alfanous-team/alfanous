#
# sensor.py
#
# Copyright (c) 2007 Nokia Corporation
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
import _sensor


"""
returns the dictionary of available sensors
format: { 'sensor name 1': { 'id': SensorID1, 'category': CategoryID1 },
          'sensor name 2': { 'id': SensorID2, 'category': CategoryID2 },
          ... }
"""
def sensors():
	return _sensor.sensors()


"""
basic event filter
other classes can derive from EventFilter and implement event() and
cleanup().
event() can process the event data and should then call self.callback(data)
with the processed data.
"""
class EventFilter:

	def __init__(self):
		self.callback = None

	def __del__(self):
		self.cleanup()

	def event(self, data):
		self.callback(data)

	def cleanup(self):
		pass


"""
orientation constants
"""
class Orientation:
	TOP    = 0
	BOTTOM = 1
	LEFT   = 2
	RIGHT  = 3
	FRONT  = 4
	BACK   = 5

orientation = Orientation()


"""
calibration constants for orientation change events
"""
class OrientationCalibration:
	def __init__(self):
		self.timeout = 0.1
		self.gravity = 300  # approx value of an acc sensor when directly exposed to gravity
		#
		# the following table defines how far from the standardised unit vectors each
		# measured vector can differ when it's recognised as a specific orientation.
		# I.e. the perfect 'top' orientation (top is up) would give a sensor measurement
		# of approx. (0, -300, 0). This table's first line defines how much the actual
		# measurement can differ from that when the orientation is still recognised as
		# 'top'.
		#                     X    Y    Z
		self.ival_span = [ [ 100, 200, 300 ],  # vertical (top, bottom)
		                   [ 200, 100, 300 ],  # horizontal (left, right)
		                   [  70,  70,  70 ] ] # flat (front, back)

orientation_calibration = OrientationCalibration()


"""
this function returns true if 'val' is at maximum 'span'
away from 'ival_middle'.
I.e. if 'val' in ]ival_middle - span, ival_middle + span[
"""
def _in_ival(val, ival_middle, span):
	return (val > ival_middle - span) and (val < ival_middle + span)


"""
This class is thought to be used as an event filter for the
acceleration sensor. Instead of the pure acceleration data, the
sensor's callback will receive events when a change in orientation
has been detected. The new orientation is a value from the 'orientation'
constants and will be passed as an argument to the callback.
The orientation reported corresponds to the side of the device that
is held upwards from the user's point of view. I.e. when 'top' is reported,
the device's top is held upwards, when 'front' is reported, the device
is lying flat on its back.
"""
class OrientationEventFilter(EventFilter):

	def __init__(self):
		global orientation
		EventFilter.__init__(self)
		self.__orientation_old = orientation.TOP
		self.__orientation_cur = orientation.TOP
		self.__timedout = False
		self.__timer = e32.Ao_timer()

	def event(self, sensor_val):
		global orientation, orientation_calibration
		
		orientation_tmp = orientation.TOP
		x = sensor_val['data_2']
		y = sensor_val['data_1']
		z = sensor_val['data_3']

		# Now we'll compare the acceleration vector to the 6 standard orientation
		# vectors and see if there is a valid orientation
		if   _in_ival(x,                      0, orientation_calibration.ival_span[0][0]) and \
		     _in_ival(y, -orientation_calibration.gravity, orientation_calibration.ival_span[0][1]) and \
		     _in_ival(z,                      0, orientation_calibration.ival_span[0][2]):
			orientation_tmp = orientation.TOP

		elif _in_ival(x,                      0, orientation_calibration.ival_span[0][0]) and \
		     _in_ival(y,  orientation_calibration.gravity, orientation_calibration.ival_span[0][1]) and \
		     _in_ival(z,                      0, orientation_calibration.ival_span[0][2]):
			orientation_tmp = orientation.BOTTOM

		elif _in_ival(x, -orientation_calibration.gravity, orientation_calibration.ival_span[1][0]) and \
		     _in_ival(y,                      0, orientation_calibration.ival_span[1][1]) and \
		     _in_ival(z,                      0, orientation_calibration.ival_span[1][2]):
			orientation_tmp = orientation.LEFT

		elif _in_ival(x,  orientation_calibration.gravity, orientation_calibration.ival_span[1][0]) and \
		     _in_ival(y,                      0, orientation_calibration.ival_span[1][1]) and \
		     _in_ival(z,                      0, orientation_calibration.ival_span[1][2]):
			orientation_tmp = orientation.RIGHT

		elif _in_ival(x,                      0, orientation_calibration.ival_span[2][0]) and \
		     _in_ival(y,                      0, orientation_calibration.ival_span[2][1]) and \
		     _in_ival(z,  orientation_calibration.gravity, orientation_calibration.ival_span[2][2]):
			orientation_tmp = orientation.FRONT

		elif _in_ival(x,                      0, orientation_calibration.ival_span[2][0]) and \
		     _in_ival(y,                      0, orientation_calibration.ival_span[2][1]) and \
		     _in_ival(z, -orientation_calibration.gravity, orientation_calibration.ival_span[2][2]):
			orientation_tmp = orientation.BACK

		else:
			return

		if orientation_tmp != self.__orientation_old:  # if the orientation is different than the saved one
			if orientation_tmp != self.__orientation_cur:  # if it has changed before we could count to orientation_calibration.max_count
				self.__orientation_cur = orientation_tmp  # set the new orientation
				self.reset_timer()
				return
			if self.__timedout:
				self.callback(orientation_tmp)
				self.__orientation_old = orientation_tmp
				self.__timedout = False

	def reset_timer(self):
		self.cancel_timer()
		self.__timer.after(orientation_calibration.timeout, self.__timer_callback)

	def cancel_timer(self):
		self.__timer.cancel()
		self.__timedout = False

	def cleanup(self):
		self.cancel_timer()

	def __timer_callback(self):
		self.__timedout = True

"""
Event filter for the 'RotSensor' resident e.g. in N95.
"""
class RotEventFilter(EventFilter):

    def __init__(self):
        global orientation
        EventFilter.__init__(self)
        self.rots = {0: orientation.RIGHT,
                    90: orientation.TOP,
                    180: orientation.LEFT,
                    270: orientation.BOTTOM}

    def event(self, sensor_val):
        y = sensor_val['data_1']
        self.callback(self.rots[y])

"""
This class represents a sensor. It has to be passed valid sensor and
category ids when created. If the passed category and sensor id do not
match any sensor, an exception occurs when connect() is called.
Sensor and category ids can be found out via this module's sensors()
function.
"""
class Sensor:

	def __init__(self, sensor_id, category_id):
		self.__connected = False
		self.__sensor = None
		self.__event_filter = EventFilter()
		self.__sensor_id = sensor_id
		self.__category_id = category_id

	def connect(self, callback):
		self.__event_filter.callback = callback
		self.__sensor = _sensor.sensor(self.__sensor_id, self.__category_id)
		connected = self.__sensor.connect(self.__event_filter.event)
		self.__connected = connected
		return connected

	def disconnect(self):
		disconnected = self.__sensor.disconnect()
		self.__connected = not disconnected
		return disconnected

	def connected(self):
		return self.__connected

	def set_event_filter(self, event_filter):
		callback = self.__event_filter.callback
		self.__event_filter = event_filter
		if self.__connected:
			self.disconnect()
			self.connect(callback)
	
