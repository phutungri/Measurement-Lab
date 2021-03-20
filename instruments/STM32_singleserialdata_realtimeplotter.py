import pandas as pd
import sys
import matplotlib.pyplot as plt
import numpy as np
import serial as sr 
import serial.tools.list_ports
from datetime import date
import os
from matplotlib.widgets import Button


def filenamer(file_name_front,x=0):
    today = date.today()
    fname=(str(today.strftime(file_name_front+"_%d%m%Y_")))
    while(os.path.exists(fname+str(x)+'.csv')):
        x=x+1
        
    return (fname+str(x)+'.csv')
        


class live_plot:

    def __init__(self,
                y_axis,
                x_axis,
                time_view=20,
                ):
        
        self.x_axis=x_axis
        self.y_axis=y_axis
        self.time_view=time_view #number of seconds to keep in view on graph
        self.fname_front='' #user will be asked to declare this string. Used to name csv file to save
        self.fname_save='' #value determised by filenamer function using self.fname_front.
        self.pauseflag=False
        self.saveflag=False


        
    def plot_initialise(self,fname_front):
        plt.ion() #Turn the interactive mode on
        
        #plot window initialisation 
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(bottom=0.2)
        self.line1, = self.ax.plot(self.x_axis,self.y_axis, 'r-')
        
        #pause button
        self.pauseplotdim = plt.axes([0.81, 0.05, 0.1, 0.075])
        self.pausebutton = Button(self.pauseplotdim, str('Pause'),color='r',hovercolor='r')
        self.pausebutton.on_clicked(self.change_pauseflag)
        
        #save button
        self.saveplotdim = plt.axes([0.051, 0.05, 0.07, 0.075])
        self.savebutton = Button(self.saveplotdim, str('Save'),color='r',hovercolor='r')
        self.savebutton.on_clicked(self.change_saveflag)
        
        #User defined varible use for naming saved data
        self.fname_front= fname_front
        
    def update_plot_xy(self,new_y,new_x): #update plot with both x and y values
        if self.check_fig_exist()==True: #checks plot window is still open
            self.dataframe=pd.DataFrame({'Time(s)':new_x,
                        'ADC':new_y})
            if self.pauseflag==False: #if pause button not pressed
                self.line1,=self.ax.plot(new_x,new_y, 'r-') #adds new data to plot
            
                if new_x[-1]>self.time_view: #shifts plot to show new data while keeping the number of point/time same
                    self.ax.set_xlim(new_x[-1]-self.time_view,new_x[-1])
                
                if self.saveflag==True: #appends new data to already declared file.
                    self.dataframe.to_csv(self.fname_save,index=False,mode='a',header=False)
            self.fig.canvas.draw() #renders the plot window
            self.fig.canvas.flush_events() #flush events
        else:
            plt.close(self.fig)
            print("figure has been closed")
            
    def update_plot_y(self,new_y): #update plot with only y axis value
        if self.check_fig_exist()==True:
            self.dataframe=pd.DataFrame({'ADC':new_y})
            if self.pauseflag==False:
                self.line1,=self.ax.plot(new_y, 'r-')    
                if self.saveflag==True:
                    self.dataframe.to_csv(self.fname_save,index=False,mode='a',header=False)
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
    
    def change_pauseflag(self,event): #handles the pressing of the pause button
        if self.pauseflag:
            self.pauseflag=False
            self.pausebutton = Button(self.pauseplotdim, str('Pause'),color='r',hovercolor='r')
            self.pausebutton.on_clicked(self.change_pauseflag)
            # self.fig.canvas.draw()
            # self.fig.canvas.flush_events()
        elif self.pauseflag==False:
            self.pauseflag=True
            self.pausebutton = Button(self.pauseplotdim, str('Pause'),color='g',hovercolor='g')
            self.pausebutton.on_clicked(self.change_pauseflag)
            # self.fig.canvas.draw()
            # self.fig.canvas.flush_events()
        
    def change_saveflag(self,event): #handles the pressing of the save bnutton
        if self.saveflag:
            self.saveflag=False
            self.fname_save=""
            self.savebutton = Button(self.saveplotdim, str('Save'),color='r',hovercolor='r')
            self.savebutton.on_clicked(self.change_saveflag)
            # self.fig.canvas.draw()
            # self.fig.canvas.flush_events()
        elif self.saveflag==False:
            self.saveflag=True
            self.fname_save=filenamer(self.fname_front)
            self.savebutton = Button(self.saveplotdim, str('Save'),color='g',hovercolor='g')
            self.savebutton.on_clicked(self.change_saveflag)
            self.dataframe.to_csv(self.fname_save,index=False,mode='a')
            # self.fig.canvas.draw()
            # self.fig.canvas.flush_events()
        


# serial communication initialisation

ports =serial.tools.list_ports.comports()
s = sr.Serial()
# portList = []
# for oneport in ports:
#     portList.append(str(oneport)) 
#     print(str(oneport))
# val = input("select Port: COM")
# for x in range(0,len(portList)):
#     if portList[x].startswith("COM"+str(val)):
#         portVar = "COM"+str(val)
#         print(portList[x])
s.baudrate = 115200
s.timeout = 100
# s.port = portVar
s.port="COM3"
s.open()

# variables to hold data or indexing
data=np.array([])
index_counter=0

#user defined varibles to optimise for system 
data_chunks_to_plot=500
data_chunks_to_view=20000
index_forbasechunk=np.linspace(1,data_chunks_to_plot,num=data_chunks_to_plot) #used for indexing the data to update plot

#Check that serial communication is working. As this is asychronous, the first data is not properly read.
try:
    read_port = s.readline()
    read_port = s.readline()
except:
    s.close()
    sys.exit("Error in initial read. Check with coolterm")


#initialise class for live plot. As only time value is not being measured,an empty array is being passed into x_axis 
plotlive=live_plot(y_axis=data,x_axis=np.array([]),time_view=data_chunks_to_view)

#ask for fname_front used to name files
filenamefront=input("filename front:")
plotlive.plot_initialise(filenamefront)




while(plotlive.check_fig_exist()): #run until plot is closed
    x=0
    while x<data_chunks_to_plot: #collect user declared number of points to update plot
        a = s.readline()
        t = a.decode("utf-8").rstrip("\n")
        data=np.append(data,int(t))
        x=x+1
     
    #calculate index
    index=index_forbasechunk+index_counter*data_chunks_to_plot
    
    #update plot
    plotlive.update_plot_xy(new_y=data,new_x=index)

    index_counter=index_counter+1
    data=np.array([]) # data varible emptied to avoid varible becoming very large
    
s.close()






