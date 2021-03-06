#!/usr/bin/env python

import roslib; roslib.load_manifest('ardrone_project_new')
import rospy
import time
from PySide import QtCore, QtGui
from ros_drone import DroneController, MainController
import ros_drone
from ardrone_autonomy.msg import Navdata
import sys

PATH_TO_SOAR = "/home/saikishor/SoarSuite/bin"
sys.path.append(PATH_TO_SOAR)
import Python_sml_ClientInterface as sml

#path = PATH_TO_SOAR
#sys.path.append(path)

SOAR_GP_PATH = "/home/saikishor/SOAR/droo8/drone.soar"

out = "NULL"
z1=0
z2=0
c = 0
d = 0
e = 6

class SOARInterface(DroneController):
	def __init__(self):
		self.altd = -1
		self.status = -1
		self.rotZ = -1
		super(SOARInterface,self).__init__()
		self.subNavdata = rospy.Subscriber('/ardrone/navdata',Navdata,self.ReceiveNavdata) 

	def ReceiveNavdata(self,navdata):
		# Although there is a lot of data in this packet, we're only interested in the state at the moment	
		self.status = navdata.state
		self.altd = navdata.altd
		self.rotZ = navdata.rotZ
		#rospy.logwarn(self.status)

	def action(self, comm):
		command_name = comm
		global out
		global c
		if command_name == "takeoff":
			out = ctrl.Takeoff() #to take-off from land
			rospy.logwarn('takeoff')
			time.sleep(2)
			c = self.altd	
			#c = self.altd

		elif command_name == "land":
			out = ctrl.Land()  #to land from air
			rospy.logwarn('land')

		elif command_name == "forward": #to Person
			out = ctrl.Forward()
			#ctrl.Table()
			#rospy.logwarn('forward')

		elif command_name == "left":
			out = ctrl.Left()
			#rospy.logwarn('left')

		elif command_name == "right":
			out = ctrl.Right()
			#rospy.logwarn('right')

		elif command_name == "reverse":                    
			out = ctrl.Reverse()
			#rospy.logwarn('reverse')

		elif command_name == "up":
			z1 = (self.rotZ+180)
			#out = ctrl.Up()
			c = self.altd
			#rospy.logwarn('up')

		elif command_name == "down":          
			out = ctrl.Down()
			#rospy.logwarn('down')

		elif command_name == "achieved":
			goal_achieved = True
			out = "succeeded"
			rospy.logwarn('goal_achieved')

		elif command_name == "table":
			out = ctrl.Table()
			rospy.logwarn('found table under me')
			rospy.logwarn('shall i land on it or not. Enter 1 to land, 0 to not land')

		elif command_name == "notable":
			rospy.logwarn("there is no table found in my flight")
			rospy.logwarn('shall i land on it or not. Enter 1 to land, 0 to not land')

		elif command_name == "side":
			out = ctrl.Side()
			rospy.logwarn("rolling right is done")

		elif command_name == "dumm":
			DroneController().SetCommand(0, 0, 0, 0)
			out = "succeeded"

		elif command_name == "revzz":
			out = ctrl.Side()

		else:
			rospy.logwarn(command_name)
			command.AddStatusComplete()
		out = "succeeded"
		rospy.logwarn(out)

	def sendOK(self):
		return "succeeded"


def define_prohibitions(): #TODISCOVER WTF IS THIS
	pass

def create_kernel():
	kernel = sml.Kernel.CreateKernelInCurrentThread()
	if not kernel or kernel.HadError():
		print kernel.GetLastErrorDescription()
		exit(1)
	return kernel

def create_agent(kernel, name):
	agent = kernel.CreateAgent("agent")
	if not agent:
		print kernel.GetLastErrorDescription()
		exit(1)
	return agent

def agent_load_productions(agent, path):
	agent.LoadProductions(path)
	if agent.HadError():
		print agent.GetLastErrorDescription()
		exit(1)

