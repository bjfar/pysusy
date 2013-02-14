"""NEXT-TO MINIMUM TEST CASE FOR ISAJET WRAPPER. NO SUPERFLUOUS SYSTEM
CALLS OCCURING IN THE MINIMUM CASE
"""

import isajet                                                           #requires ISAJET f2py extension module
from multiprocessing import Process                                     

from common.SLHAfile import SLHAFile, SpectrumFile                      #PySUSY SLHA file reader classes
#from pyscanner.scanner import BadModelPointError                        #PyScanner special error
from blockmaps.spectrum import SLHAdict                                 #spectrum generator SLHA output translation dictionary

#import time
import sys

class Isajet:
    def __init__(self,infile,outfile,template=None):
        self.infile = infile                                            #Either the file to use as input, or the name to given the input file which will be created from the file 'template'.
        self.outfile = outfile
        #self.SLHAout = SpectrumFile(name=self.outfile, directory='')    #SpectrumFile has extra blueprints defined to deal with multi-index items
        #if template != None:
        #    self.template = template
        #    self.SLHAtemplate = SLHAFile(name=self.template, directory='')       #File to modify to create infile
        #    self.SLHAtemplate.readdata()                                #Read data from the template file
                                                      
    def run(self):
        """Execute process"""
        sys.stderr.write('RUNNING ISAJET')
        p = Process(target=isajet.isasugraslha, args=(self.infile, self.outfile))
        p.start()
        p.join()
        sys.stderr.write('ISAJET PROCESS REJOINED')
