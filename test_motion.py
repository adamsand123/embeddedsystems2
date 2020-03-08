#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import socket
import sys
import json

host = "192.168.1.112"
port = 10000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((host, port))

pir_sensor = 16
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pir_sensor, GPIO.IN)

current_state = 0
print("Started motion detector")
try:
	last_state=0
	isConnected=0
	while isConnected!=1:
		try:
			s.connect((host, port))
			isConnected=1
		except:
			print("Error connecting to host: " + host + str(port))
			time.sleep(5)
			pass

	f=open("results.txt","w+")
	count=0
	while True:
		current_state = GPIO.input(pir_sensor)
		data=str(GPIO.input(pir_sensor)).encode()

		# If last message to actuator detected movement dont send another message indication movement was detected
		if current_state == 1 and last_state != 1:
			s.sendall(data)
			print(str(time.time())+" "+str(count))
			f.write(str(time.time())+"\n")
			count+=1
		elif current_state == 0 and last_state != 0:
			data=str(0).encode()
			s.sendall(data)
			print("OFF " + str(time.time())+" "+str(count))
			f.write(str(time.time())+"\n")
			count+=1
		else:
			continue
#		time.sleep(1)
		last_state=current_state
	f.close()
	s.close()
except KeyboardInterrupt:
	pass
finally:
	GPIO.cleanup()
