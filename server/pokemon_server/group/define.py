# coding: utf-8
import ujson as json
from yy.entity import create_class, define, init_fields
from yy.entity.formulas import register_formula  # NOQA
import formulas  # NOQA


extra_imports = '''
'''

group_fields = init_fields([
    define(0x0001, "entityID", "integer",     "唯一ID",       save=True),
    define(0x0002, "groupID",  "integer",     "同门ID",       formula="entityID"),
    define(0x0003, "name",     "string",      "同门名称",     save=True),
    define(0x0004, "applys",   "stored_dict", "申请的成员",   int_key=True, decoder=json.decode, encoder=json.encode),
    define(0x0005, "members",  "stored_dict", "当前的成员",   int_key=True, decoder=json.decode, encoder=json.encode),
    define(0x0006, "leaderID", "integer",     "大师兄ID",     save=True),
    define(0x0007, "invites",  "stored_set",  "已邀请的好友", int_value=True),

    define(0x0008, "leader_lastlogin", "datetime",        "大师兄上次登录时间",  save=True),
    define(0x0009, "gve_joineds",      "stored_sequence", "观战列表", int_value=True),
    define(0x000a, "gve_activateds",   "stored_sequence", "活跃列表", int_value=True),
    define(0x000b, "gve_start_time",   "integer",         "开战时间", save=True, default=0),
    define(0x000c, "gve_progress",     "stored_dict",     "进度", int_key=True, int_value=True),
    define(0x000d, "gve_deads",        "stored_set",      "死亡列表", int_value=True),
    define(0x000e, "gve_end_cd",       "integer",         "结束倒计时", save=True, default=0),
    define(0x0010, "gve_max_damage",   "integer",         "最高伤害", save=True, default=0),
    define(0x0011, "gve_rewards",      "stored_dict",     "奖励",   int_key=True, decoder=json.decode, encoder=json.encode),

    define(0x0012, "gve_last_kick_time",  "integer", "上次踢人时间", save=True, default=0),
    define(0x0013, "gve_last_reset_time", "integer", "上次重置时间", save=True, default=0),

    define(0x0014, "gve_end_activateds",     "stored_sequence", "备份活跃列表", int_value=True),
    define(0x0015, "gve_activateds_detail",  "stored_dict",     "备份活跃详细", int_key=True, decoder=json.decode, encoder=json.encode),
    define(0x0016, "lastlogin",              "datetime",        "同门大师兄最后一次登录", save=True, default=0),
])

store_tag = "g"
GroupBase = create_class("GroupBase", group_fields, store_tag)

if __name__ == "__main__":
    import os
    from yy.entity import gen_cython
    c = gen_cython(
        group_fields.values(), "c_GroupBase",
        "from group.define import GroupBase as PureEntity",
        store_tag, extra_imports)
    open(os.path.join(os.path.dirname(__file__), "c_group.pyx"), "w").write(c)
