from __future__ import division

import numpy as np
from scipy import fftpack
import scipy.signal as sig
import utility_functions as util
import ctypes
import signal
import sys
import atsapi as ats
import shutil
import matplotlib.pyplot as plt
import OCT_functions as OCT_tech
import pandas as pd
import scipy.interpolate as intrp


def ConfigureBoard_OCT_RT(board,channel,samplesPerSecond,pm_range):
	# TODO: Select clock parameters as required to generate this
	# sample rate
	#
	# For example: if samplesPerSec is 100e6 (100 MS/s), then you can
	# either:
	#  - select clock source INTERNAL_CLOCK and sample rate
	#    SAMPLE_RATE_100MSPS
	#  - or select clock source FAST_EXTERNAL_CLOCK, sample rate
	#    SAMPLE_RATE_USER_DEF, and connect a 100MHz signal to the
	#    EXT CLK BNC connector


	board.setCaptureClock(ats.INTERNAL_CLOCK,
						  ats.SAMPLE_RATE_500MSPS,
						  ats.CLOCK_EDGE_RISING,
						  0)

	# TODO: Select channel B input parameters as required.

	if channel=="B":
		board.inputControlEx(ats.CHANNEL_B,
							 ats.DC_COUPLING,
							 pm_range,
							 ats.IMPEDANCE_50_OHM)

		# TODO: Select channel B bandwidth limit as required.
		board.setBWLimit(ats.CHANNEL_B, 0)
		print("configuring Channel B")
	elif channel=="A":
		board.inputControlEx(ats.CHANNEL_A,
							 ats.DC_COUPLING,
							 pm_range,
							 ats.IMPEDANCE_50_OHM)

		# TODO: Select channel B bandwidth limit as required.
		board.setBWLimit(ats.CHANNEL_A, 0)
		print("configuring Channel A")
	else:
		print("Channel defined incorrectly! ")
		sys.exit()

	# TODO: Select trigger inputs and levels as required.
	board.setTriggerOperation(ats.TRIG_ENGINE_OP_J,
							  ats.TRIG_ENGINE_J,
							  ats.TRIG_EXTERNAL,
							  ats.TRIGGER_SLOPE_NEGATIVE,
							  128,
							  ats.TRIG_ENGINE_K,
							  ats.TRIG_DISABLE,
							  ats.TRIGGER_SLOPE_POSITIVE,
							  128)

	# TODO: Select external trigger parameters as required.
	board.setExternalTrigger(ats.DC_COUPLING,
							 ats.ETR_TTL)

	# TODO: Set trigger delay as required.
	triggerDelay_sec = 0
	triggerDelay_samples = int(triggerDelay_sec * samplesPerSecond + 0.5)
	board.setTriggerDelay(triggerDelay_samples)

	# TODO: Set trigger timeout as required.
	#
	# NOTE: The board will wait for a for this amount of time for a
	# trigger event.  If a trigger event does not arrive, then the
	# board will automatically trigger. Set the trigger timeout value
	# to 0 to force the board to wait forever for a trigger event.
	#
	# IMPORTANT: The trigger timeout value should be set to zero after
	# appropriate trigger parameters have been determined, otherwise
	# the board may trigger if the timeout interval expires before a
	# hardware trigger event arrives.
	triggerTimeout_sec = 0
	triggerTimeout_clocks = int(triggerTimeout_sec / 10e-6 + 0.5)
	board.setTriggerTimeOut(triggerTimeout_clocks)

	# Configure AUX I/O connector as required
	board.configureAuxIO(ats.AUX_OUT_TRIGGER,
						 0)
	print("configuration complete!")

