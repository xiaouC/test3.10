# coding: utf-8
from yy.entity import create_class, define, init_fields
from yy.entity.formulas import register_formula
import formulas

import ujson as json

extra_imports = '''
'''

faction_fields = init_fields([
    define(0x0001, "entityID",  "integer", "唯一ID", save=True),
    define(0x0002, "factionID", "integer", "公会ID", formula='entityID'),
    define(0x0003, "name",      "string",  "公会名称", save=True),
    define(0x0004, "level",     "integer", "公会等级"),
    define(0x0005, "totalfp",   "integer", "总贡献", save=True, default=0),
    define(0x0006, "todayfp",   "integer", "今日贡献", save=True, cycle=True, timestamp=0x0013, default=0),
    define(0x0007, "memberset", "set",     "拥有的成员",   save=True, decoder=json.decode, encoder=json.encode),
    define(0x0008, "applyset",  "set",     "申请的成员",   save=True, decoder=json.decode, encoder=json.encode),
    define(0x0009, "inviteset", "set",     "邀请的冒险者", save=True, decoder=json.decode, encoder=json.encode),
    define(0x000a, "mode",      "integer", "认证方式",     save=True, default=1),
    define(0x000b, "notice",    "string",  "公会公告",     save=True),
    define(0x000c, "createtime","integer", "创建时间",     save=True),

    define(0x000d, "strengthen_hp_level", "integer", "强化hp等级", save=True, default=0),
    define(0x000e, "strengthen_at_level", "integer", "强化攻等级", save=True, default=0),
    define(0x000f, "strengthen_ct_level", "integer", "强化暴等级", save=True, default=0),
    define(0x0010, "strengthen_df_level", "integer", "强化防等级", save=True, default=0),

    define(0x0015, "leaderID", "integer", "会长ID",     save=True),
    define(0x0016, "dflag",    "boolean", "待解散标识", save=True, default=False),

    define(0x0017, "mall_products", "set", "已经解锁商品位置", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0018, "faction_treasure", "integer", "公会宝藏", save=True, default=0),
    define(0x0019, "city_top_member",       "dict", "黄金城第一名成员", decoder=json.decode, encoder=json.encode, save=True),
    define(0x0020, "city_top_member_kills", "integer", "黄金城第一名成员所杀怪个数", save=True, default=0),
])

store_tag = 'f'
FactionBase = create_class('FactionBase', faction_fields, store_tag)

if __name__ == '__main__':
    import os
    from yy.entity import gen_cython
    c = gen_cython(faction_fields.values(), 'c_FactionBase', 'from faction.define import FactionBase as PureEntity', store_tag, extra_imports)
    open(os.path.join(os.path.dirname(__file__), 'c_faction.pyx'), 'w').write(c)
