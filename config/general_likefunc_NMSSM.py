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

#LHCb Bs->mu+mu- profile log-likelihood curve 
def LHCbBsmumulikefunc(LogLcurve,minX,maxX):    
   """
   Keyword Args:
   LogLcurve - function which returns the LHCb Delta LogL value for a given
      theory prediction.
   minX - minimum extent of LogL curve in Bsmumu ('x' axis)
   maxX - maximum extent of LogL curve in Bsmumu ('x' axis)
   """
   def Bsmumulikefunc(Bsmumu):
      """Computes the log-likelihood value for a given BR(Bs->mumu) value.
      Bsmumu - predicted value of branching ratio. This function is just a 
      wrapper around the interpolating function 'LogLcurve' to deal with 
      predictions outside the interpolating range, and with unit conversions.
      """
      # Curve defined in [10^-9] units, must convert theory value to match 
      Bsmumu=(10**9)*Bsmumu 
      # Deal with theory values outside the range covered by the LogL curve by
      # setting them to the values on the limits of the range
      if Bsmumu<minX: Bsmumu=minX
      if Bsmumu>maxX: Bsmumu=maxX
      DLogL = LogLcurve.__call__(Bsmumu) # Get logl value
      return DLogL
         
   #return likelihood function
   return Bsmumulikefunc
#==========================================================
# "Effective" priors
#==========================================================
#
# These "effective priors" are volume element factors which are NOT part of the
# transformation of the random numbers generated by the sampler, because they 
# rely on information computed by the programs in the run sequence. Instead,
# the volume element factor is multiplied into the likelihood, so the effective
# prior counts as just another piece of the likelihood function as far as pysusy # is concerned. Their effect on the scan is to change the prior actually used
# into a different "effective" one by folding in the appropriate volume factor.
#
# For more info on how this works see notebook #3 page 75-82, and the papers
# proposing the various effective priors
# implemented below (0705.0487, 0812.0536, 0907.0594, 1005.2525)
#
# NOTE: These effective priors involve Jacobians due to changing sets of 
# variables, so they are applicable only for the MODEL and PRIOR specified. If
# they are used with any other choice of model or prior they will generate errors,
# or at least rubbish results.
#
# These priors return an "effective" likehood contribution, so they must be 
# implemented through a dummy observable.

# DOYOUN'S NMSSM TUNING PRIOR GOES HERE

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
    
    def __init__(self,configfile,defconfig):
        """Gather information required to construct some of the more
        complicated likelihood functions"""
        #--------------------------------------------------------------
        # Read config file (path supplied by master config module)
        #--------------------------------------------------------------
        cfg = ConfigParser.RawConfigParser()
        # Get default config values
        # (Before reading the real config file we read in default settings, in
        # case any new ones are missing from older config files)
        print 'Reading default config file {0}'.format(defconfig)
        cfg.readfp(open(defconfig))
        #read config file
        print 'Reading config file {0}'.format(configfile)
        cfg.read(configfile)
        
        #need to know this for a few spectrum generator specific observables
        specgen = cfg.get('progoptions','spectrumgenerator') 
        
        #--------------------------------------------------------------
        # Load options (whether to exclude some observables from scan; 
        # likelihood values still computed and output just not used)
        #--------------------------------------------------------------

        #observables options
        #useHiggs            = cfg.getboolean('obsoptions', 'useHiggs')
        useLHCHiggs         = cfg.getboolean('obsoptions', 'useLHCHiggs')
        useBdecays          = cfg.getboolean('obsoptions', 'useBdecays')
        #useDMdirect         = cfg.getboolean('obsoptions', 'useDMdirect')
        centralreliclimit   = cfg.getboolean('obsoptions', 'centralreliclimit')
        #program options
        usemicrOmegas       = cfg.getboolean('progoptions','computerelic') \
                           or cfg.getboolean('progoptions','computedirdet') \
                           or cfg.getboolean('progoptions','computeindirdet')
        #useHDecay           = cfg.getboolean('progoptions', 'useHDecay')
        #likelihood options                                             #We do this so that the cfg file does not have to be read every loop by the likelihood function calculator
        #useMW               = cfg.getboolean('likefunc', 'useMW')
        #usedeltarho         = cfg.getboolean('likefunc', 'usedeltarho')
        useomegah2          = cfg.getboolean('likefunc', 'useomegah2')
        #usedeltaamu         = cfg.getboolean('likefunc', 'usedeltaamu')
        #useDSL              = cfg.getboolean('likefunc', 'useDSL')
        #prior options
        #useCCRprior         = ('CCRprior'==cfg.get('prioroptions', 'effprior'))
        #if cfg.getboolean('prioroptions', 'uselog') and useCCRprior:
        #    raise ValueError('Attempted to activate CCR prior with log prior!\
