cimport cython
from yy.entity.formulas import g_formulas as fn
from yy.entity.base import cycle
from time import time
from datetime import timedelta, date as datedate
from yy.entity.containers import ListContainer, SetContainer, DictContainer, StoredListContainer, StoredSetContainer, StoredDictContainer


from user.define import UserBase as PureEntity

cdef convert_bool(b):
    return bool(int(b))



@cython.freelist(1000)
cdef class c_UserBase(object):
    fields_list = PureEntity.fields_list
    fields = PureEntity.fields
    fields_ids_map = PureEntity.fields_ids_map
    store_tag = 'u'

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

        self.__username = None

        self.__password = None

        self.__imsi = None

        self.__createtime = None

        self.__roles = StoredDictContainer(int_value=False, int_key=True)

        self.__roles.init_entity(self, 'roles', self.touch_roles)
        self.__entityID = 0

        self.__blocktime = 0

        self.__lastserver = 0

        self.__username_alias = None

        self.__lock_device = None

        self.__channel = None

        self.__back_reward_received = False

        self.__back_level_reward_received = False


    def begin_initialize(self):
        self._initialized = False

    def end_initialize(self):
        self._initialized = True

    def load_containers(self):
        self.roles.load()
        pass

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if v is not None:
                setattr(self, k, v)

    def push_command(self, *cmd):
        self.dirty_commands.append(cmd)

    # event fields
    _listeners_username = []
    @classmethod
    def listen_username(cls, callback):
        cls._listeners_username.append(callback)

    # simple fields

    # normal fields
    cdef public unicode __username
    property username:
        def __get__(self):
            return self.__username
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__username:
                    if self._initialized:
                        for callback in type(self)._listeners_username:
                            callback(self, value)
                    self.__username = value
                    if self._initialized:
                        self.touch_username()

    cpdef touch_username(self):
        self.dirty_fields.add('username')
        if self._initialized:
            value = self.username
            for callback in type(self)._listeners_username:
                callback(self, value)
        pass
    cdef public unicode __password
    property password:
        def __get__(self):
            return self.__password
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__password:
                    self.__password = value
                    if self._initialized:
                        self.touch_password()

    cpdef touch_password(self):
        self.dirty_fields.add('password')
        pass
    cdef public unicode __imsi
    property imsi:
        def __get__(self):
            return self.__imsi
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__imsi:
                    self.__imsi = value
                    if self._initialized:
                        self.touch_imsi()

    cpdef touch_imsi(self):
        self.dirty_fields.add('imsi')
        pass
    cdef public object __createtime
    property createtime:
        def __get__(self):
            return self.__createtime
        def __set__(self, value):
                value = value
                if value != self.__createtime:
                    self.__createtime = value
                    if self._initialized:
                        self.touch_createtime()

    cpdef touch_createtime(self):
        self.dirty_fields.add('createtime')
        pass
    cdef public object __roles
    property roles:
        def __get__(self):
            return self.__roles
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_roles(self):
        pass
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
        self.__userID = None
        self.clear_userID()
        pass
    cdef public int __blocktime
    property blocktime:
        def __get__(self):
            return self.__blocktime
        def __set__(self, value):
                value = int(value)
                if value != self.__blocktime:
                    self.__blocktime = value
                    if self._initialized:
                        self.touch_blocktime()

    cpdef touch_blocktime(self):
        self.dirty_fields.add('blocktime')
        pass
    cdef public int __lastserver
    property lastserver:
        def __get__(self):
            return self.__lastserver
        def __set__(self, value):
                value = int(value)
                if value != self.__lastserver:
                    self.__lastserver = value
                    if self._initialized:
                        self.touch_lastserver()

    cpdef touch_lastserver(self):
        self.dirty_fields.add('lastserver')
        pass
    cdef public unicode __username_alias
    property username_alias:
        def __get__(self):
            return self.__username_alias
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__username_alias:
                    self.__username_alias = value
                    if self._initialized:
                        self.touch_username_alias()

    cpdef touch_username_alias(self):
        self.dirty_fields.add('username_alias')
        pass
    cdef public unicode __lock_device
    property lock_device:
        def __get__(self):
            return self.__lock_device
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__lock_device:
                    self.__lock_device = value
                    if self._initialized:
                        self.touch_lock_device()

    cpdef touch_lock_device(self):
        self.dirty_fields.add('lock_device')
        pass
    cdef public unicode __channel
    property channel:
        def __get__(self):
            return self.__channel
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__channel:
                    self.__channel = value
                    if self._initialized:
                        self.touch_channel()

    cpdef touch_channel(self):
        self.dirty_fields.add('channel')
        pass
    cdef public object __back_reward_received
    property back_reward_received:
        def __get__(self):
            return self.__back_reward_received
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__back_reward_received:
                    self.__back_reward_received = value
                    if self._initialized:
                        self.touch_back_reward_received()

    cpdef touch_back_reward_received(self):
        self.dirty_fields.add('back_reward_received')
        pass
    cdef public object __back_level_reward_received
    property back_level_reward_received:
        def __get__(self):
            return self.__back_level_reward_received
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__back_level_reward_received:
                    self.__back_level_reward_received = value
                    if self._initialized:
                        self.touch_back_level_reward_received()

    cpdef touch_back_level_reward_received(self):
        self.dirty_fields.add('back_level_reward_received')
        pass

    # formula fields
    cdef public object __userID
    property userID:
        def __get__(self):
            if self.__userID is None:
                value = self.entityID
                self.__userID = int(value)
            return self.__userID
        def __set__(self, value):
            assert self.__userID is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__userID = value
    cpdef clear_userID(self):
        self.__userID = None

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
