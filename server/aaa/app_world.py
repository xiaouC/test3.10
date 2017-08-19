#!/usr/bin/python
# coding: utf-8

from rpc_service import rpc_service

service_list = [
    rpc_service(),
]

class app_world(object):
    def __init__(self):
        pass

    def __call__(self, socket, address):
        try:
            while True:
                data = socket.recv(4096)
                if not data:
                    socket.close()
                else:
                    for service in service_list:
                        response = world_service(int(data), data, data)
                        if response:
                            socket.sendall(response)
                            break
        except Exception as e:
            print e
            socket.close()

