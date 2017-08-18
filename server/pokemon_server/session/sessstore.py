from common.redishelpers import RHash


class SessionStore(object):
    def __init__(self, pool, sid, key_prefix='sid'):
        self.key = 'sid{%s}' % sid
        self.rhash = RHash(self.key, pool)
        self.pool = pool
        self._data = None

    @property
    def data(self):
        if self._data is not None:
            return self._data
        return self.load()

    def load(self):
        self._data = self.rhash.hgetall()
        return self._data

    def __setitem__(self, name, value):
        self.data[name] = value

    def __getitem__(self, name):
        return self.data[name]

    def get(self, name):
        return self.data.get(name)

    def save(self):
        self.rhash.hmset(**self.data)

    def set_uid(self, uid):
        self['uid'] = uid

    def get_uid(self):
        n = self.get('uid')
        if n != None:
            return int(n)
        else:
            return n

    uid = property(get_uid, set_uid)
