#!/usr/bin/env python

import asyncio,websockets,json,hashlib,pymongo,time

CONN                = pymongo.Connection('localhost', 27017)
DB                  = CONN['asyncchat_db']
COLLECTION_ROOMS    = DB['rooms']
COLLECTION_MESSAGES = DB['messages']

ROOM_DICT           = {}

class Room_class(object):
	"""Simple class of a simple room"""

	def __init__(self):
		self.user_list   = {}
		self.password    = False

	@asyncio.coroutine
	def onDisconnect(self,client,reason = 'Access denied',clean = False):
		if clean and not client.open:
			print('Disconnected')
			if self.user_list.get(client,False):
				self.user_list.pop(client)
			for client_item in self.user_list:
				yield from client_item.send(json.dumps({'user_list':list(self.user_list.values())}))
		else:
			yield from client.send(json.dumps({'error':reason}))
			yield from client.close(reason = reason)

		data_json = {'user_list':list(self.user_list.values())}
		data_json = json.dumps(data_json)

		for client_item in self.user_list:
			yield from client_item.send(data_json)	

	@asyncio.coroutine
	def onConnect(self,client,data):
		"""Second level hendshake"""

		self.user_list[client] = data.get('name')

		data_json = {
					'user_list':list(self.user_list.values()),
					'name'     :data.get('name')
	             }
	             
		data_json = json.dumps(data_json)
		for client_item in self.user_list:
			yield from client_item.send(data_json)	

	@asyncio.coroutine
	def onMessage(self,client,data):
		"""Parsing messages from clients"""
		data_json = {
						'message'  :data.get('message',False),
						'image'    :data.get('image',False),
						'name'     :data.get('name',False)
		             }
		data_json = json.dumps(data_json)
		for client_item in self.user_list:
			yield from client_item.send(data_json)

for item in COLLECTION_ROOMS.find():
	ROOM_DICT[item['room_name']]          = Room_class()
	ROOM_DICT[item['room_name']].password = item['room_token']

print('77: {}'.format(ROOM_DICT))

def Enigma_match(name,token):

	if not (name and token):
		return False

	hashes={
				0:hashlib.md5,
				1:hashlib.sha512,
				2:hashlib.sha224,
				3:hashlib.sha1
	        }

	kreator = hashes.get(int(token[0]),False)

	if not kreator:
		return False
	else:
		kreator = kreator()
		kreator.update(name.encode())

	return token[1:] == kreator.hexdigest()

@asyncio.coroutine
def server(client, url):
	global ROOM_DICT

	# try:
		while client.open:
			data       = yield from client.recv()
			data       = json.loads(data)
			type_msg   = data.get('type_msg',False)
			
			crypt_test = Enigma_match(data.get('name'), data.get('token'))

			if all([(type_msg == 'login'),data.get('room',False),crypt_test]):
				room            = data.get('room',False)
				connect_trigger = [False,'Access denied']
				room_token      = data.get('room_token',False)

				if not ROOM_DICT.get(room,False):
					print('113: {}'.format(ROOM_DICT.get(room,False)))
					ROOM_DICT[room]          = Room_class()
					ROOM_DICT[room].password = room_token
					connect_trigger[0]       = True

					doc = {
					        'room_name' :room,
					        'room_token':room_token
					      }
					COLLECTION_ROOMS.save(doc)
				else:
					connect_trigger[0] = (ROOM_DICT[room].password == room_token)

				if connect_trigger[0]:
					connect_trigger = [
					                   not data.get('name') in ROOM_DICT[room].user_list.values(),
					                   "User already exists"
					                   ]
				print("123: {}".format(connect_trigger[0]))

				Tasks = [
						  lambda: ROOM_DICT[room].onDisconnect(client,reason = connect_trigger[1]),
						  lambda: ROOM_DICT[room].onConnect(client,data)
						]

				asyncio.Task(Tasks[connect_trigger[0]]())
			
			elif type_msg == 'message':
				asyncio.Task(ROOM_DICT[room].onMessage(client,data))

				doc = {                                                                 #!!
						'room_name':room,
						'message'  :data.get('message',False),
						'user'     :ROOM_DICT[room].user_list[client],
						'image'    :data.get('image',False),
						'time'     :time.time()				        
				      }

				COLLECTION_MESSAGES.save(doc)
			else:
				asyncio.Task(ROOM_DICT[room].onDisconnect(client))

	except Exception as error:
		print("150: {}".format(error))
		asyncio.Task(ROOM_DICT[room].onDisconnect(client,clean = True))

starter = websockets.serve(server, 'localhost', 4042)

asyncio.get_event_loop().run_until_complete(starter)
asyncio.get_event_loop().run_forever()