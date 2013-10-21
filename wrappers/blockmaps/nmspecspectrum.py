"""Mapping list for nmspec (NMSSMtools)'spectrum' output file. This is SLHA 
compliant I believe.
Note: also maps some of the extra blocks that nmspec creates
"""

#from collections import OrderedDict as Odict                            #ordered dictionary (needs python 2.7+)

SLHAdict = {}   #Odict()  #Use order dictionary, with order matching file, to improve efficiency of value extraction
                          #Note: makes bugger all difference I think.
                          
#----parameter name---------block name-----index/pdg code---------------

#options
# Call micrOmegas (default 0=no, 1=relic density only,
#				  2=dir. det. rate, 3=indir. det. rate, 4=both det. rates)
SLHAdict['usemicromegas'] = ('MODSEL',      [9]     )

#BLOCK SMINPUTS
SLHAdict['ialphaem' ]   =   ('SMINPUTS',    [1]     )
SLHAdict['GF'       ]   =   ('SMINPUTS',    [2]     ) 
SLHAdict['alphas'   ]   =   ('SMINPUTS',    [3]     ) 
SLHAdict['MZ'       ]   =   ('SMINPUTS',    [4]     )
SLHAdict['Mbot'     ]   =   ('SMINPUTS',    [5]     ) 
SLHAdict['Mtop'     ]   =   ('SMINPUTS',    [6]     ) 
SLHAdict['Mtau'     ]   =   ('SMINPUTS',    [7]     )

# Skipping "SMINPUTS Beyond SLHA" pseudo-block for now

#BLOCK MINPAR
SLHAdict['M0'       ]   =   ('MINPAR',      [1]     )   #at scale GUT
SLHAdict['M12'      ]   =   ('MINPAR',      [2]     )   #at scale GUT
SLHAdict['TanB'     ]   =   ('MINPAR',      [3]     )   #at scale MZ
SLHAdict['sgnmu'    ]   =   ('MINPAR',      [4]     )
SLHAdict['A0'       ]   =   ('MINPAR',      [5]     )   #at scale GUT

#BLOCK EXTPAR
#Note, not all of these are needed at once. See NMSSMTools examples for 
#valid combinations for different settings (i.e. CNMSSM vs general NMSSM etc)
#Note NOT COMPLETE! There are some entries I haven't gotten around to adding.
# NMSSM extra couplings and trilinears
SLHAdict['lambda'   ]   =   ('EXTPAR',      [61]     )  #at scale SUSY
SLHAdict['kappa'    ]   =   ('EXTPAR',      [62]     )
SLHAdict['Alambda'  ]   =   ('EXTPAR',      [63]     )
SLHAdict['Akappa'   ]   =   ('EXTPAR',      [64]     )  #at scale GUT
SLHAdict['mueff'    ]   =   ('EXTPAR',      [65]     )
# Gaugino masses
SLHAdict['M1'       ]   =   ('EXTPAR',      [1]     )
SLHAdict['M2'       ]   =   ('EXTPAR',      [2]     )
SLHAdict['M3'       ]   =   ('EXTPAR',      [3]     )
# Trilinear couplings
SLHAdict['AU3'      ]   =   ('EXTPAR',      [11]    )
SLHAdict['AD3'      ]   =   ('EXTPAR',      [12]    )
SLHAdict['AE3'      ]   =   ('EXTPAR',      [13]    )
# Higgs masses squared
SLHAdict['MHD^2'    ]   =   ('EXTPAR',      [21]    )
SLHAdict['MHU^2'    ]   =   ('EXTPAR',      [22]    )
# Sfermion masses
SLHAdict['ML3'      ]   =   ('EXTPAR',      [33]    )
SLHAdict['ME3'      ]   =   ('EXTPAR',      [36]    )
SLHAdict['MQ3'      ]   =   ('EXTPAR',      [43]    )
SLHAdict['MU3'      ]   =   ('EXTPAR',      [46]    )
SLHAdict['MD3'      ]   =   ('EXTPAR',      [49]    )


#BLOCK MASS
#SLHAdict['MW'       ]   =   ('MASS',        [24]    )
SLHAdict['MH1'      ]   =   ('MASS',        [25]    )   # lightest neutral scalar
SLHAdict['MH2'      ]   =   ('MASS',        [35]    )   # second neutral scalar
SLHAdict['MH3'      ]   =   ('MASS',        [45]    )   # third neutral scalar
SLHAdict['MA1'      ]   =   ('MASS',        [36]    )   # lightest pseudoscalar
SLHAdict['MA2'      ]   =   ('MASS',        [46]    )   # second pseudoscalar
SLHAdict['MH+'      ]   =   ('MASS',        [37]    )   # charged Higgs
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
SLHAdict['Mneut3'   ]   =   ('MASS',        [1000025])    
SLHAdict['Mneut4'   ]   =   ('MASS',        [1000035])
SLHAdict['Mneut5'   ]   =   ('MASS',        [1000045])
SLHAdict['Mchar1'   ]   =   ('MASS',        [1000024])     
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

