import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
import re
import threading
import time
import logging

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# create console handler and set level
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

'''
Levels of logging are:
	logger.debug('debug message')
	logger.info('info message')
	logger.warning('warn message')
	logger.error('error message')
	logger.critical('critical message')
'''

from FAH import FAH_Client

_ClientList = [] # global variable for the clients

# we need to access the dynamically generated widgets for edit, update, and delete
_ClientWidget = [] # global variable for client widget in the main Screen
_StatusWidget = [] # global variable for Status Widget in the main Screen
_EditWidget = [] # global variable for Edit Widget in the main Screen
_DeleteWidget = [] # global variable for Delete Widget in the main Screen

_ClientSemaphore = 0 # global variable for the threads
_UpdateClientSemaphore = 0 # global variable for updating the client window
_SelectedClient = ""

store = JsonStore('FAH_remote.json')

def removeRef(s):
	aString = s[s.find("]")+1:]
	aString = aString[:aString.rfind("[")]
	return(aString)
	
def thread_clients(number):

	i = 0
	for k in _ClientList:
		logger.debug("ClientName:",k.name)
		k.connect()
		_StatusWidget[i].text = k.status
		i = i +1

	global _ClientSemaphore
	_ClientSemaphore = 0
	
	logger.debug("Client Threading ended")


def thread_updateClient(client):

	global _UpdateClientSemaphore
	global _ClientList
	
	A = kv
	
	for x in _ClientList:
		#print("Client name: ", x.name, x.status)
		if x.name == client and x.status == "Online":
			#print("Active client found:", x.name, x.status)
			x.getOptions()
			A.screens[2].lay1.clientLay.idUser.text = x.user

			x.getPower()
			A.screens[2].lay1.clientLay.idPower.text = x.power

			x.getPPD()
			A.screens[2].lay1.clientLay.idPpd.text = x.ppd

			pJSON = x.getSlots()
			A.screens[2].lay1.slotLay.idSlot.text = pJSON['slots'][0]['id']
			A.screens[2].lay1.slotLay.idSlotStatus.text = pJSON['slots'][0]['status']
			A.screens[2].lay1.slotLay.idSlotDescription.text = pJSON['slots'][0]['description']

			spinnerValues = []
			i = 0
			while i < x.numOfSlots:
				#print("SlotID:", pJSON['slots'][i]['id'])
				spinnerValues.append(pJSON['slots'][i]['id'])
				i += 1
			#print("SpinnerValues: ", spinnerValues)
			A.screens[2].lay1.slotLay.idSlot.values = spinnerValues
			
			x.getUnits()
			pJSON = x.getUnits()
			# the slot spinner text defines the slot, let's look for it in the units JSON
			A.screens[2].lay1.queueLay.idQueue.text = "" 
			i = 0
			while i < x.numOfUnits:
				if pJSON['units'][i]['slot'] == A.screens[2].lay1.slotLay.idSlot.text:
					A.screens[2].lay1.queueLay.idQueue.text = pJSON['units'][i]['id'] 
					A.screens[2].lay1.queueLay.idQueueStatus.text = pJSON['units'][i]['state'] 
					A.screens[2].lay1.queueLay.idProgress.text = pJSON['units'][i]['percentdone'] 
					A.screens[2].lay1.queueLay.idETA.text = pJSON['units'][i]['eta'] 
				i += 1

	_UpdateClientSemaphore = 0


class WindowManager(ScreenManager):
	pass


class MainWindow(Screen):
	def __init__(self, **kwargs):
		super(MainWindow, self).__init__(**kwargs)
		Clock.schedule_interval(self.checkClients,1)
		
	def checkClients(self, *args):
		global _ClientSemaphore

		# Start the separate thread
		if _ClientSemaphore == 0:
			x = threading.Thread(target=thread_clients, args=(1,))
			_ClientSemaphore = 1
			x.start()

		
