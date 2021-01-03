import numpy as np 
import scipy.interpolate as intrp
import pandas as pd
import matplotlib.pyplot as plt



#functions
def normalise(array_matrix):
#normalise data to 0-1

    try:
        for i in range(0,(array_matrix.shape[1])):
            print("bp1")
            min_val=min(array_matrix[:,i])
            print("bp2")
            max_val=max(array_matrix[:,i])
            if min_val==max_val:
                print("Warning minimum and maximun are equal in matrix row"+str(i)+"!")
                array_matrix[:,i]=array_matrix[:,i]/min_val
            else:
                array_matrix[:,i]=(array_matrix[:,i]-min_val)/(max_val-min_val)

    except:
        min_val=min(array_matrix)
        max_val=max(array_matrix)
        if min_val==max_val:
            print("Warning minimum and maximun are equal in array!")
            array_matrix=array_matrix/min_val
        else:
            array_matrix=(array_matrix-min_val)/(max_val-min_val)

    return array_matrix


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

def get_distance_data(wavelength,amplitude,data_end_0buffer):

    """
    expects input data to contain wavelength and amlitude.
    After data processing to required form, performs inverse fourier transfrom. 
    """

    #data that has been converted to wavenumber and made linear

    test=(np.array(wavelength))
    print((test))

    k,ampl_s1=flip_convert_interpolate_data(
        wavelength*1e-9,
        amplitude
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
    
    
    #kept seperate incase more processing steps will be added in future
    final_amplitude=ampl_s3
    distance=data_z

    
    return distance,final_amplitude

def rl_deconvolution(image,psf,iterations):
    """
    richardson-lucy image processing algorithm to have better resolution. 
    Reduces the width of the peaks for the a scan. 
    """

    image=normalise((image))
    psf=normalise((psf))

    u_hat = image;
    psf_flipped=psf[::-1]

    for i in range(0,iterations):
        denom=np.convolve(u_hat,psf,'same')
        fract= np.divide(image,denom)
        sec_conv= np.convolve(fract,psf_flipped,'same')
        u_hat = np.multiply(u_hat,sec_conv)
    u_hat=normalise(u_hat)


    return u_hat

def remove_dc_OCT(ampl):
    ampl=ampl-(max(ampl)+min(ampl))/2
    return ampl

#code to use functions in this file to process a single OCT data file. 
#Source data is only used for Richardson Lucy algorithm

if __name__ == "__main__":

    #location for OCT data
    data_path="C:\\Users\\sanke\\OneDrive\\Phutung\\OCT_experiment\\Data\\test_21_01_2020\\avr_data\\avg_000um.txt"
    
    
    #option to remove peak at DC
    remove_DC=True
    #option to apply Richardson Lucy algorithm to increase resolution. Requires data of source specturm.
    richardson_lucy=True  
    
    #add 0 at end of data. Potentially increase resolution. Needs more understanding.
    data_end_0buffer=0
    
    #If richardson_lucy is true the source data has to be given
    source_path='C:\\Users\\sanke\\OneDrive\\Phutung\\OCT_experiment\\Data\\test_21_01_2020\\parsed_source\\avg_source.txt'   
    
    
    
    
    #importing data    
    data=pd.read_csv(data_path,sep='\t')
    wavelength=data[data.columns.values[0]]
    amplitude=data[data.columns.values[2]]
        
    #source data can be commented out if not using Richardson Lucy algorithm. Assumes the wavelengths match with OCT data
    source_data=pd.read_csv(source_path,sep='\t')
    source_wavelenght=source_data[source_data.columns.values[0]]
    source_amplitude=source_data[source_data.columns.values[1]]
    
    
    # data processing
    if remove_DC == True:
        data_ampl_tmp=remove_dc_OCT(amplitude)
    else:
        data_ampl_tmp=amplitude
    
    if richardson_lucy ==True :
        data_ampl_tmp=rl_deconvolution(data_ampl_tmp,source_amplitude, 10)        
    
    #the 'test' value is passed to keep track of multiple different data files
    final_distance,final_amplitude=get_distance_data(wavelength,data_ampl_tmp,data_end_0buffer)
    
    
    #plotting
    data_fig=plt.figure()
    data_ax=data_fig.add_subplot(1,1,1)
    data_ax.plot(final_distance,final_amplitude)
    data_ax.set_xlabel('Distance(um)')
    data_ax.set_ylabel('Amplitude')