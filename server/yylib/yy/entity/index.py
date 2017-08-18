from yy.utils import iter_bitmap

class DuplicateIndexException(Exception):
    def __init__(self, key, entityID, value):
        self.key = key
        self.entityID = entityID
        self.value = value

    def __unicode__(self):
        return u'value is duplicate %s %s %s' % (self.key, self.value, self.entityID)

class UniqueIndexing(object):
    def __init__(self, key, pool):
        self.key = key
        self.pool = pool

    def unregister(self, value):
        self.pool.execute('HDEL', self.key, value)

    def register(self, entityID, value):
        if not bool(self.pool.execute('HSETNX', self.key, value, entityID)):
            raise DuplicateIndexException(self.key, entityID, value)

    def update(self, entityID, value):
        return bool(self.pool.execute('HSET', self.key, value, entityID))

    def get_pk(self, value):
        rsp = self.pool.execute('HGET', self.key, value)
        if rsp is not None:
            return int(rsp)

    def exists(self, value):
        return bool(self.pool.execute('HEXISTS', self.key, value))

    def clear_raw(self):
        self.pool.execute('DEL', self.key)

class BitmapIndexing(object):
    def __init__(self, prefix, pool):
        self.key_tpl = '%s{%%s}' % prefix
        self.pool = pool

    def register(self, entityID, value):
        key = self.key_tpl % value
        self.pool.execute('SETBIT', key, entityID, 1)

    def unregister(self, entityID, value):
        key = self.key_tpl % value
        self.pool.execute('SETBIT', key, entityID, 0)

    def check(self, entityID, value):
        key = self.key_tpl % value
        return bool(self.pool.execute('GETBIT', key, entityID))

    def getall(self, value):
        key = self.key_tpl % value
        bm = self.pool.execute('GET', key)
        if bm:
            return iter_bitmap(bm)

class SortedIndexing(object):
    def __init__(self, key, pool):
        self.key = key
        self.pool = pool

    def unregister(self, entityID):
        self.pool.execute('ZREM', self.key, entityID)

    def register(self, entityID, score):
        self.pool.execute('ZADD', self.key, score, entityID)

    def get_by_range(self, start='-inf', end='+inf'):
        return map(int, self.pool.execute('zrangebyscore', self.key, start, end))

    def clear_raw(self):
        self.pool.execute('DEL', self.key)

class SetIndexing(object):
    def __init__(self, key, pool):
        self.key = key
        self.pool = pool

    def unregister(self, *members):
        self.pool.execute('SREM', self.key, *members)

    def register(self, *members):
        self.pool.execute('SADD', self.key, *members)

    def exists(self, member):
        return bool(self.pool.execute('SISMEMBER', self.key,member))

    def getall(self):
        return self.pool.execute('SMEMBERS', self.key)

    def count(self):
        return int(self.pool.execute('SCARD', self.key) or 0)

    def randmembers(self, count=1):
        return self.pool.execute('SRANDMEMBER', self.key, count)

    def clear_raw(self):
        self.pool.execute('DEL', self.key)
