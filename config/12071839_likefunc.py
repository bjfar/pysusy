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

#========Likelihood parameters that are liable to change================
#and so are nice to have readily accesible for quick alterations

#the following are from 1207.1839
#pairs contain central value (or limit) and uncertainty.

b2sg =  [3.55e4, np.sqrt(0.256**2 + 0.21**2)*1e4]                       #b -> s a
b2mumu =[4.5e-9, 4.5e-9 * 0.14]                                         #b -> mu+ mu-
mh =    [125.3,  np.sqrt(0.6**2 + 1.1**2)]                              #lightest higgs mass


#==========================================================
# Custom likelihood functions and function generators (larger than 1 liners)
#==========================================================
def squarklikefunc(smassIN,nmassIN):    #common likelihood function for remaining squarks
        smass = np.abs(smassIN)
        nmass = np.abs(nmassIN)
        return LFs.logsteplower(x=smass, limit=97 if smass-nmass>10 else 44)

#no fancy LEP limit stuff here

#Xenon limit unused, but left in unenforced for reference
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
        
        #===============================================================
        #---relic density-----------------------------------------------
        if centralreliclimit==True:
            omegalikefunc=LFs.lognormallike                        #(assumes neutralino relic density = dark matter relic density)
        else:
            omegalikefunc=LFs.logerfupper                          #(assumes neutralino relic density < dark matter relic density)
        
        #--proton-neutralino SI cross-section---------------------------
        xenonlikefunc = xenon100likefunc(obslimitcurve,exp1sigmacurve,minmX,maxmX) #(XENON likelihood contribution)

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
           
            #NO HDECAY STUFF IN HERE
            #if useHDecay:     decadict = obsdict['decay']
            
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
                likedict['bsgmo'] = (LFs.lognormallike(x=flavdict['bsgmo'], mean=b2sg[0], sigma=b2sg[1]), True)

                # BF(Bs -> mu+mu-) - USING SUPERISO VALUE FOR LIKELIHOOD. Micromegas value recorded for comparison
                #likedict['bmumu'] = (Bsmumulikefunc(flavdict['bmumu']), True)  #previous fancy version, using simplified likelihood for now
                likedict['bmumu'] = (LFs.logerfupper(x=flavdict['bmumu'], limit=b2mumu[0], sigma=b2sg[1]), True)
                
                #might as well leave the other limits in unenforced
                
                # BF(B_u -> tau nu) / BF(B_u -> tau nu)_SM 
                # ButaunuButaunuSM = MultiIndexObservable(setupobjects[LOWENERGYfile],LOWENERGYblock,(521,2,0,2,-15,16),
                #        average=1.28, sigma=0.38,likefunc=LFs.lognormallike)
                #    #copying 1107.1715, need to find proper source.
                    
                #REPLACING THE ABOVE RATIO, it is more straightforward to impose constraints directly on the branching ratio itself
                #BF(B_u -> tau nu) 
                likedict['Butaunu'] = (LFs.lognormallike(x=flavdict['Butaunu'], mean=1.67e-4, sigma=0.39e-4), False)
                                                                        #Heavy Flavour Averaging Group (HFAG)
                                                                        #1010.1589v3 (updated 6 Sep 2011), retrieved 12 Oct 2011
                                                                        #Table 127, pg 180
                # Delta0(B->K* gamma) (hope this is the same as Delta0-, seems like it might be)
                # (isospin asymmetry)
                likedict['Delta0'] = (LFs.lognormallike(x=flavdict['Delta0'], mean=0.029, sigma=sqrt(0.029**2+0.019**2+0.018**2)), False)
                                                                        # BaBAR, 2008 - 0808.1915, pg 17. No theory error included, pieces are different aspects of experimental error.
                # BR(B+->D0 tau nu)/BR(B+-> D0 e nu)
                likedict['BDtaunuBDenu'] = (LFs.lognormallike(x=flavdict['BDtaunuBDenu'], mean=0.416, sigma=0.128), False)
                                                                        # BaBAR, 2008 - 0709.1698, pg 7, Table 1 (R value). No theory error included.
                # R_l23: involves helicity suppressed K_l2 decays. Equals 1 in SM.
                likedict['Rl23'] = (LFs.lognormallike(x=flavdict['Rl23'], mean=1.004, sigma=0.007), False)
                                                                        # FlaviaNet Working Group on Kaon Decays
                                                                        # 0801.1817v1, pg 29, Eq. 4.19. No theory error included (meaning SuperISO error, as for other observables)
                # BR(D_s->tau nu)
                likedict['Dstaunu'] = (LFs.lognormallike(x=flavdict['Dstaunu'], mean=0.0538, sigma=sqrt((0.0032)**2+(0.002)**2)), False)
                                                                        #Heavy Flavour Averaging Group (HFAG)
                                                                        #1010.1589v3 (updated 6 Sep 2011), retrieved 12 Oct 2011
                                                                        #Figure 68, pg 225. Theory error stolen from 1107.1715, need to find proper source. 
                # BR(D_s->mu nu)
                likedict['Dsmunu'] = (LFs.lognormallike(x=flavdict['Dsmunu'], mean=0.00581, sigma=sqrt((0.00043)**2+(0.0002)**2)), False)
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
            #likedict['Mh0'] = (LFs.logerflower(x=mhiggs, limit=higgslimitfunc(specdict['alpha'],specdict['tanbQ'],mHlimitcurve), sigma=3), useHiggs)
            
            #now using LHC measured higgs mass
            #NOTE! SET TO TRUE! IGNORES WHATEVER IS SPECIFIED IN CONFIG FILE!
            likedict['Mh0'] = (LFs.lognormallike(x=mhiggs, mean=mh[0], sigma=mh[1]), True)
            
            #No fancy HDecay stuff in here.
            
            #===============GLOBAL LOG LIKELIHOOD=======================
            LogL = sum( logl for logl,uselike in likedict.itervalues() if uselike )
            return LogL, likedict
            
        #===ASSIGN GLOBAL LIKELIHOOD FUNCTION TO ATTRIBUTE==============
        #------(so that it can be used by PySUSY)-----------------------
        self.globlikefunc = globlikefunc
            

        
        
