# Portions Copyright (c) 2005 Nokia Corporation 

"""Generic interface to all dbm clones."""

try:
    class error(Exception):
        pass
except (NameError, TypeError):
    error = "anydbm.error"

_names = ['dbhash', 'gdbm', 'dbm', 'e32dbm', 'dumbdbm']
_errors = [error]
_defaultmod = None

for _name in _names:
    try:
        _mod = __import__(_name)
    except ImportError:
        continue
    if not _defaultmod:
        _defaultmod = _mod
    _errors.append(_mod.error)

if not _defaultmod:
    raise ImportError, "no dbm clone found; tried %s" % _names

error = tuple(_errors)

def open(file, flag = 'r', mode = 0666):
    # guess the type of an existing database
    from whichdb import whichdb
    result=whichdb(file)
    if result is None:
        # db doesn't exist
        if 'c' in flag or 'n' in flag:
            # file doesn't exist and the new
            # flag was used so use default type
            mod = _defaultmod
        else:
            raise error, "need 'c' or 'n' flag to open new db"
    elif result == "":
        # db type cannot be determined
        raise error, "db type could not be determined"
    else:
        mod = __import__(result)
    return mod.open(file, flag, mode)
