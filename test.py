import client


client.say("test!")

pos=client.posture_get()
print(pos)
if pos=="Sitting":
	pos="Stand"
else:
	pos="Sit"
#client.posture_set(pos)


names= ["LShoulderRoll","LShoulderPitch","LElbowYaw","LElbowRoll","LHand"]
for i in range(0,2):
	angles = [90,0,-90,-85,90]
	client.motion_set(names,angles)
	angles = [90,0,-90,-55,90]
	client.motion_set(names,angles)
angles = [90,0,-90,-85,90]
client.motion_set(names,angles)