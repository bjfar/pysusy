# File: NMSSM.py
# Author: Ben Farmer
# Date: 1 Feb 2013

# Summary:

# This is designed off CMSSM.py, it is not yet finished!

# ADDING SECOND CONFIGURATION LAYER!!!
# There is now a file X.cfg (supplied at command line) which contains 
# simple options for configuring what this file sets up for pysusy.
# Options include:
# - spectrum generator selection
# - choice of turning programs off
# - choice of turning off/choosing some parts of likelihood function
# - choice of linear/log priors on M0/M12 (rest are always flat)
# - CHOICE OF PARAMETER GENERATOR! Can switch from multinest to LIST mode,
# for which a file must be supplied and the columns containing the parameters
# to be extract specified.

# mSUGRA/CMSSM (SLHA MSSM model 1)
#----mSUGRA params-------
# sgn(mu) = as in template file
# log/flat priors on M0,M12
# flat priors on A0,tanB
#----SM params--------
# gaussian priors on Mtop
# All other params set to central values (either by template file or
# parameter generator internal hardcoded values (ISAJET))
#----Likelihood function notes------
# dark matter likefunc = central limit/upper limit
# higgs mass likefunc optional
# direct detection limits optional


"""MASTER SETUP SCRIPT

This is the setup script for input into the main pysusy executable. It
imports and runs each of the sub-setup scripts which define the parameters,
priors, observables, scan parameters etc. By splitting the configuration
in this way it is easier to see which general aspects of various jobs are 
the same and which are different, and then one can inspect the sub-setup
scripts for the details of those differences. One thus does not have to
search a single giant configuration file for minor changes between jobs.

For the sake of documentation, record here the list of programs that are to be
setup for running by pysusy:

PARAMETER GENERATOR:        Multinest v2.17
SPECTRUM GENERATOR:         NMSSMTools_3.2.3 (nmspec, nmhdecay)
OBSERVABLES:                NMSSMTools_3.2.3
"""

#from config.general_likefunc import LikeFuncCalculator                 #MSSM likelihood function calculator. Now the module to import is specified in the config file.
import common.priors as priors                                          #unit hypercube to prior maps
from pyscanner.common.extra import BadModelPointError                   #PyScanner special error
import ConfigParser  
import os
import sys
import time

# Extra method for the ConfigParser class. Checks the validity of a 
# value required to be a tuple of length 2.
def get2tuple(self,section,option):
    value = eval(self.get(section,option))
    msg = 'Value {0} in section {1} in config file must be a tuple of \
length 2 containing only floats or ints'.format(option,section)
    if type(value)!=tuple:
        raise ConfigParser.Error(msg)
    if len(value)!=2:
        raise ConfigParser.Error(msg)
    for val in value:
        if (type(val)!=float and type(val)!=int):
            raise ConfigParser.Error(msg)
    return value
    
#Add extra method to ConfigParser class
ConfigParser.RawConfigParser.get2tuple = get2tuple
        
