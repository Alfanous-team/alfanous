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

import os, sys

sys.path.insert(0, os.path.abspath(os.path.dirname(sys.argv[0])))

USAGE = """
Python to SIS
usage: %s <src> [sisfile] [--uid=0x01234567] [--appname=myapp] [--caps="cap_1 cap_2 ..."] [--presdk20] [--sdk30] [--armv5] [--leavetemp] [--autostart]

       src       - Source script or directory
       sisfile   - Path of the created SIS file
       uid       - Symbian UID for the application
       appname   - Name of the application
       caps      - A list of capabilities ("NONE", if caps is not given)
       presdk20  - Use a format suitable for pre-SDK2.0 phones
       sdk30     - Use a format suitable for SDK3.0 phones
       leavetemp - Leave temporary files in place
       armv5     - Generate armv5 binaries, by default gcce binaries are created. Only in SDK3.0
       autostart - Start the application during the device bootstrap (SDK3.0 only)

By default, py2sis outputs SIS packages suitable for S60 2.X handsets.

Packages for SDK3.0 phones are unsigned (use "SignSIS" for signing).
""" % os.path.basename(sys.argv[0]).lower()

if __name__ == '__main__':
    args = sys.argv
    if len(args) == 1:
        print USAGE
        sys.exit(1)
    import sismaker.cmdui
    try:
        sismaker.cmdui.main(*sys.argv[1:])
    except Exception, msg:
        print "ERROR %s" % msg
