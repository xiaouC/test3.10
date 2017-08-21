# coding: utf-8
from yy.entity import create_class, define, init_fields

import cPickle
import ujson as json
import msgpack

extra_imports = '''
from collections import defaultdict, deque
'''


def encode_dict(v):
    return json.dumps(map(lambda s: sorted(s.items(), key=lambda s: s[0]), v))


def decode_dict(v):
    return map(dict, json.loads(v))


player_fields = init_fields([
    define(0x0001, "userID",        "integer",  "用户ID",           save=True),
    define(0x0002, "username",      "string",   "用户名",           save=True),
    define(0x0003, "level",         "integer",  "等级",             save=True, sync=True),
    define(0x0004, "money",         "integer",  "金币",             save=True, sync=True),
    define(0x0005, "gold",          "integer",  "钻石",             save=True, sync=True),
    define(0x0006, "head_icon",     "integer",  "头像图标",         save=True),
    define(0x0007, "sex",           "integer",  "性别",             save=True, sync=True),
    define(0x0008, "lastlogin",     "datetime", "最后一次登录时间", save=True),
    define(0x0009, "totallogin",    "integer",  "累计登录次数",     save=True),
    define(0x0010, "seriallogin",   "integer",  "连续登录次数",     save=True),
])

store_tag = 'p'
PlayerBase = create_class('PlayerBase', player_fields, store_tag)

if __name__ == '__main__':
    import os
    from yy.entity import gen_cython
    c = gen_cython(player_fields.values(), 'c_PlayerBase', 'from player.define import PlayerBase as PureEntity', store_tag, extra_imports)
    open(os.path.join(os.path.dirname(__file__), 'c_player.pyx'), 'w').write(c)
