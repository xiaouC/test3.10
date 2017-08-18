#coding:utf-8
u'''
    >>> from .fields import *
    >>> class TestConfig(Config):
    ...     t1 = IntegerField(u'测试1', key=True)
    ...     t2 = BooleanField(u'测试2', required=False)
    ...     t3 = JSONField(u'测试3')
    ...     t4 = StringField(u'测试4')
    ...     t5 = FloatField(u'测试5')
    ...
    >>> TestConfig.haskey()
    True
    >>> header = (u'测试1', u'测试2', u'测试3', u'测试4', u'测试5')
    >>> d = TestConfig.load_csv_row(header, (1, 1, '[]', '', 34.234))
    >>> d = TestConfig.validate(d)
    >>> d['t1']
    1
    >>> d['t2']
    True
    >>> d['t3']
    []
    >>> d['t4']
    u''
    >>> d['t5']
    34.234
    >>> d = TestConfig.load_csv_row(header, (1.0, '1', '[]', '', '34.234'))
    >>> d = TestConfig.validate(d)
    >>> d['t1']
    1
    >>> d['t2']
    True
    >>> d['t3']
    []
    >>> d['t4']
    u''
    >>> d['t5']
    34.234
    >>> class SubConfig(TestConfig):
    ...     t5 = IntegerField(u'测试6')
    ...
    Traceback (most recent call last):
        ...
    DuplicateFieldError: t5 is defined in both SubConfig and TestConfig
    >>> instance = TestConfig.namedtuple(*TestConfig.to_tuple(d))
    >>> instance.t1
    1
    >>> instance.t2
    True
    >>> instance.t3
    []
    >>> instance.t4
    u''
    >>> instance.t5
    34.234
'''
from collections import namedtuple, OrderedDict
from itertools import count as icount
from .fields import Field, ValidationError

class DuplicateFieldError(Exception):
    pass

class DuplicateKeyError(Exception):
    pass

class ConfigMeta(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super(ConfigMeta, cls).__new__(cls, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, ConfigMeta)]

        # 合并父类定义的字段
        fields_list = []
        for p in parents:
            fields_list += p.fields_list

        new_list = []
        for fname, f in attrs.items():
            if isinstance(f, Field):
                f.init_class(new_cls, fname)
                new_list.append(f)

        fields_list += new_list

        # 检查重复定义的字段
        fields_map = {}
        for f in fields_list:
            if f.name in fields_map:
                raise DuplicateFieldError('%s is defined in both %s and %s' % (f.name, f.defined_class.__name__, fields_map[f.name].defined_class.__name__))
            fields_map[f.name] = f

        # 按照创建顺序排序
        fields_list.sort(key=lambda o:o.creation_counter)

        # 找到主键
        new_cls.key_field = None
        new_cls.groupkey_field = None
        new_cls.subkey_field = None
        for f in fields_list:
            if f.key:
                if new_cls.key_field is not None:
                    raise DuplicateKeyError("Duplicate key field")
                new_cls.key_field = f
            elif f.groupkey:
                if new_cls.key_field is not None or new_cls.groupkey_field is not None:
                    raise DuplicateKeyError("Duplicate key/groupkey field")
                new_cls.groupkey_field = f
            elif f.subkey:
                if new_cls.subkey_field is not None:
                    raise DuplicateKeyError("Duplicate subkey field")
                new_cls.subkey_field = f

        if new_cls.subkey_field is not None:
            assert new_cls.groupkey_field is not None, u'subkey 不能脱离 groupkey 单独存在'

        new_cls.fields_list = fields_list
        new_cls.fields = fields_map
        new_cls.fields_by_column = dict((f.column_name, f) for f in fields_list)
        new_cls.namedtuple = namedtuple(name, [f.name for f in fields_list])

        # 继承 __Meta__
        d = {}
        for b in reversed(bases):
            if hasattr(b, '__Meta__'):
                d.update(b.__Meta__.__dict__)
        if hasattr(new_cls, '__Meta__'):
            d.update(new_cls.__Meta__.__dict__)
            new_cls.__Meta__.__dict__ = d

        return new_cls

