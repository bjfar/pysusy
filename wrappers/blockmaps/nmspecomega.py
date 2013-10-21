"""Mapping list for micromegas 'libdarkomega' output file"""

blockdict = {}

#BLOCK RELDEN
blockdict['omegah2' ]   =   ('RELDEN',       [1]     )
blockdict['Xf' ]        =   ('RELDEN',       [2]     ) # Gf?

#BLOCK LSP
blockdict['LSPmass' ]   =   ('LSP',          ['noindex']) # LSP mass
blockdict['~o1comp' ]   =   ('LSP',          ['~o1'] ) # LSP composition

#BLOCK DIRECTDETECTION
blockdict['csPsi' ]     =   ('DIRECTDETECTION',  [1]) # csPsi [pb]
blockdict['csNsi' ]     =   ('DIRECTDETECTION',  [2]) # csNsi [pb]
blockdict['csPsd' ]     =   ('DIRECTDETECTION',  [3]) # csPsd [pb]
blockdict['csNsd' ]     =   ('DIRECTDETECTION',  [4]) # csNsd [pb]
         
# Can't deal with the output of BLOCK CHANNELS just yet

