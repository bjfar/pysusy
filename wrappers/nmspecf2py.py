"""PyScanner-PySUSY wrapper for nmspec (from NMSSMTools 3.2.3)
This wrapper runs nmspec via an f2py extension module, which wraps the fortran
code. Here we interface that very simple wrapper with PySUSY. (note, nmspec
output format has been modified slightly to turn it into 'block' format: this
partially wrecks the SLHA compatibility).

Ben Farmer, Feb 4 2013
"""

import nmspec                                                           #requires nmspec f2py extension module
from multiprocessingmod import Process                                     

from common.SLHAfile import SLHAFile, SpectrumFile, OmegaFile                      #PySUSY SLHA file reader classes
from blockmaps.nmspecspectrum import SLHAdict as specdict                #spectrum generator SLHA output translation dictionary
from blockmaps.nmspecomega import blockdict as DMdict                #dark matter SLHA output translation dictionary

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
    def __init__(self,infile,specout,decayout,omegaout,workdir, \
                    template=None,options={},silenceobjs=None):
        # Either the file to use as input, or the name to given the input file
        # which will be created from the file 'template'.
        # (Need to use abspath since we have to change directory to run nmspec)
        self.infile = os.path.abspath(infile)
        # Names to give output files
        self.spectr = os.path.abspath(specout)
        self.decay = os.path.abspath(decayout)
        self.omega = os.path.abspath(omegaout)
        self.SLHAspectr = SpectrumFile(name=self.spectr, directory='')    #SpectrumFile has extra blueprints defined to deal with multi-index items
        self.SLHAomega = OmegaFile(name=self.omega, directory='')    #OmegaFile has extra blueprints defined to deal with the Channels block

        if template != None:
            self.template = template
            self.SLHAtemplate = SLHAFile(name=self.template, directory='')       #File to modify to create infile
            self.SLHAtemplate.readdata()                                #Read data from the template file
        self.options = options
        
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
            nmspec.spec(self.infile, self.spectr, self.decay, self.omega)
    
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
        # Made it to the end of the checks! Therefore no errors occurred.
        return 0, ''
        
    def getspecobs(self,skiperrors=True):
        """Gather results of computations"""
        # self.SLHAspectr.readdata() # Now must run 'checkoutput' first
        return self.SLHAspectr.getobs(specdict)                            #extract observables from SLHA file using translation dictionary

    def getomegaobs(self,skiperrors=True):
        """Gather results of computations"""
        if self.options['usemicromegas'] != 0:
            # extract observables from SLHA file using translation dictionary
            obsdict = self.SLHAomega.getobs(DMdict) 
        else:
            # Nothing was computed in this case
            obsdict = {}
        return obsdict                            
        
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
