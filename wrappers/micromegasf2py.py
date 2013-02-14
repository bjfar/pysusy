"""PyScanner-PySUSY wrapper for micrOmegas 2.4.Q
This wrapper runs micrOmegas via an f2py wrapper

Ben Farmer, May 29 2012
"""

import micromegas                                                       #requires micromegas f2py extension modules
from multiprocessingmod import Process

from common.SLHAfile import SLHAFile                                    #PySUSY SLHA file reader class
#from pyscanner.common.extra import BadModelPointError                   #PyScanner special error
from blockmaps.darkomega import blockdict                               #block format output file translation dictionary

import os
import sys

from silence import Silence

class MicrOmegas:
    def __init__(self,infile,outfile,silenceobjs=None):
        self.infile = infile
        self.outfile = outfile
        self.SLHA = SLHAFile(name=outfile, directory='')
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
        """Execute process"""
        #self.silence()                                                  # Don't want default output clogging up our log files so dump it all to dev/null
        #sys.stdout = open('/dev/null')
        #micromegas.rundarkomega(self.infile, self.outfile)
        #sys.stdout = sys.__stdout__
        #self.unsilence()
        
        sys.stdout.flush()                                              #os.fork() clones the io buffer for these files, so make sure they get dumped to disk before the fork or the output will get duplicated. 
        sys.stderr.flush()
        childpid = os.fork()                                            #spawn child process and get its pid (or 0 if this is the child process)
        if childpid == 0:
            #self.silence()                                              # Don't want default output clogging up our log files so dump it all to dev/null
            with Silence(): micromegas.rundarkomega(self.infile, self.outfile)          #run micromegas in the child process; it was causing some weird errors in superiso that were had to fathom (with bsgmo calculation, was returning nan)
            os._exit(0)                                                 #exit the child process with error code 0 (even if isajet fails we'll still do this coz we can tell how things went from the output file)
        else:
            os.waitpid(childpid, 0)
        #self.unsilence()    #do the unsilencing out here, since the child process can be killed by isajet
        
        """
        p = Process(target=micromegas.rundarkomega, args=(self.infile, self.outfile))
        p.start()
        p.join()
        """
    def getobs(self,skiperrors=True):
        """Gather results of computations"""
        self.SLHA.readdata()
        return self.SLHA.getobs(blockdict)                              #extract observables from SLHA file using translation dictionary
        
        """
        self.SLHA.readdata()                          #read SLHA file (NOTE: THIS BY FAR DOMINATES THE CPU TIME FOR getobs. OPTIMISE THIS IF REQUIRED)
        self.obs = {}                                                   #reset output dictionary
        for key,(blockname,(index)) in blockdict.items():               #cycle through SLHA translation dictionary
            try:
                self.obs[key] = self.SLHA.block(blockname)[index].value     #extract observables from SLHA file object
            except TypeError, err:
                if skiperrors:
                    self.obs[key] = None
                else:
                    msg = '{0} : Possibly the block requested is missing \
from the output file (file={1}, blockname={2}, key={3})'.format(err,self.outfile,blockname,key)
                    raise TypeError(msg)
            #except (TypeError, KeyError, BadModelPointError):
        return self.obs
        """
