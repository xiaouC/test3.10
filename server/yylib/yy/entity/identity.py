class BaseIdentityGenerator(object):
    def gen(self):
        raise NotImplementedError

    def view(self):
        raise NotImplementedError

    def set_next_id(self, n):
        raise NotImplementedError

class MemoryIdentityGenerator(BaseIdentityGenerator):
    def __init__(self, init):
        self._next_id = init

    def gen(self):
        new_id = self._next_id
        self._next_id += 1
        return new_id

    def view(self):
        return self._next_id

    def set_next_id(self, n):
        self._next_id = n

class RedisIdentityGenerator(BaseIdentityGenerator):
    def __init__(self, pool, key='identity_generator'):
        self.pool = pool
        self.key = key

    def gen(self):
        with self.pool.ctx() as conn:
            return conn.execute('INCR', self.key)

    def view(self):
        result = self.pool.execute('GET', self.key)
        if result is not None:
            return int(result) + 1
        else:
            return 1

    def set_next_id(self, n):
        self.pool.execute('SET', self.key, n-1)
