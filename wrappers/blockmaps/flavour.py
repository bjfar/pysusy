"""Mapping list for superiso output file"""

flhadict = {}

flhadict['bsgmo']       =   ('FOBS',    (5,1,0,2,3,22)      )           # BF(b->s gamma)
flhadict['bmumu']       =   ('FOBS',    (531,1,0,2,13,-13)  )           # BF(Bs -> mu+mu-)
flhadict['Butaunu']     =   ('FOBS',    (521,1,0,2,-15,16)  )           # BF(B_u -> tau nu) 
flhadict['Delta0']      =   ('FOBS',    (521,4,0,2,313,22)  )           # Delta0(B->K* gamma)
flhadict['BDtaunuBDenu']=   ('FOBS',    (521,11,0,3,421,-15,16)  )      # BR(B+->D0 tau nu)/BR(B+-> D0 e nu)
flhadict['Rl23']        =   ('FOBS',    (321,12,0,2,-13,14) )           # R_l23
flhadict['Dstaunu']     =   ('FOBS',    (431,1,0,2,-15,16)  )           # BR(D_s->tau nu)
flhadict['Dsmunu']      =   ('FOBS',    (431,1,0,2,-13,14)  )           # BR(D_s->mu nu)
