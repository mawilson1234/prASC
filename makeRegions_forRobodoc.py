#by: Shevaun Lewis (slightly modified by Michael Wilson)
#created: 10/22/10
# EDITED TO GIVE OUTPUT IN STANDARD SINGLE LINE FORMAT
#This script converts a list of stimulus sentences with the regions delimited
# by forward slashes (a DEL file) into a REG file, which lists the (x,y) character 
# coordinates of the boundaries of each region.

#input: python del-make_reg_file.py 'input file' (no quotes around filename)
#output: text file 'regions.reg.txt' in same directory

#input file:
#input file contains one line per item per condition.
#Item and condition numbers must correspond to those used in the EyeTrack script file.

import sys
import string
import re

try:
	del_file = open(sentences_txt_loc, 'r')
except NameError:
	print('Error: Specify sentences.txt file (open script for usage info)')
	exit()

reglines = []

for line in del_file:
    item = line.split(" ")
    s = " ".join(item[2:])
    l = s.split('\\n')
    regstarts0 = []
    for sentence in l:
        for char in sentence:
            if char == '/':
                i = sentence.index(char)
                regstarts0.append(str(i))
                sentence = sentence[0:i]+sentence[i+1:]
            nregions0 = len(regstarts0)

    reglines.append(str(item[1])+' '+str(item[0])+' '+str(nregions0)+' '+' '.join(regstarts0))

reg_file_loc = Path(re.sub(r'[^\/\\]+$', 'sentences_tmp.reg', str(sentences_txt_loc)))

reg_file = open(reg_file_loc, 'w')

for row in reglines:
    reg_file.write(str(row)+'\n')

reg_file.close()
del_file.close()