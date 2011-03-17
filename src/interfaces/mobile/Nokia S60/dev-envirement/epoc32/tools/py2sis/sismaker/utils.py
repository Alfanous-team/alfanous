# Copyright (c) 2005-2007 Nokia Corporation
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

import os, sys, re
from shutil import copyfile, rmtree, copytree, copy
import template_engine
import fileutil


# for 1.x-2.x SDKs
UID_OFFSET_IN_APP = "0x3a4"

# for 3.x SDKs
SDK30_RSC_LOC = "\\Epoc32\\data\\z\\resource\\apps\\"
SDK30_REG_LOC = "\\Epoc32\\data\\z\\PRIVATE\\10003A3F\\APPS\\"

ERRMSG = "'%s' utility not found. Please make sure "\
         "you have the Symbian SDK correctly installed "\
         "and configured"

def uidcrc(uid):
    p = os.popen("uidcrc 0x10000079 0x100039CE "+uid, "r")
    s = p.read().strip()
    if not s:
        raise IOError, ERRMSG % 'uidcrc'
    uid1,uid2,uid3,crc = s.split()
    return crc

def make_sis(sisfile, pkgfile, searchpath):
    cmd = 'makesis -d"%s" %s %s' % (searchpath, pkgfile, sisfile)
    p = os.popen(cmd)
    s = p.read()
    if not s:
        raise IOError, ERRMSG % 'makesis'
    return s

def make_sis_sdk30(sisfile, pkgfile, searchpath):
    os.chdir(default_tempdir()) # there seems to be a bug with "makesis", hence the cwd change
    cmd = 'makesis %s %s' % (pkgfile, sisfile)
    print cmd
    p = os.popen(cmd)
    s = p.read()
    if not s:
        raise IOError, ERRMSG % 'makesis'
    return s

def find_main_script(src):
    if not os.path.exists(src):
        raise ValueError, "File or directory not found: %s" % src
    if os.path.isfile(src):
        if not src.endswith('.py'):
            raise ValueError, "Source file does not end in .py"
        main_script = src
    else:
        main_script = os.path.join(src, "default.py")
        if not os.path.exists(main_script):
            raise ValueError, "No default.py found in %s" % src        
    return main_script

def get_appname(src):
    appname = os.path.basename(src)
    if os.path.isfile(src):
        appname = os.path.splitext(appname)[0]
    return appname

def find_uid(src):
    m = re.search(r"SYMBIAN_UID\s*=\s*(0x[0-9a-fA-F]{8})", src)
    if not m:
        return
    return m.group(1)

def default_tempdir():
    return os.path.join(sys.path[0], "temp")

def default_builddir():
    return os.path.join(sys.path[0], "build")

def reverse(L):
    L.reverse()
    return L

def atoi(s):
    # Little-endian conversion from a 4-char string to an int.
    sum = 0L
    for x in reverse([x for x in s[0:4]]):
        sum = (sum << 8) + ord(x)
    return sum

def itoa(x):
    # Little-endian conversion from an int to a 4-character string.
    L=[chr(x>>24), chr((x>>16)&0xff), chr((x>>8)&0xff), chr(x&0xff)]
    L.reverse()
    return ''.join(L)

def make_app(appfile, template, uid, chksum):
    offset = int(UID_OFFSET_IN_APP, 16)
    #
    # copy the template .app file with proper name
    # and set the UID and checksum fields suitably
    #
    dotapp_name = appfile
    dotapp = file(dotapp_name, 'wb')
    appbuf = template
    csum = atoi(appbuf[24:28])
    crc1 = itoa(chksum)
    crc2 = itoa(( uid + csum ) & 0xffffffffL)
    if offset:
        temp = appbuf[0:8] + itoa(uid) + crc1 + appbuf[16:24] + crc2 +\
               appbuf[28:offset] + itoa(uid) + appbuf[(offset+4):]
    else:
        temp = appbuf[0:8] + itoa(uid) + crc1 + appbuf[16:24] + crc2 + appbuf[28:]
    dotapp.write(temp)

