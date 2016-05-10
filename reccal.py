import pyaudio
import time
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "a.wav"
frames = []

p = pyaudio.PyAudio()
def callback(in_data, frame_count, time_info, status):
	frames.append(in_data)
	return (in_data, pyaudio.paContinue)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
		stream_callback=callback)

print("* recording")

#while stream.is_active():
#    time.sleep(1)
for i in range(0,5):
	time.sleep(1)


print("* finished")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