if __name__ == '__main__':
	import sys
	rospy.init_node('connection', anonymous=True)
	rospy.logwarn('Connection node created and connection established')
	soar_interface = SOARInterface()
	stf = DroneController()
	ctrl = MainController()
	rospy.logwarn(SOAR_GP_PATH)

	print "******************************\n******************************\nNew goal\n******************************\n******************************\n"
	first_time = time.time()
	kernel = create_kernel()
	agent = create_agent(kernel, "agent")
	agent_load_productions(agent,SOAR_GP_PATH)
	agent.SpawnDebugger()

	# p_cmd = 'learn --on'
	# res = agent.ExecuteCommandLine(p_cmd)
	# res = kernel.ExecuteCommandLine(p_cmd, agent.GetAgentName)
	kernel.CheckForIncomingCommands()
	p_cmd = 'watch --learning 2'
	res = agent.ExecuteCommandLine(p_cmd)
	print str(res)	
	a=0
	b=0
	d=0
	c=0
	j=0
	r=1
	f=0
	l=0
	goal_achieved = False
	time.sleep(10)
	DroneController().SetCommand(0, 0, 0, 0)
	pInputLink = agent.GetInputLink()
	pID = agent.CreateIdWME(pInputLink, "drone")
	if(r==1):
		wme1 = agent.CreateIntWME(pID, "diff1", a)
	if(r==0):
		wme1 = agent.CreateIntWME(pID, "diff1", 1)
	while not goal_achieved:
		wme2 = agent.CreateIntWME(pID, "diff2", b)
		wme3 = agent.CreateIntWME(pID, "altd", c)
		wme3 = agent.CreateIntWME(pID, "decision", e) 
		rospy.logwarn("value of c is: %d", c)
		wme4 = agent.CreateIntWME(pID, "valtd", d)
		agent.Commit()  
		agent.RunSelfTilOutput()
		agent.Commands()
		numberCommands = agent.GetNumberCommands()
		print "Number of commands received by the agent: %s" % (numberCommands)
		rospy.logwarn("number of commands received: %d", numberCommands)
		i=0
		out="NULL"
		if numberCommands == 0:
			print 'KABOOOOOOOOOOOOOOOOOOM!!!!!!!!!!!!!!!'
			rospy.logwarn('didnot receive any command')
			l+=1
			if(l>5):
				ctrl.Land()
		else:
			while i<numberCommands:
				command = agent.GetCommand(i)
				command_name = command.GetCommandName()
				if(command_name == "forward"):
					j += 1
				if(command_name == "reverse"):
					f += 1
				print "The name of the command %d/%d is %s" % (i+1,numberCommands,command_name)
				rospy.logwarn(command_name)
				rospy.logwarn("%d, %d",j,f)
				rospy.logwarn("value of c,d is: %d, %d", c, d)
				rospy.logwarn("difference is: %d", (c-d))
				rospy.logwarn("the diff in soar is: %d, %d", a, b)
				#c = soar_interface.altd
				c = max(c, d)
				#c = d
				if command_name == "up":
					z1 = (soar_interface.rotZ + 180)
				soar_interface.action(command_name)
				if command_name == "p":
					z2 = (soar_interface.rotZ + 180)
					rospy.logwarn("z val : %f, %f, %f", z1, z2, z1-z2)
					if((z1-z2)<-2  or (z1-z2)>2):
						if((z1-z2)<-2):
							while ((z1-z2)<-2):
								DroneController().SetCommand(0, 0, -0.1, 0)
								z2 = (soar_interface.rotZ + 180)
								rospy.logwarn(z1-z2)
						elif((z1-z2)>2):
							while ((z1-z2)>2):
								DroneController().SetCommand(0, 0, 0.1, 0)
								z2 = (soar_interface.rotZ + 180)
								rospy.logwarn(z1-z2)
					DroneController().SetCommand(0, 0, 0, 0)
					rospy.logwarn("aligned")

				if command_name == "table":
					e = raw_input()
					e = int(e)
				if command_name == "notable":
					e=1
					#e = raw_input()
					#e = int(e)
				if command_name == "takeoff":
					#wme3 = agent.CreateIntWME(pID, "altd", c)
					rospy.logwarn(c)
					c=soar_interface.altd
					#d = soar_interface.altd
					rospy.logwarn(d)
					#goal_achieved = True
					#rospy.logwarn('goal achieved!!! congrats')
				if command_name == "forard":
					z2 = (soar_interface.rotZ + 180)
					rospy.logwarn("z val : %f, %f, %f", z1, z2, z1-z2)
					if((z1-z2)<-2  or (z1-z2)>2):
						if((z1-z2)<-2):
							while ((z1-z2)<-2):
								DroneController().SetCommand(0, 0, -0.1, 0)
								z2 = (soar_interface.rotZ + 180)
								rospy.logwarn(z1-z2)
						elif((z1-z2)>2):
							while ((z1-z2)>2):
								DroneController().SetCommand(0, 0, 0.1, 0)
								z2 = (soar_interface.rotZ + 180)
								rospy.logwarn(z1-z2)
					DroneController().SetCommand(0, 0, 0, 0)
					rospy.logwarn("aligned")

				if command_name == "reerse":
					z2 = (soar_interface.rotZ + 180)
					rospy.logwarn("z val : %f, %f, %f", z1, z2, z1-z2)
					if((z1-z2)<-2  or (z1-z2)>2):
						if((z1-z2)<-2):
							while ((z1-z2)<-2):
								DroneController().SetCommand(0, 0, -0.1, 0)
								z2 = (soar_interface.rotZ + 180)
								rospy.logwarn(z1-z2)
						elif((z1-z2)>2):
							while ((z1-z2)>2):
								DroneController().SetCommand(0, 0, 0.1, 0)
								z2 = (soar_interface.rotZ + 180)
								rospy.logwarn(z1-z2)
					DroneController().SetCommand(0, 0, 0, 0)
					rospy.logwarn("aligned")

				if command_name == "achieved":
					goal_achieved = True
					rospy.logwarn('goal achieved')
				i+=1
				rospy.logwarn(c)	
				d = soar_interface.altd
				fn = open('/home/saikishor/catkin_ws/src/marker.txt', 'r')
				time.sleep(0.5)
				b = fn.read()
				b = int(b)
				rospy.logwarn("the value from the marker file: %d", b)
				g = b
				#if(g<0):
					#a=0
					#b=0
					#agent.DestroyWME(wme1)
					#agent.Update(wme1, 0)
					#agent.Commit()
					#agent.RunSelf(1)
				if((g==1) and r==1):
					agent.DestroyWME(wme1)
					agent.Update(wme2, 1)
					agent.Commit()
					#agent.RunSelf(1)
					b=1
					a=1
					r=0
					DroneController().SetCommand(0, 0, 0, 0)
				time.sleep(1)
				rospy.logwarn(out)
				print "SM return: %s \n\n" % (out) 
				if out=="succeeded": 
					command.AddStatusComplete()
					rospy.logwarn("AddStatusComplete sent")
				elif out=="aborted":
					command.AddStatusError()
				else:
					print "gpsrSoar interface: unknown ERROR"
					exit(1)
	command.AddStatusComplete()

	kernel.DestroyAgent(agent)
	kernel.Shutdown()
	#del kernelCommit

	rospy.signal_shutdown('Great Flying!')


