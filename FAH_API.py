from telnetlib import Telnet
import json

cmdList = ["finish", "pause", "pause 02", "ppd", "queue-info", "unpause", "slot-info", "num-slots", "options user", "options"]

def main(command, ip="127.0.0.1", timeOut=5, port=36330):
	if command not in cmdList:
		print("Error: Command '{}' is not supported".format(command))
		return("Not supported")
	else:
		print("Command '{}' will be sent to the server {}, port {}".format(command,ip,port))
	command = command + "\r"
	try:
		tn = Telnet(ip, port)
	except:
		print("Error opening the telnet connection to ",ip, "Port:",port)
	byteCommand = command.encode(encoding='UTF-8')
	try:
		tn.write(byteCommand)
		response = tn.read_until(b"\n---\n", timeOut)
	except:
		print("Error sending the command ",command, "to the telnet server")
	finally:
		tn.write(b"exit\r")
		tn.close()
	content = response.decode()
	# strip of the beginning and the end of the so called PyON structure
	index = content.find("\nPyON ")
	content = content[index+6:]
	index = content.find("\n---\n")
	content = content[:index]
	
	#was there an error returned?
	#if content.find("error"):
	#	print("Error: ",content)
	#	return(content)
		
	#print("Stripped: \n", content)
	# so far it's generic, now we have to distinguish between the commands
	if command == "slot-info\r":
		index = content.find("slots")
		content = content[index+6:]
		content = '{ "slots": \n' + content
		content = content + '}'
		content = content.replace("False",'"False"')
		#print("JSON-String: \n", content)
		parsed_json = json.loads(content)
		#print("JSON Dump\n", json.dumps(parsed_json, indent=4, sort_keys=True))
		return parsed_json
	elif command == "num-slots\r":
		index = content.find("num-slots")
		content = content[index+10:]
		#print("It's a number: ", content)
		return content
	elif command == "ppd\r":
		index = content.find("ppd")
		content = content[index+4:]
		#print("It's a number: ", content)
		return content
	elif command == "options user\r" or command == "options\r":
		index = content.find("options")
		content = content[index+8:]
		content = '{ "options": \n' + content
		content = content + '}'
		#print("JSON-String: \n", content)
		parsed_json = json.loads(content)
		#print("JSON Dump\n", json.dumps(parsed_json, indent=4, sort_keys=True))
		return parsed_json
	elif command == "queue-info\r":
		index = content.find("units")
		content = content[index+6:]
		content = '{ "units": \n' + content
		content = content + '}'
		print("JSON-String: \n", content)
		parsed_json = json.loads(content)
		#print("JSON Dump\n", json.dumps(parsed_json, indent=4, sort_keys=True))
		return parsed_json
	elif command == "pause\r" or command == "finish\r" or command == "unpause\r":
		return
	else:
		return "No supported command"


if __name__ == '__main__':
	pJSON = main("slot-info") #slot-info return a JSON object
	print("JSON Dump\n", json.dumps(pJSON, indent=4, sort_keys=True))
	print("Number of slots: ", len(pJSON['slots']))
	i = 0
	while i < len(pJSON['slots']):
		print("SlotID:", pJSON['slots'][i]['id'])
		i += 1
	
	#num_Slots = pJSON.SizeOfArray("slots")
	#while i < num_Slots:
	#	print("SlotID: ",i , pJSON.stringOf("slots[i].id")
	
	'''
	s = main("num-slots") # returns an integer as a string
	print("It's a number: ", s)
	
	pJSON = main("options user") # returns the userID
	print("JSON Dump\n", json.dumps(pJSON, indent=4, sort_keys=True))

	pJSON = main("options") # returns the options
	print("JSON Dump\n", json.dumps(pJSON, indent=4, sort_keys=True))
	print("User: ",pJSON['options']['user'])
	
	main("finish","127.0.0.1",1) # does not return anything
	
	main("pause","127.0.0.1",1) # does not return anything
	
	'''
	pJSON = main("queue-info") # returns the queue-info
	print("JSON Dump\n", json.dumps(pJSON, indent=4, sort_keys=True))
	'''
	
	#s = main("pause 02") # error case for a not defined slot
	#print(s)
	
	ppd = main("ppd") # returns a string
	print("PointsPerDay:",ppd)
	
	# command not supported
	s = main("numbers") # not a supported command
	print("It's a number: ", s)
	'''