def AcquireData_OCT_RT(board, preTriggerSamples, postTriggerSamples, recordsPerBuffer, buffersPerAcquisition,channel_sel):



	# TODO: Select the active channels.


	if channel_sel == "B":
		channels = ats.CHANNEL_B
	elif channel_sel =="A":
		channels = ats.CHANNEL_A
	channelCount = 0
	for c in ats.channels:
		channelCount += (c & channels == c)


	# Compute the number of bytes per record and per buffer
	memorySize_samples, bitsPerSample = board.getChannelInfo()
	bytesPerSample = (bitsPerSample.value + 7) // 8
	samplesPerRecord = preTriggerSamples + postTriggerSamples
	bytesPerRecord = bytesPerSample * samplesPerRecord
	bytesPerBuffer = bytesPerRecord * recordsPerBuffer * channelCount


	# TODO: Select number of DMA buffers to allocate
	bufferCount = 4

	# Allocate DMA buffers

	sample_type = ctypes.c_uint8
	if bytesPerSample > 1:
		sample_type = ctypes.c_uint16

	buffers = []
	for i in range(bufferCount):
		buffers.append(ats.DMABuffer(board.handle, sample_type, bytesPerBuffer))

	# Set the record size
	board.setRecordSize(preTriggerSamples, postTriggerSamples)

	recordsPerAcquisition = recordsPerBuffer * buffersPerAcquisition

	# Configure the board to make an NPT AutoDMA acquisition
	board.beforeAsyncRead(channels,
						  -preTriggerSamples,
						  samplesPerRecord,
						  recordsPerBuffer,
						  recordsPerAcquisition,
						  ats.ADMA_EXTERNAL_STARTCAPTURE | ats.ADMA_TRADITIONAL_MODE)



	# Post DMA buffers to board
	for buffer in buffers:
		board.postAsyncBuffer(buffer.addr, buffer.size_bytes)

	# start = time.perf_counter() # Keep track of when acquisition started
	try:
		board.startCapture() # Start the acquisition
		print("Capturing %d buffers. Press <enter> to abort" %
			  buffersPerAcquisition)
		buffersCompleted = 0
		bytesTransferred = 0
		while (buffersCompleted < buffersPerAcquisition and not
			   ats.enter_pressed()):
			# Wait for the buffer at the head of the list of available
			# buffers to be filled by the board.
			buffer = buffers[buffersCompleted % len(buffers)]
			board.waitAsyncBufferComplete(buffer.addr, timeout_ms=5000)
			buffersCompleted += 1
			bytesTransferred += buffer.size_bytes

			# TODO: Process sample data in this buffer. Data is available
			# as a NumPy array at buffer.buffer

			# NOTE:
			#
			# While you are processing this buffer, the board is already
			# filling the next available buffer(s).
			#
			# You MUST finish processing this buffer and post it back to the
			# board before the board fills all of its available DMA buffers
			# and on-board memory.
			#
			# Samples are arranged in the buffer as follows:
			# S0A, S0B, ..., S1A, S1B, ...
			# with SXY the sample number X of channel Y.
			#
			# A 12-bit sample code is stored in the most significant bits of
			# each 16-bit sample value.
			#
			# Sample codes are unsigned by default. As a result:
			# - 0x0000 represents a negative full scale input signal.
			# - 0x8000 represents a ~0V signal.
			# - 0xFFFF represents a positive full scale input signal.
			# Optionaly save data to file
			# print(buffer.buffer)
			# if dataFile:
			#     buffer.buffer.tofile(dataFile)
			n = 0
			sampleValue = []
			for i in range(0, len(buffer.buffer)):
				val = bin(buffer.buffer[i] >> 4)
				val = int(val, 2)
				sampleValue.append(val)
			sampleValue = np.array(sampleValue)
			reshapedSampleValue = sampleValue.reshape(recordsPerBuffer*channelCount, -1)
			data_ampl = reshapedSampleValue
			data_ampl_avg = np.mean(data_ampl, axis = 0)
			data_ampl_avg = np.transpose(data_ampl_avg)
			return data_ampl_avg

			# Add the buffer to the end of the list of available buffers.
			board.postAsyncBuffer(buffer.addr, buffer.size_bytes)
	finally:
		board.abortAsyncRead()

def single_process_OCT_RT(pm_range_data_mv,bits_per_sample,RF_conversion_gain, time, data):

	data_volts = OCT_tech.sample_to_volts(data, bits_per_sample, pm_range_data_mv)
	# convert volts to mW
	# for PDB430C, RF, +/-1.8V is the full swing for a 50 ohm load
	# sensitivity is 5x10^3 V/W for a 50 ohm load

	data_watt = data_volts * 1/(RF_conversion_gain)


	# convert time to wavelength
	wavelength_nm = OCT_tech.time_to_wavelength_HSL20(time)


	return wavelength_nm, data_watt


