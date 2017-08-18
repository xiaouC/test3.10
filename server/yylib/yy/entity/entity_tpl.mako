# coding: utf-8
cimport cython
from yy.entity.formulas import g_formulas as fn
from yy.entity.base import cycle
from time import time
from datetime import timedelta, date as datedate
from yy.entity.containers import ListContainer, SetContainer, DictContainer, StoredListContainer, StoredSetContainer, StoredDictContainer
${extra_imports}
${import_pure}

cdef convert_bool(b):
    return bool(int(b))

<%
from collections import defaultdict
from yy.entity.compiler import replace_var_for_mako

c_field_type_convert = {
    'integer':  'int',
    'float':    'double',
    'string':   'unicode',
    'sequence': 'object',
    'set':      'object',
    'dict':     'object',
    'stored_sequence': 'object',
    'stored_set':      'object',
    'stored_dict':     'object',
}
py_field_type_convert = {
    'boolean':  'convert_bool',
    'integer':  'int',
    'float':    'float',
    'sequence': 'ListContainer',
    'dict':     'DictContainer',
    'set':      'SetContainer',
    'stored_sequence': 'StoredListContainer',
    'stored_dict':     'StoredDictContainer',
    'stored_set':      'StoredSetContainer',
}
stored_container_types = ['stored_sequence', 'stored_dict', 'stored_set']
container_types = ['sequence', 'dict', 'set']

def get_c_field_type(t):
    return c_field_type_convert.get(t, 'object')
def get_py_field_type(t, v):
    if t in py_field_type_convert:
        return '%s(%s)' % (py_field_type_convert[t], v)
    else:
        return v

fields = defaultdict(list)
for f in fields_list:
    if f.formula is not None:
        fields['formula'].append(f)
    elif f.cycle or f.sync or f.save or f.effect_set or f.event or f.type == 'string' or f.type in stored_container_types:
        fields['normal'].append(f)
    elif f.type in container_types:
        fields['normal'].append(f)
    else:
        fields['plain'].append(f)
    if f.event:
        fields['event'].append(f)

fieldsmap = dict((f.name, f) for f in fields_list)
%>

@cython.freelist(1000)
cdef class ${classname}(object):
    fields_list = PureEntity.fields_list
    fields = PureEntity.fields
    fields_ids_map = PureEntity.fields_ids_map
    store_tag = '${store_tag}'

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
        % for f in fields['plain']:
            % if f.raw_default:
        self.${f.name} = ${f.raw_default}
            % elif hasattr(f.default, '__name__'):
        self.${f.name} = ${f.default.__name__}()
            % else:
        self.${f.name} = ${repr(f.default)}
            % endif
        % endfor

        % for f in fields['normal']:
            % if f.raw_default:
        self.__${f.name} = ${f.raw_default}
            % elif hasattr(f.default, '__name__'):
        self.__${f.name} = ${f.default.__name__}()
            % elif f.type in stored_container_types:
        self.__${f.name} = ${py_field_type_convert[f.type]}(${'int_value=True' if f.int_value else 'int_value=False'}${', int_key=True' if f.int_key else ''})
            % else:
        self.__${f.name} = ${repr(f.default)}
            % endif

            % if f.type in container_types or f.type in stored_container_types:
        self.__${f.name}.init_entity(self, '${f.name}', self.touch_${f.name})
            % endif
        % endfor

    def begin_initialize(self):
        self._initialized = False

    def end_initialize(self):
        self._initialized = True

    def load_containers(self):
        % for f in fields['normal']:
            % if f.type in stored_container_types:
        self.${f.name}.load()
            % endif
        % endfor
        pass

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if v is not None:
                setattr(self, k, v)

    def push_command(self, *cmd):
        self.dirty_commands.append(cmd)

    # event fields
    % for f in fields['event']:
    _listeners_${f.name} = []
    @classmethod
    def listen_${f.name}(cls, callback):
        cls._listeners_${f.name}.append(callback)
    % endfor

    # simple fields
    % for f in fields['plain']:
    cdef public ${get_c_field_type(f.type)} ${f.name}
    % endfor

    # normal fields
    % for f in fields['normal']:
    cdef public ${get_c_field_type(f.type)} __${f.name}
    property ${f.name}:
        def __get__(self):
            return self.__${f.name}
        def __set__(self, value):
            % if f.type in stored_container_types:
            raise AttributeError('stored container types don\'t support __setattr__')
            % else:
                % if f.type == 'string':
                if isinstance(value, str):
                    value = value.decode('utf-8')
                % endif
                value = ${get_py_field_type(f.type, 'value')}
                % if f.type in container_types:
                value.init_entity(self, '${f.name}', self.touch_${f.name})
                % endif
                if value != self.__${f.name}:
                    % if f.event:
                    if self._initialized:
                        for callback in type(self)._listeners_${f.name}:
                            callback(self, value)
                    % endif
                    self.__${f.name} = value
                    if self._initialized:
                        self.touch_${f.name}()
            % endif

    cpdef touch_${f.name}(self):
        % if f.save:
        self.dirty_fields.add('${f.name}')
        % endif
        % if f.sync:
        self.sync_dirty_fields.add('${f.name}')
            % if f.cycle and fieldsmap[f.timestamp].sync:
        #self.sync_dirty_fields.add('${f.timestamp}')
            % endif
        % endif
        % for ff in f.effect_set:
        self.__${ff.name} = None
        % endfor
        % for ff in f.effect_set:
        self.clear_${ff.name}()
        % endfor
        % if f.event:
        if self._initialized:
            value = self.${f.name}
            for callback in type(self)._listeners_${f.name}:
                callback(self, value)
        % endif
        pass
    % endfor

    # formula fields
    % for f in fields['formula']:
    % if f.cache:
    cdef public object __${f.name}
    property ${f.name}:
        def __get__(self):
            if self.__${f.name} is None:
                value = ${replace_var_for_mako(f.formula)}
                self.__${f.name} = ${get_py_field_type(f.type, 'value')}
            return self.__${f.name}
        def __set__(self, value):
            assert self.__${f.name} is None, 'can only set formula attribute when initialize'
            % if f.type == 'string':
            if isinstance(value, str):
                value = value.decode('utf-8')
            % endif
            value = ${get_py_field_type(f.type, 'value')}
            self.__${f.name} = value
    cpdef clear_${f.name}(self):
        self.__${f.name} = None
        % if f.save:
        self.set_dirty('${f.name}')
        % endif
        % if f.sync:
        self.set_sync_dirty('${f.name}')
        % endif
        % if f.event:
        if self._initialized:
            for callback in type(self)._listeners_${f.name}:
                callback(self, None)
        % endif
    % else:
    property ${f.name}:
        def __get__(self):
            value = ${replace_var_for_mako(f.formula)}
            return ${get_py_field_type(f.type, 'value')}
    % endif
    % endfor

    % for name in ['dirty', 'sync_dirty']:
    cpdef has_${name}(self):
        return bool(self.${name}_fields)

    cpdef set_${name}(self, name):
        self.${name}_fields.add(name)

    cpdef set get_${name}(self):
        return self.${name}_fields

    cpdef set pop_${name}(self):
        cdef set fs = self.${name}_fields
        self.${name}_fields = set()
        return fs

    cpdef is_${name}(self, name):
        return name in self.${name}_fields

    cpdef remove_${name}(self, fields):
        for f in fields:
            try:
                self.${name}_fields.remove(f)
            except KeyError:
                pass
    % endfor

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
