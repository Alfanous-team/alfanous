/* Portions Copyright (c) 2005 Nokia Corporation */

/* Tuple object interface */

#ifndef Py_STRUCTSEQ_H
#define Py_STRUCTSEQ_H
#ifdef __cplusplus
extern "C" {
#endif
               
typedef struct PyStructSequence_Field {
	char *name;
	char *doc;
} PyStructSequence_Field;

typedef struct PyStructSequence_Desc {
	char *name;
	// XXX:CW32
	const char *doc;
	// XXX:CW32
	const struct PyStructSequence_Field *fields;
	int n_in_sequence;
} PyStructSequence_Desc;

// XXX:CW32
extern DL_IMPORT(void) PyStructSequence_InitType(PyTypeObject *type, 
						 const PyStructSequence_Desc *desc);
       
extern DL_IMPORT(PyObject *) PyStructSequence_New(PyTypeObject* type);

typedef struct {
	PyObject_VAR_HEAD
	PyObject *ob_item[1];
} PyStructSequence;

/* Macro, *only* to be used to fill in brand new objects */
#define PyStructSequence_SET_ITEM(op, i, v) \
	(((PyStructSequence *)(op))->ob_item[i] = v)

#define _struct_sequence_template ((PYTHON_GLOBALS->tobj).t_struct_sequence_template)

#ifdef __cplusplus
}
#endif
#endif /* !Py_STRUCTSEQ_H */
