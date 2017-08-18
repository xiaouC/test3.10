cimport cython
from yy.entity.formulas import g_formulas as fn
from yy.entity.base import cycle
from time import time
from datetime import timedelta, date as datedate
from yy.entity.containers import ListContainer, SetContainer, DictContainer, StoredListContainer, StoredSetContainer, StoredDictContainer


from faction.define import FactionBase as PureEntity

cdef convert_bool(b):
    return bool(int(b))



@cython.freelist(1000)
cdef class c_FactionBase(object):
    fields_list = PureEntity.fields_list
    fields = PureEntity.fields
    fields_ids_map = PureEntity.fields_ids_map
    store_tag = 'f'

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
        self.level = 0

        self.__entityID = 0

        self.__name = None

        self.__totalfp = 0

        self.__todayfp_ts = 0

        self.__todayfp = 0

        self.__memberset = SetContainer()

        self.__memberset.init_entity(self, 'memberset', self.touch_memberset)
        self.__applyset = SetContainer()

        self.__applyset.init_entity(self, 'applyset', self.touch_applyset)
        self.__inviteset = SetContainer()

        self.__inviteset.init_entity(self, 'inviteset', self.touch_inviteset)
        self.__mode = 1

        self.__notice = None

        self.__createtime = 0

        self.__strengthen_hp_level = 0

        self.__strengthen_at_level = 0

        self.__strengthen_ct_level = 0

        self.__strengthen_df_level = 0

        self.__leaderID = 0

        self.__dflag = False

        self.__mall_products = SetContainer()

        self.__mall_products.init_entity(self, 'mall_products', self.touch_mall_products)
        self.__faction_treasure = 0

        self.__city_top_member = DictContainer()

        self.__city_top_member.init_entity(self, 'city_top_member', self.touch_city_top_member)
        self.__city_top_member_kills = 0


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
    cdef public int level

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
        self.__factionID = None
        self.clear_factionID()
        pass
    cdef public unicode __name
    property name:
        def __get__(self):
            return self.__name
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__name:
                    self.__name = value
                    if self._initialized:
                        self.touch_name()

    cpdef touch_name(self):
        self.dirty_fields.add('name')
        pass
    cdef public int __totalfp
    property totalfp:
        def __get__(self):
            return self.__totalfp
        def __set__(self, value):
                value = int(value)
                if value != self.__totalfp:
                    self.__totalfp = value
                    if self._initialized:
                        self.touch_totalfp()

    cpdef touch_totalfp(self):
        self.dirty_fields.add('totalfp')
        pass
    cdef public int __todayfp_ts
    property todayfp_ts:
        def __get__(self):
            return self.__todayfp_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__todayfp_ts:
                    self.__todayfp_ts = value
                    if self._initialized:
                        self.touch_todayfp_ts()

    cpdef touch_todayfp_ts(self):
        self.dirty_fields.add('todayfp_ts')
        pass
    cdef public int __todayfp
    property todayfp:
        def __get__(self):
            return self.__todayfp
        def __set__(self, value):
                value = int(value)
                if value != self.__todayfp:
                    self.__todayfp = value
                    if self._initialized:
                        self.touch_todayfp()

    cpdef touch_todayfp(self):
        self.dirty_fields.add('todayfp')
        pass
    cdef public object __memberset
    property memberset:
        def __get__(self):
            return self.__memberset
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'memberset', self.touch_memberset)
                if value != self.__memberset:
                    self.__memberset = value
                    if self._initialized:
                        self.touch_memberset()

    cpdef touch_memberset(self):
        self.dirty_fields.add('memberset')
        pass
    cdef public object __applyset
    property applyset:
        def __get__(self):
            return self.__applyset
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'applyset', self.touch_applyset)
                if value != self.__applyset:
                    self.__applyset = value
                    if self._initialized:
                        self.touch_applyset()

    cpdef touch_applyset(self):
        self.dirty_fields.add('applyset')
        pass
    cdef public object __inviteset
    property inviteset:
        def __get__(self):
            return self.__inviteset
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'inviteset', self.touch_inviteset)
                if value != self.__inviteset:
                    self.__inviteset = value
                    if self._initialized:
                        self.touch_inviteset()

    cpdef touch_inviteset(self):
        self.dirty_fields.add('inviteset')
        pass
    cdef public int __mode
    property mode:
        def __get__(self):
            return self.__mode
        def __set__(self, value):
                value = int(value)
                if value != self.__mode:
                    self.__mode = value
                    if self._initialized:
                        self.touch_mode()

    cpdef touch_mode(self):
        self.dirty_fields.add('mode')
        pass
    cdef public unicode __notice
    property notice:
        def __get__(self):
            return self.__notice
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__notice:
                    self.__notice = value
                    if self._initialized:
                        self.touch_notice()

    cpdef touch_notice(self):
        self.dirty_fields.add('notice')
        pass
    cdef public int __createtime
    property createtime:
        def __get__(self):
            return self.__createtime
        def __set__(self, value):
                value = int(value)
                if value != self.__createtime:
                    self.__createtime = value
                    if self._initialized:
                        self.touch_createtime()

    cpdef touch_createtime(self):
        self.dirty_fields.add('createtime')
        pass
    cdef public int __strengthen_hp_level
    property strengthen_hp_level:
        def __get__(self):
            return self.__strengthen_hp_level
        def __set__(self, value):
                value = int(value)
                if value != self.__strengthen_hp_level:
                    self.__strengthen_hp_level = value
                    if self._initialized:
                        self.touch_strengthen_hp_level()

    cpdef touch_strengthen_hp_level(self):
        self.dirty_fields.add('strengthen_hp_level')
        pass
    cdef public int __strengthen_at_level
    property strengthen_at_level:
        def __get__(self):
            return self.__strengthen_at_level
        def __set__(self, value):
                value = int(value)
                if value != self.__strengthen_at_level:
                    self.__strengthen_at_level = value
                    if self._initialized:
                        self.touch_strengthen_at_level()

    cpdef touch_strengthen_at_level(self):
        self.dirty_fields.add('strengthen_at_level')
        pass
    cdef public int __strengthen_ct_level
    property strengthen_ct_level:
        def __get__(self):
            return self.__strengthen_ct_level
        def __set__(self, value):
                value = int(value)
                if value != self.__strengthen_ct_level:
                    self.__strengthen_ct_level = value
                    if self._initialized:
                        self.touch_strengthen_ct_level()

    cpdef touch_strengthen_ct_level(self):
        self.dirty_fields.add('strengthen_ct_level')
        pass
    cdef public int __strengthen_df_level
    property strengthen_df_level:
        def __get__(self):
            return self.__strengthen_df_level
        def __set__(self, value):
                value = int(value)
                if value != self.__strengthen_df_level:
                    self.__strengthen_df_level = value
                    if self._initialized:
                        self.touch_strengthen_df_level()

    cpdef touch_strengthen_df_level(self):
        self.dirty_fields.add('strengthen_df_level')
        pass
    cdef public int __leaderID
    property leaderID:
        def __get__(self):
            return self.__leaderID
        def __set__(self, value):
                value = int(value)
                if value != self.__leaderID:
                    self.__leaderID = value
                    if self._initialized:
                        self.touch_leaderID()

    cpdef touch_leaderID(self):
        self.dirty_fields.add('leaderID')
        pass
    cdef public object __dflag
    property dflag:
        def __get__(self):
            return self.__dflag
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__dflag:
                    self.__dflag = value
                    if self._initialized:
                        self.touch_dflag()

    cpdef touch_dflag(self):
        self.dirty_fields.add('dflag')
        pass
    cdef public object __mall_products
    property mall_products:
        def __get__(self):
            return self.__mall_products
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'mall_products', self.touch_mall_products)
                if value != self.__mall_products:
                    self.__mall_products = value
                    if self._initialized:
                        self.touch_mall_products()

    cpdef touch_mall_products(self):
        self.dirty_fields.add('mall_products')
        pass
    cdef public int __faction_treasure
    property faction_treasure:
        def __get__(self):
            return self.__faction_treasure
        def __set__(self, value):
                value = int(value)
                if value != self.__faction_treasure:
                    self.__faction_treasure = value
                    if self._initialized:
                        self.touch_faction_treasure()

    cpdef touch_faction_treasure(self):
        self.dirty_fields.add('faction_treasure')
        pass
    cdef public object __city_top_member
    property city_top_member:
        def __get__(self):
            return self.__city_top_member
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'city_top_member', self.touch_city_top_member)
                if value != self.__city_top_member:
                    self.__city_top_member = value
                    if self._initialized:
                        self.touch_city_top_member()

    cpdef touch_city_top_member(self):
        self.dirty_fields.add('city_top_member')
        pass
    cdef public int __city_top_member_kills
    property city_top_member_kills:
        def __get__(self):
            return self.__city_top_member_kills
        def __set__(self, value):
                value = int(value)
                if value != self.__city_top_member_kills:
                    self.__city_top_member_kills = value
                    if self._initialized:
                        self.touch_city_top_member_kills()

    cpdef touch_city_top_member_kills(self):
        self.dirty_fields.add('city_top_member_kills')
        pass

    # formula fields
    cdef public object __factionID
    property factionID:
        def __get__(self):
            if self.__factionID is None:
                value = self.entityID
                self.__factionID = int(value)
            return self.__factionID
        def __set__(self, value):
            assert self.__factionID is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__factionID = value
    cpdef clear_factionID(self):
        self.__factionID = None

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
