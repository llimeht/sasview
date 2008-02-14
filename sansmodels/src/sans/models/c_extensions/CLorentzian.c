/** CLorentzian
 *
 * C extension 
 *
 * WARNING: THIS FILE WAS GENERATED BY WRAPPERGENERATOR.PY
 *          DO NOT MODIFY THIS FILE, MODIFY lorentzian.h
 *          AND RE-RUN THE GENERATOR SCRIPT
 *
 * @author   M.Doucet / UTK
 */
 
#include <Python.h>
#include "structmember.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#include "lorentzian.h"

/// Error object for raised exceptions
static PyObject * CLorentzianError = NULL;


// Class definition
typedef struct {
    PyObject_HEAD
    /// Parameters
    PyObject * params;
    /// Log for unit testing
    PyObject * log;
    /// Model parameters
	LorentzianParameters model_pars;
} CLorentzian;


static void
CLorentzian_dealloc(CLorentzian* self)
{
    self->ob_type->tp_free((PyObject*)self);
    

}

static PyObject *
CLorentzian_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    CLorentzian *self;
    
    self = (CLorentzian *)type->tp_alloc(type, 0);
   
    return (PyObject *)self;
}

static int
CLorentzian_init(CLorentzian *self, PyObject *args, PyObject *kwds)
{
    if (self != NULL) {
    	
    	// Create parameters
        self->params = PyDict_New();
        
        // Initialize parameter dictionary
        PyDict_SetItemString(self->params,"scale",Py_BuildValue("d",1.000000));
        PyDict_SetItemString(self->params,"center",Py_BuildValue("d",0.000000));
        PyDict_SetItemString(self->params,"gamma",Py_BuildValue("d",1.000000));

         
        // Create empty log
        self->log = PyDict_New();
        
        

    }
    return 0;
}

static PyMemberDef CLorentzian_members[] = {
    {"params", T_OBJECT, offsetof(CLorentzian, params), 0,
     "Parameters"},
    {"log", T_OBJECT, offsetof(CLorentzian, log), 0,
     "Log"},
    {NULL}  /* Sentinel */
};

/** Read double from PyObject
    @param p PyObject
    @return double
*/
double CLorentzian_readDouble(PyObject *p) {
    if (PyFloat_Check(p)==1) {
        return (double)(((PyFloatObject *)(p))->ob_fval);
    } else if (PyInt_Check(p)==1) {
        return (double)(((PyIntObject *)(p))->ob_ival);
    } else if (PyLong_Check(p)==1) {
        return (double)PyLong_AsLong(p);
    } else {
        return 0.0;
    }
}


/**
 * Function to call to evaluate model
 * @param args: input q or [q,phi]
 * @return: function value
 */
static PyObject * run(CLorentzian *self, PyObject *args) {
	double q_value, phi_value;
	PyObject* pars;
	int npars;
	
	// Get parameters
	
	// Reader parameter dictionary
    self->model_pars.scale = PyFloat_AsDouble( PyDict_GetItemString(self->params, "scale") );
    self->model_pars.center = PyFloat_AsDouble( PyDict_GetItemString(self->params, "center") );
    self->model_pars.gamma = PyFloat_AsDouble( PyDict_GetItemString(self->params, "gamma") );

	
	// Get input and determine whether we have to supply a 1D or 2D return value.
	if ( !PyArg_ParseTuple(args,"O",&pars) ) {
	    PyErr_SetString(CLorentzianError, 
	    	"CLorentzian.run expects a q value.");
		return NULL;
	}
	  
	// Check params
	if( PyList_Check(pars)==1) {
		
		// Length of list should be 2 for I(q,phi)
	    npars = PyList_GET_SIZE(pars); 
	    if(npars!=2) {
	    	PyErr_SetString(CLorentzianError, 
	    		"CLorentzian.run expects a double or a list of dimension 2.");
	    	return NULL;
	    }
	    // We have a vector q, get the q and phi values at which
	    // to evaluate I(q,phi)
	    q_value = CLorentzian_readDouble(PyList_GET_ITEM(pars,0));
	    phi_value = CLorentzian_readDouble(PyList_GET_ITEM(pars,1));
	    // Skip zero
	    if (q_value==0) {
	    	return Py_BuildValue("d",0.0);
	    }
		return Py_BuildValue("d",lorentzian_analytical_2D(&(self->model_pars),q_value,phi_value));

	} else {

		// We have a scalar q, we will evaluate I(q)
		q_value = CLorentzian_readDouble(pars);		
		
		return Py_BuildValue("d",lorentzian_analytical_1D(&(self->model_pars),q_value));
	}	
}

