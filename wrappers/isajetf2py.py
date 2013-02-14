"""PyScanner-PySUSY wrapper for ISAJET 7.81
This wrapper runs ISAJET via an f2py extension module, which I wrote to
wrap the fortran code. Here we interface that very simple wrapper with
PySUSY.

Since ISAJET has STOP statements laced throughout it which cause our
whole process to terminate if we encounter them, we will run each loop
in a seperate process using the 'multiprocessing' module. Hopefully
this will generate less filesystem activity than simply running ISAJET
through the operating system.

Ben Farmer, May 29 2012
"""

import isajet                                                           #requires ISAJET f2py extension module
from multiprocessingmod import Process                                     

from common.SLHAfile import SLHAFile, SpectrumFile                      #PySUSY SLHA file reader classes
#from pyscanner.common.extra import BadModelPointError                   #PyScanner special error
from blockmaps.spectrum import SLHAdict                                 #spectrum generator SLHA output translation dictionary

import time
import sys
import os

from silence import Silence                                             #class to silence output of wrapped code

class Isajet:
    def __init__(self,infile,outfile,template=None,silenceobjs=None):
        self.infile = infile                                            #Either the file to use as input, or the name to given the input file which will be created from the file 'template'.
        self.outfile = outfile
        self.SLHAout = SpectrumFile(name=self.outfile, directory='')    #SpectrumFile has extra blueprints defined to deal with multi-index items
        if template != None:
            self.template = template
            self.SLHAtemplate = SLHAFile(name=self.template, directory='')       #File to modify to create infile
            self.SLHAtemplate.readdata()                                #Read data from the template file
        #save info about stdout for use by silence functions
        #NOW GET THESE EXTERNALLY SO THEY CAN BE SHARED BY ALL PROGRAMS
        ##self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in xrange(2)] # open 2 fds
        ##self.save = os.dup(1), os.dup(2)                                # save the current file descriptors to a tuple
        #self.null_fds, self.save = silenceobjs
        
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
        Used to use multiprocessing module to spawn the new process, but
        it does weird things like 'import random', so now we'll just do
        the fork ourselves.
        """
        sys.stdout.flush()                                              #os.fork() clones the io buffer for these files, so make sure they get dumped to disk before the fork or the output will get duplicated. 
        sys.stderr.flush()
        childpid = os.fork()                                            #spawn child process and get its pid (or 0 if this is the child process)
        if childpid == 0:
            #self.silence()                                              # Don't want default output clogging up our log files so dump it all to dev/null
            with Silence(): isajet.isasugraslha(self.infile, self.outfile)              #run isajet in the child process, in case a STOP statement is encountered in the fortran code
            os._exit(0)                                                 #exit the child process with error code 0 (even if isajet fails we'll still do this coz we can tell how things went from the output file)
        else:
            os.waitpid(childpid, 0)
        #self.unsilence()    #do the unsilencing out here, since the child process can be killed by isajet
        #print 'hello'
        """The fork seems to be slower than using Process, somehow? Check this.
        update: apparently the average time comes out the same so I guess it is fine
        sys.stderr.write('RUNNING ISAJET')
        p = Process(target=isajet.isasugraslha, args=(self.infile, self.outfile))
        p.start()
        p.join()
        sys.stderr.write('ISAJET PROCESS REJOINED')
        """
        
    def getobs(self,skiperrors=True):
        """Gather results of computations"""
        self.SLHAout.readdata()
        return self.SLHAout.getobs(SLHAdict)                            #extract observables from SLHA file using translation dictionary
        
        """
        self.SLHAout.readdata()                                         #read SLHA file (NOTE: THIS BY FAR DOMINATES THE CPU TIME FOR getobs. OPTIMISE THIS IF REQUIRED)
        self.obs = {}                                                   #reset output dictionary
        for key,(blockname,indices) in SLHAdict.items():                #cycle through SLHA translation dictionary
            item = self.SLHAout.block(blockname)
            try:
                for i in indices:
                   item = item[i]                                       #dig through nested lists of items 
            except TypeError:                                      
                if item: item = item[indices]                           #if no more item lists are found, assume we have only one index
                else: return None
            except AttributeError:
                print "Error extracting value from file {0}, block {1}, index {2}. Blueprint may \
    be missing, perhaps because file object is created from a class lacking this blueprint, for \
    example from 'SLHAFile' rather than 'SpectrumFile'.".format(self.SLHAout.name,blockname,indices)
                raise
            self.obs[key] = item.value
            
            try:
                if len(indices)==1: 
                    self.obs[key] = self.SLHAout.block(blockname)[indices[0]].value  #extract observables from SLHA file object
                elif len(indices)==2:
                    print self.SLHAout.block(blockname)
                    print dir(self.SLHAout.block(blockname))
                    print self.SLHAout.block(blockname)[1]
                    item = self.SLHAout.block(blockname)
                    try:
                        for i in indices:
                            item = item[i]
                    except TypeError:
                        if item: item = item[index]
                    self.obs[key] = self.SLHAout.block(blockname,indices)
                    self.obs[key] = self.SLHAout.block(blockname)[indices[0],indices[1]].value
                else:
                    raise KeyError('Invalid indices found in isajet SLHA \
input file! (key={0}, blockname={1}, indices={2})'.format(key,blockname,indices))
            except (KeyError, TypeError):
                print 'Invalid indices found in isajet SLHA \
input file! (key={0}, blockname={1}, indices={2})'.format(key,blockname,indices)
                raise
        return self.obs
        """
        
    def writeinput(self,paramvector):
        """Write the input SLHA file.
        Parameter names used in 'paramvector' dictionary must match
        'SLHAdict'
        """
        if self.template == None:
            raise ValueError('Error in ISAJET wrapper: Attempted to \
create input SLHA file without specifying a template!')
        else:
            for param,val in paramvector.items():
                try:
                    blockname,indices = SLHAdict[param]                 #get the block and index for this parameter
                except KeyError, err:
                    msg = '{0} : Parameter name supplied in paramvector \
does not match any entry of the SLHA mapping dictionary (param = {1}, \
paramvector = {2}'.format(err,param,paramvector)
                    raise KeyError(msg)
                if len(indices)==1: 
                    self.SLHAtemplate.block(blockname)[indices[0]].value = val   #set the new parameter value in the template SLHA file object
                #elif len(indices)==2:  WONT WORK! SEE self.getobs
                #    self.SLHAtemplate.block(blockname)[indices[0]][indices[1]].value = val
                else:
                    raise KeyError('No entry found in template isajet SLHA \
input file for specified parameter! (param={0}, blockname={1}, indices={2})'.format(param,blockname,indices))
            self.SLHAtemplate.copyto(self.infile)                       #save the modified template values into 'infile' in SLHA format
