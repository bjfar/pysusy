#Global MSSM likelihood calculator for PySUSY3
#Ben Farmer, 4 Jun 2012

#note: scipt causing strange library searches in loops (looking for 'random' module)
import numpy as np
from numpy import pi
import scipy.interpolate as interp
from scipy import exp, log, sqrt, log10
from scipy import absolute as abs
from scipy.special import erfinv
from scipy.stats import chi2
import common.likefuncs as LFs
import ConfigParser                                                     #standard module for parsing config files

#==========================================================
# Custom likelihood functions and function generators (larger than 1 liners)
#==========================================================
def squarklikefunc(smassIN,nmassIN):    #common likelihood function for remaining squarks
        smass = np.abs(smassIN)
        nmass = np.abs(nmassIN)
        return LFs.logsteplower(x=smass, limit=97 if smass-nmass>10 else 44)

def higgslimitfunc(alpha_IN,tanbeta_IN,limitcurve_IN):   
    """This is the function which will be called at each 
    calculation step to determine the appropriate LEP Higgs mass limit
    Keyword Args:
    alpha   -   alpha higgs scalar mixing angle
    tanbeta -   tan(higgs VEV ratio)
    limitcurve - a function which returns the approximated Higgs mass 95% confidence limit for a given coupling g (ratio of MSSM to SM g_ZZh couplings)
    """
    #print "alpha_IN=",alpha_IN
    #print "tanbeta_IN=",tanbeta_IN
    if alpha_IN==None or tanbeta_IN==None:  #if any errors occur in the external codes along the way we won't have valid values for these, so we skip the calculation
        return None
        
    #print 'tanbeta = ', tanbeta_IN
    beta = np.arctan(tanbeta_IN)  #ratio of Higgs VEVs

    #Calculate ratio of couplings to feed into mass limit curve
    Xi_HZZ = (np.sin(beta-alpha_IN))**2    # = (g_HZZ_MSSM/g_HZZ_SM)**2
    
    #Feed Xi into the limit curve to obtain the appropriate mass limit for this coupling strength
    m_H_lowlim = limitcurve_IN(Xi_HZZ)
    return m_H_lowlim

def xenon100likefunc(obslimitcurve,exp1sigmacurve,minmX,maxmX):    
   """
   Keyword Args:
   obslimitcurve - a function which returns the approximated Xenon WIMP-nucleon
   SI cross section observed 90% confidence limit for a given mWIMP
   exp1sigmacurve - a function which returns the approximated Xenon WIMP-nucleon
   SI cross section expected+1sigma 90% confidence limit for a given mWIMP
   minmX - (log10 of) minimum mWIMP mass for which limit curve data exists (logs because this is read straight from
   Xenon100 curve data)
   maxmX - (log10 of) maximum " " " 
   """
   #definitions:
   
   Dchi2obs=4.61 #delta chi squared value on observed 90% C.L. (from DOF=2 chi squared 90% quantile)
   Dchi2exp1sigma=1.282 #delta chi squared value on expected+1sigma 90% C.L. (see project notebook #3, pg 40-44)    
   
   def Ytransf(x):
      #This is just a transformation of x=Delta chi^2 values which is needed
      #for determining the xenon likelihood function
      return erfinv(2*exp(-x/2)-1)

   def xenonlikefunc(x,mX,fracxsigmaT): #flat space erf fit version.
      #x=WIMP-nucleon SI cross section
      #mX=WIMP mass
      #fracxsigmaT=fractional uncertainty in cross section due to theory
      #For given WIMP mass, need to work out appropriate limit and sigma
      #based on obslimitcurve and exp1sigmacurve:
      #print x
      # micromegas output gives cross section in pb, while Xenon limit is
      #stated in cm^2. Must convert to cm^2 to apply limit.
      #print x
      x=x*(10**-36) #(1 pb = 10^-36 cm^2)
      xsigmaT=x*fracxsigmaT   #compute absolute uncertainty in sigmaT
      
      if log10(mX)<minmX or log10(mX)>maxmX:
         return 0  #do not apply constraints outside of mass range reported by xenon, don't really know what happens there.
      else:
         if log10(mX)<=1.3: #below this the curves basically merge and the cutoff is sharp, although my curve digitizer linearly extrapolated the exp+1sigma curve (ignore this section of curve data)
            limit = 10**obslimitcurve.__call__(log10(mX)) #returns the x value at the observed xenon limit for this WIMP mass
            sigma = 0   #reduces the erf to a step function
         else:  #we can approximate the width of the erf in this region (IN FLAT SPACE THIS TIME)
            Y1 = Ytransf(Dchi2obs)
            X1 = 10**obslimitcurve.__call__(log10(mX)) #returns the x value at the observed xenon limit for this WIMP mass
            Y2 = Ytransf(Dchi2exp1sigma)
            X2 = 10**exp1sigmacurve.__call__(log10(mX)) #returns the x value at the expected+1sigma xenon limit for this WIMP mass
            limit=(X1*Y2-X2*Y1)/(Y2-Y1)  #determine the mean of the matching erf likelihood function
            sigma=(1/sqrt(2))*abs((X2-X1)/(Y2-Y1))  #determine the width of " " " 
         #compute theory error contribution
         #print x, log10(x), log10(x)+36, 10**(log10(x)+36), sigma, xsigmaT
         wtheory = LFs.logerfupper(x,limit,sqrt(sigma**2+xsigmaT**2)) #erf fit done in log space
         bare = LFs.logerfupper(x,limit,sigma)
         #print wtheory
         #return wtheory#, bare #erf fit done in log space
         return bare #erf fit done in log space
         
   return xenonlikefunc

