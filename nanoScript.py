import socket
import struct
import time
import calendar
import sys
#import matplotlib.pyplot as plt
import pylab as plt
#IP and port for board.  
UDP_IP = "192.168.133.2"
UDP_PORT = 2001
READ_PORT = 49387
#Commands to send to the board.  
oneByte = struct.pack("@2p", "\x02")[1:]
setBurst = "\x01\x09\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00"
setBurst = struct.pack("@18p", setBurst)
setBurstOff = "\x01\x09\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
setBurstOff = struct.pack("@18p", setBurstOff)
reset = "\x01\x00\x02\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00"
reset = struct.pack("@18p", reset)
requestData = "\x01\x00\x02\x00\x00\x00\x00\x00\x00\x0F\x44\x00\x00\x00\x00\x00\x00"
requestData = struct.pack("@18p", requestData)
erase = "\x01\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
erase = struct.pack("@18p", erase)
#Clock Reset Commands
dcmOne = "\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00"
dcmOne = struct.pack("@18p", dcmOne)
dcmTwo = "\x01\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00"
dcmTwo = struct.pack("@18p", dcmTwo)
dcmThree = "\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00"
dcmThree = struct.pack("@18p", dcmThree)
dcmClearOne = "\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
dcmClearOne = struct.pack("@18p", dcmClearOne)
dcmFour = "\x01\x00\x03\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00"
dcmFour = struct.pack("@18p", dcmFour)
dcmClearTwo = "\x01\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
dcmClearTwo = struct.pack("@18p", dcmClearTwo)
clockLockingDelay = 0.7;
Last = 0

continousMode = False
firstTime = True

def question (question, message):
	global continousMode
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	#sock.settimeout(1000000) #A bit generous, but might prevent errors.  
	sock.bind(( "192.168.133.49", 49387))

	response = raw_input(question)
	if response == "s" or response == "S":
		print "Command skipped."
	elif response == "E" or response == "e":
		sys.exit(0)
	elif response == "C" or response == "c":
		continousMode = not continousMode
	else:
		sock.sendto(message, (UDP_IP, UDP_PORT))
		print "Command Completed."
		sock.close()

def send (message):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	#sock.settimeout(3) #A bit generous, but might prevent errors.  
	sock.bind(( "192.168.133.49", 49387))
	sock.sendto(message, (UDP_IP, UDP_PORT))
	print "Command Completed."
	sock.close()

def receiveData ():
	global firstTime
	global Last
	data = []
	formatted = []
	formattedPlace = 0

	send(setBurst)
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	#sock.settimeout(3) #A bit generous, but might prevent errors.  
	sock.bind(( "192.168.133.49", 49387))
	m = sock.recvfrom(2048)

	ipAddress = m[1][0]
	port = m[1][1]
	length = len(m[0])
	header = struct.unpack("<B",m[0][0])[0]
	counter = struct.unpack("<B",m[0][1])[0]
	print "Counter Number:  " + str(counter)
	print "Packet Length:  " + str(length)
	print "From port:  " + str(port)
	print "From IP address:  " + str(ipAddress)  
	relData = m[0][2:]
	d0 = struct.unpack("<Q",m[0][2:10])[0]
	line = "%10s %5d %s %3s %3s %10s"%(ipAddress, port, length, hex(header), hex(counter), hex(d0))
	#print line
	if(length > 100):
		#print "data valid"
		#print len(data)

		dataPoints = 0;
		#d = struct.unpack("<Q", data[x][0:8])[0]
		done = True;
		place = 0
		while done:
			d = struct.unpack("<B", relData[place])[0]
			formatted.append(d)
			place = place + 1
			if place == len(relData):
				dataPoints = (dataPoints + len(relData))
				done = False;
			#print d
		print "Number of Data Points: " + str(dataPoints) 
		now = calendar.timegm(time.gmtime());
		difference = now - Last
		print "Time since last pulse:  " + str(difference)
		Last = now;

		plt.clf()
		plt.ylim([0,255])
		plt.plot(formatted)
		plt.ylim([0,255])
		plt.draw()
		plt.pause(0.01)
		sock.close()

print "Creating Socket:"
print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT

#question("Send one byte?  ", oneByte)
#question("Lock clocks?", dcmOne)
send(oneByte)
send(dcmOne)
time.sleep(clockLockingDelay)
send(dcmTwo)
time.sleep(clockLockingDelay)
send(dcmThree)
time.sleep(clockLockingDelay)
send(dcmClearOne)
time.sleep(clockLockingDelay)
send(dcmFour)
time.sleep(clockLockingDelay)
send(dcmClearTwo)
time.sleep(clockLockingDelay)
#question("Set burst mode?  ", setBurst)
#question("Reset write block?  ", reset)
send(setBurst)
send(reset)
plt.ion()
while True:
	#question("Erase write block?  ", erase)
	if continousMode:
		receiveData()
	elif not continousMode:
		question("Turn off burst mode?  ", setBurstOff)
		receiveData()


