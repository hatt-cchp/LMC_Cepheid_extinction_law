#!/usr/bin/env

import sys
import numpy as np
import os
import re

if __name__ == "__main__":


	filename=sys.argv[1]

	bad_star=0

	with open(filename) as f:
		for row in f:

			# IDs and info are always
			# separated by at least three 
			# blank spaces
			parts=row.split("   ")

			#print(parts)	
			# remove empty strings 
			# saturated stars or 
			# bad psf stars
			#print(parts)
			#continue
			for el in parts:
				if el == '': continue
				if '\n' in el: continue

	
				if 'saturated' in el: bad_star = 1
				if '?' in el: bad_star = 1
				if '*' in el: bad_star = 1


	print(bad_star)
