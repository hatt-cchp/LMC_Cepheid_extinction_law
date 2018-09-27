#!/usr/bin/env

import sys
import numpy as np
import os
import re

if __name__ == "__main__":

	good_ids=[]

	fileroot=sys.argv[1]
	filename=sys.argv[2] 

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
				if 'saturated' in el: continue
				if '?' in el: continue
				if '*' in el: continue

				#print(el)
				# remove preceeding white space
				# and return the id
				id_el=el.lstrip().split()[0]
				good_ids.append(id_el)

				#print(id_el)				
	
		
	#print("grep ' "+str(good_ids[0])+" ' "+fileroot+".lst")

	#with open(fileroot+'.lst',"r") as fin:
	#	for row in fin:
	#		print(row)
	#		for i in range(len(good_ids)):
	#			print(i)
	#			print(' '+str(id_el)+' ')
	#			if ' '+str(id_el)+' ' in row:
	#				print(id_el,row)
	# Just in case, avoid duplicates
	#good_ids=set(good_ids)

	os.system("head -3 "+fileroot+".lst"+" > "+fileroot+".newlst")
	for i in range(len(good_ids)):
		os.system("grep ' "+str(good_ids[i])+" ' "+fileroot+".lst >> "+fileroot+".newlst") 

		#print(good_ids[i])
	os.system('mv -f '+fileroot+".newlst "+fileroot+".lst")



			#var=re.search(fileroot+'.lst',str(good_ids[i]))
			#print(var)
			#f.write(line)
			#f.write(os.system("grep ' "+str(good_ids[i])+" ' "+fileroot+".lst") )	
#	nlines=0
#	with open(fileroot+".srt") as f:
#		for row in f:
#			nlines+=1
#
#	# -4 header lines, +1 for no blank line
#	# at the end of the file
#	nstars=(nlines-4+1)/3
#
#
#	query = "head -4 "+fileroot+".srt > test"   
#	os.system(query)
#
#
#	#print("test")
#	with open(fileroot+".srt") as f:
#
#		# ignore header
#		for i in range(4): 
#			f.readline()
#			
#                        
#
#
#		star_num=0
#		while star_num < nstars:
#			nstars += 1
#
#			first_line = f.readline()
#			second_line = f.readline()
#
#			id_el, x,y = first_line.split()[0:3]#.astype('float64')
#
#			mags=np.array(first_line.split()[3:]).astype('float64')
#			magerrs=np.array(second_line.split()[3:]).astype('float64')
#
#			# Blank line
#			f.readline()
#
#			# Use only good measurements
#			if -99.999 in mags or 99.999 in mags: continue
#			  
#
#			with open("test","a") as nf:
#				nf.write(first_line+second_line+"\n")
#
#			#query = "grep -A2 "+str(int(id_el))+" "+fileroot+".srt >> test"
#			#os.system(query)
#			#os.system("grep -A2 "+str(int(id_el))+" "+fileroot+".srt >> test")
#
#			#print(x,y)
#			#exit(0)
#			#print(mags)
#			#print(magerrs)
#			
#			
#			
#
#			#print(f.readline())
#			#print(f.readline())
#			#print(f.readline())
#			#print(f.readline())




