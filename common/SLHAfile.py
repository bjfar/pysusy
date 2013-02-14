import os
from blockdata import *
#from programs import SUSYFile

# TODO: there should be a dict from human readable string identifiers to SLHA integer identifiers.
# SLHAFile should use the integer ids to determine the correct item.

def genericitem(self,string):
   string,comment = string.split('#',1)
   formatstring = ''
   d={}
   values=0
   labels=0
   for word in string.split():
      f = fortfloat(word)
      if f:
         d['value'+values]=f
         formatstring += ' %(value%d)' % values
         values+=1
      else:
         d['label'+labels]=word
         formatstring += ' %(label%d)' % labels
         labels+=1
   if comment:
      d['name']=comment
      formatstring += ' # '+comment
   self.formatstring = formatstring
   return d

class SUSYFile:
   """File encapsulation for passing data between SUSYPrograms."""
   jobstamp = ''    #Need to run SUSYFile.set_jobstamp to set these before creating SUSYFile instances
   suffix = ''
   #NOTE!! I have set nosuffix=True by default! There are problems with making sure that programs
   #who need specifically names input files have those files named properly, and a mechanism to
   #switch off the addition of a suffix only when copying files for the purpose of input to those
   #programs has not been created. I don't actually need this feature of adding suffixes
   #to files so I am turning it off for now.
   nosuffix = True #Set this to True to prevent the filename from getting a suffix attached during copy
                    #(in case a program requires a specificially named input file)
   mpirank = None   #rank of the mpi process, if mpi initialised through pysusy. If None, set_jobstamp uses the IDpool module to create a pseudo-rank.
   mpisize = None   #number of processes in the mpi process, if mpi initialised through pysusy.
   
   @classmethod
   def set_jobstamp(cls,jobstamp):  #first argument is the class (just as a regular method receives the object name as the first argument)
        """Class function for setting the job ID
        
        Do this before creating any file objects. Need to set the jobstamp
        so that when process IDs are drawn from the ID pool they are all
        drawing from the same pool and don't try to overwrite it with a 
        new pool file.
        
        Also sets the unique file suffix for this process
        
        jobstamp -- unique string to identify this job (must not change between processes,
                i.e. a timestamp is dangerous)
        """
        print 'MPI rank?:', cls.mpirank
        pool = IDpool.getID(jobstamp,verbose=True,MPIrank=cls.mpirank)   #create ID pool object 
        ID = pool.ID
        print 'My ID number is: {0}'.format(ID)
        #SEE NOTE ON SUFFIXES ABOVE!
        #As part of turning off suffixes, I am removing the setting of the
        #parameter entirely, since nosuffix doesn't seem to do much on its
        #own
        #cls.suffix = "-{0}".format(ID)       #define the unique suffix to add to files created through the current process, to prevent file conflicts with other processes
        cls.jobstamp = jobstamp        #store the jobstamp in this class in case we want it later (which we do)
        return pool                    #send back the pool object so that we can access the process ID later on
   #set_jobstamp = Callable(set_jobstamp)

   @staticmethod
   def add_suffix(filename):
       n=filename.rpartition('.')
       return n[0] + SUSYFile.suffix + '.' + n[2]

   def __init__(self,name,outputfrom=None,directory=None):
       """Initialisation for input/output files
       
       Here we set the name of the file object and the programs and directories it
       is associated with. If the file is 'outputfrom' some program it will be assumed
       to be created by that program and thus will not be read in during startup.
       
       Keyword Args:
       
       name         -- the filename
       outputfrom   -- the program object associated with the program which creates this file
       directory    -- the directory the file is located in (assumed to be outputfrom.directory
                       by default)
       """
       #bjf> name of file ('name') needs to be appended with a unique identifier to avoid name clashes when 
       #program is run in parallel on multiple processors. We don't have direct access to the MPI information
       #(since that is handled by Multinest (the parameter generator more generally)), so we have to be a bit
       #less elegant and use the computer name instead of a nice number or something.
       self.name = name
       #bjf> outputfrom used to be either a string or a 'program' object, now it MUST be a program object
       # if file directory is different to program directory this must be supplied in the 'directory' argument as a string
       if outputfrom == None and directory == None:
          raise Exception('Either \'outputfrom\' or \'directory\' must be specified')
       elif directory == None: #i.e. outputfrom != None
          self.directory = outputfrom.directory
          self.outputfrom = outputfrom
       else: #i.e. either (outputfrom and directory != None) or (outputfrom != None and directory == None)
          self.directory = os.path.expanduser(directory) # supports ~ as the home directory
          self.outputfrom = outputfrom #this may be None still
       #bjf> NOTE: I CHANGED THIS TO REQUIRED THE 'directory' ARGUMENT. POSSIBLY NOT ALL SUBCLASSES HAVE BEEN UPDATED ACCORDINGLY

   def copyto(self,path):
      """Copy the file to a different directory."""
      # print 'copying from/to',self.fullpath(), SUSYFile.add_suffix(path)
      if nosuffix:
         shutil.copyfile(self.fullpath(), path)  #do the copying without altering the filename specified
      else:
         shutil.copyfile(self.fullpath(), SUSYFile.add_suffix(path))  #add a suffix to help keep track of what node is doing what

   def extract(self,key):
      """Extract a line of data specified by 'key' as a list.

      Warning: This method is provided only for expediency, it will not work correctly unless the desired line is the only one containing exactly the string given.
      """
      datafile = open(self.directory+self.name, 'rb')
      keylen = len(key)
      for line in datafile:
         if line.find(key)!=-1:
            r = [tryfloat(s) for s in line.split('#',1)[0].split()]
            if len(r) == 1: return r[0]
            return r
      return None

   def strextractall(self):
      """Return a list containing every line of data as a list."""
      data = []
      datafile = open(self.directory+self.name, 'rb')
      reader = csv.reader([s.replace('\t',' ') for s in datafile], delimiter=' ', skipinitialspace=True)
      try: return [line for line in reader]
      except: return None

   def extractall(self):
      return [[tryfloat(s) for s in l] for l in self.strextractall()]

   def fullpath(self):
      return self.directory + SUSYFile.add_suffix(self.name)

   def readdata(self): # TODO: probably a better way to do this
      pass
    
