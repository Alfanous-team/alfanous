/* Portions Copyright (c) 2005 Nokia Corporation */

#ifndef Py_TRACEBACK_H
#define Py_TRACEBACK_H
#ifdef __cplusplus
extern "C" {
#endif

/* Traceback interface */

struct _frame;

DL_IMPORT(int) PyTraceBack_Here(struct _frame *);
DL_IMPORT(int) PyTraceBack_Print(PyObject *, PyObject *);

/* Reveal traceback type so we can typecheck traceback objects */
  /* extern DL_IMPORT(const PyTypeObject) PyTraceBack_Type; */
#define PyTraceBack_Type ((PYTHON_GLOBALS->tobj).t_PyTraceBack)

#define PyTraceBack_Check(v) ((v)->ob_type == &PyTraceBack_Type)

#ifdef __cplusplus
}
#endif
#endif /* !Py_TRACEBACK_H */