class ClientWindow(Screen):
	def __init__(self, **kwargs):
		super(ClientWindow, self).__init__(**kwargs)
		Clock.schedule_interval(self.updateClientStatus,2)
		
	def updateClientStatus(self, *args):
		global _UpdateClientSemaphore
		global _SelectedClient

		# Start the separate thread
		if _UpdateClientSemaphore == 0:
			x = threading.Thread(target=thread_updateClient, args=(_SelectedClient,))
			_UpdateClientSemaphore = 1
			x.start()

		
	def set_client_power(self, value):
		#print("Power selected: ", value)

		global _SelectedClient
		
		for x in _ClientList:
			if x.name == _SelectedClient:
				#print("Client {} found, grabbing the data".format(args[0].text))
				x.setPower(value)
				
	def selectSlot(self, value):
		#print("Slot {} selected".format(value))

		A = kv
		
		for x in _ClientList:
			if x.name == _SelectedClient:
				pJSON = x.slots_json
				for i in range(0,x.numOfSlots):
					#print("Inkrement i:",i)
					if value == pJSON['slots'][i]['id']:
						A.screens[2].lay1.slotLay.idSlotStatus.text = pJSON['slots'][i]['status']
						A.screens[2].lay1.slotLay.idSlotDescription.text = pJSON['slots'][i]['description']
				
	def fold(self):
		A = kv
		
		for x in _ClientList:
			if x.name == _SelectedClient:
				# get the selected slot id
				slotID = A.screens[2].lay1.slotLay.idSlot.text
				x.fold(slotID)

	def pause(self):
		A = kv
		
		for x in _ClientList:
			if x.name == _SelectedClient:
				# get the selected slot id
				slotID = A.screens[2].lay1.slotLay.idSlot.text
				x.pause(slotID)

	def finish(self):
		A = kv
		
		for x in _ClientList:
			if x.name == _SelectedClient:
				# get the selected slot id
				slotID = A.screens[2].lay1.slotLay.idSlot.text
				x.finish(slotID)

	

class AddWindow(Screen):
	
	def saveBtn(self):
		clientName = self.lay1.innerLay.clientName.text.strip()
		# let's look if the given client name is unique and not empty
		# todo
		
		entries = list(store.find(name=clientName))
		#print("Entries:", entries)
		if len(entries) != 0 or len(clientName) == 0:
			show_popup("Client name exists or is empty")
			return
		
		clientIP = self.lay1.innerLay.ipAddress.text.strip()
		# let's check the IP address againt the regular expression of a real IP address
		matchIP = re.search("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", clientIP)
		if matchIP == None:
			#print("No IP address given", clientIP)
			show_popup("IP address is not valid")
		else:
		
			port = int(self.lay1.innerLay.port.text.strip())
			
			# store the new client permanent
			store.put(str(clientIP), name=clientName, port=port)
			msg = 'Client stored: ' + clientIP +" "+ clientName
			logger.info(msg)
			# switch to the main screen
			A = kv
			A.current = "main"
			
			app= App.get_running_app() # get the app to access the changeWindow function
			
			aButton = MyButton(text=clientName, name=clientName)
			aButton.bind(on_release=app.changeWindow)
			_ClientWidget.append(aButton)
			A.screens[0].lay1.innerLay.add_widget(aButton)
			
			aLabel = Label(text="Offline")
			A.screens[0].lay1.innerLay.add_widget(aLabel)
			_StatusWidget.append(aLabel)
			
			aButton = MyButton(text="Edit", name=clientName)
			aButton.bind(on_release=aButton.editBtn)
			A.screens[0].lay1.innerLay.add_widget(aButton)
			_EditWidget.append(aButton)
			
			aButton = MyButton(text="Delete", name=clientName)
			aButton.bind(on_release=aButton.deleteBtn)
			A.screens[0].lay1.innerLay.add_widget(aButton)
			_DeleteWidget.append(aButton)
			
			# create the client object and append it to the list of clients
			aClient = FAH_Client(clientName, clientIP, port)
			_ClientList.append(aClient)
			
			
