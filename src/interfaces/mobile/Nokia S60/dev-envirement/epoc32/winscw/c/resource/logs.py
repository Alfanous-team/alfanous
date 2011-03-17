#
# logs.py
#
# Copyright (c) 2006 - 2007 Nokia Corporation
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

import _logs

import exceptions
#
types={'call'		: _logs.ELogTypeCall,
		 'sms'		: _logs.ELogTypeSms,
		 'data'		: _logs.ELogTypeData,
		 'fax'		: _logs.ELogTypeFax,
		 'email'	: _logs.ELogTypeEMail,
		 'scheduler': _logs.ELogTypeScheduler}
		 
modes={'in'			: _logs.ELogModeIn,
		 'out'		: _logs.ELogModeOut,
		 'missed'	: _logs.ELogModeMissed,
		 'fetched'	: _logs.ELogModeFetched,
		 'in_alt'	: _logs.ELogModeInAlt,
		 'out_alt'	: _logs.ELogModeOutAlt }


_all_logs=0
_default_mode='in'  # see 'modes' dict for possible values


def raw_log_data():
	logevents = []
	for t in types:
		for m in modes:
			logevents.extend(_logs.list(type=types[t],mode=modes[m]))
	return logevents


def log_data(type, start_log=0, num_of_logs=_all_logs, mode=_default_mode):
	if not type in types:
		raise exceptions.RuntimeError
	if not mode in modes:
		raise exceptions.RuntimeError
	logevents = _logs.list(type=types[type],mode=modes[mode])
	if num_of_logs == _all_logs:
		num_of_logs = len(logevents)
	return logevents[start_log : (start_log + num_of_logs)]


def log_data_by_time(type, start_time, end_time, mode=_default_mode):
	time_logs = []
	for l in log_data(type=type, mode=mode):
		# did not want to use (x)range because of memory/performance
		if l['time'] >= start_time and l['time'] <= end_time:
			time_logs.append(l)
	return time_logs


def calls(start_log=0, num_of_logs=_all_logs, mode=_default_mode):
	return log_data('call', start_log, num_of_logs, mode)

def faxes(start_log=0, num_of_logs=_all_logs, mode=_default_mode):
	return log_data('fax', start_log, num_of_logs, mode)

def emails(start_log=0, num_of_logs=_all_logs, mode=_default_mode):
	return log_data('email', start_log, num_of_logs, mode)

def sms(start_log=0, num_of_logs=_all_logs, mode=_default_mode):
	return log_data('sms', start_log, num_of_logs, mode)

def scheduler_logs(start_log=0, num_of_logs=_all_logs, mode=_default_mode):
	return log_data('scheduler', start_log, num_of_logs, mode)

def data_logs(start_log=0, num_of_logs=_all_logs, mode=_default_mode):
	return log_data('data', start_log, num_of_logs, mode)

