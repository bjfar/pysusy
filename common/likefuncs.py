# some custom likelihood functions
from scipy import log, sqrt, exp, pi
from scipy.special import erf
import pymc


#All likelihood functions must take 3 arguments; the point to calculate,
#the mean (or limit) and the sigma (or similar). Even
#if these are not relevant (say for step functions) they must be included
#and then just ignored.
#Note, now that we hve moved to PySUSY3, this restriction is lifted! Use
#whatever format you like! These functions are now directly called by
#the user-defined likelihood calculator function.

def logstepupper(x,limit):
   if x==None: return -1e300
   return 0 if x<limit else -1e300

def logsteplower(x,limit):
   if x==None: return -1e300
   return 0 if x>limit else -1e300

def lognormallike(x,mean,sigma):
   if x==None: return -1e300
   tau = 1./sigma**2
   return pymc.normal_like(x,mean,tau)#-pymc.normal_like(mean,mean,tau) #removed this scaling factor, is irrelevant

def logerfupper(x,limit,sigma):
   if x==None: return -1e300
   return log((erf((limit-x)/sqrt(2*sigma**2))+1.00000000000001)/2) # TODO: figure out if we can replace the 1.01 here

def logerflower(x,limit,sigma):
   if x==None: return -1e300
   return log((erf((x-limit)/sqrt(2*sigma**2))+1.00000000000001)/2)

def halfnormalupper(x,limit,sigma):
   if x==None: return -1e300
   if x<=limit: return log(1./sqrt(2*pi*sigma**2)) #this is the value of the max of the normal distribution. Note likelihood functions are unscaled here.
   tau = 1./sigma**2
   return pymc.normal_like(x,limit,tau)#-pymc.normal_like(mean,mean,tau) #removed this scaling factor, is irrelevant

def halfnormallower(x,limit,sigma):
   if x==None: return -1e300
   if x>=limit: return log(1./sqrt(2*pi*sigma**2)) #this is the value of the max of the normal distribution. Note likelihood functions are unscaled here.
   tau = 1./sigma**2
   return pymc.normal_like(x,limit,tau)#-pymc.normal_like(mean,mean,tau) #removed this scaling factor, is irrelevant

# Double gaussian! Using to model seperate values for upper and lower
# uncertainties. Be careful using this; if some source gives seperate upper 
# and lower uncertainties for a quantity it may signal a rather non-gaussian
# underlying likelihood, which this function may approximate poorly. The bigger
# the difference b/w the upper and lower sigmas, the worse this model likelihood
# will be, generally speaking.
def logdoublenormal(x,mean,sigmaP,sigmaM):
    #mean is measured value
    #x is computed theory value
    #sigmaP and sigmaM are distances from mean to upper and lower 1 sigma (68%)
    #confidence limits.
    if x==None: return -1e300
    if x>=mean:
        tauP = 1./sigmaP**2
        #need to remove the normalisation factor so we get the same normalisation
        #for each half of the likelihood.
        loglike = pymc.normal_like(x,mean,tauP) - pymc.normal_like(mean,mean,tauP)
    if x<mean:
        tauM = 1./sigmaM**2
        loglike = pymc.normal_like(x,mean,tauM) - pymc.normal_like(mean,mean,tauM)
    return loglike
    
def variablemean(likefunc,meanfunc,observables,sigmafunc=0,extra=[]): #observables should be a tuple containing the 'observables' objects which contain values needed to compute the variable mean
   """Master likelihood function generator for variable likelihood functions
   This function is used to create likelihood functions which vary from point
   to point in the parameter space.
   
   Keyword Args:
   likefunc - The base likelihood function to be used at each point
   meanfunc - The function which returns the mean (or limit) for the given point
   observables - A list containing the 'Observables' objects needed by meanfunc
   sigmafunc - The sigma parameter for the likelihood function (NOTE, in future may want to make this variable too, i.e. a 'sigmafunc'
   extra - A list containing any extra information needed by meanfunc:
        the arguments are fed to meanfunc in the order 'observables, extra',
        in the order they appear in the tuples, so make sure these match correctly
        
   Note, 'observables' have their values extracted before being passed to meanfunc,
   while 'extra' objects are just passed straight in as-is.
   """
   def lk(x,mean,sigma):    #mean and sigma are ignored, just needed here for compatibility with way pysusy calls likelihood functions
      #print [observable.slhafile.name for observable in observables]
      #print [observable.block for observable in observables]
      #print [observable.index for observable in observables]
      #print [observable.results() for observable in observables]
      #print [observable for observable in observables]
      #print "observable.value: ",[observable.value for observable in observables]
      args = [observable.results() for observable in observables] + extra   #extract observables values and add these and extra objects to argument list for meanfunc
      return likefunc(x,meanfunc(*args),sigmafunc) # is observable.value safe to use? or should it be .results()? bjf> .value should be ok, all data is extracted from SLHA files by now. .results just gets the value from the SLHA object then returns .value. Actually there should be no harm in using .results...
      #ok decided on .results() because the observable in question may not have been extracted from the new SLHA file yet.
   return lk

def generallikefunc(likefunc,observables=[],extra=[]): #observables should be a tuple containing the 'observables' objects which contain values needed to compute the likelihood value of each point
   """Master likelihood function generator for GENERAL likelihood functions
   This function is used to create likelihood functions which vary from point
   to point in the parameter space.
   
   Keyword Args:
   likefunc - A function which takes input in the form (x,*args) where args are
      defined as below. x is the value of the Observable (whose likelihood function this
      is) at the current model point
   observables - A list containing the 'Observables' objects whose values are needed by likefunc
   extra - A list containing any extra information needed by likefunc:
        the arguments are fed to likefunc in the order 'observables, extra',
        in the order they appear in the input tuples, so make sure these match correctly
        
   Note, 'observables' have their values extracted before being passed to likefunc,
   while 'extra' objects are just passed straight in as-is.
   """
   def lk(x,mean,sigma):    #mean and sigma are ignored, just needed here for compatibility with way pysusy calls likelihood functions
      #print likefunc, x, mean, sigma
      #print [observable.slhafile.name for observable in observables]
      #print [observable.block for observable in observables]
      #print [observable.index for observable in observables]
      #print [observable.results() for observable in observables]
      #print [observable for observable in observables]
      #print "observable.value: ",[observable.value for observable in observables]
      args = [observable.results() for observable in observables] + extra   #extract observables values and add these and extra objects to argument list for meanfunc
      #print 'hello', likefunc(x,*args)
      #print 'hello 2'
      return likefunc(x,*args) # is observable.value safe to use? or should it be .results()? bjf> .value should be ok, all data is extracted from SLHA files by now. .results just gets the value from the SLHA object then returns .value. Actually there should be no harm in using .results...
      #ok decided on .results() because the observable in question may not have been extracted from the new SLHA file yet.
   return lk
   
def logoneonx(x,lower,upper):
   if x==None: return -1e300
   if x<lower or x>upper: return -1e300
   else: return log(abs(1.0/x))

nolike = lambda x,mean,sigma: 0.0

