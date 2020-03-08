#!/usr/bin/env python

import RPi.GPIO as GPIO # necessary to read data from rpi pins
import time # for time function both for evaluation and sleep fuctions
import socket # library to handle tcp connection in py3

# sets up socket info for the control unit
host = "192.168.1.112"
port = 10000
# create socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# pir_sensor 16 is the rpi pin which the movement sensor is connected to - CHANGE THIS TO THE CORRECT PIN
pir_sensor = 16
# Setup the RPI pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pir_sensor, GPIO.IN)

# initialize the variable current_state to 0 - is used later so we can keep trackof the last state so we dont send uneccsary data (several on or off signals in a row)
current_state = 0
print("Started motion detector") # message for troubleshooting / indicating its actually on
try:
	last_state=0 # keeps track of last_state - initialize to 0
	isConnected=0 # indicates if we are connected or not - 0 means no connection
	while isConnected!=1: # this loop will try to connect untill it has a connection established
		try:
			s.connect((host, port))
			isConnected=1
		except: #if a connection couldnt be established print error message and try again in 5 seconds
			print("Error connecting to host: " + host + str(port))
			time.sleep(5)
			pass

#	f=open("results.txt","w+") # was used for the evaluation
#	count=0
	while True:
		current_state = GPIO.input(pir_sensor) # reads the value from the motion sensor and sets current_state to its value
		data=str(GPIO.input(pir_sensor)).encode() # stores the value from the movement sensor in data variable and encodes it to be able to send it over tcp

		# If last message to actuator detected movement dont send another message indication movement was detected
		if current_state == 1 and last_state != 1: # if current state is 1 (movemnt detected) and last state was not 1 send the state to the control unit
			s.sendall(data) #send data to control unit
#			print(str(time.time())+" "+str(count)) # wasused for troubleshooting
#			f.write(str(time.time())+"\n") # was used for evaluation
#			count+=1
		elif current_state == 0 and last_state != 0: # if current state is 0 (no movement) and last state was not 0
			data=str(0).encode() # send a 0 (have to ecnode to send over tcp)
			s.sendall(data) # send the data to the control unit
#			print("OFF " + str(time.time())+" "+str(count))
#			f.write(str(time.time())+"\n")
#			count+=1
		else:
			continue
		last_state=current_state # set last_state to current_state at the end of each loop
#	f.close() # close file
	s.close() # close sockt
except KeyboardInterrupt:
	pass
finally:
	GPIO.cleanup()
