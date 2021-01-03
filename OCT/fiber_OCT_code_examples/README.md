# fiber OCT code examples, Optical Coherence Tomography, Measurements

These programs were made specifically for post processing parsed data from the AlazarTech DAQ. The results will be an A-scan that represents the amount of light being reflected with respect to distance (relative to the reference mirror). 

##Single data file processing 

The "example1.py" file is designed to process a single text file containing the parsed data of the experiment. If the Richard-Lucy algorithm is to be used, another text file containing the source spectrum will be required. More information on how this program is used, such as importing data will be given in the comments within the file.

##Batch processing for fiber-based experiments

The experiments were done by shifting the distance between the reference mirror and the sample. To start processing, first it is required to have a folder containing multiple folders that have parsed data .txt files for a position of the reference and sample. The workflow that has been used is to first use "average_folder.py" to average all the measurements to get the average for each relative position. This is to reduce effects of noise. Then to use "A-scan.py" to calculate the relation between light being reflected and the distance. Finally, "pdf_maker.py" will create pdfs with the A-scan data represented in graphs (viewing the graphs in the interactive python window is also possible). It is also possible to exchange the order of "A-scan.py" and "average_folder.py" however this would take more space.    
More information on how each individual file is used, will be commented in the file.

## Installing

Simply download the complete OCT folder as such as functions from OCT_functions, utility_functions are used in these examples. Each program will require setting initial parameters and paths to operate. 
