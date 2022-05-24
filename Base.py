#!/usr/bin/python3
import sys
import telnetlib
import time
import os

class Base:
	def connectCisco(self, ip, port, host, number=0):
		con = telnetlib.Telnet(ip, port)
		out = con.read_until("Entering server port", 60)
		if out.find("Entering server port") == -1:
			print ("Don't connected to Console Server on port "+str(port))
			return 1
		time.sleep(5)
		return con

	def skipInstall(self, con):
		self.sendCommand(con, "no\r\r")
		#self.sendCommand(con, "\x1A\x1A\r\r")
		time.sleep(30)

	def loginner(self, con):
		out = self.sendCommand(con, "", 2)
		if out.find("Username") != -1:
			self.sendCommand(con, self.login)
			time.sleep(1)
			out = self.sendCommand(con, self.password)
		if out.find("Password") != -1:
			out = self.sendCommand(con, self.password)
		if (out.find("Username") != -1) or (out.find("Password") != -1):
			return 1

	def downloadFirmware(self, con, hostname, number, *fileName):
		self.sendCommand(con, "conf t\r")
		self.sendCommand(con, "int f0/1\rno sh\rswitchport access vlan 1\rswitchport mode access\rip add 192.168.3."+str(110+number)+" 255.255.255.0")
		self.sendCommand(con, "int f0/0/1\rno sh\rswitchport access vlan 1\rswitchport mode access\rip add 192.168.3."+str(110+number)+" 255.255.255.0")
		self.sendCommand(con, "int g0/1\rno sh\rswitchport access vlan 1\rswitchport mode access\rip add 192.168.3."+str(110+number)+" 255.255.255.0")
		self.sendCommand(con, "int g0/0/1\rno sh\rswitchport access vlan 1\rswitchport mode access\rip add 192.168.3."+str(110+number)+" 255.255.255.0")
		self.sendCommand(con, "int g1/0/1\rno sh\rswitchport access vlan 1\rswitchport mode access\rip add 192.168.3."+str(110+number)+" 255.255.255.0")
		self.sendCommand(con, "int vlan 1\rno sh\rip add 192.168.3."+str(110+number)+" 255.255.255.0\rnameif dhcp")
		self.sendCommand(con, "int e0/1\r no sh\rswitchport access vlan 1\rswitchport mode access")
		self.sendCommand(con, "end\r")
		time.sleep(10)
		for name in fileName:
			while self.checkFiles(con, hostname, name) == 1:
				self.sendCommandSecure(con, hostname, "copy tftp://192.168.3.100/"+name+" "+name+"\r\r", 10) #NEED TO EDIT
				time.sleep(10)
		self.sendCommand(con, "conf t\r")
		self.sendCommand(con, "int f0/1\rno sh\rswitchport access vlan 1\rno switchport mode access\rno ip add 192.168.3."+str(110+number)+" 255.255.255.0")
		self.sendCommand(con, "int f0/0/1\rno sh\rswitchport access vlan 1\rno switchport mode access\rno ip add 192.168.3."+str(110+number)+" 255.255.255.0")
		self.sendCommand(con, "int g0/1\rno sh\rswitchport access vlan 1\rno switchport mode access\rno ip add 192.168.3."+str(110+number)+" 255.255.255.0")
		self.sendCommand(con, "int g0/0/1\rno sh\rswitchport access vlan 1\rno switchport mode access\rnoip add 192.168.3."+str(110+number)+" 255.255.255.0")
		self.sendCommand(con, "int g1/0/1\rno sh\rswitchport access vlan 1\rno switchport mode access\rno ip add 192.168.3."+str(110+number)+" 255.255.255.0")
		self.sendCommand(con, "int vlan 1\rno sh\rno ip add 192.168.3."+str(110+number)+" 255.255.255.0\rno nameif dhcp")
		self.sendCommand(con, "int e0/1\r no sh\rswitchport access vlan 1\rno switchport mode access")
		self.sendCommand(con, "end\r")
		return 0

	def writeInFile(self, con, openedFile, host, hostname, command):
		openedFile.write("===================================================================\n")
		openedFile.write("@Entered command on "+host+": "+command+"\n")
		openedFile.write("Output:\n")
		openedFile.write(self.sendCommandSecure(con, hostname, command))

	def checkFiles(self, con, hostname, fileName):
		out = self.sendCommandSecure(con, hostname, "dir", 1)
		if out.find(fileName) == -1:
			return 1
		return 0

	def delOtherFiles(self, con, hostname, *fileName):
		out = self.sendCommand(con, "del /recursive *")
		while out.find(hostname, len(out)-30) == -1:
			for name in fileName:
				if out.find(name) != -1:
					con.write("n")
					out = out + con.read_until("@$%#!",0.5)
			out = out + self.sendCommand(con)
		return out

	def enterEnable(self, con):
		
		self.sendCommand(con, "\r", 2)
		out = self.sendCommand(con, "enable")
		if out.find("Password") != -1:
			time.sleep(0.5)
			out = self.sendCommand(con, self.enablePass+"\r\r")
		if out.find("#") == -1:
			return 1

	def getHostname(self, con):
		try:
			out = con.read_until("@$%#!",0.1)
			con.write("\r")
			out = con.read_until("#",1)
			out = out.strip().strip('#')
			return out
		except:
			return ""

	def sendCommand(self, con, command="", timeToRead=0.5):
		try:
			out = con.read_until("@$%#!",0.1)
			con.write(command+"\r")
			out = con.read_until("@$%#!",timeToRead)
			return out
		except:
			return ""

	def sendCommandSecure(self, con, hostname, command, timeToRead=0.2):
		try:
			con.write(command+"\r")
			out = con.read_until("!@#$%",2)
			while out.find(hostname, len(out)-30) == -1:
				con.write("\r")
				out = out + con.read_until("!@#$%", timeToRead)
			return out.strip("# \r\n").replace(hostname, "").replace(hostname+"#", "").replace(hostname+"#\r", "").replace("", "").replace(" --More--         ", "").replace("<--- More --->\r              \r", "").strip("# \r\n").replace(command, "ENTERED COMMAND: "+command)+"\r"
		except:
			return ""

	def __init__(self, login, password, enablePass):
		self.login = login
		self.password = password
		self.enablePass = enablePass
