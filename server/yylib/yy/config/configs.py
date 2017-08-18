#coding:utf-8
import json
from .base import ValidationError
from .fields import *

def default_decoder(self, v, lineno=None):
    return v

def decode_delimited_float(s):
    return map(float, s.split(','))

def default_decoder_vertical_line(self, v, lineno=None):
    if v in (0, '0', ''):
        return []
    try:
       ret = map(int, v.split('|'))
    except ValueError as e:
        raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (
                lineno, self.column_name, self.name, str(e), repr(v)))
    return ret

_registereds = []

def register_config(cls):
    assert cls.__Meta__.table is not None, 'registered config must define table'
    _registereds.append(cls)
    return cls

def get_registereds():
    return _registereds
