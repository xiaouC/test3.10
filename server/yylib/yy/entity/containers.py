from yy.utils import convert_list_to_dict, convert_dict_to_list


class ListContainer(list):
    def init_entity(self, entity, name, touch_handler):
        self.touch_handler = touch_handler

    def append(self, v):
        list.append(self, v)
        self.touch_handler()

    def remove(self, v):
        list.remove(self, v)
        self.touch_handler()

    def insert(self, pos, v):
        list.insert(self, pos, v)
        self.touch_handler()

    def sort(self, *args, **kwargs):
        list.sort(self, *args, **kwargs)
        self.touch_handler()

    def reverse(self):
        list.reverse(self)
        self.touch_handler()

    def extend(self):
        list.extend(self)
        self.touch_handler()

    def pop(self, *args):
        result = list.pop(*args)
        self.touch_handler()
        return result

    def __setitem__(self, index, value):
        list.__setitem__(self, index, value)
        self.touch_handler()


class DictContainer(dict):
    def init_entity(self, entity, name, touch_handler):
        self.touch_handler = touch_handler

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.touch_handler()

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.touch_handler()

    def setdefault(self, k, d=None):
        result = dict.setdefault(self, k, d)
        self.touch_handler()
        return result

    def update(self, *args, **kwargs):
        dict.update(self, *args, **kwargs)
        self.touch_handler()

    def pop(self, *args):
        result = dict.pop(self, *args)
        self.touch_handler()
        return result

    def clear(self):
        dict.clear(self)
        self.touch_handler()

    def popitem(self):
        result = dict.popitem(self)
        self.touch_handler()
        return result


class SetContainer(set):
    def init_entity(self, entity, name, touch_handler):
        self.touch_handler = touch_handler

    def add(self, value):
        set.add(self, value)
        self.touch_handler()

    def remove(self, value):
        set.remove(self, value)
        self.touch_handler()

    def update(self, *args, **kwargs):
        set.update(self, *args, **kwargs)
        self.touch_handler()

    def clear(self):
        set.clear(self)
        self.touch_handler()


class StoredListContainer(list):
    def __init__(self, int_value=False):
        list.__init__(self)
        self.int_value = int_value

    def init_entity(self, entity, name, touch_handler):
        self.entity = entity
        self.name = name
        self.pool = entity.pool
        self.touch_handler = touch_handler
        field = entity.fields[name]
        self.encoder = getattr(field, 'encoder') or (lambda s: s)
        self.decoder = getattr(field, 'decoder') or (lambda s: s)

    @property
    def store_key(self):
        return '%s_%s' % (self.name, self.entity.make_key())

    def load(self):
        for item in self.pool.execute('LRANGE', self.store_key, 0, -1):
            if self.int_value:
                item = int(item)
            v = self.decoder(item)
            list.append(self, v)

        self.touch_handler()

    def __setitem__(self, index, value):
        list.__setitem__(self, index, value)
        value = self.encoder(value)
        self.entity.push_command('LSET', self.store_key, index, value)
        self.touch_handler()

    def append(self, value):
        list.append(self, value)
        value = self.encoder(value)
        self.entity.push_command('RPUSH', self.store_key, value)
        self.touch_handler()

    def appendleft(self, value):
        list.insert(self, 0, value)
        value = self.encoder(value)
        self.entity.push_command('LPUSH', self.store_key, value)
        self.touch_handler()

    def remove(self, value):
        list.remove(self, value)
        value = self.encoder(value)
        self.entity.push_command('LREM', self.store_key, 0, value)
        self.touch_handler()

    def lpop(self):
        result = list.pop(self, 0)
        self.entity.push_command('LPOP', self.store_key)
        self.touch_handler()
        return result

    def rpop(self):
        result = list.pop(self)
        self.entity.push_command('RPOP', self.store_key)
        self.touch_handler()
        return result

    def extend(self, l):
        list.extend(self, l)
        l = map(self.encoder, l)
        self.entity.push_command('RPUSH', self.store_key, *l)
        self.touch_handler()

    def ltrim(self, i, j):
        while i < 0:
            i += len(self)
        while j < 0:
            j += len(self)
        if i > j:
            return self.clear()
        copy = list(self)
        slice = self[i:((j) or None)]
        for v in copy:  # remove all
            list.remove(self, v)
        for v in slice:
            list.append(self, v)
        with self.entity.pool.ctx() as conn:
            size = int(conn.execute("LLEN", self.store_key) or 0)
            if i > 0:
                self.entity.push_command(
                    'QTRIM_FRONT', self.store_key, i)
            tail = size - j + 1
            if tail > 0:
                self.entity.push_command(
                    'QTRIM_BACK', self.store_key, tail)

    def insert(self, pos, v):
        raise NotImplementedError

    def pop(self, index=-1):
        raise NotImplementedError

    def reverse(self):
        raise NotImplementedError

    def sort(self, *args, **kwargs):
        raise NotImplementedError

    def clear(self):
        del self[:]
        self.entity.push_command('QCLEAR', self.store_key)
        self.touch_handler()


