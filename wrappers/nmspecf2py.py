"""PyScanner-PySUSY wrapper for nmspec (from NMSSMTools 3.2.3)
This wrapper runs nmspec via an f2py extension module, which wraps the fortran
code. Here we interface that very simple wrapper with PySUSY. (note, nmspec
output format has been modified slightly to turn it into 'block' format: this
partially wrecks the SLHA compatibility).

Ben Farmer, Feb 4 2013

update Feb 22 2013 - Now this is a kind of a 'double' wrapper, wraps both
nmspec and nmhdecay and controls which one of them is called. nmhdecay is used
when soft masses are to be specified at the low scale. Selection is controlled
by the option 'model'.
"""

import nmspec     #requires nmspec f2py extension module
import nmhdecay   #requires nmhdecay f2py extension module
from multiprocessingmod import Process                                     

from common.SLHAfile import SLHAFile, SpectrumFile, OmegaFile                      #PySUSY SLHA file reader classes
from blockmaps.nmspecspectrum import SLHAdict as specdict                #spectrum generator SLHA output translation dictionary
from blockmaps.nmspecomega import blockdict as DMdict                #dark matter SLHA output translation dictionary
from blockmaps.nmspectuning import blockdict as tundict	# Extra 'tuning' information file (added to ftpar.f) translation dictionary (ignores many things atm)

import time
import sys
import os

from silence import Silence                                             #class to silence output of wrapped code

import contextlib
import ConfigParser  

# Simple context manager function for safely changing directory 
@contextlib.contextmanager
def chdir(dirname=None):
    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)    
        