#BLOCK LOWEN
SLHAdict['bsgmo'    ]   =   ('LOWEN',       [1]     )   # BR(b -> s gamma)  
SLHAdict['bsgmo+eth']   =   ('LOWEN',       [11]    )   # (BR(b -> s gamma)+Theor.Err.)
SLHAdict['bsgmo-eth']   =   ('LOWEN',       [12]    )   # (BR(b -> s gamma)-Theor.Err.)
SLHAdict['DeltaMd'  ]   =   ('LOWEN',       [2]     )   # Delta M_d in ps^-1
SLHAdict['DeltaMd+eth'] =   ('LOWEN',       [21]    )   # Delta M_d +Theor.Err.
SLHAdict['DeltaMd-eth'] =   ('LOWEN',       [22]    )   # Delta M_d -Theor.Err.
SLHAdict['DeltaMs'  ]   =   ('LOWEN',       [3]     )   # Delta M_s in ps^-1
SLHAdict['DeltaMs+eth'] =   ('LOWEN',       [31]    )   # Delta M_s +Theor.Err.
SLHAdict['DeltaMs-eth'] =   ('LOWEN',       [32]    )   # Delta M_s -Theor.Err.
SLHAdict['bmumu'  ]     =   ('LOWEN',       [4]     )   # BR(Bs -> mu+mu-)
SLHAdict['bmumu+eth']   =   ('LOWEN',       [41]    )   # BR(Bs -> mu+mu-) +Theor.Err.
SLHAdict['bmumu-eth']   =   ('LOWEN',       [42]    )   # BR(Bs -> mu+mu-) -Theor.Err.
SLHAdict['B+taunu'  ]   =   ('LOWEN',       [5]     )   # BR(B+ -> tau+ + nu_tau)  (B+ = up-bbar)
SLHAdict['B+taunu+eth'] =   ('LOWEN',       [51]    )   # BR(B+ -> tau+ + nu_tau) +Theor.Err.
SLHAdict['B+taunu-eth'] =   ('LOWEN',       [52]    )   # BR(B+ -> tau+ + nu_tau) -Theor.Err.
SLHAdict['deltaamu'  ]  =   ('LOWEN',       [6]     )   # Del_a_mu
SLHAdict['deltaamu+eth']=   ('LOWEN',       [61]    )   # Del_a_mu +Theor.Err.
SLHAdict['deltaamu-eth']=   ('LOWEN',       [62]    )   # Del_a_mu -Theor.Err.
SLHAdict['omegah2']     =   ('LOWEN',       [10]    )   # Omega h^2

#BLOCK HMIX  (scale Q is the average of the stop/sbottom masses in this case I believe)
# comment is "STOP/SBOTTOM MASSES"
SLHAdict['muQ']         =   ('HMIX',        [1]     )   # MUEFF
SLHAdict['tanbQ']       =   ('HMIX',        [2]     )   # TAN(BETA)
SLHAdict['hvevQ']       =   ('HMIX',        [3]     )   # V(Q), Higgs vev? i.e. v^2 = (v1 + v2)^2 ?
SLHAdict['MA^2Q']       =   ('HMIX',        [4]     )   # MA^2  
SLHAdict['MP^2Q']       =   ('HMIX',        [5]     )   # MP^2   

#BLOCK NMHMIX (3*3 Higgs mixing)
SLHAdict['hmix11']      =   ('NMHMIX',      [1,1]   )   # S_(1,1)
SLHAdict['hmix12']      =   ('NMHMIX',      [1,2]   )   # S_(1,2)
SLHAdict['hmix13']      =   ('NMHMIX',      [1,3]   )   # S_(1,3)
SLHAdict['hmix21']      =   ('NMHMIX',      [2,1]   )   # S_(2,1)
SLHAdict['hmix22']      =   ('NMHMIX',      [2,2]   )   # S_(2,2)
SLHAdict['hmix23']      =   ('NMHMIX',      [2,3]   )   # S_(2,3)
SLHAdict['hmix31']      =   ('NMHMIX',      [3,1]   )   # S_(3,1)
SLHAdict['hmix32']      =   ('NMHMIX',      [3,2]   )   # S_(3,2)
SLHAdict['hmix33']      =   ('NMHMIX',      [3,3]   )   # S_(3,3)

