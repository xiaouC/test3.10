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
    define(0x0001, "userID",   "integer", "用户ID", save=True),
    define(0x0002, "username", "string", "用户名", save=True),
    define(0x0003, "IMEI",     "string",  "IMEI"),
    define(0x0004, "entityID", "integer", "角色ID",     save=True, sync=True),
    define(0x0005, "name",     "string",  "角色名字",   save=True, sync=True),
    define(0x0006, "level",    "integer", "等级",       save=True, sync=True),
    define(0x0007, "sp",       "integer", "能量",       save=True, sync=True, cycle=True, resume=6*60, timestamp="resume_sp_cd", max="spmax"),
    define(0x0008, "money",    "integer", "金币",       save=True, sync=True),

    define(0x0009, "gold",     "integer", "钻石",       save=True, sync=True),
    define(0x000a, "vs",       "integer", "PVP入场券",  save=True, sync=True),
    define(0x000b, "gp",       "integer", "抽怪货币",   save=True, sync=True),
    define(0x000c, "bp",       "integer", "工会货币",   save=True, sync=True),
    define(0x000d, "slate",    "integer", "成就点数",   save=True, sync=True),
    define(0x000e, "power",    "integer", "统领力",     sync=True, formula="fn.get_power(entityID, base_power, equip_power, faction_power, ambition_power, point_power, gems_power, honor_power)", cache=True),
    define(0x000f, "modelID",  "integer", "模型ID",     save=True),
    define(0x0010, "sex",      "integer", "性别",       save=True, sync=True),
    define(0x0011, "career",   "integer", "职业",       save=True, sync=True),

    define(0x0012, "lastlogin",   "datetime", "最后一次登录时间",  save=True),
    define(0x0013, "totallogin",  "integer",  "累计登录次数",      save=True),
    define(0x0014, "seriallogin", "integer",  "连续登录次数",      save=True),
    define(0x0015, "createtime",  "datetime", "角色创建时间",      save=True),

    define(0x0016, "fbset",        "set",     "副本列表", save=True, decoder=json.decode, encoder=json.encode),

    define(0x0017, "soul", "integer", "水晶", save=True, sync=True, default=0),

    define(0x0018, "mailset", "set",     "拥有邮件的ID", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0019, "petset",  "set",     "拥有怪物的ID", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0020, "pets",    "dict",  "玩家的所有怪物"),

    define(0x0021, "mails",        "dict",  "邮件列表"),
    define(0x0022, 'newmailcount', "integer", "新邮件数量",   formula="fn.get_newmailcount(mails)", sync=True),
    define(0x0023, "spmax",        "integer", "最大能量",     save=True, sync=True),
    define(0x0024, "petmax",       "integer", "最大怪物数量", save=True, sync=True),
    # define(0x0025, "lineups",      "sequence", "阵形",        save=True, decoder=json.decode, encoder=json.encode),
    # define(0x0026, "on_lineup",    "integer", "激活的阵形",   save=True, sync=True, default=0),
    define(0x0025, "lineups", "stored_dict", "阵形", int_key=True, decoder=json.decode, encoder=json.encode),
    define(0x0027, "fbscores", "stored_dict", "副本进度", int_key=True, decoder=json.decode, encoder=json.encode),
    define(0x0028, "currentfbID",  "integer", "当前所在副本ID", save=True, default=0),
    define(0x0029, "fbreward", "stored_dict", "副本奖励", int_key=True),

    define(0x0030, "exp", "integer", "经验", sync=True, save=True, default=0),

    define(0x0031, "expmax", "integer", "人物升级需要经验", sync=True, formula="fn.get_max_exp(level)"),
    define(0x0032, "expnxt", "integer", "上一级升级需要经验", sync=True, formula="fn.get_next_exp(level)"),

    define(0x0033, "resume_sp_cd", "integer", "下一次恢复能量剩余时间", save=True, sync=True, syncTimeout=True),

    define(0x0034, "spprop", "integer", "能量道具数量", save=True, sync=True),

    define(0x0035, "dbtag",  "string",  "数据库ID"),
    define(0x0036, "book",   "stored_set", "怪物图鉴", int_value=True),

    define(0x0038, "fbprocess", "integer", "普通副本最大进度", save=True, event=True),
    define(0x0039, "fbadvance", "integer", "精英副本最大进度", save=True),

    define(0x0047, "explore1",   "integer",  "探索1怪物id", save=True, sync=True),
    define(0x0049, "exploretime1",   "integer",  "探索结束时间戳", save=True, sync=True, syncTimeout=True),
    define(0x0050, "exploretimetype1",   "integer",  "探索时间类型", save=True),

    define(0x0051, "explore2",   "integer",  "探索2怪物id", save=True, sync=True),
    define(0x0053, "exploretime2",   "integer",  "探索结束时间戳", save=True, sync=True, syncTimeout=True),
    define(0x0054, "exploretimetype2",   "integer",  "探索时间类型", save=True),

    define(0x0055, "explore3",   "integer",  "探索3怪物id", save=True, sync=True),
    define(0x0057, "exploretime3",   "integer",  "探索结束时间戳", save=True, sync=True, syncTimeout=True),
    define(0x0058, "exploretimetype3",   "integer",  "探索时间类型", save=True),

    define(0x0059, "guide_types",  "set",  "新手引导类型", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0060, "guide_end_signal",  "integer",  "标志新手引导是否结束", save=True),

    define(0x0068, "lotteryflag", "boolean", "是否单抽过", save=True, default=False),
    define(0x0069, "slatereward_getedset",   "set",  "石板功能中已经领取奖励的id集合", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0099, "credits",     "integer", "充值积分", save=True),

    # 抽英雄
    define(0x0108, "loterry_hero_cd_A",              "integer", "抽英雄CD A",                save=True, default=0, sync=True, syncTimeout=True),
    define(0x0109, "loterry_hero_cd_B",              "integer", "抽英雄CD B",                save=True, default=0, sync=True, syncTimeout=True),
    define(0x010A, "loterry_hero_cd_C",              "integer", "抽英雄CD C",                save=True, default=0, sync=True, syncTimeout=True),
    define(0x010B, "loterry_hero_count_A",           "integer", "抽英雄次数 A",              save=True, default=0),
    define(0x010C, "loterry_hero_count_B",           "integer", "抽英雄次数 B",              save=True, default=0),
    define(0x010D, "loterry_hero_count_C",           "integer", "抽英雄次数 C",              save=True, default=0),
    define(0x010E, "loterry_hero_gold_first_A",      "boolean", "是否抽英雄首金 A",          save=True, default=True),
    define(0x010F, "loterry_hero_gold_first_B",      "boolean", "是否抽英雄首金 B",          save=True, default=True),
    define(0x0110, "loterry_hero_gold_first_C",      "boolean", "是否抽英雄首金 C",          save=True, default=True),
    define(0x0111, "loterry_hero_used_free_count_A", "integer", "抽英雄已用免费次数 A",      save=True, default=0, cycle=True, timestamp=0x0112),
    define(0x0113, "loterry_hero_used_free_count_B", "integer", "抽英雄已用免费次数 B",      save=True, default=0, cycle=True, timestamp=0x0114),
    define(0x0115, "loterry_hero_used_free_count_C", "integer", "抽英雄已用免费次数 C",      save=True, default=0, cycle=True, timestamp=0x0116),
    define(0x0117, "loterry_hero_count_2",           "integer", "抽英雄紫一代个数",          save=True, default=0),
    define(0x0118, "loterry_hero_history_3",         "set", "抽英雄垃圾紫历史",           save=True, decoder=json.decode,  encoder=json.encode),
    define(0x0119, "loterry_hero_gold_first_4",      "boolean", "抽英雄首金比紫等级4",      save=True, default=True),
    define(0x011a, "loterry_hero_gold_first_5",      "boolean", "抽英雄首金比紫等级5",      save=True, default=True),
    define(0x011B, "loterry_hero_gold_first_6",      "boolean", "抽英雄首金比紫等级6",      save=True, default=True),
    define(0x011C, "loterry_hero_gold_first_7",      "boolean", "抽英雄首金比紫等级7",      save=True, default=True),
    define(0x011D, "loterry_hero_gold_first_8",      "boolean", "抽英雄首金比紫等级7",      save=True, default=True),
    define(0x011E, "loterry_hero_cost_A",    "integer", "抽奖消耗A", sync=True, formula="fn.get_loterry_hero_cost_A()"),
    define(0x011F, "loterry_hero_cost_B",    "integer", "抽奖消耗B", sync=True, formula="fn.get_loterry_hero_cost_B()"),
    define(0x0120, "loterry_hero_cost_C",    "integer", "抽奖消耗C", sync=True, formula="fn.get_loterry_hero_cost_C()"),

    define(0x0121, "loterry_hero_cd_D",              "integer", "抽英雄CD D",                save=True, default=0, sync=True, syncTimeout=True),
    define(0x0122, "loterry_hero_count_D",           "integer", "抽英雄次数 D",              save=True, default=0),
    define(0x0123, "loterry_hero_gold_first_D",      "boolean", "是否抽英雄首金 D",          save=True, default=True),
    define(0x0124, "loterry_hero_used_free_count_D", "integer", "抽英雄已用免费次数 D",      save=True, default=0, cycle=True, timestamp=0x0125),

    define(0x0126, "loterry_hero_rest_free_count_A", "integer", "抽英雄剩余免费次数 A",  sync=True, formula="fn.get_loterry_hero_rest_free_count_A(loterry_hero_used_free_count_A)"),
    define(0x0127, "loterry_hero_rest_free_count_B", "integer", "抽英雄剩余免费次数 B",  sync=True, formula="fn.get_loterry_hero_rest_free_count_B(loterry_hero_used_free_count_B)"),
    define(0x0128, "loterry_hero_rest_free_count_C", "integer", "抽英雄剩余免费次数 C",  sync=True, formula="fn.get_loterry_hero_rest_free_count_C(loterry_hero_used_free_count_C)"),
    define(0x0129, "loterry_hero_rest_free_count_D", "integer", "抽英雄剩余免费次数 D",  sync=True, formula="fn.get_loterry_hero_rest_free_count_D(loterry_hero_used_free_count_D)"),

    define(0x012a, "loterry_hero_tips_A", "string",  "抽英雄提示A", sync=True, formula="fn.get_loterry_hero_tips_A(loterry_hero_count_A, lottery_money_accumulating)"),
    define(0x012b, "loterry_hero_tips_B", "string",  "抽英雄提示B", sync=True, formula="fn.get_loterry_hero_tips_B(loterry_hero_count_B, lottery_money_accumulating10)"),
    define(0x012c, "loterry_hero_tips_C", "string",  "抽英雄提示C", sync=True, formula="fn.get_loterry_hero_tips_C(loterry_hero_count_C, lottery_gold_accumulating)"),
    define(0x012d, "loterry_hero_tips_D", "string",  "抽英雄提示D", sync=True, formula="fn.get_loterry_hero_tips_D(loterry_hero_count_D, lottery_gold_accumulating10)"),

    define(0x0130, "loterry_hero_cost_D",    "integer", "抽奖消耗D", sync=True, formula="fn.get_loterry_hero_cost_D()"),
    define(0x0131, "resolvegold_time", "integer", "已炼银次数", save=True, default=0, cycle=True, timestamp=0x0132),
    define(0x0133, "resolvegold_level", "integer", "炼银开启的等级", sync=True, formula="fn.resolvegold_level()"),
    # PVP
    define(0x0138, "pvpgrad", "integer", "pvp 牌子",  save=True, sync=True, default=0),
    define(0x0139, "pvprankcount", "integer", "pvp总人数", formula="fn.get_pvprankcount()", sync=True),
    define(0x0140, "pvpseasonrewardreceived", "boolean", "pvp赛季奖励已发放", formula="bool(pvpseasonreward)", sync=True),
    define(0x0141, "pvpseasonreward",   "dict",  "PVP赛季奖励", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0142, "pvpseasoncount",    "integer", "PVP赛季总参战次数", save=True),
    define(0x0143, "pvprankreceiveds",  "set", "是否已经领取排名奖励", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0146, "vsCount",          "integer", "vs下注", save=True, default=0),
    define(0x0147, "pvplastcleantime", "integer", "PVP上次清除数据时间", save=True, default=0),
    define(0x0148, "pvpopenflag",      "boolean", "pvp是否开放标记", default=False),
    define(0x0149, "pvprewards",       "set",  "pvp已发放奖励", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0150, "todaybp",       "integer", "PVP今日获得BP", save=True, sync=True, cycle=True, default=0, timestamp=0x0144),
    define(0x0151, "pvprank",       "integer", "PVP排名",       save=True, sync=True, default=0),
    define(0x0152, "pvpstarttime",  "integer", "PVP开始时间", formula="fn.get_pvp_start_time(pvpopenflag)", default=0, sync=True, syncTimeout=True),
    define(0x0153, "pvpfinaltime",  "integer", "PVP结束时间", formula="fn.get_pvp_final_time(pvpopenflag)", default=0, sync=True, syncTimeout=True),
    define(0x0154, "pvpopen",       "boolean", "PVP是否开启", formula="fn.get_pvp_is_open(pvpopenflag)", default=False, sync=True),
    define(0x0155, "totalbp",       "integer", "PVP总共获得BP", sync=True),

    define(0x0156, "prototypeID",   "integer", "头像ID",   sync=True, save=True),

    define(0x0157, "exploredoubletime1",   "integer",  "探索双倍奖励倒计时类型", save=True, sync=True, syncTimeout=True),
    define(0x0158, "exploredoubletime2",   "integer",  "探索双倍奖励倒计时类型", save=True, sync=True, syncTimeout=True),
    define(0x0159, "exploredoubletime3",   "integer",  "探索双倍奖励倒计时类型", save=True, sync=True, syncTimeout=True),

    define(0x0160, "get_serialloginreward",  "integer",  "标志今天的连续登陆奖励是否已经领取过",  save=True),
    define(0x0161, "offline_attrs",  "sequence",  "离线属性修改",  save=True, decoder=json.decode, encoder=json.encode),
    define(0x0162, "lastlogout",   "datetime", "最后一次退出时间",  save=True),
    define(0x0163, "offlinemail_set", "set",   "拥有邮件的ID", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0164, "fac_offlinemail_set", "set",   "公会排名奖励已读取的离线邮件ID", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0165, "slatelen",   "integer", "成就已领个数", sync=True, formula="fn.get_slatelen(slatereward_getedset)"),

    define(0x0200, "worldID",      "integer", "当前所在服务器",    save=True, default=0),

    define(0x0220, "faction_name",      "string",  "公会名称", save=True, sync=True),
    define(0x0221, "faction_level",     "integer", "公会等级", save=True, sync=True),
    define(0x0222, "faction_is_leader", "boolean", "是否会长", save=True, sync=True),
    define(0x0223, "faction_level_rewards_received", "set", "已经领取的公会礼包", save=True, decoder=json.decode, encoder=json.encode, cycle=True, timestamp=0x0224),
    define(0x0225, "faction_level_rewards_count", "integer", "可以领取的公会礼包数量", sync=True, formula="fn.get_faction_level_rewards_count(faction_level_rewards_received, faction_level)"),
    define(0x0226, "faction_taskID",    "integer", "公会任务ID",     save=True, sync=True, cycle=True, timestamp=0x0227, default=0),
    define(0x0228, "faction_task_done", "boolean", "公会任务已完成", save=True, sync=True, cycle=True, timestamp=0x0229, default=False),
    define(0x022a, "last_factionID",    "integer", "上一个公会ID", save=True, sync=True, default=0),

    define(0x0248, "applyFactions", "set", "申请加入的公会", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0249, "joinFactionTime", "integer", "加入公会时间", save=True, default=0),
    define(0x0250, "factionID", "integer", "公会ID", save=True, sync=True, default=0),
    # define(0x0251, "applyFactionID", "integer", "申请加入的公会ID", save=True, sync=True, default=0),
    # define(0x0252, "applyFactionTime", "integer", "申请加入公会的时间", save=True, sync=True, syncTimeout=True, default=0),

    define(0x0253, "inviteFactionSet", "set", "发送邀请的公会ID集合", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0254, "inviteFactionCount", "integer", "发送邀请的公会个数", formula='fn.get_invite_faction_count(inviteFactionSet)', sync=True),
    define(0x0255, "applyMemberSet", "set", "申请列表"),
    define(0x0256, "applyMemberCount", "integer", "申请列表个数", formula='fn.get_apply_member_count(applyMemberSet)', sync=True),

    define(0x0269, "strengthen_df_level", "integer", "强化防御等级", save=True, sync=True, default=0),
    define(0x0270, "strengthen_hp_level", "integer", "强化HP等级",   save=True, sync=True, default=0),
    define(0x0271, "strengthen_at_level", "integer", "强化攻击等级", save=True, sync=True, default=0),
    define(0x0272, "strengthen_ct_level", "integer", "强化暴击等级", save=True, sync=True, default=0),

    define(0x0273, "strengthen_hp_max_level", "integer", "最大强化HP等级",   save=True, default=0),
    define(0x0274, "strengthen_at_max_level", "integer", "最大强化攻击等级", save=True, default=0),
    define(0x0275, "strengthen_ct_max_level", "integer", "最大强化暴击等级", save=True, default=0),
    define(0x0276, "strengthen_df_max_level", "integer", "最大强化防御等级", save=True, default=0),

    define(0x0280, "buy_sp_used_count", "integer", "购买能量已用次数", save=True, default=0, cycle=True, timestamp=0x0279),
    define(0x0281, "buy_sp_rest_count", "integer", "购买能量剩余次数", formula='fn.get_vip_buy_sp_rest_count(vip, buy_sp_used_count)', sync=True),
    define(0x0282, "buy_sp_cost", "integer", "购买能量消耗", formula='fn.get_buy_sp_cost(buy_sp_used_count)', sync=True),

    define(0x0300, "featureCode",   "string",  "特征串",       save=True),
    define(0x0301, "clientIP",      "string",  "客户端IP",     save=True),
    define(0x0302, "clientVersion", "string",  "客户端版本号", save=True),

    # 碎片、天庭商店、金角商店、银角商店
    define(0x0320, "petPatchs", "stored_dict",  "玩家身上的所有碎片", int_key=True, int_value=True),
    define(0x0321, "petpatchdirty", "set",  "碎片增量同步id", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0346, "golden_sp",    "integer", "用于触发金角临时商店记录的能量（触发后清零）", save=True, default=0),
    define(0x0348, "silver_sp",    "integer", "用于触发银角临时商店记录的能量（触发后清零）", save=True, default=0),

    define(0x0350, "retry_fb_count", "integer", "花费钻石战斗复活", save=True),
    define(0x0351, "consume_count",  "integer", "付费项目消费总次", save=True),
    define(0x0352, "lottery_count",  "integer", "抽将消费总次",     save=True),
    define(0x0353, "lottery_gold_accumulating",    "integer", "抽将钻石积分", save=True, default=0),
    define(0x0354, "lottery_money_accumulating",   "integer", "抽将金币积分", save=True, default=0),
    define(0x0355, "lottery_gold_accumulating10",  "integer", "抽奖钻石十连积分", save=True, default=0),
    define(0x0356, "lottery_money_accumulating10", "integer", "抽奖金币十连积分", save=True, default=0),

    define(0x0400, "credits",        "integer", "充值积分",    save=True, sync=True),
    define(0x0401, "vip",            "integer", "vip等级",     formula='fn.get_vip(credits)', sync=True),
    define(0x0402, "vip_offline",    "integer", "缓存vip字段", save=True, default=0),

    define(0x0453, "vip_refresh_fb_max_count",  "integer", "刷新副本次数上限", formula='fn.get_vip_refresh_fb_max_count(vip)', sync=True),

    define(0x0500, "tasks", "stored_dict", "任务进度",       int_key=True, decoder=json.decode, encoder=json.encode),
    define(0x0501, "taskrewards", "set",   "可领取任务奖励", save=True, decoder=json.decode, encoder=json.encode),

    define(0x0502, "task_max_patch_sign_up_count",   "integer",  "可补签次数", save=True),
    define(0x0503, "task_rest_patch_sign_up_count",  "integer",  "剩余补签次数", formula='max(task_max_patch_sign_up_count - task_used_patch_sign_up_count, 0)', sync=True),
    define(0x0504, "task_used_patch_sign_up_count",  "integer",  "已用补签次数", save=True),
    define(0x0505, "task_last_sign_up_time", "integer",  "上次签到时间", save=True),
    define(0x0506, "task_today_is_sign_up", "boolean", "今日是否签到", formula='fn.get_task_today_is_sign_up(task_last_sign_up_time)', sync=True),
    define(0x0507, "taskrewardscount1", "integer",   "可领取任务奖励数量1", formula="fn.get_taskrewardscount1(taskrewards, task_sp_daily_receiveds)", sync=True),
    define(0x0508, "taskrewardscount2", "integer",   "可领取任务奖励数量2", formula="fn.get_taskrewardscount2(taskrewards)", sync=True),
    define(0x0509, "taskrewardscount3", "integer",   "可领取任务奖励数量3", formula="fn.get_taskrewardscount3(taskrewards)", sync=True),
    define(0x050a, "taskrewardscount4", "integer",   "可领取任务奖励数量4", formula="fn.get_taskrewardscount4(taskrewards)", sync=True),
    define(0x050b, "task_is_calc_sign_up", "boolean",   "是否计算过补签次数", cycle=True, save=True, timestamp=0x050c, default=False),
    define(0x050d, "task_sp_daily_receiveds", "set", "能量每日已领取", save=True, decoder=json.decode, encoder=json.encode, cycle=True, timestamp=0x050e),
    define(0x050f, "monthly_card_30", "integer", "月卡剩余天数", save=True),
    define(0x0510, "taskrewardscountnew", "integer",   "新的可领取任务数量", formula="fn.get_taskrewardscountnew(taskrewards)", sync=True),
    define(0x0511, "taskrewardscount5", "integer",   "可领取任务奖励数量5", formula="fn.get_taskrewardscount5(taskrewards)", sync=True),
    define(0x0512, "task_noob_flag", "boolean",  "新手好礼显示隐藏标识",    formula="fn.get_task_noob_flag(entityID, taskrewards)", sync=True),
    define(0x0513, "task_noob_undo", "boolean",  "新手好礼未完成标识",      formula="fn.get_task_noob_undo(entityID, taskrewards)", sync=True),
    define(0x0514, "taskrewardscount6", "integer",   "可领取任务奖励数量6", formula="fn.get_taskrewardscount6(taskrewards)", sync=True),
    define(0x0515, "taskrewardscount7", "integer",   "可领取任务奖励数量7", formula="fn.get_taskrewardscount7(taskrewards)", sync=True),

    define(0x0516, "taskrewardscountsubtype1", "integer", "可领取成就奖励数量1", formula="fn.get_taskrewardscountsubtype1(taskrewards)", sync=True),
    define(0x0517, "taskrewardscountsubtype2", "integer", "可领取成就奖励数量2", formula="fn.get_taskrewardscountsubtype2(taskrewards)", sync=True),
    define(0x0518, "taskrewardscountsubtype3", "integer", "可领取成就奖励数量3", formula="fn.get_taskrewardscountsubtype3(taskrewards)", sync=True),
    define(0x0519, "taskrewardscountsubtype4", "integer", "可领取成就奖励数量4", formula="fn.get_taskrewardscountsubtype4(taskrewards)", sync=True),
    define(0x0520, "taskrewardscount12", "integer",   "可领取任务奖励数量12", formula="fn.get_taskrewardscount12(taskrewards)", sync=True),
    define(0x0521, "taskrewardscount13", "integer",   "可领取任务奖励数量13", formula="fn.get_taskrewardscount13(taskrewards)", sync=True),
    define(0x0522, "taskrewardscount14", "integer",   "可领取任务奖励数量14", formula="fn.get_taskrewardscount14(taskrewards)", sync=True),
    define(0x0523, "taskrewardsdone14",  "integer",   "已完成任务数14",       formula="fn.get_taskrewardsdone14(entityID, tasks, taskrewards)", sync=True),

    define(0x05ff, "reset_recharges_seq", "integer",  "重置充值序号",             save=True, default=0),
    define(0x0600, "bought_recharges",    "set",      "已购买过的充值ID",         save=True, decoder=json.decode, encoder=json.encode),
    define(0x0601, "offline_recharges",   "sequence", "回调时玩家离线缓存充值ID", save=True, decoder=json.decode, encoder=json.encode),

    define(0x0602, "limited_packs_flag", "boolean", "是否开启开启限购礼包", sync=True, formula="fn.get_limited_packs_flag()"),
    define(0x0603, "limited_packs_used_count", "integer", "已用购买限购礼包次数", save=True, default=0),
    define(0x0604, "limited_packs_rest_count", "integer", "可用购买限购礼包次数", sync=True, formula="fn.get_limited_packs_rest_count(limited_packs_used_count)"),
    define(0x0605, "limited_packs_last_time",  "integer", "上次购买限购礼包时间", save=True, default=0),

    define(0x0607, "timelimited_packs_last_time",  "integer", "上次购买限时礼包时间", save=True, default=0),
    define(0x0608, "timelimited_packs_rest_time",  "integer", "限时礼包剩余购买时间", formula="fn.get_timelimited_packs_rest_time()", sync=True),
    define(0x0609, "timelimited_packs_rest_count", "integer", "限时礼包剩余购买次数", formula="fn.get_timelimited_packs_rest_count(timelimited_packs_last_time)", sync=True),

    define(0x0610, "trigger_packs_buy_count", "integer", "触发礼包购买次数", save=True, default=0,    cycle=True, timestamp=0x0611),
    define(0x0612, "trigger_packs_flag",      "boolean", "是否开启触发礼包", save=True, default=True, cycle=True, timestamp=0x0613, sync=False),  # 关闭此功能
    # define(0x0612, "trigger_packs_flag",      "boolean", "是否开启触发礼包", save=True, default=False, sync=True),

    define(0x0620, "totallogin_after_guide",  "integer",  "新手引导结束后累计登陆天数", save=True),
    define(0x0621, "seriallogin_after_guide", "integer",  "新手引导结束后连续登录次数", save=True),

    define(0x0622, "first_recharge_flag",  "boolean", "首充礼包按钮是否显示", save=True, sync=True, default=True),

    define(0x0623, "first_recharge_recv",  "boolean", "首充礼包可否领取", formula="fn.get_first_recharge_recv(bought_recharges, first_recharge_flag)", sync=True),

    define(0x0624, "first_recharge_numb",  "integer", "首充礼包赠送金额", save=True, default=0),

    define(0x0625, "first_recharge_patch", "boolean", "首充礼包补偿", save=True, default=False),

    define(0x0630, "cleanfb", "integer",  "扫荡券",  save=True, sync=True, default=0),
    define(0x0631, "clean_campaign_vip", "integer", "活动副本扫荡vip等级", sync=True, formula="fn.get_clean_campaign_vip(vip)"),

    define(0x0700, "lineups_defend",   "sequence", "防守阵型", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0701, "on_lineup_defend", "integer",  "防守激活的阵形", save=True, sync=True, default=0),

    define(0x0702, "borderID",   "integer", "边框",   sync=True, save=True, default=0),

    define(0x0703, "rank_detail_cache", "dict", "随机到的对手缓存", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0704, "rank_count",            "integer", "总挑战次数",   save=True, sync=True, default=0),
    define(0x0705, "rank_active_count",     "integer", "主动挑战次数", save=True, sync=True, default=0),
    define(0x0706, "rank_active_win_count", "integer", "主动胜利场次", save=True, sync=True, default=0),
    define(0x0707, "rank_win_count",        "integer", "总胜利场次",   save=True, sync=True, default=0),

    define(0x0708, "rank_free_vs", "integer", "免费次数", save=True, sync=True, default=10, cycle=True, timestamp=0x0712),
    define(0x0709, "rank_cd",      "integer", "挑战CD",   save=True, sync=True, resume=10*60, syncTimeout=True, default=0),

    define(0x0710, "rank_history", "stored_sequence", "挑战历史", decoder=json.decode, encoder=json.encode),
    define(0x0711, "rank_fight_history", "stored_dict", "挑战战斗历史"),
    define(0x0713, "rank_passive_offline_count", "integer", "离线期间被打次数", save=True, sync=True, default=0),
    define(0x0714, "totalbp_on_logout", "integer", "离线时积分", save=True, sync=True, default=0),

    define(0x0715, "rank_targets",    "sequence", "pvp对手列表",  save=True, decoder=json.decode, encoder=json.encode),
    define(0x0716, "rank_defeated_targets", "set", "pvp打败了的对手", save=True, decoder=json.decode, encoder=json.encode),

    define(0x0717, "rank_rest_count", "integer",  "挑战剩余次数", save=True, sync=True, cycle=True, timestamp="rank_resume_rest_count_cd", resume=30*60, default=10, max='rank_rest_max_count'),
    define(0x0718, "rank_resume_rest_count_cd", "integer", "挑战次数恢复时间", save=True, sync=True, syncTimeout=True),

    define(0x0719, "rank_reset_used_count", "integer", "重置挑战次数已用次数", save=True, cycle=True, timestamp=0x0720, default=0),
    define(0x0721, "rank_reset_rest_count", "integer", "重置挑战次数可用次数", formula="fn.get_rank_reset_rest_count(vip, rank_reset_used_count)", sync=True),
    define(0x0722, "rank_reset_cost",       "integer", "重置挑战次数所需消耗", formula="fn.get_rank_reset_cost(rank_reset_used_count)", sync=True),

    define(0x0723, "rank_refresh_cd",         "integer", "免费刷新对手cd",       save=True, syncTimeout=True, sync=True),
    define(0x0724, "rank_refresh_used_count", "integer", "已经使用钻石刷新次数", save=True, default=0, cycle=True, timestamp=0x0740),
    define(0x0725, "rank_refresh_cost",       "integer", "钻石刷新的消耗", formula="fn.get_rank_refresh_cost(rank_refresh_used_count)", sync=True),

    define(0x0726, "rank_serial_win_count",    "integer", "连胜",   save=True, sync=True, default=0),
    define(0x0727, "rank_serial_win_count_cd", "integer", "连胜cd", save=True, sync=True, default=0, syncTimeout=True),
    define(0x0730, "npc_targets_cd", "dict", "npc对手cd时间", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0731, "npc_target_cache", "integer", "对手缓存", save=True, default=0),

    define(0x0732, "rank_rest_max_count", 'integer', '挑战次数上限', default=10),
    define(0x0733, "rank_revenged_targets", "set", "pvp已经复仇的对手", save=True, decoder=json.decode, encoder=json.encode),

    # 点将台
    define(0x0780, "hotpet_set",   "set",      "已显示过的热点精灵的csvid", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0781, "today_hotpet", "integer",  "今日热点精灵的csvid", save=True, default=0),
    define(0x0782, "superhotpet",  "integer",  "热点超精灵的csvid", save=True, default=0),
    define(0x0783, "petpalt_time", "datetime", "今日热点精灵上次刷新时间", save=True),

    define(0x0800, "mats", "stored_dict", "物品", int_key=True, int_value=True),
    define(0x0801, "dirty_mats", "set", "需要同步的物品"),

    define(0x0900, "fp",             "integer", "公会声望",         save=True, sync=True, default=0),
    define(0x0901, "totalfp",        "integer", "总公会贡献",       save=True, sync=True, default=0),

    define(0x0902, "todayfp_donate",     "integer", "今日公会捐献贡献",     save=True, sync=True, cycle=True, timestamp=0x0903, default=0),
    define(0x0904, "dismissCD",          "integer", "公会解散倒计时",   save=True, sync=True, default=0, syncTimeout=True),
    define(0x0905, "todayfp_sp",         "integer", "今日能量贡献",     save=True, sync=True, cycle=True, timestamp=0x0906, default=0),
    define(0x0907, "faction_sp",         "integer", "消耗能量（按比例转化为声望）", save=True, default=0),
    define(0x0908, "todayfp_sp_max",     "integer", "今日能量贡献上限", sync=True, formula="fn.get_todayfp_sp_max()"),
    define(0x0909, "todayfp_donate_max", "integer", "今日公会捐献贡献上限", sync=True, formula="fn.get_todayfp_donate_max()"),
    define(0x0910, "todayfp_task",       "integer", "今日任务贡献",     save=True, sync=True, cycle=True, timestamp=0x0911, default=0),
    define(0x0912, "todayfp",            "integer", "今日总贡献",       sync=True, formula="todayfp_sp + todayfp_donate + todayfp_task"),

    define(0x0950, "giftkeys", "stored_dict", "cdkey使用次数", int_value=True),

    define(0x0980, "equipset",  "set",     "拥有装备的ID", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0981, "equips",    "dict",  "玩家的所有装备"),
    define(0x0982, "equipeds", "dict", "已经装备的装备"),
    # 掠夺
    define(0x0990, "mine_rob_history_flag",     "boolean", "被掠夺", save=True, sync=True, default=False),
    define(0x0991, "mine_curr_target_cache",    "integer", "", save=True),
    define(0x0992, "mine_revenge_booty_cache",  "integer", "复仇获得缓存",  save=True, default=-1),
    define(0x0993, "mine_targets_detail_cache", "list", "匹配对手详细缓存", save=True, decoder=json.decode, encoder=json.encode),
    define(0x0994, "mine_rob_history",         "stored_sequence", "掠夺历史", decoder=json.decode, encoder=json.encode),
    define(0x0996, "mine_rob_count",           "integer", "掠夺次数",       save=True, sync=True, cycle=True, resume=120*60, timestamp="resume_mine_rob_count_cd", max="mine_rob_max_count"),
    define(0x0997, "resume_mine_rob_count_cd", "integer", "掠夺次数恢复CD", save=True, sync=True, syncTimeout=True),
    define(0x0998, "mine_rob_max_count",       "integer", "最大掠夺次数",   sync=True, formula="fn.get_mine_rob_max_count(vip)"),
    define(0x0999, "mine_protect_time",   "integer", "保护时间",        save=True, sync=True, syncTimeout=True, default=0),

    define(0x1000, "mine_products1",           "integer", "矿1",                     save=True, sync=True, default=0),
    define(0x1001, "mine_productivity1",       "integer", "矿速率1",                 save=True, sync=True, default=0),
    define(0x1002, "mine_safety1",             "integer", "矿保底值1",               sync=True, formula="fn.get_mine_safety(1, mine_level1)"),
    define(0x1003, "mine_time1",               "integer", "矿上次产出时间1",         save=True, default=0),
    define(0x1004, "mine_time_past1",          "integer", "矿上次产出距离现在时间1", sync=True, formula="fn.get_past_time(mine_time1)"),
    define(0x1005, "mine_maximum1",            "integer", "矿最大值1",               sync=True, formula="fn.get_mine_maximum(1, mine_level1)"),
    define(0x1006, "mine_free_collect_count1", "integer", "免费收集次数1",           save=True, sync=True, cycle=True, timestamp=0x1007, default=1),
    define(0x1008, "mine_level1",              "integer", "矿等级1",                 sync=True, formula="fn.get_mine_level(1, level)"),
    define(0x1009, "mine_rob_by_date1",        "stored_dict", "记录每日掠夺所得1", int_value=True),

    define(0x1010, "mine_products2",           "integer", "矿2",                     save=True, sync=True, default=0),
    define(0x1011, "mine_productivity2",       "integer", "矿速率2",                 save=True, sync=True, default=0),
    define(0x1012, "mine_safety2",             "integer", "矿保底值2",               sync=True, formula="fn.get_mine_safety(2, mine_level2)"),
    define(0x1013, "mine_time2",               "integer", "矿上次产出时间2",         save=True, default=0),
    define(0x1014, "mine_time_past2",          "integer", "矿上次产出距离现在时间2", sync=True, formula="fn.get_past_time(mine_time2)"),
    define(0x1015, "mine_maximum2",            "integer", "矿最大值2",               sync=True, formula="fn.get_mine_maximum(2, mine_level2)"),
    define(0x1016, "mine_free_collect_count2", "integer", "免费收集次数2",           save=True, sync=True, cycle=True, timestamp=0x1017, default=1),
    define(0x1018, "mine_level2",              "integer", "矿等级2",                 sync=True, formula="fn.get_mine_level(2, level)"),
    define(0x1019, "mine_rob_by_date2",        "stored_dict", "记录每日掠夺所得2", int_value=True),

    define(0x1100, "uproar_targets_cache",  "list",    "匹配对手缓存", save=True, decoder=json.decode, encoder=json.encode),
    define(0x1101, "uproar_targets_done",   "set",    "已打败对手",   save=True, decoder=json.decode, encoder=json.encode),
    define(0x1102, "uproar_chests_done",    "set",    "已领取宝箱",   save=True, decoder=json.decode, encoder=json.encode),
    define(0x1103, "uproar_target_cache",   "integer", "验证对手",     save=True, default=0),

    define(0x1104, "uproar_refresh_used_count",  "integer", "重置已用次数", save=True, cycle=True, timestamp=0x1105, default=0),
    define(0x1106, "uproar_refresh_rest_count",  "integer", "重置剩余次数", sync=True, formula="uproar_refresh_max_count - uproar_refresh_used_count"),
    define(0x1107, "uproar_refresh_max_count",   "integer", "重置最大次数", formula="fn.get_uproar_refresh_max_count(vip)"),
    define(0x1108, "jiutian", "integer", "九天币", save=True, sync=True, default=0),
    define(0x1109, "last_target", "integer", "对手进度",  sync=True, formula="fn.get_uproar_last_target(uproar_targets_done)"),
    define(0x1110, "last_chest",  "integer", "宝箱进度",  sync=True, formula="fn.get_uproar_last_chest(uproar_chests_done)"),
    define(0x1111, "uproar_targets_team", "stored_dict", "对手阵型缓存", int_key=True),
    define(0x1112, "uproar_chests_cache",  "list",   "宝箱缓存", save=True, decoder=json.decode, encoder=json.encode),
    define(0x1113, "uproar_details_cache", "stored_dict", "详细缓存",  int_key=True, encoder=cPickle.dumps, decoder=cPickle.loads),
    define(0x1114, "uproar_enemy_buff", "integer", "敌方属性加成", save=True, sync=True, default=0),
    define(0x1115, "uproar_enemy_min_power", "integer", "匹配最低战力", save=True, default=0),
    define(0x1116, "uproar_targets", "stored_dict", "匹配对手", int_key=True, encoder=cPickle.dumps, decoder=cPickle.loads),
    define(0x1117, "uproar_chests", "stored_dict", "宝箱", int_key=True, encoder=cPickle.dumps, decoder=cPickle.loads),

    # 夺宝
    define(0x1300, "loot_used_count",       "integer", "已夺宝次数",   save=True, cycle=True, timestamp=0x1301, default=0),
    define(0x1302, "loot_rest_count",       "integer", "剩余夺宝次数", sync=True, formula="loot_max_count - loot_used_count"),
    define(0x1303, "loot_max_count",        "integer", "最大夺宝次数", default=5),
    define(0x1304, "loot_last_resume_time", "integer", "上次恢复夺宝的时间", save=True, default=0),
    define(0x1305, "loot_temp_mats",    "stored_dict", "被掠夺的材料数量", int_key=True, int_value=True),
    define(0x1310, "loot_targets_cache",    "list",    "夺宝匹配对手缓存",  save=True, decoder=json.decode, encoder=json.encode),
    define(0x1311, "loot_current_target",   "integer", "当前夺取的对手", save=True, default=0),
    define(0x1312, "loot_history", "stored_sequence", "夺宝历史", decoder=json.decode, encoder=json.encode),
    define(0x1313, "loot_reset_count",      "integer",  "重置夺宝次数", sync=True, save=True, cycle=True, timestamp=0x1314, default=0),
    define(0x1315, "loot_reset_crit_count", "integer",  "刷新保底计数", save=True, cycle=True, timestamp=0x1316, default=0),
    define(0x1317, "loot_protect_time",     "integer",  "掠夺保护时间", save=True, default=0),

    define(0x1320, "reward_campaign_opened", "boolean", "翻倍奖励活动开启标识", sync=True, formula="fn.get_reward_campaign_opened()"),
    # 拜八仙
    # define(0x1350, "visit_count", "integer", "拜八仙剩余次数", save=True, sync=True, cycle=True, default=1, timestamp=0x1351),
    # define(0x1352, "visit_visited", "set",   "已经拜访的",     save=True, decoder=json.decode, encoder=json.encode),
    # define(0x1347, "visitreceiveds",  "set", "是否已经领取排名奖励", save=True, decoder=json.decode, encoder=json.encode),
    define(0x1345, "pious_backup",           "integer", "虔诚度备份",         save=True, default=0),
    define(0x1346, "visit_group",            "integer", "上次转盘配置组",     save=True, default=0),
    define(0x1347, "visit_time",             "integer", "上次转盘时间",       save=True, default=0),
    define(0x1348, "dream",                  "integer", "梦幻转盘抽奖券",     save=True, sync=True,  default=0),
    define(0x1349, "pious",                  "integer", "虔诚度",             save=True, sync=True,  default=0),
    define(0x1353, "visit_free_used_count",  "integer", "拜八仙免费已用次数", save=True, cycle=True, default=0, timestamp=0x1354),
    define(0x1355, "visit_free_rest_count",  "integer", "拜八仙免费剩余次数", sync=True, formula="fn.get_visit_free_rest_count(visit_free_used_count)"),
    define(0x1356, "visit_today_used_count", "integer", "今日已拜八仙次数",   save=True, cycle=True, default=0, timestamp=0x1357),
    define(0x1359, "visit_cost",             "integer", "拜八仙消耗",         sync=True, formula="fn.get_visit_cost()"),

    # 化缘
    define(0x1360, "beg_flag", "boolean", "可否化缘", sync=True, formula="fn.get_beg_flag(taskrewards, task_sp_daily_receiveds)"),

    # 升级礼包
    define(0x1380, "level_packs_done", "set", "可领取的升级礼包", save=True, decoder=json.decode, encoder=json.encode),
    define(0x1381, "level_packs_end",  "set", "已领取的升级礼包", save=True, decoder=json.decode, encoder=json.encode),
    define(0x1382, "level_packs_flag", "boolean", "开关升级礼包按钮", sync=True, formula="fn.get_level_packs_flag(level_packs_done, level_packs_end)"),
    define(0x1383, "level_packs_done_count", "integer", "可领取的升级礼包个数", sync=True, formula="len(level_packs_done)"),

    define(0x1390, "power_packs_done", "set", "可领取的战力礼包", save=True, decoder=json.decode, encoder=json.encode),
    define(0x1391, "power_packs_end",  "set", "已领取的战力礼包", save=True, decoder=json.decode, encoder=json.encode),
    define(0x1392, "power_packs_flag", "boolean", "开关战力礼包按钮", sync=True, formula="fn.get_power_packs_flag(power_packs_done, power_packs_end)"),
    define(0x1393, "power_packs_done_count", "integer", "可领取的战力礼包个数", sync=True, formula="len(power_packs_done)"),

    # 累计登录
    define(0x1400, "totallogin_end", "set", "累计登录已领取", save=True, decoder=json.decode, encoder=json.encode),
    define(0x1401, "totallogin_flag", "boolean", "开关累计登录按钮", sync=True, formula="fn.get_totallogin_flag(totallogin_end)"),

    # 公会加成属性
    define(0x1500, "factionHP",  "float", "公会加成血量", formula="fn.get_faction_hp(strengthen_hp_level)"),
    define(0x1501, "factionATK", "float", "公会加成攻击", formula="fn.get_faction_atk(strengthen_at_level)"),
    define(0x1502, "factionDEF", "float", "公会加成防御", formula="fn.get_faction_def(strengthen_df_level)"),
    define(0x1503, "factionCRI", "float",   "公会加成暴击", formula="fn.get_faction_crit(strengthen_ct_level)"),
    define(0x1504, "factionEVA", "float",   "公会加成闪躲", default=0.0),

    # 战斗力
    define(0x1600, "base_power",    "float", "基础战斗力", formula="fn.get_base_power(entityID, lineups)"),
    define(0x1601, "equip_power",   "float", "装备战斗力", formula="fn.get_equip_power(entityID, lineups)"),
    define(0x1602, "faction_power", "float", "公会战斗力", formula="fn.get_faction_power(factionHP, factionATK, factionDEF, factionCRI, factionEVA)"),
    define(0x1603, "max_power", "integer", "历史最高战斗力", save=True, default=0, sync=True),

    define(0x1604, "power_cache", "integer", "战斗力缓存", save=True, default=0),

    # 星级奖励
    define(0x1700, "star_packs_end", "set", "已领取星级奖励", save=True, decoder=json.decode, encoder=json.encode),
    define(0x1701, "star_packs_version", "integer", "星级奖励版本", save=True, default=0),

    # 设备信息
    define(0x1800, "appid", "string", "应用id", save=True),
    define(0x1801, "UDID",  "string", "UDID",   save=True),
    define(0x1802, "idfa",  "string", "idfa",   save=True),
    define(0x1803, "IMEI",  "string", "IMEI",   save=True),
    define(0x1804, "MAC",   "string", "MAC",    save=True),

    define(0x1805, "new_role",          "boolean", "新键角色",         sync=True, default=False),
    define(0x1810, "autofight", "boolean", "是否开启自动战斗", sync=True, save=True, default=False),
    define(0x1811, "speedUpfight", "boolean", "是否开启自动战斗", sync=True, save=True, default=False),

    define(0x1900, "dongtian_cd", "integer", "洞天挑战cd冷却时长", sync=True, save=True, default=0, syncTimeout=True),
    define(0x1901, "fudi_cd",     "integer", "福地挑战cd冷却时长", sync=True, save=True, default=0, syncTimeout=True),

    define(0x2000, "treasure_type",          "integer", "金银山宝箱类型",   sync=True, save=True, default=1),
    define(0x2001, "treasure_refresh_count", "integer", "金银山刷新次数",   save=True, default=0),
    define(0x2002, "treasure_cache",         "sequence",  "金银山cache",    save=True, decoder=json.decode, encoder=json.encode),
    define(0x2003, "treasure_count",         "integer", "金银山count",      sync=True, formula="max(treasure_max_count - treasure_used_count, 0)"),
    define(0x2004, "treasure_cd",            "integer", "金银山cd",         save=True, sync=True, default=0, syncTimeout=True),
    define(0x2005, "treasure_max_count",     "integer", "金银山count_max",  sync=True, formula="fn.get_treasure_max_count(vip)"),
    define(0x2006, "treasure_used_count",    "integer", "金银山已用次数",   save=True, default=0, cycle=True, timestamp=0x2007),
    define(0x2008, "treasure_chest_gold",   "integer", "宝箱里面的金币数", sync=True, formula="fn.get_treasure_chest_gold(treasure_type)"),

    define(0x2098, "friend_messages_count", "integer", "好友消息数量", sync=True, formula="fn.get_friend_messages_count(friend_messages)"),
    define(0x2099, "friend_messages", "stored_dict",  "好友消息", int_key=True, decoder=json.decode, encoder=json.encode),
    define(0x2100, "friendset",        "set",      "好友列表",        save=True,    decoder=json.decode, encoder=json.encode),
    define(0x2101, "friend_count",     "integer",     "好友数量",     sync=True,    formula="len(friendset)"),
    define(0x2102, "friend_max_count", "integer",     "好友上限",     sync=True,    formula="fn. get_friend_max_count(level)"),

    define(0x2103, "friend_applys",    "stored_dict", "好友申请列表", int_key=True, decoder=json.decode, encoder=json.encode),
    define(0x2104, "friend_applys_count", "integer",  "好友申请数量", sync=True, formula="len(friend_applys)"),

    define(0x2105, "friend_gift_used_count", "integer", "今日已经赠送能量次数", sync=True,  cycle=True, timestamp=0x2106, default=0),
    define(0x2107, "friend_gift_max_count",  "integer", "今日最大可赠送能量次数", sync=True, formula="fn.get_friend_gift_max_count(level)"),
    define(0x2108, "friendgiftedset", "set", "今日已赠送能量好友",  save=True, cycle=True, timestamp=0x2109, decoder=json.decode, encoder=json.encode),


    define(0x2200, "tap_hurts",       "sequence",  "群魔乱舞伤害序列", save=True, decoder=json.decode, encoder=json.encode),
    define(0x2201, "tap_hurts_index", "integer",   "群魔乱舞进度",     save=True, default=0),
    define(0x2202, "tap_monster",     "integer",   "群魔乱舞怪物",     save=True, default=0),
    define(0x2203, "tap_loop_count",  "integer",   "群魔乱舞怪物计数", save=True, default=0),

    define(0x2204, "tap_rest_count",  "integer",   "群魔乱舞剩余攻击次数", save=True, sync=True, default=120, cycle=True, resume=2 * 60, timestamp="tap_rest_count_resume_cd", max="tap_max_count"),
    define(0x2205, "tap_rest_count_resume_cd", "integer", "群魔乱舞剩余攻击次数恢复时间", save=True, sync=True, default=0, syncTimeout=True),
    define(0x2206, "tap_max_count",   "integer",   "群魔乱舞最大攻击次数", sync=True, default=120),
    define(0x2207, "tap_onekey",      "integer",   "群魔乱舞可否一键", sync=True, formula="fn.get_tap_onekey(vip)"),
    define(0x210a, "friendfb_list",              "stored_set",  "秘境列表"),
    define(0x210b, "friend_total_sp",            "integer",     "推图消耗能量总数(触发秘境后清零)", default=0, save=True),
    define(0x210c, "cache_friendfbID",           "string",      "缓存好友副本id",         save=True),
    define(0x210d, "friendfb_triggered_count",   "integer",     "已经触发秘境次数",       save=True, default=0),
    define(0x210e, "friendfb_last_trigger_time", "integer",     "上次触发秘境副本的时间", save=True, default=0),
    define(0x210f, "friendfb_last_trigger_fbID", "integer",     "上次触发的秘境副本", save=True, default=0),
    define(0x2110, "friendfb_used_count",        "integer",     "秘境已挑战次数",     save=True, cycle=True, timestamp=0x2111),
    define(0x2112, "friendfb_remain_count",      "integer",     "秘境剩余挑战次数",   sync=True, formula="fn.get_friendfb_remain_count(friendfb_used_count)"),
    define(0x2113, "friendfb_kill_count",        "integer",     "秘境击杀次数",       save=True, default=0, event=True),
    define(0x2114, "friendfb_deads",             "stored_set",  "秘境已阵亡"),
    define(0x2115, "friendfb_reborn_counts",     "stored_dict", "秘境复活次数",     int_value=True),
    define(0x2116, "friendfb_damages",           "stored_dict", "秘境历史最高伤害", int_key=True, int_value=True),
    define(0x2117, "friendfb_buff",              "integer",     "复活buff加成",     sync=True, save=True, default=0),
    define(0x2118, "friendfb_deadtimes",         "stored_dict",  "秘境已阵亡"),

    define(0x2300, "malls",              "stored_dict", "商店商品",     int_key=True, decoder=json.decode, encoder=json.encode),
    define(0x2301, "mall_times",         "stored_dict", "商店购买时间", int_key=True, int_value=True),
    define(0x2302, "mall_limits",        "dict", "商店限次",            save=True, encoder=msgpack.dumps, decoder=msgpack.loads),
    define(0x2304, "mall_refresh_times", "dict", "商店刷新次数",        save=True, encoder=msgpack.dumps, decoder=msgpack.loads, cycle=True, timestamp=0x2305),
    define(0x2306, "mall_last_refresh",  "dict", "商店上次刷新时间",    save=True, encoder=msgpack.dumps, decoder=msgpack.loads),

    define(0x2350, "mall_silver_opened",      "boolean", "开启银角商店",        sync=True, save=True, default=False),
    define(0x2351, "mall_silver_open_cost",   "integer", "开启银角商店消耗",    sync=True, formula="fn.get_mall_silver_open_cost(vip, level, mall_silver_opened)"),
    define(0x2352, "mall_silver_open_remain", "integer", "临时银角剩余时间",    save=True, sync=True, syncTimeout=True, default=0),
    define(0x2353, "mall_silver_open_vip",    "integer", "开启银角商店vip等级", sync=True, formula="fn.get_mall_silver_open_vip()"),

    define(0x2360, "mall_golden_opened",      "boolean", "开启金角商店",        sync=True, save=True, default=False),
    define(0x2361, "mall_golden_open_cost",   "integer", "开启金角商店消耗",    sync=True, formula="fn.get_mall_golden_open_cost(vip, level, mall_golden_opened)"),
    define(0x2362, "mall_golden_open_remain", "integer", "临时金角剩余时间",    save=True, sync=True, syncTimeout=True, default=0),
    define(0x2363, "mall_golden_open_vip",    "integer", "开启金角商店vip等级", sync=True, formula="fn.get_mall_golden_open_vip()"),
    define(0x2364, "shopping",                "integer", "商店刷新令", sync=True, save=True, default=0),

    define(0x2400, 'mailcount', "integer", "邮件数量",   formula="len(mails)", sync=True),

    define(0x2500, "vip_packs_limits", "dict", "vip礼包限次", save=True, encoder=msgpack.dumps, decoder=msgpack.loads),
    define(0x2501, "vip_packs_today_bought_count", "integer", "今日购买礼包次数", save=True, default=0, cycle=True, timestamp=0x2502),
    define(0x2503, "vip_packs_flag",     "boolean", "vip0礼包可以领取", sync=True, formula="fn.get_vip_packs_flag(vip, vip_packs_today_bought_count)"),
    define(0x2504, "vip_packs_limits_reset_flag", "boolean", "重置标识字段", save=True, default=False),

    define(0x2550, "wish_used_count",      "integer", "已经许愿次数", save=True, default=0),
    define(0x2552, "wish_rest_count",      "integer", "剩余许愿次数", formula="fn.get_wish_rest_count(wish_used_count)", sync=True),
    define(0x2553, "wish_remain_time",     "integer", "许愿剩余时间", formula="fn.get_wish_remain_time()", syncTimeout=True, sync=True),
    define(0x2554, "wish_experience_time", "integer", "许愿体验时间", save=True, default=0, syncTimeout=True, sync=True),
    define(0x2555, "wish_last_reset_time", "integer", "许愿重置时间", save=True, default=0),

    define(0x2556, "weeks_acc_recharge_amount",      "integer", "周累计充值", save=True, sync=True, default=0),
    define(0x2557, "weeks_acc_recharge_remain_time", "integer", "周累计充值剩余时间",  formula="fn.get_weeks_acc_recharge_remain_time()", syncTimeout=True, sync=True),
    define(0x2558, "weeks_acc_recharge_can_receive", "boolean", "可以领取周累计充值奖励", sync=True, formula="fn.get_weeks_acc_recharge_can_receive(weeks_acc_recharge_rewards)"),
    define(0x2559, "weeks_acc_recharge_last_clean_time", "integer", "上次清楚周累计充值时间", save=True, default=0),

    define(0x2560, "daily_acc_recharge_amount",      "integer", "每日累计充值", save=True, sync=True, default=0, cycle=True, timestamp=0x2561),
    define(0x2562, "daily_acc_recharge_remain_time", "integer", "每日累计充值剩余时间", formula="fn.get_daily_acc_recharge_remain_time()", syncTimeout=True, sync=True),
    define(0x2563, "daily_acc_recharge_can_receive", "boolean", "可以领取每日累计充值奖励", sync=True, formula="fn.get_daily_acc_recharge_can_receive(daily_acc_recharge_rewards)"),

    define(0x2565, "cycle_acc_recharge_amount",      "integer", "累计充值", save=True, sync=True, default=0),
    define(0x2567, "cycle_acc_recharge_remain_time", "integer", "累计充值剩余时间", formula="fn.get_cycle_acc_recharge_remain_time()", syncTimeout=True, sync=True),
    define(0x2568, "cycle_acc_recharge_can_receive", "boolean", "可以领取累计充值奖励", sync=True, formula="fn.get_cycle_acc_recharge_can_receive(cycle_acc_recharge_rewards)"),
    define(0x2569, "cycle_acc_recharge_last_clean_time", "integer", "上次清除累计充值的时间", save=True, default=0),

    define(0x2571, "daily_acc_recharge_rewards", "set", "可以领取每日累计充值奖励", save=True, encoder=json.encode, decoder=json.decode, cycle=True, timestamp=0x2572),
    define(0x2573, "cycle_acc_recharge_rewards", "set", "可以领取累计充值奖励",     save=True, encoder=json.encode, decoder=json.decode),
    define(0x2574, "weeks_acc_recharge_rewards", "set", "可以领取周累计充值奖励",   save=True, encoder=json.encode, decoder=json.decode),
    define(0x2575, "month_acc_recharge_rewards", "set", "可以领取月累计充值奖励",   save=True, encoder=json.encode, decoder=json.decode),

    define(0x2580, "month_acc_recharge_amount",          "integer", "月累计充值",             save=True, sync=True, default=0),
    define(0x2581, "month_acc_recharge_remain_time",     "integer", "月累计充值剩余时间",     formula="fn.get_month_acc_recharge_remain_time()", syncTimeout=True, sync=True),
    define(0x2582, "month_acc_recharge_can_receive",     "boolean", "可以领取月累计充值奖励", sync=True, formula="fn.get_month_acc_recharge_can_receive(month_acc_recharge_rewards)"),
    define(0x2583, "month_acc_recharge_last_clean_time", "integer", "上次清楚月累计充值时间", save=True, default=0),

    define(0x2600, "fund_bought_flag",  "boolean", "是否已经购买开服基金", sync=True, save=True, default=False),
    define(0x2601, "fund_rewards_received",  "set", "已领取基金奖励", save=True, decoder=json.decode, encoder=json.encode),
    define(0x2602, "fund_open_rewards_can_receive", "boolean", "有开服基金奖励可以领取", sync=True, formula="fn.get_fund_open_rewards_can_receive(fund_bought_flag, fund_rewards_received, level)"),
    define(0x2603, "fund_full_rewards_can_receive", "boolean", "有全民福利奖励可以领取", sync=True, formula="fn.get_fund_full_rewards_can_receive(fund_rewards_received)"),
    define(0x2604, "fund_reset_time",               "integer", "上次重置开服基金的时间", save=True, default=0),

    define(0x26ff, "check_in_over_count", "integer",  "已过期天数",   sync=True, save=True, default=0),
    define(0x2700, "check_in_used_count", "integer",  "已签到天数",   sync=True, save=True, default=0),
    define(0x2701, "check_in_rest_count", "integer",  "可补签天数",   sync=True, formula="fn.get_check_in_rest_count(createtime, check_in_used_count, check_in_today)"),
    define(0x2702, "check_in_today",      "boolean",  "今日已签到",   sync=True, save=True, default=False, cycle=True, timestamp=0x2703),
    define(0x2704, "check_in_last_time",  "datetime", "上次签到时间", save=True),

    define(0x2750, "timed_store_cd", "integer", "限时商店cd", sync=True, save=True, default=0, syncTimeout=True),
    define(0x2751, "timed_store_id", "integer", "限时商店id", save=True, default=0),

    define(0x2800, "trigger_event",    "integer", "触发事件ID",   save=True, default=0),
    define(0x2801, "trigger_event_sp", "integer", "触发事件sp",   save=True, default=0),
    define(0x2802, "trigger_chests",   "set",     "已抽宝箱索引", save=True, decoder=json.decode, encoder=json.encode),
    define(0x2803, "trigger_tasks",    "set",     "触发任务",     save=True, decoder=json.decode, encoder=json.encode, cycle=True, timestamp=0x2804),

    define(0x2848, "monthly_card_time",          "datetime", "月卡激活时间", save=True),
    define(0x2849, "monthly_card",               "integer",  "月卡剩余天数", sync=True, formula="fn.get_monthly_card(monthly_card_time, monthly_card_received)"),
    define(0x2850, "monthly_card_received",      "boolean",  "月卡今日奖励是否领取", sync=True, save=True, default=False, cycle=True, timestamp=0x2851),
    define(0x2852, "monthly_card_acc_amount",    "integer",  "月卡累计金额", save=True, default=0),
    define(0x2853, "monthly_card_remain_amount", "integer",  "月卡激活还需金额", sync=True, formula="fn.get_monthly_card_remain_amount(monthly_card_acc_amount)"),
    define(0x2854, "skip_guide",                 "boolean",  "跳过新手指引", save=True, sync=True, raw_default="fn.get_skip_guide()"),

    define(0x2860, "spar_counts",   "dict", "晶石召唤计数", save=True, encoder=msgpack.dumps, decoder=msgpack.loads),

    define(0x2861, "username_alias", "string", "用户名别名", save=True),
    define(0x2862, "chat_blocked", "boolean", "禁言，发言自己能看到，其他人看不到", save=True),
    define(0x2863, "lock_level", "integer", "锁定等级", save=True),
    define(0x2864, "channel", "string", "小渠道", save=True),

    define(0x2867, "point_power",  "float", "成就战斗力", formula="fn.get_point_power(entityID, point, lineups)"),
    define(0x2868, "point_addition",   "integer", "成就加成", sync=True, formula="fn.get_point_addition(point)"),
    define(0x2869, "point", "integer", "成就", save=True, sync=True, default=0),
    define(0x2870, "stone",                   "integer", "熔石", save=True, sync=True),
    define(0x2871, "enchant_stone_cost",      "integer", "普通重铸消耗基数", sync=True, formula="fn.get_enchant_stone_cost()"),
    define(0x2872, "enchant_ex_stone_cost",   "integer", "高级重铸消耗基数", sync=True, formula="fn.get_ex_enchant_stone_cost()"),
    define(0x2873, "enchant_stone_to_gold",   "integer", "熔石兑换比例",     sync=True, formula="fn.get_enchant_stone_to_gold()"),
    define(0x2874, "enchant_free_used_count", "integer", "已用免费重铸次数", save=True, cycle=True, timestamp=0x2875, default=0),
    define(0x2876, "enchant_free_rest_count", "integer", "剩余免费重铸次数", sync=True, formula="fn.get_enchant_free_rest_count(enchant_free_used_count)"),

    define(0x2880, "sames", "dict", "同名将映射", formula="fn.get_sames(pets)"),

    define(0x2890, "dlc_progress",     "stored_dict", "dlc进度",     int_key=True, decoder=json.decode, encoder=json.encode),
    define(0x2891, "dlc_helpers",      "stored_dict", "dlc助战cd",   int_key=True, int_value=True),
    define(0x2892, "dlc_dispatch",     "stored_dict", "dlc派驻",     int_key=True, decoder=json.decode, encoder=json.encode),
    define(0x2893, "dlc_star_packs_end", "set", "dlc已领取星级奖励", save=True, decoder=json.decode, encoder=json.encode),
    define(0x2894, "dlc_tasks",        "dict", "dlc任务",   formula="fn.get_dlc_tasks()"),
    define(0x2895, "dlc_tasks_cd",     "dict", "dlc任务cd", save=True, encoder=msgpack.dumps, decoder=msgpack.loads),
    define(0x2896, "dlc_detail_cache", "stored_dict", "dlc对手缓存", int_key=True, encoder=cPickle.dumps, decoder=cPickle.loads),
    define(0x2897, "dlc_opened",       "boolean",     "dlc开启中",   sync=True, formula="fn.get_dlc_opened()"),

    define(0x2900, "count_down_time",  "integer", "计时礼包开始时间", save=True, default=0),
    define(0x2901, "count_down_index", "integer", "当前礼包索引",     save=True, default=0),
    define(0x2902, "count_down_flag",  "boolean", "计时礼包图标开关", sync=True, formula="fn.get_count_down_flag(entityID, level, count_down_index)"),
    define(0x2903, "count_down_cd",    "integer", "计时礼包cd",       sync=True, syncTimeout=True, save=True, default=0),

    define(0x3000, "group_applys",           "object",  "同门申请列表"),
    define(0x3001, "groupID",                "integer", "同门ID",           sync=True, save=True, default=0),
    define(0x3002, "group_applys_count",     "integer", "同门申请人数",     sync=True, formula="len(group_applys or {})"),
    define(0x3003, "group_total_intimate",   "integer", "同门亲密度",       sync=True, save=True, default=0),
    define(0x3004, "group_last_kicked_time", "integer", "上次被踢出的时间", save=True, default=0),

    define(0x3012, "gve_damage",             "integer", "gve伤害",           sync=True, save=True, default=0),
    define(0x3014, "gve_score",              "integer", "gve评分",           sync=True, save=True, default=0),
    define(0x3016, "gve_index",              "integer", "gve位置",           save=True, default=0),
    define(0x3018, "gve_target",             "integer", "gve当前",           save=True, default=0),
    define(0x301a, "gve_state",              "integer", "gve状态",           sync=True, save=True, default=0),
    define(0x301b, "gve_addition",           "integer", "gve加成",           sync=True, save=True, default=0),
    define(0x301c, "gve_groupdamage",        "integer", "gve同门总伤害",     sync=True, save=True, default=0),
    define(0x301d, "gve_basereward",         "string",  "gve基础奖励",       sync=True, formula="fn.get_basereward(gve_groupdamage)"),
    define(0x301e, "gve_reborn_rest_count",  "integer", "gve复活剩余次数",   sync=True, save=True, default=1, cycle=True, timestamp=0x301f),
    define(0x3020, "gve_last_reset_time",    "integer", "gve上次重置的时间", save=True, default=0),
    define(0x3021, "gve_start_time",         "integer", "gve开始时间",       sync=True, syncTimeout=True, formula="fn.get_gve_start_time()"),
    define(0x3022, "gve_end_time",           "integer", "gve结束时间",       sync=True, syncTimeout=True, formula="fn.get_gve_end_time()"),
    define(0x3023, "gve_buff",               "integer", "gve buf加成百分比", sync=True, save=True, default=0),

    define(0x3024, "gve_reborn_cost",        "integer", "gve复活消耗",       sync=True, formula="fn.get_gve_reborn_cost()"),
    define(0x3025, "gve_buff_addition",      "integer", "gve复活后buff加成", sync=True, formula="fn.get_gve_buff_addition()"),
    define(0x3026, "gve_ranking_rewards",    "stored_set", "每日排行榜奖励"),

    define(0x3100, "last_region_name",       "string",  "前一个服务器名称",  sync=True, save=True),
    define(0x3101, "cache_fight_verify_code", "string", "缓存战斗校验码",   save=True),
    define(0x3102, "cache_fight_response",    "object", "缓存战斗返回数据", save=True, encoder=cPickle.dumps, decoder=cPickle.loads),

    define(0x3200, "boss_campaign_opened",   "boolean", "世界boss开启中",   formula="fn.get_boss_campaign_opened()", sync=True),
    define(0x3201, "boss_campaign_rewards",  "stored_set", "世界boss奖励记录"),

    define(0x3300, "skillpoint",     "integer", "技能点",    save=True, sync=True, cycle=True, resume=10*60, timestamp="skillpoint_cd", max="skillpoint_max"),
    define(0x3301, "skillpoint_cd",  "integer", "技能点cd",  save=True, sync=True, syncTimeout=True),
    define(0x3302, "skillpoint_max", "integer", "技能点max", sync=True, formula="fn.get_skillpoint_max(vip)"),

    define(0x3303, "buy_used_skillpoint_count", "integer", "已购买技能点次数", save=True, cycle=True, timestamp=0x3307, default=0),
    define(0x3304, "buy_rest_skillpoint_count", "integer", "可购买技能点次数", sync=True, formula="fn.get_buy_rest_skillpoint_count(vip, buy_used_skillpoint_count)"),
    define(0x3305, "buy_skillpoint_cost",       "integer", "购买技能点消耗",   sync=True, formula="fn.get_buy_skillpoint_cost(buy_used_skillpoint_count)"),
    define(0x3306, "buy_skillpoint_gain",       "integer", "购买技能点获得",   sync=True, formula="fn.get_buy_skillpoint_gain(buy_used_skillpoint_count)"),

    define(0x3313, "buy_used_soul_count", "integer", "已购买水晶次数", save=True, cycle=True, default=0, timestamp=0x3314),
    define(0x3315, "buy_rest_soul_count", "integer", "可购买水晶次数", sync=True, formula="fn.get_buy_rest_soul_count(vip, buy_used_soul_count)"),
    define(0x3316, "buy_soul_cost",       "integer", "购买水晶的消耗", sync=True, formula="fn.get_soul_cost(buy_used_soul_count)"),
    define(0x3317, "buy_soul_gain",       "integer", "购买水晶的获得", sync=True, formula="fn.get_soul_gain(buy_used_soul_count)"),

    define(0x3400, "swap_targets", "set", "pvp对手列表",  save=True, decoder=json.decode, encoder=json.encode),
    define(0x3401, "swap_cd", "integer", "pvp挑战cd", save=True, sync=True, syncTimeout=True, default=0),
    define(0x3402, "swap_refresh_cd_cost", "integer", "清除pvp挑战cd的消耗", sync=True, formula="fn.get_swap_refresh_cd_cost()"),
    define(0x3403, "swap_used_count", "integer", "pvp已挑战次的数", save=True, cycle=True, timestamp=0x3404, default=0, max="swap_most_count"),
    define(0x3405, "swap_rest_count", "integer", "pvp可挑战次的数", sync=True, formula="fn.get_swap_rest_count(swap_most_count, swap_used_count)"),
    define(0x3406, "swap_most_count", "integer", "pvp最大挑战次数", sync=True, formula="fn.get_swap_most_count()"),

    define(0x3407, "swap_used_reset_count", "integer", "pvp已重置的次数", save=True, cycle=True, timestamp=0x3408, default=0, max="swap_most_reset_count"),
    define(0x3409, "swap_rest_reset_count", "integer", "pvp可重置的次数", sync=True, formula="fn.get_swap_rest_reset_count(swap_most_reset_count, swap_used_reset_count)"),
    define(0x340a, "swap_most_reset_count", "integer", "pvp最大重置次数", formula="fn.get_swap_most_reset_count(vip)"),
    define(0x3411, "swap_reset_count_cost", "integer", "pvp重置次数消耗", sync=True, formula="fn.get_swap_reset_count_cost(swap_used_reset_count)"),
    define(0x3412, "swaprank", "integer", "pvp排名", sync=True, save=True, default=0),

    define(0x3413, "swap_history", "stored_sequence", "挑战历史", decoder=json.decode, encoder=json.encode),
    define(0x3414, "swap_fight_history", "stored_dict", "挑战战斗历史"),
    define(0x3415, "swap_win_count", "integer", "pvp胜利场次", sync=True, save=True, default=0),
    define(0x3416, "swapmaxrank", "integer", "pvp最高排名", save=True, default=0),
    define(0x3516, "swap_lock_cd",   "integer", "pvp战斗锁定cd", save=True, default=0),
    define(0x3517, "swap_register_time", "integer", "pvp注册时间", save=True, default=0),

    define(0x3500, "ball", "integer", "精灵球", sync=True, save=True, default=0),

    define(0x3600, "maze_step_count", "integer", "历史步数", sync=True, save=True, default=0),
    define(0x3601, "maze_rest_count", "integer", "可用步数", save=True, sync=True, cycle=True, timestamp="maze_count_cd", resume=10*60, max="maze_most_count"),
    define(0x3602, "maze_count_cd",   "integer", "步数恢复时间", save=True, sync=True, syncTimeout=True),
    define(0x3603, "maze_most_count", "integer", "最大步数", sync=True, formula="fn.get_maze_most_count()"),

    define(0x3605, "money_rest_pool", "integer", "奖励池剩余值", save=True, sync=True, default=0),
    define(0x3606, "money_most_pool", "integer", "奖励池最大值", sync=True, formula="level * 5000"),
    define(0x5607, "mazes", "list", "迷宫事件", save=True, decoder=decode_dict, encoder=encode_dict, default=list),
    define(0x5608, "maze_boss_cache", "integer", "boss战斗的时候缓存玩家选择的触发事件的索引", default=-1),
    define(0x5609, "maze_time_flag",  "integer", "当前最长一个迷宫事件的持续时间", sync=True, syncTimeout=True, formula="fn.get_maze_time_flag(mazes)"),
    define(0x5610, "maze_case_cost",  "integer", "迷宫宝箱三倍消耗", sync=True, formula="fn.get_maze_case_cost()"),

    define(0x5611, "maze_onekey_vip",   "integer", "迷宫可一键探索的vip等级",  sync=True, formula="fn.get_maze_onekey_vip()"),
    define(0x5612, "maze_onekey_point", "integer", "迷宫可一键探索的成就等级", sync=True, formula="fn.get_maze_onekey_point()"),

    define(0x5800, "online_packs_cd",        "integer",    "在线礼包",             sync=True, syncTimeout=True, save=True, default=0),
    define(0x5801, "online_packs_index",     "integer",    "在线礼包索引",         save=True, default=0),
    define(0x5802, "online_packs_last_recv", "integer",    "在线礼包上次领取时间", save=True, default=0),
    define(0x5003, "online_packs_flag",      "boolean",    "在线礼包开关",         sync=True, formula="fn.get_online_packs_flag(level, online_packs_done)"),
    define(0x5004, "online_packs_reset",     "integer",    "在线礼包重置时间",     save=True, default=0),
    define(0x5005, "online_packs_done",      "boolean",    "在线礼包全部领取完",   save=True, default=False),

    define(0x6000, "mail_reward_receiveds",  "stored_set", "记录邮件奖励是否已发"),
    define(0x7001, "refinery",   "integer", "炼化币", save=True, sync=True, default=0),

    define(0x8000, "daily_start_time", "integer", "每日PVP开始时间", sync=True, formula="fn.get_daily_start_time()", syncTimeout=True),
    define(0x8001, "daily_final_time", "integer", "每日PVP结束时间", sync=True, formula="fn.get_daily_final_time()", syncTimeout=True),
    define(0x8002, "daily_cache_targetID", "integer", "每日PVP随机对手ID", save=True, default=0),

    # define(0x8010, "win_point", "integer", "胜点", save=True, sync=True, cycle=True, default=0, timestamp=0x8011),
    # define(0x8012, "daily_cache_difficulty", "integer", "每日PVP难度缓存", save=True, default=0),
    define(0x8005, "daily_dead_resume",  "integer", "每日PVP自动复活（防止重复回复）", save=True, default=0),
    define(0x8006, "daily_reborn_cost",  "integer", "每日PVP复活消耗", sync=True, formula="fn.get_daily_reborn_cost()"),
    define(0x8007, "daily_dead_cd",    "integer", "每日PVP死亡倒计时", sync=True, save=True, syncTimeout=True, default=0),
    define(0x8008, "daily_dead",       "boolean", "每日PVP死亡", sync=True, formula="fn.get_daily_dead(entityID)"),
    define(0x8009, "daily_rewards",    "dict", "每日累计奖励", save=True, encoder=msgpack.dumps, decoder=msgpack.loads),
    define(0x8010, "daily_kill_count", "integer", "每日击杀人数", sync=True, save=True, default=0),
    define(0x8011, "daily_registered", "boolean", "每日PVP报名", sync=True, save=True, default=0),
    define(0x8012, "daily_count", "integer", "主动战斗次数", sync=True, default=0, save=True),
    define(0x8013, "daily_win_count", "integer", "连胜", sync=True, formula="fn.get_daily_win_count(entityID)"),
    define(0x8015, "daily_histories", "stored_sequence", "挑战历史", decoder=json.decode, encoder=json.encode),
    define(0x8016, "daily_history_flag",  "boolean", "挑战历史红点", default=False, save=True, sync=True),
    define(0x8017, "daily_max_win_count", "integer", "最大连胜", default=0, save=True, sync=True),
    define(0x8018, "daily_rank", "integer", "胜点排名", default=0, save=True, sync=True),
    define(0x8019, "daily_reset_time", "integer", "重置时间", default=0, save=True),

    define(0x8020, "daily_inspire_used_count", "integer", "鼓舞已用次数", default=0,  save=True),
    define(0x8022, "daily_inspire_most_count", "integer", "鼓舞最大次数", default=30, save=True, sync=True),
    define(0x8023, "daily_inspire_rest_count", "integer", "鼓舞剩余次数", sync=True, formula="daily_inspire_most_count - daily_inspire_used_count"),
    define(0x8025, "daily_inspire_buff",       "integer", "鼓舞buff",     sync=True, formula="daily_inspire_used_count * 2"),
    define(0x8026, "daily_inspire_cost",       "integer", "鼓舞消耗",     sync=True, formula="(daily_inspire_used_count + 1) * 10"),
    define(0x8027, "daily_end_panel",          "dict",    "结算面板", save=True, encoder=msgpack.dumps, decoder=msgpack.loads),
    define(0x8028, "daily_end_panel_flag",     "boolean", "结算面板", sync=True, formula="bool(daily_end_panel)"),

    define(0x8100, "task_seven_cd",   "integer", "活动倒计时",   sync=True, save=True, syncTimeout=True, default=0),

    define(0x8200, "guide_reward_flag", "boolean", "新手引导结束奖励",     save=True, sync=True, default=False),
    define(0x8201, "guide_defeat_flag", "boolean", "新手引导战斗失败奖励", save=True, sync=True, default=False),

    # define(0x8300, "ambition",          "integer", "野望",       save=True, sync=True, default=0),
    # define(0x8301, "vip_ambition",      "integer", "野望",       save=True, sync=True, default=0),
    define(0x8300, "ambition",           "string", "野望",       save=True, sync=True),
    define(0x8301, "vip_ambition",       "string", "野望",       save=True, sync=True),
    define(0x8302, "ambition_count",     "integer", "野望次数",   save=True, default=0, event=True),
    define(0x8303, "ambition_power",     "float", "野望战斗力", formula="fn.get_ambition_power(ambition, vip_ambition)"),
    define(0x8304, "ambition_cost",      "integer", "野望普通消耗", sync=True, formula="fn.get_ambition_cost()"),
    define(0x8305, "ambition_gold_cost", "integer", "野望钻石消耗", sync=True, formula="fn.get_ambition_gold_cost()"),

    define(0x8400, "player_equip1", "integer", "", sync=True, save=True, default=0),
    define(0x8401, "player_equip2", "integer", "", sync=True, save=True, default=0),
    define(0x8402, "player_equip3", "integer", "", sync=True, save=True, default=0),
    define(0x8403, "player_equip4", "integer", "", sync=True, save=True, default=0),
    define(0x8404, "player_equip5", "integer", "", sync=True, save=True, default=0),
    define(0x8405, "player_equip6", "integer", "", sync=True, save=True, default=0),

    define(0x8500, "consume_campaign_rest_time",    "integer", "累计消耗活动剩余时间", syncTimeout=True, sync=True, formula="fn.get_consume_campaign_rest_time()"),
    define(0x8501, "consume_campaign_rewards",      "set",     "累计消耗活动可领取奖励", save=True, decoder=json.decode, encoder=json.encode),
    define(0x8502, "consume_campaign_rewards_flag", "boolean", "累计消耗活动可领取奖励小红点", sync=True, formula="len(consume_campaign_rewards or [])"),
    define(0x8503, "consume_campaign_reset_time",   "integer", "累计消耗活动重置时间", save=True),
    define(0x8504, "consume_campaign_amount",       "integer", "累计消耗计数", save=True, sync=True, default=0),

    define(0x8550, "login_campaign_rest_time",        "integer", "累计登录活动剩余时间", syncTimeout=True, sync=True, formula="fn.get_login_campaign_rest_time()"),
    define(0x8551, "login_campaign_rewards",          "set",     "累计登录活动可领取奖励", save=True, decoder=json.decode, encoder=json.encode),
    define(0x8552, "login_campaign_rewards_flag",     "boolean", "累计登录活动可领取奖励小红点", sync=True, formula="len(login_campaign_rewards or [])"),
    define(0x8553, "login_campaign_reset_time",       "integer", "累计登录活动重置时间", save=True),
    define(0x8554, "login_campaign_amount",           "integer", "累计登录天数", save=True, sync=True, default=0),

    define(0x9000, "ranking_pet_count", "integer", "收集大于A、S的精灵数量", save=True, default=0, event=True),
    define(0x9001, "ranking_pet_power", "integer", "最强精灵战力", save=True, default=0, event=True),
    define(0x9002, "ranking_pet_power_entityID",    "integer", "最强精灵ID",     save=True, default=0),
    define(0x9003, "ranking_pet_power_prototypeID", "integer", "最强精灵配置ID", save=True, default=0),
    define(0x9004, "ranking_pet_power_breaklevel",  "integer", "最强精灵阶级",   save=True, default=0),
    define(0x9005, "rankingreceiveds",  "set", "是否已经领取排名奖励", save=True, decoder=json.decode, encoder=json.encode),
    define(0x9006, "ranking_receiveds",  "stored_set", "是否已经领取排名奖励"),

    define(0x9011, "ranking_equip_power",             "integer", "最强装备战力", save=True, default=0, event=True),
    define(0x9012, "ranking_equip_power_entityID",    "integer", "最强装备ID",     save=True, default=0),
    define(0x9013, "ranking_equip_power_prototypeID", "integer", "最强装备配置ID", save=True, default=0),
    define(0x9014, "ranking_equip_power_step",        "integer", "最强装备阶级",   save=True, default=0),
    define(0x9015, "ranking_equip_power_level",       "integer", "最强装备阶级",   save=True, default=0),


    define(0x9100, "daily_recharge_remain_time",   "integer", "每日单笔充值活动剩余时间", sync=True, syncTimeout=True, formula="fn.get_daily_recharge_remain_time()"),
    define(0x9101, "daily_recharge_rewards",       "list",    "每日单笔充值活动已领奖励", default=list, save=True, decoder=json.decode, encoder=json.encode, cycle=True, timestamp=0x9102),
    define(0x9103, "daily_recharge_useds",         "dict",    "每日单笔充值活动已领次数", save=True, encoder=msgpack.dumps, decoder=msgpack.loads, cycle=True, timestamp=0x9104),
    define(0x9105, "daily_recharge_rewards_count", "integer", "每日单笔充值活动的小红点", sync=True, formula="len(daily_recharge_rewards or [])"),

    define(0x9200, "scene_rewards", "stored_set", "通关奖励", int_value=True),

    define(0x9300, "free_pet_exchange", "integer", "每日免费精灵兑换次数", sync=True, save=True, cycle=True, timestamp=0x9302, default=3),
    define(0x9301, "pet_exchange_cd", "integer", "精灵兑换的开启CD", formula="fn.get_pet_exchange_cd()", sync=True, syncTimeout=True),

    define(0x9400, "lottery_campaign_cd",       "integer", "抽奖打折活动剩余时间", sync=True, syncTimeout=True, formula="fn.get_lottery_campaign_cd()"),
    define(0x9401, "lottery_campaign_discount", "integer", "抽奖打折活动折扣",     sync=True, formula="fn.get_lottery_campaign_discount()"),
    define(0x9402, "lottery_campaign_hot",      "string", "抽奖热点活动",         sync=True, formula="fn.get_lottery_campaign_hot()"),
    define(0x9403, "lottery_campaign_hot_cd",   "integer", "抽奖热点活动剩余时间", sync=True, syncTimeout=True, formula="fn.get_lottery_campaign_hot_cd()"),

    define(0x9500, "mat_exchange_campaign_cd",  "integer", "道具兑换活动剩余时间", sync=True, syncTimeout=True, formula="fn.get_mat_exchange_campaign_cd()"),
    define(0x9501, "mat_exchange_limits", "dict", "道具兑换活动次数限制", save=True, encoder=msgpack.dumps, decoder=msgpack.loads, cycle=True, timestamp=0x9502),
    define(0x9600, "last_check_mail_time", "float", "上次检查离线邮件的时间", save=True, default=0),

    define(0x9700, "city_dungeon_mg_cache",     "dict",       "黄金城推图怪物组缓存", encoder=msgpack.dumps, decoder=msgpack.loads, save=True),
    define(0x9702, "city_dungeon_start_time",   "integer",    "黄金城推图开启时间", sync=True, formula="fn.get_city_dungeon_start_time()", syncTimeout=True),
    define(0x9703, "city_dungeon_final_time",   "integer",    "黄金城推图结束时间", sync=True, formula="fn.get_city_dungeon_final_time()", syncTimeout=True),
    define(0x9704, "city_dungeon_last_reset",   "integer",    "黄金城推图上次重置时间", save=True, default=0),
    define(0x9705, "city_dungeon_rewards",      "dict",       "黄金城推图累计奖励", save=True, encoder=msgpack.dumps, decoder=msgpack.loads),
    define(0x9706, "city_dungeon_rewards_flag", "boolean",    "黄金城推图结算面板", sync=True, formula="bool(city_dungeon_rewards)"),

    define(0x9707, "city_rewards_recv",         "stored_set", "黄金城是否已经领取排名奖励"),
    define(0x9709, "city_dungeon_kill_count",   "integer",    "黄金城自己杀怪数", save=True, sync=True, default=0),
    define(0x9710, "city_treasure_recv_flag",   "boolean",    "黄金城宝藏是否领取", save=True, sync=True, cycle=True, timestamp=0x9711, default=False),

    define(0x9800, "city_contend_cache_target",          "dict",      "黄金城争夺对手缓存", encoder=msgpack.dumps, decoder=msgpack.loads, save=True),
    define(0x9801, "city_contend_rewards",               "dict",      "黄金城争夺累计奖励", encoder=msgpack.dumps, decoder=msgpack.loads, save=True),
    define(0x9802, "city_contend_rewards_flag",          "boolean",   "黄金城争夺结算面板", formula="bool(city_contend_rewards)", sync=True),
    define(0x9803, "city_contend_start_time",            "integer",   "黄金城争夺开启时间", sync=True, formula="fn.get_city_contend_start_time()", syncTimeout=True),
    define(0x9804, "city_contend_final_time",            "integer",   "黄金城争夺结束时间", sync=True, formula="fn.get_city_contend_final_time()", syncTimeout=True),
    define(0x9805, "city_contend_last_reset",            "integer",   "黄金城争夺上次重置时间", save=True, default=0),
    define(0x9807, "city_contend_treasure",              "integer",   "黄金城争夺押运宝藏数量", save=True, sync=True, default=0),
    define(0x9808, "city_contend_step",                  "integer",   "黄金城当前进度",   save=True, default=0, sync=True),
    define(0x9809, "city_contend_total_treasure",        "integer",   "黄金城累计宝藏数量", save=True, default=0, sync=True),
    define(0x9810, "city_contend_count",                 "integer",   "黄金城累计押/抢次数", save=True, sync=True, default=0),
    define(0x9811, "city_contend_events",                "sequence",  "黄金城争夺随机事件", save=True, decoder=json.decode, encoder=json.encode),
    define(0x9812, "city_contend_total_step",            "integer",   "黄金城总进度", save=True),
    define(0x9813, "city_contend_total_treasure_backup", "integer",   "黄金城累计宝藏数量备份", save=True, default=0),
    define(0x9814, "city_contend_count_backup",          "integer",   "黄金城累计押/抢次数备份", save=True, default=0),

    define(0x9900, "monthcard1", "integer", "月卡1", save=True, sync=True, default=0),
    define(0x9901, "monthcard2", "integer", "月卡2", save=True, sync=True, default=0),
    define(0x9902, "monthcard_recv1", "boolean", "月卡今日已领取1", save=True, sync=True, cycle=True, timestamp=0x9903, default=False),
    define(0x9904, "monthcard_recv2", "boolean", "月卡今日已领取2", save=True, sync=True, cycle=True, timestamp=0x9905, default=False),

    define(0x9910, "weekscard1", "integer", "周卡1", save=True, sync=True, default=0),
    define(0x9911, "weekscard2", "integer", "周卡1", save=True, sync=True, default=0),
    define(0x9912, "weekscard_recv1", "boolean", "周卡今日已领取1", save=True, sync=True, cycle=True, timestamp=0x9913, default=False),
    define(0x9914, "weekscard_recv2", "boolean", "周卡今日已领取2", save=True, sync=True, cycle=True, timestamp=0x9915, default=False),

    define(0x9916, "exchange_campaign_counter", "integer", "神将兑换的计数", save=True, default=0),
    define(0x9917, "exchange_campaign_last_time", "integer", "神将兑换计算的最后参与时间", save=True, default=0),
    define(0x9918, "exchange_campaign_remain_time", "integer", "神将兑换活动剩余时间", formula="fn.get_exchange_campaign_remain_time()", syncTimeout=True, sync=True),

    define(0x9919, "refresh_store_campaign_counter", "integer", "刷新商店活动计数", save=True, sync=True),
    define(0x9920, "refresh_store_campaign_last_time", "integer", "最后一次刷新的时间", save=True, default=0),
    define(0x9921, "refresh_store_campaign_remain_time", "integer", "刷新商店活动剩余时间", formula="fn.get_refresh_store_campaign_remain_time()", syncTimeout=True, sync=True),
    define(0x9922, "refresh_reward_done", "set", "可领取的刷新活动奖励", save=True, decoder=json.decode, encoder=json.encode),
    define(0x9923, "refresh_reward_end",  "set", "已领取的刷新活动奖励", save=True, decoder=json.decode, encoder=json.encode),
    define(0x9924, "refresh_reward_done_count", "integer", "可领取的刷新活动奖励个数", sync=True, formula="len(refresh_reward_done or [])"),

    define(0x9925, "arbor_day_campaign_remain_time", "integer", "植树节活动剩余时间", formula="fn.get_arbor_day_campaign_remain_time()", syncTimeout=True, sync=True),
    define(0x9926, "shake_tree_free_count", "integer", "免费摇树次数", sync=True, formula="fn.get_shake_tree_free_count()"),
    define(0x9928, "shake_tree_max_count", "integer", "每天摇树的最大次数限制", sync=True, formula="fn.get_shake_tree_max_count()"),
    define(0x9929, "shake_tree_used_count", "integer", "每天已经摇树的次数", save=True, sync=True, cycle=True, timestamp=0x9930, default=0),
    define(0x9932, "shake_tree_cost", "integer", "每次摇树的消耗", sync=True, formula="fn.get_shake_tree_cost()"),
    define(0x9933, "seed_state", "integer", "种子状态", save=True, sync=True, default=0),
    define(0x9934, "seed_id", "integer", "种子ID", save=True, sync=True, default=0),
    define(0x9935, "seed_campaign_remain_time", "integer", "种子活动剩余时间", formula="fn.get_seed_campaign_remain_time()", syncTimeout=True, sync=True),
    define(0x9936, "seed_state_last_change_time", "integer", "上一次状态转换的时间", save=True),
    define(0x9937, "seed_state_next_change_time", "integer", "下一个状态剩余的时间", save=True, syncTimeout=True, sync=True),
    define(0x9939, "seed_state_plant_time", "integer", "种植的时间", save=True),
    define(0x9940, "seed_state_ripening_time", "integer", "成熟的时间", save=True, syncTimeout=True, sync=True),
    define(0x9942, "watering_max_count", "integer", "每天浇水的最大次数", sync=True, formula="fn.get_watering_max_count()"),
    define(0x9943, "watering_used_count", "integer", "每天已经浇水的次数", save=True, sync=True, cycle=True, timestamp=0x9944, default=0),
    define(0x9945, "watering_time", "integer", "下一次可以浇水的时间", save=True, syncTimeout=True, sync=True),
    define(0x9947, "worming_max_count", "integer", "每天除虫的最大次数", sync=True, formula="fn.get_worming_max_count()"),
    define(0x9948, "worming_used_count", "integer", "每天已经除虫的次数", save=True, sync=True, cycle=True, timestamp=0x9949, default=0),
    define(0x9950, "worming_time", "integer", "下一次可以除虫的时间", save=True, syncTimeout=True, sync=True),
    define(0x9952, "clean_reward_index", "integer", "收割时候选择的奖励索引", save=True),
    define(0x9953, "seed_reward_index", "string", "种子收割奖励十选三选一的索引", save=True, sync=True),
    define(0x9954, "seal_seed_prob_id", "integer", "封印种子的随机索引", save=True, default=0),
    define(0x9955, "seal_seed_prob_campaign_last_time", "integer", "上一次封印种子随机索引设置的时间", save=True, default=0),
    define(0x9956, "seal_seed_reward_next_index", "integer", "封印种子下一个奖励的索引", save=True, default=0),
    define(0x9957, "shake_tree_prob_id", "integer", "遥一摇的随机索引", save=True, default=0),
    define(0x9958, "shake_tree_reward_free_next_index", "integer", "遥一摇免费下一个奖励的索引", save=True, default=0),
    define(0x9959, "shake_tree_prob_campaign_last_time", "integer", "上一次遥一摇随机索引设置的时间", save=True, default=0),
    define(0x9960, "shake_tree_reward_pay_next_index", "integer", "遥一摇付费下一个奖励的索引", save=True, default=0),

    define(0x9961, "handsel_campaign_counter", "integer", "赠送活动的计数", save=True, default=0),
    define(0x9962, "handsel_campaign_last_time", "integer", "上一次赠送的时间", save=True, default=0),
    define(0x9963, "handsel_campaign_remain_time", "integer", "赠送活动的剩余时间", formula="fn.get_handsel_campaign_remain_time()", syncTimeout=True, sync=True),
    define(0x9964, "campaign_honor_point", "string", "活动获得的荣誉", save=True, sync=True),
    define(0x9965, "flower_boss_campaign_remain_time", "integer", "鲜花BOSS活动的剩余时间", formula="fn.get_flower_boss_campaign_remain_time()", syncTimeout=True, sync=True),
    define(0x9966, "flower_boss_campaign_total_hurt", "integer", "鲜花BOSS活动的总伤害", save=True, sync=True, default=0),
    define(0x9967, "flower_boss_campaign_last_time", "integer", "上一次打鲜花BOSS的时间", save=True, default=0),
    define(0x9968, "honor_power",  "float", "荣誉战斗力", formula="fn.get_honor_power(entityID)"),

    define(0x9a00, "climb_tower_max_floor", "integer", "爬塔历史最高层", save=True, sync=True, default=0),
    define(0x9a01, "climb_tower_floor", "integer", "爬塔当前层", save=True, sync=True, default=0),
    define(0x9a02, "climb_tower_tip_floors", "set", "爬塔打赏层", save=True, decoder=json.decode, encoder=json.encode),
    define(0x9a03, "climb_tower_used_count", "integer", "爬塔重置已使用次数", save=True, sync=True, cycle=True, timestamp=0x9a04, default=0),
    define(0x9a05, "climb_tower_max_count", "integer", "爬塔重置最大次数", save=True, sync=True, formula='fn.get_climb_tower_max_count(vip)'),
    define(0x9a06, "climb_tower_chests", "set", "爬塔已领取宝箱", save=True, decoder=json.decode, encoder=json.encode),
    define(0x9a07, "climb_tower_history", "stored_sequence", "爬塔对战记录", decoder=json.decode, encoder=json.encode),
    define(0x9a08, "climb_tower_fight_history", "stored_dict", "爬塔对战记录"),
    define(0x9a09, "climb_tower_accredit_floor", "integer", "爬塔当前派驻层", save=True, sync=True, default=0),
    define(0x9a0b, "climb_tower_accredit_lineup", "string", "爬塔已派驻精灵", sync=True, formula='fn.get_climb_tower_accredit_raw_lineup(entityID, lineups, climb_tower_accredit_cd)'),
    define(0x9a0c, "climb_tower_accredit_protect_time", "integer", "精灵派驻保护时间", save=True, default=0),
    define(0x9a0d, "climb_tower_accredit_stash_time", "integer", "精灵派驻收益计算开始时间", save=True, default=0),
    define(0x9a0e, "climb_tower_accredit_cd", "integer", "精灵派驻 cd", save=True, syncTimeout=True, sync=True, default=0),
    define(0x9a0f, "climb_tower_accredit_stash_earnings", "integer", "精灵派驻暂存收益", save=True, default=0),
    define(0x9a10, "climb_tower_accredit_earnings", "integer", "精灵派驻当前层收益", formula='fn.get_climb_tower_accredit_earnings(climb_tower_accredit_stash_time, climb_tower_accredit_cd, climb_tower_accredit_floor)', cache=False),
    define(0x9a11, "climb_tower_accredit_acc_earnings", "integer", "精灵派驻累计收益", formula='climb_tower_accredit_stash_earnings + climb_tower_accredit_earnings', cache=False),
    define(0x9a12, "phantom", "integer", "幻影币", save=True, sync=True, default=0),
    define(0x9a13, "climb_tower_last_target", "integer", "敌方", save=True, default=0),
    define(0x9a14, "climb_tower_total_floor", "integer", "配置总层数", sync=True, formula='fn.get_climb_tower_total_floor()'),
    define(0x9a15, "climb_tower_verify_code", "string", "锁定对手", save=True),

    define(0x0b00, "gems", "stored_dict", "宝石", int_key=True, int_value=True),
    define(0x0b01, "dirty_gems", "set", "需要同步的宝石"),
    define(0x0b02, "gems_power", "float", "宝石战斗力", formula="fn.get_gems_power(entityID, point, lineups)"),

    define(0x0c10, "inlay1", "integer", "镶嵌等级1", save=True, sync=True, default=0),
    define(0x0c11, "inlay2", "integer", "镶嵌等级2", save=True, sync=True, default=0),
    define(0x0c12, "inlay3", "integer", "镶嵌等级3", save=True, sync=True, default=0),
    define(0x0c13, "inlay4", "integer", "镶嵌等级4", save=True, sync=True, default=0),
    define(0x0c14, "inlay5", "integer", "镶嵌等级5", save=True, sync=True, default=0),
    define(0x0c15, "inlay6", "integer", "镶嵌等级6", save=True, sync=True, default=0),
])

store_tag = 'p'
PlayerBase = create_class('PlayerBase', player_fields, store_tag)

if __name__ == '__main__':
    import os
    from yy.entity import gen_cython
    c = gen_cython(player_fields.values(), 'c_PlayerBase', 'from player.define import PlayerBase as PureEntity', store_tag, extra_imports)
    open(os.path.join(os.path.dirname(__file__), 'c_player.pyx'), 'w').write(c)
