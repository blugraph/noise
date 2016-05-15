import pyaudio
import wave
import time
from datetime import datetime
import os
import requests
import json
import serial


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
dir_name= "/home/pi/cl/"+time.strftime("%Y-%m-%d")
try:
	os.makedirs(dir_name)
except OSError:
	if os.path.exists(dir_name):
		print ": Already directory exists"
	else:
		print ": Some system Error in creating directory"
	print ": Failed creating the directory"

try:
	base_filename=time.strftime("%H_%M_%S")
        abs_file_name=os.path.join(dir_name, base_filename + "." + "wav")
        f = open(abs_file_name, 'w')
except:
                print t,": Failed to create file"

WAVE_OUTPUT_FILENAME = abs_file_name

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

#print("* recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    print i	
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
