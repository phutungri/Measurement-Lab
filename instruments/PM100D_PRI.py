from ctypes import cdll,c_long, c_ulong, c_uint32,byref,create_string_buffer,c_bool,c_char_p,c_int,c_int16,c_double, sizeof, c_voidp
from TLPM_PRI import TLPM
import time

def setupPowerMeter(wavelength, AvgMeasTimeInSeconds, powerAutorange):
	tlPM = TLPM()
	deviceCount = c_uint32()
	tlPM.findRsrc(byref(deviceCount))
	
	# print("devices found: " + str(deviceCount.value))
	
	# resourceName = create_string_buffer(1024)
	
	# for i in range(0, deviceCount.value):
	# 	tlPM.getRsrcName(c_int(i), resourceName)
	# 	# print(c_char_p(resourceName.raw).value)
	# 	break

	# resource name for PM100D
	resourceName = create_string_buffer(b"USB0::0x1313::0x8078::P0015908::INSTR")
	# print(c_char_p(resourceName.raw).value)
	# tlPM.close()
	
	# tlPM = TLPM()
	#resourceName = create_string_buffer(b"COM1::115200")
	#print(c_char_p(resourceName.raw).value)
	tlPM.open(resourceName, c_bool(True), c_bool(True))
	avgTime = c_double(AvgMeasTimeInSeconds)
	set_Wavelength = c_double(wavelength)
	set_PowerAutorange = c_int(powerAutorange)
	tlPM.setAvgTime(avgTime)
	tlPM.setWavelength(set_Wavelength)
	tlPM.setPowerAutoRange(set_PowerAutorange)
	time.sleep(2)
	# tlPM.close()
	return tlPM, resourceName

def getPowerMeterMeasurement(tlPM, resourceName):
	# # tlPM = TLPM()
	# tlPM = tlpm
	# # tlPM.open(resourceName, c_bool(True), c_bool(True))
	power = c_double()
	tlPM.measPower(byref(power))
	power_measurement = power.value
	# tlPM.close()
	return power_measurement

# #################################
# ##### Implementation method #####
# #################################
# avgTimeSec = 0.05
# wavelength = 1310
# autorange = 1 # must be 0 or 1

# tlPM, resourceName = setupPowerMeter(wavelength, avgTimeSec, autorange)

# for i in range(10):
# 	p1 = getPowerMeterMeasurement(tlPM, resourceName)
# 	print(p1)
# 	time.sleep(0.2)

# tlPM.close()