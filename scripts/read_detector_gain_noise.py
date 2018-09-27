#!/usr/bin/env



import sys

import astropy.io.fits as pyfits


fileroot = sys.argv[1]


# get average gain
hdulist = pyfits.open(fileroot+'.fits')

#print('INSTRUME' in hdulist[0].header)

# SITe2K
if 'INSTRUME' in hdulist[0].header:

	GAIN=hdulist[0].header['EGAIN']
	READN=hdulist[0].header['ENOISE']

else:
	
	# http://www.lco.cl/telescopes-information/irenee-du-pont/instruments/website/direct-ccd-manuals/direct-ccd-users-manual/ccd-manual-for-the-40-inch-100-inch-telescopes/?searchterm=ccd
	# Table 4
	GAIN=hdulist[0].header['GAIN']
	READN = 7.

READN /= GAIN
print(('{:.3f} {:.3f}').format(READN,GAIN))


