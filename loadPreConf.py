#!/usr/bin/python3
import Base
import sys
import telnetlib
import time
import os
import configFile
from threading import Thread

countOfConnections = configFile.countOfConnections
executions = configFile.executions
machinesInStand = configFile.machinesInStand
hosts =	configFile.hosts
login = configFile.login
password = configFile.password
enablePass = configFile.enablePass

base = Base.Base(login, password, enablePass)

def loadPreConf(ip, port, host):
	global executions
	try:
		con = base.connectCisco(ip, port, host)
	except:
		print "Unexpected error on "+host+" with ip "+str(ip)+":"+str(port)+"!"
		executions = executions-1
		return 1
	base.skipInstall(con)
	if base.enterEnable(con) == 1:
		print "Password on enable on "+host+" with ip "+str(ip)+":"+str(port)+"!"
		con.close()
		executions = executions-1
		return 1
	if os.path.isfile("preConf/"+host+".cfg"):
		commands = open("preConf/"+host+".cfg", "r")
		try:
			for cmd in commands:
				base.sendCommand(con, cmd)
		finally:
			commands.close()
	else:
		print host, " doesn't exist"
		executions = executions - 1
		con.close()
		return 1
	base.sendCommand(con, "wr\r\r")
	con.close()
	print("PreConf loaded on "+host+" on port "+str(port))
	executions = executions - 1







class MyThread(Thread):
    def __init__(self, ip, port, host):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.host = host

    def run(self):
        loadPreConf(self.ip, self.port, self.host)
    
def create_threads():
	global executions
	for host in range((int(sys.argv[1])-1)*machinesInStand, int(sys.argv[1])*machinesInStand):
		my_thread = MyThread(hosts[host][1], hosts[host][2], hosts[host][0])
		my_thread.start()
		executions = executions + 1
		while executions >= countOfConnections:
			time.sleep(10)
 
 
if __name__ == "__main__":
    create_threads()