#Must use flat prior instead! Please adjust options config file.')

        #===============================================================
        # ONCE OFF COMPUTATIONS
        #===============================================================
        # Construction of numerical likelihood functions from data files,
        # etc.
        
        #-----------------------------------------------------------------------
        # Read in LHCb loglikelihood curve for BR(Bs->mu+mu-) from digitized 
        # curve data
        #-----------------------------------------------------------------------
        #read in digitized curve (from suppl. material fig 11. 8 of 1211.2674 (LHCb))
        rawdata = np.loadtxt(pysusyroot+'/data/Bsmumu-1110.2411-fig8.csv', unpack=False, delimiter=",") #open data table file 
        #(data in units of [10^-9])
    
        rawdata = map(tuple,rawdata)    #we don't want a numpy array here, just a list of tuples
        finaldata=np.array(rawdata)
       
        BsmumuLogLcurve = interp.interp1d(finaldata[:,0],finaldata[:,1],kind='linear')
        # find out what the range covered by the data is
        minBR = min(finaldata[:,0])
        maxBR = max(finaldata[:,0])
        
        #===============================================================
        
        #-----------------------------------------------------------------------
        # Build likelihood definitions
        #-----------------------------------------------------------------------
        
        #---relic density-----------------------------------------------
        if centralreliclimit==True:
            #(assumes neutralino relic density = dark matter relic density)
            omegalikefunc=LFs.lognormallike          
        else:
            #(assumes neutralino relic density < dark matter relic density)
            omegalikefunc=LFs.logerfupper  
        
        #--Bs -> mu+ mu- -----------------------------------------------
        #From LHCb data 
        Bsmumulikefunc = LHCbBsmumulikefunc(BsmumuLogLcurve,minBR,maxBR) 
        
        #=======================================================================
        # COMPUTE GLOBAL LIKELIHOOD FUNCTION 
        #=======================================================================
        def globlikefunc(obsdict):
            """Compute log likelihoods and global log likelihood
            Output format:
            likedict = {likename: (logL, uselike),...}
            """
            likedict = {}   #reset likelihood dictionary
            
            #Extract individual observables dictionaries from container dictionary
            specdict = obsdict['spectrum']
            decadict = obsdict['decay']
            if usemicrOmegas: darkdict = obsdict['darkmatter']
            
            #===========================================================
            # EFFECTIVE PRIOR
            #===========================================================
            #likedict['CCRprior'] = (CCRprior(specdict['BQ'],specdict['tanbQ'],specdict['muQ']), useCCRprior)
            
            #===============================================================
            #   DEFINE LIKELIHOOD CONTRIBUTIONS
            #===============================================================
            #-----------MAIN CONTRIBUTORS TO LIKELIHOOD-----------------

            #=====Electroweak precision, RELIC DENSITY and (g-2)_mu=============
            if usemicrOmegas:
                #Dark matter relic density
                likedict['omegah2'] = (omegalikefunc(darkdict['omegah2'], \
                    0.1123, sqrt((0.0035)**2+(0.10*0.1123)**2)), useomegah2)         
                    #Jan 2010, 1001.4538v2, page 3 table 1 (WMAP + BAO + H0 mean)
                    #theory (second component) uncertainty stolen from 1107.1715,
                    #need proper source
            
            #=====Higgs constraints=============================================
            # We first need to find out which of the NMSSM Higgses is SM-like
            # Check the reduced couplings? Use those which are closest on 
            # average to 1? Crude, but good enough for first quick scan.
            
            Higgses = ['H1','H2','H3','A1','A2'] # Must match blockmap
            #Compute summed squared difference of couplings from 1
            rgsqdiff = {}
            for Higgs in Higgses:
                rgsqdiff[Higgs] = \
                    (specdict['rg_{0}_u'.format(Higgs)] - 1)**2 \
                  + (specdict['rg_{0}_d'.format(Higgs)] - 1)**2 \
                  + (specdict['rg_{0}_WZ'.format(Higgs)] - 1)**2 \
                  + (specdict['rg_{0}_g'.format(Higgs)] - 1)**2 \
                  + (specdict['rg_{0}_a'.format(Higgs)] - 1)**2 \
            #Get key of entry of rqsqdiff containing the min. squared difference
            mostSMlike = min(rgsqdiff, key=rgsqdiff.get)
                
            likedict['mh_SMlike'] = (LFs.lognormallike(\
                x=specdict['M{0}'.format(mostSMlike)], \
                mean=126., sigma=sqrt(1.**2)), useLHCHiggs) 
                # Just a rough guess at the measured mass of the SM-like Higgs.
                # Replace this with a rigorous likelihood involving decay rates.
            
            print mostSMlike, specdict['M{0}'.format(mostSMlike)], \
                rgsqdiff[mostSMlike]
                
            #===============Flavour constraints=========================
            # Branching ratios:
            # Switch on/off using "useBdecays" config option.
            # "Theory error" taken to be the larger of the upper/lower errors
            # returned by nmspec. ->UPDATE: now using LFs.logdoublenormal,
            # models upper and lower errors by seperate Gaussians.
            
            # BF(b->s gamma) (i.e. B_u/B_d -> X_s gamma)
            bsgexperr2 = (0.26e-4)**2+(0.09e-4)**2
            bsguperr2 = bsgexperr2+(specdict['bsgmo+eth']-specdict['bsgmo'])**2
            bsglwerr2 = bsgexperr2+(specdict['bsgmo-eth']-specdict['bsgmo'])**2              
            likedict['bsgmo'] = (LFs.logdoublenormal(x=specdict['bsgmo'],
                mean=3.55e-4, sigmaP=sqrt(bsguperr2), sigmaM=sqrt(bsglwerr2))
                                                                  , useBdecays)
            #HFAG, arXiv:1010.1589 [hep-ex], Table 129 (Average)
            # 0.09e-4 contribution added in accordance with newer HFAG edition:
            #HFAG, arXiv:1207.1158 [hep-ex], pg 203. (i.e. basically unchanged)

            # BR(B+ -> tau+ + nu_tau)
            btaunuexperr2 = (0.3e-4)**2
            btaunuuperr2 = btaunuexperr2+(specdict['B+taunu+eth']-specdict['B+taunu'])**2
            btaunulwerr2 = btaunuexperr2+(specdict['B+taunu-eth']-specdict['B+taunu'])**2              
            likedict['B+taunu'] = (LFs.logdoublenormal(x=specdict['B+taunu'],
                mean=1.67e-4, sigmaP=sqrt(btaunuuperr2), sigmaM=sqrt(btaunulwerr2))
                                                                  , useBdecays)
            #HFAG 1010.1589v3 (updated 6 Sep 2011), retrieved 12 Oct 2011
            #Table 127, pg 180
            #HFAG, arXiv:1207.1158 [hep-ex], pg 204. table 144
            #(basically unchanged from 2010 data, smaller uncertainity 
            #(0.39->0.3), mean unchanged.
            
            # BR(Bs -> mu+ mu-)
            # See comments where BsmumuLogLcurve is created from data files
            likedict['bmumu'] = (Bsmumulikefunc(specdict['bmumu']), useBdecays)
            #Folding theory error into this properly would be hard... need to
            #convolve it in for every point. Can't think of a better way.
            #Otherwise need to settle on something constant that can be
            #computed at the beginning of the run.
            #specdict['bmumu+eth']
            #specdict['bmumu-eth']  
            
            #===============GLOBAL LOG LIKELIHOOD=======================
            LogL = sum( logl for logl,uselike in likedict.itervalues() if uselike )
            return LogL, likedict
            
        #===ASSIGN GLOBAL LIKELIHOOD FUNCTION TO ATTRIBUTE==============
        #------(so that it can be used by PySUSY)-----------------------
        self.globlikefunc = globlikefunc
            

        
        
