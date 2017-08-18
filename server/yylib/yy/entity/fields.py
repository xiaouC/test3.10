# coding: utf-8
import logging
from datetime import datetime, date as datedate
from .containers import ListContainer, SetContainer, DictContainer, StoredListContainer, StoredSetContainer, StoredDictContainer

logger = logging.getLogger('entity')

__all__ = ( 'ValidationError'
          , 'register_field'
          , 'field_by_type'
          , 'Field'
          , 'BooleanField'
          , 'IntegerField'
          , 'FloatField'
          , 'StringField'
          , 'FormulaField'
          , 'SequenceField'
          , 'IncrementField'
          , 'ForeignField'
          , 'DatetimeField'
          , 'DatedateField'
          , 'ObjectField'
          , 'LuaTableField'
          )

datetimefmt = '%Y-%m-%d %H:%M'
datedatefmt = '%Y-%m-%d'

class ValidationError(Exception):
    pass

_fields_registry = {}

def field_by_type(t):
    return _fields_registry[t]

def register_field(cls):
    _fields_registry[cls.type_name] = cls
    return cls

def parse_lua_table(string):
    if string == '0':
        return {}
    dd = {}
    for each in string.split(','):
        each = each.strip()
        if not each:
            continue
        try:
            name, value = each.split('=')
        except ValueError:
            continue
        if value == 'true':
            value = True
        elif value == 'false':
            value = False
        else:
            value = eval(value)

        dd[name] = value
    return dd


class Field(object):
    creation_counter = 0
    type_name = None
    python_type = None

    def __init__(self, description  = ''
                     , default      = None
                     , required     = True
                     , **settings):

        '''
        @description    字段描述
        @default        默认值
        @required       是否必须
        @settings       其他选项
        '''
        #assert self.__class__.type_name, 'Can\'t create instance of Field'

        self.required = required
        self.description = description
        self.save = False # 是否持久化
        self.sync = False  # 是否同步客户端
        self.formula = None
        self.cycle = False

        self.__dict__.update(settings)

        self.creation_counter = Field.creation_counter

        if 'key' in settings:
            self.key = settings["key"]

        if "column_name" in settings:
            self.column_name = settings["column_name"]

        if "choices" in settings:
            self.choices = settings["choices"]

        self.default = default

        Field.creation_counter += 1

    def set_name(self, name):
        self.name = name
        if not getattr(self, "column_name", None):
            self.column_name = name
        self.private_name = '__'+name

    def init_class(self, cls):
        setattr(cls, self.name, property(self.get_instance, self.set_instance, self.del_instance))

    def init_instance(self, obj, value):
        if value!=None:
            setattr(obj, self.private_name, self.validate(value))

    def set_instance(self, obj, value):
        old = getattr(obj, self.private_name)
        new = self.validate(value)

        if new!=old:
            setattr(obj, self.private_name, new)

            #需要持久化的才加到dirty列表中
            if self.save:
                obj.set_dirty(self.name)

            # 记录同步客户端属性
            if self.sync:
                obj.set_sync_dirty(self.name)

            #需要更新的公式属性
            for f in self.effect_set:
                if f.formula:
                    obj.set_form_dirty(f.name)
                if f.sync:
                    obj.set_sync_dirty(f.name)

    def get_instance(self, obj):
        return getattr(obj, self.private_name)

    def del_instance(self, obj):
        delattr(obj, self.private_name)

@register_field
class ObjectField(Field):
    type_name = 'object'
    python_type = object

@register_field
class JSONField(Field):
    type_name = 'json'
    python_type = object

@register_field
class BooleanField(Field):
    type_name = 'boolean'
    python_type = bool

@register_field
class IntegerField(Field):
    type_name = 'integer'
    python_type = (int, long)

    def validate(self, v):
        if v=='':
            v = 0
        elif isinstance(v, float):
            v = int(v)
        return super(IntegerField, self).validate(v)

@register_field
class DatetimeField(Field):
    type_name = "datetime"
    python_type = datetime

    def validate(self, v):
        if isinstance(v, datetime):
            return v
        found = (v.strip().find(' ') > 0)
        if not found:
            v += ' 00:00'
        try:
            dt = datetime.strptime(v, datetimefmt)
        except:
            raise ValidationError('wrong datetime format')
        return dt

