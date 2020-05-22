import numpy as np
import os
import pandas as pd
import sys
import glob

# adding package location to path to import custom functions.This will depend on the location the
#programs utility_function and OCT_functions are saved in so change accordingly. 
sys.path.append('C:\\Users\\sanke\\Documents\\GitHub\\Measurement-Lab\\OCT')

import utility_functions as util

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


def get_foldername_paths_in_folder(path):

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
        range_limits_index.append(util.find_nearest(data, n))
        
    if range_limits_index[0]>=range_limits_index[1]:
        print("first limit has higher or equal index to second")
        
    return range_limits_index

    
def get_last_section_strarr(arr):
    new_arr=[]
    for n in range(0,len(arr)):
        new_arr.append(arr[n].split("_")[-1])

    return new_arr  

def remove_dc_OCT(df):
    #removes DC component
    columns=df.columns.values
    ampl=np.array(df)
    
    for i in range(1,(ampl.shape[1])):
        ampl[:,i]=ampl[:,i]-(max(ampl[:,i])+min(ampl[:,i]))/2
    
    dc_removed_df=pd.DataFrame(
        data=ampl,
        columns=columns
        )
       
    return dc_removed_df

def write_to_txt(df,save_folder,save_file):
    
    if os.path.isfile(save_folder+save_file):
        print("overwriting_file: " + str(save_folder+save_file))
    
    df.to_csv(
        path_or_buf=save_folder+'\\'+save_file,
        sep='\t') 