#CMS+LHCb Bs->mu+mu- limits (CLs curve, estimated as maximimum likelihood ratio) 
def CMSLHCbBsmumulikefunc(CLscurve,minX,maxX):    
   """
   Keyword Args:
   CLscurve - function which returns the CMS+LHCb CLs value for the above
      theory prediction.
   minX - minimum extent of CLs curve in Bsmumu
   maxX - maximum extent of CLs curve in Bsmumu 
   """
   #definitions:
   
   def CLs2chi2(CLs):
      """This function takes a CLs value and estimates the corresponding
      Delta(Chi^2) value. The justification for this is slightly complex
      (see mathematica notebook CLsVSchi2.nb). We essentially assume the
      CLs values are 1-CL where CL values are the confidence limits
      obtained by the maximum likelihood ratio method, where the test
      statistic is assumed to follow a chi-squared (DOF=1) distribution.
      """
      return chi2.isf(CLs,1) #inverse survival function of the chi^2(DOF=1) distribution.
   
   def Bsmumulikefunc(Bsmumu):
      """Computes the log-likelihood value for a given BR(Bs->mumu) value.
      Bsmumu - Actual value of branching ratio, NOT the observable object
      """
      Bsmumu=(10**9)*Bsmumu #curve defined in [10^-9] units, must convert theory value to match 
      #Deal with theory values outside the range covered by the CLs curve.
      #Allow everything below data range, set higher values to same value as maximum data point
      if Bsmumu<minX:
         return 0   #i.e. no limit applied
      if Bsmumu>maxX:
         Bsmumu=maxX
      Dchi2 = CLs2chi2(CLscurve.__call__(Bsmumu)) #convert CLs to estimate of delta chi^2
      return -0.5*Dchi2 #return the Log-Likelihood value
         
   #return likelihood function
   return Bsmumulikefunc
   
# NOTE: NOT USING THIS ANYMORE! NOT RIGHT NOW ANYWAY, MAYBE LATER.
# delta(g-2)mu likelihood function
# This one is pretty simple. There are several "experimental" values for
# this quantity we want to use, based on different methods of computing
# the Standard Model prediction. Being Bayesians, we wish to marginalise
# over the method of prediction, which obtains for us a weighted average
# of the two likelihood values. See notesbook 3 pg 86-87.
# Alternatively we can use a weighted average of the predictions. Both
# are coded here and can be switched between by uncommenting the
# desired option

def deltaamulikefunc():    
   """
   Keyword Args:
   """
   #definitions:
   
   #in units of 1e-10:
   #Experimentally measured a_mu value:
   amuexp=11659209
   damuexp=5.31
   #PDG 2010, 2011 partial update for 2012 edition (lepton properties summary)
   
   #Method 1: 1106.1315 (PQCD tricks) 
   PM1=0.25
   amuM1=11659117.37
   damuM1=5.31
   
   #Method 2: 1106.0427 (e+e- -> hadrons data)
   PM2=0.25
   amuM2=11659210.6
   damuM2=9.8
   
   #Method 3: 1010.4180v1 (e+e- -> hadrons data)
   PM3=0.25
   amuM3=11659180.2
   damuM3=4.9    
   
   #Method 4: 1010.4180v1 (tau decay data)
   PM4=0.25
   amuM4=11659189.4
   damuM4=5.4    
   
   #lists
   PM=[PM1,PM2,PM3,PM4]
   amu=[amuM1,amuM2,amuM3,amuM4]
   damu=[damuM1,damuM2,damuM3,damuM4]
   deltaamu=map(lambda x: (amuexp-x)*1e-10, amu)   #take difference and convert to right units, for comparison with MSSM value
   
   def weightavgLF(x):
      #see mathematica notebook "g-2_comparison.nb" for discussion of the two methods shown here.
      #L=0  #for weighted sum
      LogL=0   #for weighted average
      for PMi,deltaamui,damui in zip(PM,deltaamu,damu):
         #Add the pieces of the likelihood function together
         #L+=exp(LFs.lognormallike(x,deltaamui,sqrt(damuexp**2+damui**2)*1e-10))  #This assumes no uncertainty in the computed MSSM value, or that the SM uncertainty dominates.      
         #LogL=log(L)
         #Multiply seperate likelihood contributions together (don't need PMi contributions in this case)
         LogL+=LFs.lognormallike(x,deltaamui,sqrt(damuexp**2+damui**2)*1e-10)  #This assumes no uncertainty in the computed MSSM value, or that the SM uncertainty dominates.      
      return LogL #return the Log-Likelihood value
         
   #Construct likelihood function object
   return LFs.generallikefunc(likefunc=weightavgLF)

# lightest higgs mass/cross-section likelihood function from LHC Higgs search results
# This is the general likelihood function used for each production/decay channel cross-section
# which we constrain. It is very simple because maps of the each likelihood function have
# been pre-created. We just look them up from interpolating functions here.
def LHChiggslikefunc(chanLF,(mHmin,mHmax,xsmin,xsmax)):    
    """
    Keyword Args:
    mHiggs - the lightest CP-even Higgs mass
    chanLF - 2d interpolating function object of likelihood function for this channel (derived from the delta chi^2 map 
        created by higgs_combiner.py), (these should already be stored in the dictionary LHChiggsLF (which was
        created during initialisation of this module), i.e. "LHChiggsLF['ATLAShyyBF']" should be supplied as 
        an argument to retrieve the likelihood function for the h-->aa channel)
    mHmin - Minimum higgs mass covered by the interpolating function 
    mHmax - Maximum " " 
    xsmin - Minimum higgs production cross section*BR for this channel covered by the interpolating function 
        (scaled against SM value, i.e. xs = xs_SUSY/xs_SM)
    xsmax - Maximum " " 
    """
    #definitions:
    
    def LHChiggschanLF(x,mH):
        """
        x = xs_SUSY/xs_SM (ratio of cross sections)
        mH = mHiggs - the lightest CP-even Higgs mass
        """
        if mH>mHmax:
            #do not apply constraints outside the Higgs mass range covered by
            #data (the LEP limits will take care of the lower domain and we
            #should not (in the MSSM) find any predictions above mHmax). The
            #transition will be a little ugly but I think it is unavoidable.
            return 0    #remember this is the log-likelihood so 0 does not apply a constraint 
        if mH<mHmin:
            #extrapolate the lower mH bound of the likelihood. These values
            #will be quickly killed by the LEP bounds anyway and this will
            #prevent strange artefacts occuring due to the boundary of the
            #LHC data.
            mH=mHmin
        if x<xsmin:
            #xsmin should be zero so I expect we will not encounter this
            #condition, but just in case we should set the computed
            #value to the minimum value covered by the data we have.
            x=xsmin
        if x>xsmax:
            #if x is too large it will be excluded so return a very low
            #loglikelihood value
            return -1e300
        #print 'in LF', x, mH, chanLF(x,mH)[0,0]
        LogL = chanLF(mH,x)[0,0]    #extract the appropriate loglikelihood value from the interpolating function
        return LogL
        
    #Construct likelihood function object
    return LHChiggschanLF

