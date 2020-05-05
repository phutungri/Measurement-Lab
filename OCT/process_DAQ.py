
import numpy as np 
import matplotlib.pylab as plt
import os
import glob
import parse_ATS as ATSReader
import utility_functions as util

"""
Program to parse data from DAQ. Need to define the directory to be parsed, the saved location and the number of channels. 
Will produce PDF with the data ploted. Additional options are to show the plots. 
"""

def parse_and_plot(data_directory, parsed_directory, write_files, show_plot, num_channels):
	"""
	parses alazar tech DAQ output files 
	can handle 1 or 2 channels that are saved as *A.txt or (if two channels) *A.txt and *B.txt
	if 2 channels will combine the two files into a single file
	Output file to contain wavelength, channelA power and channel B power with hardcoded file column headings 
	"""

	if num_channels == 2:
		# get files from that directory
		fnameA = glob.glob(data_directory + '\\*A.txt')
		fnameB = glob.glob(data_directory + '\\*B.txt')
		# these fnames have the complete list of all repetitions of the experiment
		for i in range(len(fnameA)):
		# for i in range(3):
			full_path_A = fnameA[i]
			full_path_B = fnameB[i]
	
			f_out_name = fnameA[i][len(data_directory)+1:-14]
		
			Ch_A_sig = ATSReader.read_text_record(full_path_A)
			Ch_B_sig = ATSReader.read_text_record(full_path_B)
		
			time = Ch_B_sig['time']
			wavelength = Ch_B_sig['wavelength']
			signal_B = Ch_B_sig['raw_signal']
			power_mw_B = Ch_B_sig['power_mw']
			# power_mw_B = power_mw_B - np.min(power_mw_B)
			
			signal_A = Ch_A_sig['raw_signal']
			power_mw_A = Ch_A_sig['power_mw']
			# power_mw_A = power_mw_A - np.min(power_mw_A)
		
			if write_files == True:
				CHECK_FOLDER = os.path.isdir(parsed_directory)
				if not CHECK_FOLDER:
					os.makedirs(parsed_directory)
					print("created folder : ", parsed_directory)
				with open(parsed_directory+'\\'+f_out_name + '.txt', 'a') as myfile:
					myfile.write('wavelength\tpower_single (mw)\tpower_differential (mw)\n')
					for i in range(len(wavelength)):
						myfile.write('%0.13f\t%0.13f\t%0.13f\n' % (wavelength[i], power_mw_A[i], power_mw_B[i]))
			
			
			fig, ax1 = plt.subplots()
			ax2 = ax1.twinx()
			
			p1, = ax1.plot(Ch_A_sig['time'], Ch_A_sig['raw_signal'], 'r')
			ax1.tick_params(axis='y', colors='r')
			ax1.yaxis.label.set_color('r')
			ax1.set_ylabel('Single channel output (V)')
			
			p2, = ax2.plot(Ch_B_sig['time'], Ch_B_sig['raw_signal'], 'b')
			ax2.tick_params(axis='y', colors='b')
			ax2.yaxis.label.set_color('b')
			ax2.set_ylabel('Differential output (V)')
			
			ax1.set_xlabel('Time (sec)')
			plt.legend([(p1), (p2)], ['Single output', 'Differential output'])
			# plt.title(f_out_name)
			if write_files == True:
				CHECK_FOLDER = os.path.isdir(parsed_directory+'\\raw_plots\\')
				if not CHECK_FOLDER:
					os.makedirs(parsed_directory+'\\raw_plots\\')
					print("created folder : ", parsed_directory+'\\raw_plots')
				plt.savefig(parsed_directory+'\\raw_plots\\' + f_out_name+'.pdf', bbox_inches='tight')
			if show_plot == True:
				plt.show()
			plt.close('all')

		return Ch_A_sig, Ch_B_sig
	if num_channels == 1:
		fnameA = glob.glob(data_directory + '\\*A.txt')
		for i in range(len(fnameA)):
			full_path_A = fnameA[i]

			f_out_name = fnameA[i][len(data_directory)+1:-14]
		
			Ch_A_sig = ATSReader.read_text_record(full_path_A)
		
			time = Ch_A_sig['time']
			wavelength = Ch_A_sig['wavelength']
			
			signal_A = Ch_A_sig['raw_signal']
			power_mw_A = Ch_A_sig['power_mw']
			# power_mw_A = power_mw_A - np.min(power_mw_A)
		
			if write_files == True:
				CHECK_FOLDER = os.path.isdir(parsed_directory)
				if not CHECK_FOLDER:
					os.makedirs(parsed_directory)
					print("created folder : ", parsed_directory)
				with open(parsed_directory+'\\'+f_out_name + '.txt', 'a') as myfile:
					myfile.write('wavelength\tpower_single (mw)\n')
					for i in range(len(wavelength)):
						myfile.write('%0.13f\t%0.13f\n' % ( wavelength[i], power_mw_A[i]))
			
			
			fig, ax1 = plt.subplots()
			ax2 = ax1.twinx()
			
			p1, = ax1.plot(Ch_A_sig['time'], Ch_A_sig['raw_signal'], 'r')
			ax1.tick_params(axis='y', colors='r')
			ax1.yaxis.label.set_color('r')
			ax1.set_ylabel('Single channel output (V)')
			
			ax1.set_xlabel('Time (sec)')
			plt.legend([(p1)], ['Single output'])
			# plt.title(f_out_name)
			if write_files == True:
				CHECK_FOLDER = os.path.isdir(parsed_directory+'\\raw_plots\\')
				if not CHECK_FOLDER:
					os.makedirs(parsed_directory+'\\raw_plots\\')
					print("created folder : ", parsed_directory+'\\raw_plots')
				plt.savefig(parsed_directory+'\\raw_plots\\' + f_out_name+'.pdf', bbox_inches='tight')
			if show_plot == True:
				plt.show()
			plt.close('all')
		return Ch_A_sig



	
if __name__=="__main__":

	setting={

		"data_main_directory":'C:\\Users\\sanke\\OneDrive\\Phutung\\OCT_experiment\\Data\\test_21_01_2020\\raw_data',
		"parsed_main_directory":'C:\\Users\\sanke\\OneDrive\\Phutung\\OCT_experiment\\Data\\test_21_01_2020\\parsed_data',
		
		
		"write_files":True,
		"show_plot": False,
		"num_channels":2,
		}


	data_foldernames,data_folderpaths= util.get_foldername_paths_in_folder(setting["data_main_directory"])


	parsed_folderpaths=util.get_parsed_folderpaths(
		data_foldernames,
		setting["parsed_main_directory"])


	for n in range(0, len(data_folderpaths)):
		parse_and_plot(
			data_folderpaths[n],
			parsed_folderpaths[n],
			setting["write_files"],
			setting["show_plot"],
			setting["num_channels"]
			)