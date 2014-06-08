#!/usr/bin/env python

import asyncio,websockets,json,hashlib

room_dict   = {}

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
	# global client_dict
	global room_dict

	try:
		while client.open:
			data = yield from client.recv()
			data = json.loads(data)

			type_msg = data.get('type_msg',False)

			match_list = ['name','token','room']
			match_list = list(map(lambda key:data.get(key,False),match_list))
			print(match_list)

			pass_trigger = False
			if all(match_list) and type_msg == 'login':
				if Enigma_match(data.get('name',False), data.get('token',False)):

					room = data.get('room','')
					pass_trigger = True
					print(pass_trigger)

					if not room_dict.get(room,False): #пили ф-цию, а лучше класс
						room_dict[room]                = {}
						room_dict[room]['client_dict'] = {}
						room_dict[room]['user_list']   = {}						


					room_dict[room]['client_dict'][client] = {
					                                        'token' :data.get('token'),
														    'name'  :data.get('name'),
														    'client':client
															}
					room_dict[room]['user_list'][client] = data.get('name')

				else:
					data_json           = {'error':'access denied'} 
					data_json           = json.dumps(data_json)
					yield from client.send(data_json)
					yield from client.close()

			elif type_msg == 'message':
				print('34: {}'.format(room_dict[room]['client_dict']))

				data_json = {
								'message'  :data.get('message',False),
								'image'    :data.get('image',False),
								'user_list':list(room_dict[room]['user_list'].values()),
								'name'     :data.get('name')
				             }

				data_json = json.dumps(data_json)

				for client_item in room_dict[room]['client_dict']:
					yield from client_item.send(data_json)

			else:
				data_json           = {'error':'access denied'}
				data_json           = json.dumps(data_json)
				yield from client.send(data_json)
				yield from client.close()

	except Exception as error:
		print("67: {}".format(error))
		if not client.open:
			print('Disconnected')
			room_dict[room]['client_dict'].pop(client)
			room_dict[room]['user_list'].pop(client)
		for client_item in room_dict[room]['client_dict']:
			yield from client_item.send(json.dumps({'user_list':list(room_dict[room]['user_list'].values())}))

starter = websockets.serve(server, 'localhost', 4042)

asyncio.get_event_loop().run_until_complete(starter)
asyncio.get_event_loop().run_forever()