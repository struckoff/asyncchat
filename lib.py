"""Room class module"""

import asyncio
import json
import hashlib
import time


class Room(object):
    """Simple class of a simple room"""

    def __init__(self, password):
        self.user_list = {}
        self.__set_password(password)
        self._log = []

    def check_password(self, client_passwd):
        """Cmp passwords of room and client"""
        crypt = hashlib.sha256()
        crypt.update(client_passwd.encode())
        return crypt.hexdigest() == self.__password

    def has_user(self, name):
        """Check if user with same name alredy exists in a room"""
        return name in self.user_list.values()

    def __set_password(self, room_passwd):
        """Set room password"""
        crypt = hashlib.sha256()
        crypt.update(room_passwd.encode())
        self.__password = crypt.hexdigest()

    @asyncio.coroutine
    def on_disconnect(self, client):
        """Handle disconnection of user"""

        if self.user_list.get(client):
            nick = self.user_list[client]
            self.user_list.pop(client)

            data_json = {'user_list': list(self.user_list.values()),
                         'message': '{} has left'.format(nick),
                         'name': 'SERVER',
                         'time': time.time(),
                         }
            data_json = json.dumps(data_json)

            for client_item in self.user_list:
                client_item.send_str(data_json)

    @asyncio.coroutine
    def on_connect(self, client, data):
        """Handle connection of user"""

        self.user_list[client] = data.get('name')

        data_json = {
                    'user_list': list(self.user_list.values()),
                    'name': data.get('name')
                    }

        data_json = json.dumps(data_json)
        for client_item in self.user_list:
            client_item.send_str(data_json)

        for msg in self._log:
            client.send_str(msg)

    @asyncio.coroutine
    def on_message(self, client, data, reciever=None):
        """Handle messages from user"""

        data_json = {
                        'message': data.get('message'),
                        'image': data.get('image'),
                        'name': self.user_list[client],
                        'time': data.get('time'),
                     }

        data_json = json.dumps(data_json)

        self._log.append(data_json)
        if len(self._log) > 100:
            self._log = self._log[-100:]

        if reciever is not None:
            reciever.send_str(data_json)
        else:
            for client in self.user_list:
                client.send_str(data_json)
