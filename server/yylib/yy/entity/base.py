# coding: utf-8
'''
Model类
'''
import logging
logger = logging.getLogger("entity")

import time
import json
import traceback
from copy import copy
from datetime import date as datedate, timedelta
from collections import OrderedDict

from yy.utils import OrderedSet
from .attributes import define
import fields

class EntityNotFoundError(Exception):
    pass

class CanNotCreateError(Exception):
    pass

class CanNotDeleteError(Exception):
    pass

class EntityExistsException(Exception):
    def __init__(self, key):
        self.key = key
    def __unicode__(self):
        return self.key

def recursive_var_set_save(fields, f):
    '递归取得公式属性依赖的所有持久化属性'
    if f.save:
        return OrderedSet([f])
    elif hasattr(f, 'var_set'):
        r = OrderedSet()
        for name in f.var_set:
            r |= recursive_var_set_save(fields, fields[name])
        return r
    else:
        return OrderedSet()

def recursive_var_set(fields, f):
    '递归取得公式属性依赖的所有普通属性'
    if hasattr(f, 'var_set'):
        r = OrderedSet()
        for name in f.var_set:
            r |= recursive_var_set(fields, fields[name])
        return r
    else:
        return OrderedSet([f])

def cycle(self, fields=None, now=None):
    if not now:
        now = int(time.time())
    tomorrow = int(time.mktime((datedate.fromtimestamp(now) + timedelta(days=1)).timetuple()))
    if not fields:
        fields = self.fields_list
    else:
        fields_ = fields
        fields = []
        for f in fields_:
            fields.append(self.fields[f])

    for field in fields:
        if not field.cycle:
            continue

        updatetime = getattr(self, field.timestamp, 0)#下次更新的时间
        if field.resume:
            if not updatetime:
                setattr(self, field.timestamp, now + field.resume)
            elif updatetime <= now:#下次更新的时间已经到了，或者已经过去了
                interval = now - updatetime#超过的时间
                multi = interval // field.resume + 1 #超过的周期数 + 原本的一个周期
                rest  = interval % field.resume      #未达一个周期的剩余的时间
                max = getattr(self, field.max)
                old = getattr(self, field.name)
                if old < max:
                    new = min(old + multi * 1, max)
                    setattr(self, field.name, new)
                setattr(self, field.timestamp, now + field.resume - rest)#设置下次更新时间
        else:
            if updatetime:
                if datedate.fromtimestamp(updatetime) <= datedate.fromtimestamp(now):
                    if callable(field.default):
                        default = field.default()
                    else:
                        default = field.default
                    setattr(self, field.name, default)
            setattr(self, field.timestamp, tomorrow)

