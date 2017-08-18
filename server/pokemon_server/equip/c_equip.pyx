cimport cython
from yy.entity.formulas import g_formulas as fn
from yy.entity.base import cycle
from time import time
from datetime import timedelta, date as datedate
from yy.entity.containers import ListContainer, SetContainer, DictContainer, StoredListContainer, StoredSetContainer, StoredDictContainer


from equip.define import EquipBase as PureEntity

cdef convert_bool(b):
    return bool(int(b))



@cython.freelist(1000)
cdef class c_EquipBase(object):
    fields_list = PureEntity.fields_list
    fields = PureEntity.fields
    fields_ids_map = PureEntity.fields_ids_map
    store_tag = 'e'

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

        self.__prototypeID = 0

        self.__masterID = 0

        self.__type = 0

        self.__level = 0

        self.__step = 1

        self.__rest_star = 0

        self.__enchants = ListContainer()

        self.__enchants.init_entity(self, 'enchants', self.touch_enchants)
        self.__player_equip1 = 0

        self.__player_equip2 = 0

        self.__player_equip3 = 0

        self.__player_equip4 = 0

        self.__player_equip5 = 0

        self.__player_equip6 = 0


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
        self.sync_dirty_fields.add('entityID')
        self.__equipID = None
        self.__base_power = None
        self.__power = None
        self.clear_equipID()
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public int __prototypeID
    property prototypeID:
        def __get__(self):
            return self.__prototypeID
        def __set__(self, value):
                value = int(value)
                if value != self.__prototypeID:
                    self.__prototypeID = value
                    if self._initialized:
                        self.touch_prototypeID()

    cpdef touch_prototypeID(self):
        self.dirty_fields.add('prototypeID')
        self.sync_dirty_fields.add('prototypeID')
        self.__baseHP = None
        self.__baseATK = None
        self.__baseDEF = None
        self.__baseCRI = None
        self.__baseEVA = None
        self.__enchant_attrs = None
        self.__base_power = None
        self.__power = None
        self.clear_baseHP()
        self.clear_baseATK()
        self.clear_baseDEF()
        self.clear_baseCRI()
        self.clear_baseEVA()
        self.clear_enchant_attrs()
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public int __masterID
    property masterID:
        def __get__(self):
            return self.__masterID
        def __set__(self, value):
                value = int(value)
                if value != self.__masterID:
                    self.__masterID = value
                    if self._initialized:
                        self.touch_masterID()

    cpdef touch_masterID(self):
        self.__base_power = None
        self.__power = None
        self.clear_base_power()
        self.clear_power()
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
        self.__baseHP = None
        self.__baseATK = None
        self.__baseDEF = None
        self.__baseCRI = None
        self.__baseEVA = None
        self.__base_power = None
        self.__power = None
        self.clear_baseHP()
        self.clear_baseATK()
        self.clear_baseDEF()
        self.clear_baseCRI()
        self.clear_baseEVA()
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public int __level
    property level:
        def __get__(self):
            return self.__level
        def __set__(self, value):
                value = int(value)
                if value != self.__level:
                    self.__level = value
                    if self._initialized:
                        self.touch_level()

    cpdef touch_level(self):
        self.dirty_fields.add('level')
        self.sync_dirty_fields.add('level')
        self.__baseHP = None
        self.__baseATK = None
        self.__baseDEF = None
        self.__baseCRI = None
        self.__baseEVA = None
        self.__base_power = None
        self.__power = None
        self.clear_baseHP()
        self.clear_baseATK()
        self.clear_baseDEF()
        self.clear_baseCRI()
        self.clear_baseEVA()
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public int __step
    property step:
        def __get__(self):
            return self.__step
        def __set__(self, value):
                value = int(value)
                if value != self.__step:
                    self.__step = value
                    if self._initialized:
                        self.touch_step()

    cpdef touch_step(self):
        self.dirty_fields.add('step')
        self.sync_dirty_fields.add('step')
        self.__slugs = None
        self.__baseHP = None
        self.__baseATK = None
        self.__baseDEF = None
        self.__baseCRI = None
        self.__baseEVA = None
        self.__enchant_attrs = None
        self.__base_power = None
        self.__power = None
        self.clear_slugs()
        self.clear_baseHP()
        self.clear_baseATK()
        self.clear_baseDEF()
        self.clear_baseCRI()
        self.clear_baseEVA()
        self.clear_enchant_attrs()
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public int __rest_star
    property rest_star:
        def __get__(self):
            return self.__rest_star
        def __set__(self, value):
                value = int(value)
                if value != self.__rest_star:
                    self.__rest_star = value
                    if self._initialized:
                        self.touch_rest_star()

    cpdef touch_rest_star(self):
        self.dirty_fields.add('rest_star')
        self.sync_dirty_fields.add('rest_star')
        pass
    cdef public object __enchants
    property enchants:
        def __get__(self):
            return self.__enchants
        def __set__(self, value):
                value = ListContainer(value)
                value.init_entity(self, 'enchants', self.touch_enchants)
                if value != self.__enchants:
                    self.__enchants = value
                    if self._initialized:
                        self.touch_enchants()

    cpdef touch_enchants(self):
        self.dirty_fields.add('enchants')
        self.__baseHP = None
        self.__baseATK = None
        self.__baseDEF = None
        self.__baseCRI = None
        self.__baseEVA = None
        self.__enchant_attrs = None
        self.__base_power = None
        self.__power = None
        self.clear_baseHP()
        self.clear_baseATK()
        self.clear_baseDEF()
        self.clear_baseCRI()
        self.clear_baseEVA()
        self.clear_enchant_attrs()
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public int __player_equip1
    property player_equip1:
        def __get__(self):
            return self.__player_equip1
        def __set__(self, value):
                value = int(value)
                if value != self.__player_equip1:
                    self.__player_equip1 = value
                    if self._initialized:
                        self.touch_player_equip1()

    cpdef touch_player_equip1(self):
        self.__baseHP = None
        self.__baseATK = None
        self.__baseDEF = None
        self.__baseCRI = None
        self.__baseEVA = None
        self.__base_power = None
        self.__power = None
        self.clear_baseHP()
        self.clear_baseATK()
        self.clear_baseDEF()
        self.clear_baseCRI()
        self.clear_baseEVA()
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public int __player_equip2
    property player_equip2:
        def __get__(self):
            return self.__player_equip2
        def __set__(self, value):
                value = int(value)
                if value != self.__player_equip2:
                    self.__player_equip2 = value
                    if self._initialized:
                        self.touch_player_equip2()

    cpdef touch_player_equip2(self):
        self.__baseHP = None
        self.__baseATK = None
        self.__baseDEF = None
        self.__baseCRI = None
        self.__baseEVA = None
        self.__base_power = None
        self.__power = None
        self.clear_baseHP()
        self.clear_baseATK()
        self.clear_baseDEF()
        self.clear_baseCRI()
        self.clear_baseEVA()
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public int __player_equip3
    property player_equip3:
        def __get__(self):
            return self.__player_equip3
        def __set__(self, value):
                value = int(value)
                if value != self.__player_equip3:
                    self.__player_equip3 = value
                    if self._initialized:
                        self.touch_player_equip3()

    cpdef touch_player_equip3(self):
        self.__baseHP = None
        self.__baseATK = None
        self.__baseDEF = None
        self.__baseCRI = None
        self.__baseEVA = None
        self.__base_power = None
        self.__power = None
        self.clear_baseHP()
        self.clear_baseATK()
        self.clear_baseDEF()
        self.clear_baseCRI()
        self.clear_baseEVA()
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public int __player_equip4
    property player_equip4:
        def __get__(self):
            return self.__player_equip4
        def __set__(self, value):
                value = int(value)
                if value != self.__player_equip4:
                    self.__player_equip4 = value
                    if self._initialized:
                        self.touch_player_equip4()

    cpdef touch_player_equip4(self):
        self.__baseHP = None
        self.__baseATK = None
        self.__baseDEF = None
        self.__baseCRI = None
        self.__baseEVA = None
        self.__base_power = None
        self.__power = None
        self.clear_baseHP()
        self.clear_baseATK()
        self.clear_baseDEF()
        self.clear_baseCRI()
        self.clear_baseEVA()
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public int __player_equip5
    property player_equip5:
        def __get__(self):
            return self.__player_equip5
        def __set__(self, value):
                value = int(value)
                if value != self.__player_equip5:
                    self.__player_equip5 = value
                    if self._initialized:
                        self.touch_player_equip5()

    cpdef touch_player_equip5(self):
        self.__baseHP = None
        self.__baseATK = None
        self.__baseDEF = None
        self.__baseCRI = None
        self.__baseEVA = None
        self.__base_power = None
        self.__power = None
        self.clear_baseHP()
        self.clear_baseATK()
        self.clear_baseDEF()
        self.clear_baseCRI()
        self.clear_baseEVA()
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public int __player_equip6
    property player_equip6:
        def __get__(self):
            return self.__player_equip6
        def __set__(self, value):
                value = int(value)
                if value != self.__player_equip6:
                    self.__player_equip6 = value
                    if self._initialized:
                        self.touch_player_equip6()

    cpdef touch_player_equip6(self):
        self.__baseHP = None
        self.__baseATK = None
        self.__baseDEF = None
        self.__baseCRI = None
        self.__baseEVA = None
        self.__base_power = None
        self.__power = None
        self.clear_baseHP()
        self.clear_baseATK()
        self.clear_baseDEF()
        self.clear_baseCRI()
        self.clear_baseEVA()
        self.clear_base_power()
        self.clear_power()
        pass

    # formula fields
    cdef public object __equipID
    property equipID:
        def __get__(self):
            if self.__equipID is None:
                value = self.entityID
                self.__equipID = int(value)
            return self.__equipID
        def __set__(self, value):
            assert self.__equipID is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__equipID = value
    cpdef clear_equipID(self):
        self.__equipID = None
    cdef public object __slugs
    property slugs:
        def __get__(self):
            if self.__slugs is None:
                value = fn.get_slugs(self.step)
                self.__slugs = int(value)
            return self.__slugs
        def __set__(self, value):
            assert self.__slugs is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__slugs = value
    cpdef clear_slugs(self):
        self.__slugs = None
    cdef public object __baseHP
    property baseHP:
        def __get__(self):
            if self.__baseHP is None:
                value = fn.get_equip_base_hp(self.prototypeID, self.level, self.step, self.enchant_attrs, self.player_equip1, self.player_equip2, self.player_equip3, self.player_equip4, self.player_equip5, self.player_equip6, self.type)
                self.__baseHP = float(value)
            return self.__baseHP
        def __set__(self, value):
            assert self.__baseHP is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__baseHP = value
    cpdef clear_baseHP(self):
        self.__baseHP = None
    cdef public object __baseATK
    property baseATK:
        def __get__(self):
            if self.__baseATK is None:
                value = fn.get_equip_base_atk(self.prototypeID, self.level, self.step, self.enchant_attrs, self.player_equip1, self.player_equip2, self.player_equip3, self.player_equip4, self.player_equip5, self.player_equip6, self.type)
                self.__baseATK = float(value)
            return self.__baseATK
        def __set__(self, value):
            assert self.__baseATK is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__baseATK = value
    cpdef clear_baseATK(self):
        self.__baseATK = None
    cdef public object __baseDEF
    property baseDEF:
        def __get__(self):
            if self.__baseDEF is None:
                value = fn.get_equip_base_def(self.prototypeID, self.level, self.step, self.enchant_attrs, self.player_equip1, self.player_equip2, self.player_equip3, self.player_equip4, self.player_equip5, self.player_equip6, self.type)
                self.__baseDEF = float(value)
            return self.__baseDEF
        def __set__(self, value):
            assert self.__baseDEF is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__baseDEF = value
    cpdef clear_baseDEF(self):
        self.__baseDEF = None
    cdef public object __baseCRI
    property baseCRI:
        def __get__(self):
            if self.__baseCRI is None:
                value = fn.get_equip_base_crit(self.prototypeID, self.level, self.step, self.enchant_attrs, self.player_equip1, self.player_equip2, self.player_equip3, self.player_equip4, self.player_equip5, self.player_equip6, self.type)
                self.__baseCRI = float(value)
            return self.__baseCRI
        def __set__(self, value):
            assert self.__baseCRI is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__baseCRI = value
    cpdef clear_baseCRI(self):
        self.__baseCRI = None
    cdef public object __baseEVA
    property baseEVA:
        def __get__(self):
            if self.__baseEVA is None:
                value = fn.get_equip_base_dodge(self.prototypeID, self.level, self.step, self.enchant_attrs, self.player_equip1, self.player_equip2, self.player_equip3, self.player_equip4, self.player_equip5, self.player_equip6, self.type)
                self.__baseEVA = float(value)
            return self.__baseEVA
        def __set__(self, value):
            assert self.__baseEVA is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__baseEVA = value
    cpdef clear_baseEVA(self):
        self.__baseEVA = None
    cdef public object __enchant_attrs
    property enchant_attrs:
        def __get__(self):
            if self.__enchant_attrs is None:
                value = fn.get_enchant_attrs(self.prototypeID, self.slugs, self.enchants)
                self.__enchant_attrs = value
            return self.__enchant_attrs
        def __set__(self, value):
            assert self.__enchant_attrs is None, 'can only set formula attribute when initialize'
            if isinstance(value, str):
                value = value.decode('utf-8')
            value = value
            self.__enchant_attrs = value
    cpdef clear_enchant_attrs(self):
        self.__enchant_attrs = None
        self.set_sync_dirty('enchant_attrs')
    cdef public object __base_power
    property base_power:
        def __get__(self):
            if self.__base_power is None:
                value = fn.get_equip_base_power(self.entityID, self.prototypeID, self.masterID, self.baseHP, self.baseATK, self.baseDEF, self.baseCRI, self.baseEVA)
                self.__base_power = float(value)
            return self.__base_power
        def __set__(self, value):
            assert self.__base_power is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__base_power = value
    cpdef clear_base_power(self):
        self.__base_power = None
    cdef public object __power
    property power:
        def __get__(self):
            if self.__power is None:
                value = self.base_power
                self.__power = int(value)
            return self.__power
        def __set__(self, value):
            assert self.__power is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__power = value
    cpdef clear_power(self):
        self.__power = None
        self.set_sync_dirty('power')

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
