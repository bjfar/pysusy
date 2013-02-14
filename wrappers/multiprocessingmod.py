"""Modification of 'multiprocessing' module
This module contain a subclass of multiprocessing.Process which is
exactly the same as the original except one method in
multiprocess.forking which was giving me trouble and which I have
replaced
"""

import multiprocessing.process as process
import multiprocessing.forking as forking
import os
import sys
import itertools

class Popenmod(forking.Popen):
    """Modified version of mp.forking.Popen"""
    
    def __init__(self, process_obj):
        sys.stdout.flush()
        sys.stderr.flush()
        self.returncode = None

        self.pid = os.fork()
        if self.pid == 0:
            #if 'random' in sys.modules:                                #bjf> This is creating extra filesystem searches in my loops and I don't see what good it is anyway.
            #    import random
            #    random.seed()
            code = process_obj._bootstrap()
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(code)

class Process(process.Process):
    """Modified version of multiprocessing.Process"""

    def start(self):
        '''
        Start child process
        '''
        assert self._popen is None, 'cannot start a process twice'
        assert self._parent_pid == os.getpid(), \
               'can only start a process object created by current process'
        assert not _current_process._daemonic, \
               'daemonic processes are not allowed to have children'
        #_cleanup()
        process._cleanup()
        if self._Popen is not None:
            Popen = self._Popen
        else:
            #from .forking import Popen                                 #bjf> have replaced the Popen class from 'forking'
            Popen = Popenmod
        self._popen = Popen(self)
        _current_process._children.add(self)
        
#This is exactly the same as in process, but we need it to be subclassed
#from the new Process class
class _MainProcess(Process):

    def __init__(self):
        self._identity = ()
        self._daemonic = False
        self._name = 'MainProcess'
        self._parent_pid = None
        self._popen = None
        self._counter = itertools.count(1)
        self._children = set()
        #self._authkey = AuthenticationString(os.urandom(32))
        self._authkey = process.AuthenticationString(os.urandom(32))
        self._tempdir = None

_current_process = _MainProcess()
del _MainProcess
    
