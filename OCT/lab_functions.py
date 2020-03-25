import serial
import time
import numpy as np 
import datetime

def generate_position_parameters(ax1, ax1_begin, ax1_end, ax1_step,\
					ax2, ax2_begin, ax2_end, ax2_fine_step, ax2_coarse_step, ax2_step_factor, ax2_change_ht):
	"""
	Function to generate movement parameters, as well as current position to be written to file. 
	This function supports two axis only, with ax2 supporting coarse and fine movement.
	ax1 can be either x or y, but not z. Ax2 can be x, y, or z.
	"""
	# check all the conditions
	if (ax1.lower() == 'z'):
		print("ax1 must not be z-axis. Terminating program.")
		exit()
	if (ax2_change_ht <= ax2_begin):
		print("ax2 cannot change coarse to fine at a height lower than ax2_begin. Terminating program.")
		exit()
	if (ax2_change_ht > ax2_end):
		print("ax2 cannot change coarse to fine at a height greater than ax2_end. Terminating program.")
		exit()
	if (ax1_end - ax1_begin) > 250.0:
		print("ax1 range larger than 250 um, terminating program.")
		exit()
	if ((ax2.lower() != 'z') and (ax2_end - ax2_begin) > 250.0):
		print("ax2 range larger than 250 um, terminating program.")
		exit()
	if ((ax2.lower() != 'z') and ax2_step_factor != 1.0):
		print("ax2 step factor incorrect. Terminating program.")
		exit()
	if ((ax2.lower() != 'z') and (ax2_fine_step != ax2_coarse_step)):
		print("ax2 fine step and coarse step unequal when ax2 != z. Terminating program.")
		exit()

	# calculate loops
	# calculate number of loops for axis 1
	ax1_loops = (ax1_end - ax1_begin) // ax1_step
	ax1_loops += 1 # to make the end point inclusive

	# calculating number of loops for axis 2
	# coarse movement
	ax2_loops_coarse = (ax2_change_ht - ax2_begin) // (ax2_coarse_step * ax2_step_factor)
	ax2_travel_during_coarse = ax2_loops_coarse * (ax2_coarse_step * ax2_step_factor)
	ax2_end_position_after_coarse = ax2_begin + ax2_travel_during_coarse
	# fine movement
	ax2_loops_fine = (ax2_end - ax2_end_position_after_coarse) // (ax2_fine_step * ax2_step_factor)
	ax2_travel_during_fine = ax2_loops_fine * (ax2_fine_step * ax2_step_factor)
	ax2_end_position_after_fine = ax2_end_position_after_coarse + ax2_travel_during_fine
	# total loops
	ax2_loops = ax2_loops_coarse + ax2_loops_fine
	ax2_loops += 1 # to make end point inclusive

	ax1_loops = int(ax1_loops)
	ax2_loops = int(ax2_loops)

	# incremental move prefix
	inc_move_ax1 = "G21G91" + ax1.upper() + "+"
	inc_move_ax2 = "G21G91" + ax2.upper() + "+"
	# reset ax1
	ax1_reset_dist = (ax1_end - ax1_begin) + ax1_step # the additional ax1_step accounts for end point inclusion
	reset_ax1 = "G21G91" + ax1.upper() + "-" + str(ax1_reset_dist) + "F500"
	# reset ax2 if it's not z
	if (ax2.lower() != 'z'):
		ax2_reset_dist = (ax2_end - ax2_begin) + ax2_fine_step
		reset_ax2 = "G21G91" + ax2.upper() + "-" + str(ax2_reset_dist) + "F500"

	feed_rate = "F100"
	ax2_pos = ax2_begin # initialize ax2 position
	ax1_pos_list = []
	ax2_pos_list = []
	g_code_list = []
	print(ax1 + "\t" + ax2 + "\t" + "g-code next")
	for j in range(ax2_loops):
		ax1_pos = ax1_begin # this can be x or y
		for i in range(ax1_loops):
			ax1_pos_list.append(ax1_pos)
			gcode_move_ax1 = inc_move_ax1 + str(ax1_step) + feed_rate
			g_code_list.append(gcode_move_ax1)
			# print("%0.2f\t%0.2f\t%s" %(ax1_pos, ax2_pos, gcode_move_ax1))
			# increase ax1 step
			ax1_pos = ax1_pos + ax1_step
			
		# increase ax2 step
		ax2_pos_list.append(ax2_pos)
		if j < ax2_loops_coarse:
			ax2_pos = ax2_pos + (ax2_coarse_step * ax2_step_factor)
			gcode_move_ax2 = inc_move_ax2 + str(ax2_coarse_step) + feed_rate
		else:
			ax2_pos = ax2_pos + (ax2_fine_step * ax2_step_factor)
			gcode_move_ax2 = inc_move_ax2 + str(ax2_fine_step) + feed_rate
		g_code_list.append(reset_ax1)
		if j != (ax2_loops - 1):
			g_code_list.append(gcode_move_ax2)
		if (j == (ax2_loops - 1)) and (ax2.lower() != 'z'):
			g_code_list.append(reset_ax2)
		if (j == (ax2_loops - 1)) and (ax2.lower() == 'z'):
			g_code_list.append("G21G91Z0F100")
		
	return ax1_loops, ax2_loops, ax1_pos_list, ax2_pos_list, g_code_list

# # for a case when 1 axis is z
# x_loops, z_loops, x_pos, z_pos, gcode = generate_position_parameters(ax1 = 'x', ax1_begin = -15.0, ax1_end = 15.0, ax1_step = 5.0, \
# 							ax2 = 'z', ax2_begin = 0.0, ax2_end = 100.0, \
# 							ax2_fine_step = 0.50, ax2_coarse_step = 2.0, ax2_step_factor = 10.0, ax2_change_ht = 60.0)

# n = 0
# counter = 0
# for z in range(z_loops):
# 	for x in range(x_loops):
# 		fname = "x_" + "{:.1f}".format(x_pos[x]) + "z_" + "{:.1f}".format(z_pos[z])+".txt"
# 		print(counter, "\t", x_pos[x], "\t", z_pos[z], "\t", gcode[n],"\t",fname)
# 		n += 1
# 		counter += 1
# 	print(gcode[n])
# 	print(gcode[n + 1])
# 	n += 2


# x_loops, y_loops, x_pos, y_pos, gcode = generate_position_parameters(ax1 = 'x', ax1_begin = -125.0, ax1_end = 125.0, ax1_step = 5.0, \
# 							ax2 = 'y', ax2_begin = -125.0, ax2_end = 125.0, \
# 							ax2_fine_step = 5.0, ax2_coarse_step = 5.0, ax2_step_factor = 1.0, ax2_change_ht = 100.0)

# n = 0
# for y in range(y_loops):
# 	for x in range(x_loops):
# 		print(x_pos[x], "\t", y_pos[y], "\t", gcode[n])
# 		n += 1
# 	print(gcode[n])
# 	print(gcode[n + 1])
# 	n += 2

# 	arduino.close()