class NMspec:
    def __init__(self,infile,specout,decayout,omegaout,tunout,workdir, \
                    template=None,options={},silenceobjs=None,model='generalNMSSM'):
        """args:
        need to finish list
        model - model to use for computing spectrum. Currently valid options are
        'generalNMSSM'->(nmhdecay called) and 'mSUGRA'->(nmspec called)
        """
        # Either the file to use as input, or the name to given the input file
        # which will be created from the file 'template'.
        # (Need to use abspath since we have to change directory to run nmspec)
        self.infile = os.path.abspath(infile)
        # Names to give output files
        self.spectr = os.path.abspath(specout)
        self.decay = os.path.abspath(decayout)
        self.omega = os.path.abspath(omegaout)
        self.tuning = os.path.abspath(tunout)
        self.SLHAspectr = SpectrumFile(name=self.spectr, directory='')    #SpectrumFile has extra blueprints defined to deal with multi-index items
        self.SLHAomega = OmegaFile(name=self.omega, directory='')    #OmegaFile has extra blueprints defined to deal with the Channels block
	self.SLHAtuning = SpectrumFile(name=self.tuning, directory='')

        if template != None:
            self.template = template
            print "nmspec template SLHA input file: ", self.template
            self.SLHAtemplate = SLHAFile(name=self.template, directory='')       #File to modify to create infile
            self.SLHAtemplate.readdata()                                #Read data from the template file
        self.options = options
        
        # Add to self.options the appropriate switch for the selected model
        # note: I actually don't think this does anything. I think this switch
        # is just how the NMSSMTools run script decides which of nmspec,
        # nmhdecay, or nmgmsb to call. But let's set it anyway just in case.
        
        # Set which NMSSMTools code to run
        if model=='generalNMSSM':
            print 'Computing NMSSM spectrum using nmhdecay'
            self.runfunc = nmhdecay.spec
        elif model=='mSUGRA':
            print 'Computing NMSSM spectrum using nmspec'
            self.runfunc = nmspec.spec
        elif model=='GMSB':
            raise Exception("Sorry, model GMSB is not currently implemented! \
please set model='generalNMSSM' (for nmhdecay) or model='mSUGRA' (for nmspec)")
        else:
            raise Exception("model specification string does not match an \
implemented model. Please set model='generalNMSSM' (for nmhdecay) or \
model='mSUGRA' (for nmspec)")
        
        # Check that the config file specifying the location of nmspec exists.
        # It is not great that this is required, but I didn't have time or 
        # patience to make a fancy enough nmspec extension module that could
        # deal with this issue itself.
        cfg = ConfigParser.RawConfigParser()
        cfgfile = workdir+'/nmspecf2py.cfg'
        print 'Reading config file for nmspec wrapper: {0}'.format(cfgfile)
        try:
            cfg.readfp(open(cfgfile))
        except IOError as err:
            raise IOError('{0} - Cannot locate nmspecf2py config file: please \
create a file in nmspecf2py module work directory ("wrappers" if using pysusy3)\
 called "nmspecf2py.cfg", which has the contents:\n\
\n\
[settings]\n\
nmspecdir = <full path to directory containing nmspec>\n\
\n\
If using NMSSMTools_3.2.3 this path is "<parent>/NMSSMTools_3.2.3/main".\n\
Sorry that this is necessary; my nmspec extension module is not advanced enough\
 to figure this out for itself, and nmspec needs to access some files in the \
nmspec directories.'.format(err))
        self.nmspecdir = cfg.get('settings','nmspecdir')
        # END __init__
        
    def silence(self):
        """Kill the stdout of the current process. Lets us silence the
        output of the wrapped fortran code, which 
        sys.stdout = open('/dev/null'), for example, does not"""
        os.dup2(self.null_fds[0], 1)                                    # put /dev/null fds on 1 and 2
        os.dup2(self.null_fds[1], 2)
    
    def unsilence(self):
        """undoes the action of silence"""
        os.dup2(self.save[0], 1)                                        # restore file descriptors so I can print the results
        os.dup2(self.save[1], 2)
        # close the temporary fds
        #os.close(null_fds[0]) #don't think I want to do this, may as well keep using the same ones every loop
        #os.close(null_fds[1])
        
    def run(self):
        """Execute process
        For now just doing simple thing. See ISAJET wrapper if program isolation
        required (i.e. fork/multiprocessing)
        """
        # nmspec is a bit stupid and doesn't work correctly if cwd is not the
        # directory the program is installed into (since it tried to access 
        # files containing info about experimental constraints)
        # So need to change directory and back here (WILL CAUSE MAYHEM IF NMSPEC
        # CRASHES, KEEP AN EYE ON THIS)
        with chdir(self.nmspecdir):
                self.runfunc(self.infile, self.spectr, self.decay, self.omega, self.tuning)
    
    def checkoutput(self):
        """Check if errors occurred during running"""
        # Check spectrum output file for error signals
        self.SLHAspectr.readdata()
        try:
            block = self.SLHAspectr.block('SPINFO')
            item = block[4]
            errormsg = item.value
            return 1, errormsg   # Yes errors occurred
        except KeyError as err:
            if err.message==4: pass        # No errors occurred
            else: raise
       	
        if self.options['usemicromegas'] != 0:
            # Check darkmatter output file for error signals 
            self.SLHAomega.readdata()
            try:
                block = self.SLHAomega.block('RDINFO')
                item = block[4]
                errormsg = item.value
                #print 'testing', errormsg
                return 2, errormsg   # Yes errors occurred (inc. "neutralino not LSP")
            except KeyError as err:
                if err.message==4: pass        # No errors occurred
                else: raise    
        
        # Read in the tuning file; no error checks to perform. 
        self.SLHAtuning.readdata()
   
        # temp! Many points passing the checks which seem messed up, need to see what is wrong with them...
        #print "#====================================================="   
        #print "  'GOOD' POINT FOUND, SEARCHING FOR EXTRA PROBLEMS... "
        #print "#====================================================="   
        #print "SPINFO block:"
        #self.SLHAspectr.printblock('SPINFO')
        #print "RDINFO block:"
        #self.SLHAomega.printblock('RDINFO')
        #print "------------------------------------------------------"
        #print "parameter values:"
        #print "M2    : {0}".format(self.SLHAspectr.block('EXTPAR')[2]).rstrip('\n')
        #print "lambda: {0}".format(self.SLHAspectr.block('EXTPAR')[61]).rstrip('\n')
        #print "kappa : {0}".format(self.SLHAspectr.block('EXTPAR')[62]).rstrip('\n')
        #print "TanB  : {0}".format(self.SLHAspectr.block('MINPAR')[3]).rstrip('\n')
        #print "------------------------------------------------------"
        #print "tuning file values:"
        #try:
        #   self.SLHAtuning.block('TUNJACOB')[10]
        #   print "logJuds_a : {0}".format(self.SLHAtuning.block('TUNJACOB')[10]).rstrip('\n')
        #   print "logJuds_b : {0}".format(self.SLHAtuning.block('TUNJACOB')[11]).rstrip('\n')
        #   print "logJuds_c : {0}".format(self.SLHAtuning.block('TUNJACOB')[12]).rstrip('\n')
        #   print "logAJUDS  : {0}".format(self.SLHAtuning.block('TUNJACOB')[21]).rstrip('\n')
        #except TypeError:
        #   print "No TUNJACOB block!"
        #print "#====================================================="
        ## flush buffer to make sure this prints in the right place
        #sys.stdout.flush()  
 
        #Made it to the end of the checks! Therefore no errors occurred.
        return 0, ''
        
    def getspecobs(self,skiperrors=True):
        """Gather results of computations"""
        # self.SLHAspectr.readdata() # Now must run 'checkoutput' first
        return self.SLHAspectr.getobs(specdict)                            #extract observables from SLHA file using translation dictionary

    def gettunobs(self,skiperrors=True):
        """Gather results of computations"""
        #self.SLHAtuning.readdata()  # Doesn't get done in error checks, so do it here
        return self.SLHAtuning.getobs(tundict)                            #extract observables from SLHA file using translation dictionary

    def getomegaobs(self,skiperrors=True):
        """Gather results of computations"""
        if self.options['usemicromegas'] != 0:
            # extract observables from SLHA file using translation dictionary
            obsdict = self.SLHAomega.getobs(DMdict) 
        else:
            # Nothing was computed in this case
            obsdict = {}
        return obsdict 
    
    # Naming dictionary for observables read from decay file     
    entries = []
    higgses = [1,2,3]
    for h in higgses:
        # tuples are ("crushed" comment name, decaydict key)
        entries += [
                    ('#BR(H_%i->gluongluon)'%h, 'BR(H%i->gg)'%h),
                    ('#BR(H_%i->muonmuon)'%h,   'BR(H%i->mumu)'%h),
                    ('#BR(H_%i->tautau)'%h,     'BR(H%i->tautau)'%h),
                    ('#BR(H_%i->ssbar)'%h,      'BR(H%i->ssbar)'%h),
                    ('#BR(H_%i->ccbar)'%h,      'BR(H%i->ccbar)'%h),
                    ('#BR(H_%i->bbbar)'%h,      'BR(H%i->bbbar)'%h),
                    ('#BR(H_%i->ttbar)'%h,      'BR(H%i->ttbar)'%h),
                    ('#BR(H_%i->W+W-)'%h,       'BR(H%i->W+W-)'%h),
                    ('#BR(H_%i->ZZ)'%h,         'BR(H%i->ZZ)'%h),
                    ('#BR(H_%i->gammagamma)'%h, 'BR(H%i->aa)'%h),
                    ('#BR(H_%i->Zgamma)'%h,     'BR(H%i->Za)'%h),    
                   ]      
    decayentries = dict(entries)        
    
    def getdecayobs(self,skiperrors=True):
        """Reads the 'decay' output file of NMSSMTools
        This one has a weird (but SLHA compliant) format, so we cannot use the 
        standard pysusy block format reader. A custom one is used below.
        Only extracts Higgs decay information at this time."""
        decaydict = {}
        with open(self.decay,'r') as f:
            for line in f:
                words = line.split()
                # Check if we have reached a new section yet
                if words[:2]==['DECAY','25']:
                    decaydict['H1-width'] = float(words[2]); higgs=1; continue
                elif words[:2]==['DECAY','35']:
                    decaydict['H2-width'] = float(words[2]); higgs=2; continue
                elif words[:2]==['DECAY','45']:
                    decaydict['H3-width'] = float(words[2]); higgs=3; continue
                # Branching ratios (read based on "crushed" comment)
                crushedcomment = ''.join(words[4:])
                if crushedcomment in self.decayentries.keys():
                    decaydict[self.decayentries[crushedcomment]] \
                            = float(words[0])
        # Finished reading file!                                  
        return decaydict              
        
    def writeinput(self,paramvector):
        """Write the input SLHA file.
        Parameter names used in 'paramvector' dictionary must match
        'SLHAdict'
        paramvector - dictionary containing parameter names and values
        options - dictionary containing option names and values
        """
        if self.template == None:
            raise ValueError('Error in ISAJET wrapper: Attempted to \
create input SLHA file without specifying a template!')
        else:
            for param,val in self.options.items()+paramvector.items():
                try:
                    blockname,indices = specdict[param]                 #get the block and index for this parameter
                except KeyError, err:
                    msg = '{0} : Parameter name supplied in paramvector \
(or options) does not match any entry of the SLHA mapping dictionary (param = {1}, \
paramvector = {2}'.format(err,param,paramvector)
                    raise KeyError(msg)
                if len(indices)==1: 
                    self.SLHAtemplate.block(blockname)[indices[0]].value = val   #set the new parameter value in the template SLHA file object
                #elif len(indices)==2:  WONT WORK! SEE self.getobs
                #    self.SLHAtemplate.block(blockname)[indices[0]][indices[1]].value = val
                else:
                    raise KeyError('No entry found in template nmspec SLHA \
input file for specified parameter! (param={0}, blockname={1}, indices={2})'.format(param,blockname,indices))
            self.SLHAtemplate.copyto(self.infile)                       #save the modified template values into 'infile' in SLHA format
