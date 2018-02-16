import binascii
import socket
import struct
import sys
import motion

print(sys.version)

import socket
from naoqi import ALProxy
IP = "127.0.0.1"
PORT = 60577

AL_kTopCamera = 0
AL_kQVGA = 1            # 320x240
AL_kBGRColorSpace = 13
videoDevice = ALProxy('ALVideoDevice', IP, PORT)
captureDevice = videoDevice.subscribeCamera("test", 1, 3, AL_kBGRColorSpace, 10)
tts = ALProxy("ALTextToSpeech",IP,PORT)
postureProxy = ALProxy("ALRobotPosture", IP, PORT)
mp = ALProxy("ALMotion", IP, PORT)


def motionSet(names,angles,speed):
	global mp
	names=names.split("|")
	angles=angles.split("|")
	angles = [int(x) for x in angles]
	angles = [ x * motion.TO_RAD for x in angles]
	mp.post.angleInterpolationWithSpeed(names, angles, speed)
def say(txt):
	global tts
	print "SAY: "+txt
	tts.post.say(txt)
def postureSet(pos,speed):
	postureProxy.post.goToPosture(pos,speed)
def postureGet():
	global postureProxy
	packet = {"id":1,"posture":str(postureProxy.getPostureFamily())}
	packet = str(packet)
	return packet


def Main():
	global data
	global start
	global s

	c, addr = s.accept()
	print "Connection from: " + str(addr)
	while True:
		data = c.recv(1024)
		if not data:
			print "Connection lost"
			break;

		print data
		data=eval(data)
		_id=data["id"]
		if _id==0:#Say
			say(data["string"])
		if _id==1:#Posture
			if data["action"]=="set":
				postureSet(data["posture"],data["speed"])
			if data["action"]=="get":
				r=postureGet()
				c.send(r.encode())
		if _id==2:#Motion
			motionSet(data["names"],data["angles"],data["speed"])

		

		packet = {"id":-1}
		packet = str(packet)
		c.send(packet.encode())
		break;


	c.close()

def Start():
	global s
	host = "127.0.0.1"
	port=1337

	s=socket.socket()
	s.bind((host,port))

	s.listen(1)


s=-1
Start()

while True:
	Main()

videoDevice.unsubscribe(captureDevice)