class SLHAFile(SUSYFile):
   def __init__(self,name,outputfrom=None,directory=None,items=[],customblocks=[],standardblocks=[]):
      #outputfrom is a 'program' object, directory is a string
      SUSYFile.__init__(self,name,outputfrom,directory)
      self.customblocks = customblocks
      itemtype1 = Blueprint(Item," %(index)d %(value)e # %(comment)ls")
      itemtype2 = Blueprint(Item," %(index)d %(value)d # %(comment)ls")   #bjf> be careful, this may incorrectly assume some entries are supposed to be integers if they happen to be an integer in the template. Ensure zero entries have a decimal place, i.e. 0.0e0 or similar
      itemtype3 = Blueprint(Item," %(index)d %(value)s # %(comment)ls")
      itemtype4 = Blueprint(Item," %(index)d %(value)ls")    #bjf> I added this because it wasn't reading in lines with no comment. Works for strings only atm. Added to "items" list as well. Example: Softsusy output, block SPINFO, index 4, value "Point invalid: [ MuSqWrongsign ]", no name (as you call it).
      # gah, might need to remove itemtype 5 because it clashes with blankitem
      itemtype5 = Blueprint(Item," %(value)e # %(comment)ls")   #bjf> needed for 'alpha' block of softsusy output, has only one entry, which has no index
      itemtype6 = Blueprint(Item," %(value)e")   #bjf> as above, but accounting for possibility that there is no comment
      #bjf> want an item that extracts values from block itself. Try the following:
      #itemtype7 = Blueprint(Block,"BLOCK %(name)s Q= %(value)e # %(comment)ls")
      #itemtype8 = Blueprint(Block,"BLOCK %(name)s Q=%(value)e # %(comment)ls") 
      #itemtype9 = Blueprint(Block,"BLOCK %(name)s Q= %(value)e")
      #<bjf
      blankitem = Blueprint(Item," %(index)d # %(comment)ls")	
      commentline0 = Blueprint(Item,"# %(comment)ls")
      commentline = Blueprint(Item," # %(comment)ls")
      commentline2 = Blueprint(Item," #%(comment)ls")
      #itemtype5,itemtype6
      #itemtype7,itemtype8,itemtype9
      items += [itemtype2,itemtype1,itemtype3,itemtype4,itemtype5,itemtype6,
		blankitem,commentline0,commentline,commentline2] # the order here could make a difference to performance (should it be items+[ ] or [ ]+items?)
      blocktype1 = Blueprint(Block,"BLOCK %(name)s %(value)d # %(comment)ls")
      blocktype2 = Blueprint(Block,"BLOCK %(name)s # %(comment)ls")
      #WARNING!!! blocktype 3 didn't solve my problem: had lines in a file like:
      # Block CROSSSECTIONS   #LSP-nucleon spin independent (SI) and dependent (SD) sigmas
      #the lack of a space after the hash before the comment was killing the code; tried to add blocktype3
      #to compensate but didn't work. Had to changed the file to avoid problem. 
      blocktype3 = Blueprint(Block,"BLOCK %(name)s #%(comment)ls")  #bjf> spaces can cause errors apparently if not in the file
      #blocktype10 = Blueprint(Block,"Block %(name)s #%(comment)ls")  #bjf> spaces can cause errors apparently if not in the file
      blocktype4 = Blueprint(Block,"BLOCK %(name)s")
      blocktype5 = Blueprint(Block,"BLOCK %(name)s Q= %(value)e # %(comment)ls")    #bjf> added extra blocktype to deal with some of the softsusy blocks
      blocktype6 = Blueprint(Block,"BLOCK %(name)s Q=%(value)e # %(comment)ls")    #bjf> added extra blocktype to deal with some of the softsusy blocks
      blocktype7 = Blueprint(Block,"BLOCK %(name)s Q= %(value)e")    #bjf> Need one to have no comment as well
      #bjf> need blueprints to account for possible spaces before BLOCK
      #bjf> NMSSMtools has a few weird non-slha format "blocks", which these blueprints deal with
      standardblocks += [blocktype1,blocktype2,blocktype3,blocktype4,blocktype5,blocktype6,blocktype7]
      for block in standardblocks: block.subblueprints += items
      self.items = items
      self.standardblocks = standardblocks
   def readdata(self):
      #print 'IN READDATA'
      fi = FileIterator(self.fullpath())
      self.data = construct(fi,*self.customblocks+self.standardblocks)

   def update(self,inputs):
      self.readdata() # TODO: probably not needed now
      for key,val in inputs:
         self[key] = val
   def getcontent(self,key):
      try:
         for item in self.data:
            temp = item.getcontent(key)
            if temp: 
               #print 'returning temp...'
               #print 'in getcontent'
               #print 'item', item
               #print 'key', key
               #print 'temp', temp
               return temp
      except AttributeError, msg:
          print 'ERROR! Possibly self.data does not exist! Make sure\
self.readdata() is called before trying to extract data from SLHAfile\
object!'
   def extract(self,key):
      """"""
      c = self.getcontent(key)
      if c: return c.value
      return None
   def __getitem__(self,i):
      return self.extract(i)
   def __setitem__(self,i,val):
      temp = self.getcontent(i)
      if hasattr(temp,"value"): temp.value = val
   def copyto(self,path):
      f = open(SUSYFile.add_suffix(path),"wb")
      # print 'slhacopying', SUSYFile.add_suffix(path)
      for block in self.data:
         f.write(str(block))
   def block(self,blockname,index=None,value=None):
      """Return either the block's index map or the value of the item corresponding to an index if provided, which is set to value if value is provided."""
      b = self.getcontent(blockname)
      #print 'in block'
      #print self
      #print self.name
      #print blockname
      #print index
      #print value
      #print b
      #print b.indexed
      #if index!=None:
      #   print 'value:',b.indexed[index].value
      if not b: return None
      if index!=None:   #DAMMIT DANIEL!!! IF AN INDEX IS 0 IT COUNTS AS FALSE!!! "if index:" IS BAD CODE!
         #print b.indexed[index]
         try: b.indexed[index]	#see if the index can be accessed
         except KeyError:
		msg="Error, no observable at the given index found in this block: \
Program may not have generated it (file:{0}, index:{1}, block:{2})".format(self.name,index,blockname)
                raise KeyError(msg)
         if value!=None: 
            #print b.indexed[index].value
            b.indexed[index].value = value   
         return b.indexed[index].value
      return b.indexed
   def printblock(self,blockname):
        """Print out the contents of a block in somewhat human-readable format
        Useful for debugging"""
        block = self.block(blockname)
        def getindex(item,indices):
            #unravel the nested item dictionaries
            if type(item)==type({}):
                for key,val in item.items():
                    if type(key)==type(1):
                        getindex(val,indices+[key])
            else:
                print item.value, indices
                return
        #loop through each element of the block dictionary
        for key,val in block.items():
            try:
                getindex(val,[key])
            except AttributeError:
                print key, val#, val.index
        
      
   def getobs(self,translationdict):
        """Use translation dictionary to map elements of SLHA file into
        a dictionary of observables"""
        #self.readdata()                                                 #read SLHA file (NOTE: THIS BY FAR DOMINATES THE CPU TIME FOR getobs. OPTIMISE THIS IF REQUIRED)
        obs = {}                                                        #create output dictionary
        for key,(blockname,indices) in translationdict.items():         #cycle through SLHA translation dictionary
            item = self.block(blockname)
            try:
                for i in indices:
                   item = item[i]                                       #dig through nested lists of items 
            except TypeError:                                      
                if item: item = item[indices]                           #if no more item lists are found, assume we have only one index
                #elif i==indices[0]:
                #    print key,blockname,indices
                #    print "Error reading observables from output! ...."
                #    raise
                #else: item = None   # No item found 
                else: 
                    print "Error extracting value from file {0}, block {1}, index {2}. Blueprint may \
be missing, perhaps because file object is created from a class lacking this blueprint, for \
example from 'SLHAFile' rather than 'SpectrumFile', or item may not exist in the output file\
".format(self.name,blockname,indices)
                    raise   
            except AttributeError:
                print "Error extracting value from file {0}, block {1}, index {2}. Blueprint may \
be missing, perhaps because file object is created from a class lacking this blueprint, for \
example from 'SLHAFile' rather than 'SpectrumFile'.".format(self.name,blockname,indices)
                raise
            except KeyError:
                #print "Item not found" # No item found
                continue    # No value stored for this observable! 
            try:
                obs[key] = item.value
            except AttributeError:
                obs[key] = item.comment # If no value found for this item store the comment instead
                          
        return obs

