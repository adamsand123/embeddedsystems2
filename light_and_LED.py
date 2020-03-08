import RPi.GPIO as GPIO # to be able to send and recieve input from rpi
import time		# for various time functions and sleep
import socket		# for tcp connections
import threading	# library to let us use threading

global sensData # global var that recieves data from tcp connections
sensData=2 # we give sensData an initial value (later it will have either 0 or 1 indiciating movement on or off)

# function that reads the value from the light sensor
def sensor(sensorPin):
	# modules to enable reading to and from rpi
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(sensorPin, GPIO.OUT)
	GPIO.output(sensorPin, GPIO.LOW)
	GPIO.setup(sensorPin, GPIO.IN)

	return GPIO.input(sensorPin) # return the value that was read from the light sensor
# function to control the led lamp
def led(val):
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(3, GPIO.OUT)
	GPIO.output(3,0)

	printOff=0 # 1 indicates last state was LED lamp off 0 indicates on
	printOn=0 # 1 indicates last state was LED lamp on 0 indicates off

	while True: # continue to loop to be able to continually check the darkness of the light sensor and control led
		if sensData==1 and isDark(): # if it has recieved the on signal from motion sensor and the room is dark
			GPIO.output(3,1) # turn led on
			if printOn==0: # if last state was led off change the values on the variables below to indicate last state is now on
				printOn=1
				printOff=0
		elif not isDark() or sensData==0: # if its not dark and it has recieved the off signal from the movement sensor
			GPIO.output(3,0) # turn led off
			if printOff==0: # if last state was on change variables to indicate last state is off
				printOn=0
				printOff=1
		else:
			print('',end='') # print an empty line aka do nothing

# takes 10 readings from the light sensor to determine if its dark or not
def isDark():
	count=0 # count variable to loop 10 times
	countDark=0 # counts the number of "dark" readings from light sensor
	while count < 10: # Reads light sensor 10 times every 0.1 seconds
		if sensor(23) == GPIO.LOW: #if light sensor indicates dark increment countDark by 1
			countDark+=1
		count+=1
	return countDark > 8 # return true if we got more than 8/10 dark readings (can adjust this to adjust sensitivity)

# Function that checks the value of sensData and sends it to led function ever 1/10th of a second
# OLD FUNCTION NOT NECCESARY ANUYMORE CAN START IN MAIN FROM led() INSTEAD
def lightControl():
	led(sensData)

# function to listen and recieve tcp connections on prt 10000
def tcpListen():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# set up server socket
	addr='192.168.1.112'
	server_address = (addr, 10000)
	sock.bind(server_address)

	# Listen for incoming connections
	sock.listen(1)
	global sensData
	#continally loop to listen for new and existing connections
	while True:
		# Wait for a connection
		print('waiting for a connection')
		connection, client_address = sock.accept() # accepts a connection and stores connection id and address
		try:
			print('connection from', client_address) # print out a message that a connection was recieved

			while True:
				# Receive the data in small chunks and retransmit it
				data = connection.recv(16) # read the data from the connection variable
				if data: # if there was data recieved
					sensData=int(data.decode()) #store data as an integer in the global variable sensData to be used by the LED control function in the main thread
				else:
					print('no data from', client_address)
					break
		except KeyboardInterrupt: # Except and finally used so we can safely interrupt the script with ctrl+C
			pass
		finally: # close connection on keyboard interrupt
			print("Keyboard interrupt: closing connection")
			connection.close()
# main function starts tcp thread and continue to execute from the led control function
def main():
	GPIO.setmode(GPIO.BOARD) # so that we can refer to the pins by their number
	try: # create one thread for recieving data and one for controlling the light sensor and led
		tcpThread=threading.Thread(target=tcpListen)
		tcpThread.start()
		lightControl()
	except KeyboardInterrupt: # Except and finally used so we can safely interrupt the script with ctrl+C
		tcpThread.join() # on keyboard interrupt join the tcpThread to the mainthread aka kill it
		print("Killing tcp thread") # trouble shooting message
		pass
	finally:
		GPIO.cleanup() # clean up the rpi connections
		print("CLEAN") # trouble shooting message

# start exectution from the main thread
if __name__=='__main__':
	main()
