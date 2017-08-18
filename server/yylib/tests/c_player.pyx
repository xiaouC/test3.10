cimport cython
from yy.entity.formulas import g_formulas as fn
from yy.entity.base import cycle
from time import time
from datetime import timedelta, date as datedate
from yy.entity.containers import ListContainer, SetContainer, DictContainer, StoredListContainer, StoredSetContainer, StoredDictContainer

from collections import defaultdict

from tests.entity import PlayerBase as PureEntity

cdef convert_bool(b):
    return bool(int(b))



@cython.freelist(1000)
cdef class c_PlayerBase(object):
    fields_list = PureEntity.fields_list
    fields = PureEntity.fields
    fields_ids_map = PureEntity.fields_ids_map
    store_tag = 'p'

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
        self.rank = 0
        self.sp_max = 10
        self.join_time = 0
        self.rank2 = 0
        self.left_count_update_time = 0
        self.depend_on_formula3 = 0
        self.default_dict_value = defaultdict(int)

        self.__natural_score2 = 10

        self.__bool_value = False

        self.__sp_update_time = 0

        self.__worldID = 0

        self.__float_value = 0.0

        self.__some_cd_value = 0

        self.__usedcount_ts = 0

        self.__left_count = 10

        self.__datetime_value = None

        self.__dict_value = DictContainer()

        self.__dict_value.init_entity(self, 'dict_value', self.touch_dict_value)
        self.__list_value_ts = 0

        self.__list_value = ListContainer()

        self.__list_value.init_entity(self, 'list_value', self.touch_list_value)
        self.__string_value = None

        self.__name = None

        self.__set_value = SetContainer()

        self.__set_value.init_entity(self, 'set_value', self.touch_set_value)
        self.__natural_score = 10

        self.__plain = 0

        self.__sp = 0

        self.__persistent = 0

        self.__some_cd_value_ts = 0

        self.__usedcount = 0

        self.__entityID = 0

        self.__createtime = 0


        self.fbs = StoredDictContainer(int_value=False, int_key=True)
        self.fbs.init_entity(self, 'fbs', None)
        self.rewards = StoredSetContainer(int_value=True)
        self.rewards.init_entity(self, 'rewards', None)
        self.mylist = StoredListContainer(int_value=False)
        self.mylist.init_entity(self, 'mylist', None)
        self.fbrewards = StoredSetContainer(int_value=False)
        self.fbrewards.init_entity(self, 'fbrewards', None)
        self.pack = StoredDictContainer(int_value=True, int_key=True)
        self.pack.init_entity(self, 'pack', None)

    def begin_initialize(self):
        self._initialized = False

    def end_initialize(self):
        self._initialized = True

    def load_containers(self):
        self.fbs.load()
        self.rewards.load()
        self.mylist.load()
        self.fbrewards.load()
        self.pack.load()
        pass

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if v is not None:
                setattr(self, k, v)

    def push_command(self, *cmd):
        self.dirty_commands.append(cmd)

    # event fields
    _listeners_formula3 = []
    @classmethod
    def listen_formula3(cls, callback):
        cls._listeners_formula3.append(callback)

    # simple fields
    cdef public int rank
    cdef public int sp_max
    cdef public int join_time
    cdef public int rank2
    cdef public int left_count_update_time
    cdef public int depend_on_formula3
    cdef public object default_dict_value

    # normal fields
    cdef public int __natural_score2
    property natural_score2:
        def __get__(self):
            return self.__natural_score2
        def __set__(self, value):
            value = int(value)
            if value != self.__natural_score2:
                self.__natural_score2 = value
                if self._initialized:
                    self.touch_natural_score2()

    cpdef touch_natural_score2(self):
        self.sync_dirty_fields.add('natural_score2')
        pass
    cdef public object __bool_value
    property bool_value:
        def __get__(self):
            return self.__bool_value
        def __set__(self, value):
            value = convert_bool(value)
            if value != self.__bool_value:
                self.__bool_value = value
                if self._initialized:
                    self.touch_bool_value()

    cpdef touch_bool_value(self):
        self.dirty_fields.add('bool_value')
        pass
    cdef public int __sp_update_time
    property sp_update_time:
        def __get__(self):
            return self.__sp_update_time
        def __set__(self, value):
            value = int(value)
            if value != self.__sp_update_time:
                self.__sp_update_time = value
                if self._initialized:
                    self.touch_sp_update_time()

    cpdef touch_sp_update_time(self):
        self.dirty_fields.add('sp_update_time')
        self.sync_dirty_fields.add('sp_update_time')
        pass
    cdef public int __worldID
    property worldID:
        def __get__(self):
            return self.__worldID
        def __set__(self, value):
            value = int(value)
            if value != self.__worldID:
                self.__worldID = value
                if self._initialized:
                    self.touch_worldID()

    cpdef touch_worldID(self):
        self.dirty_fields.add('worldID')
        pass
    cdef public double __float_value
    property float_value:
        def __get__(self):
            return self.__float_value
        def __set__(self, value):
            value = float(value)
            if value != self.__float_value:
                self.__float_value = value
                if self._initialized:
                    self.touch_float_value()

    cpdef touch_float_value(self):
        self.dirty_fields.add('float_value')
        self.sync_dirty_fields.add('float_value')
        pass
    cdef public int __some_cd_value
    property some_cd_value:
        def __get__(self):
            return self.__some_cd_value
        def __set__(self, value):
            value = int(value)
            if value != self.__some_cd_value:
                self.__some_cd_value = value
                if self._initialized:
                    self.touch_some_cd_value()

    cpdef touch_some_cd_value(self):
        self.dirty_fields.add('some_cd_value')
        self.sync_dirty_fields.add('some_cd_value')
        pass
    cdef public int __usedcount_ts
    property usedcount_ts:
        def __get__(self):
            return self.__usedcount_ts
        def __set__(self, value):
            value = int(value)
            if value != self.__usedcount_ts:
                self.__usedcount_ts = value
                if self._initialized:
                    self.touch_usedcount_ts()

    cpdef touch_usedcount_ts(self):
        self.dirty_fields.add('usedcount_ts')
        pass
    cdef public int __left_count
    property left_count:
        def __get__(self):
            return self.__left_count
        def __set__(self, value):
            value = int(value)
            if value != self.__left_count:
                self.__left_count = value
                if self._initialized:
                    self.touch_left_count()

    cpdef touch_left_count(self):
        self.dirty_fields.add('left_count')
        pass
    cdef public object __datetime_value
    property datetime_value:
        def __get__(self):
            return self.__datetime_value
        def __set__(self, value):
            value = value
            if value != self.__datetime_value:
                self.__datetime_value = value
                if self._initialized:
                    self.touch_datetime_value()

    cpdef touch_datetime_value(self):
        self.dirty_fields.add('datetime_value')
        self.sync_dirty_fields.add('datetime_value')
        pass
    cdef public object __dict_value
    property dict_value:
        def __get__(self):
            return self.__dict_value
        def __set__(self, value):
            value = DictContainer(value)
            value.init_entity(self, 'dict_value', self.touch_dict_value)
            if value != self.__dict_value:
                self.__dict_value = value
                if self._initialized:
                    self.touch_dict_value()

    cpdef touch_dict_value(self):
        self.dirty_fields.add('dict_value')
        self.sync_dirty_fields.add('dict_value')
        pass
    cdef public int __list_value_ts
    property list_value_ts:
        def __get__(self):
            return self.__list_value_ts
        def __set__(self, value):
            value = int(value)
            if value != self.__list_value_ts:
                self.__list_value_ts = value
                if self._initialized:
                    self.touch_list_value_ts()

    cpdef touch_list_value_ts(self):
        self.dirty_fields.add('list_value_ts')
        pass
    cdef public object __list_value
    property list_value:
        def __get__(self):
            return self.__list_value
        def __set__(self, value):
            value = ListContainer(value)
            value.init_entity(self, 'list_value', self.touch_list_value)
            if value != self.__list_value:
                self.__list_value = value
                if self._initialized:
                    self.touch_list_value()

    cpdef touch_list_value(self):
        self.dirty_fields.add('list_value')
        self.sync_dirty_fields.add('list_value')
        pass
    cdef public unicode __string_value
    property string_value:
        def __get__(self):
            return self.__string_value
        def __set__(self, value):
            if isinstance(value, str):
                value = value.decode('utf-8')
            value = value
            if value != self.__string_value:
                self.__string_value = value
                if self._initialized:
                    self.touch_string_value()

    cpdef touch_string_value(self):
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
    cdef public object __set_value
    property set_value:
        def __get__(self):
            return self.__set_value
        def __set__(self, value):
            value = SetContainer(value)
            value.init_entity(self, 'set_value', self.touch_set_value)
            if value != self.__set_value:
                self.__set_value = value
                if self._initialized:
                    self.touch_set_value()

    cpdef touch_set_value(self):
        self.dirty_fields.add('set_value')
        self.sync_dirty_fields.add('set_value')
        pass
    cdef public int __natural_score
    property natural_score:
        def __get__(self):
            return self.__natural_score
        def __set__(self, value):
            value = int(value)
            if value != self.__natural_score:
                self.__natural_score = value
                if self._initialized:
                    self.touch_natural_score()

    cpdef touch_natural_score(self):
        self.sync_dirty_fields.add('natural_score')
        pass
    cdef public int __plain
    property plain:
        def __get__(self):
            return self.__plain
        def __set__(self, value):
            value = int(value)
            if value != self.__plain:
                self.__plain = value
                if self._initialized:
                    self.touch_plain()

    cpdef touch_plain(self):
        self.__integer_formula = None
        self.__formula3 = None
        self.__formula1 = None
        self.__formula2 = None
        self.clear_integer_formula()
        self.clear_formula3()
        self.clear_formula1()
        self.clear_formula2()
        pass
    cdef public int __sp
    property sp:
        def __get__(self):
            return self.__sp
        def __set__(self, value):
            value = int(value)
            if value != self.__sp:
                self.__sp = value
                if self._initialized:
                    self.touch_sp()

    cpdef touch_sp(self):
        self.dirty_fields.add('sp')
        pass
    cdef public int __persistent
    property persistent:
        def __get__(self):
            return self.__persistent
        def __set__(self, value):
            value = int(value)
            if value != self.__persistent:
                self.__persistent = value
                if self._initialized:
                    self.touch_persistent()

    cpdef touch_persistent(self):
        self.dirty_fields.add('persistent')
        self.sync_dirty_fields.add('persistent')
        self.__persist_formula1 = None
        self.__persist_formula2 = None
        self.clear_persist_formula1()
        self.clear_persist_formula2()
        pass
    cdef public int __some_cd_value_ts
    property some_cd_value_ts:
        def __get__(self):
            return self.__some_cd_value_ts
        def __set__(self, value):
            value = int(value)
            if value != self.__some_cd_value_ts:
                self.__some_cd_value_ts = value
                if self._initialized:
                    self.touch_some_cd_value_ts()

    cpdef touch_some_cd_value_ts(self):
        self.dirty_fields.add('some_cd_value_ts')
        pass
    cdef public int __usedcount
    property usedcount:
        def __get__(self):
            return self.__usedcount
        def __set__(self, value):
            value = int(value)
            if value != self.__usedcount:
                self.__usedcount = value
                if self._initialized:
                    self.touch_usedcount()

    cpdef touch_usedcount(self):
        self.dirty_fields.add('usedcount')
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
        self.__natural_ranking2 = None
        self.__natural_ranking = None
        self.clear_natural_ranking2()
        self.clear_natural_ranking()
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

    cdef public object fbs
    cdef public object rewards
    cdef public object mylist
    cdef public object fbrewards
    cdef public object pack

    # formula fields
    cdef public object __formula2
    property formula2:
        def __get__(self):
            if self.__formula2 is None:
                value = self.plain + 2
                self.__formula2 = int(value)
            return self.__formula2
        def __set__(self, value):
            assert self.__formula2 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__formula2 = value
    cpdef clear_formula2(self):
        self.__formula2 = None
        self.set_dirty('formula2')
    cdef public object __formula3
    property formula3:
        def __get__(self):
            if self.__formula3 is None:
                value = self.formula2 + 2
                self.__formula3 = int(value)
            return self.__formula3
        def __set__(self, value):
            assert self.__formula3 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__formula3 = value
    cpdef clear_formula3(self):
        self.__formula3 = None
        for callback in type(self)._listeners_formula3:
            callback(self, None)
    cdef public object __formula1
    property formula1:
        def __get__(self):
            if self.__formula1 is None:
                value = self.plain + 1
                self.__formula1 = int(value)
            return self.__formula1
        def __set__(self, value):
            assert self.__formula1 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__formula1 = value
    cpdef clear_formula1(self):
        self.__formula1 = None
        self.set_sync_dirty('formula1')
    cdef public object __natural_ranking2
    property natural_ranking2:
        def __get__(self):
            if self.__natural_ranking2 is None:
                value = fn.get_challenge_rank2(self.entityID)
                self.__natural_ranking2 = int(value)
            return self.__natural_ranking2
        def __set__(self, value):
            assert self.__natural_ranking2 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__natural_ranking2 = value
    cpdef clear_natural_ranking2(self):
        self.__natural_ranking2 = None
    cdef public object __persist_formula1
    property persist_formula1:
        def __get__(self):
            if self.__persist_formula1 is None:
                value = self.persistent + 1
                self.__persist_formula1 = int(value)
            return self.__persist_formula1
        def __set__(self, value):
            assert self.__persist_formula1 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__persist_formula1 = value
    cpdef clear_persist_formula1(self):
        self.__persist_formula1 = None
    cdef public object __persist_formula2
    property persist_formula2:
        def __get__(self):
            if self.__persist_formula2 is None:
                value = self.persist_formula1 + 1
                self.__persist_formula2 = int(value)
            return self.__persist_formula2
        def __set__(self, value):
            assert self.__persist_formula2 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__persist_formula2 = value
    cpdef clear_persist_formula2(self):
        self.__persist_formula2 = None
    cdef public object __integer_formula
    property integer_formula:
        def __get__(self):
            if self.__integer_formula is None:
                value = self.plain*0.1
                self.__integer_formula = int(value)
            return self.__integer_formula
        def __set__(self, value):
            assert self.__integer_formula is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__integer_formula = value
    cpdef clear_integer_formula(self):
        self.__integer_formula = None
    cdef public object __natural_ranking
    property natural_ranking:
        def __get__(self):
            if self.__natural_ranking is None:
                value = fn.get_challenge_rank(self.entityID)
                self.__natural_ranking = int(value)
            return self.__natural_ranking
        def __set__(self, value):
            assert self.__natural_ranking is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__natural_ranking = value
    cpdef clear_natural_ranking(self):
        self.__natural_ranking = None

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