class Master():
    """Container class for the functions to be passed to PyScanner"""
    
    def __init__(self,mpi,configpars):
        """Set up objects and options for likelihood function and prior
        Args:
        mpi -- mpi objects [comm, rank, size]. We really need only rank 
            here; the unique mpi id number given to this process. Need
            this to uniquely name input/output files to prevent
            collisions.
        configpars -- list of extra arguments received from
            command line (during launch of PySUSY3). Must contain:
            0 -- 'configfile'
            1 -- 'tmpdir'
            
        Attributes that must be set (used by PySUSY3):
        self.scanargs -- dictionary of arguments to feed to PyScanner.Scan.
            Must contain:
            sampler -- 
            sampleroptions -- 
            prior -- 
            parorder -- 
            likefunc --
            May also contain:
            maxtestattempts -- sent to pyscanner, controls number of attempts
                allowed for likelihood function test run.
        """
        self.printing = False
        self.scanargs = {}
        
        #----------Extract arguments------------------------------------
        comm, rank, size = mpi                  #get mpi object
        try:
            configfile = configpars[0]
        except IndexError, err:
            msg = '{0}: No configuration file specified. \
(no command line arguments received from PySUSY)'.format(err)
            raise IndexError(msg)
        try:
            tmpdir = configpars[1]
        except IndexError, err:
            msg = '{0}: No temporary directory specified. \
(no command line argument received from PySUSY)'.format(err)
            raise IndexError(msg)
        #----------Read config file-------------------------------------
        cfg = ConfigParser.RawConfigParser()

        #set default values
        #pysusyroot = '/home/565/bff565/projects/pysusyMSSM/pysusy3'
        pysusyroot = os.getcwd() #Assumes script was run from pysusy root! 
                                 #Might cause badness for queued jobs.
        defconfig = pysusyroot+'/config/general_defaultsNMSSM.cfg'
        print 'Reading default config file {0}'.format(defconfig)
        cfg.readfp(open(defconfig))   #before reading the real config file, read 
        #in the defaults (just sets some boring parameters not likely to change)
        print 'Reading config file {0}'.format(configfile)
        cfg.readfp(open(configfile))
        #cfg.read(configfile)  #Don't use this way, will not throw an error if
                               #requested file is not found.
        
        #============Import likelihood function=========================
        """module must contain a class 'LikeFuncCalculator' which takes
        the config file as an argument and has a method 'globlikefunc'
        which takes the observables dictionary as an argument and
        returns LogL and a dictionary of likelihood component values, 
        i.e. the call "LogL, likedict = LFCalc.globlikefunc(obsdict)"
        is made later in this script"""
        
        #get the module name to import from the config file
        LFmodname = cfg.get('likefunc', 'modulename')  
        __import__(LFmodname)                 #import module
        LFmod = sys.modules[LFmodname]        #assign module the name 'LFmod'
        
        #============Set up parameter generator=========================
        # get parameters tio cluster (need this now to set ncdims)
        tmp = cfg.get('prioroptions','clusterpars')
        if tmp=='all':
           clusterpars = 'all'
        else:
           clusterpars = [w.strip() for w in tmp.split(',')] 
        
        if cfg.getboolean('list','listmode')==False:
            multinest_options = {
            'p_is' : 1,         #use importance sampling?
            'p_mmodal' : 1,     #whether to do multimodal sampling
            'p_ceff' : 0,       #sample with constant efficiency
            'p_nlive' : cfg.getint('sampleroptions', 'nlive'),  
                                #No. of live points to use
            'p_tol' : cfg.getfloat('sampleroptions', 'tol'),                    
                                #evidence tolerance factor (controls allowed 
#error in evidence, scan stops faster if this tolerance is higher. Use 1e-4 for 
#detailed likelihood function mapping)
            'p_efr' : cfg.getfloat('sampleroptions', 'efr'),                    
                                #enlargement factor reduction parameter (I set
#this really low to tell the code to relax the bounding ellipsoids, to help 
#avoid missing points. I think this is what should happen anyway)
            'p_maxmodes' : cfg.getint('sampleroptions', 'maxmodes'),            
                                #max modes expected, for memory allocation
            'p_updint' : cfg.getint('sampleroptions', 'updint'),                
                                #no. of iterations after which the ouput files 
                                #should be updated
            'p_nullz' : -1e90,  #null evidence (set it to very high negative no.
                                #if null evidence is unknown)
            'p_seed' : -1,      #seed for nested sampler, -ve means take it from
                                #sys clock
            #bjf> not sure what this is supposed to be > #p_pwrap(4)   
              #parameters to wrap around (0 is F & non-zero T)
            'p_feedback' : 0,   #feedback on the sampling progress?     
            'p_resume' : 1,     #whether to resume from a previous run
            'p_outfile' : 1,    #write output files?
            'p_initmpi' : 0,    #initialize MPI routines?, relevant only if 
#compiling with MPI. Set it to F if you want your main program to handle MPI 
#initialization
            'p_logzero' : -1e90,#points with loglike < logZero will be ignored 
                                #by MultiNest
            'p_context' : 0,    #dummy integer for the C interface (not really 
                                #sure what this does...)
            }
            
            if clusterpars!='all': multinest_options['p_ncdims'] = len(clusterpars) #no. of parameters to cluster (for mode detection)
            # else we want all parameters clustered, which is the default option!
            # so don't add this option in this case.
            self.scanargs['sampler'] = 'multinest'
            self.scanargs['sampleroptions'] = multinest_options
        #---------------List mode setup---------------------------------
        
        # The input list file may have all manner of stuff in it, we need to 
        # tell the parameter generator which columns correspond to the scan 
        # parameters. To do this we generate a dictionary, where the keys
        # match the names of the parameters defined in 'parameterlist' and the 
        # values are the columns of the input file in which they can be found. 
        # If the list is previous pysusy output then the corresponding .info 
        # file specifies the contents of each column.
        if cfg.getboolean('list','listmode'):
            raise Exception("NOTE TO SELF! HAVE NOT ENABLED LIST MODE PROPERLY FOR NMSSM YET!")
            coldict = {
               'M0'    : cfg.getint('list','M0'),
               'M12'   : cfg.getint('list','M12'),
               'TanB'  : cfg.getint('list','TanB'),
               'A0'    : cfg.getint('list','A0'),
               'lambda': cfg.getint('list','lambda'),
               'Akappa': cfg.getint('list','Akappa'),
               'Mtop'  : cfg.getint('list','MTop'),
               }
     
            listrun_options = {         #(keyword arguments to be fed directly to listwrapper function)
               'inputfile' : cfg.get('list','inputlist'),        #the location and name of the input data array file to be used as the template for the scan.
               'coldict'   : coldict          #the dictionary specifying which columns of 'inputfile' correspond to which model parameters.
               }                              #should be generated to match the settings in parameter setup module.   
            self.scanargs['sampler'] = 'list'
            self.scanargs['sampleroptions'] = listrun_options
        
        #==========PROGRAM AND FILE SETUP===============================
        
        #-------Check in config file which programs we need-------------
        #self.useSuperISO    = cfg.getboolean('progoptions', 'useSuperISO')
        #self.usemicrOmegas  = cfg.getboolean('progoptions', 'usemicrOmegas')
        #self.useHDecay      = cfg.getboolean('progoptions', 'useHDecay')
        
        #----------Import programs wrappers-----------------------------
        #---------(based on options in config file)---------------------
        from wrappers.nmspecf2py import NMspec                 
                    
        ftemplate = cfg.get('prioroptions','templatefile')
        
        #---------Set up temporary directory and input/output files-----
        fspectrumin =   '{0}/spectrumin-{1}.slha'.format(tmpdir,rank)
        fspectrumout =  '{0}/spectrumout-{1}.slha'.format(tmpdir,rank)
        fdarkmatterout ='{0}/darkmatterout-{1}.slha'.format(tmpdir,rank)
        fdecayout =     '{0}/decayout-{1}.slha'.format(tmpdir,rank)
        ftuningout =    '{0}/tuningout-{1}.slha'.format(tmpdir,rank)      
 
        #---------Initialise program wrappers---------------------------
        # Get nmspec running options from config file
        boolrelic = cfg.getboolean('progoptions','computerelic')
        booldirdet = cfg.getboolean('progoptions','computedirdet')
        boolindirdet = cfg.getboolean('progoptions','computeindirdet')
        # Call micrOmegas (default 0=no, 1=relic density only,
		#		  2=dir. det. rate, 3=indir. det. rate, 4=both det. rates)
        nmspecoptions = {}
        if booldirdet and boolindirdet:
            print "micrOmegas IS running: relic density, direct, and indirect \
detection rates will be computed"
            nmspecoptions['usemicromegas'] = 4
        elif boolindirdet:
            print "micrOmegas IS running: relic density and indirect \
detection rates will be computed"
            nmspecoptions['usemicromegas'] = 3
        elif booldirdet: 
            print "micrOmegas IS running: relic density and direct \
detection rates will be computed"
            nmspecoptions['usemicromegas'] = 2
        elif boolrelic:
            print "micrOmegas IS running: relic density only will be computed"
            nmspecoptions['usemicromegas'] = 1
        else:
            print "micrOmegas IS NOT running"
            nmspecoptions['usemicromegas'] = 0
        
        # Extra flag for deciding whether to skip bad omega points
	checkomega = cfg.getboolean('progoptions','checkbadomega')

        # Initialise nmspec wrapper object
        # -> now moved to after prior setup since we need to initialise the
        # wrapper differently depending on the model chosen.

        #==========PRIOR SETUP==========================================
        
        def orderpars(clusterpars,allpars):
            """Arrange parameters into order requested by user clustering
               specification"""
            if clusterpars=="all":
               #Clustering on ALL parameters, order unimportant
               return allpars

            if len(clusterpars)>len(allpars): 
              raise ValueError("Invalid parameters \
specified in config file 'clusterpars' field, (in 'prioroptions'). Number of \
parameters listed exceeds number of parameters being scanned!")
            for par in clusterpars:
              if par not in allpars: raise ValueError("Invalid parameter \
specified in config file 'clusterpars' field, (in 'prioroptions'). For CNMSSM \
allowed names are {0}.".format(allpars)) 
            reorderedpars = clusterpars[:]
            for par in allpars:
              if par not in clusterpars: reorderedpars+=[par]
            return reorderedpars

        #----------Generate prior mapping function----------------------
        #Can skip the section below if we are running in list mode
        if cfg.getboolean('list','listmode')==False:
            #Check which model is in use and set options appropriately
            def setupCNMSSM():
                # 'whichcode' is used to initialise the nmspec wrapper. 
                # Determines whether nmspec or nmhdecay is used to generate 
                # spectrum.
                self.whichcode = 'mSUGRA' #->nmspec
                
                print "Setting up prior for CNMSSM..."
                #parameter/prior scan settings set here:
                uselog = cfg.getboolean('prioroptions','uselog')
                massprior = priors.logprior if uselog else priors.linear
                
                #get ranges for scan (must be tuples of length 2, i.e. (min,max))
                M0range = cfg.get2tuple('prioroptions','M0range')
                M12range = cfg.get2tuple('prioroptions','M12range')
                TanBrange = cfg.get2tuple('prioroptions','TanBrange')
                A0range = cfg.get2tuple('prioroptions','A0range')
                lambdarange = cfg.get2tuple('prioroptions','lambdarange')
                #nuis par tuple values interpreted as mean and std of gaussian prior
                Mtopmeanstd = cfg.get2tuple('prioroptions','Mtopmeanstd') 
                 
                priorslist = [  ('M0',   massprior(*M0range)),
                                ('M12',  massprior(*M12range)),
                                ('TanB', priors.linear(*TanBrange)),
                                ('A0',   priors.linear(*A0range)),
                                ('lambda', priors.linear(*lambdarange)),
                                ('Mtop', priors.gaussian(*Mtopmeanstd)),   
                            ]
                            
                def CNMSSMparlinks(paramvector):
                    # No extra parameter links to add, just copies paramvector
                    # into inputvector. See NMSSM10 for example of what this
                    # feature can be used for.
                    # paramvector - dictionary of scan parameter values,
                    # transformed by self.prior (from pyscanner, sent via
                    # likelihood function defined below)
                    
                    p = paramvector
                    try:
                        i = self.inputvector
                    except AttributeError:
                        # if we haven't yet, need to create the inputvector dict
                        self.inputvector = p.copy()
                        i = self.inputvector
                        
                    # copy all the new values from p to i, except for 's'
                    # because it doesn't exist in i.
                    for key, val in p.items():
                        i[key] = val
                    
                    return i
                    
                self.addlinks = CNMSSMparlinks # called by likelihood function
                
                #=================SET PRIOR=================================
                #----------(to be used by PyScanner)---------------------------
                self.scanargs['prior'] = priors.genindepprior(priorslist)     
                #self.scanargs['parorder'] = ['A0','lambda','M0','M12','TanB','Mtop'] 
                
                # Parse parameters to cluster from config file
                allpars = ['M0','M12','TanB','A0','lambda','Mtop']
                self.scanargs['parorder'] = orderpars(clusterpars,allpars)
                
                #END CNMSSM SETTINGS
            
            def setupCNMSSMAk():
                """Same as CNMSSM, but with Akappa GUT unification broken, i.e.
                Akappa is scanned independently"""
                # 'whichcode' is used to initialise the nmspec wrapper. 
                # Determines whether nmspec or nmhdecay is used to generate 
                # spectrum.
                self.whichcode = 'mSUGRA' #->nmspec
                
                print "Setting up prior for CNMSSMAk..."
                #parameter/prior scan settings set here:
                uselog = cfg.getboolean('prioroptions','uselog')
                massprior = priors.logprior if uselog else priors.linear
                
                #get ranges for scan (must be tuples of length 2, i.e. (min,max))
                M0range = cfg.get2tuple('prioroptions','M0range')
                M12range = cfg.get2tuple('prioroptions','M12range')
                TanBrange = cfg.get2tuple('prioroptions','TanBrange')
                A0range = cfg.get2tuple('prioroptions','A0range')
                Akapparange = cfg.get2tuple('prioroptions','Akapparange')
                lambdarange = cfg.get2tuple('prioroptions','lambdarange')
                #nuis par tuple values interpreted as mean and std of gaussian prior
                Mtopmeanstd = cfg.get2tuple('prioroptions','Mtopmeanstd') 
                 
                priorslist = [  ('M0',   massprior(*M0range)),
                                ('M12',  massprior(*M12range)),
                                ('TanB', priors.linear(*TanBrange)),
                                ('A0',   priors.linear(*A0range)),
                                ('Akappa', priors.linear(*Akapparange)),
                                ('lambda', priors.linear(*lambdarange)),
                                ('Mtop', priors.gaussian(*Mtopmeanstd)),   
                            ]
                            
                def CNMSSMAkparlinks(paramvector):
                    # No extra parameter links to add, just copies paramvector
                    # into inputvector. See NMSSM10 for example of what this
                    # feature can be used for.
                    # paramvector - dictionary of scan parameter values,
                    # transformed by self.prior (from pyscanner, sent via
                    # likelihood function defined below)
                    
                    p = paramvector
                    try:
                        i = self.inputvector
                    except AttributeError:
                        # if we haven't yet, need to create the inputvector dict
                        self.inputvector = p.copy()
                        i = self.inputvector
                        
                    # copy all the new values from p to i, except for 's'
                    # because it doesn't exist in i.
                    for key, val in p.items():
                        i[key] = val
                    
                    return i
                    
                self.addlinks = CNMSSMAkparlinks # called by likelihood function
                
                #=================SET PRIOR=================================
                #----------(to be used by PyScanner)---------------------------
                self.scanargs['prior'] = priors.genindepprior(priorslist)     

                # Parse parameters to cluster from config file
                allpars = ['M0','M12','TanB','A0','Akappa','lambda','Mtop']
                self.scanargs['parorder'] = orderpars(clusterpars,allpars)
                
                #END CNMSSMAk SETTINGS
            
            def setupNMSSM9():
                # 'whichcode' is used to initialise the nmspec wrapper. 
                # Determines whether nmspec or nmhdecay is used to generate 
                # spectrum.
                self.whichcode = 'generalNMSSM' #->nmhdecay
                
                print "Setting up prior for NMSSM9..."
                #parameter/prior scan settings set here:
                uselog = cfg.getboolean('prioroptions','uselog')
                massprior = priors.logprior if uselog else priors.linear
                #mass2prior = priors.logprior if uselog else None
                #parameters: MTOP TANB M2 ML3=ME3=MD3 MQ3 MU3
                #LAMBDA KAPPA MHD^2 MHD^2 
                #get ranges for scan (must be tuples of length 2, i.e. (min,max))
                M2range = cfg.get2tuple('prioroptions','M2range')
                MD3range = cfg.get2tuple('prioroptions','MD3range')
                MQ3range = cfg.get2tuple('prioroptions','MQ3range')
                MU3range = cfg.get2tuple('prioroptions','MU3range')
                #MHU2range = cfg.get2tuple('prioroptions','MHU^2range')
                #MHD2range = cfg.get2tuple('prioroptions','MHD^2range')
                TanBrange = cfg.get2tuple('prioroptions','TanBrange')
                AU3range = cfg.get2tuple('prioroptions','AU3range')
                lambdarange = cfg.get2tuple('prioroptions','lambdarange')
                # Can't seem to get nmhdecay to take MHU2 and MHD2 as input,
                # switching to kappa and s instead.
                kapparange = cfg.get2tuple('prioroptions','kapparange')
                srange = cfg.get2tuple('prioroptions','srange')
                #nuis par tuple values interpreted as mean and std of gaussian prior
                Mtopmeanstd = cfg.get2tuple('prioroptions','Mtopmeanstd') 
                
                
                
                priorslist = [  ('M2',   massprior(*M2range)),
                                ('MD3',  massprior(*MD3range)),                              
                                ('MQ3',  massprior(*MQ3range)),
                                ('MU3',  massprior(*MU3range)),
                                #('MHU^2', mass2prior(*MHU2range)),
                                #('MHD^2', mass2prior(*MHD2range)),
                                ('TanB', priors.linear(*TanBrange)),
                                ('AU3',  priors.linear(*AU3range)),
                                ('lambda', priors.linear(*lambdarange)),
                                ('kappa', priors.linear(*kapparange)),
                                ('s', priors.linear(*srange)),
                                ('Mtop', priors.gaussian(*Mtopmeanstd)),   
                            ]
                # First and second generation sfermions all set to high masses 
                # in template file.
                # Trilinears (except AU3=AU2=AU1) all set to zero
                # We set ML3=ME3=MD3 manually below
                
                # nmhdecay then sets 
                #  MD3=MD2=MD1,
                #  ME3=ME2=ME1 and
                #  ML3=ML2=ML1.
                # also
                #  MQ3=MQ2=MQ1
                #  MU3=MU2=MU1
                #  AU3=AU2=AU1
                                                                
                # Extra links between SLHA input parameters
                def NMSSM9parlinks(paramvector):
                    # Need to link the scanned parameters to the ones actually
                    # written to the nmspec input template file. In this case we
                    # actually only need to add a couple of extra ones and set
                    # them equal to MD3.
                    # paramvector - dictionary of scan parameter values,
                    # transformed by self.prior (from pyscanner, sent via
                    # likelihood function defined below)
                    
                    p = paramvector
                    try:
                        i = self.inputvector
                    except AttributeError:
                        # if we haven't yet, need to create the inputvector dict
                        self.inputvector = p.copy()
                        i = self.inputvector
                        del i['s']  #this parameter is scanned only, doesn't
                                    #exist in nmspec SLHA input file. Is
                                    #transformed to mueff.
                    # copy all the new values from p to i, except for 's'
                    # because it doesn't exist in i.
                    for key, val in p.items():
                        if key!='s': i[key] = val
                    # MD3 links
                    i['ML3'] = p['MD3'] # nmspec then sets ML3=ML2=ML1 by default
                    i['ME3'] = p['MD3'] # nmspec then sets ME3=ME2=ME1 by default
                    
                    # scanning s (singlet vev) but nmhdecay wants mu_eff as input
                    i['mueff'] = p['lambda']*p['s']
  
                    return i
                    
                self.addlinks = NMSSM9parlinks # called by likelihood function
                
                # New feature: specify a valid set of parameters to use which
                # will generate the full set of observables to be recorded. Will
                # speed up the 'testing' loop of pyscanner.
                #self.testvals = {'M2':,'MD3':,'MQ3':,'MU3':,'MHU^2':,
                #  'MHD^2':,'TanB':,'AU3':,'lambda':,'Mtop':]
                #=================SET PRIOR=================================
                #----------(to be used by PyScanner)---------------------------
                self.scanargs['prior'] = priors.genindepprior(priorslist)     
                
                # Parse parameters to cluster from config file
                allpars = ['M2','s','MD3','MQ3','MU3','TanB',\
                'AU3','lambda','Mtop','kappa']#'MHU^2','MHD^2',]
                self.scanargs['parorder'] = orderpars(clusterpars,allpars)
                
                #END NMSSM9 SETTINGS
            
            def setupNMSSM11():
                """Same as NMSSM9, but also varying Alambda and Akappa"""
                # 'whichcode' is used to initialise the nmspec wrapper. 
                # Determines whether nmspec or nmhdecay is used to generate 
                # spectrum.
                self.whichcode = 'generalNMSSM' #->nmhdecay
                
                print "Setting up prior for NMSSM11..."
                #parameter/prior scan settings set here:
                uselog = cfg.getboolean('prioroptions','uselog')
                massprior = priors.logprior if uselog else priors.linear
                #mass2prior = priors.logprior if uselog else None
                #parameters: MTOP TANB M2 ML3=ME3=MD3 MQ3 MU3
                #LAMBDA KAPPA MHD^2 MHD^2 
                #get ranges for scan (must be tuples of length 2, i.e. (min,max))
                M2range = cfg.get2tuple('prioroptions','M2range')
                MD3range = cfg.get2tuple('prioroptions','MD3range')
                MQ3range = cfg.get2tuple('prioroptions','MQ3range')
                MU3range = cfg.get2tuple('prioroptions','MU3range')
                TanBrange = cfg.get2tuple('prioroptions','TanBrange')
                AU3range = cfg.get2tuple('prioroptions','AU3range')
                Alambdarange = cfg.get2tuple('prioroptions','Alambdarange')
                Akapparange = cfg.get2tuple('prioroptions','Akapparange')
                lambdarange = cfg.get2tuple('prioroptions','lambdarange')
                kapparange = cfg.get2tuple('prioroptions','kapparange')
                srange = cfg.get2tuple('prioroptions','srange')
                #nuis par tuple values interpreted as mean and std of gaussian prior
                Mtopmeanstd = cfg.get2tuple('prioroptions','Mtopmeanstd') 
                
                
                
                priorslist = [  ('M2',   massprior(*M2range)),
                                ('MD3',  massprior(*MD3range)),                              
                                ('MQ3',  massprior(*MQ3range)),
                                ('MU3',  massprior(*MU3range)),
                                ('TanB', priors.linear(*TanBrange)),
                                ('AU3',  priors.linear(*AU3range)),
                                ('lambda', priors.linear(*lambdarange)),
                                ('kappa', priors.linear(*kapparange)),
                                ('Alambda', priors.linear(*Alambdarange)),
                                ('Akappa', priors.linear(*Akapparange)),
                                ('s', priors.linear(*srange)),
                                ('Mtop', priors.gaussian(*Mtopmeanstd)),   
                            ]
                # First and second generation sfermions all set to high masses 
                # in template file.
                # Trilinears (except AU3=AU2=AU1, Alambda, Akappa) all set to zero
                # We set ML3=ME3=MD3 manually below
                
                # nmhdecay then sets 
                #  MD3=MD2=MD1,
                #  ME3=ME2=ME1 and
                #  ML3=ML2=ML1.
                # also
                #  MQ3=MQ2=MQ1
                #  MU3=MU2=MU1
                #  AU3=AU2=AU1
                                                                
                # Extra links between SLHA input parameters
                def NMSSM11parlinks(paramvector):
                    # Need to link the scanned parameters to the ones actually
                    # written to the nmspec input template file. In this case we
                    # actually only need to add a couple of extra ones and set
                    # them equal to MD3.
                    # paramvector - dictionary of scan parameter values,
                    # transformed by self.prior (from pyscanner, sent via
                    # likelihood function defined below)
                    
                    p = paramvector
                    try:
                        i = self.inputvector
                    except AttributeError:
                        # if we haven't yet, need to create the inputvector dict
                        self.inputvector = p.copy()
                        i = self.inputvector
                        del i['s']  #this parameter is scanned only, doesn't
                                    #exist in nmspec SLHA input file. Is
                                    #transformed to mueff.
                    # copy all the new values from p to i, except for 's'
                    # because it doesn't exist in i.
                    for key, val in p.items():
                        if key!='s': i[key] = val
                    # MD3 links
                    i['ML3'] = p['MD3'] # nmspec then sets ML3=ML2=ML1 by default
                    i['ME3'] = p['MD3'] # nmspec then sets ME3=ME2=ME1 by default
                    
                    # scanning s (singlet vev) but nmhdecay wants mu_eff as input
                    i['mueff'] = p['lambda']*p['s']
  
                    return i
                    
                self.addlinks = NMSSM11parlinks # called by likelihood function
                
                # New feature: specify a valid set of parameters to use which
                # will generate the full set of observables to be recorded. Will
                # speed up the 'testing' loop of pyscanner.
                #self.testvals = {'M2':,'MD3':,'MQ3':,'MU3':,'MHU^2':,
                #  'MHD^2':,'TanB':,'AU3':,'lambda':,'Mtop':]
                #=================SET PRIOR=================================
                #----------(to be used by PyScanner)---------------------------
                self.scanargs['prior'] = priors.genindepprior(priorslist)     
                
                # Parse parameters to cluster from config file
                allpars = ['M2','s','MD3','MQ3','MU3','TanB',\
                'AU3','lambda','kappa','Alambda','Akappa','Mtop']
                self.scanargs['parorder'] = orderpars(clusterpars,allpars)

                #END NMSSM11 SETTINGS
            
            # Dictionary to select which model to set up (functions like a case
            # or switch statement)
            casedict = { 'CNMSSM':   setupCNMSSM,
                         'CNMSSMAk': setupCNMSSMAk,
                         'NMSSM9':   setupNMSSM9,
                         'NMSSM11':  setupNMSSM11,
                       }
            # Run the appropriate prior setup as chosen in the config file
            model = cfg.get('prioroptions','model')
            try:
                casedict[model]()   # Runs the selected setup function
            except KeyError as err:
                msg = "{0} -- ERROR! Model chosen in config file (prioroptions: \
model) is not implemented. Please check the name is correct (only CNMSSM, \
CNMSSMAk, NMSSM9 and NMSSM11 are currently valid".format(err.message)
                raise KeyError(msg)
                
            # NOW initialise nmspec/nmhdecay wrapper object
            nmspec = NMspec(infile = fspectrumin, 
                            specout = fspectrumout,
                            omegaout = fdarkmatterout,
                            decayout = fdecayout,
                            tunout = ftuningout, 
                            template = ftemplate,
                            options = nmspecoptions,
                            workdir = pysusyroot+'/wrappers',
                            model = self.whichcode)
        #==========LIKELIHOOD FUNCTION SETUP============================
    
        #----------Initialise likelihood calculator---------------------
        #...according to options set in configfiles
        LFCalc = LFmod.LikeFuncCalculator(configfile,defconfig)
        
        if self.whichcode=='generalNMSSM': self.code = 'nmhdecay' 
        if self.whichcode=='mSUGRA': self.code = 'nmspec' 
        
        #----------Define function to perform likelihood calculation----
        def pyscannerlikefunc(paramvector):
            """Main likelihood function calculator
            Passed AS IS to PyScanner via PySUSY
            Args:
            paramvector -- dictionary of (input parameter, value) pairs,
                with values generated uniformly in a unit hypercube by 
                the parameter generator, and mapped to the physical 
                parameter space according to 'self.Prior'.
            Output:
            LogL -- global log-likelihood value for point specified by 
                paramvector.
            obsdict -- dictionary containing a dictionary of 
                observables for by each program in the run sequence.
            likedict -- dictionary of loglikelihood function components.
                        (tuples containing (LogL, uselike), where
                        uselike is True or False and specifies whether
                        the LogL value formed part of the global LogL.
            timing -- dictionary of timing information to be recorded
            """
            
            #----------Run codes and collect observables----------------
            obsdict = {}        #reset observable storage dictionary
            timing = []         #reset timing storage list
            ti = time.time()    #initialise ti
            
            # Add extra linkages between SLHA input file parameters, and/or
            # other transformations of scanned parameters
            inputvector = self.addlinks(paramvector) 
            if self.printing:
                for key, value in inputvector.items(): 
                    print key,':',value
                print ''
                    
            # Write the new SLHA input file, with values modified according to
            # those in 'paramvector'
            nmspec.writeinput(inputvector)  
            nmspec.run()    #Execute nmspec main function
            errorsQ = nmspec.checkoutput()  #Check if any errors occured
            if errorsQ[0]==1:   # code 1 indicates problem with spectrum output
                raise BadModelPointError('{0}: Problem with spectrum found! \
({1})'.format(self.code,errorsQ[1]))
            
            if checkomega:	# If we aren't driving the scan with omega 
                                # variables it can be handy not to skip
                                # all bad omega points
                if errorsQ[0]==2:   # code 2 indicates problem with spectrum output
                    raise BadModelPointError('{0}: Problem with omega output found! \
({1})'.format(self.code,errorsQ[1]))
                #else continue as normal  
            
            # Add nmspec spectrum observables to obsdict
            obsdict['spectrum'] = nmspec.getspecobs() 
            obsdict['darkmatter'] = nmspec.getomegaobs()
            obsdict['decay'] = nmspec.getdecayobs()
            obsdict['tuning'] = nmspec.gettunobs()
            
            # Compute time since ti and reset ti
            tf = time.time(); timing += [(tf - ti)*1000]; ti = tf       

            if self.printing: 
                for key, value in obsdict['spectrum'].items(): 
                    print key,':',value
                print ''
                for key, value in obsdict['darkmatter'].items(): 
                    print key,':',value
                print ''
                for key, value in obsdict['decay'].items(): 
                    print key,':',value
                print ''
                for key, value in obsdict['tuning'].items(): 
                    print key,':',value
                print 'timing (ms):', timing
        
            #---------Compute likelihoods-------------------------------
            LogL, likedict = LFCalc.globlikefunc(obsdict)
            
            #LogL = -1e300
            #likedict = {}
            #for key, value in likedict.items(): 
            #        print key,':',value

            return LogL, likedict, obsdict, timing
            
        #================SET LIKELIHOOD FUNCTION========================
        #----------------(to be used by PyScanner)-------------------------
        self.scanargs['likefunc'] = pyscannerlikefunc                              
        
        #======Attempts allowed during likelihood function test run=====
        self.scanargs['maxtestattempts'] = cfg.getint('sampleroptions','maxtestattempts')
        
            
