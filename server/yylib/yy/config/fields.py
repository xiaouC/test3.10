# coding: utf-8
import logging
from datetime import datetime
import ujson

__all__ = (
    'ValidationError',
    'Field',
    'CustomField',
    'JSONField',
    'BooleanField',
    'IntegerField',
    'DatetimeField',
    'FloatField',
    'StringField')

DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M'


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


class ValidationError(Exception):

    def __str__(self):
        return "see message for content"


class Field(object):
    creation_counter = 0  # 用户字段排序
    python_type = object  # 对应python对象的类型，用于校验

    def __init__(
        self,
        column_name=None,
        default=None,
        required=True,
        key=False,
        choices=None,
        repeated=False,
        range=None,
        skipzero=False,
        related=None,
        groupkey=False,
        subkey=False,
        allowmiss=None,
    ):
        '''
        @column_name    中文字段名
        @default        默认值
        @required       是否必须
        @key            是否主键
        @choices        枚举选项
        @repeated       是否列表
        @range          列表字段读csv时的范围, 可以只指定起始点
        @skipzero       列表字段, 过滤0
        @allowmiss      允许哪些配置表没有这个字段, 如果没有default, 则为None
        '''
        self.column_name = column_name
        self.required = required
        self.key = key
        # 支持直接传入一个类
        if hasattr(choices, '__dict__'):
            enums = choices
            choices = []
            for k, v in enums.__dict__.items():
                if not k.startswith('__'):
                    choices.append((v, k))
            choices = tuple(sorted(choices))
        self.choices = choices

        self.repeated = repeated
        self.range = range
        self.skipzero = skipzero
        if repeated:
            self.required = False
            assert self.range is not None,\
                'must specify range for repeated field'

        self.allowmiss = allowmiss or tuple()
        if default is not None:
            default = self.validate(default)

        self.default = default

        # 外键关联，校验的时候有用
        self.related = related

        # 分组主键
        self.groupkey = groupkey
        self.subkey = subkey

        assert not (self.groupkey and self.key), u'groupkey和key不能同时存在'

        # 在哪个类中定义的
        self.defined_class = None
        # 用于排序
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    def init_class(self, cls, name):
        '在ConfigMeta中被初始化'
        self.defined_class = cls
        self.name = name

    def validate(self, v, lineno=None):
        '''
        默认校验方法, required, python_type, choices
        '''
        v = self.convert(v, lineno)

        if self.choices is not None:
            for e in self.choices:
                if isinstance(e, tuple) and len(e) == 2:
                    value, _ = e
                else:
                    value = e
                if value == v:
                    break
            else:
                raise ValidationError(
                    u'在第 %s 行，字段 %s(%s) 的值 `%s` 不在枚举中: %s' %
                    (lineno, self.column_name,
                     self.name, repr(v),
                     self.choices))

        if v is None and self.required:
            if self.default is not None:
                return self.default
            raise ValidationError(
                u'在第 %s 行，字段 %s(%s) 是必须的, 但是没有设置' %
                (lineno, self.column_name, self.name))

        return v

    def convert(self, v, lineno=None):
        if not isinstance(v, self.python_type):
            try:
                if callable(self.python_type):
                    force_convert = self.python_type
                else:
                    force_convert = self.python_type[0]
                v = force_convert(v)
            except ValueError:
                raise ValidationError(
                    u'在第 %s 行，字段 %s(%s) 需要是%s类型，但是设置了类型为%s的值: %s' %
                    (lineno,
                     self.column_name,
                     self.name,
                     self.python_type,
                     type(v),
                        repr(v)))

        return v


class CustomField(Field):

    def __init__(self, *args, **kwargs):
        decoder = kwargs.pop('decoder')
        if not decoder or not callable(decoder):
            raise Exception('must provide decoder for custom field')
        self.decoder = decoder
        super(CustomField, self).__init__(*args, **kwargs)

    def convert(self, v, lineno=None):
        return self.decoder(self, v, lineno)


class JSONField(Field):

    def convert(self, v, lineno=None):
        try:
            return ujson.loads(v)
        except ValueError:
            raise ValidationError(u'在第 %s 行，字段 %s(%s) 的值 `%s` 不是有效的json' % (
                lineno, self.column_name, self.name, repr(v)))


class BooleanField(Field):
    python_type = bool

    def convert(self, v, lineno=None):
        if v not in ('0', '1', 0, 1, 'true', 'false', True, False):
            raise ValidationError(u'在第 %s 行，字段 %s(%s) 的值 `%s` 不是有效的布尔值' % (
                lineno, self.column_name, self.name, repr(v)))
        if v in ('0', 0, 'false', False):
            return False
        else:
            return True


class IntegerField(Field):
    python_type = (int, long)

    def convert(self, v, lineno=None):
        if v == '':
            return None
        if isinstance(v, str):  # FIXME NOTE  fightmonster 浮点数 问题
            return int(float(v))
        # if isinstance(v, float) and int(v)!=v:
        #    raise ValidationError(u'在第 %s 行，字段 %s(%s) 的值 `%s` 不是有效的整数值' % (
        #            lineno, self.column_name, self.name, repr(v)))

        return super(IntegerField, self).convert(v)


class DatetimeField(Field):
    python_type = datetime

    def convert(self, v, lineno=None):
        if not self.required and not v:
            return v

        if isinstance(v, (str, unicode)):
            found = (v.strip().find(' ') > 0)
            if not found:
                v += ' 00:00'

            try:
                return datetime.strptime(v[0:16], DEFAULT_TIME_FORMAT)
            except ValueError:
                raise ValidationError(
                    u'在第 %s 行，字段 %s(%s) 的值 `%s` 不是有效的日期时间格式' %
                    (lineno, self.column_name, self.name, repr(v)))
        elif isinstance(v, datetime):
            return v
        else:
            raise ValidationError(u'在第 %s 行，字段 %s(%s) 的值 `%s` 不是日期时间' % (
                lineno, self.column_name, self.name, repr(v)))


class FloatField(Field):
    python_type = float


class StringField(Field):
    python_type = (str, unicode)

    def convert(self, v, lineno=None):
        if v == '0':  # csv潜规则
            return u''
        if isinstance(v, str):
            try:
                return v.decode('utf-8')
            except UnicodeDecodeError:
                raise ValidationError(
                    u'在第 %s 行，字段 %s(%s) 的值 `%s` 不是有效的utf-8编码' %
                    (lineno, self.column_name, self.name, repr(v)))
        elif isinstance(v, unicode):
            return v
        else:
            raise ValidationError(u'在第 %s 行，字段 %s(%s) 的值 `%s` 不是字符串' % (
                lineno, self.column_name, self.name, repr(v)))
