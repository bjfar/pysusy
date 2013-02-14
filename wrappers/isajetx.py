"""PyScanner-PySUSY wrapper for ISAJET 7.81
This wrapper runs ISAJET via the filesystem

Ben Farmer, May 29 2012
"""

import subprocess as sp
import sys
import os

class Isajet:
    def __init__(self,path,infile,outfile):
        self.path = path
        self.infile = os.path.abspath(infile)
        self.outfile = os.path.abspath(outfile)
                                                
    def run(self):
        """Execute process"""
        exe = 'isasugraSLHA.x'
        sp.call([exe, self.infile, self.outfile])
        

    def getobs(self):
        """Gather results of computations"""
        pass