class OmegaFile(SLHAFile):
   def __init__(self,name,outputfrom=None,directory=None):
      items = [Blueprint(Item,"%(value)s %(index0)s %(index1)s -> %(index2)s %(index3)s")]
      items.append(Blueprint(Item,"%(index)s = %(value)ls"))
      #items.append(Blueprint(Item,"%(value)e # %(name)ls"))
      items.append(Blueprint(Item,"%(particle)s = %(composition)s"))
      SLHAFile.__init__(self,name,outputfrom,directory,items)

class DecayFile(SLHAFile):
    def __init__(self,name,directory):
        decayitem = Blueprint(Item," %(value)e %(index0)d %(index1)d %(index2)d # %(name)ls")
        decayblock = Blueprint(Block,"DECAY %(name)d %(width)e # %(comment)ls",[decayitem])
        SLHAFile.__init__(self,name,directory,customblocks=[decayblock])

class SpectrumFile(SLHAFile): #bjf> passed more arguments through to SLHAFile constructor
    def __init__(self,name,outputfrom=None,directory=None):
        items = [Blueprint(Item," %(index0)d %(index1)d %(value)e # %(name)ls")]
        valblock = Blueprint(Block,"BLOCK %(name)s %(var0)s %(value)e # %(comment)ls")
        SLHAFile.__init__(self,name,outputfrom,directory,items,standardblocks=[valblock])
        
class FlavourFile(SLHAFile): #bjf> designed to read flavour physics blocks in SuperIso output
    def __init__(self,name,outputfrom=None,directory=None):
        items = [
            Blueprint(Item," %(index0)d %(index1)d %(value)e %(index2)d %(index3)d %(index4)d %(index5)d %(index6)d # %(name)ls"),
            Blueprint(Item," %(index0)d %(index1)d %(value)e %(index2)d %(index3)d %(index4)d %(index5)d # %(name)ls"),
            ]
        SLHAFile.__init__(self,name,outputfrom,directory,items,standardblocks=[])
        
'''
class LHCFile(SLHAFile):
    def __init__(self,name,dirctory):
        channelitem = Blueprint(Item,"%(value)e # %(index)ls")
        higgsblock = Blueprint(Block,"# %(name)s",[channelitem])
        SLHAFile.__init__(self,name,directory,items,customblocks=[higgsblock])
        self.standardblocks = []
'''


        