class Config(object):
    '''
    @fields_list    字段列表
    @fields_map     按字段名索引
    @key_field      主键
    @groupkey_field      分组主键
    '''
    __metaclass__ = ConfigMeta

    @classmethod
    def haskey(cls):
        return bool(cls.__Meta__.unique_together or cls.key_field or cls.groupkey_field)

    @classmethod
    def getkey(cls, attrs):
        if cls.__Meta__.unique_together:
            tmp = []
            for e in cls.__Meta__.unique_together:
                tmp.append(attrs[e])
            return tuple(tmp), False
        elif cls.key_field:
            return attrs[cls.key_field.name], False
        elif cls.groupkey_field:
            return attrs[cls.groupkey_field.name], True
        else:
            return None, False

    @classmethod
    def get_container(cls):
        return OrderedDict() if cls.haskey() else []

    @classmethod
    def load_csv(cls, table, header, reader, path=None):
        '''
        @path 如果csv是来自文件，则是文件的路径。如果csv来自文本，则路径为空
        本方法会做配置内部的校验，关联校验在 loadcsv 模块中。
        '''
        cls._path = path
        cls._current_table = table

        data = cls.get_container()
        keys = set()
        isempty = True

        bottom_empty_line = False
        for lineno, row in enumerate(reader, 1):
            if not row:
                if not bottom_empty_line:
                    bottom_empty_line = True
                continue#跳过末尾空行
            if bottom_empty_line:
                # 文件中间有空行，报错
                raise ValidationError(u'第 %s 行前面有空行'%(lineno,))
            attrs = cls.load_csv_row(header, row)
            attrs = cls.validate(attrs, lineno)

            key, grouped = cls.getkey(attrs)

            if cls.haskey() and not cls.groupkey_field:
                if key in keys:
                    raise ValidationError(u'第 %s 行有重复的字段 %s'%(lineno, key))
                keys.add(key)

            if cls.haskey():
                if grouped:
                    if key not in data:
                        if cls.subkey_field is not None:
                            data[key] = {}
                        else:
                            data[key] = []
                    if cls.subkey_field is not None:
                        subkey = attrs[cls.subkey_field.name]
                        if subkey in data[key]:
                            raise ValidationError(u'第 %s 行有重复的字段，字段名 %s，值 %s' % (lineno, cls.subkey_field.name, subkey))
                        data[key][subkey] = attrs
                    else:
                        data[key].append(attrs)
                else:
                    data[key] = attrs
            else:
                data.append(attrs)

            isempty = False

        assert not isempty, u'文件 %s 为空'%path
        return data

    @classmethod
    def load_csv_row(cls, header, row):
        return dict(zip(header, row))

    @classmethod
    def validate(cls, csvrow, lineno=None):
        cleaned = {}
        for f in cls.fields_list:
            v = None
            if not f.repeated:
                try:
                    v = csvrow[f.column_name]
                    v = f.validate(v, lineno)
                except KeyError:
                    if cls._current_table not in f.allowmiss:
                        raise ValidationError(u'第 %s 行没有字段 %s' % (lineno, f.column_name))
                    v = getattr(f, 'default', None)
            else:
                data = []
                is_infinite = isinstance(f.range, (int, long))#是否不指定终止点
                range = icount(f.range) if is_infinite else f.range
                for i in range:
                    column_name = f.column_name + str(i)
                    try:
                        v = csvrow[column_name]
                    except KeyError:
                        if is_infinite or cls._current_table in f.allowmiss:
                            break
                        else:
                            raise ValidationError(u'第 %s 行没有字段 %s' % (lineno, column_name))
                    v = f.validate(v, lineno)

                    if v is not None and not (not v and f.skipzero):#过滤零
                        data.append(v)

                v = data

            if v is not None:
                cleaned[f.name] = v

        for f in cls.fields_list:
            if hasattr(cls, 'validate_%s'%f.name):
                getattr(cls, 'validate_%s'%f.name)(cleaned[f.name], cleaned)

        return cleaned

    @classmethod
    def to_tuple(cls, cleanedrow):
        return tuple(cleanedrow.get(f.name) for f in cls.fields_list)

    @classmethod
    def post_validation(cls, alldata):
        '在所有配置加载完成后，做全局校验，比如外键'
        data = alldata[cls.__name__]
        items = data.values() if isinstance(data, dict) else data
        for f in cls.fields_list:
            if f.related is None:
                continue
            if isinstance(f.related, basestring):
                related = __import__('.configs', f.related)[f.related]
            else:
                related = f.related
            related_data = alldata[related.__name__]
            for lineno, item in enumerate(items):
                if not f.repeated:
                    if item[f.name] not in related_data:
                        raise ValidationError(u'文件 %s 第 %s 行字段 %s 的值 %s 在表 %s 中不存在' % (
                                cls.__Meta__.table, lineno, f.name, item[f.name], related.__Meta__.table))
                else:
                    for value in item[f.name]:
                        if value not in related_data:
                            raise ValidationError(u'文件 %s 第 %s 行字段 %s 的值 %s 在表 %s 中不存在' % (
                                    cls.__Meta__.table, lineno, f.name, value, related.__Meta__.table))

    class __Meta__:
        table = None            # 对应csv文件名
        unique_together = None  # 约束条件
        dict_class = dict       # 容器类型 dict / OrderedDict

if __name__ == '__main__':
    import doctest
    doctest.testmod()
