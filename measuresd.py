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

BACKLOG_BUFF_LEN=999

tofile=[]

lps_int=1
leq_int=10

SEND_LOOP=60 

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


#time.sleep(3)

#This section deals with GPS
session = gps.gps()
#os.system('clear')
print ' GPS reading'
#print '----------------------------------------'
print 'latitude    ' , session.fix.latitude
print 'longitude   ' , session.fix.longitude
print 'time utc    ' , session.utc, session.fix.time
#print 'altitude    ' , session.fix.altitude
#print 'eph         ' , session.fix.eph
#print 'epv         ' , session.fix.epv
#print 'ept         ' , session.fix.ept
#print 'speed       ' , session.fix.speed
#print 'climb       ' , session.fix.climb
#print ' Satellites (total of', len(session.satellites) , ' in view)'
#for i in session.satellites:
#    print '\t', i

for i in range (1,2):
        print "Waiting for GPS."
        time.sleep(1)
        if (session.fix.latitude == 0.0 or session.fix.longitude == 0.0):
                print "Waiting for GPS.."
                time.sleep(1)
        elif (session.utc == 'nan'):
                print "Waiting for GPS..."
                time.sleep(1)
        else:
                print "Locking to GPS"

if (session.fix.latitude == 0.0 or session.fix.longitude == 0.0 or session.utc == 'nan'):
        print "Cant find the location"
        print "Cant find time"





p = os.popen("df -h /")
i = 0
for i in range (1, 3):
        line = p.readline()
        if i==2:
                disk_space= (line.split()[3])

ser1 = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=2)
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
time.sleep(2)
ser1.flushInput()

out = ' '
set=0
while 1:
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
                  if set==0:
		     set=1	
	             try:
                        print "In the settings loop"
                        r2 = requests.put("http://52.74.191.39/blunois/stationdata.php",data="N1001")
                        print (r2.content)
                        data = json.loads(r2.content)
                        # Settings for data capture"
                        if data[3]=="100ms":
                                lps_int=.1
                        elif data[3]=="200ms":
                                lps_int=.2
                        elif data[3]=="1s":
                                lps_int=1
                        elif data[3]=="Leq1s":
                                lps_int=1
                        else :
                                lps_int=100

                        if data[0]=="Off":
                                leq_int=100
                        elif data[0]=="10s":
                                leq_int=10
                        elif data[0]=="1m":
                                leq_int=60
                        elif data[0]=="5m":
                                leq_int=300
                        elif data[0]=="10m":
                                leq_int=600
                        elif data[0]=="30m":
                                leq_int=1800
                        elif data[0]=="1h":
                                leq_int=3600
                        elif data[0]=="8h":
                                leq_int=28800
                        elif data[0]=="24h":
                                leq_int=86400
                        elif data[0]=="Manual":
                                leq_int=data[0]

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
#                        ser1.write("Ly Type,")
#                        ser1.write(data[13])
#			ser1.write("Lpeak")
				
#                        ser1.write('\r\n')
#                        time.sleep(.2)
                        ser1.write("TRM,")
                        ser1.write(data[19])
                        ser1.write('\r\n')
                        time.sleep(.2)
                        ser1.write("Diffuse Sound Field Correction,")
                        ser1.write(data[8])
                        ser1.write('\r\n')
#                       ser1.flushInput()               
                        time.sleep(1)
                        ser1.write("Delay Time,")
                        ser1.write(data[20])
                        ser1.write('\r\n')
                        ser1.write("Back Erase,")
                        ser1.write(data[21])
                        ser1.write('\r\n')
                        network_send=data[22] #to see if send over or store locally 
#                        network_send="ON"
#			ser1.flushInput()  
			time.sleep(2)
			while ser1.inWaiting() > 0:
                                out += ser1.read(1)
                        print out
                        time.sleep(2)

                     except:
                        print "No Network avavailable"
                        print "Unexpected error:", sys.exc_info()[0]
		  if lps_int==100 and leq_int==100:
		    print "No Measurement Needs to be done - Both Intervals are turned off"	
		    measure=0
		  else:
			if lps_int < leq_int:
	            		meas_int=lps_int
		    		measure=1
		  	else:
		    		meas_int=leq_int
		    		measure=1
                        ser1.write("Measure,Start")
                        ser1.write('\r\n')
                  	print "The measurement Interavel is :"+str(meas_int)+"s"
			while ser1.inWaiting() > 0:
                                out += ser1.read(1)
                        print out
 		  if measure==1:
			meas_star_time=time.time()
		    	while ((time.time() - meas_star_time) < SEND_LOOP) or (time.time() - meas_star_time) < meas_int:	
				ser1.flushInput()
	                        ser1.write("DOD?")
        	                ser1.write('\r\n')
				time.sleep(meas_int)
		                while ser1.inWaiting() > 0:
                	                out += ser1.read(1)
#				print out
			        try:
        	                       	noise= out.splitlines()[1]
#					print "++++++"	
					print noise
#					print "++++++"
					ser1.flushInput()
					i = time.strftime("%Y-%m-%d %H:%M:%S")
                                	print (i)
                                	payload = {"deviceID":"N1001", "noise": noise, "time":i}                                        
                                	tofile.append(payload)
	                        except:
               		               print "No Response from the Machine"
				out=' '
				noise=' '
				#time.sleep(meas_int) 
			if (len(tofile))>0:	
                		print "At least one data in the making"
        			try:
#				   if network_send=="ON":
                			r1 = requests.put("http://52.74.191.39/blunois/noisedata.php", data=json.dumps(tofile), timeout=0.1)
	                		print r1.status_code,": server response."
#       	        		print r1.content
#                			del tofile[:]
        			except:
                			print ": Network Failed while uploading data buffer:"	  
#				if len(tofile)>BACKLOG_BUFF_LEN:
				try:
					dir_name= "/media/BGBAR/measure/"+time.strftime("%Y-%m-%d_%H")
        	    			try:
                				os.makedirs(dir_name)
            				except OSError:
                				if os.path.exists(dir_name):
                        				print ": Already directory exists"
                				else:
                        				print ": Some system Error in creating directory"

       				        	print ": Failed creating the directory"

		            		try:
#              					base_filename=time.strftime("%H_%M_%S")
#              					abs_file_name=os.path.join(dir_name, base_filename + "." + "txt")
               					
						if not os.path.isfile("measure.txt"):
							with open(fname, mode='w') as f:
        							f.write(json.dumps(tofile, indent=2))
						else:
    							with open(fname) as feedsjson:
        							feeds = json.load(feedsjson)
    								feeds.append(tofile)
    								with open(fname, mode='w') as f:
        								f.write(json.dumps(feeds, indent=2))
#						f = open("measure.txt", 'w')
#              					print>>f, json.dumps(tofile)
#			                	del tofile[:]
            				except:
                				print ": Failed to create file"
				except:
					print "File can not be written to the drive"
				del tofile[:]				
		else:
			print "Measure Released"
			s=0
			ser1.write("Measure,Stop")
        		ser1.write('\r\n')
	
	except (KeyboardInterrupt, SystemExit):
			
		ser1.write("Measure,Stop")
       		ser1.write('\r\n')
                print "No Network avavailable"
                print "Unexpected error:", sys.exc_info()[0]	
		exit()
	
# This is to start the recording

