#! /usr/bin/env python

"""MAIN PYSUSY RUNSEQUENCE

This module is the main executable for pysusy. Its instructions are stored
in a number of setup scripts which are listed below, which are to be
specified in the MASTER config file. Pysusy may be run from the command line
or from within the interpreter.
Because functions must be defined before they are called, the order of functions
listed here is almost the reverse of the order they are called. To best read the
code go to the end of this file and read the commands actually executed when
the script is invoked, then work upwards through each function as it is called.

Command line usage:

python pysusy.py [MASTER config module name] [Job ID string] [extra run options]

OR

./pysusy.py [MASTER config module name] [Job ID string] [extra run options]

The "extra run options" arguments are passed to the master configuration script,
they allow the user to set extra configuration options at runtime. Of course the
user must tell the master configuration script what to do with these arguments.

Note: [MASTER config module name] can refer to a submodule, i.e. if you organise
your config files into a python package structure, say put them within a directory
called 'master' and name the config file 'Mconfig', then the argument given should
be 'master.Mconfig'.
"""

# Import external modules
import os
import sys
import shutil
import getopt

# Import PyScanner machinery
import pyscanner.scanner as pyscan

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
    
def process(args):
    """Main run sequence for pysusy
    
    describe functionality here
    
    Keyword arguments:
    
    args -- list containing the arguments supplied to the program. These should be:
        args[0] -> masterconfig -- the string name of the master configuration script for the job.
        args[1] -> jobname -- a string to identify the job, so that the seperately running parallel
        processes can function together correctly. This should be unique enough that concurrently
        running jobs can be distinguished, there will be serious problems if two running jobs have the
        same jobname.
        args[2+] -> extra config options -- these arguments are passed "as is" to the master
        configuration script. They allow the user to interact with their config script at runtime.
    NOTE: Modification- pysusy now searches args 2+ for the string "--testing", if found goes into testing mode,
    in which it goes super-verbose. This should be at the end of the argument list to avoid screwing up arguments
    sent to configuration module    
    """

    #--------------Error handling for program arguments-----------------
    try:
        outdir = os.path.abspath(args[0])    #Careful, Multinest has a limit of 100 characters for path+filenames. (note, I hacked it to make this limit 300)
    except IndexError, err:
        msg = "(IndexError - {0}) : First program argument not found, this should be a \
string specifying the desired root directory for program output ('.' for current directory)".format(err)
        raise Usage(msg)    
    print 'checkpoint process 3'
    try:
        masterconfig = args[1]      #master config module
        print masterconfig
        __import__(masterconfig)    #imports the module with the name stored in masterconfig
        master = sys.modules[masterconfig] #__import__ imports the top level module in the name
                                    #masterconfig (i.e. 'foo' if masterconfig='foo.bar.baz'), 
                                    #this line associates master with 'foo.bar.baz' itself
        print master
    except IndexError, err:
        msg = '(IndexError - {0}) : Second program argument not found, this should be a \
string identifying the master configuration module'.format(err)
        raise Usage(msg)
    except ImportError, err:
        print '(ImportError - {0}) : Error importing master configuration module, please check \
module name'.format(err)
        raise
    print 'checkpoint process 4'
    try:
        jobname = args[2]           #unique string identifying job
    except IndexError, err:
        msg = "({0}) : Third program argument not found, this should be a \
string identifying the job".format(err)
        raise Usage(msg)
#read in remaining arguments to a list to be passed to the configurations scripts
    argsleft = True #initialise boolean
    configargs = [] #initialise empty list to add arguments to
    slot = 3 #variable to count which args slot we are reading from
    testing = False #initialise testing flag
    skipproblems = True #initialise problem skip flag
    while argsleft: 
        try:
            configargs += [args[slot]]  #need the extra list brackets so we treat the string as one element of a list, not a list of characters
            if args[slot]=="--testing": testing=True    #if we find this argument in there, set program to testing mode.
            if args[slot]=="--dontskipproblems": skipproblems=False #Tell code not to skip problems that generate BadModelPointErrors
            slot += 1
        except IndexError, err:
            #If there is an index error it means we have run out of arguments, so stop looping
            argsleft = False
    print 'checkpoint process 5'
    #-------------------------------------------------------------------

    #---------------LOAD MASTER CONFIGURATION---------------------------
    #Create master configuration object (supplying mpi objects and extra user arguments)
    comm,rank,size = pyscan.initMPI()
    masterconfig = master.Master((comm,rank,size),configargs)           
    #-------------------------------------------------------------------

    #---------------Initialise "Scan" object----------------------------
    scan = pyscan.Scan(outdir, jobname, testing=testing, skipproblems=skipproblems, mpi=(comm,rank,size), **masterconfig.scanargs)

    #---------------Begin scan!-----------------------------------------
    scan.run()
    
    #---------------ARCHIVE RESULTS------------------------------------
    
    if rank==0:    #do only if this is the process with rank 0
        rootname = outdir+'/'+jobname+'-'
        tarname = rootname+'.tar'
        print "Archiving results..."
        infoarchive=tarfile.open(tarname,'a')#open archive for compressed writing
        #if multinest: (current path should be pysusy root)
        #add switch to deal with other samplers once these are added.
        if scan.sampler=='multinest':
            suffixlist = ['resume.dat','phys_live.points','live.points','ev.dat', \
            'stats.dat','summary.txt','post_separate.dat','post_equal_weights.dat', \
            '.txt','.info','.timing','.timinginfo']   #'info' is the file we created in the likelihood function to record some labels for the '.txt' file output columns
        elif scan.sampler=='list':
            suffixlist = [] #for now, no archiving of results done for list sampling mode, since we generally use array jobs and these need to be combined in post-processing.
        problem = False
        for suffix in suffixlist:
            attempts=1
            while True:
                try:
                    infoarchive.add(rootname+suffix) #adds the output file corresponding to this suffix to the archive (path relative to pysusy root)     
                    break       #if read is successful break out of the while loop
                except OSError, msg:
                    if attempts<=50:#we'll give the program 50 attempts to read the file before conceding defeat and letting it crash out (been having problems with sporadic OSError's)
                        print("OSError encountered, retrying... (attempt {0})".format(attempts))
                        time.sleep(5)   #wait some time and hope problem goes away in the meantime.
                        attempts += 1   #add 1 to attempts count
                        pass
                    else:
                        print("Problem encountered adding file to final archive, skipping...: {0}".format(rootname+suffix))                        
                        print("Message: {0}".format(msg))
                        problem = True
                        break #go on to next file in list
        infoarchive.close()
        if problem:
            print "Problem encountered creating final archive. Completed \
results may still be found in the chains directory"
        print "Results archived in '{0}'".format(tarname)

    
# main function, for processing of arguments
def main(argv=None):
    """
    Initial pysusy runsequence, for processing command line arguments
    
    Argument should be a master configuration script defining the job.
    """
    # parse command line options
    if argv is None:            
        argv = sys.argv         #If no argument is supplied, assume module is being run from the command line and get the arguments from there
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error, msg:
            raise Usage(msg)
        # process options
        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                return 0
        # process arguments
        process(args)    # process() defined above. This runs the main pysusy sequence.
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2
        
if __name__ == "__main__":
    """Execute commands
    
    These are the commands that are run first once the script is invoked
    from the command line
    """
    #try:
    sys.exit(main())
    #finally:    #add any cleanup commands here
    #    for file in glob.glob('IDpool-*.log')   #iterate through list of files matching pattern given (in current directory, but can supply absolute or relative path too)
    #        os.remove(file) #delete file (we are cleaning up the ID pool files)
