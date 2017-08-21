# coding:utf-8
import os
import ujson
import logging
logger = logging.getLogger("config")
from datetime import time as timetime

from yy.config.fields import *  # NOQA
from yy.config.base import Config
from yy.config.configs import default_decoder_vertical_line
from yy.config.configs import register_config, get_registereds
from yy.config.cache import get_config, get_config_by_name
from yy.utils import trie


def default_decoder_by(seq):
    def default_decoder(self, v, lineno=None):
        if v in (0, '0', ''):
            return []
        try:
            ret = map(int, v.split(seq))
        except ValueError as e:
            raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (lineno, self.column_name, self.name, str(e), repr(v)))
        return ret
    return default_decoder


def decode_rewards(self, v, lineno=None):
    if v in (0, '0', ''):
        return []
    try:
        ls = map(int, v.split('|'))
        if len(ls) == 2:
            ls.insert(1, 0)
        ret = dict(zip(('type', 'arg', 'count'), ls))
    except ValueError as e:
        raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (lineno, self.column_name, self.name, str(e), repr(v)))
    return ret


def decode_json(self, v, lineno=None):
    if v in (0, '0', ''):
        return []
    try:
        v = v.replace("'", '"')
        ret = ujson.loads(v)
    except ValueError as e:
        raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (lineno, self.column_name, self.name, str(e), repr(v)))
    return ret


def docode_timetime(self, v, lineno=None):
    try:
        hour, minute = map(int, v.split(":", 1))
        # 配置需要导成JSON，不支持timetime类，所以还是返回字符串
        timetime(hour, minute)
    except ValueError as e:
        raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (lineno, self.column_name, self.name, str(e), repr(v)))
    return v


CURDIR = os.path.dirname(__file__)
forbid_names_trie = trie.trie_empty()
dirty_words_trie = trie.trie_empty()


def reload_dirty_words():
    lines = open(os.path.join(CURDIR, '../data/dirty_words.txt')).readlines()
    dirty_words_list = [line.strip().decode('utf-8') for line in lines if line.strip()]
    trie.trie_clear(dirty_words_trie)
    trie.trie_append(dirty_words_trie, dirty_words_list)

    lines = open(os.path.join(CURDIR, '../data/forbid_names.txt')).readlines()
    forbid_name_list = [line.strip().decode('utf-8') for line in lines if line.strip()]
    trie.trie_clear(forbid_names_trie)
    trie.trie_append(forbid_names_trie, forbid_name_list + dirty_words_list)

reload_dirty_words()


@register_config
class CreatePlayerConfig(Config):
    # 初始属性
    sex = IntegerField(u'sex')
    money = IntegerField(u'money')
    gold = IntegerField(u'gold')

    class __Meta__:
        table = 'CreatePlayer'
        unique_together = ('sex', 'career')