/**
 * Function to call to evaluate model in cartesian coordinates
 * @param args: input q or [qx, qy]]
 * @return: function value
 */
static PyObject * runXY(CLorentzian *self, PyObject *args) {
	double qx_value, qy_value;
	PyObject* pars;
	int npars;
	
	// Get parameters
	
	// Reader parameter dictionary
    self->model_pars.scale = PyFloat_AsDouble( PyDict_GetItemString(self->params, "scale") );
    self->model_pars.center = PyFloat_AsDouble( PyDict_GetItemString(self->params, "center") );
    self->model_pars.gamma = PyFloat_AsDouble( PyDict_GetItemString(self->params, "gamma") );

	
	// Get input and determine whether we have to supply a 1D or 2D return value.
	if ( !PyArg_ParseTuple(args,"O",&pars) ) {
	    PyErr_SetString(CLorentzianError, 
	    	"CLorentzian.run expects a q value.");
		return NULL;
	}
	  
	// Check params
	if( PyList_Check(pars)==1) {
		
		// Length of list should be 2 for I(qx, qy))
	    npars = PyList_GET_SIZE(pars); 
	    if(npars!=2) {
	    	PyErr_SetString(CLorentzianError, 
	    		"CLorentzian.run expects a double or a list of dimension 2.");
	    	return NULL;
	    }
	    // We have a vector q, get the qx and qy values at which
	    // to evaluate I(qx,qy)
	    qx_value = CLorentzian_readDouble(PyList_GET_ITEM(pars,0));
	    qy_value = CLorentzian_readDouble(PyList_GET_ITEM(pars,1));
		return Py_BuildValue("d",lorentzian_analytical_2DXY(&(self->model_pars),qx_value,qy_value));

	} else {

		// We have a scalar q, we will evaluate I(q)
		qx_value = CLorentzian_readDouble(pars);		
		
		return Py_BuildValue("d",lorentzian_analytical_1D(&(self->model_pars),qx_value));
	}	
}

static PyObject * reset(CLorentzian *self, PyObject *args) {
    

    return Py_BuildValue("d",0.0);
}


static PyMethodDef CLorentzian_methods[] = {
    {"run",      (PyCFunction)run     , METH_VARARGS,
      "Evaluate the model at a given Q or Q, phi"},
    {"runXY",      (PyCFunction)runXY     , METH_VARARGS,
      "Evaluate the model at a given Q or Qx, Qy"},
    {"reset",    (PyCFunction)reset   , METH_VARARGS,
      "Reset pair correlation"},
    //{"numerical_1D",      (PyCFunction)numerical_1D     , METH_VARARGS,
    //  "Evaluate the 1D model at a given Q"},
   {NULL}
};

static PyTypeObject CLorentzianType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "CLorentzian",             /*tp_name*/
    sizeof(CLorentzian),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)CLorentzian_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "CLorentzian objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    CLorentzian_methods,             /* tp_methods */
    CLorentzian_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)CLorentzian_init,      /* tp_init */
    0,                         /* tp_alloc */
    CLorentzian_new,                 /* tp_new */
};


static PyMethodDef module_methods[] = {
    {NULL} 
};

/**
 * Function used to add the model class to a module
 * @param module: module to add the class to
 */ 
void addCLorentzian(PyObject *module) {
	PyObject *d;
	
    if (PyType_Ready(&CLorentzianType) < 0)
        return;

    Py_INCREF(&CLorentzianType);
    PyModule_AddObject(module, "CLorentzian", (PyObject *)&CLorentzianType);
    
    d = PyModule_GetDict(module);
    CLorentzianError = PyErr_NewException("CLorentzian.error", NULL, NULL);
    PyDict_SetItemString(d, "CLorentzianError", CLorentzianError);
}