#BLOCK NMAMIX (3*3 Pseudoscalar Higgs mixing)
SLHAdict['Amix11']      =   ('NMAMIX',      [1,1]   )   # P_(1,1)
SLHAdict['Amix12']      =   ('NMAMIX',      [1,2]   )   # P_(1,2)
SLHAdict['Amix13']      =   ('NMAMIX',      [1,3]   )   # P_(1,3)
SLHAdict['Amix21']      =   ('NMAMIX',      [2,1]   )   # P_(2,1)
SLHAdict['Amix22']      =   ('NMAMIX',      [2,2]   )   # P_(2,2)
SLHAdict['Amix23']      =   ('NMAMIX',      [2,3]   )   # P_(2,3)

# 3rd generation sfermion mixing

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

#BLOCK NMNMIX (Gaugino-Higgsino mixing)
SLHAdict['nmix11']      =   ('NMNMIX',      [1,1]   )   
SLHAdict['nmix12']      =   ('NMNMIX',      [1,2]   )
SLHAdict['nmix13']      =   ('NMNMIX',      [1,3]   )
SLHAdict['nmix14']      =   ('NMNMIX',      [1,4]   )
SLHAdict['nmix15']      =   ('NMNMIX',      [1,5]   )
SLHAdict['nmix21']      =   ('NMNMIX',      [2,1]   )
SLHAdict['nmix22']      =   ('NMNMIX',      [2,2]   )
SLHAdict['nmix23']      =   ('NMNMIX',      [2,3]   )
SLHAdict['nmix24']      =   ('NMNMIX',      [2,4]   )
SLHAdict['nmix25']      =   ('NMNMIX',      [2,5]   )
SLHAdict['nmix31']      =   ('NMNMIX',      [3,1]   )
SLHAdict['nmix32']      =   ('NMNMIX',      [3,2]   )
SLHAdict['nmix33']      =   ('NMNMIX',      [3,3]   )
SLHAdict['nmix34']      =   ('NMNMIX',      [3,4]   )
SLHAdict['nmix35']      =   ('NMNMIX',      [3,5]   )
SLHAdict['nmix41']      =   ('NMNMIX',      [4,1]   )
SLHAdict['nmix42']      =   ('NMNMIX',      [4,2]   )
SLHAdict['nmix43']      =   ('NMNMIX',      [4,3]   )
SLHAdict['nmix44']      =   ('NMNMIX',      [4,4]   )
SLHAdict['nmix45']      =   ('NMNMIX',      [4,5]   )
SLHAdict['nmix51']      =   ('NMNMIX',      [5,1]   )
SLHAdict['nmix52']      =   ('NMNMIX',      [5,2]   )
SLHAdict['nmix53']      =   ('NMNMIX',      [5,3]   )
SLHAdict['nmix54']      =   ('NMNMIX',      [5,4]   )
SLHAdict['nmix55']      =   ('NMNMIX',      [5,5]   )

#BLOCK UMIX (Chargino U Mixing Matrix)
SLHAdict['umix11']      =   ('UMIX',        [1,1]   )   
SLHAdict['umix12']      =   ('UMIX',        [1,2]   )   
SLHAdict['umix21']      =   ('UMIX',        [2,1]   )   
SLHAdict['umix22']      =   ('UMIX',        [2,2]   )  

#BLOCK VMIX (Chargino V Mixing Matrix)
SLHAdict['vmix11']      =   ('VMIX',        [1,1]   )   
SLHAdict['vmix12']      =   ('VMIX',        [1,2]   )   
SLHAdict['vmix21']      =   ('VMIX',        [2,1]   )   
SLHAdict['vmix22']      =   ('VMIX',        [2,2]   ) 