class EditClient(Screen):
	
	def saveBtn(self):
		
		global _SelectedClient
		global _ClientList
		
		for key, entry in store.find(name=_SelectedClient):
			#print('key:', key, ', entry:', entry)
			#print("Name", entry['name'])
			oldIP = key
			oldEntry = entry

		# delete the old entry in the storage
		store.delete(oldIP)
		
		# get the client line index for the widgets
		widgetIndex = 0
		for x in _ClientList:
			if x.name == _SelectedClient:
				#print("x.name:", x.name)
				break
			widgetIndex += 1
		
		#print("WidgetIndex", widgetIndex)
		
		clientName = self.lay1.innerLay.clientName.text.strip()
		
		# name must be unique
		entries = list(store.find(name=clientName))
		#print("Entries:", entries)
		if len(entries) != 0 or len(clientName) == 0:
			show_popup("Client name exists or is empty")
			# restore old client
			store.put(oldIP, name=oldEntry['name'], port=oldEntry['port'])
			return
		
		clientIP = self.lay1.innerLay.ipAddress.text.strip()
		# let's check the IP address againt the regular expression of a real IP address
		matchIP = re.search("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", clientIP)
		if matchIP == None:
			#print("No IP address given", clientIP)
			show_popup("IP address is not valid")
			# restore old client
			store.put(oldIP, name=oldEntry['name'], port=oldEntry['port'])
		else:
					
			port = int(self.lay1.innerLay.port.text.strip())

			# update the widgets, clients and client lists
			_ClientWidget[widgetIndex].text = clientName
			_EditWidget[widgetIndex].name = clientName
			_DeleteWidget[widgetIndex].name = clientName 	
			_SelectedClient = clientName
			#print("SelectedClient: ", _SelectedClient)

			# switch to the main screen
			A = kv
			A.current = "main"

			#return # for the time being

			# store the new client permanent
			store.put(str(clientIP), name=clientName, port=port)
			msg = 'Client stored: ' + clientIP +" "+ clientName + " " + str(port)
			logger.info(msg)
			#print(msg)
			# update the client object and the clientList
			aClient = _ClientList.pop(widgetIndex)
			aClient.name = clientName
			aClient.ip_address = clientIP
			aClient.port = port
			
			_ClientList.insert(widgetIndex,aClient)
			

class IPTextInput(TextInput):
	def insert_text(self, substring, from_undo=False):
		if re.search(r"[0-9\.]",substring):
			s = substring
		else:
			s = ""
		return super(IPTextInput, self).insert_text(s, from_undo=from_undo)


class MyPopup(FloatLayout):
	def __init__(self, **kwargs):
		super(MyPopup, self).__init__()
		self.idLabel.text = kwargs['text']

class ConfirmPopup(FloatLayout):
	def __init__(self, **kwargs):
		super(ConfirmPopup, self).__init__()
		self.idLabel.text = kwargs['text']

	
def show_popup(textStr):
	show = MyPopup(text=textStr) # Create a new instance of the Popup class 
	
	popupWindow = Popup(title="Popup Window", content=show, size_hint=(None,None),size=(400,400)) 
	# Create the popup window

	show.idButton.bind(on_press=popupWindow.dismiss)

	popupWindow.open() # show the popup

def show_ConfirmPopup(clientName):
	msg = "Do you really wanna delete the client " + clientName + "?"
	show = ConfirmPopup(text=msg) # Create a new instance of the Popup class 
	
	popupWindow = Popup(title="Confirm Window", content=show, size_hint=(None,None),size=(400,400)) 
	# Create the popup window

	# toDo: we have to call the real deleteClient function here
	app= App.get_running_app() # get the app to access the deleteClient function
	
	show.idButton.bind(on_press=app.deleteClient)
	show.idButton.bind(on_release=popupWindow.dismiss)

	show.idCancel.bind(on_press=popupWindow.dismiss)

	popupWindow.open() # show the popup

	
	
# Load the kivy file with the static GUI components 
kv = Builder.load_file("FAH.kv")

class MyButton(Button):
	def __init__(self, **kwargs):
		super(MyButton, self).__init__()
		self.text = kwargs['text']
		self.name = kwargs['name']

	def editBtn(self, *args):
		#print("Text Prop:",self.text)
		#print("Client Prop:",self.name)
		
		global _SelectedClient
		_SelectedClient = self.name
		A = kv
		A.transition.direction = "left"
		A.current = "EditWindow"
		A.screens[3].lay1.innerLay.clientName.text = _SelectedClient
		for x in _ClientList:
			if x.name == _SelectedClient:
				A.screens[3].lay1.innerLay.ipAddress.text = x.ip_address
				A.screens[3].lay1.innerLay.port.text = str(x.port)
			
	def deleteBtn(self, *args):
		#print("Text Prop:",self.text)
		#print("Client Prop:",self.name)
		global _SelectedClient
		_SelectedClient = self.name
		show_ConfirmPopup(self.name)

