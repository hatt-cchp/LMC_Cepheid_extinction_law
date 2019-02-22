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

to_review_file = "../matching/to_review.dat"
os.system("rm -f "+to_review_file)

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
	fig = plt.figure()
	plt.scatter(mag1,mag1-mag2,s=0.5)
	plt.title(raw_file)
	plt.ylim(-4,4)
	plt.xlim(10,23)
	plt.ylabel('ref mag - comp mag')
	plt.xlabel('ref mag')
	print(raw_file)
	#plt.draw()
	#plt.waitforbuttonpress(0)
	#if_keep  = input("Record as needing update: 1; your choice: ")
	#plt.close(fig)

	#if if_keep == "1":
	#	with open(to_review_file,"a") as outfile:
	#		outfile.write(raw_file+"\n")
	plt.show()
	