#BLOCK REDCOUP (Higgs reduced couplings, as compared to a SM Higgs with same mass)
# ...by which I think they mean everything is divided by equivalent SM Higgs couplings.
# H1
SLHAdict['rg_H1_u']     =   ('REDCOUP',     [1,1]   ) # U-type fermions
SLHAdict['rg_H1_d']     =   ('REDCOUP',     [1,2]   ) # D-type fermions
SLHAdict['rg_H1_WZ']    =   ('REDCOUP',     [1,3]   ) # W,Z bosons
SLHAdict['rg_H1_g']     =   ('REDCOUP',     [1,4]   ) # Gluons
SLHAdict['rg_H1_a']     =   ('REDCOUP',     [1,5]   ) # Photons
# H2
SLHAdict['rg_H2_u']     =   ('REDCOUP',     [2,1]   ) # U-type fermions
SLHAdict['rg_H2_d']     =   ('REDCOUP',     [2,2]   ) # D-type fermions
SLHAdict['rg_H2_WZ']    =   ('REDCOUP',     [2,3]   ) # W,Z bosons
SLHAdict['rg_H2_g']     =   ('REDCOUP',     [2,4]   ) # Gluons
SLHAdict['rg_H2_a']     =   ('REDCOUP',     [2,5]   ) # Photons
# H3
SLHAdict['rg_H3_u']     =   ('REDCOUP',     [3,1]   ) # U-type fermions
SLHAdict['rg_H3_d']     =   ('REDCOUP',     [3,2]   ) # D-type fermions
SLHAdict['rg_H3_WZ']    =   ('REDCOUP',     [3,3]   ) # W,Z bosons
SLHAdict['rg_H3_g']     =   ('REDCOUP',     [3,4]   ) # Gluons
SLHAdict['rg_H3_a']     =   ('REDCOUP',     [3,5]   ) # Photons
# A1
SLHAdict['rg_A1_u']     =   ('REDCOUP',     [4,1]   ) # U-type fermions
SLHAdict['rg_A1_d']     =   ('REDCOUP',     [4,2]   ) # D-type fermions
SLHAdict['rg_A1_WZ']    =   ('REDCOUP',     [4,3]   ) # W,Z bosons
SLHAdict['rg_A1_g']     =   ('REDCOUP',     [4,4]   ) # Gluons
SLHAdict['rg_A1_a']     =   ('REDCOUP',     [4,5]   ) # Photons
# A2
SLHAdict['rg_A2_u']     =   ('REDCOUP',     [5,1]   ) # U-type fermions
SLHAdict['rg_A2_d']     =   ('REDCOUP',     [5,2]   ) # D-type fermions
SLHAdict['rg_A2_WZ']    =   ('REDCOUP',     [5,3]   ) # W,Z bosons
SLHAdict['rg_A2_g']     =   ('REDCOUP',     [5,4]   ) # Gluons
SLHAdict['rg_A2_a']     =   ('REDCOUP',     [5,5]   ) # Photons

# GAUGE AND YUKAWA COUPLINGS AT THE SUSY SCALE

#BLOCK GAUGE 
SLHAdict['Qsusy']       =   ('GAUGE',       ['blockvalue']) # (SUSY SCALE)
SLHAdict['g`_Qsusy']    =   ('GAUGE',       [1]     ) # g1=sqrt(5/3)*g` (Q,DR_bar)
SLHAdict['g2_Qsusy']    =   ('GAUGE',       [2]     ) # g2=g (Q,DR_bar)
SLHAdict['g3_Qsusy']    =   ('GAUGE',       [3]     ) # g3 (Q,DR_bar)
#BLOCK YU
SLHAdict['yt_Qsusy']    =   ('YU',          [3,3]   ) # HTOP(Q,DR_bar)
#BLOCK YD
SLHAdict['yb_Qsusy']    =   ('YD',          [3,3]   ) # HBOT(Q,DR_bar)
#BLOCK YE
SLHAdict['ytau_Qsusy']  =   ('YE',          [3,3]   ) # HTAU(Q,DR_bar)

# SOFT TRILINEAR COUPLINGS AT THE SUSY SCALE

#BLOCK AU
SLHAdict['Au_Qsusy']    =   ('AU',          [1,1]   )
SLHAdict['Ac_Qsusy']    =   ('AU',          [2,2]   )
SLHAdict['At_Qsusy']    =   ('AU',          [3,3]   )
#BLOCK AD
SLHAdict['Ad_Qsusy']    =   ('AD',          [1,1]   )
SLHAdict['As_Qsusy']    =   ('AD',          [2,2]   )
SLHAdict['Ab_Qsusy']    =   ('AD',          [3,3]   )
#BLOCK AE
SLHAdict['Ae_Qsusy']    =   ('AE',          [1,1]   )
SLHAdict['Amu_Qsusy']   =   ('AE',          [2,2]   )
SLHAdict['Atau_Qsusy']  =   ('AE',          [3,3]   )

# SOFT MASSES AT THE SUSY SCALE

