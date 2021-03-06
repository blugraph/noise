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

BACKLOG_BUFF_LEN=59


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
out = ' '

while 1:
# This is to start the measurement, recording and upload files 
	noise = ' '
	out= ' ' 
	try:
#		ser1.flushInput()
		
		r3 = requests.put("http://52.74.191.39/blunois/stationaction.php",data="N1001")
		data = json.loads(r3.content)
		print (r3.content)
		if data[1]=="1":
			if rec==0: # This is recording setup and start recording for the first time 
				print "Record Button Pressed"
				rec=1
				dir_name= "/home/pi/dev/files"
#				dir_name= "/media/files"
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
	              			print "Failed to create file or the py audio failed"
			else: 	# Call back function on recording on, there is nothing to be done
				time.sleep(1)
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

