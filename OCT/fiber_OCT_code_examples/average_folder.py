import os
import glob
import pandas as pd
import numpy as np
import sys

# adding package location to path to import custom functions. This will depend on the location the
#programs utility_function and OCT_functions are saved in so change accordingly. 
sys.path.append('C:\\Users\\sanke\\Documents\\GitHub\\Measurement-Lab\\OCT')

import utility_functions as util
import OCT_functions as OCT_tech

import fiber_OCT_support_functions as fosf

"""
The program averages a directory with folders of data. Each folders of data should be of the same conditions.
Need to declare the location of the data to be averaged and the place to be save the results.
Expected columns also has to be declared
"""



def multi_txt_1column_index_average(data_folder_path,column_names):
    
    filenames,filepaths=fosf.list_txt_file(data_folder_path)
    data=pd.DataFrame()
    avg_data=pd.DataFrame()
    
    if len(filenames)==0:
        print("ERROR-no txt files in path "+str(data_folder_path))
    else:
        print('files: '+str(filenames))
        
    data=(
        fosf.get_data_folder_txt(
            filenames,
            filepaths,
            column_names)
        )

    
    if (len(column_names)-1)==1:
        avg_data[column_names[1]]=data.mean(axis=1)        
    else:
        arr = np.arange(len(data.columns)) % (len(column_names)-1)

        for n in range(0,(len(column_names)-1)):
            avg_data[column_names[n+1]]  = data.iloc[:, arr == n/(len(column_names)-2)].mean(axis=1)
            
  

    return(avg_data),data



def add_avg_txt_to_strarr(arr):
    n_arr=[]
    for n in arr:
        n_arr.append('avg_'+str(n)+'.txt')
    return n_arr

def average_folder_folder_data(folder_folder_path,save_path,column_names):
    save_filename,data_folder_paths=(fosf.get_foldername_paths_in_folder(folder_folder_path))
    save_filename=add_avg_txt_to_strarr(save_filename)
    
    
    for n in range(0,len(save_filename)):
        avg_data, data=multi_txt_1column_index_average(
            data_folder_paths[n],
            column_names
            )
        
        fosf.write_to_txt(
            avg_data, 
            save_path,
            save_filename[n]
            )

data_folder_path="C:\\Users\\sanke\\OneDrive\\Phutung\\OCT_experiment\\Data\\test_21_01_2020\\parsed_data"
save_path="C:\\Users\\sanke\\OneDrive\\Phutung\\OCT_experiment\\Data\\test_21_01_2020\\avr_data"

column_names=['wavelength','single_arm','differential']

average_folder_folder_data(data_folder_path, save_path, column_names)
    

    
    