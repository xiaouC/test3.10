cimport cython
from yy.entity.formulas import g_formulas as fn
from yy.entity.base import cycle
from time import time
from datetime import timedelta, date as datedate
from yy.entity.containers import ListContainer, SetContainer, DictContainer, StoredListContainer, StoredSetContainer, StoredDictContainer


from mail.define import MailBase as PureEntity

cdef convert_bool(b):
    return bool(int(b))



@cython.freelist(1000)
cdef class c_MailBase(object):
    fields_list = PureEntity.fields_list
    fields = PureEntity.fields
    fields_ids_map = PureEntity.fields_ids_map
    store_tag = 'm'

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

        self.__playerID = 0

        self.__title = None

        self.__content = None

        self.__type = 0

        self.__addtime = 0

        self.__addition = DictContainer()

        self.__addition.init_entity(self, 'addition', self.touch_addition)
        self.__isread = False

        self.__isreceived = False

        self.__limitdata = DictContainer()

        self.__limitdata.init_entity(self, 'limitdata', self.touch_limitdata)
        self.__cd = 0

        self.__configID = 0


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
        self.__mailID = None
        self.clear_mailID()
        pass
    cdef public int __playerID
    property playerID:
        def __get__(self):
            return self.__playerID
        def __set__(self, value):
                value = int(value)
                if value != self.__playerID:
                    self.__playerID = value
                    if self._initialized:
                        self.touch_playerID()

    cpdef touch_playerID(self):
        self.dirty_fields.add('playerID')
        pass
    cdef public unicode __title
    property title:
        def __get__(self):
            return self.__title
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__title:
                    self.__title = value
                    if self._initialized:
                        self.touch_title()

    cpdef touch_title(self):
        self.dirty_fields.add('title')
        pass
    cdef public unicode __content
    property content:
        def __get__(self):
            return self.__content
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__content:
                    self.__content = value
                    if self._initialized:
                        self.touch_content()

    cpdef touch_content(self):
        self.dirty_fields.add('content')
        pass
    cdef public int __type
    property type:
        def __get__(self):
            return self.__type
        def __set__(self, value):
                value = int(value)
                if value != self.__type:
                    self.__type = value
                    if self._initialized:
                        self.touch_type()

    cpdef touch_type(self):
        self.dirty_fields.add('type')
        pass
    cdef public int __addtime
    property addtime:
        def __get__(self):
            return self.__addtime
        def __set__(self, value):
                value = int(value)
                if value != self.__addtime:
                    self.__addtime = value
                    if self._initialized:
                        self.touch_addtime()

    cpdef touch_addtime(self):
        self.dirty_fields.add('addtime')
        pass
    cdef public object __addition
    property addition:
        def __get__(self):
            return self.__addition
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'addition', self.touch_addition)
                if value != self.__addition:
                    self.__addition = value
                    if self._initialized:
                        self.touch_addition()

    cpdef touch_addition(self):
        self.dirty_fields.add('addition')
        pass
    cdef public object __isread
    property isread:
        def __get__(self):
            return self.__isread
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__isread:
                    self.__isread = value
                    if self._initialized:
                        self.touch_isread()

    cpdef touch_isread(self):
        self.dirty_fields.add('isread')
        pass
    cdef public object __isreceived
    property isreceived:
        def __get__(self):
            return self.__isreceived
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__isreceived:
                    self.__isreceived = value
                    if self._initialized:
                        self.touch_isreceived()

    cpdef touch_isreceived(self):
        self.dirty_fields.add('isreceived')
        pass
    cdef public object __limitdata
    property limitdata:
        def __get__(self):
            return self.__limitdata
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'limitdata', self.touch_limitdata)
                if value != self.__limitdata:
                    self.__limitdata = value
                    if self._initialized:
                        self.touch_limitdata()

    cpdef touch_limitdata(self):
        self.dirty_fields.add('limitdata')
        pass
    cdef public int __cd
    property cd:
        def __get__(self):
            return self.__cd
        def __set__(self, value):
                value = int(value)
                if value != self.__cd:
                    self.__cd = value
                    if self._initialized:
                        self.touch_cd()

    cpdef touch_cd(self):
        self.dirty_fields.add('cd')
        pass
    cdef public int __configID
    property configID:
        def __get__(self):
            return self.__configID
        def __set__(self, value):
                value = int(value)
                if value != self.__configID:
                    self.__configID = value
                    if self._initialized:
                        self.touch_configID()

    cpdef touch_configID(self):
        self.dirty_fields.add('configID')
        pass

    # formula fields
    cdef public object __mailID
    property mailID:
        def __get__(self):
            if self.__mailID is None:
                value = self.entityID
                self.__mailID = int(value)
            return self.__mailID
        def __set__(self, value):
            assert self.__mailID is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mailID = value
    cpdef clear_mailID(self):
        self.__mailID = None

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
