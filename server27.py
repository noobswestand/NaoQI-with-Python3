import socket
import sys
import motion
import select
import msvcrt
import numpy as np
import time
import zlib
import base64 as b64
import json
import threading

import cv2

print(sys.version)

import socket
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
IP = "10.255.19.209"#"10.255.14.124"#"127.0.0.1"
PORT = 9559#59592#9559



AL_kTopCamera = 0
AL_kQVGA = 1            # 320x240
AL_kBGRColorSpace = 13
videoDevice = ALProxy('ALVideoDevice', IP, PORT)
videoResolution=2
captureDevice = videoDevice.subscribeCamera("test", AL_kTopCamera, videoResolution, AL_kBGRColorSpace, 10)
tts = ALProxy("ALAnimatedSpeech",IP,PORT)
postureProxy = ALProxy("ALRobotPosture", IP, PORT)
mp = ALProxy("ALMotion", IP, PORT)
if PORT==9559:
	aud = ALProxy("ALAudioDevice", IP, PORT)
led = ALProxy("ALLeds",IP,PORT)
mem = ALProxy("ALMemory",IP,PORT)
tou = ALProxy("ALTouch", IP,PORT)


videoResolutionWidth=0
videoResolutionHeight=0
if videoResolution==3:
	videoResolutionWidth = 1280
	videoResolutionHeight = 960
if videoResolution==2:
	videoResolutionWidth = 640
	videoResolutionHeight = 480
if videoResolution==1:
	videoResolutionWidth = 320
	videoResolutionHeight = 240
if videoResolution==7:
	videoResolutionWidth = 80
	videoResolutionHeight = 60



class cameraGetConv(threading.Thread):
	def __init__(self):
		super(cameraGetConv, self).__init__()
		self.done=True
		self.values=[]
		self.result=""
		self.step=-1
		self.running=True
		self.pid=-1
	def run(self):
		global videoResolution
		global videoResolutionHeight
		global videoResolutionWidth
		while self.running:
			if self.done==False:
				st=str({"id":6,"a":"d","r":videoResolution,"d":self.values})
				st+="{END}"
				self.result=st.encode()
				self.done=True
				global image
				image.update(self.pid)
			

class cameraGetConst(threading.Thread):
	def __init__(self):
		super(cameraGetConst, self).__init__()
		self.running=True
		self.workerLimit=4
		self.worker = [None] * self.workerLimit
		self.step=0
		for i in range(self.workerLimit):
			self.worker[i]=cameraGetConv()
			self.worker[i].pid=i;
			self.worker[i].start()
	def run(self):
		while self.running:
			#start_time = time.time()
			result = videoDevice.getImageRemote(captureDevice)
			#print("--- %s seconds ---" % (time.time() - start_time))
			
			if result == None:
				print 'cannot capture.'
				error("cannot capture.")
			elif result[6] == None:
				print 'no image data string.'
				error("no image data string.")
			else:
				self.step+=1
				did=False
				for i in range(self.workerLimit):
					if self.worker[i].done==True:
						self.worker[i].values=str(result[6])
						self.worker[i].step=self.step
						self.worker[i].done=False
						did=True
						break;
				if did==False:
					print "Could not find worker!"
	def stop(self):
		for i in range(self.workerLimit):
			self.worker[i].running=False
		self.running=False
class cameraGetValue():
	def __init__(self):
		self.running=True
		self.pck=""
		self.step=0
		self.camera=-1
	def stop(self):
		self.running=False
	def update(self,i):
		if self.camera.worker[i].done==True and self.camera.worker[i].step>self.step:
				self.step=camera.worker[i].step
				self.pck=camera.worker[i].result


camera = cameraGetConst()
image = cameraGetValue()
image.camera=camera
camera.start()
def cameraGet(s):
	global image
	s.send(image.pck)


