#!/usr/bin/env python

import asyncio,websockets,json,hashlib,pymongo,time

CONN = pymongo.Connection('localhost', 27017)
DB = CONN['asyncchat_db']
COLLECTION = DB['rooms']

ROOM_DICT   = {}

class Room_class(object):
	"""Simple class of simple room"""

	def __init__(self):
		self.client_dict = {}
		self.user_list   = {}
		self.password    = False

	@asyncio.coroutine
	def onDisconnect(self,client,reason = 'Access denied',clean = False):
		"""For disconctions by user/server"""
		if clean and not client.open:
			print('Disconnected')
			self.client_dict.pop(client)
			self.user_list.pop(client)
			for client_item in self.client_dict:
				yield from client_item.send(json.dumps({'user_list':list(self.user_list.values())}))
		else:
			yield from client.send(json.dumps({'error':reason}))
			yield from client.close(reason = reason)

		data_json = {'user_list':list(self.user_list.values())}
		data_json = json.dumps(data_json)

		for client_item in self.client_dict:
			yield from client_item.send(data_json)	

	@asyncio.coroutine
	def onConnect(self,client,data):
		"""Second level hendshake"""
		self.client_dict[client] = {
                                    'token' :data.get('token'),
								    'name'  :data.get('name')
									}

		if data.get('name') in self.user_list.values():
			print(data.get('name') in self.user_list.values())
			asyncio.Task(self.onDisconnect(client,reason = 'User already exists'))
		else:
			self.user_list[client] = data.get('name')

			data_json = {
						'user_list':list(self.user_list.values()),
						'name'     :data.get('name')
		             }
		             
			data_json = json.dumps(data_json)
			for client_item in self.client_dict:
				yield from client_item.send(data_json)	

	@asyncio.coroutine
	def onMessage(self,client,data):
		"""Parsing messages from clients"""
		data_json = {
						'message'  :data.get('message',False),
						'image'    :data.get('image',False),
						'name'     :data.get('name')
		             }
		data_json = json.dumps(data_json)
		for client_item in self.client_dict:
			yield from client_item.send(data_json)

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

	try:
		while client.open:
			data = yield from client.recv()
			data = json.loads(data)
			type_msg = data.get('type_msg',False)

			crypt_test = Enigma_match(data.get('name'), data.get('token'))
			room_test  = data.get('room',False)

			if all([(type_msg == 'login'),room_test,crypt_test]):
				room = data.get('room')
				room_pass_test = False
				room_token = data.get('room_token',False)

				if not ROOM_DICT.get(room,False):
					ROOM_DICT[room] = Room_class()
					ROOM_DICT[room].password = room_token
					room_pass_test = True

					log = {room:{'token':room_token}}
					COLLECTION.save(log)
				else:
					room_pass_test = (ROOM_DICT[room].password == room_token)

				asyncio.Task(ROOM_DICT[room].onConnect(client,data) if room_pass_test else ROOM_DICT[room].onDisconnect(client))
			
			elif type_msg == 'message':
				asyncio.Task(ROOM_DICT[room].onMessage(client,data))

				log = {room:{'message':data.get('message',False),'name':ROOM_DICT[room].user_list[client],'image':data.get('image',False),'time':time.time()}}
				COLLECTION.save(log)
			else:
				asyncio.Task(ROOM_DICT[room].onDisconnect(client))

	except Exception as error:
		print("67: {}".format(error))
		asyncio.Task(ROOM_DICT[room].onDisconnect(client,clean = True))

starter = websockets.serve(server, 'localhost', 4042)

asyncio.get_event_loop().run_until_complete(starter)
asyncio.get_event_loop().run_forever()