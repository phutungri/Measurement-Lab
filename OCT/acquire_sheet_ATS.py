import serial
import time
import numpy as np 
import datetime

import lab_functions as lab

# for a case when 1 axis is z

# define the axes to move in this chunk
ax1 = 'x'
ax2 = 'z'
# define limits of axis
ax1_begin = -15.0
ax1_end = 10.0
ax1_step = 5.0

ax2_begin = 0.0
ax2_end = 100.0
ax2_coarse_step = 2.0
ax2_fine_step = 0.5
ax2_step_factor = 10.0
ax2_change_ht = 60.0



x_loops, z_loops, x_pos, z_pos, gcode = lab.generate_position_parameters(ax1 = ax1, ax1_begin = ax1_begin, ax1_end = ax1_end, ax1_step = ax1_step, \
							ax2 = ax2, ax2_begin = ax2_begin, ax2_end = ax2_end, \
							ax2_fine_step = ax2_fine_step, ax2_coarse_step = ax2_coarse_step, \
							ax2_step_factor = ax2_step_factor, ax2_change_ht = ax2_change_ht)

n = 0
counter = 0
for z in range(z_loops):
	for x in range(x_loops):
		fname = "x_" + "{:.1f}".format(x_pos[x]) + "z_" + "{:.1f}".format(z_pos[z])+".txt"
		print(counter, "\t", x_pos[x], "\t", z_pos[z], "\t", gcode[n],"\t",fname)
		n += 1
		counter += 1
	print(gcode[n])
	print(gcode[n + 1])
	n += 2