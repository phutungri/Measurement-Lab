import numpy as np 
import math
import matplotlib.pyplot as plt 
import os
import glob
from scipy import fftpack
import scipy.signal as sig
import utility_functions as util 
import OCT_functions as OCT_tech
import scipy.integrate as integrate
import sys
from matplotlib import ticker, cm
import pandas as pd
import time
import ntpath

global bits_per_sample
bits_per_sample = 12

global RF_conversion_gain
RF_conversion_gain = 10 * 1e3 # volts/watt

def get_config(config_file):
	"""
	Imports the configuration file written during data acquisition using Alazar SDK techniques
	"""
	with open(config_file, 'r') as myConfigFile:
		configParams = []
		for i in range(8): # number of configuration parameters, known
			line = myConfigFile.readline().strip()
			configParams.append(line.split("\t")[-1])
	print('Board configuration parameters:')
	print(configParams)
	return configParams

def single_process(configParams, no_chip_data_array, data_file, data_file_channels):
	"""
	Import and analyze a single sample file. 
	Arguments:
		configParams 		: configuration parameters, list. Return value of get_config
		no_chip_data_array	: RF signal out of balance detector, with the chip line disconnected, numpy 2D array. no_chip_data_array = [nc_time, nc_samples, nc_volts]
		data_file 			: filename of the data file to process
		data_file_channels	: number of channels in file

	Edited: March 24, 2020. Rijan Maharjan.

	"""
	# get the configuration parameters
	samplesPerSecond = float(configParams[0])
	preTriggerSamples = int(configParams[1])
	postTriggerSamples = int(configParams[2])
	recordsPerBuffer = int(configParams[3])
	buffersPerAcquisition = int(configParams[4])
	pm_range_chA_mv = float(configParams[5])
	pm_range_chB_mv = float(configParams[6])
	grinFaceHeight = float(configParams[7])

	# processing data part
	samplesPerRecord = preTriggerSamples + postTriggerSamples
	recordsPerAcquisition = recordsPerBuffer * buffersPerAcquisition

	# import file to read
	chA_samples, chB_samples = OCT_tech.import_data_DAQ(data_file, data_file_channels)
	# convert to volts
	chA_volts = OCT_tech.sample_to_volts(chA_samples, bits_per_sample, pm_range_chA_mv) 
	chB_volts = OCT_tech.sample_to_volts(chB_samples, bits_per_sample, pm_range_chB_mv) 

	# convert volts to mW
	# for PDB430C, RF, +/-1.8V is the full swing for a 50 ohm load
	# sensitivity is 5x10^3 V/W for a 50 ohm load
	chA_watt = chA_volts *  1/(RF_conversion_gain)
	chB_watt = chB_volts * 1/(RF_conversion_gain)

	#ChA is the single channel, and chB is the RF channel. Need to extract chip signal from RF channel
	# get the reference series from no-chip data
	nc_time = no_chip_data_array[0]
	nc_samples = no_chip_data_array[1]
	nc_volts = no_chip_data_array[2] 

	time_step_nc = np.mean(np.diff(nc_time))
	nc_watt = nc_volts * 1/(RF_conversion_gain)

	# get the chip signal via heterodyne extraction
	num_pts_sm = 30 # smooth the data
	if num_pts_sm != 0:
		nc_time = util.truncate_array(nc_time, num_pts_sm)
	HP_threshold = 5.0e6 # high pass filter threshold frequency

	chip_extract = OCT_tech.heterodyne_extract(chB_watt, nc_watt, num_pts_sm, HP_threshold, time_step_nc)
	# convert time to wavelength
	wavelength_nm = OCT_tech.time_to_wavelength_HSL20(nc_time)
	# get integrated power using simpsons rule
	normalized_power = integrate.simps(chip_extract, nc_time)
	return wavelength_nm, chip_extract, normalized_power, nc_time, chA_watt, chB_watt

