import numpy as np 
from scipy import fftpack
import scipy.signal as sig
import matplotlib.pyplot as plt 
import os
import glob

# simple utility functions for python

"""
Lists the utilitiy functions often used in the project
Primary author: 
	Rijan Maharjan
Secondary author:
	Sanket Bohora
Last edited: May 01, 2020
"""

# find the nearest index of a value in numpy array 
def find_nearest(array, value):
	array = np.asarray(array)
	idx = (np.abs(array - value)).argmin()
	return idx

# function to get a sliding average over N points
def sliding_average(array, num_pts):
	N = num_pts
	smoothed_array = np.convolve(array, np.ones((N,))/N, mode='valid')[(N-1):]
	return smoothed_array
# After the sliding average is performed, other arrays may require truncation to plot and such
def truncate_array(array, num_pts):
	array = array[2 * num_pts - int(num_pts/2) - 1:-int(num_pts/2) + 1]
	return array

# high pass filter, returns signal after performing high pass filter
def HP_filter(signal, time_step, frequency_to_filter):
	fft = fftpack.fft(signal)
	fft_freq = fftpack.fftfreq(fft.size, d = time_step)
	idx_high_pos = np.where((fft_freq < frequency_to_filter) & (fft_freq > -frequency_to_filter))
	fft[idx_high_pos[0]] = 0.
	sig_return = fftpack.ifft(fft)
	return sig_return.real

# returns coordinate positions as an array from a filename that includes the values
# this file is created from the DAQ system acquisition codes (SDK versions)
def plane_filename_to_coordinate(fname, ax1, ax2):
	fragments = fname.split('/')[-1]
	for i in range(len(fragments)):
		if ax1 == 'x':
			if fragments[i] == 'x' and fragments[i+1] != 't':
				sub_frag = fragments[i+2::]
				if ax2 == 'y':
					sub_frag = sub_frag.split('y')
				elif ax2 == 'z':
					sub_frag = sub_frag.split('z')
				else:
					print("Coordinate system error.")
				x_val = sub_frag[0]
				y_val = sub_frag[1]
				y_val = y_val[1:-4]
				return float(x_val), float(y_val)

		elif ax1 == 'y':
			if fragments[i] == 'y':
				sub_frag = fragments[i+2::]
				if ax2 == 'z':
					sub_frag = sub_frag.split('z')
				else:
					print("Coordinate system error.")
				x_val = sub_frag[0]
				y_val = sub_frag[1]
				y_val = y_val[1:-4]
				return float(x_val), float(y_val)


def normalise(array_matrix):
#normalise data to 0-1

	try:
		for i in range(0,(array_matrix.shape[1])):
			print("bp1")
			min_val=min(array_matrix[:,i])
			print("bp2")
			max_val=max(array_matrix[:,i])
			if min_val==max_val:
				print("Warning minimum and maximun are equal in matrix row"+str(i)+"!")
				array_matrix[:,i]=array_matrix[:,i]/min_val
			else:
				array_matrix[:,i]=(array_matrix[:,i]-min_val)/(max_val-min_val)

	except:
		min_val=min(array_matrix)
		max_val=max(array_matrix)
		if min_val==max_val:
			print("Warning minimum and maximun are equal in array!")
			array_matrix=array_matrix/min_val
		else:
			array_matrix=(array_matrix-min_val)/(max_val-min_val)

	return array_matrix

def roundup(x, sf=1):
	try:
		decimalpoint=int((floor(log10(abs(x))))-(sf-1))
	except:
		decimalpoint=0
	n=10**decimalpoint
	rounded=ceil(x/n)*n
	return rounded

def rounddown(x,sf=1):
	try:
		decimalpoint=int((floor(log10(abs(x))))-(sf-1))
	except:
		decimalpoint=0
	n=10**decimalpoint
	rounded=floor(x/n)*n
	return rounded

def find_nearest(array, value):
	array = np.asarray(array)
	idx = (np.abs(array-value)).argmin()
	return idx

def find_low_higher_index(value_array,limits_array):
	idx_low=find_nearest(value_array, limits_array[0])
	idx_high=find_nearest(value_array, limits_array[1])
	return [idx_low,idx_high]