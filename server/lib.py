import asyncio,json,hashlib,time

class Room_class(object):
	"""Simple class of a simple room"""

	def __init__(self,password = False):
		self.user_list   = {}
		self.password    = password

	@asyncio.coroutine
	def onDisconnect(self,client,reason = 'Access denied',clean = False):
		if clean and not client.open:
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
	def onMessage(self,data=False):
		"""Parsing messages from clients"""
		data_json = {
						'message'  :data.get('message',False),
						'image'    :data.get('image'  ,False),
						'name'     :data.get('name'   ,False),
						'time'     :data.get('time'   ,False),
		             }
		data_json = json.dumps(data_json)
		for client_item in self.user_list:
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