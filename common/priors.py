# PRIOR PROBABILITY DISTRIBUTIONS

# This file contains a series of functions which define prior probability distributions
# for the input parameters. They return the functions which scale a number selected linearly
# from the range 0-1 into a sample selected from the desired distribution.

from math import log, exp, sqrt, floor
from scipy.special import erf, erfinv
import pymc

#--------------------------
# FULL PRIORS from lists of partial priors
#--------------------------
# These take as input some combination of parameters and functions which scale those parameters
# from unit intervals to the desired range in such a way as to produce the desired prior.
# They generate functions which take the parameter vector dictionary 'cubedict' and apply
# those parameter scalings to it.
# The function which do the actual scaling are defined after these, in the 'partial priors' section


#General prior for independent parameters (i.e. so that the full prior over the parameter space
#is just a product of 1-D priors for each individual parameter)
#The 1-D prior function for each parameter is specified as input to this function constructor
#through a list of tuples of the form (parameter, prior function) in the list priors1D
def genindepprior(priors1D):
    #print 'priors1D:',priors1D
    def productofpriors(cubedict):
        for param, priorfunc in priors1D:
            #print 'param, priorfunc, cubedict[param]:',param, priorfunc, cubedict[param]
            cubedict[param] = priorfunc(cubedict[param])  #Take the input parameter vector (in cubedict) and apply the appropriate prior scaling function to it.
        return cubedict               #return the dictionary, but now it contains the scaled values instead of the (0,1) values
    return productofpriors

#GMSB linear (but not flat) prior. Scales Lambda up linearly, then scales Mmess up linearly to an interval dependent on Lambda.
#This distribution favours low Mmess and Lambda since the low Lambda intervals are smaller, concentrating more points in
#that region. This is then multiplied by the 1D priors of the other parameters as in the general independent priors case.
def GMSBcombinedprior(priors2D,priors1D):
    def productofpriors(cubedict):
        for params, priorfunc in priors2D: #extracts the pair of tuples from priors 2D
            #we calculate two parameters at once and assign a pair of values to the cube simultaneously
            #the priorfunc is assumed to be the 'triangleprior' output of GMSBlinear here, but I will presumably design 
            #other priors to work the same way in the future.
            cubedict[params[0]] , cubedict[params[1]] = priorfunc(cubedict[params[0]],cubedict[params[1]])
        for param, priorfunc in priors1D: #now we do the scaling of the 1D priors
            cubedict[param] = priorfunc(cubedict[param])  #Take the input parameter vector (in cubedict) and apply the appropriate prior scaling function to it.
        return cubedict               #return the dictionary, but now it contains the scaled values instead of the (0,1) values
    return productofpriors
    
#-----------------------------------
# PARTIAL PRIORS - generating functions
#-----------------------------------
# These functions take input which specifies the range desired for a parameter (or set of parameters),
# then return a function which scales that parameter (or set of parameters) to that range such that
# the input parameter, drawn randomly (uniformly) from the unit interval, is mapped to an output random variable
# with the desired probability distribution. In the simple linear case this just means the output parameter
# is drawn uniformly from some larger interval.


def GMSBlinear((Lmin,Lmax),(Kmin,Kmax)):
    #Lmin and Lmax are the range of Lambda, i.e. 
    #   Lmin <= Lambda <= Lmax 
    #Kmin and Kmax are the scaling factors for the range of Mmess, i.e.
    #   Kmin*Lambda <= Mmess <= Kmax*Lambda
    def triangleprior(LambdaIN,MmessIN):
         L = LambdaIN*(Lmax-Lmin)+Lmin
         M = MmessIN*(Kmax*L-Kmin*L)+Kmin*L
         return L,M #L and M are the correctly scaled Lambda and Mmess values
    return triangleprior #returns the function which scales a pair of (0,1) parameters up to the correct pair of values.

#Simple linear prior. Takes a value sampled uniformly from the distribution (0,1)
#and maps it to a value sampled uniformly from the distribution (lower,upper)
def linear(lower,upper):
    def linprior(x):
        y = x*(upper-lower)+lower
        return y
    return linprior #returns the function which scales the (0,1) parameter up to the correct distribution


#Simple logathmic prior. Takes a value sampled uniformly from the distribution (0,1)
#and maps it to a value sampled logarithmically from the distribution (lower,upper)  
#i.e. from the distribution Pr(log(x)) =           
def logprior(lower,upper,base=10):  #input a different base if desired
    def logpr(x):
        scaledx = (log(upper,base)-log(lower,base))*x + log(lower,base)    #scales the uniform distribution to the logarithm of the desired range (so the prior is flat in this range)
        y = base**scaledx
        return y
    return logpr #returns the function which scales the (0,1) parameter up to the correct distribution
    
#Simple gaussian prior. Takes a value sampled uniformly from the distribution (0,1)
#and maps it to a value sampled from the normal distribution with (mean,sigma)
#(0 maps to -inf, 0.5 maps to mean, 1 maps to +inf)
def gaussian(mean,sigma):
    def gausspr(x):
        y = mean + sqrt(2)*sigma*erfinv(2*x-1)
        return y
    return gausspr
    
#Discrete prior. Takes the unit interval and maps it into equal bins.
#I assume multinest will work fine with this, a little unsure though...
def discrete(binlist):
    NumBins = len(binlist)
    def discretepr(x):
        bin = int(floor(x*NumBins)) #turns x into a bin index from 0 to NumBins-1
        y = binlist[bin]    #gets the value of this bin from the list
        return y
    return discretepr
