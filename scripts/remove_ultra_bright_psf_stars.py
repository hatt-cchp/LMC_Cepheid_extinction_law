#!/usr/bin/env


import os
import sys
import numpy as np

# Sometimes a bright star will ruin the PSF
# but not be flagged as bad by daophot. Often
# these are brighter than 12 instrumental mags


if __name__ == "__main__":

	filename=sys.argv[1]

	outfile = open("temp.lst","w")

	with open(filename) as f:

		header = [f.readline() for x in range(3)]

		for line in header:
			outfile.write(line)

		for row in f:	

			parts=[float(x) for x in row.split() ]

			if parts[3] >= 12.0:
				outfile.write(row)
		
	query="mv -f temp.lst "+filename	
	os.system(query)

	
