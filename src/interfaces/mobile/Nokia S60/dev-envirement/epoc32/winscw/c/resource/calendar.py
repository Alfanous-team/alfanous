#
# calendar.py
#
# Copyright (c) 2006-2008 Nokia Corporation
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

import _calendar

def revdict(d):
    return dict([(d[k],k) for k in d.keys()])

# maps
replicationmap={"open":_calendar.rep_open,
                "private":_calendar.rep_private,
                "restricted":_calendar.rep_restricted}
_replicationreversemap=revdict(replicationmap)
entrytypemap={"appointment":_calendar.entry_type_appt,
              "event":_calendar.entry_type_event,
              "anniversary":_calendar.entry_type_anniv,
              "todo":_calendar.entry_type_todo,
              "reminder":_calendar.entry_type_reminder}
_entrytypereversemap=revdict(entrytypemap)


# Calendar database class
class CalendarDb(object):
    def __init__(self,dbfile=None,mode=None):
        if dbfile is None:
            self._db=_calendar.open()
        else:
            dbfile = unicode(dbfile)
            if len(dbfile)==0:
                raise RuntimeError, "invalid filename"
            if len(dbfile)<2 or dbfile[1]!=':':
                dbfile = u"c:" + dbfile
            if len(dbfile)==2:
                raise RuntimeError, "invalid filename"    
            if mode is None:
                self._db=_calendar.open(dbfile)
            else:
                self._db=_calendar.open(dbfile,mode)
    def __iter__(self):
        entry_ids=list()
        for id in self._db:
            entry_ids.append(id)
        return iter(entry_ids)
    def __len__(self):
        return self._db.entry_count()
    def __delitem__(self,key):
        self._db.delete_entry(key)
    def __getitem__(self,key):
        _entry = self._db.get_entry(key)
        if _entry.type()==_calendar.entry_type_appt:
            return CalendarDb.AppointmentEntry(_entry,self)
        elif _entry.type()==_calendar.entry_type_event:
            return CalendarDb.EventEntry(_entry,self)
        elif _entry.type()==_calendar.entry_type_anniv:
            return CalendarDb.AnniversaryEntry(_entry,self)
        elif _entry.type()==_calendar.entry_type_reminder:
            return CalendarDb.ReminderEntry(_entry,self)
        elif _entry.type()==_calendar.entry_type_todo:
            return CalendarDb.TodoEntry(_entry,self)
    def add_appointment(self):
        return CalendarDb.AppointmentEntry(self._db.add_entry(_calendar.entry_type_appt),self,locked='as_new_entry')
    def add_event(self):
        return CalendarDb.EventEntry(self._db.add_entry(_calendar.entry_type_event),self,locked='as_new_entry')
    def add_anniversary(self):
        return CalendarDb.AnniversaryEntry(self._db.add_entry(_calendar.entry_type_anniv),self,locked='as_new_entry')
    def add_reminder(self):
        return CalendarDb.ReminderEntry(self._db.add_entry(_calendar.entry_type_reminder),self,locked='as_new_entry')
    def add_todo(self):
        return CalendarDb.TodoEntry(self._db.add_entry(_calendar.entry_type_todo),self,locked='as_new_entry')
    def _create_filter(self,appointments,events,anniversaries,todos,reminders):
        filter=0
        if appointments:
            filter|=_calendar.appts_inc_filter
        if events:
            filter|=_calendar.events_inc_filter
        if anniversaries:
            filter|=_calendar.annivs_inc_filter
        if todos:
            filter|=_calendar.todos_inc_filter
        if reminders:
            filter|=_calendar.reminders_inc_filter
        return filter
    def monthly_instances(self,month,appointments=0,events=0,anniversaries=0,todos=0,reminders=0):
        return self._db.monthly_instances(month,self._create_filter(appointments,events,anniversaries,todos,reminders))
    def daily_instances(self,day,appointments=0,events=0,anniversaries=0,todos=0,reminders=0):
        return self._db.daily_instances(day,self._create_filter(appointments,events,anniversaries,todos,reminders))
    def find_instances(self,start_date,end_date,search_string=u'',appointments=0,events=0,anniversaries=0,todos=0,reminders=0):
        return self._db.find_instances(start_date,end_date,unicode(search_string),self._create_filter(appointments,events,anniversaries,todos,reminders))
    def export_vcalendars(self,entry_ids):
        return self._db.export_vcals(entry_ids)
    def import_vcalendars(self,vcalendar_string):
        return list(self._db.import_vcals(vcalendar_string))
    def compact(self):
        raise RuntimeError, "compacting no more supported"
    def add_todo_list(self,name=None):
        raise RuntimeError, "todo lists no more supported"
    
    # Entry class
    class Entry(object):   
        # PRIVATE functions    
        def __init__(self,_entry,db,locked=0):
            self._entry=_entry
            self._db=db
            self._locked=locked   
            self._available=1            
        def __del__(self):
            if self._locked:
                import warnings
                warnings.warn("entry still locked in destructor", RuntimeWarning)            
        def _set_content(self,content):
            self._fetch_entry()
            self._entry.set_content(unicode(content))
            self._autocommit()
        def _content(self):
            return self._entry.content()
        def _set_description(self,description):
            self._fetch_entry()
            self._entry.set_description(unicode(description))
            self._autocommit()
        def _description(self):
            return self._entry.description()
        def _get_type(self):
            return _entrytypereversemap[self._entry.type()]
        def _unique_id(self):
            return self._entry.unique_id()
        def _set_location(self,location):
            self._fetch_entry()
            self._entry.set_location(unicode(location))
            self._autocommit()
        def _location(self):
            return self._entry.location()
        def _last_modified(self):
            return self._entry.last_modified()
        def _set_priority(self,priority):
            self._fetch_entry()
            self._entry.set_priority(priority)
            self._autocommit()
        def _priority(self):
            return self._entry.priority()
        def _set_alarm(self,alarm_datetime):
            self._fetch_entry()
            if alarm_datetime is None:
                self._entry.cancel_alarm()
            else:
                self._entry.set_alarm(alarm_datetime)
            self._autocommit()
        def _get_alarm(self):
            return self._entry.alarm_datetime()
        def _set_replication(self, status):
            self._fetch_entry()
            self._entry.set_replication(replicationmap[status])
            self._autocommit()
        def _replication(self):
            if _replicationreversemap.has_key(self._entry.replication()):
                return _replicationreversemap[self._entry.replication()]
            return "unknown"  
        def _cross_out(self,value):
            self._fetch_entry()
            import time
            if value:
                self._entry.set_crossed_out(1,time.time())
            else:
                self._entry.set_crossed_out(0,time.time())
            self._autocommit()
        def _is_crossed_out(self):
            if self._entry.crossed_out_date() is None:
                return 0
            else:
                return 1
        def _start_datetime(self):
            return self._entry.start_datetime()
        def _end_datetime(self):
            return self._entry.end_datetime()
        def _originating_entry(self):
            return self._entry.originating_entry()
        def _autocommit(self):
            if not self._locked:
                self._entry.commit()
                self._available=0                
        #A workarround caused by platform bug: 
        #1665914   modifying calendar event with long event content field fails. 
        #This function will reload entry . Once the bug is fixed, function _fetch_entry(self) and it's calls should
        #be deleted. The same goes for flag self._available.
        def _fetch_entry(self):
            if self._available==0 and self._locked==0:         
                self._entry=self._db[self.id]._entry         

        # PUBLIC functions 
        def begin(self):
            self._fetch_entry()
            if self._locked:
                raise RuntimeError('entry already open')
            self._locked=1
        def commit(self):
            if not self._locked:
                raise RuntimeError('entry not open')
            self._entry.commit()
            self._locked=0
        def rollback(self):
            if not self._locked:
                raise RuntimeError('entry not open')
            if self._locked == 'as_new_entry':
                # clear the content of new uncommited entry by creating a new _entry.
                self._entry=self._db._db.add_entry(self._entry.type())
            else:
                # clear the content of old committed entry by fetching the last committed data from the database.
                self._entry=self._db._db[self._entry.unique_id()]
            self._locked=0
        def as_vcalendar(self):
            return self._db.export_vcalendars((self.id,))
        def set_repeat(self,repeat):
            self._fetch_entry()
            if not repeat:
                repeat={"type":"no_repeat"}
            self._entry.set_repeat_data(repeat)
            self._autocommit()
        def get_repeat(self):
            repeat=self._entry.repeat_data()
            if repeat["type"]=="no_repeat":
                return None
            return self._entry.repeat_data()
        def set_time(self,start=None,end=None):
            self._fetch_entry()
            if start is None:
                start=end
            if end is None:
                end=start
            if end is None and start is None:
                if self._entry.type()==_calendar.entry_type_todo:
                    self._entry.make_undated() # TODO: THIS DOES NOTHING???
                    return None
                else:
                    raise RuntimeError,"only todos can be made undated" 
            self._entry.set_start_and_end_datetime(start,end)
            self._autocommit()
            
        # PROPERTIES
        content=property(_content,_set_content)
        description=property(_description,_set_description)
        type=property(_get_type)
        location=property(_location,_set_location)
        last_modified=property(_last_modified)
        priority=property(_priority,_set_priority)
        id=property(_unique_id)
        crossed_out=property(_is_crossed_out,_cross_out)
        alarm=property(_get_alarm,_set_alarm)
        replication=property(_replication,_set_replication)
        end_time=property(_end_datetime)
        originating=property(_originating_entry)
        start_time=property(_start_datetime)
    
    # AppointmentEntry class
    class AppointmentEntry(Entry):
        def __init__(self,_entry,db,locked=0):
            CalendarDb.Entry.__init__(self,_entry,db,locked)
        def __str__(self):
            return '<AppointmentEntry #%d: "%s">'%(self.id,self.content)
    
    # EventEntry class
    class EventEntry(Entry):
        def __init__(self,_entry,db,locked=0):
            CalendarDb.Entry.__init__(self,_entry,db,locked)
        def __str__(self):
            return '<EventEntry #%d: "%s">'%(self.id,self.content)

    # AnniversaryEntry class
    class AnniversaryEntry(Entry):
        def __init__(self,_entry,db,locked=0):
            CalendarDb.Entry.__init__(self,_entry,db,locked)
        def __str__(self):
            return '<AnniversaryEntry #%d: "%s">'%(self.id,self.content)
            
    # ReminderEntry class
    class ReminderEntry(Entry):
        def __init__(self,_entry,db,locked=0):
            CalendarDb.Entry.__init__(self,_entry,db,locked)
        def __str__(self):
            return '<ReminderEntry #%d: "%s">'%(self.id,self.content)

    # TodoEntry class
    class TodoEntry(Entry):
        def __init__(self,_entry,db,locked=0):
            CalendarDb.Entry.__init__(self,_entry,db,locked)
        def __str__(self):
            return '<TodoEntry #%d: "%s">'%(self.id,self.content)
        def _get_cross_out_time(self):
            return self._entry.crossed_out_date()
        def _set_cross_out_time(self,cross_out_datetime):
            if cross_out_datetime==0:
                raise ValueError, "illegal datetime value"
            self._entry.set_crossed_out(1,cross_out_datetime)
            self._autocommit()
        cross_out_time=property(_get_cross_out_time,_set_cross_out_time)
        def _set_todo_list(self,list_id):
            raise RuntimeError, "todo lists no more supported"
        def _todo_list_id(self):
            raise RuntimeError, "todo lists no more supported"
        todo_list=property(_todo_list_id,_set_todo_list)

    # Todo list handling
    def _todo_lists(self):
        raise RuntimeError, "todo lists no more supported"
    todo_lists=property(_todo_lists)

        
# Module methods
def open(dbfile=None,mode=None):
    return CalendarDb(dbfile,mode)
