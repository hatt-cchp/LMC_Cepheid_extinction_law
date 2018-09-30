#!/usr/bin/env

import sys
import astropy.io.fits as fits

import scipy.optimize
import numpy as np

from astropy.stats import median_absolute_deviation



def moments2D(inpData):
	""" Returns the (amplitude, xcenter, ycenter, xsigma, ysigma, rot, bkg, e) estimated from moments in the 2d input array Data """
	
	bkg=np.median(np.hstack((inpData[0,:],inpData[-1,:],inpData[:,0],inpData[:,-1])))  #Taking median of the 4 edges points as background
	Data=np.ma.masked_less(inpData-bkg,0)   #Removing the background for calculating moments of pure 2D gaussian
	#We also masked any negative values before measuring moments
	
	amplitude=Data.max()
	
	total= float(Data.sum())
	Xcoords,Ycoords= np.indices(Data.shape)
	
	xcenter= (Xcoords*Data).sum()/total
	ycenter= (Ycoords*Data).sum()/total
	
	RowCut= Data[int(xcenter),:]  # Cut along the row of data near center of gaussian
	ColumnCut= Data[:,int(ycenter)]  # Cut along the column of data near center of gaussian
	xsigma= np.sqrt(np.ma.sum(ColumnCut* (np.arange(len(ColumnCut))-xcenter)**2)/ColumnCut.sum())    
	ysigma= np.sqrt(np.ma.sum(RowCut* (np.arange(len(RowCut))-ycenter)**2)/RowCut.sum())
	
	#Ellipcity and position angle calculation
	Mxx= np.ma.sum((Xcoords-xcenter)*(Xcoords-xcenter) * Data) /total
	Myy= np.ma.sum((Ycoords-ycenter)*(Ycoords-ycenter) * Data) /total
	Mxy= np.ma.sum((Xcoords-xcenter)*(Ycoords-ycenter) * Data) /total
	e= np.sqrt((Mxx - Myy)**2 + (2*Mxy)**2) / (Mxx + Myy)
	pa= 0.5 * np.arctan(2*Mxy / (Mxx - Myy))
	rot= np.rad2deg(pa)
	
	return amplitude,xcenter,ycenter,xsigma,ysigma, rot,bkg, e

def Gaussian2D(amplitude, xcenter, ycenter, xsigma, ysigma, rot,bkg):
	""" Returns a 2D Gaussian function with input parameters. rotation input rot should be in degress """
	rot=np.deg2rad(rot)  #Converting to radians
	Xc=xcenter*np.cos(rot) - ycenter*np.sin(rot)  #Centers in rotated coordinates
	Yc=xcenter*np.sin(rot) + ycenter*np.cos(rot)
	#Now lets define the 2D gaussian function
	def Gauss2D(x,y) :
		""" Returns the values of the defined 2d gaussian at x,y """
		xr=x * np.cos(rot) - y * np.sin(rot)  #X position in rotated coordinates
		yr=x * np.sin(rot) + y * np.cos(rot)
		return amplitude*np.exp(-(((xr-Xc)/xsigma)**2 +((yr-Yc)/ysigma)**2)/2) +bkg
	
	return Gauss2D


def FitGauss2D(Data,ip=None):
	""" Fits 2D gaussian to Data with optional Initial conditions ip=(amplitude, xcenter, ycenter, xsigma, ysigma, rot, bkg)
	Example: 
	>>> X,Y=np.indices((40,40),dtype=np.float)
	>>> Data=np.exp(-(((X-25)/5)**2 +((Y-15)/10)**2)/2) + 1
	>>> FitGauss2D(Data)
	(array([  1.00000000e+00,   2.50000000e+01,   1.50000000e+01, 5.00000000e+00,   1.00000000e+01,   2.09859373e-07, 1]), 2)
	 """
	if ip is None:   #Estimate the initial parameters form moments and also set rot angle to be 0
		ip=moments2D(Data)[:-1]   #Remove ellipticity from the end in parameter list
	
	Xcoords,Ycoords= np.indices(Data.shape)    
	def errfun(ip):
		dXcoords= Xcoords-ip[1]
		dYcoords= Ycoords-ip[2]
		Weights=np.sqrt(np.square(dXcoords)+np.square(dYcoords)) # Taking radius as the weights for least square fitting

		return np.ravel((Gaussian2D(*ip)(*np.indices(Data.shape)) - Data)/np.sqrt(Weights))  #Taking a sqrt(weight) here so that while scipy takes square of this array it will become 1/r weight.

	p, success = scipy.optimize.leastsq(errfun, ip)

	return p,success




