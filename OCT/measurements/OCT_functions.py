import numpy as np 
from scipy import fftpack
import scipy.signal as sig
import matplotlib.pyplot as plt
import utility_functions as util

"""
This file includes functions required to parse, extract, analyze data acquired from Chip for OCT systems. 
Primary authors:
	Rijan Maharjan
	Sanket Bohora

Last edited: March 24, 2020.
"""

def heterodyne_extract(experimental_series, reference_series, num_pts_sm, HP_threshold, time_step):
	"""
	Extracts the weak signal, such as one from the chip, boosted with a local oscillator, extracted using a reference signal.
		experimental_series – the main measured signal, like the RF signal from the balance detector.
		reference_series – local-oscillator signal. RF signal without when chip is disconnected
		num_pts_sm – how many data points to smooth over
		HP_threshold – frequency above which all signals are zero'd. High Pass filter threshold
		time_step – time difference between two consecutive data points
	"""
	# normalize the data with maximum of reference series
	experimental_series = experimental_series/np.max(reference_series)
	reference_series = reference_series/np.max(reference_series)
	# average the data using the sliding average function from utility functions
	if num_pts_sm != 0:
		experimental_series = util.sliding_average(experimental_series, num_pts_sm)
		reference_series = util.sliding_average(reference_series, num_pts_sm)
	# extract just the intereference envelope
	interference_component_only = experimental_series - reference_series
	# apply High Pass filter
	HP_filtered_signal = util.HP_filter(interference_component_only, time_step, HP_threshold)
	# extract the analytic signal, and finally the envelope
	analytic_signal = sig.hilbert(HP_filtered_signal)
	extracted_signal = np.abs(analytic_signal)
	return extracted_signal

def import_data_DSO_parsed(fname, num_channels):
	"""
	this function imports the data from an already parsed signal, from ATS parser (parses raw data)
	"""
	data = np.loadtxt(fname, skiprows=1)
	time = data[:, 0]
	wavelength = data[:, 1]
	if num_channels == 2:
		ChA_raw = data[:, 2]
		ChB_raw = data[:, 3]
		ChA_power = data[:, 4]
		ChB_power = data[:, 5]
		return time, wavelength, ChA_raw, ChB_raw, ChA_power, ChB_power
	if num_channels == 1:
		ChA_raw = data[:, 2]
		ChA_power = data[:, 3]
		return time, wavelength, ChA_raw, ChA_power
	else:
		print('Incorrect number of channels. Try again.')
		return

def import_data_DSO_raw_samples(fname):
	"""
	imports directly saved Alazar Text Records files, and returns only the time, sample value, and scaled voltages from DSO software
	"""
	data = np.loadtxt(fname, skiprows=46, delimiter=',')
	time = data[:, 1]
	samples = data[:, 2]
	volts = data[:, 3]
	return time, samples, volts

def import_data_DAQ(fname, num_channels):
	"""
	Function imports data acquired from the DAQ board using AlazarSDK code.
	"""
	data = np.loadtxt(fname, skiprows=1)
	m, n = data.shape
	if n != num_channels:
		print('Import DAQ error: Expected num of channels does not match.')
		return
	else:
		if n == 1:
			ChA_samples = data[:, 0]
			return ChA_samples
		else:
			ChA_samples = data[:, 0] 
			ChB_samples = data[:, 1]
		return ChA_samples, ChB_samples

def sample_to_volts(sample_array, bits_per_sample, pm_range_mv):
	"""
	converts a sample array from the DSO acquisition to mV based on the +/- range and bits per sample (12)
	"""
	value_min = 0
	value_max = 2**bits_per_sample
	value_range = value_max - value_min
	volts_min = -1 * pm_range_mv
	volts_max = +1 * pm_range_mv
	volts_range = volts_max - volts_min
	if sample_array.ndim == 1:
		sampleVolts = (((sample_array - value_min) * volts_range)/value_range) + volts_min
		return sampleVolts * 0.001
	else:
		print("Sample to volts error. Check array shape.")
		return

def time_to_wavelength_HSL20(time_array_sec):
	"""
	Uses the data provided by the manufacturer to get corresponding wavelength information from given time, using a fitted function.
	Time must be in seconds.
	"""
	# convert time in micro seconds
	time = time_array_sec * 1000 * 1000
	wavelength = 1256 + 15.8138*time + 5.5467*time**2 - 1.0695*time**3 + 0.02803*time**4
	return wavelength