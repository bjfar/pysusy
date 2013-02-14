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
SPECTRUM GENERATOR:         NMSSMTools_3.2.3 (nmspec)
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
        comm, rank, size = mpi                                          #get mpi object
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
        pysusyroot = '/home/565/bff565/projects/pysusyMSSM/pysusy3'
        defconfig = pysusyroot+'/config/general_defaultsNMSSM.cfg'
        print 'Reading default config file {0}'.format(defconfig)
        cfg.readfp(open(defconfig))                                     #before reading the real config file, read in the defaults (in case any new ones are missing from older config files)
        #read config file
        print 'Reading config file {0}'.format(configfile)
        cfg.read(configfile)
        
        #============Import likelihood function=========================
        """module must contain a class 'LikeFuncCalculator' which takes
        the config file as an argument and has a method 'globlikefunc'
        which takes the observables dictionary as an argument and
        returns LogL and a dictionary of likelihood component values, 
        i.e. the call "LogL, likedict = LFCalc.globlikefunc(obsdict)"
        is made later in this script"""
        
        LFmodname = cfg.get('likefunc', 'modulename')                   #get the module name to import from the config file
        __import__(LFmodname)                                           #import module
        LFmod = sys.modules[LFmodname]                                  #assign module the name 'LFmod'
        
        #============Set up parameter generator=========================
        
        if cfg.getboolean('list','listmode')==False:
            multinest_options = {
            'p_mmodal' : 1,                     #whether to do multimodal sampling
            'p_ceff' : 0,                       #sample with constant efficiency
            'p_nlive' : cfg.getint('sampleroptions', 'nlive'),                 #No. of live points to use
            'p_tol' : cfg.getfloat('sampleroptions', 'tol'),                      #evidence tolerance factor (controls allowed error in evidence, scan stops faster if this tolerance is higher. Use 1e-4 for detailed likelihood function mapping)
            'p_efr' : cfg.getfloat('sampleroptions', 'efr'),                      #enlargement factor reduction parameter (I set this really low to tell the code to relax the bounding ellipsoids, to help avoid missing points. I think this is what should happen anyway)
            'p_ncdims' : cfg.getint('sampleroptions', 'ncdims'),                     #no. of parameters to cluster (for mode detection)
            'p_maxmodes' : cfg.getint('sampleroptions', 'maxmodes'),                  #max modes expected, for memory allocation
            'p_updint' : cfg.getint('sampleroptions', 'updint'),                   #no. of iterations after which the ouput files should be updated
            'p_nullz' : -1e90,                  #null evidence (set it to very high negative no. if null evidence is unknown)
            'p_seed' : -1,                      #seed for nested sampler, -ve means take it from sys clock
            #bjf> not sure what this is supposed to be > #p_pwrap(4)                       #parameters to wrap around (0 is F & non-zero T)
            'p_feedback' : 0,                   #feedback on the sampling progress?     
            'p_resume' : 1,                     #whether to resume from a previous run
            'p_outfile' : 1,                     #write output files?
            'p_initmpi' : 0,                    #initialize MPI routines?, relevant only if compiling with MPI
                                               #set it to F if you want your main program to handle MPI initialization
            'p_logzero' : -1e90,                 #points with loglike < logZero will be ignored by MultiNest
            'p_context' : 0,                    #dummy integer for the C interface (not really sure what this does...)
            }
            self.scanargs['sampler'] = 'multinest'
            self.scanargs['sampleroptions'] = multinest_options
        #---------------List mode setup---------------------------------
        
        # The input list file may have all manner of stuff in it, we need to tell the parameter generator
        # which columns correspond to the scan parameters. To do this we generate a dictionary, where the keys
        # match the names of the parameters defined in 'parameterlist' and the values are the columns of the input
        # file in which they can be found. If the list is previous pysusy output then the corresponding .info file
        # specifies the contents of each column.
        if cfg.getboolean('list','listmode'):
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
        
        # Initialise nmspec wrapper object
        nmspec = NMspec(infile = fspectrumin, 
                        specout = fspectrumout,
                        omegaout = fdarkmatterout,
                        decayout = fdecayout, 
                        template = ftemplate,
                        options = nmspecoptions)

        #==========PRIOR SETUP==========================================
        
        #----------Generate prior mapping function----------------------
        #Can skip the section below if we are running in list mode
        if cfg.getboolean('list','listmode')==False:    
            #parameter/prior scan settings set here:
            uselog = cfg.getboolean('prioroptions','uselog')            #whether to use linear or log priors for mass parameters
            massprior = priors.logprior if uselog else priors.linear    #choose the mass parameter prior
            
            #get ranges for scan (must be tuples of length 2, i.e. (min,max))
            M0range = cfg.get2tuple('prioroptions','M0range')
            M12range = cfg.get2tuple('prioroptions','M12range')
            TanBrange = cfg.get2tuple('prioroptions','TanBrange')
            A0range = cfg.get2tuple('prioroptions','A0range')
            lambdarange = cfg.get2tuple('prioroptions','lambdarange')
            Akapparange = cfg.get2tuple('prioroptions','Akapparange')
            #nuis par tuple values interpreted as mean and std of gaussian prior
            Mtopmeanstd = cfg.get2tuple('prioroptions','Mtopmeanstd') 
             
            priorslist = [  ('M0',   massprior(*M0range)),
                            ('M12',  massprior(*M12range)),
                            ('TanB', priors.linear(*TanBrange)),
                            ('A0',   priors.linear(*A0range)),
                            ('lambda', priors.linear(*lambdarange)),
                            ('Akappa', priors.linear(*Akapparange)),
                            ('Mtop', priors.gaussian(*Mtopmeanstd)),   
                        ]
            #=================SET PRIOR=================================
            #----------(to be used by PyScanner)---------------------------
            self.scanargs['prior'] = priors.genindepprior(priorslist)     
            self.scanargs['parorder'] = ['M0','M12','TanB','A0',
                                         'lambda','Akappa','Mtop']      
        
        #==========LIKELIHOOD FUNCTION SETUP============================
    
        #----------Initialise likelihood calculator---------------------
        LFCalc = LFmod.LikeFuncCalculator(configfile)                   #Initialise likelihood calculator object, according to options set in configfile
        
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
            obsdict = {}                                                #reset observable storage dictionary
            timing = []                                                 #reset timing storage list
            ti = time.time()                                            #initialise ti
            
            nmspec.writeinput(paramvector)                              #write the new SLHA input file, with values modified according to those in 'paramvector'
            nmspec.run()                                                #Execute nmspec main function
            errorsQ = nmspec.checkoutput()                              #Check if any errors occured
            if errorsQ[0]==1:   # code 1 indicates problem with spectrum output
                raise BadModelPointError('nmspec: Problem with spectrum found! \
({0})'.format(errorsQ[1]))
            if errorsQ[0]==2:   # code 2 indicates problem with spectrum output
                raise BadModelPointError('nmspec: Problem with omega output found! \
({0})'.format(errorsQ[1]))
            #else continue as normal  
            
            obsdict['spectrum'] = nmspec.getspecobs()                   #add nmspec spectrum observables to obsdict
            obsdict['darkmatter'] = nmspec.getomegaobs()
            obsdict['decay'] = {}      #nmspec.getdecayobs()
            for key, value in obsdict['spectrum'].items(): print key,':',value
            print ''
            for key, value in obsdict['darkmatter'].items(): print key,':',value
                 
            tf = time.time(); timing += [(tf - ti)*1000]; ti = tf       #compute time since ti and reset ti
            
            if self.printing: 
                print obsdict['spectrum']
                #print obsdict['darkmatter']
                #print obsdict['decay']
                print 'timing (ms):', timing
        
            #---------Compute likelihoods-------------------------------
            LogL, likedict = LFCalc.globlikefunc(obsdict)
            
            #LogL = -1e300
            #likedict = {}

            return LogL, likedict, obsdict, timing
            
        #================SET LIKELIHOOD FUNCTION========================
        #----------------(to be used by PyScanner)-------------------------
        self.scanargs['likefunc'] = pyscannerlikefunc                              
        
        #======Attempts allowed during likelihood function test run=====
        self.scanargs['maxtestattempts'] = cfg.getint('sampleroptions','maxtestattempts')
        
            
