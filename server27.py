import binascii
import socket
import struct
import sys
import motion
import threading
import select
import msvcrt
import numpy as np

print(sys.version)

import socket
from naoqi import ALProxy
IP = "10.255.12.120"
PORT = 9559



AL_kTopCamera = 0
AL_kQVGA = 1            # 320x240
AL_kBGRColorSpace = 13
videoDevice = ALProxy('ALVideoDevice', IP, PORT)
captureDevice = videoDevice.subscribeCamera("test", 1, 3, AL_kBGRColorSpace, 10)
tts = ALProxy("ALTextToSpeech",IP,PORT)
postureProxy = ALProxy("ALRobotPosture", IP, PORT)
mp = ALProxy("ALMotion", IP, PORT)
aud = ALProxy("ALAudioDevice", IP, PORT)
led = ALProxy("ALLeds",IP,PORT)

def cameraGet():
	global captureDevice
	global videoDevice
	global image
	result = videoDevice.getImageRemote(captureDevice);
	if result == None:
		print 'cannot capture.'
		error("cannot capture.")
	elif result[6] == None:
		print 'no image data string.'
		error("no image data string.")
	else:
		values = map(ord, list(result[6]))
		packet=packet = {"id":6,"d":"|".join(str(x) for x in values)}
		return str(packet)

def motionSet(names,angles,speed):
	global mp
	names=names.split("|")
	angles=angles.split("|")
	angles = [int(x) for x in angles]
	angles = [ x * motion.TO_RAD for x in angles]
	mp.post.angleInterpolationWithSpeed(names, angles, speed)
def motionGet(names):
	global mp
	names=names.split("|")
	a=mp.getAngles(names,True)
	a = [ x * motion.TO_DEG for x in a]
	packet = {"id":2,"angles":"|".join(str(x) for x in a)}
	return str(packet)
def say(txt):
	global tts
	tts.post.say(txt)
def postureSet(pos,speed):
	postureProxy.post.goToPosture(pos,speed)
def postureGet():
	global postureProxy
	packet = {"id":1,"posture":str(postureProxy.getPostureFamily())}
	packet = str(packet)
	return packet
def volumeSet(vol):
	global aud
	aud.setOutputVolume(vol)
def volumeGet():
	global aud
	packet = {"id":3,"volume":str(aud.getOutputVolume())}
	return str(packet)

def motionStiffSet(names,stiff):
	global mp
	names=names.split("|")
	stiff=stiff.split("|")
	stiff = [float(x) for x in stiff]
	if len(stiff)==1:
		mp.setStiffnesses(names,stiff[0])
	else:
		mp.setStiffnesses(names,stiff)
def motionStiffGet(names):
	global mp
	names=names.split("|")
	a=mp.getStiffnesses(names)
	packet = {"id":4,"stiff":"|".join(str(x) for x in a)}
	return str(packet)

def ledGroupCreate(groupName,names):
	global led
	led.createGroup(groupName,names)
def ledOn(groupName):
	global led
	led.on(groupName)
def ledOff(groupName):
	global led
	led.off(groupName)
def ledFade(groupName,i,d):
	global led
	led.post.fade(groupName,i,d)
def ledFadeListRGB(name,rgb,time):
	global led
	rgb=rgb.split("|")
	time = [hex(x) for x in time]
	time=time.split("|")
	time = [float(x) for x in time]
	led.post.fadeListRGB(name,rgb,time)
def ledFadeRGB(name,rgb,d):
	global led
	led.post.fadeRGB(name,hex(rgb),float(d))
def ledGet(l):
	global led
	v=[]
	if l in led.listGroups():
		for a in led.listGroup(l):
			v.append(led.getIntensity(a))
	else:
		v.append(led.getIntensity(l))

	packet = {"id":5,"action":"get","led":"|".join(str(x) for x in v)}
	return str(packet)
def ledGroupGet():
	global led
	a=led.listGroups();
	packet = {"id":5,"action":"getGroups","groups":"|".join(str(x) for x in a)}
	return str(packet)
def ledReset(l):
	global led
	led.reset(l)

packetError=-1
def error(err):
	global packetError
	packetError = {"id":0,"error":err}

quit=False
def Main():
	global data
	global start
	global server_socket
	global read_list
	global quit
	global packetError

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
				data = s.recv(1024*4)
				if data:
					print data
					data=eval(data)
					_id=data["id"]

					try:
						if _id==0:#Say
							say(data["string"])
						if _id==1:#Posture
							if data["action"]=="set":
								postureSet(data["posture"],data["speed"])
							if data["action"]=="get":
								r=postureGet()
								s.send(r.encode())
						if _id==2:#Motion
							if data["action"]=="set":
								motionSet(data["names"],data["angles"],data["speed"])
							if data["action"]=="get":
								a=motionGet(data["names"])
								s.send(a.encode())
						if _id==3:#Volume
							if data["action"]=="set":
								volumeSet(int(data["volume"]))
							if data["action"]=="get":
								v=volumeGet()
								s.send(v.encode())
						if _id==4:#Stiffness
							if data["action"]=="set":
								motionStiffSet(data["names"],data["stiff"])
							if data["action"]=="get":
								stiff=motionStiffGet(data["names"])
								s.send(stiff.encode())
						if _id==5:#LEDs
							if data["action"]=="groupCreate":
								ledGroupCreate(data["groupName"],data["ledNames"])
							if data["action"]=="on":
								ledOn(data["groupName"])
							if data["action"]=="off":
								ledOff(data["groupName"])
							if data["action"]=="fade":
								ledFade(data["groupName"],data["i"],data["d"])
							if data["action"]=="fadelrgb":
								ledFadeListRGB(data["groupName"],data["colorlist"],data["d"])
							if data["action"]=="fadergb":
								ledFadeRGB(data["groupName"],data["color"],data["d"])
							if data["action"]=="get":
								l=ledGet(str(data["led"]))
								s.send(l.encode())
							if data["action"]=="getGroup":
								l=ledGroupGet()
								s.send(l.encode())
							if data["action"]=="reset":
								l=ledReset(data["led"])
						if _id==6:#Camera
							img=cameraGet()
							s.send(img.encode())


					except:
						print sys.exc_info()[0]
						print sys.exc_info()[1]
						error(str(sys.exc_info()[0]))


					if type(packetError) is dict:
						s.send(str(packetError).encode())
					else:
						packet = {"id":-1}
						packet = str(packet)
						s.send(packet.encode())

					s.close()
					read_list.remove(s)
				else:
					s.close()
					read_list.remove(s)





def Start():
	global server_socket
	global read_list
	host = "127.0.0.1"
	port=1337

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((host,port))
	server_socket.listen(5)
	
	read_list = [server_socket]

server_socket=-1
Start()

print "Ready"

while quit==False:
	Main()

videoDevice.unsubscribe(captureDevice)