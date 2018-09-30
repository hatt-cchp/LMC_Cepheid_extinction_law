#!/usr/bin/

import pandas as pd
import os


info_file = '../info/Cepheid.info'


cepheid_df = pd.read_csv(info_file)

cepheid_names = cepheid_df.set_index('name').index.unique().values


start_match_rad=20

f = open("daomatch_daomaster_als_script","w")

f.write("#!/bin/sh\n\n")

for cepheid in cepheid_names:

	# Data relevant for current cepheid
	sub_df = cepheid_df[ cepheid_df['name'].str.contains(cepheid) ].copy()

	als_names=sub_df['image'].values
	
	# Remove .fits extension, add .als
	for i in range(len(als_names)):

		als_names[i] = als_names[i].split('.fits')[0]+'.als'

		
	# Remove old *.mch instances
	f.write("rm -f "+cepheid+".mch\n\n")

	f.write("daomatch << _DAOMATCH_\n")

	f.write(als_names[0]+"\n")
	f.write(cepheid+'.mch\n')
	
	for als_name in als_names[1:]:
		f.write(als_name+"\n")
		f.write("Y\n") # Add yes just in case daomatch wants confirmation of transformation

	f.write("EXIT\n")
	f.write("_DAOMATCH_\n\n")

	# Remove existing *raw files
	os.system("rm -f "+cepheid+".raw\n")

	# Loop through progressively higher daomaster transformations
	order_transforms=["6","12","20"]
	for order_transform in order_transforms:

		f.write("daomaster << _DAOMASTER_\n")
		f.write(cepheid+'.mch\n')
		f.write("3,0.5,6\n")
		f.write("99\n")
		f.write(order_transform+"\n")
		f.write(str(start_match_rad)+"\n")
		# daomaster requires manually entering of return
		# for each file that's in the list...
		for i in range(len(als_names)):
			f.write("\n")
		# Count down from start_match_rad to 1 then 0 to exit
		for i in range(start_match_rad-1,-1,-1):
			f.write(str(i)+"\n")

		# Assign new star IDs? 	
		f.write("N\n")
		# A file with mean magnitudes and scatter?
		f.write("N\n")
		# A file with corrected magnitudes and errors?
		f.write("N\n")
		# A file with raw magnitudes and errors? 
		if order_transform != "20":
			f.write("N\n")
		else:
			f.write("Y\n")
			f.write(cepheid+".raw\n")
		# A file with the new transformations?
		f.write("Y\n")
		# Output file name (default ...)
		f.write(cepheid+'.mch\n')
		f.write("OVERWRITE\n")
		# A file with the transfer table?
		f.write("N\n")
		# Individual .COO files? 
		f.write("N\n")
		# Simply transfer star IDs? 
		f.write("N\n")
		
		f.write("_DAOMASTER_\n\n")



f.close()
