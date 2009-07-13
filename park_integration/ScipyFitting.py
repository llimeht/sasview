"""
    @organization: ScipyFitting module contains FitArrange , ScipyFit,
    Parameter classes.All listed classes work together to perform a 
    simple fit with scipy optimizer.
"""

import numpy 
from scipy import optimize

from AbstractFitEngine import FitEngine, sansAssembly,FitAbort

class fitresult:
    """
        Storing fit result
    """
    calls     = None
    fitness   = None
    chisqr    = None
    pvec      = None
    cov       = None
    info      = None
    mesg      = None
    success   = None
    stderr    = None
    parameters= None
    

class ScipyFit(FitEngine):
    """ 
        ScipyFit performs the Fit.This class can be used as follow:
        #Do the fit SCIPY
        create an engine: engine = ScipyFit()
        Use data must be of type plottable
        Use a sans model
        
        Add data with a dictionnary of FitArrangeDict where Uid is a key and data
        is saved in FitArrange object.
        engine.set_data(data,Uid)
        
        Set model parameter "M1"= model.name add {model.parameter.name:value}.
        @note: Set_param() if used must always preceded set_model()
             for the fit to be performed.In case of Scipyfit set_param is called in
             fit () automatically.
        engine.set_param( model,"M1", {'A':2,'B':4})
        
        Add model with a dictionnary of FitArrangeDict{} where Uid is a key and model
        is save in FitArrange object.
        engine.set_model(model,Uid)
        
        engine.fit return chisqr,[model.parameter 1,2,..],[[err1....][..err2...]]
        chisqr1, out1, cov1=engine.fit({model.parameter.name:value},qmin,qmax)
    """
    def __init__(self):
        """
            Creates a dictionary (self.fitArrangeDict={})of FitArrange elements
            with Uid as keys
        """
        self.fitArrangeDict={}
        self.paramList=[]
    #def fit(self, *args, **kw):
    #    return profile(self._fit, *args, **kw)

    def fit(self ,handler=None,curr_thread= None):
       
        fitproblem=[]
        for id ,fproblem in self.fitArrangeDict.iteritems():
            if fproblem.get_to_fit()==1:
                fitproblem.append(fproblem)
        if len(fitproblem)>1 : 
            raise RuntimeError, "Scipy can't fit more than a single fit problem at a time."
            return
        elif len(fitproblem)==0 : 
            raise RuntimeError, "No Assembly scheduled for Scipy fitting."
            return
    
        listdata=[]
        model = fitproblem[0].get_model()
        listdata = fitproblem[0].get_data()
        # Concatenate dList set (contains one or more data)before fitting
        #data=self._concatenateData( listdata)
        data=listdata
        self.curr_thread= curr_thread
        
        try:
            functor= SansAssembly(self.paramList,model,data, curr_thread= self.curr_thread)
            out, cov_x, info, mesg, success = optimize.leastsq(functor,model.getParams(self.paramList), full_output=1, warning=True)
            
            chisqr = functor.chisq(out)
            
            if cov_x is not None and numpy.isfinite(cov_x).all():
                stderr = numpy.sqrt(numpy.diag(cov_x))
            else:
                stderr=None
            if not (numpy.isnan(out).any()) or ( cov_x !=None) :
                    result = fitresult()
                    result.fitness = chisqr
                    result.stderr  = stderr
                    result.pvec = out
                    result.success = success
                    return result
            else:  
                raise ValueError, "SVD did not converge"+str(success)
        except FitAbort:
            ## fit engine is stop
            return None
        
        except:
            raise
       
def profile(fn, *args, **kw):
    import cProfile, pstats, os
    global call_result
    def call():
        global call_result
        call_result = fn(*args, **kw)
    cProfile.runctx('call()', dict(call=call), {}, 'profile.out')
    stats = pstats.Stats('profile.out')
    #stats.sort_stats('time')
    stats.sort_stats('calls')
    stats.print_stats()
    os.unlink('profile.out')
    return call_result

      