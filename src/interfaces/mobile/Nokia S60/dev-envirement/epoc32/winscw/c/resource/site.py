# Portions Copyright (c) 2005 Nokia Corporation 
import sys, os
import e32

import __builtin__

# interactive prompt objects for printing the license text, a list of
# contributors and the copyright notice.
class _Printer:

    def __init__(self, name, data, files=(), dirs=()):
        self.__name = name
        self.__data = data
        self.__files = files
        self.__dirs = dirs
        self.__lines = None

    def __setup(self):
        if self.__lines:
            return
        data = None
        for dir in self.__dirs:
            for file in self.__files:
                file = os.path.join(dir, file)
                try:
                    fp = open(file)
                    data = fp.read()
                    fp.close()
                    break
                except IOError:
                    pass
            if data:
                break
        if not data:
            data = self.__data
        self.__lines = data.split('\n')
        self.__linecnt = len(self.__lines)

    def __repr__(self):
        self.__setup()
        return "\n".join(self.__lines)

    def __call__(self):
        self.__setup()
        lineno = 0
        try:
            for i in range(lineno, lineno + self.__linecnt):
                print self.__lines[i]
        except IndexError:
            pass

nokia_copyright = "\n\nPython for S60 is Copyright (c) 2004-2007 Nokia.\n"
__builtin__.copyright = _Printer("copyright", sys.copyright+nokia_copyright)
__builtin__.credits = _Printer("credits", """\
See www.python.org for more information.""")
here = os.path.dirname(os.__file__)
__builtin__.license = _Printer(
    "license", '''
Copyright (c) 2005-2006 Nokia Corporation. This is Python for S60 version
'''+e32.pys60_version+''' created by Nokia Corporation. Files added by Nokia
Corporation are licensed under Apache License Version 2.0. The
original software, including modifications of Nokia Corporation
therein, is licensed under the applicable license(s) for Python 2.2.2,
unless specifically indicated otherwise in the relevant source code
file.

See http://www.apache.org/licenses/LICENSE-2.0
and http://www.python.org/2.2.2/license.html
''',["LICENSE.txt", "LICENSE"],
    [here])

#
# The test for presence is needed when
# this module is run as a script, because this code is executed twice.
#

def _test():
    print "sys.path = ["
    for dir in sys.path:
        print "    %s," % `dir`
    print "]"

if __name__ == '__main__':
    _test()

# Set a special import hook for loading native code if running under
# S60 3rd edition. Seems like the only way to test for the existence
# of a .pyd in 3rd ed is to try to load it.
import e32
if e32.s60_version_info>=(3,0):
    import imp
    _original_import=__builtin__.__import__
    def platsec_import(name, globals=None, locals=None, fromlist=None):
        name=str(name)
        try:
            # First try importing the given module as Python code.
            return _original_import(name, globals, locals, fromlist)
        except ImportError, e:
            # Couldn't import the module. Check that it was really the
            # top level import that failed and not a nested import.
            error_message=e.args[0]
            if error_message != 'No module named '+name:            
                raise # The top level module was found - this ImportError
                      # is from a nested import. Pass the exception
                      # through.
            # Couldn't find a Python module with that name. Try importing
            # as native code.
            try:
                return imp.load_dynamic(name, name+'.pyd')
            except SymbianError, e:
                if e[0]==-1: # KErrNotFound
                    raise ImportError("No module named "+name)
                if e[0]==-46: # KErrPermissionDenied
                    raise ImportError("Permission denied (error -46). Possible cause: Check that %s.pyd is compiled to have at least the same capabilities as this Python interpreter process."%name)
                # Pass other exceptions through.
                raise
    __builtin__.__import__=platsec_import