class MyLabel(Label):
	def __init__(self, **kwargs):
		super(MyLabel, self).__init__()
		self.text = kwargs['text']
		self.name = kwargs['name']

			
	
class FAH_Remote(App):

	def changeWindow(self, *args):
		A = kv
		A.current = "Client"
		logger.debug("Change Screen to ClientName: ", args[0].text)
		A.screens[2].lay1.idClient.text = "Client: "+args[0].text
		
		# clear screen for the new client
		A.screens[2].lay1.clientLay.idUser.text = ""
		A.screens[2].lay1.clientLay.idPower.text = ""
		A.screens[2].lay1.clientLay.idPpd.text = ""

		A.screens[2].lay1.slotLay.idSlot.text = "Slot"
		A.screens[2].lay1.slotLay.idSlotStatus.text = ""
		A.screens[2].lay1.slotLay.idSlotDescription.text = ""
		A.screens[2].lay1.slotLay.idSlot.values = "SlotID"
		A.screens[2].lay1.queueLay.idQueue.text = "" 
		A.screens[2].lay1.queueLay.idQueueStatus.text = "" 
		A.screens[2].lay1.queueLay.idProgress.text = "" 
		A.screens[2].lay1.queueLay.idETA.text = "" 
		
		global _SelectedClient
		_SelectedClient = args[0].text

	def deleteClient(self, *args):

		global _SelectedClient
		global _ClientList
		
		for key, entry in store.find(name=_SelectedClient):
			#print('key:', key, ', entry:', entry)
			#print("Name", entry['name'])
			oldIP = key
			oldEntry = entry

		# delete the old entry in the storage
		store.delete(oldIP)
		
		# get the client line index for the widgets
		widgetIndex = 0
		for x in _ClientList:
			if x.name == _SelectedClient:
				#print("x.name:", x.name)
				break
			widgetIndex += 1

		#print("Parent:", _ClientWidget[0].parent)
		# now let's walk through the children
		for widget in _ClientWidget[0].parent.walk():
			if isinstance(widget,MyButton):
				if widget.name == _SelectedClient:
					#print("MyButton WidgetName:", widget.name)
					_ClientWidget[0].parent.remove_widget(widget)
			if isinstance(widget,MyLabel):
				if widget.name == _SelectedClient:
					#print("MyLabel WidgetName:", widget.name)
					_ClientWidget[0].parent.remove_widget(widget)

		#print("SelectedClient: ", _SelectedClient)

		# remove the client object from the clientList
		aClient = _ClientList.pop(widgetIndex)

		msg = 'Client deleted: ' + oldIP +" "+ oldEntry['name'] + " " + str(oldEntry['port'])
		logger.info(msg)

		

	def build(self):

		A = kv
		A.current = 'main'
		# add the client lines from the store to the GUI
		logger.debug("Keys in the client dictionary: ",store.keys())
		clients = store.keys()
		#app= App.get_running_app() # get the app to access the changeWindow function

		for k in clients:
			logger.debug("Pairs: ", store.get(k))
			logger.debug("Name: ", store.get(k)['name'])
			logger.debug("Keys: ",store.keys())
			cName = store.get(k)['name']
			
			aButton = MyButton(text=cName, name=cName)
			aButton.bind(on_release=self.changeWindow)
			A.screens[0].lay1.innerLay.add_widget(aButton)
			_ClientWidget.append(aButton)
			
			aLabel = MyLabel(text="Offline", name=cName)
			A.screens[0].lay1.innerLay.add_widget(aLabel)
			_StatusWidget.append(aLabel)
			
			aButton = MyButton(text="Edit", name=cName)
			A.screens[0].lay1.innerLay.add_widget(aButton)
			aButton.bind(on_release=aButton.editBtn)
			_EditWidget.append(aButton)

			aButton = MyButton(text="Delete", name=cName)
			A.screens[0].lay1.innerLay.add_widget(aButton)
			aButton.bind(on_release=aButton.deleteBtn)
			_DeleteWidget.append(aButton)

			# create the client object and append it to the list of clients
			aClient = FAH_Client(cName, k, store.get(k)['port'])
			_ClientList.append(aClient)
		
		return kv

if __name__ == "__main__":

	logger.info("FAH_Remote started")
	
	FAH_Remote().run()
    
