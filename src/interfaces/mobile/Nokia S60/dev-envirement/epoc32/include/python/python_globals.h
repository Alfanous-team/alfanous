/*
* ====================================================================
*  python_globals.h  
*  
*  Facilities to store static writable variables to thread local
*  storage in Symbian environment.
*     
* Copyright (c) 2005 Nokia Corporation
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
* ====================================================================
*/

#ifndef __PYTHON_GLOBALS_H
#define __PYTHON_GLOBALS_H

#include "Python.h"
#include "importdl.h"
#include "grammar.h"
#include "pythread.h"

#ifdef __cplusplus
extern "C" {
#endif

  typedef struct wrapperbase slotdef;

  typedef struct {
    char *name;
    PyObject **exc;
    PyObject **base;                    
    char *docstr;
    PyMethodDef *methods;
    int (*classinit)(PyObject *);
  } t_exctable;

  typedef struct {
    PyTypeObject t_PyBuffer;
    PyTypeObject t_PyType;
    PyTypeObject t_PyBaseObject;
    PyTypeObject t_PySuper;
    PyTypeObject t_PyCell;
    PyTypeObject t_PyClass;
    PyTypeObject t_PyInstance;
    PyTypeObject t_PyMethod;
    PyTypeObject t_PyCObject;
    PyTypeObject t_PyComplex;
    PyTypeObject t_PyWrapperDescr;
    PyTypeObject t_PyProperty;
    PyTypeObject t_PyMethodDescr;
    PyTypeObject t_PyMemberDescr;
    PyTypeObject t_PyGetSetDescr;
    PyTypeObject t_proxytype;
    PyTypeObject t_wrappertype;
    PyTypeObject t_PyDict;
    PyTypeObject t_PyDictIter;
    PyTypeObject t_PyFile;
    PyTypeObject t_PyFloat;
    PyTypeObject t_PyFrame;
    PyTypeObject t_PyFunction;
    PyTypeObject t_PyClassMethod;
    PyTypeObject t_PyStaticMethod;
    PyTypeObject t_PyInt;
    PyTypeObject t_PyList;
    PyTypeObject t_immutable_list_type;
    PyTypeObject t_PyLong;
    PyTypeObject t_PyCFunction;
    PyTypeObject t_PyModule;
    PyTypeObject t_PyNone;
    PyTypeObject t_PyNotImplemented;
    PyTypeObject t_PyRange;
    PyTypeObject t_PySlice;
    PyTypeObject t_PyString;
    PyTypeObject t_PyTuple;
    PyTypeObject t_PyUnicode;
    PyTypeObject t_PySeqIter;
    PyTypeObject t_PyCallIter;
    PyTypeObject t__PyWeakref_Ref;
    PyTypeObject t__PyWeakref_Proxy;
    PyTypeObject t__PyWeakref_CallableProxy;
    PyTypeObject t_struct_sequence_template;
    PyTypeObject t_PyEllipsis;
    PyTypeObject t_gentype;
    PyTypeObject t_PyCode;
    PyTypeObject t_PySymtableEntry;
    PyTypeObject t_PyTraceBack;
    PyTypeObject t_Lock;
    PyTypeObject t_StructTimeType;    // timemodule.c
    PyTypeObject t_StatResultType;    // posixmodule.c
    PyTypeObject t_MD5;               // md5module.c
    PyTypeObject t_Pattern;           // _sre.c
    PyTypeObject t_Match;             // _sre.c
    PyTypeObject t_Scanner;           // _sre.c
    /* own extensions */
    PyTypeObject t_Application;
    PyTypeObject t_Listbox;
    PyTypeObject t_Content_handler;
    PyTypeObject t_Form;
    PyTypeObject t_Text;
    PyTypeObject t_Ao;
    PyTypeObject t_Ao_callgate;
    // Not here because we want to preserve binary compatibility for now. See the end of SPy_Python_globals.
    //PyTypeObject t_Canvas; 
  } SPy_type_objects;

  /*
   * struct SPy_Python_globals that holds the globals
   */

  typedef struct {
    char buildinfo[50];                // Modules\getbuildinfo.c
    PyObject* ZlibError;               // Modules\zlibmodule.c
    PyObject* StructError;             // Modules\structmodule.c
    PyObject* binascii_Error;          // Modules\binascii.c
    PyObject* binascii_Incomplete;
    PyObject* moddict;                 // Modules\timemodule.c
#ifdef WITH_CYCLE_GC
    void* gc_globals;                  // Modules\gcmodule.c
#endif
#ifdef not_def
    grammar _PyParser_Grammar_mutable; // Parser\pythonrun.c
#endif
    int (*PyOS_InputHook)();           // Parser\myreadline.c
    char *(*PyOS_ReadlineFunctionPointer)(char *);
    char grammar1_buf[100];            // Parser\grammar1.c
    int listnode_level;                // Parser\listnode.c
    int listnode_atbol;
    int _TabcheckFlag;                 // Parser\parsetok.c
#define NPENDINGCALLS 32
    struct {
      int (*func)(void *);
      void *arg;
    } pendingcalls[NPENDINGCALLS];     // Python\ceval.c
    PyThread_type_lock interpreter_lock;
    long main_thread;
    int pendingfirst;
    int pendinglast;
    int things_to_do;
    int recursion_limit;
    int add_pending_call_busy;
    int make_pending_calls_busy;
    PyObject* implicit;                // Python\compile.c
    char ok_name_char[256];
    PyObject* _PyExc_Exception;        // Python\exceptions.c
    PyObject* _PyExc_StopIteration;
    PyObject* _PyExc_StandardError;
    PyObject* _PyExc_ArithmeticError;
    PyObject* _PyExc_LookupError;
    PyObject* _PyExc_AssertionError;
    PyObject* _PyExc_AttributeError;
    PyObject* _PyExc_EOFError;
    PyObject* _PyExc_FloatingPointError;
    PyObject* _PyExc_EnvironmentError;
    PyObject* _PyExc_IOError;
    PyObject* _PyExc_OSError;
    PyObject* _PyExc_SymbianError;
    PyObject* _PyExc_ImportError;
    PyObject* _PyExc_IndexError;
    PyObject* _PyExc_KeyError;
    PyObject* _PyExc_KeyboardInterrupt;
    PyObject* _PyExc_MemoryError;
    PyObject* _PyExc_NameError;
    PyObject* _PyExc_OverflowError;
    PyObject* _PyExc_RuntimeError;
    PyObject* _PyExc_NotImplementedError;
    PyObject* _PyExc_SyntaxError;
    PyObject* _PyExc_IndentationError;
    PyObject* _PyExc_TabError;
    PyObject* _PyExc_ReferenceError;
    PyObject* _PyExc_SystemError;
    PyObject* _PyExc_SystemExit;
    PyObject* _PyExc_TypeError;
    PyObject* _PyExc_UnboundLocalError;
    PyObject* _PyExc_UnicodeError;
    PyObject* _PyExc_ValueError;
    PyObject* _PyExc_ZeroDivisionError;
    PyObject* _PyExc_MemoryErrorInst;
    PyObject* _PyExc_Warning;
    PyObject* _PyExc_UserWarning;
    PyObject* _PyExc_DeprecationWarning;
    PyObject* _PyExc_SyntaxWarning;
    PyObject* _PyExc_OverflowWarning;
    PyObject* _PyExc_RuntimeWarning;
    t_exctable* exctable;
    struct _frozen *PyImport_FrozenModules;   // Python\frozen.c
    int import_encodings_called;              // Python\codecs.c
    PyObject *_PyCodec_SearchPath;
    PyObject *_PyCodec_SearchCache;
    char version[250];                        // Python\getversion.c
    long imp_pyc_magic;                       // Python\import.c
    PyObject *imp_extensions;
    struct filedescr * imp__PyImport_Filetab;
    PyThread_type_lock imp_import_lock;
    long imp_import_lock_thread; // initialized to -1 in python_globals.cpp
    int imp_import_lock_level;
    PyObject *namestr;
    PyObject *pathstr;
    PyObject *imp_silly_list;
    PyObject *imp_builtins_str;
    PyObject *imp_import_str;
    struct _inittab *imp_our_copy;
    struct filedescr imp_fd_frozen;
    struct filedescr imp_fd_builtin;
    struct filedescr imp_fd_package;
    struct filedescr imp_resfiledescr;
    struct filedescr imp_coderesfiledescr;
    struct _inittab *_PyImport_Inittab;
    char *_Py_PackageContext;                  // Python\modsupport.c
    PyThread_type_lock head_mutex;             // Python\pystate.c
    PyInterpreterState *interp_head;
    PyThreadState *_g_PyThreadState_Current;
    unaryfunc __PyThreadState_GetFrame;
    
    int initialized;    // Python\pythonrun.c
    char* programname;
    char *default_home;
    int _PyThread_Started;
#define NEXITFUNCS 32
    void (*exitfuncs[NEXITFUNCS])(void);
    int nexitfuncs;
    int _DebugFlag;
    int _VerboseFlag;
    int _InteractiveFlag;
    int _OptimizeFlag;
    int _NoSiteFlag;
    int _FrozenFlag;
    int _UnicodeFlag;
    int _IgnoreEnvironmentFlag;
    int _DivisionWarningFlag;
    int _QnewFlag;
    PyObject *whatstrings[4];   // Python\sysmodule.c
    PyObject *warnoptions;
    int thread_initialized;     // Python\thread.c
    int _PyOS_opterr;           // Python\getopt.c
    int _PyOS_optind;
    char *_PyOS_optarg;
    char *opt_ptr;

    PyObject *__bases__;        // Objects\abstract.c
    PyObject *__class__;
    PyObject *getattrstr;       // Objects\classobject.c
    PyObject *setattrstr;
    PyObject *delattrstr;
    PyObject *docstr;
    PyObject *modstr;
    PyObject *classobject_namestr;
    PyObject *initstr;
    PyObject *delstr;
    PyObject *reprstr;
    PyObject *strstr;
    PyObject *hashstr;
    PyObject *eqstr;
    PyObject *cmpstr;
    PyObject *getitemstr;
    PyObject *setitemstr;
    PyObject *delitemstr;
    PyObject *lenstr;
    PyObject *iterstr;
    PyObject *nextstr;
    PyObject *getslicestr;
    PyObject *setslicestr;
    PyObject *delslicestr;
    PyObject *__contains__;
    PyObject *coerce_obj;
    PyObject *cmp_obj;
    PyObject *nonzerostr;
    PyObject **name_op;
    PyObject *instance_neg_o;
    PyObject *instance_pos_o;
    PyObject *instance_abs_o;
    PyObject *instance_invert_o;
    PyObject *instance_int_o;
    PyObject *instance_long_o;
    PyObject *instance_float_o;
    PyObject *instance_oct_o;
    PyObject *instance_hex_o;
    PyMethodObject *classobj_free_list;
    PyObject *complexstr;          // Objects\complexobject.c
    PyObject *dummy;               // Objects\dictobject.c
    PyObject* xreadlines_function; // Objects\fileobject.c
    PyObject *not_yet_string;
    void *block_list;              // floatobject.c 
    void *free_list;
    void *FO_free_list;            // frameobject.c
    int numfree;
    PyObject *builtin_object;
    void *INTOBJ_block_list;       // intobject.c
    void *INTOBJ_free_list;
#ifndef NSMALLPOSINTS
#define NSMALLPOSINTS           100
#endif
#ifndef NSMALLNEGINTS
#define NSMALLNEGINTS           1
#endif
    PyIntObject *small_ints[NSMALLNEGINTS + NSMALLPOSINTS];
    PyIntObject _Py_ZeroStruct;
    PyIntObject _Py_TrueStruct;
    PyObject *indexerr; // Objects\listobject.c
    int ticker; // longobject.c
    PyCFunctionObject *METHODOBJ_free_list;     // methodobject.c
    int compare_nesting;              // Objects\object.c
    PyObject _Py_NotImplementedStruct;
    PyObject _Py_NoneStruct;
    int _PyTrash_delete_nesting;
    PyObject * _PyTrash_delete_later;
    PyObject *object_c_key;
    PyObject *unicodestr;
    PyObject _Py_EllipsisObject; // Objects\sliceobject.c
    // stringobject.c :
#if !defined(HAVE_LIMITS_H) && !defined(UCHAR_MAX)
#define UCHAR_MAX 255
#endif
    void *characters[UCHAR_MAX + 1];
#ifndef DONT_SHARE_SHORT_STRINGS
    void *nullstring;
#endif
    PyObject *interned; 
#ifndef MAXSAVESIZE
#define MAXSAVESIZE     20  /* Largest tuple to save on free list */
#endif
    void *free_tuples[MAXSAVESIZE];     // Objects\tupleobject.c
    int num_free_tuples[MAXSAVESIZE];
    slotdef* slotdefs;  // Objects\typeobject.c
    PyObject *bozo_obj;
    PyObject *finalizer_del_str;
    PyObject *mro_str;
    PyObject *copy_reg_str;
    PyObject *sq_length_len_str;
    PyObject *sq_item_getitem_string;
    PyObject *sq_ass_item_delitem_str;
    PyObject *sq_ass_item_setitem_str;
    PyObject *sq_ass_slice_delslice_str;
    PyObject *sq_ass_slice_setslice_str;
    PyObject *contains_str;
    PyObject *mp_ass_subs_delitem_str;
    PyObject *mp_ass_subs_setitem_str;
    PyObject *pow_str;
    PyObject *nb_nonzero_str;
    PyObject *nb_nonzero_len_str;
    PyObject *coerce_str;
    PyObject *half_compare_cmp_str;
    PyObject *repr_str;
    PyObject *str_str;
    PyObject *tp_hash_hash_str;
    PyObject *tp_hash_eq_str;
    PyObject *tp_hash_cmp_str;
    PyObject *call_str;
    PyObject *o_getattribute_str;
    PyObject *getattribute_str;
    PyObject *getattr_str;
    PyObject *tp_set_delattr_str;
    PyObject *tp_set_setattr_str;
    PyObject *op_str[6];
    PyObject *tp_iter_iter_str;
    PyObject *tp_iter_getitem_str;
    PyObject *next_str;
    PyObject *tp_descr_get_str;
    PyObject *tp_descr_set_del_str;
    PyObject *tp_descr_set_set_str;
    PyObject *init_str;
    int slotdefs_initialized;
    PyObject *slot_nb_negative_cache_str;
    PyObject *slot_nb_positive_cache_str;
    PyObject *slot_nb_absolute_cache_str;
    PyObject *slot_nb_invert_cache_str;
    PyObject *slot_nb_int_cache_str;
    PyObject *slot_nb_long_cache_str;
    PyObject *slot_nb_float_cache_str;
    PyObject *slot_nb_oct_cache_str;
    PyObject *slot_nb_hex_cache_str;
    PyObject *slot_sq_concat_cache_str;
    PyObject *slot_sq_repeat_cache_str;
    PyObject *slot_sq_inplace_concat_cache_str;
    PyObject *slot_sq_inplace_repeat_cache_str;
    PyObject *slot_mp_subscript_cache_str;
    PyObject *slot_nb_inplace_add_cache_str;
    PyObject *slot_nb_inplace_subtract_cache_str;
    PyObject *slot_nb_inplace_multiply_cache_str;
    PyObject *slot_nb_inplace_divide_cache_str;
    PyObject *slot_nb_inplace_remainder_cache_str;
    PyObject *slot_nb_inplace_lshift_cache_str;
    PyObject *slot_nb_inplace_rshift_cache_str;
    PyObject *slot_nb_inplace_and_cache_str;
    PyObject *slot_nb_inplace_xor_cache_str;
    PyObject *slot_nb_inplace_or_cache_str;
    PyObject *slot_nb_inplace_floor_divide_cache_str;
    PyObject *slot_nb_inplace_true_divide_cache_str;
    PyObject *slot_sq_slice_cache_str;
    PyObject *slot_nb_inplace_power_cache_str;
    PyObject *slot_nb_power_binary_cache_str;
    PyObject *slot_nb_power_binary_rcache_str;
    PyObject *slot_nb_add_cache_str;
    PyObject *slot_nb_add_rcache_str;
    PyObject *slot_nb_subtract_cache_str;
    PyObject *slot_nb_subtract_rcache_str;
    PyObject *slot_nb_multiply_cache_str;
    PyObject *slot_nb_multiply_rcache_str;
    PyObject *slot_nb_divide_cache_str;
    PyObject *slot_nb_divide_rcache_str;
    PyObject *slot_nb_remainder_cache_str;
    PyObject *slot_nb_remainder_rcache_str;
    PyObject *slot_nb_divmod_cache_str;
    PyObject *slot_nb_divmod_rcache_str;
    PyObject *slot_nb_lshift_cache_str;
    PyObject *slot_nb_lshift_rcache_str;
    PyObject *slot_nb_rshift_cache_str;
    PyObject *slot_nb_rshift_rcache_str;
    PyObject *slot_nb_and_cache_str;
    PyObject *slot_nb_and_rcache_str;
    PyObject *slot_nb_xor_cache_str;
    PyObject *slot_nb_xor_rcache_str;
    PyObject *slot_nb_or_cache_str;
    PyObject *slot_nb_or_rcache_str;
    PyObject *slot_nb_floor_divide_cache_str;
    PyObject *slot_nb_floor_divide_rcache_str;
    PyObject *slot_nb_true_divide_cache_str;
    PyObject *slot_nb_true_divide_rcache_str;
    int unicode_freelist_size;         // unicodeobject.c
    PyUnicodeObject *unicode_freelist;
    PyUnicodeObject *unicode_empty;
    PyUnicodeObject *unicode_latin1[256];
    char unicode_default_encoding[100];
    void *ucnhash_CAPI;
    PyWeakReference *WRO_free_list;    // weakrefobject.c
    char* argnames[1];
    SPy_type_objects tobj;
    PyObject* global_dict;
    void* lib_handles;                 // dynload_symbian.c
    PyObject* ThreadError;             // threadmodule.c
    char stdo_buf[0x200];              // e32module.cpp
    int stdo_buf_len;
    void* interpreter;                 // CSPyInterpreter.cpp
    PyTypeObject t_Canvas;
    PyTypeObject t_Icon;
#if SERIES60_VERSION>=30    
    PyTypeObject t_InfoPopup;
#endif /* SERIES60_VERSION */
    PyTypeObject t_Ao_timer;
#ifdef USE_GLOBAL_DATA_HACK
    int *globptr;
    int global_read_count;
    int thread_locals_read_count;
    int tls_mode;
#endif
#ifdef WITH_PYMALLOC
    void* usedpools;             // Objects\obmalloc.c
    void* freepools;
    unsigned int arenacnt;
    unsigned int watermark;
    void* arenalist;
    void* arenabase;
#endif
  } SPy_Python_globals;

#define MAXTHREADEXITFUNCS 32
  typedef struct {
    PyThreadState *thread_state;
    int n_exitfuncs;
    void (*exitfuncs[MAXTHREADEXITFUNCS])();
  } SPy_Python_thread_locals;
  
  typedef struct {
    SPy_Python_globals* globals;
    SPy_Python_thread_locals* thread_locals;
  } SPy_Tls;
  
#ifdef __ARMCC__
  DL_IMPORT(SPy_Python_globals*) SPy_get_globals()  __pure;
  DL_IMPORT(SPy_Python_thread_locals*) SPy_get_thread_locals();
#else  
  DL_IMPORT(SPy_Python_globals*) SPy_get_globals()  __attribute__((const));
  DL_IMPORT(SPy_Python_thread_locals*) SPy_get_thread_locals();
#endif  

#define PYTHON_GLOBALS (SPy_get_globals())
#define PYTHON_TLS (SPy_get_thread_locals())

#ifdef __cplusplus
}
#endif

extern int SPy_globals_initialize(void*);
extern void SPy_globals_finalize();

extern int SPy_tls_initialize(SPy_Python_globals*);
extern void SPy_tls_finalize(int);

#endif /* __PYTHON_GLOBALS_H */
