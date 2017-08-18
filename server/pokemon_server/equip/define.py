# coding: utf-8
from yy.entity import create_class, define, init_fields
from yy.entity.formulas import register_formula
from equip import formulas

import ujson as json

extra_imports = '''
'''

equip_fields = init_fields([
    define(0x0001, "entityID",      "integer", "唯一实体ID", save=True, sync=True),
    define(0x0002, "prototypeID",   "integer", "配置ID", save=True, sync=True),
    define(0x0003, "masterID",      "integer", "主人的角色ID"),
    define(0x0004, "type",          "integer", "类型"),
    define(0x0005, 'equipID',       'integer', '装备ID',   formula='entityID'),
    define(0x0006, 'level',         "integer", "强化等级", save=True, sync=True),
    define(0x0007, 'step',          "integer", "装备阶数", save=True, sync=True, default=1),
    define(0x0008, 'rest_star',     "integer", "剩余兵魂", save=True, sync=True, default=0),
    define(0x0009, "slugs",         "integer", "加成属性槽数", formula="fn.get_slugs(step)"),

    define(0x0020, "baseHP",        "float", "基础血量", formula="fn.get_equip_base_hp(prototypeID, level, step, enchant_attrs, player_equip1, player_equip2, player_equip3, player_equip4, player_equip5, player_equip6, type)"),
    define(0x0021, "baseATK",       "float", "基础攻击", formula="fn.get_equip_base_atk(prototypeID, level, step, enchant_attrs, player_equip1, player_equip2, player_equip3, player_equip4, player_equip5, player_equip6, type)"),
    define(0x0022, "baseDEF",       "float", "基础防御", formula="fn.get_equip_base_def(prototypeID, level, step, enchant_attrs, player_equip1, player_equip2, player_equip3, player_equip4, player_equip5, player_equip6, type)"),
    define(0x0023, "baseCRI",       "float",   "基础暴击", formula="fn.get_equip_base_crit(prototypeID, level, step, enchant_attrs, player_equip1, player_equip2, player_equip3, player_equip4, player_equip5, player_equip6, type)"),
    define(0x0024, "baseEVA",       "float",   "基础闪躲", formula="fn.get_equip_base_dodge(prototypeID, level, step, enchant_attrs, player_equip1, player_equip2, player_equip3, player_equip4, player_equip5, player_equip6, type)"),


    define(0x0025, "enchants",      "sequence",   "附魔", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0026, "enchant_attrs", "string", "附魔属性", sync=True, formula="fn.get_enchant_attrs(prototypeID, slugs, enchants)"),
    define(0x0080, "base_power",    "float",  "装备战力", formula="fn.get_equip_base_power(entityID, prototypeID, masterID, baseHP, baseATK, baseDEF, baseCRI, baseEVA)"),
    define(0x0081, "power",         "integer", "战力",    sync=True, formula="base_power"),

    define(0x0099, "player_equip1", "integer", "玩家装备等级1", default=0),
    define(0x009a, "player_equip2", "integer", "玩家装备等级2", default=0),
    define(0x009b, "player_equip3", "integer", "玩家装备等级3", default=0),
    define(0x009c, "player_equip4", "integer", "玩家装备等级4", default=0),
    define(0x009d, "player_equip5", "integer", "玩家装备等级5", default=0),
    define(0x009e, "player_equip6", "integer", "玩家装备等级6", default=0),
])

store_tag = 'e'
EquipBase = create_class("EquipBase", equip_fields, store_tag)

if __name__ == '__main__':
    import os
    from yy.entity import gen_cython
    c = gen_cython(equip_fields.values(), 'c_EquipBase', 'from equip.define import EquipBase as PureEntity', store_tag, extra_imports)
    open(os.path.join(os.path.dirname(__file__), 'c_equip.pyx'), 'w').write(c)
