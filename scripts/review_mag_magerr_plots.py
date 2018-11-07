#!/usr/bin/env

import os
import glob
import numpy as np
import matplotlib.pyplot as plt


"""

A valid set of transformations will be reflected in the
delta-mag plot as a clear offset or a CMD. Anything else
will show that there was trouble in matching the photometry
files and need to be fixed.


"""

to_review_file = "../als_star_files/to_review.dat"
os.system("rm -f "+to_review_file)

als_files = glob.glob("../als_star_files/*.als")

for als_file in als_files:

	mag=[]
	magerr=[]

	with open(als_file,"r") as f:

		# Reject header
		for i in range(3): _ = f.readline()

		for row in f:
		
			parts=row.split()
			
			mag.append(float(parts[3]))
			magerr.append(float(parts[4]))

	mag=np.array(mag)
	magerr=np.array(magerr)
	fig = plt.figure()
	plt.scatter(mag,magerr,s=0.5)
	plt.title(als_file)
	plt.ylim(0,0.5)
	plt.xlim(10,23)
	plt.ylabel('magerr')
	plt.xlabel('mag')
	print(als_file)
	plt.draw()
	plt.waitforbuttonpress(0)
	if_keep  = input("Record as needing update: 1; your choice: ")
	plt.close(fig)

	if if_keep == "1":
		with open(to_review_file,"a") as outfile:
			outfile.write(als_file+"\n")
	#plt.show()
	

