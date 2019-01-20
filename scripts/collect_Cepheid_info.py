#!/usr/bin/env


import glob
import astropy.io.fits as pyfits
import pandas as pd
import datetime

dirs=["Dec2009Im6firstNightsBeforeSp/","Nov2008Imaging6nights/*/","Dec2009Im4nights4spectra/HV*/"]


allowed_prefixes=["dbccd","sccd","fbccd"]


copy_file=open("copy_cepheid_obs","w")

df = pd.DataFrame()

for curr_dir in  dirs:

	for prefix in allowed_prefixes:
	
		files=glob.glob(curr_dir+prefix+"*.fits")

		for curr_file in files:
			hdulist = pyfits.open(curr_file)
			object_name=hdulist[0].header['OBJECT']


			# Ignore sky imagse
			if "sky" in object_name: continue

			# Sometimes the filter is append to the object name
			if " " in object_name: 
				object_name_parts = object_name.split(" ")
				if object_name_parts[0].upper() == "HV":
					object_name = object_name_parts[0] + object_name_parts[1]
				else:
					object_name = object_name_parts[0]
				
			
			print(curr_file,object_name)

			
			

			if object_name[0:2].upper() == "HV": # upper since a few cases of Hv

				
				# normalize name by removing underscore 
				if "_" in object_name:
					object_name=object_name[0:2]+object_name[3:]

				# Remove alias with /
				if "/" in object_name:
					object_name=object_name.split('/')[0]

					# HV879 and HV2257 are in the same
					# field-of-view
					if object_name == "HV879" or object_name == "HV2257":
						object_name = "HV878"

						

				# Remove preceeding zeros from object_name
				# Correct cases of "Hv"
				object_name=object_name[0:2].upper()+str(int(object_name[2:]))

				if object_name == "HV879" or object_name == "HV2257":
					object_name = "HV878"

				if object_name == "HV2729":
					object_name = "HV2749"



				if  "HV2836" in object_name: continue # This is not supposed to be included






				filter_name=hdulist[0].header['FILTER']
				date_obs=hdulist[0].header['DATE-OBS']
				exptime=hdulist[0].header['EXPTIME']
		
				# Sometimes _filter is append to the filter name
				if "_FILTER" in filter_name.upper():
					filter_name = filter_name.split("_")[0]


				if prefix == "sccd": 
					ut_start = hdulist[0].header["UTSTART"]
					ut_end   = hdulist[0].header["UTEND"]
				elif prefix == "dbccd" or prefix == "fbccd":
					# For dbccd, make seconds decimal
					ut_start = hdulist[0].header["UT-TIME"]+'.0'
					ut_end   = hdulist[0].header["UT-END"] +'.0'



				# Convert date and times to seconds since reference point
				#print(curr_file,date_obs,ut_start)	

				# round seconds for datetime object
				#ut_start = ut_start[0:8]
				#print(ut_start)

				start_time=pd.to_datetime(date_obs+'-'+ut_start,format='%Y-%m-%d-%H:%M:%S.%f')
				end_time=pd.to_datetime(date_obs+'-'+ut_end,format='%Y-%m-%d-%H:%M:%S.%f')

				#print(datetime.start_time.total_seconds())
				#print(pd.Timestamp(start_time,unit='s'))
				start_delta = start_time - datetime.datetime(1970,1,1)
				end_delta   = end_time   - datetime.datetime(1970,1,1)

				start_time_s = start_delta.total_seconds()
				end_time_s = end_delta.total_seconds()
				# Check if times agree. In some cases there's bad end time 
				if end_time_s - start_time_s < 0:	
					end_time_s = start_delta.total_seconds() + exptime


				#if end_time_s - start_time_s > exptime + 1.1:
				#	print(curr_file,end_time_s-start_time_s,exptime)


				#print(("{:.3f} {:.3f}").format(end_time_s-start_time_s,exptime)) 

				#print(curr_file,end_time_s-start_time_s)

				#print(ut_end,end_time)
				curr_file_noext = curr_file.split("/")[-1]
				
				#print(object_name,filter_name,curr_file_noext,start_time_s,end_time_s)
				series = pd.Series({'name':object_name,'filter':filter_name,
						'image':curr_file_noext,'start_time':start_time_s,'end_time':end_time_s})
				df = df.append(series,ignore_index=True)
				#print(df)
				#print(series)

				# Write full extension out for copying
				copy_file.write(curr_file+"\n")



# put columns in better order
cols=['name','filter','image','start_time','end_time']

df = df[cols]
# Sort by name and filter
df = df.sort_values(['name','filter','start_time']).set_index('name')

#print(df)

# Write df to file
with open("Cepheid.info","w") as f:
	f.write("name,filter,image,start_time,end_time\n")
	for index,row in df.iterrows():
		write_string=("{},{},{},{:.1f},{:.1f}\n").format(index,row['filter'],row['image'],row['start_time'],row['end_time'])
		f.write(write_string)




