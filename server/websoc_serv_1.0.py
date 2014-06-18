#!/usr/bin/env python

import asyncio,websockets,json,pymongo,time
from lib import *

CONN                = pymongo.Connection('localhost', 27017)
# CONN                = pymongo.MongoClient('mongodb://:@kahana.mongohq.com:10047/async_db')
DB                  = CONN['async_db']
COLLECTION_ROOMS    = DB['rooms']
COLLECTION_MESSAGES = DB['messages']

ROOM_DICT           = {}

#Восстанавливаем комнаты из бэкапа
ROOM_DICT.update((item['room_name'],Room_class(item.get('room_token',False))) for item in COLLECTION_ROOMS.find())

@asyncio.coroutine
def server(client, url):
	global ROOM_DICT

	while client.open:
		data = yield from client.recv()

		#При отключение польвателя data принимет значение None, используем это для ловде отключившихся
		if data == None:
			asyncio.Task(ROOM_DICT[room].onDisconnect(client,clean = True))
			print('User {} disconnected'.format(ROOM_DICT[room].user_list[client]))


		data     = json.loads(data)
		type_msg = data.get('type_msg',False)
		
		crypt_test = Enigma_match(data.get('name'), data.get('token'))

		if all([(type_msg == 'login'),data.get('room',False),crypt_test]):
			room            = data.get('room',False)
			connect_trigger = [False,'Access denied']
			room_token      = data.get('room_token',False)

			if not ROOM_DICT.get(room,False):
				ROOM_DICT[room]          = Room_class(room_token)
				connect_trigger[0]       = True

				#Небольшое бэкап списка комнат (на случай рестарта сервера)
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

					#небольшая альтернатива условиям
			Tasks = [ 
					  lambda: ROOM_DICT[room].onDisconnect(client,reason = connect_trigger[1]),
					  lambda: ROOM_DICT[room].onConnect(client,data)
					]

			asyncio.Task(Tasks[connect_trigger[0]]()) #решаем что делать с пользователем

			#Рассылаем логи
			if connect_trigger[0]:
				for item in COLLECTION_MESSAGES.find().sort('time'):
					asyncio.Task(ROOM_DICT[room].onMessage(data = item))

				print('User {} conneced'.format(data.get('name',False)))
		
		elif type_msg == 'message':
			data['time'] = time.time() 
			data['name'] = ROOM_DICT[room].user_list[client]
			asyncio.Task(ROOM_DICT[room].onMessage(data = data))

			#Отправляем полученое сообщение в БД (храним логи)
			doc = {                                                                 
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