cimport cython
from yy.entity.formulas import g_formulas as fn
from yy.entity.base import cycle
from time import time
from datetime import timedelta, date as datedate
from yy.entity.containers import ListContainer, SetContainer, DictContainer, StoredListContainer, StoredSetContainer, StoredDictContainer


from pet.define import PetBase as PureEntity

cdef convert_bool(b):
    return bool(int(b))



@cython.freelist(1000)
cdef class c_PetBase(object):
    fields_list = PureEntity.fields_list
    fields = PureEntity.fields
    fields_ids_map = PureEntity.fields_ids_map
    store_tag = 't'

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

        self.__level = 1

        self.__modelID = 0

        self.__skill = 1

        self.__lskill = 1

        self.__prototypeID = 0

        self.__masterID = 0

        self.__exp = 0

        self.__gettime = 0

        self.__dispatched = 0

        self.__mtype = 0

        self.__activated_relations = DictContainer()

        self.__activated_relations.init_entity(self, 'activated_relations', self.touch_activated_relations)
        self.__uproar_dead = False

        self.__restHP = 0

        self.__add_star = 0

        self.__skill1 = 1

        self.__skill2 = 1

        self.__skill3 = 1

        self.__skill4 = 1

        self.__skill5 = 1

        self.__equipeds = StoredDictContainer(int_value=True, int_key=True)

        self.__equipeds.init_entity(self, 'equipeds', self.touch_equipeds)
        self.__daily_dead = False

        self.__daily_restHP = 0


    def begin_initialize(self):
        self._initialized = False

    def end_initialize(self):
        self._initialized = True

    def load_containers(self):
        self.equipeds.load()
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
        self.__base_power = None
        self.__power = None
        self.clear_base_power()
        self.clear_power()
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
        self.sync_dirty_fields.add('name')
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
        self.__base_power = None
        self.__power = None
        self.__baseHP = None
        self.__baseATK = None
        self.__baseDEF = None
        self.__baseCRI = None
        self.__baseEVA = None
        self.clear_base_power()
        self.clear_power()
        self.clear_baseHP()
        self.clear_baseATK()
        self.clear_baseDEF()
        self.clear_baseCRI()
        self.clear_baseEVA()
        pass
    cdef public int __modelID
    property modelID:
        def __get__(self):
            return self.__modelID
        def __set__(self, value):
                value = int(value)
                if value != self.__modelID:
                    self.__modelID = value
                    if self._initialized:
                        self.touch_modelID()

    cpdef touch_modelID(self):
        self.dirty_fields.add('modelID')
        pass
    cdef public int __skill
    property skill:
        def __get__(self):
            return self.__skill
        def __set__(self, value):
                value = int(value)
                if value != self.__skill:
                    self.__skill = value
                    if self._initialized:
                        self.touch_skill()

    cpdef touch_skill(self):
        self.dirty_fields.add('skill')
        self.sync_dirty_fields.add('skill')
        pass
    cdef public int __lskill
    property lskill:
        def __get__(self):
            return self.__lskill
        def __set__(self, value):
                value = int(value)
                if value != self.__lskill:
                    self.__lskill = value
                    if self._initialized:
                        self.touch_lskill()

    cpdef touch_lskill(self):
        self.dirty_fields.add('lskill')
        self.sync_dirty_fields.add('lskill')
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
        self.__breaklevel = None
        self.__base_power = None
        self.__power = None
        self.__baseHP = None
        self.__baseATK = None
        self.__baseDEF = None
        self.__baseCRI = None
        self.__baseEVA = None
        self.__star = None
        self.__base_star = None
        self.__max_level = None
        self.__next_max_level = None
        self.clear_breaklevel()
        self.clear_base_power()
        self.clear_power()
        self.clear_baseHP()
        self.clear_baseATK()
        self.clear_baseDEF()
        self.clear_baseCRI()
        self.clear_baseEVA()
        self.clear_star()
        self.clear_base_star()
        self.clear_max_level()
        self.clear_next_max_level()
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
    cdef public int __exp
    property exp:
        def __get__(self):
            return self.__exp
        def __set__(self, value):
                value = int(value)
                if value != self.__exp:
                    self.__exp = value
                    if self._initialized:
                        self.touch_exp()

    cpdef touch_exp(self):
        self.dirty_fields.add('exp')
        self.sync_dirty_fields.add('exp')
        pass
    cdef public int __gettime
    property gettime:
        def __get__(self):
            return self.__gettime
        def __set__(self, value):
                value = int(value)
                if value != self.__gettime:
                    self.__gettime = value
                    if self._initialized:
                        self.touch_gettime()

    cpdef touch_gettime(self):
        self.dirty_fields.add('gettime')
        self.sync_dirty_fields.add('gettime')
        pass
    cdef public int __dispatched
    property dispatched:
        def __get__(self):
            return self.__dispatched
        def __set__(self, value):
                value = int(value)
                if value != self.__dispatched:
                    self.__dispatched = value
                    if self._initialized:
                        self.touch_dispatched()

    cpdef touch_dispatched(self):
        self.dirty_fields.add('dispatched')
        self.sync_dirty_fields.add('dispatched')
        pass
    cdef public int __mtype
    property mtype:
        def __get__(self):
            return self.__mtype
        def __set__(self, value):
                value = int(value)
                if value != self.__mtype:
                    self.__mtype = value
                    if self._initialized:
                        self.touch_mtype()

    cpdef touch_mtype(self):
        self.sync_dirty_fields.add('mtype')
        pass
    cdef public object __activated_relations
    property activated_relations:
        def __get__(self):
            return self.__activated_relations
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'activated_relations', self.touch_activated_relations)
                if value != self.__activated_relations:
                    self.__activated_relations = value
                    if self._initialized:
                        self.touch_activated_relations()

    cpdef touch_activated_relations(self):
        self.dirty_fields.add('activated_relations')
        self.__relations = None
        self.__base_power = None
        self.__power = None
        self.__baseHP = None
        self.__baseATK = None
        self.__baseDEF = None
        self.__baseCRI = None
        self.__baseEVA = None
        self.clear_relations()
        self.clear_base_power()
        self.clear_power()
        self.clear_baseHP()
        self.clear_baseATK()
        self.clear_baseDEF()
        self.clear_baseCRI()
        self.clear_baseEVA()
        pass
    cdef public object __uproar_dead
    property uproar_dead:
        def __get__(self):
            return self.__uproar_dead
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__uproar_dead:
                    self.__uproar_dead = value
                    if self._initialized:
                        self.touch_uproar_dead()

    cpdef touch_uproar_dead(self):
        self.dirty_fields.add('uproar_dead')
        self.sync_dirty_fields.add('uproar_dead')
        pass
    cdef public int __restHP
    property restHP:
        def __get__(self):
            return self.__restHP
        def __set__(self, value):
                value = int(value)
                if value != self.__restHP:
                    self.__restHP = value
                    if self._initialized:
                        self.touch_restHP()

    cpdef touch_restHP(self):
        self.dirty_fields.add('restHP')
        self.sync_dirty_fields.add('restHP')
        pass
    cdef public int __add_star
    property add_star:
        def __get__(self):
            return self.__add_star
        def __set__(self, value):
                value = int(value)
                if value != self.__add_star:
                    self.__add_star = value
                    if self._initialized:
                        self.touch_add_star()

    cpdef touch_add_star(self):
        self.dirty_fields.add('add_star')
        self.__breaklevel = None
        self.__base_power = None
        self.__power = None
        self.__baseHP = None
        self.__baseATK = None
        self.__baseDEF = None
        self.__baseCRI = None
        self.__baseEVA = None
        self.__star = None
        self.__max_level = None
        self.__next_max_level = None
        self.clear_breaklevel()
        self.clear_base_power()
        self.clear_power()
        self.clear_baseHP()
        self.clear_baseATK()
        self.clear_baseDEF()
        self.clear_baseCRI()
        self.clear_baseEVA()
        self.clear_star()
        self.clear_max_level()
        self.clear_next_max_level()
        pass
    cdef public int __skill1
    property skill1:
        def __get__(self):
            return self.__skill1
        def __set__(self, value):
                value = int(value)
                if value != self.__skill1:
                    self.__skill1 = value
                    if self._initialized:
                        self.touch_skill1()

    cpdef touch_skill1(self):
        self.dirty_fields.add('skill1')
        self.sync_dirty_fields.add('skill1')
        self.__base_power = None
        self.__power = None
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public int __skill2
    property skill2:
        def __get__(self):
            return self.__skill2
        def __set__(self, value):
                value = int(value)
                if value != self.__skill2:
                    self.__skill2 = value
                    if self._initialized:
                        self.touch_skill2()

    cpdef touch_skill2(self):
        self.dirty_fields.add('skill2')
        self.sync_dirty_fields.add('skill2')
        self.__base_power = None
        self.__power = None
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public int __skill3
    property skill3:
        def __get__(self):
            return self.__skill3
        def __set__(self, value):
                value = int(value)
                if value != self.__skill3:
                    self.__skill3 = value
                    if self._initialized:
                        self.touch_skill3()

    cpdef touch_skill3(self):
        self.dirty_fields.add('skill3')
        self.sync_dirty_fields.add('skill3')
        self.__base_power = None
        self.__power = None
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public int __skill4
    property skill4:
        def __get__(self):
            return self.__skill4
        def __set__(self, value):
                value = int(value)
                if value != self.__skill4:
                    self.__skill4 = value
                    if self._initialized:
                        self.touch_skill4()

    cpdef touch_skill4(self):
        self.dirty_fields.add('skill4')
        self.sync_dirty_fields.add('skill4')
        self.__base_power = None
        self.__power = None
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public int __skill5
    property skill5:
        def __get__(self):
            return self.__skill5
        def __set__(self, value):
                value = int(value)
                if value != self.__skill5:
                    self.__skill5 = value
                    if self._initialized:
                        self.touch_skill5()

    cpdef touch_skill5(self):
        self.dirty_fields.add('skill5')
        self.sync_dirty_fields.add('skill5')
        self.__base_power = None
        self.__power = None
        self.clear_base_power()
        self.clear_power()
        pass
    cdef public object __equipeds
    property equipeds:
        def __get__(self):
            return self.__equipeds
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_equipeds(self):
        self.__equipeds_json = None
        self.clear_equipeds_json()
        pass
    cdef public object __daily_dead
    property daily_dead:
        def __get__(self):
            return self.__daily_dead
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__daily_dead:
                    self.__daily_dead = value
                    if self._initialized:
                        self.touch_daily_dead()

    cpdef touch_daily_dead(self):
        self.dirty_fields.add('daily_dead')
        self.sync_dirty_fields.add('daily_dead')
        pass
    cdef public int __daily_restHP
    property daily_restHP:
        def __get__(self):
            return self.__daily_restHP
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_restHP:
                    self.__daily_restHP = value
                    if self._initialized:
                        self.touch_daily_restHP()

    cpdef touch_daily_restHP(self):
        self.dirty_fields.add('daily_restHP')
        self.sync_dirty_fields.add('daily_restHP')
        pass

    # formula fields
    cdef public object __breaklevel
    property breaklevel:
        def __get__(self):
            if self.__breaklevel is None:
                value = fn.get_breaklevel(self.prototypeID, self.star)
                self.__breaklevel = int(value)
            return self.__breaklevel
        def __set__(self, value):
            assert self.__breaklevel is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__breaklevel = value
    cpdef clear_breaklevel(self):
        self.__breaklevel = None
        self.set_sync_dirty('breaklevel')
    cdef public object __relations
    property relations:
        def __get__(self):
            if self.__relations is None:
                value = fn.get_relations(self.activated_relations)
                self.__relations = value
            return self.__relations
        def __set__(self, value):
            assert self.__relations is None, 'can only set formula attribute when initialize'
            if isinstance(value, str):
                value = value.decode('utf-8')
            value = value
            self.__relations = value
    cpdef clear_relations(self):
        self.__relations = None
        self.set_sync_dirty('relations')
    cdef public object __base_power
    property base_power:
        def __get__(self):
            if self.__base_power is None:
                value = fn.get_pet_base_power(self.entityID, self.prototypeID, self.masterID, self.baseHP, self.baseATK, self.baseDEF, self.baseCRI, self.baseEVA, self.skill1, self.skill2, self.skill3, self.skill4, self.skill5)
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
    cdef public object __baseHP
    property baseHP:
        def __get__(self):
            if self.__baseHP is None:
                value = fn.get_pet_base_hp(self.prototypeID, self.level, self.breaklevel, self.activated_relations)
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
                value = fn.get_pet_base_atk(self.prototypeID, self.level, self.breaklevel, self.activated_relations)
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
                value = fn.get_pet_base_def(self.prototypeID, self.level, self.breaklevel, self.activated_relations)
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
                value = fn.get_pet_base_crit(self.prototypeID, self.level, self.breaklevel, self.activated_relations)
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
                value = fn.get_pet_base_dodge(self.prototypeID, self.level, self.breaklevel, self.activated_relations)
                self.__baseEVA = float(value)
            return self.__baseEVA
        def __set__(self, value):
            assert self.__baseEVA is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__baseEVA = value
    cpdef clear_baseEVA(self):
        self.__baseEVA = None
    cdef public object __star
    property star:
        def __get__(self):
            if self.__star is None:
                value = fn.get_star(self.base_star, self.add_star)
                self.__star = int(value)
            return self.__star
        def __set__(self, value):
            assert self.__star is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__star = value
    cpdef clear_star(self):
        self.__star = None
        self.set_sync_dirty('star')
    cdef public object __base_star
    property base_star:
        def __get__(self):
            if self.__base_star is None:
                value = fn.get_base_star(self.prototypeID)
                self.__base_star = int(value)
            return self.__base_star
        def __set__(self, value):
            assert self.__base_star is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__base_star = value
    cpdef clear_base_star(self):
        self.__base_star = None
    cdef public object __equipeds_json
    property equipeds_json:
        def __get__(self):
            if self.__equipeds_json is None:
                value = fn.get_equipeds_json(self.equipeds)
                self.__equipeds_json = value
            return self.__equipeds_json
        def __set__(self, value):
            assert self.__equipeds_json is None, 'can only set formula attribute when initialize'
            if isinstance(value, str):
                value = value.decode('utf-8')
            value = value
            self.__equipeds_json = value
    cpdef clear_equipeds_json(self):
        self.__equipeds_json = None
        self.set_sync_dirty('equipeds_json')
    cdef public object __max_level
    property max_level:
        def __get__(self):
            if self.__max_level is None:
                value = fn.get_max_level(self.breaklevel)
                self.__max_level = int(value)
            return self.__max_level
        def __set__(self, value):
            assert self.__max_level is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__max_level = value
    cpdef clear_max_level(self):
        self.__max_level = None
        self.set_sync_dirty('max_level')
    cdef public object __next_max_level
    property next_max_level:
        def __get__(self):
            if self.__next_max_level is None:
                value = fn.get_next_max_level(self.breaklevel)
                self.__next_max_level = int(value)
            return self.__next_max_level
        def __set__(self, value):
            assert self.__next_max_level is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__next_max_level = value
    cpdef clear_next_max_level(self):
        self.__next_max_level = None
        self.set_sync_dirty('next_max_level')

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
