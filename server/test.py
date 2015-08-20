from aiohttp import web
import aiohttp
import asyncio


@asyncio.coroutine
def websocket_handler(request):

    ws = web.WebSocketResponse()
    ws.start(request)
    print(request)

    while True:
        msg = yield from ws.receive()
        print(msg)

        if msg.tp == aiohttp.MsgType.text:
            if msg.data == 'close':
                yield from ws.close()
            else:
                ws.send_str(msg.data + '/answer')
        elif msg.tp == aiohttp.MsgType.close:
            print('websocket connection closed')
        elif msg.tp == aiohttp.MsgType.error:
            print('ws connection closed with exception %s',
                  ws.exception())

    return ws


@asyncio.coroutine
def index_handler(request):
    print('index', request)
    return web.Response(status=404)


@asyncio.coroutine
def html_handler(request):
    # data = yield from request.get()
    # print(data)
    with open('templates/async_login.html', 'r') as template:
        response = web.Response(text=template.read())
        response.content_type = 'text/html; charset=UTF-8'
        return response


@asyncio.coroutine
def post_handler(request):
    data = yield from request.post()
    print(data)
    with open('templates/async.html', 'r') as template:
        response = web.Response(text=template.read())
        response.content_type = 'text/html; charset=UTF-8'
        return response


app = web.Application()
app.router.add_static(path='static', prefix='/static/')
app.router.add_route('GET', '/', html_handler)
app.router.add_route('POST', '/', post_handler)
loop = asyncio.get_event_loop()
handler = app.make_handler()
f = loop.create_server(handler, '0.0.0.0', 4042)
srv = loop.run_until_complete(f)
print('serving on', srv.sockets[0].getsockname())
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.run_until_complete(handler.finish_connections(1.0))
    srv.close()
    loop.run_until_complete(srv.wait_closed())
    loop.run_until_complete(app.finish())
loop.close()