@register_field
class DatedateField(Field):
    type_name = "datedate"
    python_type = datedate

    def validate(self, v):
        if isinstance(v, datedate):
            return v
        try:
            dt = datedate.strptime(v, datedatefmt)
        except:
            raise ValidationError('wrong datedate format')
        return dt

@register_field
class FloatField(Field):
    type_name = 'float'
    python_type = float

    def validate(self, v):
        if v=='':
            v = 0.0
        return super(FloatField, self).validate(v)

@register_field
class StringField(Field):
    type_name = 'string'
    python_type = (str, unicode)

    def validate(self, v):
        if v=='0':
            v = ''
        if isinstance(v, str):
            try:
                v = v.decode('utf-8')
            except UnicodeDecodeError:
                v = v.decode('gbk')
        return super(StringField, self).validate(v)

@register_field
class SequenceField(Field):
    type_name = 'sequence'
    python_type = (list, tuple)

@register_field
class DictField(Field):
    type_name = 'dict'
    python_type = (dict,)

@register_field
class SetField(Field):
    type_name = 'set'
    python_type = (set,)

@register_field
class IncrementField(Field):
    next_id = 0
    type_name = "increment"
    python_type = int

    def init_instance(self, obj, value=None):
        assert value==None, 'IncrementField don\'t accept value'
        value = IncrementField.next_id
        IncrementField.next_id += 1
        super(IncrementField, self).init_instance(obj, value)

    def set_instance(self, obj, value):
        raise Exception("IncrementField field don't accept value")

@register_field
class FormulaField(Field):
    type_name = 'formula'
    python_type = object

    def __init__(self, *args, **kwargs):
        super(FormulaField, self).__init__(*args, **kwargs)
        assert callable(self.formula_lambda), 'Need valid formula'

    def set_name(self, name):
        super(FormulaField, self).set_name(name)
        #self.private_name = None

    def init_class(self, cls):
        setattr(cls, self.name, property(self.get_instance, self.set_instance))

    def init_instance(self, obj, value):
        from yy.entity.context import AttributeContext
        obj.attribute_context = AttributeContext(obj)

    def get_instance(self, obj):
        if not self.cache:
            return self.formula_lambda(obj.attribute_context)
        #缓存公式属性
        if obj.is_form_dirty(self.name):
            v = self.formula_lambda(obj.attribute_context)
            obj.pop_form_dirty(self.name)
            setattr(obj, self.private_name, v)
        else:
            v = getattr(obj, self.private_name)
        return v

    def set_instance(self, obj, value):
        if self.saveOnQuit:
            return
        raise Exception("Formula field don't accept value")

@register_field
class ForeignField(Field):
    type_name = 'foreign'
    python_type = (int or long)

    def __init__(self, *args, **kwargs):
        if not kwargs.get('related'):
            raise Exception('foreign field has not related config')
        self.related = kwargs['related']
        self.allow_zero = kwargs.get('allow_zero', True)#允许为零, 不检查关联表
        super(ForeignField, self).__init__(*args, **kwargs)

    def validate(self, v):
        if v == '' or v is None:
            v = 0
        v = super(ForeignField, self).validate(v)
        return v

    def init_instance(self, obj, value):
        table = obj.__Meta__.table
        v = self.validate(value)
        if not (self.allow_zero and v == 0):
            from config.loaders import pending_look_up
            from config.loaders import _config_cache
            try:
                if isinstance(self.related, basestring):
                    related_tbl = self.related
                else:
                    related_tbl = self.related.__Meta__.table
                related = _config_cache[related_tbl]
            except KeyError:
                # Try to look up the related config
                pending_look_up.add((v, self.related, table))
            if not v in related:
                pending_look_up.add((v, self.related, table))
        setattr(obj, self.private_name, v)

@register_field
class LuaTableField(Field):
    type_name = 'lua_table'
    python_type = dict

    def validate(self, v):
        return parse_lua_table(v)
