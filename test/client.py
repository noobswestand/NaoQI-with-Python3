import socket


host = "127.0.0.1"
port = 1337
s = socket.socket()
s.connect((host,port))
s.send(str("gimme data").encode())

end=False
pdata=""

def pak(data):
	print(data)
	if data=="STOP PLZ":
		print("stopped")

while end==False:
	d = s.recv(1024*2)
	d=d.decode()
	pdata=pdata+d

	while("{END}" in str(pdata)):
		data=pdata.split("{END}",1)
		pdata=str(data[1])
		data=data[0]
		pak(data)