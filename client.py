import socket
import sys
print(sys.version)

def say(txt):
	packet= {"id":0,"string": txt}
	Main(packet)
def posture_get():
	packet = {"id":1,"action":"get"}
	return Main(packet)
def posture_set(pos,speed=1):
	packet = {"id":1,"action":"set","posture":pos,"speed":speed}
	Main(packet)

def motion_set(names,angles,speed=0.3):
	packet = {"id":2,"names":"|".join(str(x) for x in names),"angles":"|".join(str(x) for x in angles),"speed":speed}
	Main(packet)


def Main(packet):
	host = "127.0.0.1"
	port = 1337
	s = socket.socket()
	s.connect((host,port))
	s.send(str(packet).encode())

	data={"id":0}
	while data["id"]>=0:
		data = s.recv(1024)
		data = eval(data)

		_id=data["id"]

		if _id==1:
			return data["posture"]


	s.close()
		

#Main(packet)


#Old packets
'''
#packet = {"id":0,"string":"Hello. My name is Bob"}
#packet = {"id":1,"action":"get"}

packet = {"id":1,"action":"set","posture":"Sit","speed":1.0}
#s.send(str(packet).encode())

packet = {"id":0,"string":"Hello. My name is Bob"}
#s.send(str(packet).encode())

Arm1=[90,0,-90,-85,90]
JointName=["LShoulderRoll","LShoulderPitch","LElbowYaw","LElbowRoll","LHand"]
packet = {"id":2,"names":"|".join(str(x) for x in JointName),"angles":"|".join(str(x) for x in Arm1),"speed":0.2}
s.send(str(packet).encode())
'''