class OCT_RT:
	
	def __init__(
			self,
			samplesPerSec=500000000.0,
			preTriggerSamples=320,
			postTriggerSamples=2880,
			recordsPerBuffer=25,
			buffersPerAcquisition=1,
			channel="B",
			fiber_or_chip="Fiber",
			pm_range=ats.INPUT_RANGE_PM_1_V,
			bits_per_sample=12,
			RF_conversion_gain=10 * 1e3,
			data_end_buffer=0,
			richardson_lucy=False,
			PSF=False,
			iterations=10,
			):
		
		self.samplesPerSec = samplesPerSec
		self.preTriggerSamples = preTriggerSamples
		self.postTriggerSamples = postTriggerSamples
		self.recordsPerBuffer = recordsPerBuffer
		self.buffersPerAcquisition = buffersPerAcquisition
		self.channel=channel
		self.fiber_or_chip=fiber_or_chip
		self.pm_range=pm_range
		self.bits_per_sample = bits_per_sample
		self.RF_conversion_gain = RF_conversion_gain
		
		self.board=0
		self.data_amplitude=np.array([])
		self.data_time=np.arange(-preTriggerSamples,postTriggerSamples,1)*(1/samplesPerSec)
		self.data_wavelength=np.array([])
		self.data_power=np.array([])
		self.data_processed_amplitude=np.array([])
		self.data_distance=np.array([])
		self.data_end_buffer=data_end_buffer
		self.richardson_lucy=richardson_lucy
		self.PSF=PSF
		self.iterations=iterations

		
		if (self.richardson_lucy==True):
			if isinstance(self.PSF, int):
				print("PSF not given")
				sys.exit()
		
	def configure_DAQ_board(self):
		
		self.board = ats.Board(systemId = 1, boardId = 1)
		OCT_tech.ConfigureBoard_OCT(self.board,self.channel,self.samplesPerSec,self.pm_range)
		
	def update_data_amplitude(self):
		
		self.data_amplitude=OCT_tech.AcquireData_OCT(self.board, self.preTriggerSamples, self.postTriggerSamples, self.recordsPerBuffer, self.buffersPerAcquisition,self.channel)
		self.data_wavelength,self.data_power=OCT_tech.single_process_OCT_RT(self.pm_range,self.bits_per_sample,self.RF_conversion_gain,self.data_time, self.data_amplitude)
		
	def clip_wavelength_power(self,wavelength_range_index):
		if self.wavelength_clipping==True:
			self.data_wavelength=self.data_wavelength[wavelength_range_index[0],wavelength_range_index[1]]
			self.data_power=self.data_power[wavelength_range_index[0],wavelength_range_index[1]]
		
	def process_data(self):
		
		if (self.richardson_lucy==True):
			self.data_power_tmp= OCT_tech.rl_deconvolution_RT(self.data_power,self.PSF,self.iterations)
		else:
			self.data_power_tmp=self.data_power
		self.data_distance,self.data_processed_amplitude=OCT_tech.get_distance_data_OCT_RT(self.data_wavelength,self.data_power_tmp,self.data_end_buffer)
	
class live_plot:

	def __init__(self,
				x_axis,
				y_axis,
				):
		
		self.x_axis=x_axis
		self.y_axis=y_axis
		
	def plot_initialise(self):
		plt.ion()
		self.fig = plt.figure()
		self.ax = self.fig.add_subplot(111)
		self.line1, = self.ax.plot(self.x_axis,self.y_axis, 'r-')
		
	def update_plot(self,new_y):
		if self.check_fig_exist()==True:
			self.line1.set_ydata(new_y)
			self.ax.set_ylim(util.rounddown((new_y).min(),1),1.1*util.roundup((new_y).max(),1))
			self.fig.canvas.draw()
			self.fig.canvas.flush_events()
			
		else:
			plt.close(self.fig)
			print("figure has been closed")
		
	def check_fig_exist(self):
		if plt.fignum_exists(self.fig.number)==True:
			return True
		elif plt.fignum_exists(self.fig.number)==False:
			return False
		else:
			print("ERROR in check close")


if __name__="__main__":
	distance_range=np.array([0,1000])
	wavelength_range=np.array([1257,1355])

	data_PSF_path="D:\\SanketWorkFiles\\real_time_OCT\\Data\\Parsed_source\\avg_source_26_02_2020.txt"

	data_PSF=pd.read_csv(
		data_PSF_path,
		sep='\t',
		)

	data_PSF=np.array(data_PSF)
	PSF_wavelength_index_range=util.find_low_higher_index(data_PSF,wavelength_range)
	PSF_wavelength=data_PSF[PSF_wavelength_index_range[0]:PSF_wavelength_index_range[0],0]
	PSF_ampl=data_PSF[PSF_wavelength_index_range[0]:PSF_wavelength_index_range[0],1]

	# main=OCT_RL(richardson_lucy=True,PSF=PSF_ampl)
	main=OCT_RL()
	main.configure_DAQ_board()
	main.update_data_amplitude()
	wavelength_index_range=util.find_low_higher_index(main.data_wavelength, wavelength_range)
	main.clip_wavelength_power(wavelength_index_range)
	main.process_data()

	index_range=util.find_low_higher_index(main.data_distance,distance_range)


	wavelength_live_plot=live_plot(x_axis=main.data_wavelength,
								y_axis=main.data_power)
	wavelength_live_plot.plot_initialise()

	fft_live_plot=live_plot(x_axis=main.data_distance[index_range[0]:index_range[1]],
						y_axis=main.data_processed_amplitude[index_range[0]:index_range[1]])
	fft_live_plot.plot_initialise()

	while (fft_live_plot.check_fig_exist() & wavelength_live_plot.check_fig_exist()):
		
		main.update_data_amplitude()
		main.clip_wavelength_power(wavelength_index_range)
		main.process_data()
		
		if fft_live_plot.check_fig_exist() & wavelength_live_plot.check_fig_exist()==True:
			wavelength_live_plot.update_plot(main.data_power)
		else:
			plt.close(wavelength_live_plot.fig)
			plt.close(fft_live_plot.fig)
		
		if fft_live_plot.check_fig_exist() & wavelength_live_plot.check_fig_exist()==True:
			fft_live_plot.update_plot(main.data_processed_amplitude[index_range[0]:index_range[1]])
		else:
			plt.close(fft_live_plot.fig)
			plt.close(wavelength_live_plot.fig)

