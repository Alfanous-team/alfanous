
# This module implements a gdbm-like DBM object on top of the native
# Symbian DBMS using the e32db module.
#
# Note:
# 1) There is currently no support for concurrent access.
# 2) The internal database format may still change. No guarantee
#    of compatibility is given for databases created with
#    different releases.
#
# Copyright (c) 2005-2006 Nokia Corporation
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


import os

try:
    import e32db
except ImportError:
    # prevent a second import of this module from spuriously succeeding
    import sys
    del sys.modules[__name__]
    raise

# encoding used for storing string data in the database
_dbencoding='latin1'

def sqlquote(value):
    if type(value) is str:
        value=value.decode(_dbencoding)
    return value.replace("'","''")

class e32dbm:
    """e32dbm.open will returns a class instance of this type."""
    def __init__(self, flags, db):
        self.flags = flags
        self.db = db
        self.fast = 'f' in flags
        self.pending_updates = {}
    def __del__(self):
        if self.db:
            self.close()
    # direct DB access functions
    def _query(self,statement):
        """Execute a query and return results."""
        #print "Executing query: %s"%statement
        DBV = e32db.Db_view()
        DBV.prepare(self.db, unicode(statement))
        n = DBV.count_line()
        DBV.first_line()
        data=[]
        for i in xrange(n):
            DBV.get_line()
            line=[]
            for j in xrange(DBV.col_count()):
                line.append(DBV.col(1+j).encode(_dbencoding))
            data.append(tuple(line))
            DBV.next_line()
        del DBV
        return data
    def _execute(self,statement):
        #print "Executing: %s"%statement
        self.db.execute(statement)

    # DB access layer, accesses only database, not
    # the pending_updates cache.
    def _dbget(self, key):
        try:
            results=self._query(
                u"select key, value from data where hash=%d and key='%s'"%
                (hash(key),sqlquote(key)))
        except SymbianError:
