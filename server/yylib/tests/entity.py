# coding: utf-8
from yy.entity import create_class, define, init_fields
from yy.entity.formulas import register_formula
import cPickle

import ujson as json

extra_imports = '''
from collections import defaultdict
'''

player_fields = init_fields(
    define(0x000b, "entityID", "integer", "", save=True),
    define(0x0001, "plain", "integer", ""),
    define(0x0002, "persistent", "integer", "", save=True, sync=True),
    define(0x0003, "formula1", "integer", "", formula="plain + 1", sync=True),
    define(0x0004, "formula2", "integer", "", formula="plain + 2", save=True),
    define(0x0005, "formula3", "integer", "", formula="formula2 + 2", event=True),

    define(0x0006, "sp", "integer", "", cycle=True, timestamp='sp_update_time', resume=10, max='sp_max', default=0),
    # 0x0007 sp_ts
    define(0x0008, "sp_max", "integer", "", default=10),
    define(0x0024, "sp_update_time", "integer", "", sync=True, save=True, default=0),

    define(0x0009, "left_count", "integer", "", cycle=True, resume=0, default=10, timestamp='left_count_update_time'),
    define(0x000a, "left_count_update_time", "integer", ""),

    define(0x000c, "list_value", "sequence", "", cycle=True, timestamp=0x0015, sync=True, save=True, encoder=json.encode, decoder=json.decode),
    define(0x000d, "string_value", "string", ""),
    define(0x000e, "dict_value", "dict", "", save=True, sync=True, encoder=json.encode, decoder=json.decode),
    define(0x000f, "default_dict_value", "object", "", encoder=json.encode, decoder=json.decode, raw_default='defaultdict(int)'),
    define(0x0010, "set_value", "set", "", save=True, sync=True, encoder=json.encode, decoder=json.decode),

    define(0x0011, "some_cd_value", "integer", "", cycle=True, timestamp=0x0012, save=True, sync=True, syncTimeout=True),
    define(0x0013, "float_value", "float", "", save=True, sync=True),

    define(0x0014, "datetime_value", "datetime", "", save=True, sync=True),

    # 普通属性排行榜
    define(0x0016, "natural_score",   "integer", "", sync=True, default=10),
    define(0x001A, "natural_ranking", "integer", "", formula='fn.get_challenge_rank(entityID)'),
    define(0x0017, "rank",  "integer", ""),
    define(0x0018, "depend_on_formula3", "integer", ""),
    define(0x0019, "rank2",  "integer", ""),

    # 材料背包 测试stored_dict
    define(0x001B, 'pack', 'stored_dict', '', int_key=True, int_value=True),
    # 材料背包 测试stored_set
    define(0x001C, 'rewards', 'stored_set', '', int_value=True),

    # 依赖持久属性的公式属性
    define(0x001D, "persist_formula1", "integer", "", formula="persistent + 1"),
    define(0x001E, "persist_formula2", "integer", "", formula="persist_formula1 + 1"),
    define(0x001F, 'fbs',  'stored_dict', '', int_key=True, encoder=json.encode, decoder=json.decode),

    define(0x0020, "integer_formula", "integer", "", formula="plain*0.1"),

    define(0x0021, "name", "string", "", save=True),

    define(0x0022, "worldID", "integer", "", save=True),
    define(0x0023, "bool_value", "boolean", "", save=True),

    define(0x0025, "natural_ranking2",  "integer", "", formula='fn.get_challenge_rank2(entityID)'),
    define(0x0026, "natural_score2",    "integer", "", sync=True, default=10),
    define(0x0027, "join_time",         "integer", ""),
    define(0x0030, "createtime", "integer", "", save=True),
    define(0x0031, "createtime", "integer", "", save=True),

    define(0x0032, "usedcount", "integer", "", cycle=True, timestamp=0x0033, save=True, default=0),

    # stored_set encoding
    define(0x0040, 'fbrewards', 'stored_set', '', encoder=cPickle.dumps, decoder=cPickle.loads),

    # stored_list encoding
    define(0x0041, 'mylist', 'stored_sequence', '', encoder=json.encode, decoder=json.decode),
)
store_tag = 'p'
PlayerBase = create_class('PlayerBase', player_fields, store_tag)

if __name__ == '__main__':
    import os
    from yy.entity import gen_cython
    c = gen_cython(player_fields.values(), 'c_PlayerBase', 'from tests.entity import PlayerBase as PureEntity', store_tag, extra_imports)
    open(os.path.join(os.path.dirname(__file__), 'c_player.pyx'), 'w').write(c)
