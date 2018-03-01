import socket
import select
import msvcrt
host = "127.0.0.1"
port=1337

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host,port))
server_socket.listen(5)
read_list = [server_socket]


def sendData(s):
	st=""
	for i in range(50000):
		st+=str(i)
	s.send(st+"{END}")
	s.send("hi{END}")
	s.send("hi{END}")
	s.send("STOP PLZ{END}")



quit=False
while quit==False:
	if msvcrt.kbhit():
		key = msvcrt.getch()
		if str(key)=="q":
			print "Stopping..."
			quit=True

	readable, writable, errored = select.select(read_list, [], [],1)
	for s in readable:
		if s is server_socket:
			client_socket, address = server_socket.accept()
			read_list.append(client_socket)
			print "Connection from", address
		else:
			data = s.recv(1024*2)
			if data:
				print data
				sendData(s)
