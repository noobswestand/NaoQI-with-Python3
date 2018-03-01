import socket
import sys
import numpy as np
import zlib
import base64 as b64
import json
print(sys.version)


def pak(data,s):
	data = eval(data)
	#print(data)
	_id=data["id"]

	if _id==-1:
		#end=True
		print("ended")

	if _id==0:#Error
		print(data["error"])
		return -1

	if _id==1:
		return data["posture"]
	if _id==2:#Motion
		angles=data["angles"].split("|")
		angles = [int(round(float(x))) for x in angles]
		return angles
	if _id==3:#Volume
		vol=data["volume"]
		return int(vol)
	if _id==4:#Stiff
		stiff=data["stiff"].split("|")
		stiff = [float(x) for x in stiff]
		return stiff
	if _id==5:#LED
		if data["action"]=="get":
			i=data["led"].split("|")
			return [int(round(float(x))) for x in i]
		if data["action"]=="getGroups":
			return data["groups"].split("|")
	if _id==6:#Camera
		if data["a"]=="d":
			st=data["d"]
			#st = st + "=" * (-len(st) % 4)
			#st=b64.b64decode(st)
			#st=zlib.decompress(st)
			r=json.loads(st)
			if data["r"]==3:
				width = 1280
				height = 720
			if data["r"]==2:
				width = 640
				height = 480
			if data["r"]==1:
				width = 320
				height = 240
			if data["r"]==7:
				width = 80
				height = 60

			image = np.zeros((height, width, 3), np.uint8)
			i = 0
			for y in range(0, height):
				for x in range(0, width):
					image.itemset((y, x, 0), r[i + 0])
					image.itemset((y, x, 1), r[i + 1])
					image.itemset((y, x, 2), r[i + 2])
					i += 3
			return image
	return None
			


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
	packet = {"id":2,"action":"set","names":"|".join(str(x) for x in names),"angles":"|".join(str(x) for x in angles),"speed":speed}
	Main(packet)
def motion_get(names):
	packet = {"id":2,"action":"get","names":"|".join(str(x) for x in names)}
	return Main(packet)

def motion_stiff_get(names):
	packet = {"id":4,"action":"get","names":"|".join(str(x) for x in names)}
	return Main(packet)
def motion_stiff_set(names,stiff):
	if type(stiff) is list:
		packet = {"id":4,"action":"set","names":"|".join(str(x) for x in names),"stiff":"|".join(str(x) for x in stiff)}
	else:
		packet = {"id":4,"action":"set","names":"|".join(str(x) for x in names),"stiff":str(stiff)}
	Main(packet)

def volume_get():
	packet = {"id":3,"action":"get"}
	return Main(packet)
def volume_set(vol):
	packet = {"id":3,"action":"set","volume":vol}
	Main(packet)

def led_group_create(groupName,names):
	packet = {"id":5,"action":"groupCreate","groupName":groupName,"ledNames":names}
	Main(packet)
def led_on(groupName):
	packet = {"id":5,"action":"on","groupName":groupName}
	Main(packet)
def led_off(groupName):
	packet = {"id":5,"action":"off","groupName":groupName}
	Main(packet)
def led_fade(groupName,i,d):
	packet = {"id":5,"action":"fade","groupName":groupName,"i":i,"d":d}
	Main(packet)
def led_fade_rgb(groupName,colorList,d):
	packet = {"id":5,"action":"fadelrgb","groupName":groupName,"colorlist":colorList,"d":d}
	Main(packet)
def led_fade_rgb(groupName,color,d):
	packet = {"id":5,"action":"fadergb","groupName":groupName,"color":color,"d":d}
	Main(packet)
def led_get(led):
	packet = {"id":5,"action":"get","led":led}
	return Main(packet)
def led_group_get():
	packet = {"id":5,"action":"getGroup"}
	return Main(packet)
def led_reset(g):
	packet = {"id":5,"action":"get","led":g}
	return Main(packet)


def camera_get():
	packet = {"id":6,"action":"get"}
	return Main(packet)

def Main(packet):
	host = "127.0.0.1"
	port = 1337
	s = socket.socket()
	s.connect((host,port))
	s.send(str(packet).encode())

	l=[]

	pdata=""
	end=False
	pack=False
	while end==False:
		d = s.recv(1024*1000)
		d=d.decode()
		pdata=pdata+d

		while("{END}" in str(pdata)):
			data=pdata.split("{END}",1)
			pdata=str(data[1])
			data=data[0]
			r=pak(data,s)
			return r;

	s.close()
	
