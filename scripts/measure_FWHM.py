#!/usr/bin/env

import sys
import astropy.io.fits as fits

import scipy.optimize
import numpy as np



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





if __name__ == "__main__":
	fileroot=sys.argv[1]

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
			



	#X,Y=np.indices((40,40),dtype=np.float)
	#Data=np.exp(-(((X-25)/5)**2 +((Y-15)/10)**2)/2) + 1
	#results=FitGauss2D(Data)
	#print(results[0][-4])

	# Loop through X,Y values and try to fit Gaussian.
	# Record the FWHM with each iteration
	x_FWHMs=[]#np.zeros(len(xs))
	y_FWHMs=[]#np.zeros(len(ys))

	sample_rate=int(len(xs)/100.)

	count=0
	for x,y in zip(xs,ys):
		count+=1
		if count % sample_rate != 0: continue

		min_x = int(max(x-5,0)) 
		max_x = int(min(x+5,2046))
		min_y = int(max(y-5,0))
		max_y = int(min(y+5,2046))
		#print(min_x,max_x,min_y,max_y)
		#if x < 10 or y < 10: continue
		star_data=data[min_x:max_x+1,min_y:max_y+1]
		results=FitGauss2D(star_data)
		#print(results[0][-4])
		#x_FWHMs.append(	
		if count==100: break
		x_FWHMs.append(results[0][-4])
		y_FWHMs.append(results[0][-3])
		count+=1
				
	x_med=np.nanmedian(x_FWHMs)*2.355
	y_med=np.nanmedian(y_FWHMs)*2.355
	print(0.5*(x_med+y_med))	


