# Portions Copyright (c) 2005 - 2007 Nokia Corporation
import os
 
def copyfileobj(fsrc, fdst, length=16*1024):
    """copy data from file-like object fsrc to file-like object fdst"""
    while 1:
        buf = fsrc.read(length)
        if not buf:
            break
        fdst.write(buf)

def copyfile(src, dst):
    """Copy data from src to dst"""
    fsrc = None
    fdst = None
    try:
        fsrc = open(src, 'rb')
        fdst = open(dst, 'wb')
        copyfileobj(fsrc, fdst)
    finally:
        if fdst:
            fdst.close()
        if fsrc:
            fsrc.close()

def copy2(src, dst):
    """Copy data and all stat info ("cp -p src dst").
 
    The destination may be a directory.
 
    """
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    copyfile(src, dst)
#    copystat(src, dst)