def batch_process(no_chip_data_array, 
				source_directory, 
				data_destination, 
				write_files, 
				save_plots, 
				outDataFile,
				ax1,
				ax2):
	"""
	Function to batch process data files from DAQ, acquired using Alazar SDK system.
	Arguments:
		no_chip_data_array 		: RF signal out of balance detector, with the chip line disconnected, numpy 2D array. no_chip_data_array = [nc_time, nc_samples, nc_volts]
		source_directory 		: Directory where the files to process are saved. Filenames must be coordinate locations
		data_destination		: directory to save outDataFile
		plot_destination		: directory to save compiled data plots of integrated power if save plots enabled, and 
		write_files				: binary, write compiled files or not
		save_plots				: binary, save compliled plot or not
		outDataFile				: filename for output of compiled data
		ax1						: ax1 label, x or y
		ax2						: ax2 label, x or y, or z
	
	Edited: 24 March 2020. Rijan Maharjan

	"""
	files = glob.glob(source_directory + '*.txt')
	filesChannels = 2
	# check and remove the configuration file and outDataFile if it exists in the list
	if ntpath.basename(files[0]) == 'configuration.txt':
		files.pop(0)
	if source_directory + outDataFile in files: files.remove(source_directory + outDataFile)
	# if source_directory + 'configuration.txt' in files: files.remove(source_directory + 'configuration.txt')
	# if source_directory + outDataFile in files: files.remove(source_directory + outDataFile)
	
	try:
		configParams = get_config(source_directory + 'configuration.txt')
	except FileNotFoundError:
		print("Configuration file missing. Aborting.")
	except:
		e = sys.exc_info()[0]
		print("Unexpected error: ", e)
		raise

	# get the xy coordinates
	x_coord = np.zeros(len(files))
	y_coord = np.zeros(len(files))
	integral_value = np.zeros(len(files))

	if write_files == 1:
		compiled_data = open(data_destination + outDataFile, 'w')
		compiled_data.write(ax1+'_coord\t'+ax2+'_coord\tnormalized power\n')

	for k in range(len(files)):
	# for k in range(5):
		# parse the filename
		fname = files[k]
		x_val, y_val = util.plane_filename_to_coordinate(fname, ax1, ax2)
		x_coord[k] = x_val
		y_coord[k] = y_val
		# process the individual files
		wavelength_nm, chip_extract, normalized_power, _, _, _ = single_process(configParams,
																	no_chip_data_array,
																	files[k],
																	filesChannels)
		if write_files == 1:
			compiled_data.write("%0.2f\t%0.2f\t%0.13f\n" %(x_val, y_val, normalized_power))
	if (write_files == 1 and save_plots == 1):
		plot_compiled_2D(data_destination + outDataFile, 0, 1)
	return

def volume_batch_process(no_chip_data_array, 
				source_directory, 
				data_destination, 
				write_files, 
				save_plots, 
				outDataFile,
				ax1,
				ax2,
				ax3):
	"""
	Function to batch process data files from DAQ, acquired using Alazar SDK system.
	Arguments:
		no_chip_data_array 		: RF signal out of balance detector, with the chip line disconnected, numpy 2D array. no_chip_data_array = [nc_time, nc_samples, nc_volts]
		source_directory 		: Directory where the files to process are saved. Filenames must be coordinate locations
		data_destination		: directory to save outDataFile
		plot_destination		: directory to save compiled data plots of integrated power if save plots enabled, and 
		write_files				: binary, write compiled files or not
		save_plots				: binary, save compliled plot or not
		outDataFile				: filename for output of compiled data
		ax1						: ax1 label, x
		ax2						: ax2 label, y
		ax2						: ax3 label, z
	
	Edited: 20 May 2020. Rijan Maharjan

	"""
	files = glob.glob(source_directory + '*.txt')
	filesChannels = 2
	# check and remove the configuration file and outDataFile if it exists in the list
	if ntpath.basename(files[0]) == 'configuration.txt':
		files.pop(0)
	# if source_directory[:-1] + '\\configuration.txt' in files: files.remove(source_directory[:-1] + '\\configuration.txt')
	if source_directory + outDataFile in files: files.remove(source_directory + outDataFile)
	# print(files[0])
	# print(source_directory + 'configuration.txt')
	try:
		configParams = get_config(source_directory + 'configuration.txt')
	except FileNotFoundError:
		print("Configuration file missing. Aborting.")
	except:
		e = sys.exc_info()[0]
		print("Unexpected error: ", e)
		raise

	# get the xyz coordinates
	x_coord = np.zeros(len(files))
	y_coord = np.zeros(len(files))
	z_coord = np.zeros(len(files))
	integral_value = np.zeros(len(files))

	if write_files == 1:
		compiled_data = open(data_destination + outDataFile, 'w')
		compiled_data.write(ax1+'_coord\t'+ax2+'_coord\t'+ax3+'_coord\tnormalized power\n')

	for k in range(len(files)):
	# for k in range(5):
		# parse the filename
		fname = files[k]
		x_val, y_val, z_val = util.volume_filename_to_coordinate(fname, ax1, ax2, ax3)
		x_coord[k] = x_val
		y_coord[k] = y_val
		z_coord[k] = z_val
		# process the individual files
		wavelength_nm, chip_extract, normalized_power, _, _, _ = single_process(configParams,
																	no_chip_data_array,
																	files[k],
																	filesChannels)
		if write_files == 1:
			compiled_data.write("%0.2f\t%0.2f\t%0.2f\t%0.13f\n" %(x_val, y_val, z_val, normalized_power))
	# if (write_files == 1 and save_plots == 1):
	# 	plot_compiled_2D(data_destination + outDataFile, 0, 1)
	return

