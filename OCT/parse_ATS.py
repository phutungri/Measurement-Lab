import numpy as np 

# this module reads file formats from AlazarDSO software
# datafile assumes both A

def get_power(signal_V):
	# for PDB430C, conversion gain is 10 V/mW
	power_m_watt = (signal_V)/10.0
	power_dBm = 10 * np.log10(power_m_watt/1.0)
	return power_m_watt, power_dBm

# function to find nearest index for a value in numpy
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def read_text_record(fname):
	data = np.loadtxt(fname, skiprows=46, delimiter=',')
	pre_trig_samples = np.loadtxt(fname, skiprows=28, max_rows=1, usecols=1, delimiter=',', dtype=int)

	# initialize a python dictionary
	data_dict = {}
	data_dict['available_keys'] = ['trigger_begins', 'sample', 'time', 'value', 'raw_signal', 'wavelength', 'power_mw', 'power_dBm']
	data_dict['trigger_begins'] = pre_trig_samples
	# extract the first spectrum only
	# limit of fit function is -0.5 usec from trigger to 4.5 usec after trigger
	t_begin = -0.5e-6
	t_end = 4.5e-6
	# time column is data[:, 1]
	if data[0, 1] < t_begin:
		idx_begin = find_nearest(data[:, 1], t_begin)
	elif data[0, 1] >= t_begin:
		idx_begin = 0

	if data[-1, 1] > t_end:
		idx_end = find_nearest(data[:, 1], t_end)
	elif data[-1, 1] <= t_end:
		idx_end = len(data[:, 1]) - 1

	data_dict['sample'] = data[idx_begin:idx_end, 0]
	data_dict['time'] = data[idx_begin:idx_end, 1]
	data_dict['value'] = data[idx_begin:idx_end, 2]
	data_dict['raw_signal'] = data[idx_begin:idx_end, 3]
	# convert time to wavelength
	# For the fitting process, t = 0 happens right at the trigger begin point (falling edge of the trigger)
	# time in micro seconds
	time = data[idx_begin:idx_end, 1] * 1000 * 1000
	wavelength = 1256 + 15.8138*time + 5.5467*time**2 - 1.0695*time**3 + 0.02803*time**4
	data_dict['wavelength'] = wavelength
	[power_mw, power_dBm] = get_power(data[idx_begin:idx_end, 3])
	data_dict['power_mw'] = power_mw
	data_dict['power_dBm'] = power_dBm

	return data_dict
