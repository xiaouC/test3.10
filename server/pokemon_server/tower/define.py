#!/usr/bin/env python
# -*- coding: utf-8 -*-

from yy.entity import create_class, define, init_fields
from yy.entity.formulas import register_formula
from tower import formulas

import ujson as json

extra_imports = '''
'''

floor_fields = init_fields([
    define(0x0001, "entityID", "integer", "实体ID", save=True),
    define(0x0002, "floor", "integer", "层数", save=True),
    define(0x0003, "idx", "object", "派驻索引", formula='fn.get_idx(floor)'),
    define(0x0004, "idx_p", "object", "派驻保护索引", formula='fn.get_idx_p(floor)'),
    define(0x0005, "lock", "object", "匹配忽略索引", formula='fn.get_lock(floor)'),
    define(0x0006, "limit", "integer", "派驻上限", save=True),
    define(0x0007, "payoff", "integer", "统一结算时间", save=True),
])

store_tag = 'l'
FloorBase = create_class("FloorBase", floor_fields, store_tag)

if __name__ == '__main__':
    import os
    from yy.entity import gen_cython
    c = gen_cython(floor_fields.values(), 'c_FloorBase', 'from tower.define import FloorBase as PureEntity', store_tag, extra_imports)
    open(os.path.join(os.path.dirname(__file__), 'c_floor.pyx'), 'w').write(c)
