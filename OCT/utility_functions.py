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

def get_foldername_paths_in_folder(path):

	"""
	Returns names and paths of folders within the given path
	"""

	fname_arr=[d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
	fpath_arr=[]

	for n in range(0,len(fname_arr)):
		fpath_arr.append(path+'\\'+fname_arr[n])

	return fname_arr,fpath_arr

def get_parsed_folderpaths(fnames,parsed_main_path):
	
	"""
	For a given array of foldernames and the path for the folders, 
	this function will return an array with the foldernames appended to the path
	"""
	
	parsed_fname_arr=[]
	for n in fnames:
		parsed_fname_arr.append(parsed_main_path+"\\"+n)
		
	return parsed_fname_arr

def list_txt_file(path):
	starting_dir=os.path.abspath(os.getcwd())
	os.chdir(path)
	fname_array=[]
	fpath_array=[]
	for file in glob.glob("*.txt"):
		fname_array.append(file)
		fpath_array.append(path+"\\"+file)
		
	os.chdir(starting_dir)
		
	return fname_array, fpath_array

def add_str_to_list(string,arr):
	for n in range(len(arr)):
		arr[n]=arr[n]+'_'+string
	return arr

def get_data_folder_txt(fname_array,fpath_array,columns):
	for n in range(0,len(fname_array)):
		tmp=get_data_txt(fname_array[n],fpath_array[n],columns)
		if n ==0:
			data=tmp
		else:
			data=pd.concat([data,tmp], axis=1)        
	return data

def get_data_txt(data_fname,data_path,columns):
	data=pd.read_csv(
		data_path,
		sep='\t',
		index_col=0,
		)
	data_shortened_fname=os.path.splitext(data_fname)[0]
	data_headings=add_str_to_list(data_shortened_fname,columns[1:])
	data.columns=data_headings
	return data

def get_distance_limits(range_limits,data):
	range_limits_index=[]
	
	for n in range_limits:
		range_limits_index.append(find_nearest(data, n))
		
	if range_limits_index[0]>=range_limits_index[1]:
		print("first limit has higher or equal index to second")
		
	return range_limits_index

	
def get_last_section_strarr(arr):
	new_arr=[]
	for n in range(0,len(arr)):
		new_arr.append(arr[n].split("_")[-1])

	return new_arr  

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