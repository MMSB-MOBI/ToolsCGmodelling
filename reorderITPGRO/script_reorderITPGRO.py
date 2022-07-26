#!/usr/bin/env python
# Autor : Romuald Marin <romuald.mrn@outlook.fr> 

import sys

try:
    file1 = sys.argv[1]
    file2 = sys.argv[2]
except IndexError:
    print("Error ! You should give 2 files " )
    print("    Exemple : python3 bipbip.py 4a3Cit_CG.itp CIT.gro ")
    quit()


if file1.endswith("itp"):
    itpname = file1
if file2.endswith("itp"):
    itpname = file2
if file2.endswith("gro"):
    groname = file2
if file1.endswith("gro"):
    groname = file1

#Well now we have our 2 files ! 

#So we can start to parse the gro file to find out new atoms/beads order

#init dictionnary
grOrder = { }
#init position 
pos = 1 

for line in open( groname).readlines():
    # https://manual.gromacs.org/documentation/5.1/user-guide/file-formats.html#gro
    residue_number = line[0:5].strip(" ")
    residue_name = line[5:10].strip(" ")
    atom_name = line[10:15].strip(" ")
    atom_number = line[ 15:20] .strip(" ")
    #get the first molecule
    if ( (residue_number.isdigit()) & (atom_name != "") ):
        grOrder[ atom_name ]= pos
        pos += 1

#now we have the new order 
 

#let's go for the ITP file
# https://manual.gromacs.org/current/reference-manual/topologies/topology-file-formats.html

#init id old, new id 
dictnewpos = { }

def splitMyITPline( l : str):
    l = l.strip('\n')
    l = l.strip(" ")
    l = l.replace("\t", " ")
    return [i for i in l.split(" ") if  i != ""  ]

def atom( line : str ) :
    #Get atom name
    d = splitMyITPline(line)
    try:
        newid = str(grOrder[ d[4] ])
        dictnewpos[ str(d[0]) ] = newid
        d[0] = newid
    except KeyError:
        print("Error !" )
        print(d[4]+" not in gro file ")
        quit()
 
    #change first id 
    return "\t".join(d) 

def pair( line ) :
    d = splitMyITPline(line)
    old1 =  d[0] 
    new1 = dictnewpos[ old1 ] 
    
    old2 =  d[1] 
    new2 = dictnewpos[ old2 ] 
    
    d[0] = new1
    d[1] = new2
    
    return "\t".join(d) 

def bond( line ) :
    d = splitMyITPline(line)
    old1 =  d[0] 
    new1 = dictnewpos[ old1 ] 
    
    old2 =  d[1]
    new2 = dictnewpos[ old2 ] 
    
    d[0] = new1
    d[1] = new2
    
    return "\t".join(d) 

def dihedral( line ) :
    d = splitMyITPline(line)
    old1 =  d[0] 
    new1 = dictnewpos[ old1 ] 
    
    old2 =  d[1] 
    new2 = dictnewpos[ old2 ] 
    
    old3 =  d[2] 
    new3 = dictnewpos[ old3 ] 
    
    old4 =  d[3] 
    new4 = dictnewpos[ old4 ] 
 
    d[0] = new1
    d[1] = new2
    d[2] = new3
    d[3] = new4
    
    return "\t".join(d) 

def angle( line ) :
    d = splitMyITPline(line)
    
    old1 =  d[0] 
    new1 = dictnewpos[ old1 ] 
    
    old2 =  d[1] 
    new2 = dictnewpos[ old2 ] 
    
    old3 =  d[2] 
    new3 = dictnewpos[ old3 ] 
 
    d[0] = new1
    d[1] = new2
    d[2] = new3
    
    return "\t".join(d) 

def exclusion( line ) :
    d = splitMyITPline(line)
    
    l = []
    for i in d : 
        l.append( dictnewpos[ i ] )
 
    return "\t".join(l) 
    
lineAtomUnsorted = []
state = ""
for line in open( itpname).readlines():
    lineclear = line.strip("\n")
    if (lineclear.strip().replace(" ", "") == "[ atoms ]".replace(" ", "")):
        state = "atom"
        print( lineclear)
        continue
    if (lineclear.strip().replace(" ", "") == "[ bonds ]".replace(" ", "")):
        state = "bonds"
        print( lineclear)
        continue

    if (lineclear.strip().replace(" ", "") == "[ angles ]".replace(" ", "")):
        state = "angles"
        print( lineclear)
        continue
    
    if (lineclear.strip().replace(" ", "") == "[ pairs ]".replace(" ", "")):
        state = "pairs"
        print( lineclear)
        continue
    
    if (lineclear.strip().replace(" ", "") == "[ dihedrals ]".replace(" ", "")):
        state = "dihedrals"
        print( lineclear)
        continue
    
    if (lineclear.strip().replace(" ", "") == "[ exclusions ]".replace(" ", "")):
        state = "exclusions"
        print( lineclear)
        continue

    if (lineclear == "") or (lineclear.startswith(";")):
        if (state == "atom") and lineAtomUnsorted : 
            #Time to print the sorted tab 
            for i in sorted(lineAtomUnsorted, key=lambda x: int(x.split("\t")[0]))  : 
                print( i )
            print( "\n")
            lineAtomUnsorted = []
            continue
        else : 
            print( lineclear)
            continue
    if state == "":
        print( lineclear)
    
    if (state == "atom"):
        lineAtomUnsorted.append( atom( lineclear ) )
    if (state == "bonds"):
        print(bond( lineclear ) )
    if (state == "angles"):
        print(angle( lineclear ) )
    if (state == "pairs"):
        print(pair( lineclear ) )
    if (state == "dihedrals"):
        print(dihedral( lineclear ) )
    if (state == "exclusions"):
        print(exclusion( lineclear ) )
        
