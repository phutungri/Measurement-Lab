import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
import pandas as pd
import re
import fiber_OCT_support_functions as fosf

"""
Program to import data from a particular folder and make PDFs. Specifically for the OCT experiments 
where data is taken at different reference mirror positions. 
Need to declare the location of the data to be made into PDF and the location to save the PDF. The expected columns
in the text file and the data column to be used to make the PDFs has to be declared.
Other options on how to process the data and wether to show the plots as the program is available  
"""


##features to be implelmented
#be able to declare number of data files to plot in one graph for multiplot with ability to select all
#ability to allow option to declare the distance shift for the distogram


def get_color_spec(n_lines):
	"""
	creates a list of colors that gradually changes from blue to red 
	"""
	color_list=[]
	color_f= np.linspace(0,1,num=n_lines)
	for n in range(0,n_lines):
		color_list.append((color_f[n],(1-color_f[n]),1+(-color_f[n])**3,1))
	return color_list

def plot_ifftGraph(distance,data_ampl,heading,distance_limit_index):
	"""
	Plotting a single graph of distance vs amplitude
	"""
	y_val = np.array(data_ampl)
	distance=np.array(distance)

	data_fig=plt.figure()
	data_ax=data_fig.add_subplot(1,1,1)

	
	y_val_truncated = y_val[distance_limit_index[0]:distance_limit_index[1]]
	x_val_truncated = distance[distance_limit_index[0]:distance_limit_index[1]]

	data_ax.plot(
		x_val_truncated,
		y_val_truncated,
		linewidth=0.5
		)
	
	#data_ax.plot(data_z, data_ampl,linewidth=0.5)
	data_ax.set_xlabel('Distance(um)')
	data_ax.set_ylabel('Amplitude')
	data_fig.suptitle(heading)
	
	return data_fig

def plot_mult_ifftGraph(distance,data_ampl,legend,distance_limit):
	"""
	Plotting mutliple lines on same graph. For changing refernces
	"""
	y_val = np.array(data_ampl)
	distance=np.array(distance)

	data_fig=plt.figure()
	data_ax=data_fig.add_subplot(1,1,1)
	
	y_val_truncated = y_val[distance_limit[0]:distance_limit[1]]
	x_val_truncated = distance[distance_limit[0]:distance_limit[1]]

	#looped to make clearer that data and legend label are linked
	color_spec=get_color_spec(y_val_truncated.shape[1])
	for n in range(0,y_val_truncated.shape[1]):
		data_ax.plot(
			x_val_truncated,
			y_val_truncated[:,n],
			label=legend[n],
			linewidth=0.5,
			color=color_spec[n]
			)    
	data_ax.set_xlabel('Distance(um)')
	data_ax.set_ylabel('Amplitude')
	data_ax.legend(loc='upper right')
	data_fig.suptitle('Combined graph')
	
	return data_fig


def plot_distogram(data_x,data_ampl,filenames,x_spec_lim_size):
	"""
	Ploting a spectrogram like graph. the Yaxis will represent change in reference point and the amplitude will be represented by color.
	The x axis will be distance as before.
	Filename declaration has to be in specific format and contain the change in distance from reference.
	"""

	y_val=[]
	c_val=np.array(data_ampl).T

	for i in range(0,len(filenames)):
		print(filenames[i])
		y_val.append(float((re.findall(r'\d+', filenames[i]))[0]))
	if len(y_val)!=len(filenames):
		print('filenames not declared correctly')


	c_val_truncated = c_val[:,x_spec_lim_size[0]:x_spec_lim_size[1]]
	x_val_truncated = data_x[x_spec_lim_size[0]:x_spec_lim_size[1]]
	
	data_fig=plt.figure()
	data_ax=data_fig.add_subplot(1,1,1)

	c=data_ax.pcolorfast(x_val_truncated,y_val,c_val_truncated)
	data_fig.colorbar(c,ax=data_ax)
	data_ax.set_title("Combined graph for different reference distance")

	return data_fig

def plot_shifted_distogram(data_x,data_ampl,filenames,x_spec_lim_size):
	"""
	Similar to the distogram but shifted the same amount as the distance from the reference
	Filename declaration has to be be in specific format 
	"""
	
	y_val=[]
	c_val=np.array(data_ampl).T
	
	for i in range(0,len(filenames)):
		y_val.append(float((re.findall(r'\d+', filenames[i]))[0]))
	if len(y_val)!=len(filenames):
		print('filenames not declared correctly')
	
	c_val_truncated = c_val[:,x_spec_lim_size[0]:x_spec_lim_size[1]]
	x_val_truncated = data_x[x_spec_lim_size[0]:x_spec_lim_size[1]]
	xx,yy = np.meshgrid(x_val_truncated,y_val)

	
	for i in range(len(y_val)):
		xx[i,:]=xx[i,:]-yy[i,:]
		
	data_fig=plt.figure()
	data_ax=data_fig.add_subplot(1,1,1)

	c=data_ax.contourf(xx,yy,c_val_truncated,50)
	data_ax.set_title("Combined contour graph shifted depending on reference distance")
	data_fig.colorbar(c)
	
	return data_fig

