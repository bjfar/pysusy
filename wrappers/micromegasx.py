"""PyScanner-PySUSY wrapper for micrOmegas 2.4.Q
This wrapper runs micrOmegas via the filesystem

Ben Farmer, May 29 2012
"""

import subprocess as sp
import sys
import os

class MicrOmegas:
    def __init__(self,path,infile,outfile):
        self.path = path
        self.infile = infile
        self.outfile = outfile
                          
    def run(self):
        """Execute process"""
        exe = '{0}/MSSM/darkomegabjf'.format(self.path)
        sp.call([exe, self.infile, self.outfile, os.path.abspath(self.path)])
        

    def getobs(self):
        """Gather results of computations"""
        pass
