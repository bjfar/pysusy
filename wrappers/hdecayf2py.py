"""PyScanner-PySUSY wrapper for HDECAY
This wrapper runs HDecay via an f2py extension module, which I wrote to
wrap the fortran code. Here we interface that very simple wrapper with
PySUSY.

Ben Farmer, 11 Jun 2012
"""

import hdecay                                                           #requires hdecay f2py extension module
#from multiprocessingmod import Process                                     
import subprocess as sp
import os
import shutil

from common.SLHAfile import SLHAFile                                    #PySUSY SLHA file reader classes
#from pyscanner.common.extra import BadModelPointError                   #PyScanner special error
from blockmaps.hdecay import blockdict                                  #hdecay block output translation dictionary

import sys

class HDecay:
    def __init__(self,infile,outfile,template=None):
        self.infile = infile                                            #Either the file to use as input, or the name to given the input file which will be created from the file 'template'.
        self.outfile = outfile
        hdecayroot = '/home/565/bff565/projects/pysusyMSSM/hdecay_ratio'
        self.root = hdecayroot
        #default extra input files
        hdecayindef = hdecayroot+'/hdecay.in'                           #extra hdecay input files (specifying constants etc)
        brinputdef = hdecayroot+'/br.input'               
        #new names of extra input files                                 #use the output file name as the base name for these, as it should have a unique identifier in it to prevent clashes between processes
        self.hdecayin = outfile+'.hdecay.in'                         
        self.brinput = outfile+'.br.input'               
        #copy default files to new location                             #copy default input files to temporary directory (assume this is given as part of the output file name)
        shutil.copyfile(hdecayindef, self.hdecayin)
        shutil.copyfile(brinputdef, self.brinput)
        
        self.SLHAout = SLHAFile(name=self.outfile, directory='')
        #self.exe = 'run'      
        
    def run(self):
        """Execute process"""
        """
        cwd=os.getcwd()
        os.chdir(self.root)
        sp.call([self.exe, self.outfile])
        os.chdir(cwd)
        """
        #REALLY WEIRD ERRORS GOING ON IF I RUN THIS IN THE MAIN PYTHON PROCESS
        #DOING THE FORK NOW ONLY TO PREVENT SUCH THINGS OCCURRING
        sys.stdout.flush()                                              #os.fork() clones the io buffer for these files, so make sure they get dumped to disk before the fork or the output will get duplicated. 
        sys.stderr.flush()
        childpid = os.fork()                                            #spawn child process and get its pid (or 0 if this is the child process)
        if childpid == 0:
            hdecay.ratios(self.infile, self.hdecayin, self.brinput, self.outfile)
            os._exit(0)                                                 #exit the child process with error code 0 (even if isajet fails we'll still do this coz we can tell how things went from the output file)
        else:
            os.waitpid(childpid, 0)
        """
        p = Process(target=hdecay.ratios, args=(self.infile, self.hdecayin, self.brinput, self.outfile))
        p.start()
        p.join()
        """
    def getobs(self,skiperrors=True):
        """Gather results of computations"""
        self.SLHAout.readdata()
        return self.SLHAout.getobs(blockdict)                            #extract observables from block format file using translation dictionary
