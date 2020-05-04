import numpy as np 
from scipy import fftpack
import scipy.signal as sig
import matplotlib.pyplot as plt
import utility_functions as util
import scipy.interpolate as intrp
import pandas as pd

import utility_functions as util
"""
TO DO SANK-
change inputs to functions to make them more general-remove setting

"""


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

""" 
ADDED by SANK
"""

def flip_convert_interpolate_data(wavelength,ampl):

	"""
	will flip all the data so that wave_num will be in acending order
	converts wavelength to wavenumber
	creates array of wave_number increasing linearly and then interpolates data at these points
	"""

	ampl=np.asarray(ampl)
	wavelength=np.asarray(wavelength)

	wavelength_flip=wavelength[::-1]
	ampl_flip=np.flip(ampl,0)

	k_flip=(2*np.pi)/wavelength_flip
	k_lin=np.linspace(k_flip[0],k_flip[-1],num=len(k_flip),endpoint=True)

	ampl_lin=np.zeros(ampl_flip.shape)

	try:
		for i in range(0,(ampl_flip.shape[1])):
			ampl_if=intrp.interp1d(k_flip,ampl_flip[:,i])
			ampl_lin[:,i]=ampl_if(k_lin)
	except:
		ampl_if=intrp.interp1d(k_flip,ampl_flip)
		ampl_lin=ampl_if(k_lin)

	return k_lin,ampl_lin

def add_buffer(wave_number,ampl_lin,extendbuffer):

	"""
	add buffer values before and after test values
	wavenumber needs to be from 0 for z data to be accurate which is before the experimental data
	extend buffer is the number of points after the data points
	"""

	dk=wave_number[1]-wave_number[0]
	data_step=len(wave_number)
	kstep_to_0=int(wave_number[0]/dk)
	k_step_total=data_step+extendbuffer+kstep_to_0
	k_final=dk*k_step_total

	k_final=np.linspace(0,k_final,num=k_step_total,endpoint=True)

	try:
		ampl_final=np.zeros((k_step_total,ampl_lin.shape[1]))
		for i in range(0,(ampl_lin.shape[1])):
			ampl_final[kstep_to_0:kstep_to_0+data_step,i]=ampl_lin[:,i]
	except:
		ampl_final=np.zeros((k_step_total))
		ampl_final[kstep_to_0:kstep_to_0+data_step]=ampl_lin

	return k_final,ampl_final



def get_ifft(wave_number,ampl_final):

	"""
	calculates the iverse fourier transform and shifts the data to be linearly changing
	converts the wavenumber data points to distance
	"""

	ID_z=np.zeros(ampl_final.shape)
	ID_z=ID_z.astype(complex)

	try:
		for i in range(0,(ampl_final.shape[1])):
			ID_z[:,i]=np.fft.ifft(ampl_final[:,i])
			ID_z[:,i]=np.fft.ifftshift(ID_z[:,i])
			deltak=(np.pi*len(wave_number)/(wave_number[-1]))
			dis=np.fft.fftfreq(ID_z[:,i].shape[-1])
			dis=1e6*deltak*np.fft.fftshift(dis)
	except:
		ID_z=np.fft.ifft(ampl_final)
		ID_z=np.fft.ifftshift(ID_z)
		deltak=(np.pi*len(wave_number)/(wave_number[-1]))
		dis=np.fft.fftfreq(ID_z.shape[-1])
		dis=1e6*deltak*np.fft.fftshift(dis)

	return dis, abs(ID_z)

def get_distance_data(filename,data,expected_columns,data_end_0buffer):

	"""
	expects input data to contain wavelength and amlitude.
	After data processing to required form, performs inverse fourier transfrom. 
	"""

	#data that has been converted to wavenumber and made linear

	test=(np.array(data[expected_columns[0]]))
	print((test))

	k,ampl_s1=flip_convert_interpolate_data(
		data[expected_columns[0]]*1e-9,
		data[expected_columns[1:]]
		)

		
	#data with buffers before and after experimental data 
	k_s2,ampl_s2=add_buffer(
		k,
		ampl_s1,
		data_end_0buffer
		)

	
	#data in terms of distance
	data_z,ampl_s3=get_ifft(
		k_s2,
		ampl_s2
		)
	

	data_colums=[]
	for i in range(1,len(expected_columns)):
		data_colums.append(expected_columns[i]+filename)

	data_df=pd.DataFrame(
		data=ampl_s3,
		index=data_z,
		columns=(data_colums)
		)

	
	return data_df

def rl_deconvolution(image,psf,iterations):
	"""
	richardson-lucy image processing algorithm to have better resolution. 
	Reduces the width of the peaks for the a scan. 
	"""

	image=util.normalise((image))
	psf=util.normalise((psf))

	u_hat = image;
	psf_flipped=psf[::-1]

	for i in range(0,iterations):
		denom=np.convolve(u_hat,psf,'same')
		fract= np.divide(image,denom)
		sec_conv= np.convolve(fract,psf_flipped,'same')
		u_hat = np.multiply(u_hat,sec_conv)
	u_hat=util.normalise(u_hat)


	return u_hat



