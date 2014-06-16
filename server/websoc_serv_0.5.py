#!/usr/bin/env python

import asyncio,websockets,json,pymongo,time
from lib import *

# CONN                = pymongo.Connection('localhost', 27017)
CONN                = pymongo.MongoClient('mongodb://qwe:rty@kahana.mongohq.com:10047/async_db')
DB                  = CONN['async_db']
COLLECTION_ROOMS    = DB['rooms']
COLLECTION_MESSAGES = DB['messages']

ROOM_DICT           = {}

for item in COLLECTION_ROOMS.find():
	ROOM_DICT[item['room_name']]          = Room_class()
	ROOM_DICT[item['room_name']].password = item['room_token']

print('77: {}'.format(ROOM_DICT))

@asyncio.coroutine
def server(client, url):
	global ROOM_DICT

	while client.open:
		data = yield from client.recv()

		if data == None:
			asyncio.Task(ROOM_DICT[room].onDisconnect(client,clean = True))

		data     = json.loads(data)
		type_msg = data.get('type_msg',False)
		
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

			if connect_trigger[0]:
				for item in COLLECTION_MESSAGES.find().sort('time'):
					asyncio.Task(ROOM_DICT[room].onMessage(data = item))

		
		elif type_msg == 'message':
			data['time'] = time.time() 
			asyncio.Task(ROOM_DICT[room].onMessage(data = data))

			doc = {                                                                 #!!
					'room_name':room,
					'message'  :data.get('message',False),
					'name'     :ROOM_DICT[room].user_list[client],
					'image'    :data.get('image',False),
					'time'     :time.time()				        
			      }

			COLLECTION_MESSAGES.save(doc)
		else:
			asyncio.Task(ROOM_DICT[room].onDisconnect(client))

starter = websockets.serve(server, 'localhost', 4042)

asyncio.get_event_loop().run_until_complete(starter)
asyncio.get_event_loop().run_forever()