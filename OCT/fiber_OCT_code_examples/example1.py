import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt

# adding package location to path to import custom functions. This will depend on the location the
#programs utility_function and OCT_functions are saved in so change accordingly. 
sys.path.append('C:\\Users\\sanke\\Documents\\GitHub\\Measurement-Lab\\OCT')

import OCT_functions as OCT_tech

import fiber_OCT_support_functions as fosf



"""
Basic example to process a single parsed OCT data. 
If richardson lucy algorithm is to be applied, source data has to be provided by providing the path to this data.

The user is required to set the setting according to what is desired. The paths to the data will depend
according to where the user has stored the data. The expected columns are the columns in the data file.
The numbers of columns should match however the name of the columns are not important.  
"""


#user set settings    
data_path="C:\\Users\\sanke\\OneDrive\\Phutung\\OCT_experiment\\Data\\test_21_01_2020\\avr_data\\avg_000um.txt"
expected_columns=np.array(['Wavelength','Single_Arm','Differential'])   
remove_DC=True
richardson_lucy=True  
data_end_0buffer=0

source_path='C:\\Users\\sanke\\OneDrive\\Phutung\\OCT_experiment\\Data\\test_21_01_2020\\parsed_source\\avg_source.txt'   
source_expected_columns=np.array(['Wavelength','amplitude'])  
                   

#importing data    
data=pd.read_csv(data_path,sep='\t')
data.columns=expected_columns

if len(data.columns.values) != len(expected_columns):
    print("data columns do not match expected columns")
    sys.exit()
    
source_data=pd.read_csv(source_path,sep='\t')
source_data.columns=source_expected_columns

if len(source_data.columns.values) != len(source_expected_columns):
    print("source data columns do not match expected columns")
    sys.exit()

# data processing
if remove_DC == True:
    data_tmp=fosf.remove_dc_OCT(data)
else:
    data_tmp=data

if richardson_lucy ==True :
    for n in data_tmp.columns[1:]:
        data_tmp[n]=OCT_tech.rl_deconvolution(np.array(data_tmp[n]),source_data[source_expected_columns[1]], 10)        

final_data=OCT_tech.get_distance_data('test',data_tmp,expected_columns,data_end_0buffer)

#plotting
data_fig=plt.figure()
data_ax=data_fig.add_subplot(1,1,1)
data_ax.plot(final_data)
data_ax.set_xlabel('Distance(um)')
data_ax.set_ylabel('Amplitude')
