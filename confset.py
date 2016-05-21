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


while 1:

        try:
           r1 = requests.put("http://52.74.191.39/blunois/stationstatus.php",data="N1001")
#          print (r1.content)
           data = json.loads(r1.content)
#          print "first",data[0]
           if data[0]=="1":
                try:
                        print "In the settings loop"
                        r2 = requests.put("http://52.74.191.39/blunois/stationdata.php",data="N1001")
#                       print (r2.content)
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
			print r2
#                        network_send=data[22] //to see if send over or store locally 
                        network_send="ON"
                        time.sleep(2)
                except:
                        print "No Network avavailable"
                        print "Unexpected error:", sys.exc_info()[0]
           else:
                print "No Settings to change"
                time.sleep(2)
        except:
                print "No Network"

