#
# dir_iter.py
#
# Utility module for filebrowser.
#     
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
#

import sys
import os
import time

class Directory_iter:
    def __init__(self, drive_list):
        self.drives = [((i, u"Drive")) for i in drive_list]
        self.at_root = 1
        self.path = '\\'

    def pop(self):
        if os.path.splitdrive(self.path)[1] == '\\':
            self.path = '\\'
            self.at_root = 1
        else:
            self.path = os.path.split(self.path)[0]

    def add(self, i):
        if self.at_root:
            self.path = str(self.drives[i][0]+u'\\')
            self.at_root = 0
        else:
            self.path = os.path.join(self.path, os.listdir(self.name())[i])

    def name(self):
        return self.path

    def list_repr(self):
        if self.at_root:
            return self.drives
        else:
            def item_format(i):
                full_name = os.path.join(str(self.name()), i)
                try:
                    time_field = time.strftime("%d.%m.%Y %H:%M",\
                                               time.localtime(os.stat(full_name).st_mtime));
                    info_field = time_field+"  "+str(os.stat(full_name).st_size)+"b"
                    if os.path.isdir(full_name):
                        name_field = "["+i+"]"
                    else:
                        name_field = i
                except:
                    info_field = "[inaccessible]"
                    name_field = "["+i+"]"
                return (unicode(name_field), unicode(info_field))
            try:
                l = map(item_format, os.listdir(self.name()))
            except:
                l = []
            return l

    def entry(self, i):
        return os.path.join(self.name(), os.listdir(self.name())[i])
