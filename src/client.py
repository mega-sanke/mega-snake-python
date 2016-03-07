import socket
import time

s = socket.socket()

s.connect(('127.0.0.1', 8820))


s.send("test,23,4")

time.sleep(0.1)

s.send('barak,1,1')


while True:
	pass
