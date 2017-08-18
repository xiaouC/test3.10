cimport cython
from yy.entity.formulas import g_formulas as fn
from yy.entity.base import cycle
from time import time
from datetime import timedelta, date as datedate
from yy.entity.containers import ListContainer, SetContainer, DictContainer, StoredListContainer, StoredSetContainer, StoredDictContainer


from tower.define import FloorBase as PureEntity

cdef convert_bool(b):
    return bool(int(b))



@cython.freelist(1000)
cdef class c_FloorBase(object):
    fields_list = PureEntity.fields_list
    fields = PureEntity.fields
    fields_ids_map = PureEntity.fields_ids_map
    store_tag = 'l'

    def cycle(self, *args, **kwargs):
        return cycle(self, *args, **kwargs)

    cdef bint _initialized
    cdef public set dirty_fields
    cdef public set sync_dirty_fields
    cdef public list dirty_commands

    _listeners_on_load = []
    _listeners_on_create = []

    @classmethod
    def listen_on_load(cls, cb):
        cls._listeners_on_load.append(cb)

    @classmethod
    def listen_on_create(cls, cb):
        cls._listeners_on_create.append(cb)

    def __cinit__(self):
        self._initialized = True
        self.dirty_fields = set()
        self.sync_dirty_fields = set()
        self.dirty_commands = []
        # set default value

        self.__entityID = 0

        self.__floor = 0

        self.__limit = 0

        self.__payoff = 0


    def begin_initialize(self):
        self._initialized = False

    def end_initialize(self):
        self._initialized = True

    def load_containers(self):
        pass

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if v is not None:
                setattr(self, k, v)

    def push_command(self, *cmd):
        self.dirty_commands.append(cmd)

    # event fields

    # simple fields

    # normal fields
    cdef public int __entityID
    property entityID:
        def __get__(self):
            return self.__entityID
        def __set__(self, value):
                value = int(value)
                if value != self.__entityID:
                    self.__entityID = value
                    if self._initialized:
                        self.touch_entityID()

    cpdef touch_entityID(self):
        self.dirty_fields.add('entityID')
        pass
    cdef public int __floor
    property floor:
        def __get__(self):
            return self.__floor
        def __set__(self, value):
                value = int(value)
                if value != self.__floor:
                    self.__floor = value
                    if self._initialized:
                        self.touch_floor()

    cpdef touch_floor(self):
        self.dirty_fields.add('floor')
        self.__idx = None
        self.__idx_p = None
        self.__lock = None
        self.clear_idx()
        self.clear_idx_p()
        self.clear_lock()
        pass
    cdef public int __limit
    property limit:
        def __get__(self):
            return self.__limit
        def __set__(self, value):
                value = int(value)
                if value != self.__limit:
                    self.__limit = value
                    if self._initialized:
                        self.touch_limit()

    cpdef touch_limit(self):
        self.dirty_fields.add('limit')
        pass
    cdef public int __payoff
    property payoff:
        def __get__(self):
            return self.__payoff
        def __set__(self, value):
                value = int(value)
                if value != self.__payoff:
                    self.__payoff = value
                    if self._initialized:
                        self.touch_payoff()

    cpdef touch_payoff(self):
        self.dirty_fields.add('payoff')
        pass

    # formula fields
    cdef public object __idx
    property idx:
        def __get__(self):
            if self.__idx is None:
                value = fn.get_idx(self.floor)
                self.__idx = value
            return self.__idx
        def __set__(self, value):
            assert self.__idx is None, 'can only set formula attribute when initialize'
            value = value
            self.__idx = value
    cpdef clear_idx(self):
        self.__idx = None
    cdef public object __idx_p
    property idx_p:
        def __get__(self):
            if self.__idx_p is None:
                value = fn.get_idx_p(self.floor)
                self.__idx_p = value
            return self.__idx_p
        def __set__(self, value):
            assert self.__idx_p is None, 'can only set formula attribute when initialize'
            value = value
            self.__idx_p = value
    cpdef clear_idx_p(self):
        self.__idx_p = None
    cdef public object __lock
    property lock:
        def __get__(self):
            if self.__lock is None:
                value = fn.get_lock(self.floor)
                self.__lock = value
            return self.__lock
        def __set__(self, value):
            assert self.__lock is None, 'can only set formula attribute when initialize'
            value = value
            self.__lock = value
    cpdef clear_lock(self):
        self.__lock = None

    cpdef has_dirty(self):
        return bool(self.dirty_fields)

    cpdef set_dirty(self, name):
        self.dirty_fields.add(name)

    cpdef set get_dirty(self):
        return self.dirty_fields

    cpdef set pop_dirty(self):
        cdef set fs = self.dirty_fields
        self.dirty_fields = set()
        return fs

    cpdef is_dirty(self, name):
        return name in self.dirty_fields

    cpdef remove_dirty(self, fields):
        for f in fields:
            try:
                self.dirty_fields.remove(f)
            except KeyError:
                pass
    cpdef has_sync_dirty(self):
        return bool(self.sync_dirty_fields)

    cpdef set_sync_dirty(self, name):
        self.sync_dirty_fields.add(name)

    cpdef set get_sync_dirty(self):
        return self.sync_dirty_fields

    cpdef set pop_sync_dirty(self):
        cdef set fs = self.sync_dirty_fields
        self.sync_dirty_fields = set()
        return fs

    cpdef is_sync_dirty(self, name):
        return name in self.sync_dirty_fields

    cpdef remove_sync_dirty(self, fields):
        for f in fields:
            try:
                self.sync_dirty_fields.remove(f)
            except KeyError:
                pass

    cpdef list pop_dirty_values(self):
        cdef list result = []
        cdef dict fields = type(self).fields
        for name in self.pop_dirty():
            try:
                f = fields[name]
            except KeyError:
                continue
            value = getattr(self, name)
            if f.encoder is not None:
                value = f.encoder(value)
            result.append((name, value))
        return result

    cpdef list pop_sync_dirty_values(self):
        cdef dict fields = self.fields
        cdef list result = []
        cdef int now = 0
        for name in self.pop_sync_dirty():
            value = getattr(self, name)
            f = fields[name]
            if f.syncTimeout:
                if now == 0:
                    now = time()
                value = value - now
            elif f.encoder is not None:
                value = f.encoder(value)
            result.append((name, value))
        return result

    cycle = cycle

    @classmethod
    def getAttributeByID(cls, id):
        return cls.fields_ids_map[id]

    @classmethod
    def getAttributeIDByName(cls, name):
        return cls.fields[name].id

    @classmethod
    def expend_fields(cls, fields):
        result = set()
        for name in fields:
            f = cls.fields[name]
            if f.formula and not f.save:
                for ff in f.depend_set_save:
                    result.add(ff.name)
            else:
                result.add(name)
        return result
