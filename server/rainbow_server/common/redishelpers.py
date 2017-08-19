# coding: utf-8
from yy.utils import convert_list_to_dict, convert_dict_to_list
from yy.entity.identity import RedisIdentityGenerator


class RHash(object):
    def __init__(self, key, pool):
        self.key = key
        self.pool = pool

    def hgetall(self):
        return convert_list_to_dict(self.pool.execute('hgetall', self.key))

    def hget(self, key):
        return self.pool.execute('hget', self.key, key)

    def hmget(self, *keys):
        return self.pool.execute('hget', self.key, *keys)

    def hset(self, key, value):
        return self.pool.execute('hset', self.key, key, value)

    def hmset(self, **kwargs):
        return self.pool.execute('hmset', self.key, *convert_dict_to_list(kwargs))


class RSet(object):
    def __init__(self, key, pool):
        self.key = key
        self.pool = pool

    def smembers(self):
        return self.pool.execute('smembers', self.key)

    def sadd(self, *args):
        return self.pool.execute('sadd', self.key, *args)

    def srem(self, *args):
        return self.pool.execute('srem', self.key, *args)

    def clear(self):
        return self.pool.execute('del', self.key)


class RString(object):
    def __init__(self, key, pool):
        self.key = key
        self.pool = pool

    def get(self):
        return self.pool.execute('get', self.key)

    def set(self, value):
        return self.pool.execute('set', self.key, value)


class EntityIdentityGenerator(RedisIdentityGenerator):

    def __init__(self, pool, key='identity_generator', initial=1):
        super(EntityIdentityGenerator, self).__init__(pool, key)
        self.initial = max(initial - 1, 0)  # incr will add 1
        self.initialized = False

    def set_initial(self):
        with self.pool.ctx() as conn:
            rs = conn.execute('SETNX', self.key, self.initial)
        self.initialized = True
        return rs

    def gen(self):
        if not self.initialized:
            self.set_initial()
        with self.pool.ctx() as conn:
            return conn.execute('INCR', self.key)

    def get(self):
        if not self.initialized:
            self.set_initial()
        with self.pool.ctx() as conn:
            return conn.execute('GET', self.key)
