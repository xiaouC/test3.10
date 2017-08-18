#coding:utf-8
from yy.entity import create_class, define

PlayerBase = create_class('Player', attributes=(
    #临时属性
    define(0x0001, "userID",   "integer", "用户ID"),
    define(0x0002, "username", "string",  "用户名"),
    define(0x0003, "IMEI",     "string",  "IMEI"),
    #持久化属性, 同步属性
    define(0x0004, "entityID", "integer", "唯一实体ID", isPers=True, isSync=True),
    define(0x0005, "name",     "string",  "名称",       isPers=True, isSync=True, isBase=True),
    define(0x0006, "level",    "integer", "等级",       isPers=True, isSync=True, isBase=True),
    #恢复属性， 每**时间恢复1点，timestamp 用于指定存储时间戳的属性， 如果不指定， 会自动生成一个, max用于指定恢复的最大值
    define(0x0007, "sp",       "integer", "体力",       isPers=True, isSync=True, isCycle=True, resume=5*60, timestamp='resume_sp_cd', max='spmax'),
    define(0x0008, "money",    "integer", "金钱",       isPers=True, isSync=True),
    define(0x0009, "gold",     "integer", "金币",       isPers=True, isSync=True),
    define(0x000a, "vs",       "integer", "PVP入场券",  isPers=True, isSync=True),
    define(0x000b, "gp",       "integer", "抽怪货币",   isPers=True, isSync=True),
    define(0x000c, "bp",       "integer", "工会货币",   isPers=True, isSync=True),
    define(0x000d, "slate",    "integer", "成就点数",   isPers=True, isSync=True),
    define(0x000e, "power",    "integer", "统领力",     isPers=True, isSync=True, default=20),
    define(0x000f, "modelID",  "integer", "模型ID",     isPers=True, isBase=True),
    define(0x0010, "sex",      "integer", "性别",       isPers=True, isSync=True, isBase=True),
    define(0x0011, "career",   "integer", "职业",       isPers=True, isSync=True, isBase=True),

    define(0x0012, "lastlogin",   "datetime", "最后一次登录时间",  isPers=True, isBase=True),
    define(0x0013, "totallogin",  "integer",  "累计登录次数",  isPers=True),
    define(0x0014, "seriallogin", "integer",  "连续登录次数",  isPers=True),
    define(0x0015, "createtime",  "datetime", "角色创建时间",  isPers=True, isBase=True),

    define(0x0020, "pets",   "object",  "玩家的所有怪物", default=dict),

    define(0x0023, "spmax",  "integer", "最大体力",     isPers=True, isSync=True), 
    define(0x0024, "petmax", "integer", "最大怪物数量", isPers=True, isSync=True), 
    define(0x0025, "lineups", "object", "阵形",         isPers=True, decoder=decode_pickle, encoder=encode_pickle, default=list),
    define(0x0026, "on_lineup", "integer", "激活的阵形", isPers=True, isSync=True, default=0),

    define(0x0027, "fbscores",  "object",  "副本进度",       default=dict),
    define(0x0028, "currentfbID", "integer", "当前所在副本ID", isPers=True, default=0),
    define(0x0029, "fbreward",  "object",  "副本奖励",       isPers=True, decoder=decode_pickle, encoder=encode_pickle, default=dict),

    define(0x0030, "exp", "integer", "经验", isSync=True, isPers=True, default=0),

    #公式属性
    define(0x0031, "expmax", "integer", "人物升级需要经验", isSync=True, isForm=True, form="formulas.get_max_exp(level)"),
    define(0x0032, "expnxt", "integer", "下一级升级需要经验", isSync=True, isForm=True, form="formulas.get_next_exp(level)"),

    define(0x0033, "resume_sp_cd", "integer", "下一次恢复体力剩余时间", isPers=True, isSync=True, syncTimeout=True),

    define(0x0034, "spprop", "integer", "体力道具数量", isPers=True, isSync=True),

    define(0x0035, "dbtag",  "string",  "数据库ID"),        
    #复杂结构
    define(0x0036, "book",   "object",  "怪物图鉴", isPers=True, decoder=decode_json_set, encoder=encode_json_set, default=set),
))


class Player(PlayerBase):#继承创建出来的class
    #实现所需要的on方法
    @classmethod
    def on_async_load(cls, *args, **kwargs):
        '''异步加载'''
        raise NotImplementedError

    @classmethod
    def on_load(cls, *args, **kwargs):
        '''加载'''
        raise NotImplementedError

    @classmethod
    def on_async_create(cls, *args, **kwargs):
        '''异步创建'''
        raise NotImplementedError

    @classmethod
    def on_create(cls, *args, **kwargs):
        '''创建'''
        raise NotImplementedError

    def on_sync(self, all=False):
        '''属性同步（组织消息）'''
        #返回sendto，rsp给do_sync
        raise NotImplementedError

    def do_sync(self, sendto, rsp):
        '''属性同步（发送消息）'''
        raise NotImplementedError

    def on_delete(self):
        '''删除'''
        raise NotImplementedError

    def on_save(self):
        '''保存'''
        raise NotImplementedError
