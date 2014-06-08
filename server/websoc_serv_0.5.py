#!/usr/bin/env python

import asyncio,websockets,json,hashlib

room_dict   = {}

class Room_class(object):
	"""Simple class of simple room"""

	def __init__(self):
		self.client_dict = {}
		self.user_list   = {}
		self.password    = False

	@asyncio.coroutine
	def onDissconnect(self,client,reason = 'Access denied',clean = False):
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
		self.client_dict[client] = {
                                    'token' :data.get('token'),
								    'name'  :data.get('name')
									}
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
	global room_dict

	try:
		while client.open:
			data = yield from client.recv()
			data = json.loads(data)
			type_msg = data.get('type_msg',False)

			def matcher(data):
				match_list = ['name','token','room']
				match_list = list(map(lambda key:data.get(key,False),match_list))
				return all(match_list)

			if type_msg == 'login' and matcher(data):
				room = data.get('room')
				if Enigma_match(data.get('name'), data.get('token')):

					if not room_dict.get(room,False):
						room_dict[room] = Room_class()
						room_dict[room].password = data.get('room_password')

					if room_dict[room].password == data.get('room_password'):
						asyncio.Task(room_dict[room].onConnect(client,data))
					else:
						asyncio.Task(room_dict[room].onDissconnect(client))
				else:
					asyncio.Task(room_dict[room].onDissconnect(client))
			elif type_msg == 'message':
				asyncio.Task(room_dict[room].onMessage(client,data))
			else:
				asyncio.Task(room_dict[room].onDissconnect(client))

	except Exception as error:
		print("67: {}".format(error))
		asyncio.Task(room_dict[room].onDissconnect(client,clean = True))

starter = websockets.serve(server, 'localhost', 4042)

asyncio.get_event_loop().run_until_complete(starter)
asyncio.get_event_loop().run_forever()