#========================================================================
    #Special note: make sure 'limitcurve' for higgs likelihood function is loaded during observables initialisation.
    #Special note 2: make sure likelihood maps for LHC higgs likelihood function are loaded during observables initialisation.
    
#==========================================================
# "Effective" priors
#==========================================================
#
# These "effective priors" are volume element factors which are NOT part of the transformation of the random numbers
# generated by the sampler, because they rely on information computed by the programs in the run sequence. Instead,
# the volume element factor is multiplied into the likelihood, so the effective prior counts as just another piece of
# the likelihood function as far as pysusy is concerned. Their effect on the scan is to change the prior actually
# used into a different "effective" one by folding in the appropriate volume factor.
#
# For more info on how this works see notebook #3 page 75-82, and the papers proposing the various effective priors
# implemented below (0705.0487, 0812.0536, 0907.0594, 1005.2525)
#
# NOTE: These effective priors involve Jacobians due to changing sets of variables, so they are applicable only for
# the MODEL and PRIOR specified. If they are used with any other choice of model or prior they will generate errors,
# or at least rubbish results.
#
# These priors return an "effective" likehood contribution, so they must be implemented through a dummy observable.

def CCRprior(Blow,tanb,muZ): 
    """Prior as defined by 0907.0594
    For use with CMSSM, with FLAT prior in {m0,m12,A0,tanB}
    Keyword args:
    Blow - low scale value of higgs potential B parameter
    tanb - low scale value of tan(beta) 
    muZ - low scale value of higgs potential mu parameter,
     fixed to value required to reproduce Z mass (as it should
     be ordinarily)
    """
    tan2b = tanb**2
    J = (tan2b - 1)/(tan2b*(1 + tan2b)) * (Blow/muZ)
    #print "CCR prior factor: ",J
    #if J is negative the log will return a complex number. This is bad,
    #so we better take the mod.
    return log(np.abs(J)) #return log J because it will be ADDED to the other *log*likelihood components
    
#==========================================================
# BUILD LIKELIHOOD FUNCTION CALCULATOR CLASS
#==========================================================

