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

import os, os.path, getopt

ARGS = ('uid=', 'appname=', 'caps=')
FLAGS = ('presdk20', 'sdk30', 'armv5', 'leavetemp', 'autostart')

def main(src, sisfile=None, *args):
    args = list(args)
    if sisfile is not None and sisfile.startswith('--'):
        args.insert(0, sisfile)
        sisfile = None

    arglist, values = getopt.getopt(args, '', ARGS+FLAGS)
    args = {}
    for k,v in arglist:
        key = k.strip('-')
        if key in FLAGS:
            v = True
        args[key] = v

    appname = args.get('appname')
    if sisfile is None:
        if appname is None:
            sisfile = os.path.basename(src)
            if os.path.isfile(src):
                sisfile = os.path.splitext(sisfile)[0]
        else:
            sisfile = appname
        sisfile = os.path.abspath(sisfile)+".sis"

    if args.get('presdk20'):
        print "Creating SIS for Pre-SDK2.0"
    elif args.get('sdk30'):
        print "Creating SIS for SDK3.0 and later"
    else:
        print "Creating SIS for SDK2.X"

    from sismaker import SISMaker
    s = SISMaker()
    try:
        output = s.make_sis(src, sisfile, **args)
    finally:
        if not args.get('leavetemp'):
            s.del_tempdir()
    print output

    if args.get('sdk30'):
        print "Note: Sign the created SIS file prior installation (tool \"SignSIS\")"
