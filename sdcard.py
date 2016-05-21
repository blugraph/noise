import os

p = os.popen("df -h /")
i = 0
for i in range (1, 3):
	line = p.readline()
	if i==2:
		print (line.split()[1:5])
		print (line.split()[3])
	
str= line.split()[3]
print str.strip("G")
print int(str.strip("G"))*5

