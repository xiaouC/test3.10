# coding: utf-8
from yy.message.header import clean_msgtype

class MethodNotFound(Exception):
    pass

class MethodKeyCollide(Exception):
    pass

class MetaRpcService(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(MetaRpcService, cls).__new__
        new_cls = super_new(cls, name, bases, attrs)

        _method_map = {}

        # 处理继承
        parents = [b for b in bases if isinstance(b, MetaRpcService)]
        if not parents:
            # RpcService itself
            return new_cls
        for p in parents[::-1]: # reverse
            for k in p._method_map:
                if k in _method_map:
                    raise MethodKeyCollide()
                _method_map[k] = p._method_map[k]

        for name, value in attrs.items():
            if callable(value) and hasattr(value, '_rpc_method_key'):
                if value._rpc_method_key in _method_map:
                    raise MethodKeyCollide(value._rpc_method_key)
                _method_map[value._rpc_method_key] = value

        new_cls._method_map = _method_map
        return new_cls

def rpcmethod(key):
    def decorator(func):
        func._rpc_method_key = key
        return func
    return decorator

class RpcService(object):
    _method_map = {}
    __metaclass__ = MetaRpcService

    def rpccall(self, key, *args, **kwargs):
        method_map = self.__class__._method_map
        raw_key = key
        key = clean_msgtype(key)
        if key in method_map:
            result = method_map[key](self, raw_key, *args, **kwargs)
            return result
        else:
            return self.method_not_found(key, *args, **kwargs)

    def method_not_found(self, key, *args, **kwargs):
        'can be overwritten by subclass'
        raise MethodNotFound('%s (%s,%s)'%(key, args, kwargs))