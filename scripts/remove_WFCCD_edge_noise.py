#!/usr/bin/env
  
import os
import sys
import numpy as np

# Sometimes a bright star will ruin the PSF
# but not be flagged as bad by daophot. Often
# these are brighter than 12 instrumental mags


if __name__ == "__main__":

	filename = sys.argv[1]

	center_x, center_y = 2048., 2048.
	allowed_rad = 1500.
	
	outfile = open("temp.coo","w")
	
	with open(filename) as f:
	
		header = [f.readline() for x in range(3)]
		
		for line in header:
			outfile.write(line)
		
		for row in f:
		
			parts=[float(x) for x in row.split() ]
			
			dx = parts[1] - center_x
			dy = parts[2] - center_y
			
			rad = np.sqrt(dx**2 + dy**2)
			
			if rad <= allowed_rad:
				outfile.write(row)	
	
	query="mv -f temp.coo "+filename
	os.system(query)
	
	
