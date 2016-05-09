import time
from datetime import datetime
import RPi.GPIO as GPIO
import requests
import json
import serial
import os
import struct
import sys

import gps, os, time

lf=0x0A

setNameList = [
'remote_cntrl',
'sys_ver',
'station_datetime',
'sd_size',
'sd_free',
'disp_add_proc',
'disp_leq',
'disp_le',
'disp_lmax',
'disp_lmin',
'disp_ln1',
'disp_ln2',
'disp_ln3',
'disp_ln4',
'disp_ln5',
'per_ln1',
'per_ln2',
'per_ln3',
'per_ln4',
'per_ln5',
'disp_time_lvl',
'disp_time_lvl_s',
'out_lr_up',
'out_lr_lr',
'ac_out',
'dc_out',
'com_int',
'bd_rate',
'st_md',
'st_nm',
'st_ad',
'measure_start',
'measure_stop',
'measure_pause',
'manual_store',
'meaure_pre_int',
'measure_num',
'measure_unit',
'leq_cal_int',
'leq_cal_num',
'leq_cal_unit'
'ws_cor',
'diff_sound_corr',
'del_time',
'back_erase',
'freq_weigh',
'freq_weigh_sub',
'time_weigh',
'time_weigh_sub',
'add_proc',
'underr_lp',
'underr_leq',
'overld_lp',
'overld_leq',
'overld_out',
'trm',
'noise'
]

noswals={}


ser1 = serial.Serial("/dev/ttyUSB0", timeout=2)
print ser1
ser1.flushInput()

# Setting Clock 
tnow = time.strftime("%Y/%m/%d %H:%M:%S")
print tnow

ser1.write("Clock,")
ser1.write(tnow)
ser1.write('\r\n')

# Displays switched ON 
ser1.write("Display Sub Channel,On")
ser1.write('\r\n')

ser1.write("Display Ly,On")
ser1.write('\r\n')

ser1.write("Display Leq,On")
ser1.write('\r\n')

ser1.write("Display LE,On")
ser1.write('\r\n')

ser1.write("Display Lmax,On")
ser1.write('\r\n')

ser1.write("Display Lmin,On")
ser1.write('\r\n')

ser1.write("Display LN1,On")
ser1.write('\r\n')

ser1.write("Display LN2,On")
ser1.write('\r\n')

ser1.write("Display LN3,On")
ser1.write('\r\n')

ser1.write("Display LN4,On")
ser1.write('\r\n')

ser1.write("Display LN5,On")
ser1.write('\r\n')

ser1.write("AC OUT, Main")
ser1.write('\r\n')

ser1.flushInput()

out = ' '

while 1:
	try:
	   r1 = requests.put("http://52.74.191.39/blunois/stationstatus.php",data="N1001")
#	   print (r1.content)
	   data = json.loads(r1.content)
#	   print "first",data[0]
           if data[0]=="1":
                try:
                        print "In the settings loop"

                        r2 = requests.put("http://52.74.191.39/blunois/stationdata.php",data="N1001")
#                       print (r2.content)
                        data = json.loads(r2.content)

                        ser1.write("Output Level Range Upper,")
                        ser1.write(data[10])
                        ser1.write('\r\n')

                        ser1.write("Output Level Range Lower,")
                        ser1.write(data[11])
                        ser1.write('\r\n')

                        ser1.write("Frequency Weighting,")
                        ser1.write(data[9])
                        ser1.write('\r\n')

                        ser1.write("Time Weighting,")
                        ser1.write(data[12])
                        ser1.write('\r\n')

                        ser1.write("Ly Type,")
                        ser1.write(data[13])
                        ser1.write('\r\n')

                        ser1.write("TRM,")
                        ser1.write(data[19])
                        ser1.write('\r\n')

                        ser1.write("Diffuse Sound Field Correction,")
                        ser1.write(data[8])
                        ser1.write('\r\n')

#                       ser1.flushInput()               
                        time.sleep(1)
#                       ser1.write("Delay Time,")
#                        ser1.write(data[20])
#                        ser1.write('\r\n')
#                       ser1.write("Back Erase,")
#                        ser1.write(data[21])
#                        ser1.write('\r\n')

                        ser1.write("Frequency Weighting?")
                        ser1.write('\r\n')

#                       while ser1.inWaiting() > 0:
#                               out += ser1.read(1)
#                       print out       

                        r2 = requests.put("http://52.74.191.39/blunois/stationdataup.php",data="N1001")
                        time.sleep(2)
                except:
                        print "No Network avavailable"
                        print "Unexpected error:", sys.exc_info()[0]
	   else:
                print "No Settings to change"
                time.sleep(2)

	except:
		print "No Network"

# This is to start the measurement, recording and upload files 

	try:
		r3 = requests.put("http://52.74.191.39/blunois/stationaction.php",data="N1001")
		data = json.loads(r3.content)

		if data[0]=="1":
			print "Measure Button Pressed"
		else:
			print "Measure Released"
	
		if data[1]=="1":
                        print "Record Button Pressed"
                else:
                        print "Record Button Released"

		if data[2]=="1":
                        print "Upload  Button Pressed"
                else:
                        print "Upload Button  Released"

	except:
                        print "No Network avavailable"
                        print "Unexpected error:", sys.exc_info()[0]	

# This is to start the recording

