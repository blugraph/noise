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

import pyaudio
import wave

stationID="N1001"

lf=0x0A

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
WIDTH = 2
rec=0 # To indicate that a recording has started
livefile=0 # To indicate that a file info not updated to server is available now
fltr=0 # To Indicate that a file avaialble to transfer to is available now 


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

def callback(in_data, frame_count, time_info, status):
        frames.append(in_data)
        return (in_data, pyaudio.paContinue)

noswals={}

p = os.popen("df -h /")
i = 0
for i in range (1, 3):
        line = p.readline()
        if i==2:
                disk_space= (line.split()[3])

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
time.sleep(.2)
ser1.write("Display Ly,On")
ser1.write('\r\n')
time.sleep(.2)
ser1.write("Display Leq,On")
ser1.write('\r\n')
time.sleep(.2)
ser1.write("Display LE,On")
ser1.write('\r\n')
time.sleep(.2)
ser1.write("Display Lmax,On")
ser1.write('\r\n')
time.sleep(.2)
ser1.write("Display Lmin,On")
ser1.write('\r\n')
time.sleep(.2)
ser1.write("Display LN1,On")
ser1.write('\r\n')
time.sleep(.2)
ser1.write("Display LN2,On")
ser1.write('\r\n')
time.sleep(.2)
ser1.write("Display LN3,On")
ser1.write('\r\n')
time.sleep(.2)
ser1.write("Display LN4,On")
ser1.write('\r\n')
time.sleep(.2)
ser1.write("Display LN5,On")
ser1.write('\r\n')
time.sleep(.2)
ser1.write("AC OUT, Main")
ser1.write('\r\n')
time.sleep(.2)
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
			time.sleep(.2)
                        ser1.write("Output Level Range Lower,")
                        ser1.write(data[11])
                        ser1.write('\r\n')
			time.sleep(.2)
                        ser1.write("Frequency Weighting,")
                        ser1.write(data[9])
                        ser1.write('\r\n')
			time.sleep(.2)	
                        ser1.write("Time Weighting,")
                        ser1.write(data[12])
                        ser1.write('\r\n')
			time.sleep(.2)
                        ser1.write("Ly Type,")
                        ser1.write(data[13])
                        ser1.write('\r\n')
			time.sleep(.2)
                        ser1.write("TRM,")
                        ser1.write(data[19])
                        ser1.write('\r\n')
			time.sleep(.2)
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
	noise = ' '
	out= ' ' 
	try:
#		ser1.flushInput()
		
		r3 = requests.put("http://52.74.191.39/blunois/stationaction.php",data="N1001")
		data = json.loads(r3.content)
		print (r3.content)
		if data[0]=="1":
			print "Measure Button Pressed"
			ser1.write("Measure,Start")
			ser1.write('\r\n')

                        ser1.flushInput()
#			print time.strftime("%Y/%m/%d %H:%M:%S")
        		ser1.write("DOD?")
        		ser1.write('\r\n')
			time.sleep(1)			
		        while ser1.inWaiting() > 0:
            			out += ser1.read(1)
#			print out
        		try:
                		noise= out.splitlines()[2]
#				print "This is result" + noise
        		except:
                		print "No Response from the Machine"
		        print noise
        		i = time.strftime("%Y-%m-%d %H:%M:%S")
        		print (i)
        		payload = [{"deviceID":"N1001", "noise": noise, "time":i}]
        		print "Send Data to server"
        		r4 = requests.put("http://52.74.191.39/blunois/noisedata.php", data=json.dumps(payload))
        		print r4.status_code
		        time.sleep(2)

		else:
			print "Measure Released"
			ser1.write("Measure,Stop")
        		ser1.write('\r\n')
	
		if data[1]=="1":
			if rec==0: # This is recording setup and start recording for the first time 
				print "Record Button Pressed"
				rec=1
				dir_name= "/home/pi/dev/files"
            			try:
	               			os.makedirs(dir_name)

            			except OSError:
                			if os.path.exists(dir_name):
                        			print "Directory Already exists"
                			else:
                        			print "Some system Error in creating directory"

		                	print " Failed creating the directory"

	            		try:
					p = pyaudio.PyAudio()
                                        base_filename=(time.strftime("%Y-%m-%d_%H_%M_%S")+"." + "wav")
#                                        abs_file_name=os.path.join(dir_name, base_filename + "." + "wav")
					abs_file_name=os.path.join(dir_name, base_filename)	
                                        wf = wave.open(abs_file_name, 'wb')

                                        frames = []

                                        stream = p.open(format=FORMAT,
                                                channels=CHANNELS,
                                                rate=RATE,
                                                input=True,
                                                frames_per_buffer=CHUNK,
                                                stream_callback=callback)

			    	except:
	              			print t,"Failed to create file or the py audio failed"
			else: 	# Call back function on recording on, there is nothing to be done
				time.sleep(.5)
				print("* recording")
		else:
			if rec==1: # Recording has stopped, now save the file and indicate there is a live file. 
				rec=0
				print "Record Released"
				stream.stop_stream()
				stream.close()
				p.terminate()
				wf.setnchannels(CHANNELS)
				wf.setsampwidth(p.get_sample_size(FORMAT))
				wf.setframerate(RATE)
				wf.writeframes(b''.join(frames))
				wf.close()
				livefile=1
	                else:
				if livefile==1: # There is a file to transfer
					print "Trasnferring file info"
					payload = [{"FileName":base_filename, "stationID":stationID, "StorageSpace":disk_space}]
					r4 = requests.put("http://52.74.191.39/blunois/recordvoice.php",data=json.dumps(payload))
		                       	print (r4.content)
					livefile=0
				else:
					print "Record Inactive "


		if data[2]=="1":
                        print "Upload  Button Pressed"
			r3 = requests.put("http://52.74.191.39/blunois/voicesend.php",data="N1001")
	                data = json.loads(r3.content)
        	        print (r3.content)
                else:
                        print "Upload Button  Released"

	except (KeyboardInterrupt, SystemExit):
			
			ser1.write("Measure,Stop")
        		ser1.write('\r\n')
                        print "No Network avavailable"
                        print "Unexpected error:", sys.exc_info()[0]	
			exit()
	
# This is to start the recording

