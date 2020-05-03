#
# Classes for the FAH Remote application
#
from telnetlib import Telnet
import json
import logging
	
# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# create console handler and set level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class FAH_Client:
	timeOut = 1
	def __init__(self, name, ip_address, port):
		self.name = name
		self.ip_address = ip_address
		self.port = port
		self.user = ""
		self.team = ""
		self.power = ""
		self.status = "Offline"
		self.tn = None
				
	def connect(self):
		# open the telnet connection
		if self.tn == None:
			try:
				self.tn = Telnet(self.ip_address, self.port, self.timeOut)
				self.status = "Online"
				msg = "Connected to the telnet server " + str(self.ip_address) + " Port:" + str(self.port)
				logger.info(msg)
			except:
				msg = "Error opening the telnet connection to " + str(self.ip_address) + " Port:" + str(self.port)
				logger.warning(msg)
				self.status = "Offline"
			else:
				cmd = self.tn.read_until(b"\n", 2)
				cmd = cmd.decode("ascii")
				cmd = cmd[:-1]
				if cmd.find("Welcome to the Folding@home Client command server"):
					msg = "Server "+ str(self.ip_address) + "is running a Folding@home client and said hello"
					logger.info(msg)
				else:
					logger.warning("It looks that the telnet server is not running a Folding@home client")
		else:
			# ToDo ping the server
			pass
			
		
	def getOptions(self):
		# let's check the telnet connection
		self.connect()
		if self.status == "Offline":
			return
					
		# telnet server connected		
		command = "options" + "\r"
		byteCommand = command.encode(encoding='UTF-8')
		try:
			self.tn.write(byteCommand)
			response = self.tn.read_until(b"\n---\n", self.timeOut)
		except:
			msg = "Error sending the command " + command + "to the telnet server"
			logger.error(msg)

		content = response.decode()
		# strip of the beginning and the end of the so called PyON structure
		index = content.find("\nPyON ")
		content = content[index+6:]
		index = content.find("\n---\n")
		content = content[:index]
		
		index = content.find("options")
		content = content[index+8:]
		content = '{ "options": \n' + content
		content = content + '}'
		print("JSON-String: \n", content)
		self.options_JSON = json.loads(content)
		
		msg = "JSON Dump\n" + json.dumps(self.options_JSON, indent=4, sort_keys=True)
		logger.debug(msg)
		self.power = ""
		self.user = ""
		self.team = ""
		try:
			self.power = self.options_JSON['options']['power']
		except: 
			logger.warning("power not found in the options")
		try:
			self.user = self.options_JSON['options']['user']
		except: 
			logger.warning("user not found in the options")
		try:	
			self.team = self.options_JSON['options']['team']
		except: 
			logger.warning("team not found in the options")
		
		return 

	def getPower(self):
		# let's check the telnet connection
		self.connect()
		if self.status == "Offline":
			return
					
		# telnet server connected		
		command = "options power" + "\r"
		byteCommand = command.encode(encoding='UTF-8')
		try:
			self.tn.write(byteCommand)
			response = self.tn.read_until(b"\n---\n", self.timeOut)
		except:
			msg = "Error sending the command " + command + "to the telnet server"
			logger.error(msg)

		content = response.decode()
		# strip of the beginning and the end of the so called PyON structure
		index = content.find("\nPyON ")
		content = content[index+6:]
		index = content.find("\n---\n")
		content = content[:index]
		
		index = content.find("options")
		content = content[index+8:]
		content = '{ "options": \n' + content
		content = content + '}'
		#print("JSON-String: \n", content)
		self.options_JSON = json.loads(content)
		
		msg = "JSON Dump\n" + json.dumps(self.options_JSON, indent=4, sort_keys=True)
		#print(msg)
		logger.debug(msg)
		
		self.power = ""
		try:
			self.power = self.options_JSON['options']['power']
		except: 
			logger.warning("power not found in the options")
		
		return 
		
	def setPower(self, value):
		# let's check the telnet connection
		self.connect()
		if self.status == "Offline":
			return
					
		# telnet server connected		
		command = "option power " +value + "\r"
		msg = "Power command: "+command
		logger.info(msg)
		byteCommand = command.encode(encoding='UTF-8')
		try:
			self.tn.write(byteCommand)
		except:
			msg = "Error sending the command " + command + "to the telnet server"
			logger.error(msg)
		self.power = value
		
		return 
	
	def getPPD(self):
		# let's check the telnet connection
		self.connect()
		if self.status == "Offline":
			return
					
		# telnet server connected		
		command = "ppd" + "\r"
		byteCommand = command.encode(encoding='UTF-8')
		try:
			self.tn.write(byteCommand)
			response = self.tn.read_until(b"\n---\n", self.timeOut)
		except:
			msg = "Error sending the command " + command + "to the telnet server"
			logger.error(msg)

		content = response.decode()
		# strip of the beginning and the end of the so called PyON structure
		index = content.find("\nPyON ")
		content = content[index+6:]
		index = content.find("\n---\n")
		content = content[:index]
		
		index = content.find("ppd")
		content = content[index+4:]
		#content = '{ "options": \n' + content
		#content = content + '}'
		self.ppd = str(int(float(content)))

		msg = "Client: " + self.name +" PPD: " + self.ppd
		logger.debug(msg)
		
		return 

		
	def getSlots(self):
		# let's check the telnet connection
		self.connect()
		if self.status == "Offline":
			return None

		# get the slot stucture
		command = "slot-info\r"
		byteCommand = command.encode(encoding='UTF-8')
		try:
			self.tn.write(byteCommand)
			response = self.tn.read_until(b"\n---\n", 2)
		except:
			msg = "Error sending the command " + command + "to the telnet server"
			logger.error(msg)

		content = response.decode()

		index = content.find("\nPyON ")
		content = content[index+6:]
		index = content.find("\n---\n")
		content = content[:index]

		index = content.find("slots")
		content = content[index+6:]
		content = '{ "slots": \n' + content
		content = content + '}'
		content = content.replace("False",'"False"')

		#print("JSON-String: \n", content)
		self.slots_json = json.loads(content)
		msg = "JSON Slots\n" + json.dumps(self.slots_json, indent=4, sort_keys=True)
		
		logger.info(msg)
		
		self.numOfSlots = len(self.slots_json['slots'])
		#print("Number of slots: ", self.numOfSlots)

		return self.slots_json
		
		
	def fold(self, slotID):
		# let's check the telnet connection
		self.connect()
		if self.status == "Offline":
			return
					
		# telnet server connected		
		command = "unpause " + slotID + "\r"
		#print("Unpause command: "+command)
		byteCommand = command.encode(encoding='UTF-8')
		try:
			self.tn.write(byteCommand)
		except:
			msg = "Error sending the command " + command + "to the telnet server"
			logger.error(msg)

		return

	def pause(self, slotID):
		# let's check the telnet connection
		self.connect()
		if self.status == "Offline":
			return
					
		# telnet server connected		
		command = "pause " + slotID + "\r"
		#print("Unpause command: "+command)
		byteCommand = command.encode(encoding='UTF-8')
		try:
			self.tn.write(byteCommand)
		except:
			msg = "Error sending the command " + command + "to the telnet server"
			logger.error(msg)

		return
		
	def finish(self, slotID):
		# let's check the telnet connection
		self.connect()
		if self.status == "Offline":
			return
					
		# telnet server connected		
		command = "finish " + slotID + "\r"
		#print("Unpause command: "+command)
		byteCommand = command.encode(encoding='UTF-8')
		try:
			self.tn.write(byteCommand)
		except:
			msg = "Error sending the command " + command + "to the telnet server"
			logger.error(msg)

		return

	def getUnits(self):
		# let's check the telnet connection
		self.connect()
		if self.status == "Offline":
			return

		# get the unit stucture
		command = "queue-info\r"
		byteCommand = command.encode(encoding='UTF-8')
		try:
			self.tn.write(byteCommand)
			response = self.tn.read_until(b"\n---\n", 2)
		except:
			msg = "Error sending the command " + command + "to the telnet server"
			logger.error(msg)

		content = response.decode()

		index = content.find("\nPyON ")
		content = content[index+6:]
		index = content.find("\n---\n")
		content = content[:index]

		# get the work units from the server
		index = content.find("units")
		content = content[index+6:]
		content = '{ "units": \n' + content
		content = content + '}'
		#print("JSON-String: \n", content)
		self.units_json = json.loads(content)
		self.numOfUnits = len(self.units_json['units'])
		msg = "JSON Dump\n" +  json.dumps(self.units_json, indent=4, sort_keys=True)
		logger.debug(msg)
		return self.units_json
		

def main():		
	ClientList = []
	OneClient = FAH_Client("First", "127.0.0.1", 36330)

	print(OneClient.name)

	print(OneClient.ip_address)

	print (len(ClientList))

	ClientList.append(OneClient)

	OneClient = FAH_Client("Second", "192.168.178.24")

	ClientList.append(OneClient)

	print(ClientList[0].name)
	print(ClientList[1].name)

	print (len(ClientList))


if __name__ == '__main__':
	main()