def makepdf(main_dict,main_dict_columns,file_columns,make_pdf_columns, distance_limits,log_norm,show_multifig,show_distogram,show_shifted_distogram):
	"""
	Make pdf contain the ifft graphs, the combined ifft graph and the distograms.
	"""


	temp_data=pd.DataFrame()
	arr = np.arange(len(main_dict_columns)) % (len(file_columns)-1)
	
	for n in range(0,(len(file_columns)-1)):
		for m in make_pdf_columns:
			if file_columns[n+1]==m:
				temp_data  = main_dict.iloc[:, arr == n/(len(file_columns)-2)]
				temp_columns=temp_data.columns
				pdffile= PdfPages(file_columns[n+1]+log_norm+'.pdf')
				
				for i in range(0,len(temp_columns)):
					
					fig=plot_ifftGraph(
						main_dict.index.values,
						temp_data[temp_columns[i]],
						temp_columns[i],
						distance_limits
						)
					pdffile.savefig(fig)
					plt.close()
				
				temp_legend=fosf.get_last_section_strarr(temp_columns)
				
				multi_fig=plot_mult_ifftGraph(
					main_dict.index.values,
					temp_data,
					temp_legend,
					distance_limits
					)
				pdffile.savefig(multi_fig)
				if show_multifig == True:
					plt.show()
				plt.close()
				
				disto=plot_distogram(
					main_dict.index.values,
					temp_data,
					temp_legend,
					distance_limits)
				pdffile.savefig(disto)
				if show_distogram ==True:
					plt.show()
				plt.close()
				
				shifted_disto=plot_shifted_distogram(
					main_dict.index.values,
					temp_data,
					temp_legend,
					distance_limits)
				pdffile.savefig(shifted_disto)
				if show_shifted_distogram ==True:
					plt.show()
				plt.close()
				pdffile.close()
				

			
			
		

setting={
	
	"path_to_data":'C:\\Users\\sanke\\OneDrive\\Phutung\\OCT_experiment\\Data\\test_21_01_2020\\results_txt\\set5\\results_',
	"path_to_savepdf":'C:\\Users\\sanke\\OneDrive\\Phutung\\OCT_experiment\\Data\\test_21_01_2020\\results_pdf\\set5',

	#expected columns in the data files. These names will be used in dataframe column heading
	"expected_columns":['Distance','single_arm','differential'],
	#of the expected columns, the columns to be used to make the PDFs
	"make_pdf_columns":['differential'],
		
	"normalise_data":False,
	#distance to be shown, in micrometer
	"distance_range":np.array([0,5000]),

	#show figure as the PDFs as being made. Individual plots are not an option as they can take a long time.
	"show_multifig":False,
	"show_distogram":False,
	"show_shifted_distogram":False,
		

	}


data={
	  "fname":[],
	  "path":[],
	  "distance":pd.DataFrame(),
	  "distance_limits_index":[],
	  "distance_fullrange_index":[],
	  
	  "amplitude":pd.DataFrame(),
	  "log_amplitude":pd.DataFrame(),
	  "columns":[]
	  }


data["fname"],data["path"]=fosf.list_txt_file(setting["path_to_data"])


data["amplitude"]=fosf.get_data_folder_txt(
	data["fname"],
	data["path"],
	setting["expected_columns"])

data["distance"]=data["amplitude"].index.values
data["columns"]=data["amplitude"].columns.values
	
 
#calculate log of amplitude    
data["log_amplitude"]=pd.DataFrame(
	data=np.log(data["amplitude"]),
	columns=data["amplitude"].columns
	)


#get distance indexs
	
data["distance_fullrange_index"]=[0,(len(data["distance"])-1)]   
data["distance_limits_index"]=fosf.get_distance_limits(
	setting["distance_range"],
	data["distance"]
	) 

#make linear scale distance/amplitude graphs full range

os.chdir(setting["path_to_savepdf"])

makepdf(
	data["amplitude"],
	data["columns"],
	setting["expected_columns"],
	setting["make_pdf_columns"],
	data["distance_fullrange_index"],
	'_linear_full',
	setting["show_multifig"],
	setting["show_distogram"],
	setting["show_shifted_distogram"]

	)


#make log scale distance/amplitude graphs full range
makepdf(
	data["log_amplitude"],
	data["columns"],
	setting["expected_columns"],
	setting["make_pdf_columns"],
	data["distance_fullrange_index"],
	'_log_full',
	setting["show_multifig"],
	setting["show_distogram"],
	setting["show_shifted_distogram"]
	)
	
#make linear scale distance/amplitude graphs limited range

makepdf(
	data["amplitude"],
	data["columns"],
	setting["expected_columns"],
	setting["make_pdf_columns"],
	data["distance_limits_index"],
	'_linear_limited',
	setting["show_multifig"],
	setting["show_distogram"],
	setting["show_shifted_distogram"]
	)

#make log scale distance/amplitude graphs limited range
makepdf(
	data["log_amplitude"],
	data["columns"],
	setting["expected_columns"],
	setting["make_pdf_columns"],
	data["distance_limits_index"],
	'_log_limited',
	setting["show_multifig"],
	setting["show_distogram"],
	setting["show_shifted_distogram"]
	)
