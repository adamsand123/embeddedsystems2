import RPi.GPIO as GPIO
import time
import socket
import sys
import threading

global sensData # global var that recieves data from tcp connections
sensData=2

# function that reads the value from the light sensor
def sensor(sensorPin):
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(sensorPin, GPIO.OUT)
	GPIO.output(sensorPin, GPIO.LOW)
	GPIO.setup(sensorPin, GPIO.IN)

	return GPIO.input(sensorPin)
# 
def led(val):
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)

	printOff=0
	printOn=0
#	count=0

	while True:
		f=open("results.txt","a+")
		GPIO.setup(3,GPIO.OUT)
		if sensData==1 and isDark():
			GPIO.output(3,1)
			if printOn==0:
#				print("ON " + str(time.time())+" "+str(count))
#				f.write(str(time.time())+"\n")
				printOn=1
				printOff=0
#			time.sleep(5) # delay på 20 sekunder innan lampan släcks
		elif not isDark() or sensData==0:
			GPIO.output(3,0)
			if printOff==0:
#				print("OFF " + str(time.time())+" "+str(count))
#				f.write(str(time.time())+"\n")
				printOn=0
				printOff=1
		else:
			print('',end='')
#		count+=1
#		f.close()

# takes 10 readings from the light sensor to determine if its dark or not
def isDark():
	count=0
	countDark=0
	while count < 10: # Reads light sensor 10 times every 0.1 seconds
		if sensor(23) == GPIO.LOW:
			countDark+=1
		count+=1
		#time.sleep(0.1) # Sleep for a 10th of a second between every sampling
	return countDark > 5

# Function that checks the value of sensData and sends it to led function ever 1/10th of a second
def lightControl():
	led(sensData)

def tcpListen():
	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Bind the socket to the port
	addr='192.168.1.112'
	server_address = (addr, 10000)
	print('starting up on {} port {}'.format(*server_address))
	sock.bind(server_address)

	# Listen for incoming connections
	sock.listen(1)
	global sensData
	f=open("transmission.txt","a")
	while True:
		# Wait for a connection
		print('waiting for a connection')
		connection, client_address = sock.accept()
		try:
			print('connection from', client_address)

			while True:
				# Receive the data in small chunks and retransmit it
				data = connection.recv(16)
#				print('received {!r}'.format(data))
				if data:
					sensData=int(data.decode())
					print(str(time.time()))
					f.write(str(time.time()))
				else:
					print('no data from', client_address)
					break
		except KeyboardInterrupt: # Except and finally used so we can safely interrupt the script with ctrl+C
			pass
		finally:
			connection.close()
def main():
	GPIO.setmode(GPIO.BOARD) # so that we can refer to the pins by their number
	try: # create one thread for recieving data and one for controlling the light sensor and led
		tcpThread=threading.Thread(target=tcpListen)
		tcpThread.start()
		ledThread=threading.Thread(target=lightControl)
		ledThread.start()
	except KeyboardInterrupt: # Except and finally used so we can safely interrupt the script with ctrl+C
		pass
	finally:
		print("\nKeyboardInterrupt detected: closing script")
		GPIO.cleanup()

if __name__=='__main__':
	main()
