#!/usr/bin/env python
# Autor : Romuald Marin <romuald.mrn@outlook.fr> 

import sys
import argparse

parser = argparse.ArgumentParser(description='Script for combining a mapping index file with a pdb file. The mapping index file can containe either atom numbers or names which can be found in the corresponding pdb file. The output pdb file along with the corresponding itp file can be added to CG2AT for converting CG into Atomistic resolution.')

parser.add_argument('-p',"--pdb",  required=True,
                    help='Give the pdb file')

parser.add_argument('-n',"--ndx",  required=True,
                    help='Give the ndx file')

parser.add_argument('-o',"--output", default="OUT.pdb",
                    help='Output file')

args = parser.parse_args()

mapp = open( args.ndx, 'r').readlines()
pdb = open(args.pdb,'r').readlines()
out = open( args.output, 'w')

#Is ID provide by ndx file are in atom number or atom name
IDnumber = None
D = {}
orderBeads = []
currentbead = ""

lineBeforeATOM = []
lineAfterATOM = []
lineATOM = [ ]
beforeATOM = False



for line in mapp:
    line = line.strip("\n")
    if line.startswith('['):
        currentbead = line.replace(" ", "").strip("[").strip("]")
        orderBeads.append(currentbead )
        
        D[ currentbead] = ''
    elif line == "" or line.startswith("END"):
        continue
    else:
        listID = line.strip(" ").split(' ')
        if IDnumber == None:
            IDnumber = listID[0].isdigit()
        D[ currentbead] = listID
list_number_name = []       
        
if IDnumber :
    for line in pdb:
        line = line.strip("\n")
        if line.startswith('ATOM'):
            lineATOM.append(line)
            beforeATOM = True
        elif (not beforeATOM) and (not line.startswith('ATOM')):
            lineBeforeATOM.append(line)
        elif beforeATOM and (not line.startswith('ATOM')):
            lineAfterATOM.append(line)
        else:
            print("QUOI !??? Weird thing happend", line) 
elif IDnumber == False:
    #Besoin de faire une table de correspondance entre ligne et Atom name
    for line in pdb:
        line = line.strip("\n")
        if line.startswith('ATOM'):
            #get atom name
            pasedLine = [i for i in line.split(' ') if i != '']  
            list_number_name.append(pasedLine[2])
            lineATOM.append(line )
            beforeATOM = True
        elif (not beforeATOM) and (not line.startswith('ATOM')):
            lineBeforeATOM.append(line)
        elif beforeATOM and (not line.startswith('ATOM')):
            lineAfterATOM.append(line)
        else:
            print("QUOI !??? Weird thing happend", line) 
else :
    print( "QUOI !??? atom number of atom name !!???" )

# print(list_number_name)

#check atom in double
#reverse the beads dico 
reverseD = {}
for key in D:
    for i in D[key]:
        try:
            reverseD[ i ].append( key )
        except KeyError:
            reverseD[ i ] = [ key ]


for l in lineBeforeATOM:
    out.write(l+"\n"  )
    
for actualBead in orderBeads:
    out.write( '[ '+actualBead+' ]\n')
    for atom in D[actualBead]:
        #Si l'atom est partager par plusieurs beads 
        if len( reverseD[ atom ]) > 1:
            print('This atom can be in several beads could you choose one ?')
            if IDnumber:
                print('\tpdb line :    '+ lineATOM[ int(atom ) -1 ].strip("\n") )
            else:
                try:
                    print('\tpdb line :    '+lineATOM[ list_number_name.index(atom) ].strip("\n") ) 
                except ValueError:
                    print( atom, "not in the pdb file. ")
                    exit()
            while True:
                inputbead = str(input("Please choose your bead betwen "+', '.join(reverseD[ atom ])+':  '))
                if inputbead in reverseD[ atom ]:
                    #ok correct answer 
                    #if current bead is choosen then write it 
                    if actualBead == inputbead:
                        if IDnumber:
                            out.write(lineATOM[ int(atom ) -1 ]+"\n" )
                        else:
                            out.write(lineATOM[ list_number_name.index(atom) ]+"\n" )
                    #and then remove it 
                    for otherbead in reverseD[ atom ]:
                        if otherbead != inputbead:
                            D[otherbead].remove( atom )
                            reverseD[atom].remove( otherbead )
                    break
                else:
                    print( '\tWrong answer !')
        else:
            if IDnumber:
                out.write(lineATOM[ int(atom ) -1 ]+"\n" )
            else:
                out.write(lineATOM[ list_number_name.index(atom) ]+"\n" )

for l in lineAfterATOM:
    out.write(l+"\n" )
