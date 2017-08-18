# coding: utf-8
import msgpack
from yy.entity import create_class, define, init_fields
from yy.entity.formulas import register_formula
from pet import formulas

import ujson as json

extra_imports = '''
'''

pet_fields = init_fields([
    define(0x0004, "entityID",    "integer", "唯一实体ID",   save=True, sync=True),
    define(0x0005, "name",        "string",  "名称",         save=True, sync=True),
    define(0x0006, "level",       "integer", "等级",         save=True, sync=True, default=1),
    define(0x000f, "modelID",     "integer", "模型ID",       save=True),

    define(0x0015, "breaklevel",  "integer", "突破等级",     formula="fn.get_breaklevel(prototypeID, star)", sync=True),
    define(0x0018, "skill",       "integer", "普通技能等级", sync=True, save=True, default=1),
    define(0x0019, "lskill",      "integer", "队长技能等级", sync=True, save=True, default=1),

    define(0x0021, "prototypeID", "integer", "怪物配置ID",   save=True, sync=True),
    define(0x0022, "masterID",    "integer", "主人的角色ID"),

    define(0x0030, "exp",         "integer", "经验",         sync=True, save=True, default=0),

    #  define(0x0035, "subattr1",    "integer", "副元素1",      save=True, sync=True, default=0),
    #  define(0x0036, "subattr2",    "integer", "副元素2",      save=True, sync=True, default=0),
    define(0x0037, "gettime",     "integer", "入手时间",     save=True, sync=True, default=0),
    define(0x0038, "dispatched",  "integer", "dlc派驻关卡",  save=True, sync=True, syncTimeout=True, default=0),

    #  define(0x0039, "subattr_point1", "integer", "副元素积分1", save=True, default=0),
    #  define(0x003a, "subattr_point2", "integer", "副元素积分2", save=True, default=0),
    #  define(0x003b, "subattr_point3", "integer", "副元素积分3", save=True, default=0),
    #  define(0x003c, "subattr_point4", "integer", "副元素积分4", save=True, default=0),
    #  define(0x003d, "subattr_point5", "integer", "副元素积分5", save=True, default=0),

    define(0x003f, "mtype",  "integer", "怪物类型", default=0, sync=True),

    define(0x0040, "activated_relations", "dict", "激活的情缘", save=True, decoder=msgpack.loads, encoder=msgpack.dumps),
    define(0x0041, "relations",           "string",   "情缘",       sync=True, formula="fn.get_relations(activated_relations)"),

    define(0x0061, "uproar_dead",  "boolean", "是否在大闹天宫中阵亡", save=True, sync=True, default=False),
    define(0x0062, "restHP",       "integer", "剩余血量", save=True,  sync=True, default=0),

    define(0x0080, "base_power",   "float", "基础战斗力(不包括装备与公会加成)", formula="fn.get_pet_base_power(entityID, prototypeID, masterID, baseHP, baseATK, baseDEF, baseCRI, baseEVA, skill1, skill2, skill3, skill4, skill5)"),
    define(0x0081, "power",  "integer", "战斗力", formula="base_power", sync=True),

    define(0x0100, "baseHP",     "float", "基础血量",      formula="fn.get_pet_base_hp(prototypeID, level, breaklevel, activated_relations)"),
    define(0x0101, "baseATK",    "float", "基础攻击",      formula="fn.get_pet_base_atk(prototypeID, level, breaklevel, activated_relations)"),
    define(0x0102, "baseDEF",    "float", "基础防御",      formula="fn.get_pet_base_def(prototypeID, level, breaklevel, activated_relations)"),
    define(0x0103, "baseCRI",    "float",   "基础暴击",    formula="fn.get_pet_base_crit(prototypeID, level, breaklevel, activated_relations)"),
    define(0x0104, "baseEVA",    "float",   "基础闪躲",    formula="fn.get_pet_base_dodge(prototypeID, level, breaklevel, activated_relations)"),
    define(0x0105, "star",       "integer", "星魄",        sync=True, formula="fn.get_star(base_star, add_star)"),
    define(0x0106, "base_star",  "integer", "基础星魂",    formula="fn.get_base_star(prototypeID)"),
    define(0x0107, "add_star",   "integer", "升星星魂",    save=True, default=0),

    define(0x0200, "skill1", "integer", "技能1", save=True, sync=True, default=1),
    define(0x0201, "skill2", "integer", "技能2", save=True, sync=True, default=1),
    define(0x0202, "skill3", "integer", "技能3", save=True, sync=True, default=1),
    define(0x0203, "skill4", "integer", "技能4", save=True, sync=True, default=1),
    define(0x0204, "skill5", "integer", "技能5", save=True, sync=True, default=1),

    define(0x0300, "equipeds", "stored_dict", "已装备列表", int_value=True, int_key=True),
    define(0x0301, "equipeds_json", "string", "已装备列表", sync=True, formula="fn.get_equipeds_json(equipeds)"),
    define(0x0302, "max_level", "integer", "等级上限", sync=True, formula="fn.get_max_level(breaklevel)"),
    define(0x0303, "next_max_level", "integer", "下一等级上限", sync=True, formula="fn.get_next_max_level(breaklevel)"),

    define(0x9061, "daily_dead",    "boolean", "是否在每日PVP中阵亡", save=True, sync=True, default=False),
    define(0x9077, "daily_restHP",  "integer", "每日PVP中的剩余血量", save=True, sync=True, default=0),
])
store_tag = 't'
PetBase = create_class('PetBase', pet_fields, store_tag)

if __name__ == '__main__':
    import os
    from yy.entity import gen_cython
    c = gen_cython(pet_fields.values(), 'c_PetBase', 'from pet.define import PetBase as PureEntity', store_tag, extra_imports)
    open(os.path.join(os.path.dirname(__file__), 'c_pet.pyx'), 'w').write(c)