#BLOCK MSOFT
SLHAdict['M1_Qsusy']    =   ('MSOFT',       [1]     ) # M1
SLHAdict['M2_Qsusy']    =   ('MSOFT',       [2]     ) # M2
SLHAdict['M3_Qsusy']    =   ('MSOFT',       [3]     ) # M3
SLHAdict['MHd^2_Qsusy'] =   ('MSOFT',       [21]    ) # M_HD^2
SLHAdict['MHu^2_Qsusy'] =   ('MSOFT',       [22]    ) # M_HU^2
SLHAdict['MeL_Qsusy']   =   ('MSOFT',       [31]    ) # M_eL
SLHAdict['MmuL_Qsusy']  =   ('MSOFT',       [32]    ) # M_muL
SLHAdict['MtauL_Qsusy'] =   ('MSOFT',       [33]    ) # M_tauL
SLHAdict['MeR_Qsusy']   =   ('MSOFT',       [34]    ) # M_eR
SLHAdict['MmuR_Qsusy']  =   ('MSOFT',       [35]    ) # M_muR
SLHAdict['MtauR_Qsusy'] =   ('MSOFT',       [36]    ) # M_tauR
SLHAdict['MqL1_Qsusy']  =   ('MSOFT',       [41]    ) # M_q1L
SLHAdict['MqL2_Qsusy']  =   ('MSOFT',       [42]    ) # M_q2L
SLHAdict['MqL3_Qsusy']  =   ('MSOFT',       [43]    ) # M_q3L
SLHAdict['MuR_Qsusy']   =   ('MSOFT',       [44]    ) # M_uR
SLHAdict['McR_Qsusy']   =   ('MSOFT',       [45]    ) # M_cR
SLHAdict['MtR_Qsusy']   =   ('MSOFT',       [46]    ) # M_tR
SLHAdict['MdR_Qsusy']   =   ('MSOFT',       [47]    ) # M_dR
SLHAdict['MsR_Qsusy']   =   ('MSOFT',       [48]    ) # M_sR
SLHAdict['MbR_Qsusy']   =   ('MSOFT',       [49]    ) # M_bR

# BLOCK NMSSMRUN (NMSSM SPECIFIC PARAMETERS THE SUSY SCALE)
SLHAdict['lambda_Qsusy']=   ('NMSSMRUN',    [1]     ) # LAMBDA(Q,DR_bar)
SLHAdict['kappa_Qsusy'] =   ('NMSSMRUN',    [2]     ) # KAPPA(Q,DR_bar)
SLHAdict['Alambda_Qsusy']=  ('NMSSMRUN',    [3]     ) # ALAMBDA
SLHAdict['Akappa_Qsusy']=   ('NMSSMRUN',    [4]     ) # AKAPPA
SLHAdict['mueff_Qsusy'] =   ('NMSSMRUN',    [5]     ) # MUEFF
SLHAdict['XIF_Qsusy']   =   ('NMSSMRUN',    [6]     ) # XIF
SLHAdict['XIS_Qsusy']   =   ('NMSSMRUN',    [7]     ) # XIS
SLHAdict['mu`_Qsusy']   =   ('NMSSMRUN',    [8]     ) # MU'
SLHAdict['MS`^2_Qsusy'] =   ('NMSSMRUN',    [9]     ) # MS'^2
SLHAdict['MS^2_Qsusy']  =   ('NMSSMRUN',    [10]    ) # MS^2
SLHAdict['M3H^2_Qsusy'] =   ('NMSSMRUN',    [11]    ) # M3H^2

# GAUGE AND YUKAWA COUPLINGS AT THE GUT SCALE
# Note, I hacked the output of nmspec so that it named these blocks differently
# to the SUSY scale versions. Breaks SLHA compliance.

#BLOCK GAUGEGUT 
SLHAdict['QGUT']        =   ('GAUGEGUT',    ['blockvalue']) # (GUT SCALE)
SLHAdict['g`_QGUT']     =   ('GAUGEGUT',    [1]     ) # g1=sqrt(5/3)*g` (MGUT,DR_bar)
SLHAdict['g2_QGUT']     =   ('GAUGEGUT',    [2]     ) # g2=g (MGUT,DR_bar)
SLHAdict['g3_QGUT']     =   ('GAUGEGUT',    [3]     ) # g3 (MGUT,DR_bar)
#BLOCK YUGUT
SLHAdict['yt_QGUT']     =   ('YUGUT',       [3,3]   ) # HTOP(MGUT,DR_bar)
#BLOCK YDGUT
SLHAdict['yb_QGUT']     =   ('YDGUT',       [3,3]   ) # HBOT(MGUT,DR_bar)
#BLOCK YEGUT
SLHAdict['ytau_QGUT']   =   ('YEGUT',       [3,3]   ) # HTAU(MGUT,DR_bar)

# SOFT TRILINEAR COUPLINGS AT THE GUT SCALE

