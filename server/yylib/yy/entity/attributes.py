#-*- coding:utf-8 -*-

import json
import cPickle
from collections import namedtuple, defaultdict
from yy.utils.importlib import import_module
from datetime import datetime
from time import mktime
from .compiler import compile
from .fields import field_by_type, Field
from .containers import ListContainer, DictContainer, SetContainer

def make_field(attr):
    attrs = attr._asdict()

    if attr.formula:
        t = 'formula'
        attrs['var_set'], attrs['formula_lambda'] = compile(attr.formula)
    else:
        t = attr.type
        attrs['default'] = attr.default    

    cls = Field
    attrs['is_entity'] = True
    return cls(**attrs)

def decode_json_set(s):
    return set(json.loads(s))

def encode_json_set(s):
    return json.dumps(list(s))

def decode_json_defaultdict_int(s):
    return defaultdict(int, json.loads(s))

def decode_pickle(s):
    return cPickle.loads(str(s))

def encode_pickle(s):
    return cPickle.dumps(s)

def noop(o):
    return o

Attribute = namedtuple("Attribute", ("id"          #属性id
                                   , "name"        #名字
                                   , "type"        #类型
                                   , "description" #描述
                                   , "saveOnQuit"  #战斗属性特殊处理
                                   , "save"      #持久
                                   , "sync"      #同步
                                   , "syncTimeout" #同步时与当前时间相减
                                   , "default"     #default value
                                   , "encoder"
                                   , "decoder"
                                   , "formula"        #公式
                                   , "cache"       #公式属性是否缓存
                                   , "cycle"     #是否恢复或重置属性
                                   , "resume"      #0为重置属性，其他为恢复间隔时长，单位是分钟
                                   , "timestamp"   #cycle属性所对应的上次作用时间的属性名，
                                                   #当为None时，自动生成一个属性，id为该字段的属性id加1，
                                                   #所以，会占用两个属性ID
                                   , "max"         #恢复属性的最大值，字符串表示为所关联的属性名，数字代表最大值, None时不判断
                                   , "isBase"      #用于分表存储
                                   , 'raw_default' # 用于生成cython时，表达复杂的默认值表达式
                                   , 'event'
                                   , 'int_key'
                                   , 'int_value'
                       ))

def encode_datetime(d):
    return int(mktime(d.timetuple()))

def decode_datetime(n):
    return datetime.fromtimestamp(float(n))

def define(*args, **kwargs):
    '''不传默认值时，根据类型补全'''
    # 默认值
    default_attrs = {
        'saveOnQuit': False,
        'save': False,
        'sync': False,
        'syncTimeout': False,
        'encoder': None,
        'decoder': None,
        'formula': None,
        'cache':True,
        'cycle':False,
        'resume':0,
        'timestamp':None,
        'max':None,
        'isBase':False,
        'raw_default': None,
        'event': False,
        'int_key': False,
        'int_value': False,
    }
    m = {}
    for idx, name in enumerate(Attribute._fields):
        try:
            m[name] = args[idx]
        except IndexError:
            if name in kwargs:
                m[name] = kwargs[name]

    if m.get('cycle', False) and 'save' not in m:
        m['save'] = True

    if m.get('cycle', False):
        assert 'timestamp' in m, 'cycle attribute %s not define timestamp' % m['name']

    if m['type'] in ['sequence', 'dict', 'set', 'stored_sequence', 'stored_dict', 'stored_set']:
        assert 'default' not in m, 'container attribute don\'t need default value'

    if m['type'] in ['stored_sequence', 'stored_dict', 'stored_set']:
        assert 'save' not in m and 'sync' not in m and 'formula' not in m, 'stored container attribute don\'t need save/sync/formula'

    if m['type'] == 'datetime':
        if 'encoder' not in m:
            m['encoder'] = encode_datetime
        if 'decoder' not in m:
            m['decoder'] = decode_datetime

    if m.get('formula') and m.get('cache', True)==False:
        assert not m.get('save', False), 'only cached formula can persist %s' % m['name']

    for k,v in default_attrs.items():
        if k not in m:
            m[k] = v

    defaults = {
        'integer': 0,
        'float': 0.0,
        'string': None,
        'boolean': False,
        'sequence': ListContainer,
        'dict': DictContainer,
        'set': SetContainer,
    }
    type = m['type']
    if 'default' not in m:
        m['default'] = defaults.get(type)
    return make_field(Attribute(**m))