class LikeFuncCalculator:
    """Computes the PySUSY likelihood dictionary and global likelihood
    Args:
    obsdict -- a dictionary containing a dictionaries of observables 
        from each program in the run sequence, e.g.
        obsdict = { 'spectrum':          {  'mH': 125,
                                            'mX': 1200,
                                         },
                    'darkmatter':        {  'omegah2': 0.1,
                                            'gmuon'  : 33e-10,
                                         }
                  }
    Attributes set:
    self.globlikefunc -- Global likelihood function. Used by CMSSM.py.
    """
    #==========================================================
    # BEGIN OBJECT INITIALISATION
    #==========================================================
    # Read in various data files and do pre-analysis required to
    # build the various likelihood functions
    
    def __init__(self,configfile):
        """Gather information required to construct some of the more
        complicated likelihood functions"""
        #--------------------------------------------------------------
        # Read config file (path supplied by master config module)
        #--------------------------------------------------------------
        cfg = ConfigParser.RawConfigParser()
        #set default values
        pysusyroot = '/home/565/bff565/projects/pysusyMSSM/pysusy3'
        defconfig = pysusyroot+'/config/general_defaultsMSSM.cfg'
        print 'Reading default config file {0}'.format(defconfig)
        cfg.readfp(open(defconfig))                                     #before reading the real config file, read in the defaults (in case any new ones are missing from older config files)
        #read config file
        print 'Reading config file {0}'.format(configfile)
        cfg.read(configfile)
        
        specgen = cfg.get('progoptions','spectrumgenerator') #need to know this for a few spectrum generator specific observables
        
        #--------------------------------------------------------------
        # Load options (whether to exclude some observables from scan; likelihood values still computed and output just not used)
        #--------------------------------------------------------------
        #observables options
        useHiggs            = cfg.getboolean('obsoptions', 'useHiggs')
        useLHCHiggs         = cfg.getboolean('obsoptions', 'useLHCHiggs')
        useDMdirect         = cfg.getboolean('obsoptions', 'useDMdirect')
        centralreliclimit   = cfg.getboolean('obsoptions', 'centralreliclimit')
        #program options
        useSuperISO         = cfg.getboolean('progoptions', 'useSuperISO')
        usemicrOmegas       = cfg.getboolean('progoptions', 'usemicrOmegas')
        useHDecay           = cfg.getboolean('progoptions', 'useHDecay')
        #likelihood options                                             #We do this so that the cfg file does not have to be read every loop by the likelihood function calculator
        useMW               = cfg.getboolean('likefunc', 'useMW')
        usedeltarho         = cfg.getboolean('likefunc', 'usedeltarho')
        useomegah2          = cfg.getboolean('likefunc', 'useomegah2')
        usedeltaamu         = cfg.getboolean('likefunc', 'usedeltaamu')
        useDSL              = cfg.getboolean('likefunc', 'useDSL')
        #prior options
        useCCRprior         = ('CCRprior'==cfg.get('prioroptions', 'effprior'))
        if cfg.getboolean('prioroptions', 'uselog') and useCCRprior:
            raise ValueError('Attempted to activate CCR prior with log prior!\
Must use flat prior instead! Please adjust options config file.')
        
        #Once off computations:
        #===================================================================
        #---------------------------------------------------------------
        # GENERATE HIGGS MASS LIMIT CURVE (see likefunctest.py and interpolate-test.py for testing)
        #---------------------------------------------------------------
        #read in digitized curve (from hep-ph/0603247 fig 3a)
        rawdata = np.loadtxt(pysusyroot+'/data/Fig3a_hep-ph0603247.asc', unpack=False) #open data table file for reading (contains x,y (mH,g) data for curve in two columns separated by a space)
        rawdata = map(tuple,rawdata)    #we don't want a numpy array here, just a list of tuples
        #need to sort the data to enforce monotonicity (we want the smallest m_H (x) allowed for a given coupling (y))
        #to do this we loop through the data from largest to smallest y, killing any data with larger x than the previous point.
        sortdata = sorted(rawdata, key=lambda coords: coords[1], reverse=True) #sorts the rows by the second column in decending order
        maxx = sortdata[0][0]    #x value of 1st data entry
        finaldata = []       #array to store results in
        for entry in sortdata:    
            if entry[0] <= maxx: #if this entry has a smaller x than the current maximum  
                finaldata += [entry]    #then add it to the list of final entries
                maxx = entry[0] #and set this as the new maximum allowed x value (i.e. maxx has been reduced)
            #otherwise we throw the data entry away
        finaldata.reverse() #reverse the data to put it in the correct order for use with interp1d (increasing in the x value)
        finaldata = np.array(finaldata)    #convert to a numpy array so we can manipulate the contents more easily with indices
        #find limits of data (g=coupling)
        ming = min(finaldata[:,1])
        maxg = max(finaldata[:,1])
        minm = min(finaldata[:,0])
        maxm = max(finaldata[:,0])
    
        curve = interp.interp1d(finaldata[:,1],finaldata[:,0],kind='linear')  #note x and y are swapped because we want to supply a coupling and get back out a mass limit
        
        #The following function defines the Higgs mass lower bound for a given coupling g, feed it into
        #the Higgs likelihood function 'higgslikefunc'
        def mHlimitcurve(g):  #define a function which will return the correct Higgs mass lower bound for a given coupling g
            if g<ming:
                m_H = 0  #if the coupling is lower than we have a curve for there is no limit on the Higgs mass 
            elif g>maxg:
                m_H = maxm #if the coupling is higher than we have curve for assume the maximum limit found is a lower bound on the read limit
            else:
                m_H = curve.__call__(g) #if we are in the middle find the mass bound using the interpolating function we created
            return m_H
        
        #-----------------------------------------------------------------------
        # Read in Xenon100 confidence limits from digitized curve data
        #-----------------------------------------------------------------------
        # read in digitized curves (from 1104.2529 fig 5)
        rawdata = np.loadtxt(pysusyroot+'/data/1104.2529-Xenon100fig5.csv', unpack=False, delimiter=",") #open data table file for reading (contains x,y (mH,g) data for curve in two columns separated by a space)
        rawdata = map(tuple,rawdata)    #we don't want a numpy array here, just a list of tuples
        
        finaldata=np.array(rawdata)
        
        obslimitcurve = interp.interp1d(finaldata[:,0],finaldata[:,1],kind='linear')
        exp1sigmacurve = interp.interp1d(finaldata[:,0],finaldata[:,2],kind='linear')
        
        minmX = min(finaldata[:,0])
        maxmX = max(finaldata[:,0])
        #-----------------------------------------------------------------------
        # Read in CMS+LHCb CLs values for BR(Bs->mu+mu-) from digitized curve data
        #-----------------------------------------------------------------------
        #read in digitized curve (from fig 8 of 1110.2411 (LHCb))
        rawdata = np.loadtxt(pysusyroot+'/data/Bsmumu-1110.2411-fig8.csv', unpack=False, delimiter=",") #open data table file 
        #(data assumed to be in units of [10^-9])
    
        rawdata = map(tuple,rawdata)    #we don't want a numpy array here, just a list of tuples
        finaldata=np.array(rawdata)
       
        CLscurve = interp.interp1d(finaldata[:,0],finaldata[:,1],kind='linear')
       
        minBR = min(finaldata[:,0])
        maxBR = max(finaldata[:,0])
        #-----------------------------------------------------------------------
        # Read in reconstructed ATLAS likelihood functions for Higgs searches
        #-----------------------------------------------------------------------
        # Likelihoods reconstructed from signal fit results using 'higgs_combination.py'
        # MAKE SURE THESE WERE ALL GENERATED USING THE SAME mHvals AND xsvals!
        
        mherrTH=1.5 #=====THEORY ERROR IN HIGGS MASS (GeV)=======================
        mherrEX=1.  #=====EXTRA EXPERIMENTAL UNCERTAINTY IN HIGGS MASS (GeV)=====
        mherr=sqrt(mherrTH**2+mherrEX**2) #==COMBINED EXTRA UNCERTAINTY IN MH===
        #print 'mherr=', mherr
        #read in higgs mass and xs/xs_SM axis values
        mHvals = np.loadtxt(pysusyroot+'/data/mHvalsDchi2.dat', unpack=False, delimiter=" ")
        xsvals = np.loadtxt(pysusyroot+'/data/xsvalsDchi2.dat', unpack=False, delimiter=" ")
        #retrieve step size used for mH arrays (to be used in convolution)
        dmh=mHvals[1]-mHvals[0]
        dxs=xsvals[1]-xsvals[0]
        # get boundaries of data
        minmH = min(mHvals)
        maxmH = max(mHvals)
        minxs = min(xsvals)
        maxxs = max(xsvals)
        mHxsbounds = (minmH,maxmH,minxs,maxxs)
        #filename prefixes for chi2 maps
        prefixes = ['ATLAShZZ4lBF','ATLAShyyBF','ATLAShWW2l2vBF'] 
        #(ATLAS h-->ZZ-->4l, h-->aa and h-->WW-->2l+2v respectively)
        Dchi2IN = {}    #dictionary to store input chi2 maps
        LHChiggsLF = {} #dictionary to store output likelihood function interpolating function
        for prefix in prefixes:
            Dchi2IN[prefix] = np.loadtxt(pysusyroot+'/data/{0}Dchi2.dat'.format(prefix), unpack=False, delimiter=" ") #read in chi2 map
            #print Dchi2IN[prefix].shape
            # Convolve input chi2 map with the combined theory+experimental uncertainty on the higgs mass 
            #(Really I think we should not do this to BOTH the LEP and LHC likelihood functions, it should be done AFTER
            #they are combined, but that is difficult to arrange and we will not make much of a mistake by doing
            #it this way).
            errvals = np.arange(-6*mherr,6*mherr,dmh) #make sure chosen range covers at least 5 standard deviations of the err
            if np.mod(len(errvals),2)==0:
                errvals=errvals[:-1]    #if the error range length is even, cut off an element to make it odd (was having some problems when it was even)
            if len(errvals)!=0:
                #If error is smaller than the step size of the input chi^2 map 
                #in mH direction, don't bother with the convolution
                #---------
                #define arrays to be convolved for every xs value
                Larray = exp(-0.5*Dchi2IN[prefix]) #convert input chi2 values to likelihood values
                Lerrvect = 1./sqrt(2*pi*mherr**2)*exp(-0.5*errvals**2/mherr**2)
                #convolve in mh direction for each value of xs
                convLF = np.array([np.convolve(Larray[ixs,:],Lerrvect,mode='full') for ixs,xs in enumerate(xsvals)])
                #Now, I did the full convolution in case the error gaussian array is so big it is larger than the Likelihood
                #function array itself. We will manually chop out the piece of the result corresponding to the original
                #mH values that we started with. I am pretty sure I am doing this correctly now.
                hfw=(len(Lerrvect)-1)//2
                #print 'hfw=', hfw, 'len(convLF[0,:])=',len(convLF[0,:]), 'len(Lerrvect)=',len(Lerrvect)
                if hfw!=0:
                    convLF = convLF[:,hfw:-hfw]
                else:
                    convLF = convLF[:,0:-1]
                #print convLF.shape
            else:
                convLF = exp(-0.5*Dchi2IN[prefix])  #just convert to likelihood values
            #We will have messed up the scaling by doing the convolution, so need to rescale to the maximum likelihood point
            #(this also fixes up constant factors resulting from delta_mh, i.e. the scaling due to the width of the mH slices
            #Go back to log likelihood to do the interpolation
            convLF = log(convLF)
            convLF[np.isneginf(convLF)]=-1e300 #need to deal with the log(0) entries. These generate -inf's which here are replaced by a very large negative number.
            #Find global max
            globmaxLogL = max(convLF.flatten())
            convLFrw= convLF - globmaxLogL
            #create an interpolating function of the result
            LHChiggsLF[prefix] = interp.RectBivariateSpline(mHvals,xsvals,convLFrw.transpose(),kx=1,ky=1)   #set kx,ky=1 to do piecewise linear spline. Don't want higher-order stuff.
        
        #===============================================================
        #---relic density-----------------------------------------------
        if centralreliclimit==True:
            omegalikefunc=LFs.lognormallike                        #(assumes neutralino relic density = dark matter relic density)
        else:
            omegalikefunc=LFs.logerfupper                          #(assumes neutralino relic density < dark matter relic density)
        
        #--proton-neutralino SI cross-section---------------------------
        xenonlikefunc = xenon100likefunc(obslimitcurve,exp1sigmacurve,minmX,maxmX) #(XENON likelihood contribution)
         
        #--Bs -> mu+ mu- -----------------------------------------------
        Bsmumulikefunc = CMSLHCbBsmumulikefunc(CLscurve,minBR,maxBR) #From LHCb data 
            
        #---BUILD LIKELIHOOD FUNCTIONS----------------------------------
        #ATLAS Higgs search likelihood functions:
        useATLAShiggsLogL = False
        ATLAShiggsLogLs = {}                                       
        for prefix in prefixes:
            ATLAShiggsLogLs[prefix] = LHChiggslikefunc(LHChiggsLF[prefix],mHxsbounds)
    
        #===============================================================
        #== COMPUTE GLOBAL LIKELIHOOD FUNCTION ===========================
        #===============================================================
        def globlikefunc(obsdict):
            """Compute log likelihoods and global log likelihood
            Output format:
            likedict = {likename: (logL, uselike),...}
            """
            likedict = {}                                               #reset likelihood dictionary
            
            #Extract individual observables dictionaries from container dictionary
            specdict = obsdict['spectrum']
            if usemicrOmegas: darkdict = obsdict['darkmatter']
            if useSuperISO:   flavdict = obsdict['flavour']
            if useHDecay:     decadict = obsdict['decay']
            
            #===========================================================
            # EFFECTIVE PRIOR
            #===========================================================
            likedict['CCRprior'] = (CCRprior(specdict['BQ'],specdict['tanbQ'],specdict['muQ']), useCCRprior)
            
            #===============================================================
            #   DEFINE LIKELIHOOD CONTRIBUTIONS
            #===============================================================
            #Note: some things left commented in old pysusy2 format because
            #they contain useful information and I can't be bothered
            #reformatting it.
            #-----------STANDARD MODEL DATA ------------
            # this is used to constrain the nuisance parameters
            # -NB-REMOVED -> USING GAUSSIAN PRIORS INSTEAD.
            #ialphaemL = Observable(slhafile=setupobjects[SPECTRUMfile], block="SMINPUTS", 
            #    index=1, average=127.918, sigma=0.018,likefunc=LFs.lognormallike)    
            #    #Jun 2009 hep-ph/0906.0957v2, they reference PDG 2008, but I can't find the value myself.
            #alphasL = Observable(slhafile=setupobjects[SPECTRUMfile], block="SMINPUTS", 
            #    index=3, average=0.1184, sigma=0.0007,likefunc=LFs.lognormallike)     
            #    #PDG 2010 pg 101 - Physical Constants
            #MZL = Observable(slhafile=setupobjects[SPECTRUMfile], block="SMINPUTS", 
            #    index=4, average=91.1876, sigma=0.0021,likefunc=LFs.lognormallike)          
            #    #PDG 2010 pg 101 - Physical Constants
            #MtopL = Observable(slhafile=setupobjects[SPECTRUMfile], block="SMINPUTS", 
            #    index=6, average=173.3, sigma=1.1,likefunc=LFs.lognormallike)             
            #    #1007.3178, tevatron, 19 Jul 2010
            #MbotL = Observable(slhafile=setupobjects[SPECTRUMfile], block="SMINPUTS", 
            #    index=5, average=4.19, sigma=0.18,likefunc=LFs.lognormallike)        
            #    #PDG 2010 quark summary - http://pdg.lbl.gov/2010/tables/rpp2010-sum-quarks.pdf (NOTE - lower uncertainty is 0.06 not 0.18, altered distribution to make it symmetric for simplicity)
            
            likedict['MW'] = (LFs.lognormallike(x=specdict['MW'], mean=80.399, sigma=sqrt(0.023**2+0.015**2)), useMW) 
                                                                        #PDG 2010, 2011 and partial 2012 update
                                                                        #from
                                                                        #http://lepewwg.web.cern.ch/LEPEWWG/ - extracted Apr 8 2011 (Jul 2010 average value)
                                                                        #theory (second component) uncertainty stolen from 1107.1715, need proper source (they
                                                                        #do not give one)
            #-----------MAIN CONTRIBUTORS TO LIKELIHOOD-----------------

            #=====Electroweak precision, RELIC DENSITY and (g-2)_mu========
            if usemicrOmegas:
                # delta rho parameter, describes MSSM corrections to electroweak observables
                likedict['deltarho'] = (LFs.lognormallike(x=darkdict['deltarho'], mean=0.0008, sigma=0.0017), usedeltarho)
                                                                        #PDG Standard Model Review: Electroweak model and constraints on new physics, pg 33 eq 10.47.
                                                                        #Taking larger of the 1 sigma confidence internal values
                                                                        #(likelihood function is actually highly asymmetric, PDG gives
                                                                        #1 sigma: 1.0008 +0.0017,-0.0007
                                                                        #2 sigma: 1.0004 +0.0029,-0.0011
                                                                        #We are ignoring these complexities. The 0.0017 sigma should be quite on the conservative
                                                                        #side, and contributions seem to only be positive, so the weird lower sigmas are essentially
                                                                        #irrelevant anyway, in the CMSSM at least. I do not know if other MSSM models will be different,
                                                                        #I assume probably not.
                                                                        #In ISAJET have sin**2(thetaw), consider replacing deltarho with this. Values in different schemes
                                                                        #in same part of pdg, pg 30, Table 10.8.
                #Dark matter relic density
                likedict['omegah2'] = (omegalikefunc(darkdict['omegah2'], 0.1123, sqrt((0.0035)**2+(0.10*0.1123)**2)), useomegah2)         
                                                                        #Jan 2010, 1001.4538v2, page 3 table 1 (WMAP + BAO + H0 mean)
                                                                        #theory (second component) uncertainty stolen from 1107.1715, need proper source
                #Anomalous muon magnetic moment
                likedict['deltaamu'] = (LFs.lognormallike(x=darkdict['deltaamu'], mean=33.53e-10, sigma=8.24e-10), usedeltaamu)
                                                                        #1106.1315v1, Table 10, Solution B (most conservative)
                #=====FLAVOUR OBSERVABLES FROM DARKMATTERfile======
                # Note: Ditching these for now. Don't use them and they just make the output confusing.
                # micrOmegas computes some of these essentially 'for free', so we may
                # as well record them for comparison.
                # NOTE: See equivalent flavour file observables definitions for references.
                #
                #bsgmoM = Observable(slhafile=setupobjects[DARKMATTERfile], block="CONSTRAINTS", 
                #index=2, average=3.55e-4, sigma=sqrt((0.26e-4)**2+(0.30e-4)**2),likefunc=LFs.lognormallike, uselike=False)
                #       
                #bmumuM = Observable(slhafile=setupobjects[DARKMATTERfile], block="CONSTRAINTS", 
                #index=3, average=4.3e-8, sigma=0.14*4.3e-8,likefunc=CMSLHCbBsmumulikefunc(CLscurve,minBR,maxBR), uselike=False)
                #
                #obsorder += ['bsgmoM','bmumuM'] 
                
                #=====DARK MATTER DIRECT DETECTION========
                # LSP-nucleon cross sections                            # uncertainty in LSP-proton SI cross-section
                                                                        # Note, this is based on uncertainties in hadronic scalar coefficients, currently hardcoded into micromegas.
                                                                        # These uncertainties are propagated through a modified version of micromegas alongside the amplitude calculation.
                                                                        # LSP-proton SI cross-section
                likedict['sigmaLSPpSI'] = (xenonlikefunc(darkdict['sigmaLSPpSI'],specdict['Mneut1'],darkdict['dsigmaLSPpSI']),useDMdirect) 
                                                                        #likelihood function built from information in fig 5 of 1104.2549, 100 days of Xenon100 data (Apr 2011)     
            #=====FLAVOUR OBSERVABLES=============
            if useSuperISO:
                #Branching ratios
                # BF(b->s gamma) - USING SUPERISO VALUE FOR LIKELIHOOD. Micromegas value recorded for comparison
                likedict['bsgmo'] = (LFs.lognormallike(x=flavdict['bsgmo'], mean=3.55e-4, sigma=sqrt((0.26e-4)**2+(0.05*3.55e-4)**2)), True)
                                                                        #PDG 2010, page 883, theory (second component) uncertainty stolen from 1107.1715, need proper source
                                                                        #Ok, hep-ph/0009337v2 figure 2 shows some predictions for b->s gamma in the MSSM, figure 3 shows the mu<0
                                                                        #branch. Also on pg 13 they compare two computational procedures and say the difference is of order 5%
                                                                        #Let's go with 5%, is about 0.18 extra uncertainty component)
                # BF(Bs -> mu+mu-) - USING SUPERISO VALUE FOR LIKELIHOOD. Micromegas value recorded for comparison
                likedict['bmumu'] = (Bsmumulikefunc(flavdict['bmumu']), True)
                                                                        #bmumu = MultiIndexObservable(setupobjects[LOWENERGYfile],LOWENERGYblock,(531,1,0,2,13,-13), 
                                                                        #average=4.3e-8, sigma=0.14*4.3e-8,likefunc=CMSLHCbBsmumulikefunc(CLscurve,minBR,maxBR))       
                                                                        #likelihood function derived from CMS+LHCb CLs curve presented at Lepton-Photon Aug 2011, Mumbai
                                                                        #Basically the same as 1110.2411v1 from the look of it, but the Lepton-Photon curve extends to
                                                                        #lower values so let's keep using that.
                                                                        #sigma left over from old likefunc, no longer does anything
                """
                Turns out SuperIso does this already, so I will cut out the extra computation.
                # BF(B_u -> tau nu)
                Butaunu = MultiIndexObservable(setupobjects[LOWENERGYfile],LOWENERGYblock,((521,1,0,2,-15,16)),likefunc=LFs.nolike)      
                # BF(B_u -> tau nu)_SM
                ButaunuSM = MultiIndexObservable(setupobjects[LOWENERGYfile],SMLOWENERGYblock,((521,1,0,2,-15,16)),likefunc=LFs.nolike)
                def obsdiv(obs1,obs2):  #simple function to divide two numbers, feed into composite observable (compute ratio of two branching fractions)
                    return obs1/obs2
                # BF(B_u -> tau nu) / BF(B_u -> tau nu)_SM 
                ButaunuButaunuSM = CompositeObservable(function=obsdiv,observables=[Butaunu,ButaunuSM],
                        average=1.28, sigma=0.38,likefunc=LFs.lognormallike)
                    #copying 1107.1715, need to find proper source.
                """
                # BF(B_u -> tau nu) / BF(B_u -> tau nu)_SM 
                # ButaunuButaunuSM = MultiIndexObservable(setupobjects[LOWENERGYfile],LOWENERGYblock,(521,2,0,2,-15,16),
                #        average=1.28, sigma=0.38,likefunc=LFs.lognormallike)
                #    #copying 1107.1715, need to find proper source.
                    
                #REPLACING THE ABOVE RATIO, it is more straightforward to impose constraints directly on the branching ratio itself
                #BF(B_u -> tau nu) 
                likedict['Butaunu'] = (LFs.lognormallike(x=flavdict['Butaunu'], mean=1.67e-4, sigma=0.39e-4), True)
                                                                        #Heavy Flavour Averaging Group (HFAG)
                                                                        #1010.1589v3 (updated 6 Sep 2011), retrieved 12 Oct 2011
                                                                        #Table 127, pg 180
                # Delta0(B->K* gamma) (hope this is the same as Delta0-, seems like it might be)
                # (isospin asymmetry)
                likedict['Delta0'] = (LFs.lognormallike(x=flavdict['Delta0'], mean=0.029, sigma=sqrt(0.029**2+0.019**2+0.018**2)), True)
                                                                        # BaBAR, 2008 - 0808.1915, pg 17. No theory error included, pieces are different aspects of experimental error.
                # BR(B+->D0 tau nu)/BR(B+-> D0 e nu)
                likedict['BDtaunuBDenu'] = (LFs.lognormallike(x=flavdict['BDtaunuBDenu'], mean=0.416, sigma=0.128), True)
                                                                        # BaBAR, 2008 - 0709.1698, pg 7, Table 1 (R value). No theory error included.
                # R_l23: involves helicity suppressed K_l2 decays. Equals 1 in SM.
                likedict['Rl23'] = (LFs.lognormallike(x=flavdict['Rl23'], mean=1.004, sigma=0.007), True)
                                                                        # FlaviaNet Working Group on Kaon Decays
                                                                        # 0801.1817v1, pg 29, Eq. 4.19. No theory error included (meaning SuperISO error, as for other observables)
                # BR(D_s->tau nu)
                likedict['Dstaunu'] = (LFs.lognormallike(x=flavdict['Dstaunu'], mean=0.0538, sigma=sqrt((0.0032)**2+(0.002)**2)), True)
                                                                        #Heavy Flavour Averaging Group (HFAG)
                                                                        #1010.1589v3 (updated 6 Sep 2011), retrieved 12 Oct 2011
                                                                        #Figure 68, pg 225. Theory error stolen from 1107.1715, need to find proper source. 
                # BR(D_s->mu nu)
                likedict['Dsmunu'] = (LFs.lognormallike(x=flavdict['Dsmunu'], mean=0.00581, sigma=sqrt((0.00043)**2+(0.0002)**2)), True)
                                                                        #Heavy Flavour Averaging Group (HFAG)
                                                                        #1010.1589v3 (updated 6 Sep 2011), retrieved 14 Oct 2011
                                                                        #Figure 67, pg 224. Theory error stolen from 1107.1715, need to find proper source.               
            #=================Direct sparticle search limits=============================
            nmass=np.abs(specdict['Mneut1'])                            #get abs because spectrum generator returns negative values sometimes
            smass=np.abs(specdict['MseL'])
            likedict['MseL'] = (LFs.logsteplower(x=smass, limit=99 if nmass<84 else 96 if smass-nmass>6 else 73), useDSL) #Phys. Lett. B544 p73 (2002)
            smass=np.abs(specdict['MsmuL'])
            likedict['MsmuL'] = (LFs.logsteplower(x=smass, limit=94.4 if smass-nmass>6 else 73), useDSL) #Phys. Lett. B544 p73 (2002)
            smass=np.abs(specdict['Mstau1'])
            likedict['Mstau1'] = (LFs.logsteplower(x=smass, limit=86 if smass-nmass>8 else 73), useDSL) #Phys. Lett. B544 p73 (2002)
            smass=np.abs(specdict['MesnuL'])
            likedict['MesnuL'] = (LFs.logsteplower(x=smass, limit=43 if smass-nmass<10 else 94), useDSL) #Phys. Lett. B544 p73 (2002)
            smass=np.abs(specdict['Mchar1'])
            likedict['Mchar1'] = (LFs.logsteplower(x=smass, limit=97.1 if (smass-nmass)>3 else 45), useDSL) #45 GeV limit from PDG 2010, unconditional limit from invisible Z width, other limit from Eur. Phys. J. C31 p421 (2003)
            #NOTE: USING SAME LIMITS FOR L AND R SQUARKS, CHECK THAT THIS IS FINE.
            smass=np.abs(specdict['Mstop1'])                            
            likedict['Mstop1'] = (LFs.logsteplower(x=smass, limit=95 if smass-nmass>8 else 63), useDSL) #? Damn don't seem to have written down where this comes from. Need to find out.
            smass=np.abs(specdict['Msbot1'])                            #NOTE: stop2 heavier than stop1 by definition so only need to bother applying limit to stop1. (1 and 2 are the mass eigenstates, mixtures of L and R interaction eigenstates). Same for sbot2
            likedict['Msbot1'] = (LFs.logsteplower(x=smass, limit=93 if smass-nmass>8 else 63), useDSL)
            #NOTEL USING SAME LIMITS FOR REST OF SQUARKS, CHECK THIS ABOVE, 'squarklikefunc'.
            #likelihood function defined above, usage: squarklikefunc(smassIN,nmassIN) (smass - THIS sparticle mass, nmass - neutralino 1 mass)
            #NOTE: L and R states are same as 1 and 2 states for other squarks because off diagonal terms in the mixing matrices are
            #negligible. This is not true for the third generation squarks which is why we are sure to label them 1 and 2 above (1=lightest)
            for Msquark in ['MsupL','MsupR',
                            'MsdownL','MsdownR',
                            'MsstrangeL','MsstrangeR',
                            'MscharmL', 'MscharmR']:
                likedict[Msquark] = (squarklikefunc(specdict[Msquark],nmass), useDSL)
            likedict['Mgluino'] = (LFs.logerflower(x=specdict['Mgluino'], limit=289, sigma=15), useDSL) #from 08093792 - not well checked, probably need to update with LHC data.
            
            # ---------------NOTE: LEP HIGGS MASS LIMIT-------------------. Using digitized LEP limit from hep-ph/0603247 (2006), fig 3a
            # Using digitized curve to compute m_h bound appropriate to g_ZZh coupling for each model point with estimated 3 GeV sigma for m_h returned by SoftSusy
            # Need the following observables to be extracted to compute Higgs likelihood function:
            # alpha,tanbetaQ    #RGE running of tanb is slow so tanbQ should be approximately the EW tanb value
            # Likelihood function for this is written above (needs to return a lower limit erf likelihood depending on g_ZZh):
            #higgs=lightest higgs mass;alpha=higgs scalar mixing angle;tanbeta=tan(higgs VEV ratio)
            mhiggs = np.abs(specdict['Mh0'])
            likedict['Mh0'] = (LFs.logerflower(x=mhiggs, limit=higgslimitfunc(specdict['alpha'],specdict['tanbQ'],mHlimitcurve), sigma=3), useHiggs)
            #NOTE!: DO THIS NEXT PAPER: 
            #uncertainty is borrowed from 1112.3564, who offer no justification for it. Reduced from previous value of 3 GeV. 
            # I assume the coupling for the other higgses is different so I need to check these before I can impose the LEP limit on them (which may make a tiny difference, it is possible for a heavier higgs to be detected while a lighter one with a smaller coupling remains unseen)
            
            # --------------LHC HIGGS SEARCH CONSTRAINTS---------------
            # Using likelihood functions extracted from ATLAS signal best-fit
            # plots for the 3 major search channels used in the 12 December 2011
            # combination (ATLAS-CONF-2011-163)
            # Channels used:
            # h-->aa
            # h-->ZZ-->4l
            # h-->WW-->2l+2v
            # Note, only the gg-->h production channel is important as the others
            # produce extra particles in the final state. We are assuming that these
            # are not missed by the detectors, but error due to this should be minimal.
            # Cross sections for each of these processes in the MSSM are computed 
            # using HDecay, and we constrain these directly using the ATLAS search
            # results.
            # Note: Cross-sections are relative to Standard Model values, i.e. x = xs_SUSY/xs_SM
            
            if useHDecay:
                #HDecay is having some problems with some model points at high m12. 
                #(returning nans) Assume these are NOT excluded for now (set cross-sections to zero)
                if np.isnan(decadict['XSgghaa']):       decadict['XSgghaa']     = 0
                if np.isnan(decadict['XSgghWW2l2v']):   decadict['XSgghWW2l2v'] = 0
                if np.isnan(decadict['XSgghZZ4l']):     decadict['XSgghZZ4l']   = 0
                likedict['XSgghaa']     = (ATLAShiggsLogLs['ATLAShyyBF']    (mhiggs, decadict['XSgghaa']), useLHCHiggs)
                likedict['XSgghWW2l2v'] = (ATLAShiggsLogLs['ATLAShWW2l2vBF'](mhiggs, decadict['XSgghWW2l2v']), useLHCHiggs)
                likedict['XSgghZZ4l']   = (ATLAShiggsLogLs['ATLAShZZ4lBF']  (mhiggs, decadict['XSgghZZ4l']), useLHCHiggs)
                
            #print useHDecay, specdict['Mh0'], decadict['XSgghaa']
            #----------for testing only---------------------------------
            #Check for 'nans' in the likedict
            #for likename,(logl,uselike) in likedict.iteritems():
            #    if np.isnan(logl):
            #        print likename, logl
            #        quit()
            
            #===============GLOBAL LOG LIKELIHOOD=======================
            LogL = sum( logl for logl,uselike in likedict.itervalues() if uselike )
            return LogL, likedict
            
        #===ASSIGN GLOBAL LIKELIHOOD FUNCTION TO ATTRIBUTE==============
        #------(so that it can be used by PySUSY)-----------------------
        self.globlikefunc = globlikefunc
            

        
        