#BLOCK AUGUT
SLHAdict['Au_QGUT']     =   ('AUGUT',       [1,1]   )
SLHAdict['Ac_QGUT']     =   ('AUGUT',       [2,2]   )
SLHAdict['At_QGUT']     =   ('AUGUT',       [3,3]   )
#BLOCK ADGUT
SLHAdict['Ad_QGUT']     =   ('ADGUT',       [1,1]   )
SLHAdict['As_QGUT']     =   ('ADGUT',       [2,2]   )
SLHAdict['Ab_QGUT']     =   ('ADGUT',       [3,3]   )
#BLOCK AEGUT
SLHAdict['Ae_QGUT']     =   ('AEGUT',       [1,1]   )
SLHAdict['Amu_QGUT']    =   ('AEGUT',       [2,2]   )
SLHAdict['Atau_QGUT']   =   ('AEGUT',       [3,3]   )

# SOFT MASSES SQUARED AT THE GUT SCALE
#BLOCK MSOFTGUT
SLHAdict['M1_QGUT']     =   ('MSOFTGUT',    [1]     ) # M1
SLHAdict['M2_QGUT']     =   ('MSOFTGUT',    [2]     ) # M2
SLHAdict['M3_QGUT']     =   ('MSOFTGUT',    [3]     ) # M3
SLHAdict['MHd^2_QGUT']  =   ('MSOFTGUT',    [21]    ) # M_HD^2
SLHAdict['MHu^2_QGUT']  =   ('MSOFTGUT',    [22]    ) # M_HU^2
SLHAdict['MeL^2_QGUT']  =   ('MSOFTGUT',    [31]    ) # M_eL^2
SLHAdict['MmuL^2_QGUT'] =   ('MSOFTGUT',    [32]    ) # M_muL^2
SLHAdict['MtauL^2_QGUT']=   ('MSOFTGUT',    [33]    ) # M_tauL^2
SLHAdict['MeR^2_QGUT']  =   ('MSOFTGUT',    [34]    ) # M_eR^2
SLHAdict['MmuR^2_QGUT'] =   ('MSOFTGUT',    [35]    ) # M_muR^2
SLHAdict['MtauR^2_QGUT']=   ('MSOFTGUT',    [36]    ) # M_tauR^2
SLHAdict['MqL1^2_QGUT'] =   ('MSOFTGUT',    [41]    ) # M_q1L^2
SLHAdict['MqL2^2_QGUT'] =   ('MSOFTGUT',    [42]    ) # M_q2L^2
SLHAdict['MqL3^2_QGUT'] =   ('MSOFTGUT',    [43]    ) # M_q3L^2
SLHAdict['MuR^2_QGUT']  =   ('MSOFTGUT',    [44]    ) # M_uR^2
SLHAdict['McR^2_QGUT']  =   ('MSOFTGUT',    [45]    ) # M_cR^2
SLHAdict['MtR^2_QGUT']  =   ('MSOFTGUT',    [46]    ) # M_tR^2
SLHAdict['MdR^2_QGUT']  =   ('MSOFTGUT',    [47]    ) # M_dR^2
SLHAdict['MsR^2_QGUT']  =   ('MSOFTGUT',    [48]    ) # M_sR^2
SLHAdict['MbR^2_QGUT']  =   ('MSOFTGUT',    [49]    ) # M_bR^2

#BLOCK NMSSMRUNGUT (NMSSM SPECIFIC PARAMETERS AT THE GUT SCALE)
SLHAdict['lambda_QGUT'] =   ('NMSSMRUNGUT', [1]     ) # LAMBDA(MGUT,DR_bar)
SLHAdict['kappa_QGUT']  =   ('NMSSMRUNGUT', [2]     ) # KAPPA(MGUT,DR_bar)
SLHAdict['Alambda_QGUT']=   ('NMSSMRUNGUT', [3]     ) # ALAMBDA
SLHAdict['Akappa_QGUT'] =   ('NMSSMRUNGUT', [4]     ) # AKAPPA
SLHAdict['mueff_QGUT']  =   ('NMSSMRUNGUT', [5]     ) # MUEFF
SLHAdict['XIF_QGUT']    =   ('NMSSMRUNGUT', [6]     ) # XIF
SLHAdict['XIS_QGUT']    =   ('NMSSMRUNGUT', [7]     ) # XIS
SLHAdict['mu`_QGUT']    =   ('NMSSMRUNGUT', [8]     ) # MU'
SLHAdict['MS`^2_QGUT']  =   ('NMSSMRUNGUT', [9]     ) # MS'^2
SLHAdict['MS^2_QGUT']   =   ('NMSSMRUNGUT', [10]    ) # MS^2
SLHAdict['M3H^2_QGUT']  =   ('NMSSMRUNGUT', [11]    ) # M3H^2