class StoredDictContainer(dict):
    def __init__(self, int_key=False, int_value=False):
        dict.__init__(self)
        self.int_key = int_key
        self.int_value = int_value

    def init_entity(self, entity, name, touch_handler):
        self.entity = entity
        self.name = name
        self.pool = entity.pool
        self.touch_handler = touch_handler
        field = entity.fields[name]
        self.encoder = getattr(field, 'encoder') or (lambda s: s)
        self.decoder = getattr(field, 'decoder') or (lambda s: s)

    @property
    def store_key(self):
        return '%s_%s' % (self.name, self.entity.make_key())

    def load(self):
        k = None
        for item in self.pool.execute('HGETALL', self.store_key):
            if k is None:
                k = item
            else:
                if self.int_key:
                    k = int(k)
                if self.int_value:
                    item = int(item)
                v = self.decoder(item)
                dict.__setitem__(self, k, v)
                k = None
        self.touch_handler()

    def __setitem__(self, k, v):
        dict.__setitem__(self, k, v)
        v = self.encoder(v)
        self.entity.push_command('HSET', self.store_key, k, v)
        self.touch_handler()

    def __delitem__(self, k):
        dict.__delitem__(self, k)
        self.entity.push_command('HDEL', self.store_key, k)
        self.touch_handler()

    def pop(self, k, *args):
        result = dict.pop(self, k, *args)
        self.entity.push_command('HDEL', self.store_key, k)
        self.touch_handler()
        return result

    def update(self, *args, **kwargs):
        dict.update(self, *args, **kwargs)
        data = {}
        if args:
            e = args[0]
            if hasattr(e, 'items'):
                data = e
            else:
                data = convert_list_to_dict(e)
        data.update(kwargs)
        for k, v in data.items():
            data[k] = self.encoder(v)
        values = convert_dict_to_list(data)
        self.entity.push_command('HMSET', self.store_key, *values)
        self.touch_handler()

    def popitem(self):
        raise NotImplementedError

    def setdefault(self, k, d=None):
        raise NotImplementedError

    def clear(self):
        dict.clear(self)
        self.entity.push_command('HCLEAR', self.store_key)
        self.touch_handler()


class StoredSetContainer(set):
    def __init__(self, int_value=False):
        set.__init__(self)
        self.int_value = int_value

    def init_entity(self, entity, name, touch_handler):
        self.entity = entity
        self.name = name
        self.pool = entity.pool
        self.touch_handler = touch_handler
        field = entity.fields[name]
        self.encoder = getattr(field, 'encoder') or (lambda s: s)
        self.decoder = getattr(field, 'decoder') or (lambda s: s)

    @property
    def store_key(self):
        return '%s_%s' % (self.name, self.entity.make_key())

    def load(self):
        for item in self.pool.execute('HKEYS', self.store_key):
            if self.int_value:
                item = int(item)
            v = self.decoder(item)
            set.add(self, v)
        self.touch_handler()

    def add(self, v):
        set.add(self, v)
        v = self.encoder(v)
        self.entity.push_command('HSET', self.store_key, v, "")
        self.touch_handler()

    def remove(self, v):
        set.remove(self, v)
        v = self.encoder(v)
        self.entity.push_command('HDEL', self.store_key, v)
        self.touch_handler()

    def clear(self):
        set.clear(self)
        self.entity.push_command('HCLEAR', self.store_key)
        self.touch_handler()

    def pop(self):
        raise NotImplementedError


# class StoredSetContainer(set):
#     def __init__(self, int_value=False):
#         set.__init__(self)
#         self.int_value = int_value
#
#     def init_entity(self, entity, name, touch_handler):
#         self.entity = entity
#         self.name = name
#         self.pool = entity.pool
#         self.touch_handler = touch_handler
#         field = entity.fields[name]
#         self.encoder = getattr(field, 'encoder') or (lambda s:s)
#         self.decoder = getattr(field, 'decoder') or (lambda s:s)
#
#     @property
#     def store_key(self):
#         return '%s_%s'%(self.name, self.entity.make_key())
#
#     def load(self):
#         import ipdb; ipdb.set_trace()
#         for item in self.pool.execute('SMEMBERS', self.store_key):
#             if self.int_value:
#                 item = int(item)
#             v = self.decoder(item)
#             set.add(self, v)
#         self.touch_handler()
#
#     def add(self, v):
#         set.add(self, v)
#         v = self.encoder(v)
#         self.entity.push_command('SADD', self.store_key, v)
#         self.touch_handler()
#
#     def remove(self, v):
#         set.remove(self, v)
#         v = self.encoder(v)
#         self.entity.push_command('SREM', self.store_key, v)
#         self.touch_handler()
#
#     def clear(self):
#         set.clear(self)
#         self.entity.push_command('DEL', self.store_key)
#         self.touch_handler()
#
#     def pop(self):
#         raise NotImplementedError
