/* Portions Copyright (c) 2005 Nokia Corporation */
#ifndef Py_ERRORS_H
#define Py_ERRORS_H
#ifdef __cplusplus
extern "C" {
#endif


/* Error handling definitions */

DL_IMPORT(void) PyErr_SetNone(PyObject *);
DL_IMPORT(void) PyErr_SetObject(PyObject *, PyObject *);
DL_IMPORT(void) PyErr_SetString(PyObject *, const char *);
DL_IMPORT(PyObject *) PyErr_Occurred(void);
DL_IMPORT(void) PyErr_Clear(void);
DL_IMPORT(void) PyErr_Fetch(PyObject **, PyObject **, PyObject **);
DL_IMPORT(void) PyErr_Restore(PyObject *, PyObject *, PyObject *);

/* Error testing and normalization */
DL_IMPORT(int) PyErr_GivenExceptionMatches(PyObject *, PyObject *);
DL_IMPORT(int) PyErr_ExceptionMatches(PyObject *);
DL_IMPORT(void) PyErr_NormalizeException(PyObject**, PyObject**, PyObject**);


/* Predefined exceptions */

  /* extern DL_IMPORT(PyObject *) PyExc_Exception; */
#define PyExc_Exception (PYTHON_GLOBALS->_PyExc_Exception)
  /* extern DL_IMPORT(PyObject *) PyExc_StopIteration; */
#define PyExc_StopIteration (PYTHON_GLOBALS->_PyExc_StopIteration)
  /* extern DL_IMPORT(PyObject *) PyExc_StandardError; */
#define PyExc_StandardError (PYTHON_GLOBALS->_PyExc_StandardError)
  /* extern DL_IMPORT(PyObject *) PyExc_ArithmeticError; */
#define PyExc_ArithmeticError (PYTHON_GLOBALS->_PyExc_ArithmeticError)
  /* extern DL_IMPORT(PyObject *) PyExc_LookupError; */
#define PyExc_LookupError (PYTHON_GLOBALS->_PyExc_LookupError)

  /* extern DL_IMPORT(PyObject *) PyExc_AssertionError; */
#define PyExc_AssertionError (PYTHON_GLOBALS->_PyExc_AssertionError)
  /* extern DL_IMPORT(PyObject *) PyExc_AttributeError; */
#define PyExc_AttributeError (PYTHON_GLOBALS->_PyExc_AttributeError)
  /* extern DL_IMPORT(PyObject *) PyExc_EOFError; */
#define PyExc_EOFError (PYTHON_GLOBALS->_PyExc_EOFError)
  /* extern DL_IMPORT(PyObject *) PyExc_FloatingPointError; */
#define PyExc_FloatingPointError (PYTHON_GLOBALS->_PyExc_FloatingPointError)
  /* extern DL_IMPORT(PyObject *) PyExc_EnvironmentError; */
#define PyExc_EnvironmentError (PYTHON_GLOBALS->_PyExc_EnvironmentError)
  /* extern DL_IMPORT(PyObject *) PyExc_IOError; */
#define PyExc_IOError (PYTHON_GLOBALS->_PyExc_IOError)
  /* extern DL_IMPORT(PyObject *) PyExc_OSError; */
#define PyExc_OSError (PYTHON_GLOBALS->_PyExc_OSError)
  /* extern DL_IMPORT(PyObject *) PyExc_ImportError; */
#define PyExc_ImportError (PYTHON_GLOBALS->_PyExc_ImportError)
  /* extern DL_IMPORT(PyObject *) PyExc_IndexError; */
#define PyExc_IndexError (PYTHON_GLOBALS->_PyExc_IndexError)
  /* extern DL_IMPORT(PyObject *) PyExc_KeyError; */
#define PyExc_KeyError (PYTHON_GLOBALS->_PyExc_KeyError)
  /* extern DL_IMPORT(PyObject *) PyExc_KeyboardInterrupt; */
#define PyExc_KeyboardInterrupt (PYTHON_GLOBALS->_PyExc_KeyboardInterrupt)
  /* extern DL_IMPORT(PyObject *) PyExc_MemoryError; */
#define PyExc_MemoryError (PYTHON_GLOBALS->_PyExc_MemoryError)
  /* extern DL_IMPORT(PyObject *) PyExc_NameError; */
#define PyExc_NameError (PYTHON_GLOBALS->_PyExc_NameError)
  /* extern DL_IMPORT(PyObject *) PyExc_OverflowError; */
#define PyExc_OverflowError (PYTHON_GLOBALS->_PyExc_OverflowError)
  /* extern DL_IMPORT(PyObject *) PyExc_RuntimeError; */
#define PyExc_RuntimeError (PYTHON_GLOBALS->_PyExc_RuntimeError)
  /* extern DL_IMPORT(PyObject *) PyExc_NotImplementedError; */
#define PyExc_NotImplementedError (PYTHON_GLOBALS->_PyExc_NotImplementedError)
  /* extern DL_IMPORT(PyObject *) PyExc_SyntaxError; */
#define PyExc_SyntaxError (PYTHON_GLOBALS->_PyExc_SyntaxError)
  /* extern DL_IMPORT(PyObject *) PyExc_IndentationError; */
#define PyExc_IndentationError (PYTHON_GLOBALS->_PyExc_IndentationError)
  /* extern DL_IMPORT(PyObject *) PyExc_TabError; */
#define PyExc_TabError (PYTHON_GLOBALS->_PyExc_TabError)
  /* extern DL_IMPORT(PyObject *) PyExc_ReferenceError; */
#define PyExc_ReferenceError (PYTHON_GLOBALS->_PyExc_ReferenceError)
  /* extern DL_IMPORT(PyObject *) PyExc_SystemError; */
#define PyExc_SystemError (PYTHON_GLOBALS->_PyExc_SystemError)
  /* extern DL_IMPORT(PyObject *) PyExc_SystemExit; */
#define PyExc_SystemExit (PYTHON_GLOBALS->_PyExc_SystemExit)
  /* extern DL_IMPORT(PyObject *) PyExc_TypeError; */
#define PyExc_TypeError (PYTHON_GLOBALS->_PyExc_TypeError)
  /* extern DL_IMPORT(PyObject *) PyExc_UnboundLocalError; */
#define PyExc_UnboundLocalError (PYTHON_GLOBALS->_PyExc_UnboundLocalError)
  /* extern DL_IMPORT(PyObject *) PyExc_UnicodeError; */
#define PyExc_UnicodeError (PYTHON_GLOBALS->_PyExc_UnicodeError)
  /* extern DL_IMPORT(PyObject *) PyExc_ValueError; */
#define PyExc_ValueError (PYTHON_GLOBALS->_PyExc_ValueError)
  /* extern DL_IMPORT(PyObject *) PyExc_ZeroDivisionError; */
#define PyExc_ZeroDivisionError (PYTHON_GLOBALS->_PyExc_ZeroDivisionError)
#ifdef MS_WINDOWS
  /* extern DL_IMPORT(PyObject *) PyExc_WindowsError; */
#define PyExc_WindowsError (PYTHON_GLOBALS->_PyExc_WindowsError)
#endif
#ifdef SYMBIAN
#define PyExc_SymbianError (PYTHON_GLOBALS->_PyExc_SymbianError)
#endif

  /* extern DL_IMPORT(PyObject *) PyExc_MemoryErrorInst; */
#define PyExc_MemoryErrorInst (PYTHON_GLOBALS->_PyExc_MemoryErrorInst)

/* Predefined warning categories */
  /* extern DL_IMPORT(PyObject *) PyExc_Warning; */
#define PyExc_Warning (PYTHON_GLOBALS->_PyExc_Warning)
  /* extern DL_IMPORT(PyObject *) PyExc_UserWarning; */
#define PyExc_UserWarning (PYTHON_GLOBALS->_PyExc_UserWarning)
  /* extern DL_IMPORT(PyObject *) PyExc_DeprecationWarning; */
#define PyExc_DeprecationWarning (PYTHON_GLOBALS->_PyExc_DeprecationWarning)
  /* extern DL_IMPORT(PyObject *) PyExc_SyntaxWarning; */
#define PyExc_SyntaxWarning (PYTHON_GLOBALS->_PyExc_SyntaxWarning)
  /* extern DL_IMPORT(PyObject *) PyExc_OverflowWarning; */
#define PyExc_OverflowWarning (PYTHON_GLOBALS->_PyExc_OverflowWarning)
  /* extern DL_IMPORT(PyObject *) PyExc_RuntimeWarning; */
#define PyExc_RuntimeWarning (PYTHON_GLOBALS->_PyExc_RuntimeWarning)


/* Convenience functions */

extern DL_IMPORT(int) PyErr_BadArgument(void);
extern DL_IMPORT(PyObject *) PyErr_NoMemory(void);
extern DL_IMPORT(PyObject *) PyErr_SetFromErrno(PyObject *);
extern DL_IMPORT(PyObject *) PyErr_SetFromErrnoWithFilename(PyObject *, char *);
extern DL_IMPORT(PyObject *) PyErr_Format(PyObject *, const char *, ...)
			__attribute__((format(printf, 2, 3)));
#ifdef MS_WINDOWS
extern DL_IMPORT(PyObject *) PyErr_SetFromWindowsErrWithFilename(int, const char *);
extern DL_IMPORT(PyObject *) PyErr_SetFromWindowsErr(int);
#endif

/* Export the old function so that the existing API remains available: */
extern DL_IMPORT(void) PyErr_BadInternalCall(void);
extern DL_IMPORT(void) _PyErr_BadInternalCall(char *filename, int lineno);
/* Mask the old API with a call to the new API for code compiled under
   Python 2.0: */
#define PyErr_BadInternalCall() _PyErr_BadInternalCall(__FILE__, __LINE__)

/* Function to create a new exception */
DL_IMPORT(PyObject *) PyErr_NewException(char *name, PyObject *base,
                                         PyObject *dict);
extern DL_IMPORT(void) PyErr_WriteUnraisable(PyObject *);

/* Issue a warning or exception */
extern DL_IMPORT(int) PyErr_Warn(PyObject *, char *);
extern DL_IMPORT(int) PyErr_WarnExplicit(PyObject *, char *,
					 char *, int, char *, PyObject *);

/* In sigcheck.c or signalmodule.c */
extern DL_IMPORT(int) PyErr_CheckSignals(void);
extern DL_IMPORT(void) PyErr_SetInterrupt(void);

/* Support for adding program text to SyntaxErrors */
extern DL_IMPORT(void) PyErr_SyntaxLocation(char *, int);
extern DL_IMPORT(PyObject *) PyErr_ProgramText(char *, int);

/* These APIs aren't really part of the error implementation, but
   often needed to format error messages; the native C lib APIs are
   not available on all platforms, which is why we provide emulations
   for those platforms in Python/mysnprintf.c,
   WARNING:  The return value of snprintf varies across platforms; do
   not rely on any particular behavior; eventually the C99 defn may
   be reliable.
*/
#if defined(MS_WIN32) && !defined(HAVE_SNPRINTF)
# define HAVE_SNPRINTF
# define snprintf _snprintf
# define vsnprintf _vsnprintf
#endif

#include <stdarg.h>
extern DL_IMPORT(int) PyOS_snprintf(char *str, size_t size, const char  *format, ...)
			__attribute__((format(printf, 3, 4)));
extern DL_IMPORT(int) PyOS_vsnprintf(char *str, size_t size, const char  *format, va_list va)
			__attribute__((format(printf, 3, 0)));


#ifdef __cplusplus
}
#endif
#endif /* !Py_ERRORS_H */
