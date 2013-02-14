"""MINIMUM TEST CASE FOR ISAJET WRAPPER, TRYING TO ISOLATE SUPERFLOUS
SYSTEM CALLS
"""

import sys
import isajet                                                           #requires ISAJET f2py extension module
from multiprocessing import Process                                     

class Isajet:
    def __init__(self,infile,outfile):
        self.infile = infile                                            #Either the file to use as input, or the name to given the input file which will be created from the file 'template'.
        self.outfile = outfile
                                                
    def run(self):
        """Execute process"""
        sys.stderr.write('RUNNING ISAJET')
        p = Process(target=isajet.isasugraslha, args=(self.infile, self.outfile))
        p.start()
        p.join()
        sys.stderr.write('ISAJET PROCESS REJOINED')