class touchGet(threading.Thread):
	def __init__(self):
		super(touchGet, self).__init__()
		self.running=True
		self.packet="";
	def run(self):
		while self.running==True:
			global tou
			status = tou.getStatus()
			self.packet = {"id":7,"status":status}
	def stop(self):
		self.running=False

touch=touchGet()
touchRunning=False
#touch.start()

def touchGet():
	global touch
	return str(touch.packet)

def cameraGet_OLD(s):
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
		st=json.dumps(values)
		st=zlib.compress(st,zlib.Z_BEST_COMPRESSION)
		st=b64.b64encode(st)
		st = st.rstrip("=")
		send2(str({"id":6,"a":"d","d":st}),s)
		print "sent image"

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
def say(txt,conf):
	global tts
	tts.post.say(txt,conf)
	print conf
def postureSet(pos,speed):
	postureProxy.post.goToPosture(pos,speed)
def postureGet():
	global postureProxy
	packet = {"id":1,"posture":str(postureProxy.getPostureFamily())}
	packet = str(packet)
	return packet
def volumeSet(vol):
	global PORT
	if PORT==9559:
		global aud
		aud.setOutputVolume(vol)
	else:
		print "Cannot use audio functions on virutal robot!"
def volumeGet():
	global PORT
	if PORT==9559:
		global aud
		packet = {"id":3,"volume":str(aud.getOutputVolume())}
		return str(packet)
	else:
		print "Cannot use audio functions on virutal robot!"

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
	led.post.on(groupName)
def ledOff(groupName):
	global led
	led.post.off(groupName)
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
def ledEar(degree,duration,leave):
	global led
	led.earLedsSetAngle(degree,duration,leave)

packetError=-1
def error(err):
	global packetError
	packetError = {"id":0,"error":err}
def send2(st,s):
	st=str(st)
	st+="{END}"
	s.sendall(st.encode())
	#s.send("{'id':-99,'m':'hi there'}{END}".encode())

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

		readable, writable, errored = select.select(read_list, [], [], 0.5)
		for s in readable:
			if s is server_socket:
				client_socket, address = server_socket.accept()
				read_list.append(client_socket)
				#print "Connection from", address
			else:
				data = s.recv(1024*50)
				if data:
					print data
					data=eval(data)
					_id=data["id"]

					try:
						if _id==0:#Say
							say(data["string"],eval(data["conf"]))
						if _id==1:#Posture
							if data["action"]=="set":
								postureSet(data["posture"],data["speed"])
							if data["action"]=="get":
								r=postureGet()
								send2(r,s)
						if _id==2:#Motion
							if data["action"]=="set":
								motionSet(data["names"],data["angles"],data["speed"])
							if data["action"]=="get":
								a=motionGet(data["names"])
								send2(a,s)
						if _id==3:#Volume
							if data["action"]=="set":
								volumeSet(int(data["volume"]))
							if data["action"]=="get":
								v=volumeGet()
								send2(v,s)
						if _id==4:#Stiffness
							if data["action"]=="set":
								motionStiffSet(data["names"],data["stiff"])
							if data["action"]=="get":
								stiff=motionStiffGet(data["names"])
								send2(stiff,s)
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
								send2(l,s)
							if data["action"]=="getGroup":
								l=ledGroupGet()
								send(l,s)
							if data["action"]=="reset":
								l=ledReset(data["led"])
							if data["action"]=="ear":
								l=ledEar(int(data["degree"]),float(data["duration"]),bool(data["leave"]))
						if _id==6:#Camera
							img=cameraGet(s)
						if _id==7:#Touch
							touch=touchGet()
							send2(touch,s)


					except:
						print sys.exc_info()[0]
						print sys.exc_info()[1]
						error(str(sys.exc_info()[0]))


					if type(packetError) is dict:
						send2(str(packetError),s)
					else:
						packet = {"id":-1}
						packet = str(packet)
						send2(packet,s)

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
camera.stop()
image.stop()
touch.stop()