#BLOCK FINETUNING (note, I also hacked this blockname into the nmspec output)
# FINE-TUNING parameter d(ln Mz^2)/d(ln PG^2)
SLHAdict['tun_MHu']     =   ('FINETUNING',  [1]     ) # PG=MHU
SLHAdict['tun_MHd']     =   ('FINETUNING',  [2]     ) # PG=MHD
SLHAdict['tun_MS']      =   ('FINETUNING',  [3]     ) # PG=MS
SLHAdict['tun_M0']      =   ('FINETUNING',  [4]     ) # PG=M0
SLHAdict['tun_M1']      =   ('FINETUNING',  [5]     ) # PG=M1
SLHAdict['tun_M2']      =   ('FINETUNING',  [6]     ) # PG=M2
SLHAdict['tun_M3']      =   ('FINETUNING',  [7]     ) # PG=M3
SLHAdict['tun_M12']     =   ('FINETUNING',  [8]     ) # PG=M12
SLHAdict['tun_Alambda'] =   ('FINETUNING',  [9]     ) # PG=ALAMBDA
SLHAdict['tun_Akappa']  =   ('FINETUNING',  [10]    ) # PG=AKAPPA
SLHAdict['tun_A0']      =   ('FINETUNING',  [11]    ) # PG=A0
SLHAdict['tun_XIF']     =   ('FINETUNING',  [12]    ) # PG=XIF
SLHAdict['tun_XIS']     =   ('FINETUNING',  [13]    ) # PG=XIS
SLHAdict['tun_Mup']     =   ('FINETUNING',  [14]    ) # PG=MUP
SLHAdict['tun_MSP']     =   ('FINETUNING',  [15]    ) # PG=MSP
SLHAdict['tun_M3H']     =   ('FINETUNING',  [16]    ) # PG=M3H
SLHAdict['tun_lambda']  =   ('FINETUNING',  [17]    ) # PG=lambda
SLHAdict['tun_kappa']   =   ('FINETUNING',  [18]    ) # PG=kappa
SLHAdict['tun_HTOP']    =   ('FINETUNING',  [19]    ) # PG=HTOP
SLHAdict['tun_G0']      =   ('FINETUNING',  [20]    ) # PG=G0
SLHAdict['tun_MGUT']    =   ('FINETUNING',  [21]    ) # PG=MGUT
SLHAdict['tun_MAX']     =   ('FINETUNING',  [22]    ) # MAX
SLHAdict['tun_IMAX']    =   ('FINETUNING',  [23]    ) # IMAX (index of max? probably no use to us)

#BLOCK FINETUNING (note, I also hacked this blockname into the nmspec output)
# FINE-TUNING parameter d(ln Mz^2)/d(ln PG^2)
SLHAdict['tun_MHu']     =   ('FINETUNING',  [1]     ) # PG=MHU

#BLOCK DERIVATIVES (new block I added to store tuning related derivatives)
SLHAdict['dldMZ2']      =   ('DERIVATIVES', [1]     ) # d(lambda)/d(MZ^2) (D1Z)
SLHAdict['dkdMZ2']      =   ('DERIVATIVES', [2]     ) # d(kappa) /d(MZ^2) (D2Z)
SLHAdict['dtdMZ2']      =   ('DERIVATIVES', [3]     ) # d(tanb)  /d(MZ^2) (D3Z)
SLHAdict['dldt']        =   ('DERIVATIVES', [4]     ) # d(lambda)/d(tanb) (D1T)
SLHAdict['dkdt']        =   ('DERIVATIVES', [5]     ) # d(kappa) /d(tanb) (D2T)
SLHAdict['dtdt']        =   ('DERIVATIVES', [6]     ) # d(tanb)  /d(tanb) (D3T)
SLHAdict['dldmu']       =   ('DERIVATIVES', [7]     ) # d(lambda)/d(mu)   (D1M)
SLHAdict['dkdmu']       =   ('DERIVATIVES', [8]     ) # d(kappa) /d(mu)   (D2M)
SLHAdict['dtdmu']       =   ('DERIVATIVES', [9]     ) # d(tanb)  /d(mu)   (D3M)
SLHAdict['dA1']         =   ('DERIVATIVES', [10]    ) # D2T*D3M-D2M*D3T
SLHAdict['dA2']         =   ('DERIVATIVES', [11]    ) # D3T*D1M-D3M*D1T
SLHAdict['dA3']         =   ('DERIVATIVES', [12]    ) # D1T*D2M-D1M*D2T
SLHAdict['det123']      =   ('DERIVATIVES', [13]    ) # Determinant: A1*D1Z+A2*D2Z+A3*D3Z
        
