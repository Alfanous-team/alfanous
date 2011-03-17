/* Portions Copyright (c) 2005 Nokia Corporation */
#ifndef Py_SLICEOBJECT_H
#define Py_SLICEOBJECT_H
#ifdef __cplusplus
extern "C" {
#endif

/* The unique ellipsis object "..." */

  /* extern DL_IMPORT(const PyObject) _Py_EllipsisObject; *//* Don't use this directly */

#define Py_Ellipsis (&(PYTHON_GLOBALS->_Py_EllipsisObject))

#define PyEllipsis_Type ((PYTHON_GLOBALS->tobj).t_PyEllipsis)

/* Slice object interface */

/*

A slice object containing start, stop, and step data members (the
names are from range).  After much talk with Guido, it was decided to
let these be any arbitrary python type.
*/

typedef struct {
    PyObject_HEAD
    PyObject *start, *stop, *step;
} PySliceObject;

  /* extern DL_IMPORT(const PyTypeObject) PySlice_Type; */

#define PySlice_Type ((PYTHON_GLOBALS->tobj).t_PySlice)

#define PySlice_Check(op) ((op)->ob_type == &PySlice_Type)

DL_IMPORT(PyObject *) PySlice_New(PyObject* start, PyObject* stop,
                                  PyObject* step);
DL_IMPORT(int) PySlice_GetIndices(PySliceObject *r, int length,
                                  int *start, int *stop, int *step);

#ifdef __cplusplus
}
#endif
#endif /* !Py_SLICEOBJECT_H */
