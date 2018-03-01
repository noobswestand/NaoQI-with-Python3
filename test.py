import client
import time
import random
import numpy as np
import cv2






#client.say("aaaa")
while True:
	image=client.camera_get()
	cv2.imshow("aa",image)
	if cv2.waitKey(33) == 27:
		cv2.destroyAllWindows()
		break







'''
pos=client.posture_get()
print(pos)
if pos=="Sitting":
	pos="Stand"
else:
	pos="Sit"
'''

#client.say("hi")

'''
names=[]
for i in range(8):
	names.append("Face/Led/Red/Left/"+str(i*45)+"Deg/Actuator/Value")
	names.append("Face/Led/Red/Right/"+str(i*45)+"Deg/Actuator/Value")
	names.append("Face/Led/Green/Left/"+str(i*45)+"Deg/Actuator/Value")
	names.append("Face/Led/Green/Right/"+str(i*45)+"Deg/Actuator/Value")
	names.append("Face/Led/Blue/Left/"+str(i*45)+"Deg/Actuator/Value")
	names.append("Face/Led/Blue/Right/"+str(i*45)+"Deg/Actuator/Value")
client.led_group_create("test",names)

client.led_off("test")

time.sleep(1)
print(client.led_get("test"))
#print(client.led_group_get())

'''


#client.posture_set(pos)
#print(client.volume_get())

#names= ["LShoulderRoll","LShoulderPitch","LElbowYaw","LElbowRoll"]
#client.motion_stiff_set(names,[0,1,0.5,0.25])
#print(client.motion_stiff_get(names))
'''
names= ["LShoulderRoll","LShoulderPitch","LElbowYaw","LElbowRoll","LHand"]
a=client.motion_get(["LShoulderRoll","LShoulderPitch","LElbowYaw","LElbowRoll"])
print(a)
for i in range(0,2):
	angles = [90,0,-90,-85,90]
	client.motion_set(names,angles)
	angles = [90,0,-90,-55,90]
	client.motion_set(names,angles)
angles = [90,0,-90,-85,90]
client.motion_set(names,angles)
'''