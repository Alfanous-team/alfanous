/* Portions Copyright (c) 2005 Nokia Corporation */
#ifndef Py_ITEROBJECT_H
#define Py_ITEROBJECT_H
/* Iterators (the basic kind, over a sequence) */
#ifdef __cplusplus
extern "C" {
#endif

  /* extern DL_IMPORT(const PyTypeObject) PySeqIter_Type; */

#define PySeqIter_Type ((PYTHON_GLOBALS->tobj).t_PySeqIter)

#define PySeqIter_Check(op) ((op)->ob_type == &PySeqIter_Type)

extern DL_IMPORT(PyObject *) PySeqIter_New(PyObject *);

  /* extern DL_IMPORT(const PyTypeObject) PyCallIter_Type; */

#define PyCallIter_Type ((PYTHON_GLOBALS->tobj).t_PyCallIter)

#define PyCallIter_Check(op) ((op)->ob_type == &PyCallIter_Type)

extern DL_IMPORT(PyObject *) PyCallIter_New(PyObject *, PyObject *);
#ifdef __cplusplus
}
#endif
#endif /* !Py_ITEROBJECT_H */

