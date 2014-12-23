import os.path, re, subprocess
import argparse
import time, datetime
import math
import hashlib

# Get today date
cD = datetime.date.today()
cYear = "%04d" % cD.year
cMonth = "%02d" % cD.month
cDay = "%02d" % cD.day

# Set date in YYYY.MM.DD format
curDate = cYear + '.' + cMonth + '.' + cDay

# Set working directories and chdir to current date folder
dailiesPath = '/mnt/VIDEO1/LUNA/DAILIES/' + curDate + '/'
shotsPath = '/mnt/VIDEO1/LUNA/FROM_CG_DAILIES/'
os.chdir(dailiesPath)
print dailiesPath

# Define inotify function
def watchfile():
	f = subprocess.check_output(['inotifywait', '-r', '--format', '\'%f\'', '-e', 'create', dailiesPath])
	return f[1:-2]

# Main cycle
while (1):
	# Wait for new file created
	newFile = subprocess.check_output(['inotifywait', '-r', '--format', '\'%f\'', '-e', 'create', dailiesPath])
	print newFile + 'Created'
	time.sleep(2)
	statInfo = os.stat(newFile[1:-2])
	newFileSize = statInfo.st_size
	writewait = round (newFileSize / 30000000)
	time.sleep(10)
	# Set shotDir and make new directory
	shotDir = shotsPath + newFile[1:-10] +'/'
	print shotDir
	if not os.path.isdir(shotDir):
		os.mkdir(shotDir,0777)
	# Set name for H264 encoded file
	newFileH264 = newFile[1:-10] + '_H264' + newFile[-10:-6] + '.mov'
	# Run ffmpeg
	try:
   		codingFile = subprocess.check_output(['ffmpeg', '-i', newFile[1:-2], '-c:v', 'libx264', '-pass', '1', '-b:v', '10000k', newFileH264])
   	except subprocess.CalledProcessError as e:
   		print e.output
   	# Calculate SHA1 hash
   	sha1 = hashlib.sha1()
   	f = open(newFileH264,'rb')
   	try:
   		sha1.update(f.read())
   	finally:
   		f.close()
   	print 'Secure hash:' + sha1.hexdigest()
   	# Make hardlink to H264 encoded file in shotDir
   	os.link(newFileH264, shotDir + newFileH264)


	#newfile = subprocess.check_output(['inotifywait', '--format', '\'%f\'', '-e', 'close_write', newfile[1:-2]])
	#print newfile + 'Closed'
	#codingFile = subprocess.check_output(['ffmpeg', '-i', newFile[1:-2], '-c:v', 'libx264', '-pass', '1', '-b:v', '10000k', newFile[1:-6]+'h264'+'.mov'])

#try:
#    dailyfile = open(newfile, "r+") # or "a+", whatever you need
#except IOError:
#    print "Could not open file! Please close Excel!"
