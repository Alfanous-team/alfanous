/* Portions Copyright (c) 2005 Nokia Corporation */

#ifndef Py_PYDEBUG_H
#define Py_PYDEBUG_H
#ifdef __cplusplus
extern "C" {
#endif

  /* Eextern DL_IMPORT(int) Py_DebugFlag; */
#define Py_DebugFlag (PYTHON_GLOBALS->_DebugFlag)

  /* extern DL_IMPORT(int) Py_VerboseFlag; */
#define Py_VerboseFlag (PYTHON_GLOBALS->_VerboseFlag)

  /* extern DL_IMPORT(int) Py_InteractiveFlag; */
#define Py_InteractiveFlag (PYTHON_GLOBALS->_InteractiveFlag)

  /* extern DL_IMPORT(int) Py_OptimizeFlag; */
#define Py_OptimizeFlag (PYTHON_GLOBALS->_OptimizeFlag)

  /* extern DL_IMPORT(int) Py_NoSiteFlag; */
#define Py_NoSiteFlag (PYTHON_GLOBALS->_NoSiteFlag)

  /* extern DL_IMPORT(int) Py_UseClassExceptionsFlag; */
#define Py_UseClassExceptionsFlag (PYTHON_GLOBALS->_UseClassExceptionsFlag)

  /* extern DL_IMPORT(int) Py_FrozenFlag; */
#define Py_FrozenFlag (PYTHON_GLOBALS->_FrozenFlag)

  /* extern DL_IMPORT(int) Py_TabcheckFlag; */
#define Py_TabcheckFlag (PYTHON_GLOBALS->_TabcheckFlag)

  /* extern DL_IMPORT(int) Py_UnicodeFlag; */
#define Py_UnicodeFlag (PYTHON_GLOBALS->_UnicodeFlag)

  /* extern DL_IMPORT(int) Py_IgnoreEnvironmentFlag; */
#define Py_IgnoreEnvironmentFlag (PYTHON_GLOBALS->_IgnoreEnvironmentFlag)

  /* extern DL_IMPORT(int) Py_DivisionWarningFlag; */
#define Py_DivisionWarningFlag (PYTHON_GLOBALS->_DivisionWarningFlag)

/* _XXX Py_QnewFlag should go away in 2.3.  It's true iff -Qnew is passed,
  on the command line, and is used in 2.2 by ceval.c to make all "/" divisions
  true divisions (which they will be in 2.3). */
  /* extern DL_IMPORT(int) _Py_QnewFlag; */
#define _Py_QnewFlag (PYTHON_GLOBALS->_QnewFlag)

/* this is a wrapper around getenv() that pays attention to
   Py_IgnoreEnvironmentFlag.  It should be used for getting variables like
   PYTHONPATH and PYTHONHOME from the environment */
#define Py_GETENV(s) (Py_IgnoreEnvironmentFlag ? NULL : getenv(s))

DL_IMPORT(void) Py_FatalError(char *message);

#ifdef __cplusplus
}
#endif
#endif /* !Py_PYDEBUG_H */
