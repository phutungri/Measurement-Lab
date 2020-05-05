import numpy as np
import os
import pandas as pd
import sys

# adding package location to path to import custom functions. This will depend on the location the
#programs utility_function and OCT_functions are saved in so change accordingly. 
sys.path.append('C:\\Users\\sanke\\Documents\\GitHub\\Measurement-Lab\\OCT')

import utility_functions as util
import OCT_functions as OCT_tech

import fiber_OCT_support_functions as fosf

#Program processing data to get distance vs light being reflected.
#Need to declared the path of the data to be processed and the results to be saved. 
#Need to declare the expected columns as well as additional options on how the process the data. 
#program expecting a folder with text files with atleast 2 colums with
#wavelength(nm), Data1 output(mw), Data2 output(mw). The second data (Data2) is optional.


def get_avr_source(source_filename_array):
	
	for n in range(0,len(source_filename_array)):
		source_df=pd.read_csv(
			source_filename_array[n],
			sep='\t')
		
		if n==0:
			wavelength=np.array(source_df[source_df.columns[0]])
			source_ampl=np.array(source_df[source_df.columns[1]])
		else:
			source_ampl +=np.array(source_df[source_df.columns[1]])
			wavelength_check=np.array(source_df[source_df.columns[0]])
			if np.array_equal(wavelength, wavelength_check)== False:
				print("source wavelength not matching")
				sys.exit()
	avr_source_ampl=source_ampl/len(source_filename_array)        
	return wavelength, avr_source_ampl
	

def get_raw_OCTdata(fname,path,expected_columns):
	"""
	For a folder path and filename returns the data within the file as a pandas dataframe.
	Dataframe columns set as expected columns.
	"""
	
	data_path=path+"\\"+fname
	
	data=pd.read_csv(
	data_path,
	sep='\t',
	)
	
	data.columns=expected_columns
	
	if len(data.columns.values) != len(expected_columns):
		print("data columns do not match expected columns")
		sys.exit()
	   
	return data

def process_single_OCT(filename,folder_path,source_data,setting):

	"""
	Gets OCT data and outputs the resulting amplitude vs distance of the ascan.
	"""

	raw_data=get_raw_OCTdata(filename,folder_path,setting["expected_columns"])
	
	if setting["remove_DC"] == True:
		data_tmp=fosf.remove_dc_OCT(raw_data)
	else:
		data_tmp=raw_data
	
	if setting["richardson_lucy"] ==True :
		for n in data_tmp.columns[1:]:
			data_tmp[n]=OCT_tech.rl_deconvolution(np.array(data_tmp[n]),source_data["amplitude"], 10)        

	final_data=OCT_tech.get_distance_data(filename,data_tmp,setting["expected_columns"],setting["data_end_0buffer"])
	

	return final_data


def process_folder_of_folder_OCT(source_data,setting):
	
	if setting["folder_containing_folders"]==True:
		folder_names,folder_paths=util.get_foldername_paths_in_folder(setting["data_path"])
	else:
		folder_paths=[setting["data_path"]]
		folder_names=[""]

	print(folder_paths)
	for n in range(0,len(folder_paths)):
		os.chdir(folder_paths[n])
		filenames,filepaths=util.list_txt_file(folder_paths[n])
		folder_to_save=setting["result_txt_path"]+"\\results_"+folder_names[n]
		if not os.path.exists(folder_to_save):
			os.makedirs(folder_to_save)
		
		for x in range(0,len(filenames)):
			OCT_data=process_single_OCT(
				filenames[x],
				folder_paths[n],
				source_data,
				setting
				)
			print(OCT_data)
			OCT_data.to_csv(
				folder_to_save+"\\"+filenames[x],
				index_label="Distance",
				sep='\t'
				)
	
def save_setting_txt(setting):
	os.chdir(setting["result_txt_path"])
	setting_keys=list(setting.keys())
	
	if os.path.isfile('settings.txt'):
		os.remove('settings.txt')
	
	with open('settings.txt', 'a') as myfile:
		myfile.write('KEYS\tVALUE\n')
		for n in range(len(setting_keys)):
			myfile.write(str(setting_keys[n])+'\t'+str(setting[setting_keys[n]])+'\n')

    

#self declared variables    
setting={


		  
	"richardson_lucy":False,
		# options-> True,False 
	"remove_DC":False,
		# options-> True,False
	"data_end_0buffer":0, 
		#options-> positive integer value or 0
	"expected_columns":np.array(
		['Wavelength','Single_Arm','Differential']
		),
			#option->wavelength and power columns. Can accept more than one power
			#colums. Must be consistent with all data that are being batched
	"folder_containing_folders":False,
		#if data path is a folder containing the data file, declare false. If the path contains a folder with multiple 
		#folders containing data, declare true.
	
	
	"result_txt_path":'C:\\Users\\sanke\\OneDrive\\Phutung\\OCT_experiment\\Data\\test_21_01_2020\\results_txt\\set2',
	"data_path":'C:\\Users\\sanke\\OneDrive\\Phutung\\OCT_experiment\\Data\\test_21_01_2020\\avr_data',
	"source_path":'C:\\Users\\sanke\\OneDrive\\Phutung\\OCT_experiment\\Data\\test_21_01_2020\\parsed_source',
		
	}

source_data={
	"file_names":[],
	"wavelength":[],
	"amplitude":[],
	}





# Source correction-optional
if setting["richardson_lucy"]==True:
	os.chdir(setting["source_path"])
	
	source_data["file_names"]=os.listdir(setting["source_path"])
	source_data["wavelength"],source_data["amplitude"]=get_avr_source(source_data["file_names"])
   


# process raw OCT data in data path in setting

process_folder_of_folder_OCT(source_data,setting)
 

#create txt file with setting values
save_setting_txt(setting)



	