#           import traceback
#           traceback.print_exc()
            raise KeyError(key)
        if len(results)==0:
            #print "empty result"
            raise KeyError(key)
        return results[0][1]
    def _dbhaskey(self,key):
        try:
            self._dbget(key)
        except KeyError:
            return False
        return True
    def _dbset(self, key, value):
        if self._dbhaskey(key):
            self._execute(u"UPDATE data SET value='%s' WHERE hash=%d AND key='%s'"% (sqlquote(value),hash(key),sqlquote(key)))
        else:
            self._execute(u"INSERT INTO data VALUES (%d,'%s','%s')"% (hash(key),sqlquote(key),sqlquote(value)))
    def _dbclear(self):
        self._execute(u"DELETE FROM data")
    def _dbdel(self, key):
        self._execute(u"DELETE FROM data WHERE hash=%d AND key='%s'"% (hash(key),sqlquote(key)))
        
    # cached DB access functions
    def keys(self):
        results=self._query(u"select key from data")
        keydict=dict([(x[0],1) for x in results])       
        if self.fast:
            keydict.update(self.pending_updates)
        # remove deleted records from list of keys
        return filter(lambda x: keydict[x] is not None,keydict)
    def items(self):
        results=self._query(u"select key,value from data")
        data=dict([(x[0],x[1]) for x in results])       
        if self.fast:
            data.update(self.pending_updates)
        # remove deleted records from list of items
        return filter(lambda x: x[1] is not None,data.items())
    def values(self):
        return map(lambda x: x[1], self.items())

    # essential application layer
    def __getitem__(self, key):     
        if type(key) != type("") and type(key) != type(u""):
            raise TypeError, "Only string keys are accepted."
        if self.pending_updates.has_key(key):
            if self.pending_updates[key] is None:
                raise KeyError
            else:
                return self.pending_updates[key]
        else:
            return self._dbget(key)
    def __setitem__(self, key, value):
        if 'r' in self.flags:
            raise IOError, "Read-only database."
        if type(key) != type("") and type(key) != type(u""):
            raise TypeError, "Only string keys are accepted."
        if type(value) != type("") and type(value) != type(u""):
            raise TypeError, "Only string values are accepted."
        if self.fast:
            self.pending_updates[key]=value
        else:
            self._dbset(key,value)
    def __delitem__(self, key):
        if 'r' in self.flags:
            raise IOError, "Read-only database."
        if type(key) != type("") and type(key) != type(u""):
            raise TypeError, "Only string keys are accepted."
        if self.fast:
            self.pending_updates[key]=None
        else:
            self._dbdel(key)

    # nonessential application layer, convenience functions.
    def has_key(self,targetkey):
        try:
            self.__getitem__(targetkey)
            return True
        except KeyError:
            return False    
    def update(self,newdata):
        for k in newdata:
            self[k]=newdata[k]

    def __len__(self):
        # FIXME should ask this via SQL for efficiency
        return len(self.keys())
    def __iter__(self):
        return self.iterkeys()
    def iterkeys(self):
        return iter(self.keys())
    def iteritems(self):
        return iter(self.items())
    def itervalues(self):
        return iter(self.values())
    def get(self,key,defaultvalue=None):
        if self.has_key(key):
            return self[key]
        else:
            return defaultvalue
    def setdefault(self,key,defaultvalue=None):
        if self.has_key(key):
            return self[key]
        else:
            self[key]=defaultvalue
            return defaultvalue
    def pop(self,key,defaultvalue=None):
        try:
            value=self[key]
            del self[key]
            return value
        except KeyError:
            if defaultvalue is not None:
                return defaultvalue
            raise KeyError("dictionary is empty")
    def popitem(self):
        # FIXME this could be done more efficiently
        items=self.items()
        if len(items)==0:
            raise KeyError("dictionary is empty")
        item=items[0]
        del self[item[0]]
        return item

    def clear(self):
        self._dbclear()
        self.pending_updates={}
        
    def close(self):
        """Close the database. Further access will fail."""
        if self.db:
            self.sync()
            self.db.close()
            self.db = None
        else:
            raise RuntimeError("Already closed")
    def sync(self):
        """Synchronize memory and disk databases. In the slow
        mode this is done for all accesses that modify the
        memory database, in the fast mode, on close and on
        explicit call."""
        if not self.fast:
            return
        self.db.begin()
        try:
            for key,value in self.pending_updates.items():
                if value is None:
                    self._dbdel(key)
                else:
                    self._dbset(key,value)
            self.db.commit()
            self.pending_updates={}
        except:
            self.db.rollback()
            raise
    def reorganize(self):
        self.sync()
        self.db.compact()

def open(name, flags = 'r', mode = 0666):
    """Open the specified database, flags is one of c to create
    it, if it does not exist, n to create a new one (will destroy
    old contents), r to open it read-only and w to open it read-
    write. Appending 'f' to the flags opens the database in fast
    mode, where updates are not written to the database
    immediately. Use the sync() method to force a write."""
    create = 0
    if name.endswith('.e32dbm'):
        filename=unicode(name)
    else:
        filename=unicode(name+'.e32dbm')
    
    if flags[0] not in 'cnrw':
        raise TypeError, "First flag must be one of c, n, r, w."
    if flags[0] == 'c' and not os.path.exists(filename):
        create = 1
    if flags[0] == 'n':
        create = 1
    db = e32db.Dbms()
    if create:
        db.create(filename)
        db.open(filename)
        db.execute(u"CREATE TABLE data (hash integer, key LONG VARCHAR, value LONG VARCHAR)")
        # The funny separate hash column is needed because an index
        # for a truncated column can't be created with the SQL
        # interface.
        db.execute(u"CREATE INDEX hash_idx ON data (hash)")
    else:
        db.open(filename)
    return e32dbm(flags, db)

error = SymbianError

__all__ = ["error","open"]
