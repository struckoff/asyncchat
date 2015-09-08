#!/usr/bin/env python
# coding=utf-8

import asyncio
import json
import aiohttp
import sys
from aiohttp import web
from lib import Room

PORT = 4042
IP = '0.0.0.0'
if len(sys.argv) == 2:
    PORT = int(sys.argv[1])
elif len(sys.argv) > 2:
    IP = sys.argv[1]
    PORT = int(sys.argv[2])


ROOM_DICT = {}


@asyncio.coroutine
def main_handler(request):
    with open('templates/single_page.html', 'r') as template:
        response = web.Response(text=template.read())
        response.content_type = 'text/html; charset=UTF-8'
        return response


@asyncio.coroutine
def websocket_handler(request):
    client = web.WebSocketResponse()
    client.start(request)
    room = None

    @asyncio.coroutine
    def access_granted(data):
        asyncio.Task(ROOM_DICT[data['room']].on_connect(client, data))
        with open('templates/chat.html', 'r') as template:
            res = json.dumps({'body': template.read()})
            client.send_str(res)

    @asyncio.coroutine
    def access_denied(reason):
        client.send_str(json.dumps({"error": reason}))
        yield from client.close()

    while True:
        msg = yield from client.receive()

        if msg.tp == aiohttp.MsgType.text:
            data = json.loads(msg.data)
            if data['type_msg'] == 'login':
                room = ROOM_DICT.get(data['room'])
                if room:
                    if not room.check_password(data['room_pass']):
                        yield from access_denied("Access denied")
                    elif room.has_user(data['name']):
                        yield from access_denied("User already exists")
                    else:
                        yield from access_granted(data)
                else:
                    ROOM_DICT[data['room']] = Room(data['room_pass'])
                    room = ROOM_DICT.get(data['room'])
                    yield from access_granted(data)

                # client.send_str(msg.data)
            elif data['type_msg'] == 'message' and (room is not None):
                asyncio.Task(room.on_message(client, data=data))

        elif msg.tp == aiohttp.MsgType.close:
            asyncio.Task(room.on_disconnect(client))
            print('websocket connection closed')
            break
        elif msg.tp == aiohttp.MsgType.error:
            print('ws connection closed with exception %s', client.exception())
            break

    return client


APP = web.Application()

APP.router.add_static(path='static', prefix='/static/')
APP.router.add_route('*', '/', main_handler)
APP.router.add_route('GET', '/ws', websocket_handler)

LOOP = asyncio.get_event_loop()
HANDLER = APP.make_handler()
SERVER_FACTORY = LOOP.create_server(HANDLER, IP, PORT)
SERVER = LOOP.run_until_complete(SERVER_FACTORY)

print('serving on', SERVER.sockets[0].getsockname())

try:
    LOOP.run_forever()
except KeyboardInterrupt:
    pass
finally:
    LOOP.run_until_complete(HANDLER.finish_connections(1.0))
    SERVER.close()
    LOOP.run_until_complete(SERVER.wait_closed())
    LOOP.run_until_complete(APP.finish())
LOOP.close()