def compute_mad_estimates(x_FWHMs,y_FWHMs):
	"""
	"""

	
	# Computing median and mad estimates
	x_med=np.nanmedian(x_FWHMs)
	y_med=np.nanmedian(y_FWHMs)
	x_mad = median_absolute_deviation(x_FWHMs,ignore_nan=True)
	y_mad = median_absolute_deviation(y_FWHMs,ignore_nan=True)

	# Outlier resistant median
	x_med_clipped = np.median(np.array(x_FWHMs)[ abs(x_FWHMs-x_med) <= 2.0*x_mad ])	
	y_med_clipped = np.median(np.array(y_FWHMs)[ abs(y_FWHMs-y_med) <= 2.0*y_mad ])	


	return 0.5*(x_med_clipped+y_med_clipped)*2.355











if __name__ == "__main__":
	fileroot=sys.argv[1]
	max_num_stars=float(sys.argv[2])

	hdul = fits.open(fileroot+'.fits')
	data = hdul[0].data # assuming the first extension is a table	

	# Loop through X,Y values from the *.coo file
	xs=[]
	ys=[]
	with open(fileroot+".coo") as coo_file:

		# Skip header
		for row in range(3):
			coo_file.readline()

		for row in coo_file:
			parts=row.split()		
			xs.append(float(parts[1]))
			ys.append(float(parts[2]))
			

	# Loop through X,Y values and try to fit Gaussian.
	# Record the FWHM with each iteration

	x_FWHMs=[]
	y_FWHMs=[]

	#sample_number=int(len(xs)/num_stars)

	count=0
	prev_mean_FWHM = -99

	for x,y in zip(xs,ys):

		if count == max_num_stars: break #% sample_number != 0: continue

		min_x = int(x-5)
		max_x = int(x+5)
		min_y = int(y-5)
		max_y = int(y+5)

		# Avoid stars at the edges of the image

		if max_x < 10 or max_y < 10 or min_x > 2040 or min_y > 2040: continue

		star_data=data[min_x:max_x+1,min_y:max_y+1]
		results=FitGauss2D(star_data)

		x_sig=results[0][-4]
		y_sig=results[0][-3]

		if np.nan in results[0]: continue

		# Avoid bogus FWHM measures.
		# Too small of FWHM can be cosmic rays
		# Also avoid very large FWHMs. DAOPHOT
		# is currently only able to go up to 50 pix
		# for the outer sky.

		if x_sig <= 0.5 or y_sig <= 0.5 or \
			x_sig >= 10 or y_sig >= 10 or \
			np.isnan(x_sig)  or np.isnan(y_sig): continue
			
		
		#print(x_sig,y_sig,type(x_sig),np.isnan(x_sig))
			

		x_FWHMs.append(x_sig)
		y_FWHMs.append(y_sig)


		if prev_mean_FWHM == -99: 
			
			prev_mean_FWHM = 0.5*(x_FWHMs[0] + y_FWHMs[0]) 

		else:

			mean_FWHM  = compute_mad_estimates(x_FWHMs,y_FWHMs)

			mean_diff = abs(mean_FWHM - prev_mean_FWHM) 

			if mean_diff <= 0.1 and count >= 100 and mean_diff != np.nan: 
				count = max_num_stars
		
			prev_mean_FWHM = mean_diff


			#print(mean_FWHM)

		count+=1


	#print(prev_mean_FWHM,mean_FWHM,mean_diff)

	#import matplotlib.pyplot as plt 
	#plt.hist(x_FWHMs,bins=1000)	
	#plt.xlim(0,3)
	#plt.show()

	#print(x_FWHMs)
	
	## Computing median and mad estimates
	#x_med=np.nanmedian(x_FWHMs)
	#y_med=np.nanmedian(y_FWHMs)
	#x_mad = median_absolute_deviation(x_FWHMs,ignore_nan=True)
	#y_mad = median_absolute_deviation(y_FWHMs,ignore_nan=True)
	#
	## Outlier resistant median
	#x_med = np.median(np.array(x_FWHMs)[ abs(x_FWHMs-x_mad) <= 2.0*x_mad ])	
	#y_med = np.median(np.array(y_FWHMs)[ abs(y_FWHMs-y_mad) <= 2.0*y_mad ])	

	print( "{:.2f}".format(mean_FWHM) )
	

	


