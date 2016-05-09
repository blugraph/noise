#import smbus
import time
from datetime import datetime
import RPi.GPIO as GPIO
import requests
import json
import serial
import os
import struct

import gps, os, time

time.sleep(3)

#This section deals with GPS
session = gps.gps()
#os.system('clear')
print ' GPS reading'
print '----------------------------------------'
print 'latitude    ' , session.fix.latitude
print 'longitude   ' , session.fix.longitude
print 'time utc    ' , session.utc, session.fix.time
print 'altitude    ' , session.fix.altitude
#print 'eph         ' , session.fix.eph
print 'epv         ' , session.fix.epv
print 'ept         ' , session.fix.ept
print 'speed       ' , session.fix.speed
print 'climb       ' , session.fix.climb
print ' Satellites (total of', len(session.satellites) , ' in view)'
for i in session.satellites:
    print '\t', i

for i in range (1,3):
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
#
cr=0x0D
lf=0x0A

ser1 = serial.Serial("/dev/ttyUSB0", timeout=2)
print ser1
ser1.flushInput()

ser1.write("Frequency Weighting?")
ser1.write('\r\n')

while ser1.inWaiting() > 0:
      out += ser1.read(1)
      print out

ser1.write("Echo,Off")
ser1.write('\r\n')

tnow = time.strftime("%Y/%m/%d %H:%M:%S")
print tnow

ser1.write("Clock,")
ser1.write(tnow)
#ser1.write('\r\n')

# Setting parameters to ON
ser1.write("Display Sub Channel,On")
ser1.write('\r\n')
#time.sleep(1)

ser1.write("Display Ly,On")
ser1.write('\r\n')
#time.sleep(1)

ser1.write("Ly Type,Lpeak")
ser1.write('\r\n')

ser1.write("Display Leq,On")
ser1.write('\r\n')
#time.sleep(1)
ser1.write("Display LE,On")
ser1.write('\r\n')
#time.sleep(1)
ser1.write("Display Lmax,On")
ser1.write('\r\n')
#time.sleep(1)
ser1.write("Display Lmin,On")
ser1.write('\r\n')
#time.sleep(1)
ser1.write("Display LN1,On")
ser1.write('\r\n')
#time.sleep(1)
ser1.write("Display LN2,On")
ser1.write('\r\n')
#time.sleep(1)
ser1.write("Display LN3,On")
ser1.write('\r\n')
#time.sleep(1)
ser1.write("Display LN4,On")
ser1.write('\r\n')
#time.sleep(1)
ser1.write("Display LN5,On")
ser1.write('\r\n')
#time.sleep(1)
ser1.write("AC OUT, Main")
ser1.write('\r\n')

ser1.write("Display Ly, On")
ser1.write('\r\n')

ser1.write("Measure,Start")
ser1.write('\r\n')

noise = "0"

while 1:
#  ser1.flushInput()
  out = ''
  try:
        print time.strftime("%Y/%m/%d %H:%M:%S")
        ser1.write("DOD?")
        ser1.write('\r\n')

        while ser1.inWaiting() > 0:
            out += ser1.read(1)
	
	try:
	        noise= out.splitlines()[1]
        except:
		print "No Response from the Machine"

	print noise
        i = time.strftime("%Y-%m-%d %H:%M:%S")
        print (i)
        payload = [{"deviceID":"N1001", "noise": noise, "time":i}]
        print "Send Data to server"
        r1 = requests.put("http://52.74.191.39/blunois/noisedata.php", data=json.dumps(payload))
        print r1.status_code

        time.sleep(3)

  except KeyboardInterrupt:
        ser1.write("Measure,Stop")
        ser1.write('\r\n')



