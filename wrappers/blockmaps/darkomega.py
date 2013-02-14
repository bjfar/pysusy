"""Mapping list for micromegas 'libdarkomega' output file"""

blockdict = {}

#BLOCK OMEGA
blockdict['omegah2' ]   =   ('OMEGA',       (1)     )
blockdict['GF'      ]   =   ('OMEGA',       (2)     ) 

#BLOCK CONSTRAINTS
blockdict['deltaamu']   =   ('CONSTRAINTS', (1)     ) 
blockdict['bsgmo'   ]   =   ('CONSTRAINTS', (2)     ) 
blockdict['bmumu'   ]   =   ('CONSTRAINTS', (3)     ) 
blockdict['deltarho']   =   ('CONSTRAINTS', (4)     ) 

#BLOCK CROSSSECTIONS
blockdict['sigmaLSPpSI'] =  ('CROSSSECTIONS', (1)   ) 
blockdict['dsigmaLSPpSI'] = ('CROSSSECTIONS', (5)   ) 