def plot_compiled_2D(compiled_file, show_plot, save_plot):
	"""
	Function to plot a sheet of data acquired from the DAQ and parsed using functions in this file.
	Arguments:
		compiled_file 		: filename of the compiled file from batch process
		show_plot			: binary, show the plot or not
		save_plot 			: binary, save the plot or not. Save location same as compiled file location. Same filename.

	Edited: 24 March 2020. Rijan Maharjan
	"""
	try:
		# import data, data must be in 3 column format. 
		# Column 1 has x-axis data, column 2 has y-axis data, column 3 has z-values. 
		# First row has headers.
		df = pd.read_csv(compiled_file, delimiter='\t')
		# In case the column isn't sorted, it must first be sorted
		sorted_data = df.sort_values(by=[df.columns[0], df.columns[1]])
		data = sorted_data.to_numpy() # convert to numpy for easier manipulation
		# split columns 
		coor_1 = data[:, 0] # x-data
		coor_2 = data[:, 1] # y-data
		norm_power = data[:, 2] # z-values
		
		# Extract headers
		with open(compiled_file) as f:
			column_headers = f.readline().strip()
		column_headers = column_headers.split('\t')
		col_head1 = column_headers[0]
		col_head2 = column_headers[1]

		# Extract the unique set of values that make up the x and y axis columns
		coor_1_range = np.unique(coor_1)
		coor_2_range = np.unique(coor_2)

		# convert the x, y axis values to a mesh
		mesh_coor1, mesh_coor2 = np.meshgrid(coor_1_range, coor_2_range)

		# since the z-values are currently in 1D array, convert them to match the x-y grid, based on sizes of the axes
		power_2d = norm_power.reshape(len(coor_1_range), len(coor_2_range))
		power_2d = power_2d.transpose() # transpose to match

		# plotting the data
		# define plot
		fig, ax = plt.subplots()
		# make a contour plot, set to contour level of 400 sub-levels, and choose colormap
		cs = plt.contourf(mesh_coor1, mesh_coor2, power_2d, 400, cmap=cm.jet)
		# show the color bar
		cbar = fig.colorbar(cs)
		# use column headers as axis labels
		plt.xlabel(col_head1)
		plt.ylabel(col_head2)
		plt.axis('equal')

		# create a plot title based on the filename. 
		plt.title(compiled_file.split('/')[0] + '  ' + compiled_file.split('/')[2] + '  ' + compiled_file.split('/')[3])
		# if plot is to be shown:
		if show_plot == 1:
			plt.show()
		# if plot is to be saved to file
		if save_plot == 1:
			plt.savefig(compiled_file+'.pdf', bbox_inches='tight')

	except FileNotFoundError:
		print("compiled file not found. Check path/processing steps.")
	except:
		e = sys.exc_info()[0]
		print("Unexpected error: ", e)
		raise

def wavelength_sheet(no_chip_data_array, 
				source_directory, 
				data_destination, 
				write_files,
				save_plot, 
				outDataFile,
				target_wavelength,
				ax1, ax2,
				bandwidth=1.0):
	"""
	Function to extract power at a particular wavelength, with a maximum bandwidth at said wavelength of 10nm
	Arguments:
		no_chip_data_array 		: RF signal out of balance detector, with the chip line disconnected, numpy 2D array. no_chip_data_array = [nc_time, nc_samples, nc_volts]
		source_directory 		: Directory where the files to process are saved. Filenames must be coordinate locations
		data_destination		: directory to save outDataFile
		write_files				: binary, write compiled files or not
		save_plots				: binary, save compliled plot or not. Same name/location as outDataFile.
		outDataFile				: filename for output of compiled data
		ax1						: ax1 label, x or y
		ax2						: ax2 label, x or y, or z
		bandwidth				: bandwidth to compute power at. defaults to 1.0 nm. Max 10 nm.
	
	Edited: 24 March 2020. Rijan Maharjan

	"""

	files = glob.glob(source_directory + '*.txt')
	filesChannels = 2
	# check and remove the configuration file and outDataFile if it exists in the list
	if source_directory + 'configuration.txt' in files: files.remove(source_directory + 'configuration.txt')
	if source_directory + outDataFile in files: files.remove(source_directory + outDataFile)
	
	try:
		configParams = get_config(source_directory + 'configuration.txt')
	except FileNotFoundError:
		print("Configuration file missing. Aborting.")
	except:
		e = sys.exc_info()[0]
		print("Unexpected error: ", e)
		raise

	# get the xy coordinates
	x_coord = np.zeros(len(files))
	y_coord = np.zeros(len(files))
	integral_value = np.zeros(len(files))

	if write_files == 1:
		compiled_data = open(data_destination + outDataFile, 'w')
		compiled_data.write(ax1+'_coord\t'+ax2+'_coord\tavg_power\tintegral_power\n')

	for k in range(len(files)):
	# for k in range(5):
		# parse the filename
		fname = files[k]
		x_val, y_val = util.plane_filename_to_coordinate(fname, ax1, ax2)
		x_coord[k] = x_val
		y_coord[k] = y_val
		# process the individual files
		wavelength_nm, chip_extract, _, nc_time, _, _ = single_process(configParams,
																	no_chip_data_array,
																	files[k],
																	filesChannels)
		if bandwidth <= 10:
			idx_min = util.find_nearest(wavelength_nm, target_wavelength - bandwidth/2)
			idx_max = util.find_nearest(wavelength_nm, target_wavelength + bandwidth/2)
			avg_power_in_range = np.sum(chip_extract[idx_min:idx_max])/(idx_max-idx_min)
			integral_power_in_range = integrate.simps(chip_extract[idx_min:idx_max], nc_time[idx_min:idx_max])
			if write_files == 1:
				compiled_data.write("%0.2f\t%0.2f\t%0.13f\t%0.13f\n" %(x_val, y_val, avg_power_in_range, integral_power_in_range))
		else:
			print('bandwidth out of range. fix code')
	if (write_files == 1 and save_plot == 1):
		plot_compiled_2D(data_destination + outDataFile, 0, 1)
	return