#BLOCK RCROSSSECTIONS (note, hacked in this blockname too)
# REDUCED CROSS SECTIONS AT LHC
# NOTE! VBF/VH->H1->ZZ/WW and ggF->H1->ZZ/WW changed to just ZZ final state!
# Pretty sure this is what was coming out previously anyway! Compute WW final
# state version from the ZZ version by dividing out BR(H->ZZ)/BR(H->ZZ)_SM and 
# multiplying in BR(H->WW)/BR(H->WW)_SM (the ggF->H production cross-section 
# bit is the same!)
# H1 production
SLHAdict['VBF/VH->H1->tautau']  = ('RCROSSSECTIONS', [11] )
SLHAdict['ggF->H1->tautau']     = ('RCROSSSECTIONS', [12] ) 
SLHAdict['VBF/VH->H1->bb']      = ('RCROSSSECTIONS', [13] ) 
SLHAdict['ttH->H1->bb']         = ('RCROSSSECTIONS', [14] )
SLHAdict['VBF/VH->H1->ZZ']      = ('RCROSSSECTIONS', [15] )
SLHAdict['ggF->H1->ZZ']         = ('RCROSSSECTIONS', [16] )
SLHAdict['VBF/VH->H1->aa']      = ('RCROSSSECTIONS', [17] )
SLHAdict['ggF->H1->aa']         = ('RCROSSSECTIONS', [18] )
# H2 production
SLHAdict['VBF/VH->H2->tautau']  = ('RCROSSSECTIONS', [21] )
SLHAdict['ggF->H2->tautau']     = ('RCROSSSECTIONS', [22] ) 
SLHAdict['VBF/VH->H2->bb']      = ('RCROSSSECTIONS', [23] ) 
SLHAdict['ttH->H2->bb']         = ('RCROSSSECTIONS', [24] )
SLHAdict['VBF/VH->H2->ZZ']      = ('RCROSSSECTIONS', [25] )
SLHAdict['ggF->H2->ZZ']         = ('RCROSSSECTIONS', [26] )
SLHAdict['VBF/VH->H2->aa']      = ('RCROSSSECTIONS', [27] )
SLHAdict['ggF->H2->aa']         = ('RCROSSSECTIONS', [28] )
# H3 production
SLHAdict['VBF/VH->H3->tautau']  = ('RCROSSSECTIONS', [31] )
SLHAdict['ggF->H3->tautau']     = ('RCROSSSECTIONS', [32] ) 
SLHAdict['VBF/VH->H3->bb']      = ('RCROSSSECTIONS', [33] ) 
SLHAdict['ttH->H3->bb']         = ('RCROSSSECTIONS', [34] )
SLHAdict['VBF/VH->H3->ZZ']      = ('RCROSSSECTIONS', [35] )
SLHAdict['ggF->H3->ZZ']         = ('RCROSSSECTIONS', [36] )
SLHAdict['VBF/VH->H3->aa']      = ('RCROSSSECTIONS', [37] )
SLHAdict['ggF->H3->aa']         = ('RCROSSSECTIONS', [38] )

#BLOCK BRANCHINGRATIOS (note, hacked in this blockname too)
# Higgs branching ratios to SM particles
# SM=Hi indicates which NMSSM Higgs mass was used (I think)
SLHAdict['BR(h->tautau)_SM=H1'] = ('BRANCHINGRATIOS', [1] )
SLHAdict['BR(h->bbar)_SM=H1']   = ('BRANCHINGRATIOS', [2] )
SLHAdict['BR(h->ZZ)_SM=H1']     = ('BRANCHINGRATIOS', [3] )
SLHAdict['BR(h->WW)_SM=H1']     = ('BRANCHINGRATIOS', [4] )
SLHAdict['BR(h->aa)_SM=H1']     = ('BRANCHINGRATIOS', [5] )
SLHAdict['BR(h->tautau)_SM=H2'] = ('BRANCHINGRATIOS', [6] )
SLHAdict['BR(h->bbar)_SM=H2']   = ('BRANCHINGRATIOS', [7] )
SLHAdict['BR(h->ZZ)_SM=H2']     = ('BRANCHINGRATIOS', [8] )
SLHAdict['BR(h->WW)_SM=H2']     = ('BRANCHINGRATIOS', [9] )
SLHAdict['BR(h->aa)_SM=H2']     = ('BRANCHINGRATIOS',[10] )
SLHAdict['BR(h->tautau)_SM=H3'] = ('BRANCHINGRATIOS',[11] )
SLHAdict['BR(h->bbar)_SM=H3']   = ('BRANCHINGRATIOS',[12] )
SLHAdict['BR(h->ZZ)_SM=H3']     = ('BRANCHINGRATIOS',[13] )
SLHAdict['BR(h->WW)_SM=H3']     = ('BRANCHINGRATIOS',[14] )
SLHAdict['BR(h->aa)_SM=H3']     = ('BRANCHINGRATIOS',[15] )

