import time
from datetime import datetime
import RPi.GPIO as GPIO
import requests
import json
import serial
import struct
import sys
import os
import time
from os import listdir
from os.path import isfile, join
import glob, os
import requests
import cPickle as pickle
import gps, os, time

import pyaudio
import wave

stationID="N1001"

file_list_local = []
file_list_target = []
SERVER_ADDR = "52.74.191.39"
RUN_DIR = "/home/pi/dev/"

dir_name = RUN_DIR

os.chdir(dir_name)
for file in glob.glob("*.wav"):
        file_list_local.append(file)

print "There are " + str(len(file_list_local)) + " files in the directory"

for k in range(0, len(file_list_local)): 
	print "test"

for i in range (0,1):
	files1 = {'file': file_list_local[i]}	
	print "Sending the file now"
	svc_url = "http://" + SERVER_ADDR + "/blunois/voicefile.php"
	r1 = requests.put("http://52.74.191.39/blunois/voicesend.php", files=files1, timeout=0.1)
	print r1.status_code
	if r1.status_code=="200":
 #                                               try:
		print "Successfully sent the file, deleting now"
 		
#                  	except:

#					print "Network error"


