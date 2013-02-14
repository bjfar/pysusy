"""PyScanner-PySUSY wrapper for SuperISO v3.1
This wrapper runs SuperISO via a c shared library using ctypes.

Ben Farmer, Jun 7 2012
"""

import superiso                                                         #Requires superiso c extension wrapper to be installed                                                       
#from multiprocessingmod import Process

from common.SLHAfile import FlavourFile                                 #PySUSY SLHA file reader class
#from pyscanner.common.extra import BadModelPointError                   #PyScanner special error
from blockmaps.flavour import flhadict                                  #FLHA format output file translation dictionary
import os
import sys

class SuperISO:
    def __init__(self,infile,outfile):
        self.infile = infile
        self.outfile = outfile
        self.FLHA = FlavourFile(name=outfile, directory='')

    def run(self):
        """Execute process"""
        sys.stdout.flush()                                              #os.fork() clones the io buffer for these files, so make sure they get dumped to disk before the fork or the output will get duplicated. 
        sys.stderr.flush()
        childpid = os.fork()                                            #spawn child process and get its pid (or 0 if this is the child process)
        if childpid == 0:
            superiso.slha(self.infile, self.outfile)
            os._exit(0)                                                 #exit the child process with error code 0 (even if isajet fails we'll still do this coz we can tell how things went from the output file)
        else:
            os.waitpid(childpid, 0)
        """
        p = Process(target=superiso.slha, args=(self.infile, self.outfile))
        p.start()
        p.join()
        """
        
    def getobs(self,skiperrors=True):
        """Gather results of computations"""
        self.FLHA.readdata()
        #self.FLHA.printblock('FOBS')
        return self.FLHA.getobs(flhadict)                              #extract observables from SLHA file using translation dictionary
