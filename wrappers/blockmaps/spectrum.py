"""Mapping list for SLHA compliant spectrum generator output files
Note: also maps extra blocks I hacked into ISAJET
"""

#from collections import OrderedDict as Odict                            #ordered dictionary (needs python 2.7+)

SLHAdict = {}   #Odict()  #Use order dictionary, with order matching file, to improve efficiency of value extraction
                          #Note: makes bugger all difference I think.
                          
#----parameter name---------block name-----index/pdg code---------------

#BLOCK SMINPUTS
SLHAdict['ialphaem' ]   =   ('SMINPUTS',    [1]     )
SLHAdict['GF'       ]   =   ('SMINPUTS',    [2]     ) 
SLHAdict['alphas'   ]   =   ('SMINPUTS',    [3]     ) 
SLHAdict['MZ'       ]   =   ('SMINPUTS',    [4]     )
SLHAdict['Mbot'     ]   =   ('SMINPUTS',    [5]     ) 
SLHAdict['Mtop'     ]   =   ('SMINPUTS',    [6]     ) 
SLHAdict['Mtau'     ]   =   ('SMINPUTS',    [7]     )

#BLOCK MINPAR
SLHAdict['M0'       ]   =   ('MINPAR',      [1]     )
SLHAdict['M12'      ]   =   ('MINPAR',      [2]     )
SLHAdict['TanB'     ]   =   ('MINPAR',      [3]     )
SLHAdict['sgnmu'    ]   =   ('MINPAR',      [4]     )
SLHAdict['A0'       ]   =   ('MINPAR',      [5]     )

#BLOCK MASS
SLHAdict['MW'       ]   =   ('MASS',        [24]    )
SLHAdict['Mh0'      ]   =   ('MASS',        [25]    )
SLHAdict['MH0'      ]   =   ('MASS',        [35]    )
SLHAdict['MA0'      ]   =   ('MASS',        [36]    )
SLHAdict['MH+'      ]   =   ('MASS',        [37]    )
SLHAdict['MsdownL'  ]   =   ('MASS',        [1000001])
SLHAdict['MsupL'    ]   =   ('MASS',        [1000002])
SLHAdict['MsstrangeL']  =   ('MASS',        [1000003])
SLHAdict['MscharmL' ]   =   ('MASS',        [1000004])
SLHAdict['Msbot1'   ]   =   ('MASS',        [1000005])
SLHAdict['Mstop1'   ]   =   ('MASS',        [1000006])
SLHAdict['MseL'     ]   =   ('MASS',        [1000011])
SLHAdict['MesnuL'   ]   =   ('MASS',        [1000012])
SLHAdict['MsmuL'    ]   =   ('MASS',        [1000013])
SLHAdict['MmusnuL'  ]   =   ('MASS',        [1000014])
SLHAdict['Mstau1'   ]   =   ('MASS',        [1000015])    
SLHAdict['MtausnuL' ]   =   ('MASS',        [1000016]) 
SLHAdict['Mgluino'  ]   =   ('MASS',        [1000021])    
SLHAdict['Mneut1'   ]   =   ('MASS',        [1000022])    
SLHAdict['Mneut2'   ]   =   ('MASS',        [1000023])    
SLHAdict['Mchar1'   ]   =   ('MASS',        [1000024])    
SLHAdict['Mneut3'   ]   =   ('MASS',        [1000025])    
SLHAdict['Mneut4'   ]   =   ('MASS',        [1000035])    
SLHAdict['Mchar2'   ]   =   ('MASS',        [1000037])    
SLHAdict['MsdownR'  ]   =   ('MASS',        [2000001])    
SLHAdict['MsupR'    ]   =   ('MASS',        [2000002])    
SLHAdict['MsstrangeR']  =   ('MASS',        [2000003])           
SLHAdict['MscharmR' ]   =   ('MASS',        [2000004])    
SLHAdict['Msbot2'   ]   =   ('MASS',        [2000005])    
SLHAdict['Mstop2'   ]   =   ('MASS',        [2000006])
SLHAdict['MseR'     ]   =   ('MASS',        [2000011])    
SLHAdict['MsmuR'    ]   =   ('MASS',        [2000013])        
SLHAdict['Mstau2'   ]   =   ('MASS',        [2000015])   

#BLOCK ALPHA
SLHAdict['alpha'    ]   =   ('ALPHA',       ['noindex'])   
 
#BLOCK STOPMIX
SLHAdict['stopmix11']   =   ('STOPMIX',     [1,1]   )   
SLHAdict['stopmix12']   =   ('STOPMIX',     [1,2]   )   
SLHAdict['stopmix21']   =   ('STOPMIX',     [2,1]   )   
SLHAdict['stopmix22']   =   ('STOPMIX',     [2,2]   )  

#BLOCK SBOTMIX
SLHAdict['sbotmix11']   =   ('SBOTMIX',     [1,1]   )   
SLHAdict['sbotmix12']   =   ('SBOTMIX',     [1,2]   )   
SLHAdict['sbotmix21']   =   ('SBOTMIX',     [2,1]   )   
SLHAdict['sbotmix22']   =   ('SBOTMIX',     [2,2]   )    

#BLOCK STAUMIX
SLHAdict['staumix11']   =   ('STAUMIX',     [1,1]   )   
SLHAdict['staumix12']   =   ('STAUMIX',     [1,2]   )   
SLHAdict['staumix21']   =   ('STAUMIX',     [2,1]   )   
SLHAdict['staumix22']   =   ('STAUMIX',     [2,2]   )    

