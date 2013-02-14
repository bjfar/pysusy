"""PyScanner-PySUSY wrapper for SuperISO v3.1
This wrapper runs SuperISO via a c shared library using ctypes.

Ben Farmer, Jun 7 2012
"""

import ctypes                                                          
from multiprocessing import Process

from common.SLHAfile import SLHAFile                                    #PySUSY SLHA file reader class
#from pyscanner.common.extra import BadModelPointError                   #PyScanner special error
from blockmaps.flavour import flhadict                                  #FLHA format output file translation dictionary

superiso = ctypes.CDLL('/home/565/bff565/projects/pysusyMSSM/superiso_v3.1/libslha.so') #path to SuperISO c shared library

class SuperISO:
    def __init__(self,infile,outfile):
        self.infile = infile
        self.outfile = outfile
        self.SLHA = SLHAFile(name=outfile, directory='')
        self.runfunc = superiso.slha
                          
    def run(self):
        """Execute process"""
        p = Process(target=self.runfunc, args=(self.infile, self.outfile))
        p.start()
        p.join()

    def getobs(self,skiperrors=True):
        """Gather results of computations"""
        self.SLHA.readdata()                                            #read SLHA file (NOTE: THIS BY FAR DOMINATES THE CPU TIME FOR getobs. OPTIMISE THIS IF REQUIRED)
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
