cimport cython
from yy.entity.formulas import g_formulas as fn
from yy.entity.base import cycle
from time import time
from datetime import timedelta, date as datedate
from yy.entity.containers import ListContainer, SetContainer, DictContainer, StoredListContainer, StoredSetContainer, StoredDictContainer


from group.define import GroupBase as PureEntity

cdef convert_bool(b):
    return bool(int(b))



@cython.freelist(1000)
cdef class c_GroupBase(object):
    fields_list = PureEntity.fields_list
    fields = PureEntity.fields
    fields_ids_map = PureEntity.fields_ids_map
    store_tag = 'g'

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

        self.__name = None

        self.__applys = StoredDictContainer(int_value=False, int_key=True)

        self.__applys.init_entity(self, 'applys', self.touch_applys)
        self.__members = StoredDictContainer(int_value=False, int_key=True)

        self.__members.init_entity(self, 'members', self.touch_members)
        self.__leaderID = 0

        self.__invites = StoredSetContainer(int_value=True)

        self.__invites.init_entity(self, 'invites', self.touch_invites)
        self.__leader_lastlogin = None

        self.__gve_joineds = StoredListContainer(int_value=True)

        self.__gve_joineds.init_entity(self, 'gve_joineds', self.touch_gve_joineds)
        self.__gve_activateds = StoredListContainer(int_value=True)

        self.__gve_activateds.init_entity(self, 'gve_activateds', self.touch_gve_activateds)
        self.__gve_start_time = 0

        self.__gve_progress = StoredDictContainer(int_value=True, int_key=True)

        self.__gve_progress.init_entity(self, 'gve_progress', self.touch_gve_progress)
        self.__gve_deads = StoredSetContainer(int_value=True)

        self.__gve_deads.init_entity(self, 'gve_deads', self.touch_gve_deads)
        self.__gve_end_cd = 0

        self.__gve_max_damage = 0

        self.__gve_rewards = StoredDictContainer(int_value=False, int_key=True)

        self.__gve_rewards.init_entity(self, 'gve_rewards', self.touch_gve_rewards)
        self.__gve_last_kick_time = 0

        self.__gve_last_reset_time = 0

        self.__gve_end_activateds = StoredListContainer(int_value=True)

        self.__gve_end_activateds.init_entity(self, 'gve_end_activateds', self.touch_gve_end_activateds)
        self.__gve_activateds_detail = StoredDictContainer(int_value=False, int_key=True)

        self.__gve_activateds_detail.init_entity(self, 'gve_activateds_detail', self.touch_gve_activateds_detail)
        self.__lastlogin = 0


    def begin_initialize(self):
        self._initialized = False

    def end_initialize(self):
        self._initialized = True

    def load_containers(self):
        self.applys.load()
        self.members.load()
        self.invites.load()
        self.gve_joineds.load()
        self.gve_activateds.load()
        self.gve_progress.load()
        self.gve_deads.load()
        self.gve_rewards.load()
        self.gve_end_activateds.load()
        self.gve_activateds_detail.load()
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
        self.__groupID = None
        self.clear_groupID()
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
    cdef public object __applys
    property applys:
        def __get__(self):
            return self.__applys
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_applys(self):
        pass
    cdef public object __members
    property members:
        def __get__(self):
            return self.__members
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_members(self):
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
    cdef public object __invites
    property invites:
        def __get__(self):
            return self.__invites
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_invites(self):
        pass
    cdef public object __leader_lastlogin
    property leader_lastlogin:
        def __get__(self):
            return self.__leader_lastlogin
        def __set__(self, value):
                value = value
                if value != self.__leader_lastlogin:
                    self.__leader_lastlogin = value
                    if self._initialized:
                        self.touch_leader_lastlogin()

    cpdef touch_leader_lastlogin(self):
        self.dirty_fields.add('leader_lastlogin')
        pass
    cdef public object __gve_joineds
    property gve_joineds:
        def __get__(self):
            return self.__gve_joineds
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_gve_joineds(self):
        pass
    cdef public object __gve_activateds
    property gve_activateds:
        def __get__(self):
            return self.__gve_activateds
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_gve_activateds(self):
        pass
    cdef public int __gve_start_time
    property gve_start_time:
        def __get__(self):
            return self.__gve_start_time
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_start_time:
                    self.__gve_start_time = value
                    if self._initialized:
                        self.touch_gve_start_time()

    cpdef touch_gve_start_time(self):
        self.dirty_fields.add('gve_start_time')
        pass
    cdef public object __gve_progress
    property gve_progress:
        def __get__(self):
            return self.__gve_progress
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_gve_progress(self):
        pass
    cdef public object __gve_deads
    property gve_deads:
        def __get__(self):
            return self.__gve_deads
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_gve_deads(self):
        pass
    cdef public int __gve_end_cd
    property gve_end_cd:
        def __get__(self):
            return self.__gve_end_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_end_cd:
                    self.__gve_end_cd = value
                    if self._initialized:
                        self.touch_gve_end_cd()

    cpdef touch_gve_end_cd(self):
        self.dirty_fields.add('gve_end_cd')
        pass
    cdef public int __gve_max_damage
    property gve_max_damage:
        def __get__(self):
            return self.__gve_max_damage
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_max_damage:
                    self.__gve_max_damage = value
                    if self._initialized:
                        self.touch_gve_max_damage()

    cpdef touch_gve_max_damage(self):
        self.dirty_fields.add('gve_max_damage')
        pass
    cdef public object __gve_rewards
    property gve_rewards:
        def __get__(self):
            return self.__gve_rewards
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_gve_rewards(self):
        pass
    cdef public int __gve_last_kick_time
    property gve_last_kick_time:
        def __get__(self):
            return self.__gve_last_kick_time
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_last_kick_time:
                    self.__gve_last_kick_time = value
                    if self._initialized:
                        self.touch_gve_last_kick_time()

    cpdef touch_gve_last_kick_time(self):
        self.dirty_fields.add('gve_last_kick_time')
        pass
    cdef public int __gve_last_reset_time
    property gve_last_reset_time:
        def __get__(self):
            return self.__gve_last_reset_time
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_last_reset_time:
                    self.__gve_last_reset_time = value
                    if self._initialized:
                        self.touch_gve_last_reset_time()

    cpdef touch_gve_last_reset_time(self):
        self.dirty_fields.add('gve_last_reset_time')
        pass
    cdef public object __gve_end_activateds
    property gve_end_activateds:
        def __get__(self):
            return self.__gve_end_activateds
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_gve_end_activateds(self):
        pass
    cdef public object __gve_activateds_detail
    property gve_activateds_detail:
        def __get__(self):
            return self.__gve_activateds_detail
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_gve_activateds_detail(self):
        pass
    cdef public object __lastlogin
    property lastlogin:
        def __get__(self):
            return self.__lastlogin
        def __set__(self, value):
                value = value
                if value != self.__lastlogin:
                    self.__lastlogin = value
                    if self._initialized:
                        self.touch_lastlogin()

    cpdef touch_lastlogin(self):
        self.dirty_fields.add('lastlogin')
        pass

    # formula fields
    cdef public object __groupID
    property groupID:
        def __get__(self):
            if self.__groupID is None:
                value = self.entityID
                self.__groupID = int(value)
            return self.__groupID
        def __set__(self, value):
            assert self.__groupID is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__groupID = value
    cpdef clear_groupID(self):
        self.__groupID = None

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