#BLOCK NMIX
SLHAdict['nmix11']      =   ('NMIX',        [1,1]   )   
SLHAdict['nmix12']      =   ('NMIX',        [1,2]   )
SLHAdict['nmix13']      =   ('NMIX',        [1,3]   )
SLHAdict['nmix14']      =   ('NMIX',        [1,4]   )
SLHAdict['nmix21']      =   ('NMIX',        [2,1]   )
SLHAdict['nmix22']      =   ('NMIX',        [2,2]   )
SLHAdict['nmix23']      =   ('NMIX',        [2,3]   )
SLHAdict['nmix24']      =   ('NMIX',        [2,4]   )
SLHAdict['nmix31']      =   ('NMIX',        [3,1]   )
SLHAdict['nmix32']      =   ('NMIX',        [3,2]   )
SLHAdict['nmix33']      =   ('NMIX',        [3,3]   )
SLHAdict['nmix34']      =   ('NMIX',        [3,4]   )
SLHAdict['nmix41']      =   ('NMIX',        [4,1]   )
SLHAdict['nmix42']      =   ('NMIX',        [4,2]   )
SLHAdict['nmix43']      =   ('NMIX',        [4,3]   )
SLHAdict['nmix44']      =   ('NMIX',        [4,4]   )

#BLOCK UMIX
SLHAdict['umix11']      =   ('UMIX',        [1,1]   )   
SLHAdict['umix12']      =   ('UMIX',        [1,2]   )   
SLHAdict['umix21']      =   ('UMIX',        [2,1]   )   
SLHAdict['umix22']      =   ('UMIX',        [2,2]   )  

#BLOCK VMIX
SLHAdict['vmix11']      =   ('VMIX',        [1,1]   )   
SLHAdict['vmix12']      =   ('VMIX',        [1,2]   )   
SLHAdict['vmix21']      =   ('VMIX',        [2,1]   )   
SLHAdict['vmix22']      =   ('VMIX',        [2,2]   ) 

#BLOCK GAUGE
SLHAdict['Q']           =   ('GAUGE',       ['blockvalue'])
SLHAdict['g`']          =   ('GAUGE',       [1]     ) 
SLHAdict['g2']          =   ('GAUGE',       [2]     ) 
SLHAdict['g3']          =   ('GAUGE',       [3]     )

#BLOCK YU
SLHAdict['yt']          =   ('YU',          [3,3]   ) 

#BLOCK YD
SLHAdict['yb']          =   ('YD',          [3,3]   ) 

#BLOCK YE
SLHAdict['ytau']        =   ('YE',          [3,3]   ) 

#BLOCK HMIX
SLHAdict['muQ']         =   ('HMIX',        [1]     )   
SLHAdict['tanbQ']       =   ('HMIX',        [2]     )   
SLHAdict['hvevQ']       =   ('HMIX',        [3]     )   
SLHAdict['MA^2Q']       =   ('HMIX',        [4]     )   

#BLOCK MSOFT
SLHAdict['M1Q']         =   ('MSOFT',       [1]     ) 
SLHAdict['M2Q']         =   ('MSOFT',       [2]     ) 
SLHAdict['M3Q']         =   ('MSOFT',       [3]     ) 
SLHAdict['MeLQ']        =   ('MSOFT',       [31]    ) 
SLHAdict['MmuLQ']       =   ('MSOFT',       [32]    ) 
SLHAdict['MtauLQ']      =   ('MSOFT',       [33]    ) 
SLHAdict['MeRQ']        =   ('MSOFT',       [34]    ) 
SLHAdict['MmuRQ']       =   ('MSOFT',       [35]    ) 
SLHAdict['MtauRQ']      =   ('MSOFT',       [36]    ) 
SLHAdict['MqL1Q']       =   ('MSOFT',       [41]    ) 
SLHAdict['MqL2Q']       =   ('MSOFT',       [42]    ) 
SLHAdict['MqL3Q']       =   ('MSOFT',       [43]    ) 
SLHAdict['MuRQ']        =   ('MSOFT',       [44]    ) 
SLHAdict['McRQ']        =   ('MSOFT',       [45]    ) 
SLHAdict['MtRQ']        =   ('MSOFT',       [46]    ) 
SLHAdict['MdRQ']        =   ('MSOFT',       [47]    ) 
SLHAdict['MsRQ']        =   ('MSOFT',       [48]    ) 
SLHAdict['MbRQ']        =   ('MSOFT',       [49]    ) 

#BLOCK AU
SLHAdict['Au']          =   ('AU',          [1,1]   )
SLHAdict['Ac']          =   ('AU',          [2,2]   )
SLHAdict['At']          =   ('AU',          [3,3]   )

#BLOCK AD
SLHAdict['Ad']          =   ('AD',          [1,1]   )
SLHAdict['As']          =   ('AD',          [2,2]   )
SLHAdict['Ab']          =   ('AD',          [3,3]   )

#BLOCK AE
SLHAdict['Ae']          =   ('AE',          [1,1]   )
SLHAdict['Amu']         =   ('AE',          [2,2]   )
SLHAdict['Atau']        =   ('AE',          [3,3]   )

#BLOCK EXTRAS
SLHAdict['QEXTRAS']     =   ('EXTRAS',      [1]     )
SLHAdict['sin2thetawQ'] =   ('EXTRAS',      [2]     )
SLHAdict['muQEXTRAS']   =   ('EXTRAS',      [3]     )
SLHAdict['BQ']          =   ('EXTRAS',      [4]     )
SLHAdict['MHd^2Q']      =   ('EXTRAS',      [5]     )
SLHAdict['MHu^2Q']      =   ('EXTRAS',      [6]     )
SLHAdict['tanbQEXTRAS'] =   ('EXTRAS',      [7]     )

#BLOCK WARNINGS
SLHAdict['IALLOW']      =   ('WARNINGS',    [1]     )
