#!/usr/bin/python
# coding: utf-8

from functools import wraps

class rpc_service(object):
    def __init__(self):
        self.msg_callbacks = {}

    def register_msg(self, msg_id):
        print 'msg_id : ', msg_id
        def decorator(func):
            print 'func : ', func
            self.msg_callbacks[msg_id] = func

            #@wraps(func)
            def new_msg_func(*args, **kwargs):
                func(*args, **kwargs)

            return new_msg_func

        return decorator

    def __call__(self, msg_id, *args, **kwargs):
        if self.msg_callbacks[msg_id]:
            return self.msg_callbacks[msg_id](*args, **kwargs)

        return None

# service_1 = rpc_service()
# 
# @service_1.register_msg(1)
# def test(a, b):
#     print 'test 111111111111111111'
#     print a, b
# 
# test(1, 3)
# 
# print '============================================'
# service_1.msg_callbacks[1]('xx', 'yy')
# 
# service_1(1, 'ttt', 'bbb')
