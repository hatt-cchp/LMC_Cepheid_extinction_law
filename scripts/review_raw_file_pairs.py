#!/usr/bin/env

import glob
import numpy as np
import matplotlib.pyplot as plt


"""

A valid set of transformations will be reflected in the
delta-mag plot as a clear offset or a CMD. Anything else
will show that there was trouble in matching the photometry
files and need to be fixed.


"""


raw_files = glob.glob("../matching/*.raw")

for raw_file in raw_files:

	mag1=[]
	mag2=[]

	with open(raw_file,"r") as f:

		# Reject header
		for i in range(3): _ = f.readline()

		for row in f:
		
			parts=row.split()
			
			mag1.append(float(parts[3]))
			mag2.append(float(parts[5]))

	mag1=np.array(mag1)
	mag2=np.array(mag2)
	plt.scatter(mag1,mag1-mag2,s=0.5)
	plt.title(raw_file)
	plt.ylim(-3,3)
	plt.xlim(10,20)
	plt.ylabel('ref mag - comp mag')
	plt.xlabel('ref mag')
	plt.show()
	

