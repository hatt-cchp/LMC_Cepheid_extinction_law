#!/usr/bin/

import pandas as pd


info_file = '../info/Cepheid.info'


cepheid_df = pd.read_csv(info_file)

cepheid_names = cepheid_df.set_index('name').index.unique().values


start_match_rad=20

f_daomatch = open("daomatch_als_script","w")
f_daomaster = open("daomaster_als_script","w")

f_daomatch.write("#!/bin/sh\n\n")
f_daomaster.write("#!/bin/sh\n\n")

for cepheid in cepheid_names:

	# Data relevant for current cepheid
	sub_df = cepheid_df[ cepheid_df['name'].str.contains(cepheid) ].copy()

	als_names=sub_df['image'].values
	
	# Remove .fits extension, add .als
	for i in range(len(als_names)):

		als_names[i] = als_names[i].split('.fits')[0]+'.als'

		
	
	
	for als_name in als_names[1:]:

		match_file_name = cepheid+'_'+als_names[0]+'_'+als_name+'.mch'
		# Remove old *.mch instances
		f_daomatch.write('rm -f '+match_file_name+'\n')

		f_daomatch.write("daomatch << _DAOMATCH_\n")		
		f_daomatch.write(als_names[0]+"\n")
		f_daomatch.write(match_file_name+'\n')
		f_daomatch.write(als_name+"\n")
		f_daomatch.write("Y\n") # Add yes just in case daomatch wants confirmation of transformation
		f_daomatch.write("EXIT\n")
		f_daomatch.write("_DAOMATCH_\n\n")


	# Loop through progressively higher daomaster transformations

	order_transforms=["6","12","20"]

	for als_name in als_names[1:]:
	                                                                       	
		match_file_name = cepheid+'_'+als_names[0]+'_'+als_name+'.mch'
		
		# Remove existing *raw files
		f_daomaster.write("rm -f "+match_file_name.split('.mch')[0]+".raw\n")

		for order_transform in order_transforms:

			f_daomaster.write("daomaster << _DAOMASTER_\n")
			f_daomaster.write(match_file_name+'\n')
			f_daomaster.write("2,1,2\n")
			f_daomaster.write("99\n")
			f_daomaster.write(order_transform+"\n")
			f_daomaster.write(str(start_match_rad)+"\n")
			# daomaster requires manually entering of return
			# for each file that's in the list...
			for i in range(2):
				f_daomaster.write("\n")
			#for i in range(len(als_names)):
			#	f_daomaster.write("\n")
			# Count down from start_match_rad to 1 then 0 to exit
			#for i in range(start_match_rad-10,20-1,-10):
			#	f_daomaster.write(str(i)+"\n")
			for i in range(19,-1,-1):
        	        	f_daomaster.write(str(i)+"\n")

			# Assign new star IDs? 	
			f_daomaster.write("N\n")
			# A file with mean magnitudes and scatter?
			f_daomaster.write("N\n")
			# A file with corrected magnitudes and errors?
			f_daomaster.write("N\n")
			# A file with raw magnitudes and errors? 
			if order_transform != "20":
				f_daomaster.write("N\n")
			else:
				f_daomaster.write("Y\n")
				f_daomaster.write(match_file_name.split('.mch')[0]+".raw\n")
			# A file with the new transformations?
			f_daomaster.write("Y\n")
			# Output file name (default ...)
			f_daomaster.write(match_file_name+'\n')
			f_daomaster.write("OVERWRITE\n")
			# A file with the transfer table?
			f_daomaster.write("N\n")
			# Individual .COO files? 
			f_daomaster.write("N\n")
			# Simply transfer star IDs? 
			f_daomaster.write("N\n")
			
			f_daomaster.write("_DAOMASTER_\n\n")



f_daomatch.close()
f_daomaster.close()