def make_app_sdk30(appname, uid, tempdir, tempdir_eka2, caps, armv5, autostart):
    if armv5:
        SDK30_EXE_LOC = "\\Epoc32\\release\\ARMV5\\UREL\\"
    else:
        SDK30_EXE_LOC = "\\Epoc32\\release\\GCCE\\UREL\\"
    # make builddir and copy templates to builddir:
    builddir = default_builddir()
    if os.path.exists(builddir):
        os.popen("attrib -r build\*.*") # XXX remove
        rmtree(builddir)

    copytree(os.path.join(sys.path[0], tempdir_eka2), builddir)

    # configure in builddir:
    import template_engine

    config = {}
    config["PY2SIS_UID"] = uid
    config["PY2SIS_APPNAME"] = appname
    if caps==None: # XXX sanity check for caps needed?
        config["PY2SIS_CAPS"] = "NONE"
    else:
        config["PY2SIS_CAPS"] = caps

    if autostart:
        config["PY2SIS_AUTOSTART"] = 1
    else:
        config["PY2SIS_AUTOSTART"] = 0     

    for f in fileutil.all_files(builddir,'*.template'):
        print "Processing template %s"%f
        template_engine.process_file(f,config)

    old_cw = os.getcwd()
    os.chdir(builddir)

    # copy the autostart file to correct name
    if autostart:
        copy("00000000.rss", (uid[2:] + ".rss"))

    # compilation step starts
    print "Compiling..."

    # bldmake bldfiles (in build_dir)
    os.popen("bldmake bldfiles") # XXX stdout?

    if armv5:
        # abld build armv5 urel
        os.popen("abld build armv5 urel") # XXX stdout?
    else:
        # abld build gcce urel
        os.popen("abld build gcce urel") # XXX stdout? }}

    print "Done."

    #make subdirectories:
    sys_bin = os.path.join(tempdir, 'sys', 'bin')
    resource_apps = os.path.join(tempdir, 'resource','apps')
    reg_private = os.path.join(tempdir, 'Private', '10003a3f', 'import', 'apps')
    if autostart:
        reg_autostart = os.path.join(tempdir, 'Private', '101f875a', 'import')
    os.makedirs(sys_bin)
    os.makedirs(resource_apps)
    os.makedirs(reg_private)
    if autostart:
        os.makedirs(reg_autostart)

    appname_uid = appname + '_' + uid

    #copy compiled files to temp folder to correct places:
    copy((SDK30_EXE_LOC + appname_uid + ".exe"), (os.path.join(sys_bin, (appname_uid + ".exe"))))
    copy((SDK30_RSC_LOC + appname_uid + '_' + "AIF" + ".mif"), (os.path.join(resource_apps, (appname_uid + '_' + "AIF" + ".mif"))))
    copy((SDK30_RSC_LOC + "PyTest.RSC"), os.path.join(resource_apps, (appname_uid + ".rsc")))
    copy((SDK30_REG_LOC + "PyTest_reg.rsc"), os.path.join(reg_private, (appname_uid + "_reg.rsc")))
    if autostart:
        copy((SDK30_RSC_LOC + (uid[2:] + ".rsc")), os.path.join(reg_autostart, ("["+uid[2:] + "]" + ".rsc")))

    os.chdir(old_cw)

def make_pkg(pkgfile, appname, template, uid, files):
    file = open(pkgfile, "w")
    file.write(template % (appname, uid))
    appdir = "!:\\system\\apps\\%s\\" % appname
    for src,dst in files:
        dstpath = appdir + dst
        file.write('"%s"\t\t-"%s"\n' % (src,dstpath))
    file.close()

def make_pkg_sdk30(pkgfile, appname, template, uid, files):
    file = open(pkgfile, "w")
    file.write(template % (appname, uid))
    appdir = "!:\\private\\%s\\" % uid[2:]
    for src,dst in files:
        ext = os.path.splitext(src)[1]
        if ext in ('.pyc', '.pyo', '.py'):
            dstpath = appdir + dst
            file.write('"%s"\t\t-"%s"\n' % (src,dstpath))
        else:
            file.write('"%s"\t\t-"!:\\%s"\n' % (src,dst))
    file.close()