class EntityBase(type):
    store_tags = {}
    def __new__(cls, name, bases, attrs):
        super_new = super(EntityBase, cls).__new__
        attrs = attrs.copy()

        #assert attrs['store_tag'] not in EntityBase.store_tags

        parents = [b for b in bases if isinstance(b, EntityBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        new_cls = super_new(cls, name, bases, attrs)
        EntityBase.store_tags[attrs['store_tag']] = new_cls

        fields_list = []
        for p in parents:
            fields_list += p.fields_list

        new_list = []
        for fname, f in attrs.items():
            if isinstance(f, fields.Field):
                f.set_name(fname)
                new_list.append(f)
                del attrs[fname]

        new_list.sort(key=lambda o:o.creation_counter)
        fields_list += new_list

        fields_map = dict((f.name, f) for f in fields_list)
        fields_ids_map = dict((f.id, f) for f in fields_list)

        for f in fields_list:
            f.init_class(new_cls)

        setattr(new_cls, 'fields_list', fields_list)
        setattr(new_cls, 'fields', fields_map)
        setattr(new_cls, 'fields_ids_map', fields_ids_map)

        return new_cls

class Entity(object):
    __metaclass__ = EntityBase
    fields_list = []
    fields_map = {}
    fields_ids_map = {}

    def __init__(self, *args, **kwargs):
        self._initialized = False

        self._dirty_fields = set()
        self._sync_dirty_fields = set()
        #确保所有公式属性都被计算一次
        self._form_dirty_fields = set([f.name for f in self.fields_list if f.formula])

        for i, f in enumerate(self.fields_list):

            if f.private_name:
                setattr(self, f.private_name, None)

            if i < len(args):
                value = args[i]
            elif f.name in kwargs:
                value = kwargs[f.name]
            else:
                value = f.default
                if callable(value):
                    value = value()
            if f.type in ('json', 'sequence', 'object'):
                f.init_instance(self, copy(value))
            else:
                f.init_instance(self, value)

        self._initialized = True

    def __setattr__(self, name, value):
        if name[0]!='_' and self._initialized:
            # check name
            if name not in self.__class__.fields:
                raise Exception('field %s is not exists' % name)
                
        return super(Entity, self).__setattr__(name, value)

    def __unicode__(self):
        return ','.join('%s=%s' % (f.name, getattr(self, f.private_name)) for f in self.fields_list if f.private_name)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def has_dirty(self):
        return bool(self._dirty_fields)

    def set_dirty(self, name):
        self._dirty_fields.add(name)

    def get_dirty(self):
        return self._dirty_fields

    def pop_dirty(self):
        fs = self._dirty_fields
        self._dirty_fields = set()
        return fs

    def is_dirty(self, name):
        return name in self._dirty_fields

    def set_sync_dirty(self, name):
        self._sync_dirty_fields.add(name)

    def get_sync_dirty(self):
        return self._sync_dirty_fields

    def is_sync_dirty(self, name):
        return name in self._sync_dirty_fields

    def remove_sync_dirty(self,fields):
        s = self._sync_dirty_fields
        d = s - fields
        self._sync_dirty_fields = d
        return s & fields

    def pop_sync_dirty(self,syncSence = True):
        s = set()
        fs = self._sync_dirty_fields - s
        self._sync_dirty_fields = s
        return fs

    def set_form_dirty(self, name):
        self._form_dirty_fields.add(name)

    def is_form_dirty(self, name):
        return name in self._form_dirty_fields

    def pop_form_dirty(self, name):
        try:
            self._form_dirty_fields.remove(name)
        except KeyError:
            pass
    
    def validate(self):
        excs = []
        for f in self.fields_list:
            if f.private_name:
                try:
                    f.validate(getattr(self, f.private_name))
                except fields.ValidationError as e:
                    excs.append(e)

        if excs:
            raise fields.ValidationError('\n'.join(map(str, excs)))

    cycle = cycle

    def pop_dirty_values(self):
        return [(name, getattr(self, name)) for name in self.pop_dirty()]

    @classmethod
    def getAttributeByID(cls, id):
        return cls.fields_ids_map[id]

    @classmethod
    def getAttributeIDByName(cls, name):
        return cls.fields[name].id

def init_fields(fields):
    fieldsmap = OrderedDict()
    unique_id_set = set()
    for field in fields:
        if field.cycle:
            if isinstance(field.timestamp, int):
                #自动生成时间属性
                ts_id = isinstance(field.timestamp, int) and field.timestamp or field.id+1
                field_ts = define(ts_id, '%s_ts'%field.name, 'integer', '', save=True)
                fieldsmap[field_ts.name] = field_ts 
                field.timestamp = field_ts.name
                assert field_ts.id not in unique_id_set, '属性id 0x0%x `%s` 已经被定义过了(cycle属性占两个ID)。'%(field_ts.id, field_ts.name)
                unique_id_set.add(field_ts.id)

        fieldsmap[field.name] = field
        assert field.id not in unique_id_set, '属性id 0x0%x `%s` 已经被定义过了(cycle属性占两个ID)。'%(field.id, field.name)
        unique_id_set.add(field.id)

    #检查时间属性和属性最大值
    for name, field in fieldsmap.items():
        if field.cycle:
            assert field.timestamp in fieldsmap, 'field `{}` 的时间属性 `{}` 不存在。'.format(field.name, field.timestamp)
            if isinstance(field.max, basestring):
                assert field.max in fieldsmap, 'field `{}` 的最大值 `{}` 不存在。'.format(field.name, field.max)

    # 处理公式属性关联
    for f in fieldsmap.values():
        f.effect_set = OrderedSet()
        f.depend_set = OrderedSet()

    for f in fieldsmap.values():
        f.depend_set_save = recursive_var_set_save(fieldsmap, f)
        try:
            f.depend_set_save.remove(f)
        except KeyError:
            pass
        f.depend_set = recursive_var_set(fieldsmap, f)
        try:
            f.depend_set.remove(f)
        except KeyError:
            pass
        if f.cache:
            for f1 in f.depend_set:
                f1.effect_set.add(f)

    for name, field in fieldsmap.items():
        field.set_name(name)

    return fieldsmap

def create_class(classname, fieldsmap, store_tag):
    return EntityBase(classname, (Entity, ), dict(fieldsmap, store_tag=store_tag))

def gen_cython(fields_list, classname, import_pure, store_tag, extra_imports=''):
    import os
    from mako.template import Template
    path = os.path.join(os.path.dirname(__file__), 'entity_tpl.mako')
    return Template(filename=path, module_directory='/tmp', output_encoding='utf-8').render(**locals())

if __name__ == '__main__':
    import doctest
    doctest.testmod()