def wavelength_volume(no_chip_data_array, 
				source_directory, 
				data_destination, 
				write_files,
				save_plot, 
				outDataFile,
				target_wavelength,
				ax1, ax2, ax3,
				bandwidth=1.0):
	"""
	Function to extract power at a particular wavelength, with a maximum bandwidth at said wavelength of 10nm
	Arguments:
		no_chip_data_array 		: RF signal out of balance detector, with the chip line disconnected, numpy 2D array. no_chip_data_array = [nc_time, nc_samples, nc_volts]
		source_directory 		: Directory where the files to process are saved. Filenames must be coordinate locations
		data_destination		: directory to save outDataFile
		write_files				: binary, write compiled files or not
		save_plots				: binary, save compliled plot or not. Same name/location as outDataFile.
		outDataFile				: filename for output of compiled data
		ax1						: ax1 label, x 
		ax2						: ax2 label, y
		ax3						: ax3 label, z
		bandwidth				: bandwidth to compute power at. defaults to 1.0 nm. Max 10 nm.
	
	Edited: 28 May 2020. Rijan Maharjan

	"""

	files = glob.glob(source_directory + '*.txt')
	filesChannels = 2
	# check and remove the configuration file and outDataFile if it exists in the list
	if ntpath.basename(files[0]) == 'configuration.txt':
		files.pop(0)
	# if source_directory[:-1] + '\\configuration.txt' in files: files.remove(source_directory[:-1] + '\\configuration.txt')
	if source_directory + outDataFile in files: files.remove(source_directory + outDataFile)
	
	try:
		configParams = get_config(source_directory + 'configuration.txt')
	except FileNotFoundError:
		print("Configuration file missing. Aborting.")
	except:
		e = sys.exc_info()[0]
		print("Unexpected error: ", e)
		raise

	# get the xy coordinates
	x_coord = np.zeros(len(files))
	y_coord = np.zeros(len(files))
	z_coord = np.zeros(len(files))
	integral_value = np.zeros(len(files))

	if write_files == 1:
		compiled_data = open(data_destination + outDataFile, 'w')
		compiled_data.write(ax1+'_coord\t'+ax2+'_coord\t'+ax3+'_coord\tavg_power\tintegral_power\n')

	for k in range(len(files)):
	# for k in range(5):
		# parse the filename
		fname = files[k]
		x_val, y_val, z_val = util.volume_filename_to_coordinate(fname, ax1, ax2, ax3)
		x_coord[k] = x_val
		y_coord[k] = y_val
		z_coord[k] = z_val
		# process the individual files
		wavelength_nm, chip_extract, _, nc_time, _, _ = single_process(configParams,
																	no_chip_data_array,
																	files[k],
																	filesChannels)
		if bandwidth <= 10:
			idx_min = util.find_nearest(wavelength_nm, target_wavelength - bandwidth/2)
			idx_max = util.find_nearest(wavelength_nm, target_wavelength + bandwidth/2)
			avg_power_in_range = np.sum(chip_extract[idx_min:idx_max])/(idx_max-idx_min)
			integral_power_in_range = integrate.simps(chip_extract[idx_min:idx_max], nc_time[idx_min:idx_max])
			if write_files == 1:
				compiled_data.write("%0.2f\t%0.2f\t%0.2f\t%0.13f\t%0.13f\n" %(x_val, y_val, z_val, avg_power_in_range, integral_power_in_range))
		else:
			print('bandwidth out of range. fix code')
	if (write_files == 1 and save_plot == 1):
		plot_compiled_2D(data_destination + outDataFile, 0, 1)
	return
