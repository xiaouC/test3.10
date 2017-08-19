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
from scene.constants import FbType
from mat.constants import MatType
from reward.constants import RewardItemType


def default_decoder_by(seq):
    def default_decoder(self, v, lineno=None):
        if v in (0, '0', ''):
            return []
        try:
            ret = map(int, v.split(seq))
        except ValueError as e:
            raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (
                lineno, self.column_name, self.name, str(e), repr(v)))
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
        raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (
            lineno, self.column_name, self.name, str(e), repr(v)))
    return ret


def decode_json(self, v, lineno=None):
    if v in (0, '0', ''):
        return []
    try:
        v = v.replace("'", '"')
        ret = ujson.loads(v)
    except ValueError as e:
        raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (
            lineno, self.column_name, self.name, str(e), repr(v)))
    return ret


def docode_timetime(self, v, lineno=None):
    try:
        hour, minute = map(int, v.split(":", 1))
        # 配置需要导成JSON，不支持timetime类，所以还是返回字符串
        timetime(hour, minute)
    except ValueError as e:
        raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (
            lineno, self.column_name, self.name, str(e), repr(v)))
    return v


CURDIR = os.path.dirname(__file__)
forbid_names_trie = trie.trie_empty()
dirty_words_trie = trie.trie_empty()


def reload_dirty_words():
    lines = open(os.path.join(CURDIR, '../data/dirty_words.txt')).readlines()
    dirty_words_list = [line.strip().decode('utf-8')
                        for line in lines if line.strip()]
    trie.trie_clear(dirty_words_trie)
    trie.trie_append(dirty_words_trie, dirty_words_list)

    lines = open(os.path.join(CURDIR, '../data/forbid_names.txt')).readlines()
    forbid_name_list = [line.strip().decode('utf-8')
                        for line in lines if line.strip()]
    trie.trie_clear(forbid_names_trie)
    trie.trie_append(forbid_names_trie, forbid_name_list + dirty_words_list)

reload_dirty_words()


@register_config
class LevelupConfig(Config):

    """等级经验"""
    level = IntegerField(u"lv", key=True)
    exp = IntegerField(u"exp")
    add_power = IntegerField(u'power')
    add_spmax = IntegerField(u'sp')
    mine1 = IntegerField("get_money1")
    mine2 = IntegerField("get_exp1")
    add_sp = IntegerField(u"addsp")
    friends_num = IntegerField(u"friends_num")
    gift_num = IntegerField(u"gift_num")
    getgift_num = IntegerField(u"getgift_num")

    union = IntegerField(u"union")
    pvp = IntegerField(u"pvp")
    hard_fb = IntegerField(u"hard_fb")
    equip = IntegerField(u"equip")  # 装备佩戴
    levelup = IntegerField(u"levelup")  # 精灵升级
    evo = IntegerField(u"evo")
    star = IntegerField(u"star")
    ticket = IntegerField(u"ticket")
    uproar = IntegerField(u"ticket_ex")
    rob = IntegerField(u"rob")
    get_money1 = IntegerField(u"get_money1")
    get_exp1 = IntegerField(u"get_exp1")
    refine = IntegerField(u"refine")
    refine_fabao = IntegerField(u"refine_fabao")
    chatroom = IntegerField(u"chatroom")
    mission = IntegerField(u"mission")
    refine_equip = IntegerField(u"refine_equip")
    golden_finger = IntegerField("golden_finger")
    hotunits = IntegerField("hotunits")
    sliverstore = IntegerField("sliverstore")
    goldenstore = IntegerField("goldenstore")
    triggerPacks1 = IntegerField("one_gift")
    triggerPacks2 = IntegerField("several_gift")
    visit = IntegerField("visit")
    friendfb = IntegerField("relicfb")
    friend = IntegerField(u"friends")
    count_down = IntegerField(u"limit_time_gift")
    online_packs = IntegerField(u"online_package")

    class __Meta__:
        table = "Lvup"


@register_config
class AttributeFormulaConfig(Config):

    """属性计算公式"""
    ID = IntegerField(u"ID", key=True)
    value = StringField(u"value")

    class __Meta__:
        table = "AttributeFormula"


@register_config
class NameprefixEConfig(Config):
    ID = IntegerField(u"ID", key=True)
    name = StringField(u"nameprefixE")

    class __Meta__:
        table = "nameprefixE"


@register_config
class NameprefixFConfig(Config):
    ID = IntegerField(u"ID", key=True)
    name = StringField(u"nameprefixF")

    class __Meta__:
        table = "nameprefixF"


@register_config
class MalenameConfig(Config):
    ID = IntegerField(u"ID", key=True)
    name = StringField(u"malename")

    class __Meta__:
        table = "malefirstname"


@register_config
class FemalenameConfig(Config):
    ID = IntegerField(u"ID", key=True)
    name = StringField(u"femalename")

    class __Meta__:
        table = "femalefirstname"


@register_config
class CreatePlayerConfig(Config):
    # 初始属性
    sex = IntegerField(u'sex')
    career = IntegerField(u'career')
    money = IntegerField(u'money')
    gold = IntegerField(u'gold')
    level = IntegerField(u'level')
    petIDs = CustomField(u'petID', decoder=default_decoder_vertical_line)
    sp = IntegerField(u'sp')
    petmax = IntegerField(u'petmax')
    drop = IntegerField(u'drop')
    prototypeID = IntegerField(u'face')
    borderID = IntegerField(u'frame')
    accumulating = IntegerField("integral")  # 单抽积分

    class __Meta__:
        table = 'CreatePlayer'
        unique_together = ('sex', 'career')


@register_config
class PetConfig(Config):
    prototypeID = IntegerField(u'id', key=True)
    name = StringField(u'name')
    attr = IntegerField(u'attr')     # 元素
    mtype = IntegerField(u'mtype')    # mtype
    ability = IntegerField(u'ability')
    mvRgeTL = IntegerField(u'mvRgeTL')  # 左上
    mvRgeT = IntegerField(u'mvRgeT')   # 上
    mvRgeTR = IntegerField(u'mvRgeTR')  # 右上
    mvRgeL = IntegerField(u'mvRgeL')   # 左
    mvRgeR = IntegerField(u'mvRgeR')   # 右
    mvRgeBL = IntegerField(u'mvRgeBL')  # 左下
    mvRgeB = IntegerField(u'mvRgeB')   # 下
    mvRgeBR = IntegerField(u'mvRgeBR')  # 右下
    hpMin = IntegerField(u'hpMin')    # 最小HP
    hpMax = IntegerField(u'hpMax')    # 最大HP
    atkMin = IntegerField(u'atkMin')   # 最小攻击
    atkMax = IntegerField(u'atkMax')   # 最大攻击
    defMin = IntegerField(u'defMin')   # 最小防御
    defMax = IntegerField(u'defMax')   # 最大防御
    critMin = IntegerField(u"critmin")  # 最小暴击
    dodgeMin = IntegerField(u"dodgemin")  # 最小闪躲
    rarity = IntegerField(u'rarity')   # 星级 颜色
    cexp = FloatField(u'cexp')     # 经验系数
    gtype = IntegerField(u'gtype')    # gtype
    mexp = IntegerField(u'mexp')     # 单体1级兑换经验
    seq = IntegerField(u'seq')      # 序号
    gupm = IntegerField(u'gupm')     # 进化要求怪兽
    gupr = IntegerField(u'gupr')     # 进化结果
    # guptype1    = IntegerField(u'guptype1') # 材料类型1
    # gup1        = IntegerField(u'gup1')     # 进化素材1
    # gupnum1     = IntegerField(u'gupnum1')  # 进化素材数量1
    # guptype2    = IntegerField(u'guptype2') # 材料类型2
    # gup2        = IntegerField(u'gup2')     # 进化素材2
    # gupnum2     = IntegerField(u'gupnum2')  # 进化素材数量2
    # guptype3    = IntegerField(u'guptype3') # 材料类型3
    # gup3        = IntegerField(u'gup3')     # 进化素材3
    # gupnum3     = IntegerField(u'gupnum3')  # 进化素材数量3
    # guptype4    = IntegerField(u'guptype4') # 材料类型4
    # gup4        = IntegerField(u'gup4')     # 进化素材4
    # gupnum4     = IntegerField(u'gupnum4')  # 进化素材数量4
    gups = IntegerField(u'gup', repeated=True, range=1)
    guptypes = IntegerField(u'guptype', repeated=True, range=1)
    gupnums = IntegerField(u'gupnum', repeated=True, range=1)
    coinUp = IntegerField(u'coinUp')   # 每级掉落金币
    expUp = IntegerField(u'expUp')    # 每级掉落经验
    droppack = IntegerField(u'droppack')  # 掉落
    drop1 = IntegerField(u'drop1')    # 石像可能掉落1
    num1 = IntegerField(u'num1')     # 石像掉落权重1
    drop2 = IntegerField(u'drop2')    # 石像可能掉落2
    num2 = IntegerField(u'num2')     # 石像掉落权重2
    drop3 = IntegerField(u'drop3')    # 石像可能掉落3
    num3 = IntegerField(u'num3')     # 石像掉落权重3
    dtype = IntegerField(u'dtype')    # 掉落类型
    piece = IntegerField(u'piece')
    step = IntegerField(u'step')
    init_lv = CustomField(u'levelscope', decoder=default_decoder_vertical_line)
    same = IntegerField(u'same')
    need_patch = IntegerField(u'piece_amount')
    drop_piece = IntegerField(u'drop_piece')
    breaklv = IntegerField(u'breakLv')
    cid = IntegerField(u'cid')
    camount = IntegerField(u'camount')
    mhp = IntegerField(u"mhp")
    matk = IntegerField(u"matk")
    mdef = IntegerField(u"mdef")
    mcrit = IntegerField(u"mcrit")
    mdodge = IntegerField(u"mdodge")
    sellk = IntegerField(u"sellk")
    cls = IntegerField(u'class')
    equips = CustomField(u"equip", decoder=default_decoder_vertical_line)
    excl_equip = IntegerField(u"excl_equip")
    herostep = IntegerField(u"herostep")
    skill_base1 = IntegerField(u"skill_base1")
    skill_base2 = IntegerField(u"skill_base2")
    skill_base3 = IntegerField(u"skill_base3")
    skill_base4 = IntegerField(u"skill_base4")
    skill_base5 = IntegerField(u"skill_base5")
    skill_incr1 = IntegerField(u"skill_lvup1")
    skill_incr2 = IntegerField(u"skill_lvup2")
    skill_incr3 = IntegerField(u"skill_lvup3")
    skill_incr4 = IntegerField(u"skill_lvup4")
    skill_incr5 = IntegerField(u"skill_lvup5")
    hp_break = CustomField(u'hp_break', decoder=default_decoder_vertical_line)
    atk_break = CustomField(
        u'atk_break', decoder=default_decoder_vertical_line)
    def_break = CustomField(
        u'def_break', decoder=default_decoder_vertical_line)

    @classmethod
    def post_validation(cls, alldata):
        configs = alldata[cls.__name__]
        droppacks = alldata[DroppackConfig.__name__]
        error = u"{} 中 {} 为 {}， 不存在于 {} 中。"
        for id, config in configs.items():
            if config["droppack"] and config["droppack"] not in droppacks:
                col = cls.fields["droppack"]
                error = error.format(
                    cls.__Meta__.table,
                    col.column_name,
                    config["droppack"],
                    MatConfig.__Meta__.table)
                raise ValidationError(error)

    class __Meta__:
        table = 'units'


@register_config
class PetBySameConfig(Config):
    prototypeID = IntegerField('id')
    same = IntegerField('same', groupkey=True)

    class __Meta__:
        table = 'units'


@register_config
class SceneInfoConfig(Config):
    ID = IntegerField(u'id', key=True)
    name = StringField(u'name')  # 地宫名
    prev = IntegerField(u'prev')  # 上一地宫ID
    post = IntegerField(u'post')  # 下一地宫ID
    fbs = CustomField(u'fbgroub', decoder=default_decoder_vertical_line)
    drop = IntegerField(u'dropid')
    openlv = IntegerField(u"openlv")  # 等级限制
    type = IntegerField(u"type")
    subtype = IntegerField(u"subtype", required=False)  # 活动本中判断是通天还是福地, DLC里代表BOSS关卡

    class __Meta__:
        table = 'SceneInfo'


@register_config
class FbInfoConfig(Config):
    ID = IntegerField(u'id', key=True)
    name = StringField(u'name')          # 关卡名称
    sceneID = IntegerField(u'sceneID')      # 地宫ID
    prev = CustomField(
        u'prev',
        decoder=default_decoder_vertical_line)         # 上一关卡
    post = CustomField(
        u'post',
        decoder=default_decoder_vertical_line)         # 下一关卡
    type = IntegerField(u'type')  # 类型
    sp = IntegerField(u'sp')           # 消耗能量
    max = IntegerField(u'max')          # 可挑战次数
    group1 = IntegerField(u'group1')       # 怪物组1
    group2 = IntegerField(u'group2')       # 怪物组2
    group3 = IntegerField(u'group3')       # 怪物组3
    group4 = IntegerField(u'group4')       # 怪物组4
    group5 = IntegerField(u'group5')       # 怪物组5
    # droppackID  = IntegerField(u'droppackID') # 掉落包ID
    itemfirst_id = IntegerField(u'itemfirst_id')  # 首次掉落包ID
    itemdrops_id = IntegerField(u'itemdrops_id')  # 掉落包ID
    exp_reward = IntegerField(u'first_reward1')  # 经验奖励
    monster_drop = IntegerField(u'dropmonster')  # 怪物掉落
    goldenstore = IntegerField(u'goldenstore')  # 是否开启临时金角商店
    silverstore = IntegerField(u'silverstore')  # 是否开启临时银角商店
    buffid = IntegerField(u'buffid')
    buffpose = IntegerField(u'buffpose')
    boss_drop = IntegerField(u"bossdrops_id")  # boss掉落
    openlv = IntegerField(u"openlv")  # 等级限制
    gold_reward = IntegerField(u"gold_reward")

    class __Meta__:
        table = 'FbInfo'


@register_config
class ExSceneInfoConfig(Config):
    sceneID = IntegerField('id', key=True)
    desc = StringField('desc')
    cycle = IntegerField('cycletype')
    opendays = StringField('openday')
    days = JSONField('openday')
    max = IntegerField('fight_time')
    mark = StringField('mark')

    class __Meta__:
        table = 'ExSceneInfo'


@register_config
class FbInfoByTypeConfig(Config):
    type = IntegerField(u'type', groupkey=True)  # 类型
    ID = IntegerField(u'id')

    class __Meta__:
        table = 'FbInfo'


@register_config
class FbInfoBySceneConfig(Config):
    scene = IntegerField(u'sceneID', groupkey=True)  # 类型
    ID = IntegerField(u'id')

    class __Meta__:
        table = 'FbInfo'


@register_config
class GroupConfig(Config):
    ID = IntegerField(u'id', key=True)
    monster_id1 = IntegerField(u'monster_id1')    # 怪物ID1
    monster_level1 = IntegerField(u'monster_level1')  # 怪物等级1
    monster_id2 = IntegerField(u'monster_id2')    # 怪物ID2
    monster_level2 = IntegerField(u'monster_level2')  # 怪物等级2
    monster_id3 = IntegerField(u'monster_id3')    # 怪物ID3
    monster_level3 = IntegerField(u'monster_level3')  # 怪物等级3
    monster_id4 = IntegerField(u'monster_id4')    # 怪物ID4
    monster_level4 = IntegerField(u'monster_level4')  # 怪物等级4

    class __Meta__:
        table = 'monstergroup'


@register_config
class DroppackConfig(Config):
    # dropID     = IntegerField(u'dropID', key=True)
    packID = IntegerField(u'packID', groupkey=True)  # 掉落包ID
    randomtype = IntegerField(u'randomtype')            # 随机类型
    type = IntegerField(u'type', choices=RewardItemType)  # 奖励类型
    itemID = IntegerField(u'itemID')                # 物品ID
    amount = IntegerField(u'amount')                # 数量
    dropProb = IntegerField(u'dropProb')              # 概率

    @classmethod
    def ref_check(cls, line, colname, alldata, refcls):
        if line[colname] not in alldata[refcls.__name__]:
            col = cls.fields[colname]
            msg = u"{} 中 packID 为 {} 的记录，字段 {} 引用了一个不存在于 {} 的值 {}。".format(
                cls.__Meta__.table, line["packID"],
                "%s(%s)" % (col.column_name, col.name),
                refcls.__Meta__.table, line[colname])
            raise ValidationError(msg)

    @classmethod
    def post_validation(cls, alldata):
        for k, packs in alldata[cls.__name__].items():
            for pack in packs:
                if pack["type"] == RewardItemType.Droppack:
                    cls.ref_check(pack, "itemID", alldata, cls)
                elif pack["type"] == RewardItemType.Pet:
                    cls.ref_check(pack, "itemID", alldata, PetConfig)
                elif pack["type"] == RewardItemType.Mat:
                    cls.ref_check(pack, "itemID", alldata, MatConfig)
                elif pack["type"] == RewardItemType.Equip:
                    cls.ref_check(pack, "itemID", alldata, NewEquipConfig)
                elif pack["type"] == RewardItemType.Specpack:
                    cls.ref_check(pack, "itemID", alldata, SpecpackConfig)

    class __Meta__:
        table = 'Droppack'


class DroppackRawConfig(Config):
    packID = IntegerField(u'packID')  # 掉落包ID
    packs = CustomField(u'掉落', decoder=lambda s: s)

# @register_config
# class LotteryConfig(Config):
#    '''used cost only'''
# type = IntegerField(u'type', key=True) #类型
# cost = IntegerField(u'cost') #消耗
# droppackID = IntegerField(u'droppackID') #掉落包ID
#    class __Meta__:
#        table = 'Lottery'


@register_config
class PayDrawConfig(Config):
    type = IntegerField(u'type', groupkey=True)
    ID = IntegerField(u'id')
    WT = IntegerField(u'weight')

    class __Meta__:
        table = 'paydraw'


@register_config
class LotteryNoticeConfig(Config):
    ID = IntegerField(u'ID', key=True)
    notice = StringField(u'notice')  # 公告

    class __Meta__:
        table = 'LotteryNotice'


@register_config
class RandomMonsterConfig(Config):
    ID = IntegerField(u'id', key=True)
    monsters = IntegerField(
        u'monster_id',
        required=True,
        repeated=True,
        range=1,
        skipzero=True)
    weights = IntegerField(
        u'pose',
        required=True,
        repeated=True,
        range=1,
        skipzero=True)

    class __Meta__:
        table = 'roundmoster'


@register_config
class ExploreRewardConfig(Config):
    adventureTime = IntegerField(u'adventureTime')  # 探索时长类型 1 2 3 4 5
    rarity = IntegerField(u'rarity')  # 星级
    second = IntegerField(u'second')  # 探索时长对应的秒数
    expGet = IntegerField(u'expGet')  # 奖励宠物经验
    packID = IntegerField(u'packID')  # 掉落包id

    class __Meta__:
        table = 'adventure'
        unique_together = ('adventureTime', 'rarity')


@register_config
class LoginRewardConfig(Config):
    dropID = IntegerField(u'dropID', key=True)  # dropid
    loginday = IntegerField(u'loginday')  # 累计登陆天数
    type = IntegerField(u'type')  # 奖励类型
    itemID = IntegerField(u'itemID')  # 物品ID
    amount = IntegerField(u'amount')  # 数量

    class __Meta__:
        table = 'loginreward'


@register_config
class SerialLoginReward(Config):
    dropID = IntegerField(u'dropID', key=True)  # dropid
    loginday = IntegerField(u'loginday')  # 连续登陆天数
    type = IntegerField(u'type')  # 奖励类型
    itemID = IntegerField(u'itemID')  # 物品ID
    amount = IntegerField(u'amount')  # 数量

    class __Meta__:
        table = 'continuereward'


@register_config
class NoticeConfig(Config):
    id = IntegerField(u'id', key=True)  # dropid
    title = StringField(u'title')  # 公告标题
    content = StringField(u'content')  # 公告内容

    class __Meta__:
        table = 'Tips'


@register_config
class SlateRewardConfig(Config):
    id = IntegerField(u'id', key=True)  # id
    name = StringField(u'name')  # 名称
    number = IntegerField(u'number')  # 石板数量
    type = IntegerField(u'type')  # 奖品类型
    itemID = IntegerField(u'itemID')  # 物品id
    amount = IntegerField(u'amount')  # 数量

    class __Meta__:
        table = 'Achievement'


@register_config
class LeaderSkills(Config):
    ID = IntegerField(u'id', key=True)
    name = StringField(u'name')
    type = IntegerField(u'sType')
    k = IntegerField(u'val11')
    attr = StringField(u'shuxing', required=False)

    class __Meta__:
        table = 'leaderSkills'


@register_config
class GiveGoldConfig(Config):
    ID = IntegerField(u'id')
    title = StringField(u"title")
    desc = StringField(u"desc")
    start = DatetimeField(u"start")
    end = DatetimeField(u"end")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = 'GiveGold'

# {{{ 新抽英雄


@register_config
class LotteryFunctionConfig(Config):

    """抽英雄 CD 及免费次数配置"""
    ID = IntegerField('ID', key=True)
    Price = IntegerField('Price')  # 价格
    ColdDown = IntegerField('ColdDown')  # 冷却时间
    FreeTimes = IntegerField('FreeTimes')  # 免费次数
    title = IntegerField('title')  # 标题资源
    description = IntegerField('discription')  # 描述资源
    rangeset = JSONField('range')  # 属性限制范围
    level = IntegerField('lv')  # 达到等级可抽

    class __Meta__:
        table = 'LotteryFunction'
        reloadable = True


@register_config
class RechargeScoreSeatConfig(Config):

    """抽英雄开启个数配置"""
    ID = IntegerField(u'ID')
    goldcount = IntegerField('goldcount', key=True)  # 累计充值积分
    count = IntegerField('count')  # 开启个数

    class __Meta__:
        table = 'RechargeScoreSeat'


@register_config
class CreateScoreAttributeConfig(Config):

    """抽英雄属性及积分配置"""
    Attribute = IntegerField('Attribute', key=True)  # 属性
    FirstFreeA = IntegerField('FirstFreeA')  # 免费首刷A
    NormalFreeA = IntegerField('NormalFreeA')  # 免费A
    FirstGoldA = IntegerField('FirstGoldA')  # 钻石首刷A
    NormalGoldA = IntegerField('NormalGoldA')  # 钻石A
    LimitedGoldA = IntegerField('LimitedGoldA')  # 非首金限制A
    FirstFreeB = IntegerField('FirstFreeB')  # 免费首刷B
    NormalFreeB = IntegerField('NormalFreeB')  # 免费B
    FirstGoldB = IntegerField('FirstGoldB')  # 钻石首刷B
    NormalGoldB = IntegerField('NormalGoldB')  # 钻石B
    LimitedGoldB = IntegerField('LimitedGoldB')  # 非首金限制B
    FirstFreeC = IntegerField('FirstFreeC')  # 免费首刷C
    NormalFreeC = IntegerField('NormalFreeC')  # 免费C
    FirstGoldC = IntegerField('FirstGoldC')  # 钻石首刷C
    NormalGoldC = IntegerField('NormalGoldC')  # 钻石C
    LimitedGoldC = IntegerField('LimitedGoldC')  # 非首金限制C
    FirstFreeD = IntegerField('FirstFreeD')  # 免费首刷D
    NormalFreeD = IntegerField('NormalFreeD')  # 免费D
    FirstGoldD = IntegerField('FirstGoldD')  # 钻石首刷D
    NormalGoldD = IntegerField('NormalGoldD')  # 钻石D
    LimitedGoldD = IntegerField('LimitedGoldD')  # 非首金限制D

    class __Meta__:
        table = 'CreateScoreAttribute'


@register_config
class AttributeDroppackConfig(Config):

    """抽英雄掉落包配置"""
    Attribute = IntegerField('Attribute', key=True)  # 属性
    RewardDroppack = IntegerField('RewardDroppack', default=0)  # 掉落包ID
    Accumulating = IntegerField("integral")
    AccumDroppack = IntegerField("IntegDroppack", default=0)
    arg = StringField("reward")
    tips1 = StringField("this_summon")
    tips2 = StringField("again_summon")

    class __Meta__:
        table = 'AttributeDroppack'
# }}}


#  @register_config
#  class SkillConfig(Config):
#      ID = IntegerField('id', key=True)
#      maxLevel = IntegerField('rqPoint')
#
#      class __Meta__:
#          table = 'skills'


@register_config
class PvpActivityConfig(Config):
    ID = IntegerField('id', key=True)
    start = DatetimeField('starttime')
    end = DatetimeField('lasttime')
    group = IntegerField('group')

    class __Meta__:
        table = 'daytime'


@register_config
class PvpFightRewardConfig(Config):
    id = IntegerField(u'id')
    result = IntegerField(u'result', key=True)  # 1为战胜奖励 0为战败奖励
    type1 = IntegerField(u'type1')
    itemID1 = IntegerField(u'itemID1')
    amount1 = IntegerField(u'amount1')
    type2 = IntegerField(u'type2')
    itemID2 = IntegerField(u'itemID2')
    amount2 = IntegerField(u'amount2')

    class __Meta__:
        table = 'result'


@register_config
class PvpGroupConfig(Config):
    ID = CustomField(u'id', key=True, decoder=lambda s, v, _: -int(v))
    name = StringField(u'play_name')
    level = IntegerField(u'play_lv')
    monster_id1 = IntegerField('monster_id1')
    monsters = IntegerField(
        'monster_id',
        required=True,
        repeated=True,
        range=range(1, 5))
    levels = IntegerField(
        'monster_level',
        required=True,
        repeated=True,
        range=range(1, 5))
    stars = IntegerField(
        'monster_star',
        required=True,
        repeated=True,
        range=range(1, 5))
    equips = IntegerField(
        'monster_equip',
        required=True,
        repeated=True,
        range=range(1, 5))
    skills = CustomField(
        'monster_skill_level',
        required=True,
        repeated=True,
        range=range(1, 5), decoder=default_decoder_vertical_line)
    group = IntegerField(u"group")
    career = IntegerField(u'career')
    rob_money = IntegerField(u"rob_money")
    rob_soul = IntegerField(u"rob_exp")
    score = IntegerField(u"score")
    power = IntegerField("efficiency")
    visible = IntegerField("is_visible")

    class __Meta__:
        table = 'pvpgroup'


@register_config
class PvpGroupByPowerConfig(Config):
    power = IntegerField("efficiency", groupkey=True)
    ID = CustomField('id', decoder=lambda s, v, _: -int(v))

    class __Meta__:
        table = 'pvpgroup'


@register_config
class PvpGroupByGroupConfig(Config):
    group = IntegerField("group", groupkey=True)
    ID = CustomField('id', decoder=lambda s, v, _: -int(v))

    class __Meta__:
        table = 'pvpgroup'


@register_config
class PvpGroupByLevelConfig(Config):
    level = IntegerField(u"play_lv", groupkey=True)
    ID = CustomField(u'id', decoder=lambda s, v, _: -int(v))

    class __Meta__:
        table = 'pvpgroup'


@register_config
class PvpGroupEquipsConfig(Config):

    def decode_equip(self, v, lineno=None):
        if v in (0, '0', ''):
            return []
        try:
            ret = map(int, v.split('|'))
        except ValueError as e:
            raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (
                lineno, self.column_name, self.name, str(e), repr(v)))
        return ret

    ID = IntegerField(u"id", key=True)
    equips = CustomField(
        'equip', repeated=True, range=range(1, 7),
        decoder=decode_equip, skipzero=True)

    class __Meta__:
        table = "robotequip"


@register_config
class PvpRewardConfig(Config):
    ID = IntegerField('id', key=True)
    group = IntegerField('group')
    ranking = IntegerField("ranking")
    title = StringField('title')
    content = StringField('comment')
    condition = CustomField('condition', decoder=default_decoder_vertical_line)
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    grad_png = StringField('grad_png')

    class __Meta__:
        table = 'PvpReward'


@register_config
class PvpRewardByGroupConfig(Config):
    ID = IntegerField('id')
    group = IntegerField('group', groupkey=True)

    class __Meta__:
        table = 'PvpReward'


@register_config
class SkillupConfig(Config):
    count = IntegerField('id', key=True)
    probs = IntegerField('pose', repeated=True, range=1)

    class __Meta__:
        table = 'skillup'


@register_config
class EvolutionConfig(Config):
    id = IntegerField(u'id', key=True)
    coin = IntegerField(u'silver')

    class __Meta__:
        table = 'evolution'


@register_config
class RusherConfig(Config):

    def decode_rusher(self, v, lineno=None):
        if v in (0, '0', ''):
            return []
        try:
            ret = dict(
                zip(('prototypeID', 'camp', 'index'), map(int, v.split('|'))))
        except ValueError as e:
            raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (
                lineno, self.column_name, self.name, str(e), repr(v)))
        return ret
    fbID = IntegerField(u'fbid', groupkey=True)  # 类型
    layer = IntegerField(u'area')
    rusher = CustomField(
        'monsterid|unit|location',
        repeated=True,
        range=1,
        decoder=decode_rusher,
        skipzero=True)

    class __Meta__:
        table = 'reinforce'


@register_config
class FactionLimitConfig(Config):
    level = IntegerField(u'lv', key=True)
    limit = IntegerField(u'num')
    exp = IntegerField(u'exp')

    class __Meta__:
        table = 'unions'


@register_config
class FactionStrengthenConfig(Config):
    level = IntegerField(u'lv', key=True)
    cost = IntegerField(u'cost')
    learn_cost = IntegerField(u'study')
    HP = FloatField(u"uhp")
    ATK = FloatField(u"uatk")
    CRI = FloatField(u"ubj")
    DEF = FloatField(u"udef")

    class __Meta__:
        table = 'strengthen'


#  @register_config
#  class FactionRewardConfig(Config):
#      ID = IntegerField('id', key=True)
#      title = StringField('comment')
#      condition = CustomField('condition', decoder=default_decoder_vertical_line)
#      rewards = CustomField(
#          'type|itemID|amount',
#          repeated=True,
#          range=1,
#          decoder=decode_rewards,
#          skipzero=True)
#
#      class __Meta__:
#          table = 'rewards'

@register_config
class FactionLevelRewardConfig(Config):
    level = IntegerField("unionsLevel", key=True)
    types = IntegerField("type", repeated=True, range=1, skipzero=True)
    itemIDs = IntegerField("itemID", repeated=True, range=1, skipzero=True)
    amounts = IntegerField("amount", repeated=True, range=1, skipzero=True)

    class __Meta__:
        table = 'unionsrewards'


@register_config
class CanStrengthenConfig(Config):
    ID = IntegerField('id', key=True)
    can = BooleanField('switch')

    class __Meta__:
        table = 'strengthentime'


@register_config
class BuySpCostConfig(Config):
    count = IntegerField('time', key=True)
    cost = IntegerField('coin')

    class __Meta__:
        table = 'physical'


@register_config
class BuyFbCostConfig(Config):
    count = IntegerField('time', key=True)
    cost = IntegerField('coin')

    class __Meta__:
        table = 'fbtime'


# @register_config
# class PatchChangeConfig(Config):
#     uid = IntegerField('id', key=True)  # 专属碎片id
#     num = IntegerField('num')  # 兑换所需数量
#
#     class __Meta__:
#         table = 'convert'

# @register_config
# class PatchCompoundConfig(Config):
# materialid = IntegerField('itemid1', key=True) #碎片合成材料
# num        = IntegerField('num')     #合成所需数量
# proudctid  = IntegerField('itemid2') #碎片合成结果
#
#    class __Meta__:
#        table = 'compose'


@register_config
class SkyMallDroppackConfig(Config):
    id = IntegerField('id')
    droptype = IntegerField('droptype', groupkey=True)  # 掉落包类型
    dropprob = IntegerField('dropProb')  # 掉落权重
    itemtype = IntegerField('itemtype')
    itemid = IntegerField('itemid')  # 兑换材料id，白、绿、蓝、紫、金
    num = IntegerField('price')  # 材料数量
    timelimit = IntegerField('timesLimit')  # 兑换限制次数
    type = IntegerField('producttype')  # 商品类型
    itemID = IntegerField('productID')  # 商品id
    amount = IntegerField('amount')  # 商品数量
    openlevel = IntegerField('openlevel')  # 开启等级

    class __Meta__:
        table = 'StoreDroppack'


@register_config
class PatchMallRangeConfig(Config):
    range = CustomField('range', decoder=default_decoder_by(','))
    droptype = CustomField('droptype', decoder=default_decoder_vertical_line)
    # 1,天庭商店 2,银角商店 3,金角商店 3,临时银角商店 4,临时的金角商店
    type = IntegerField('type', groupkey=True)

    class __Meta__:
        table = 'StoreGoodsDrop'


@register_config
class MallFlushConfig(Config):
    id = IntegerField('id')
    type = IntegerField('type', key=True)  # 1,天庭商店 2,银角商店 3,金角商店
    gold = IntegerField('coin')  # 刷新所需钻石数
    cdtimes = IntegerField('cdtimes')  # 刷新cd
    num = IntegerField('num')  # 神秘商店界面显示条目数
    level = IntegerField('level')  # 开启等级限制
    goldenup = IntegerField('goldenup')  # 开启永久商店所需要钻石数
    daytime1 = IntegerField('daytime1')  # 每日刷新时间
    daytime2 = IntegerField('daytime2')
    daytime3 = IntegerField('daytime3')
    daytime4 = IntegerField('daytime4')

    class __Meta__:
        table = 'renovate'


@register_config
class VipConfig(Config):
    level = IntegerField('level', key=True)
    amount = IntegerField('amount')
    description = StringField('version')
    buy_sp_count = IntegerField('buy_sp_count')
    golden_finger_count = IntegerField('golden_finger_count')
    buy_advanced_fb_count = IntegerField('buy_advanced_fb_count')
    refresh_shop_count = IntegerField('refresh_shop_count')
    silver_king_shop = BooleanField('silver_king_shop')
    golden_king_shop = BooleanField('golden_king_shop')
    silver_shop_count = IntegerField('silver_shop_count')
    golden_shop_count = IntegerField('golden_shop_count')
    can_cleanfb = IntegerField('fb_clean')
    pvp_shop_count = IntegerField('pvp_shop_count')
    hot_unit = IntegerField('hot_unit')
    strengthen_crit_min = IntegerField('cir_min')
    strengthen_crit_max = IntegerField('cir_max')
    rob_max_count = IntegerField("rob_max_count")
    uproar_count = IntegerField("uproar_num")
    uproar_shop_count = IntegerField("fairy_shop_count")
    pvp_reset_count = IntegerField("buy_pvp_count")
    treasure_max_count = IntegerField("golden_silver_hill_count")
    tap_onekey = IntegerField("atk_monster_clear")
    giftID = IntegerField("gift_id")
    day_giftID = IntegerField("daygift_id")
    skill_up_count = IntegerField("skill_up_count")
    buy_skill_count = IntegerField("buy_skill_count")
    daily_buy_most_count = IntegerField("buy_dailypvp_count")
    buy_soul_count = IntegerField("soul_finger_count")
    treeIsland_count = IntegerField("treeIsland_count")   # 树岛森林挑战次数
    twinIsland_count = IntegerField("twinIsland_count")  # 双子岛挑战次数
    faction_shop_count = IntegerField("unions_shop_count")
    climb_tower_reset_count = IntegerField("climb_tower_reset")  # 幻影之塔重置次数

    class __Meta__:
        table = 'Vip'


@register_config
class RefreshFbCostConfig(Config):
    count = IntegerField('time', key=True)
    cost = IntegerField('coin')

    class __Meta__:
        table = 'elite'


@register_config
class RechargeConfig(Config):

    """充值列表"""
    id = IntegerField('id', key=True)
    type = IntegerField('type')
    name = StringField('name')
    cmd1 = StringField('cmd1')
    golden = IntegerField('golden')
    currency = StringField('currency')
    amount = StringField('amount')
    sdktype = IntegerField('sdktype')
    goodsid = StringField('goodsid')
    gift_png = StringField('gift_png')
    first_tag = StringField('first_tag')
    general_tag = StringField('general_tag')
    first_drop = IntegerField('first_drop')
    general_drop = IntegerField('general_drop')
    general_cmd = StringField('general_cmd')
    bright_point = BooleanField("bright_point")
    channelLabel = StringField("channelLabel")

    class __Meta__:
        table = 'goldenup'


@register_config
class RechargeBySdktypeConfig(Config):
    sdktype = IntegerField("sdktype", groupkey=True)
    id = IntegerField("id")

    class __Meta__:
        table = 'goldenup'


@register_config
class RechargeByTypeConfig(Config):
    type = IntegerField("type", groupkey=True)
    id = IntegerField("id")

    class __Meta__:
        table = 'goldenup'


@register_config
class RechargeByLabelConfig(Config):
    label = StringField("channelLabel", groupkey=True)
    id = IntegerField("id")

    class __Meta__:
        table = 'goldenup'


def validate_rewards_json(self, v, lineno=None):
    if v in (0, '0', ''):
        return "[]"
    try:
        decoded = ujson.loads(v)
        for i in decoded:
            if not isinstance(i, (list, tuple, set)):
                raise ValueError
    except Exception as e:
        raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (
            lineno, self.column_name, self.name, str(e), repr(v)))
    return v


@register_config
class TaskConfig(Config):
    ID = IntegerField('id', key=True)
    prev = IntegerField('upindex')
    post = IntegerField('downindex')
    type = IntegerField('missiontype')
    subtype = IntegerField("table")
    cond = IntegerField('conditiontype')
    goal = IntegerField('planvalue')
    drop = IntegerField('packid')
    # iconType = IntegerField('icontype')
    # iconID = StringField('iconid')
    # quality = StringField('quality')
    title = StringField('titledesc')
    desc = StringField('desc')
    # dropdesc = StringField('rewarddesc')
    arg = IntegerField('arg')
    arg2 = CustomField(
        'arg2',
        decoder=default_decoder_vertical_line,
        skipzero=True)  # 条件参数
    openlevel = IntegerField('openlevel')  # 开启等级
    sameID = IntegerField('saveid')
    groupID = IntegerField('groupid')
    rewards = CustomField("rewards", decoder=validate_rewards_json)
    openfb = CustomField(
        'openfb',
        decoder=default_decoder_vertical_line,
        skipzero=True)  # 开启副本

    push = BooleanField("push")
    order = IntegerField("order")
    transmit = StringField("transmit")

    class __Meta__:
        table = 'missionreward'


@register_config
class TaskByTypeConfig(Config):
    ID = IntegerField('id')
    type = IntegerField('missiontype', groupkey=True)

    class __Meta__:
        table = 'missionreward'


@register_config
class TaskByCondConfig(Config):
    ID = IntegerField('id')
    cond = IntegerField('conditiontype', groupkey=True)

    class __Meta__:
        table = 'missionreward'


@register_config
class TaskByGroupConfig(Config):
    ID = IntegerField('id')
    group = IntegerField("groupid", groupkey=True)

    class __Meta__:
        table = 'missionreward'


@register_config
class GoldenFingerConfig(Config):
    id = IntegerField('id', key=True)
    golden = IntegerField('golden')
    silver = IntegerField('silver')

    class __Meta__:
        table = 'golden_finger'


@register_config
class GoldFingerLvLimitConfig(Config):
    id = IntegerField('id', key=True)
    openlv = IntegerField('open_lv')

    class __Meta__:
        table = 'golden_finger_lv'


@register_config
class GoldenMallDroppackConfig(Config):
    id = IntegerField('id')
    droptype = IntegerField('droptype', groupkey=True)  # 掉落包类型
    dropprob = IntegerField('dropProb')  # 掉落权重
    itemtype = IntegerField('itemtype')  # 货币类型
    itemid = IntegerField('itemid')  # 货币id
    num = IntegerField('price')  # 货币数量
    timelimit = IntegerField('timesLimit')  # 购买限制次数
    type = IntegerField('producttype')  # 商品类型
    itemID = IntegerField('productID')  # 商品id
    amount = IntegerField('amount')  # 商品数量
    openlevel = IntegerField('openlevel')  # 开启等级

    class __Meta__:
        table = 'goldenstore'


@register_config
class SilverMallDroppackConfig(Config):
    id = IntegerField('id')
    droptype = IntegerField('droptype', groupkey=True)  # 掉落包类型
    dropprob = IntegerField('dropProb')  # 掉落权重
    itemtype = IntegerField('itemtype')  # 货币类型
    itemid = IntegerField('itemid')  # 货币id
    num = IntegerField('price')  # 货币数量
    timelimit = IntegerField('timesLimit')  # 购买限制次数
    type = IntegerField('producttype')  # 商品类型
    itemID = IntegerField('productID')  # 商品id
    amount = IntegerField('amount')  # 商品数量
    openlevel = IntegerField('openlevel')  # 开启等级

    class __Meta__:
        table = 'silverstore'


@register_config
class PvpMallDroppackConfig(Config):
    id = IntegerField('id')
    droptype = IntegerField('droptype', groupkey=True)  # 掉落包类型
    dropprob = IntegerField('dropProb')  # 掉落权重
    itemtype = IntegerField('itemtype')  # 货币类型
    itemid = IntegerField('itemid')  # 货币id
    num = IntegerField('price')  # 货币数量
    timelimit = IntegerField('timesLimit')  # 购买限制次数
    type = IntegerField('producttype')  # 商品类型
    itemID = IntegerField('productID')  # 商品id
    amount = IntegerField('amount')  # 商品数量
    openlevel = IntegerField('openlevel')  # 开启等级

    class __Meta__:
        table = 'pvpstore'


@register_config
class TempStoreOpenConfig(Config):
    id = IntegerField('id')
    sp = IntegerField('sp', key=True)  # 累计能量
    silverprob = FloatField('prob1')  # 开启临时银角商店概率
    goldenprob = FloatField('prob2')  # 开启临时金角商店概率

    class __Meta__:
        table = 'storeopen'


@register_config
class GrowthConfig(Config):
    ID = IntegerField('id', key=True)
    rarity = IntegerField('rarity')
    step = IntegerField('step')
    evo_cost = IntegerField('evo_cost')
    breed_cost = IntegerField('breed_cost')
    hero_lv = IntegerField('hero_lv')

    class __Meta__:
        table = 'herogrowth'


@register_config
class MallflushgoldConfig(Config):
    time = IntegerField('id', key=True)
    refresh_golden_type = IntegerField('refresh_golden_type')
    goldengold = IntegerField('refresh_golden_coin')
    refresh_silver_type = IntegerField('refresh_silver_type')
    silvergold = IntegerField('refresh_silver_coin')
    refresh_sky_type = IntegerField('refresh_air_type')
    skygold = IntegerField('refresh_air_coin')
    refresh_pvp_type = IntegerField('refresh_pvp_type')
    pvpgold = IntegerField('refresh_pvp_coin')
    refresh_uproar_type = IntegerField("refresh_fairy_type")
    uproargold = IntegerField('refresh_fairy_coin')

    class __Meta__:
        table = 'refresh_shop'


@register_config
class PetPaltHotConfig(Config):
    id = IntegerField('id', key=True)
    itemid1 = IntegerField('itemid1')  # 精灵1
    type1 = IntegerField('type1')
    amount1 = IntegerField('amount1')
    prob1 = IntegerField('prob1')
    itemid2 = IntegerField('itemid2')  # 精灵2
    type2 = IntegerField('type2')
    amount2 = IntegerField('amount2')
    prob2 = IntegerField('prob2')
    itemid3 = IntegerField('itemid3')  # 精灵3
    type3 = IntegerField('type3')
    amount3 = IntegerField('amount3')
    prob3 = IntegerField('prob3')
    packid = IntegerField('drop')

    class __Meta__:
        table = 'dayunits'


@register_config
class PetPaltSuperHotConfig(Config):
    id = IntegerField('id', key=True)
    itemid = IntegerField('itemid')  # 热点超精灵
    type = IntegerField('type')
    amount = IntegerField('amount')
    prob = IntegerField('prob')
    starttime = DatetimeField('starttime')
    endtime = DatetimeField('lasttime')

    class __Meta__:
        table = 'hotunits'


@register_config
class PetPaltLimitConfig(Config):
    id = IntegerField('id', key=True)
    level = IntegerField('lv')
    gold = IntegerField('gold')

    class __Meta__:
        table = 'openlv'


@register_config
class MatConfig(Config):
    ID = IntegerField('id', key=True)
    type = IntegerField('type', choices=MatType)
    arg = IntegerField('index')  # 对应的units表里的prototypeID
    arg2 = IntegerField("piece_index")  # 如果arg是进化怪，那么对应的物品表ID（用于精灵兑换）
    tips = StringField("tips")

    class __Meta__:
        table = 'items'


@register_config
class BreakConfig(Config):
    level = IntegerField('id', key=True)
    bhp = FloatField('bHP')
    batk = FloatField('batk')
    bdef = FloatField('bdef')
    bcrit = FloatField('bcrit')
    bdodge = FloatField('bdodge')
    amount = IntegerField('amount')
    money = IntegerField('silver')
    # star = IntegerField("star_value")
    max_level = IntegerField("lv_limit")

    class __Meta__:
        table = 'break'


@register_config
class FactionDonateConfig(Config):
    type = IntegerField('id', key=True)
    arg1 = IntegerField('cointype1')
    arg2 = IntegerField('cointype2')

    class __Meta__:
        table = 'union_convert'


@register_config
class GiftkeyConfig(Config):

    def decode_json_object(self, v, lineno=None):
        if v in (0, '0', ''):
            return {}
        try:
            v = ujson.loads(v)
            if not isinstance(v, dict):
                raise TypeError
        except Exception as e:
            raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (
                lineno, self.column_name, self.name, str(e), repr(v)))
        return v

    ID = IntegerField('id', key=True)
    group = IntegerField("group")
    name = StringField('name')
    start_time = DatetimeField('start_time', required=False)
    end_time = DatetimeField('end_time', required=False)
    dropPacks = CustomField(
        'packid', decoder=default_decoder_vertical_line, skipzero=True)
    dropPacks_count = CustomField(
        'packcount', decoder=default_decoder_vertical_line, skipzero=True)
    mats = CustomField(
        'matid', decoder=default_decoder_vertical_line, skipzero=True)
    mats_count = CustomField(
        'matcount', decoder=default_decoder_vertical_line, skipzero=True)
    equips = CustomField(
        'equipid', decoder=default_decoder_vertical_line, skipzero=True)
    equips_count = CustomField(
        'equipcount', decoder=default_decoder_vertical_line, skipzero=True)
    specPacks = CustomField(
        'specPackid', decoder=default_decoder_vertical_line, skipzero=True)
    specPacks_count = CustomField(
        'specPackcount', decoder=default_decoder_vertical_line, skipzero=True)
    pets = CustomField(
        'petid', decoder=default_decoder_vertical_line, skipzero=True)
    pets_count = CustomField(
        'petcount', decoder=default_decoder_vertical_line, skipzero=True)
    attrs = CustomField('attrs', decoder=decode_json_object)
    each_use_count = IntegerField('each_use_count')
    use_count = IntegerField('use_count')

    class __Meta__:
        table = 'cdkey'


@register_config
class EquipConfig(Config):
    prototypeID = IntegerField('eid', key=True)
    name = StringField('ename')
    type = IntegerField('ekind')
    quality = IntegerField('ecolor')
    k = IntegerField('eq')  # 强化消耗系数
    need_patch = IntegerField("pnum")
    refining = IntegerField("value")  # 炼化保底钱币
    ATK = IntegerField("ATK")
    AGU = FloatField("AGU")
    AGV = IntegerField("AGV")
    HP = IntegerField("HP")
    HGU = FloatField("HGU")
    HGV = IntegerField("HGV")
    DEF = IntegerField("DEF")
    DGU = FloatField("DGU")
    DGV = IntegerField("DGV")
    EVA = IntegerField("EVA")
    EGU = FloatField("EGU")
    EGV = IntegerField("EGV")
    CRI = IntegerField("CRI")
    CGU = FloatField("CGU")
    CGV = IntegerField("CGV")
    suitID = IntegerField("issuit")
    exclID = IntegerField("isexclusive")
    enchID = IntegerField("attr_id")

    class __Meta__:
        table = 'equip'


@register_config
class EquipAdvanceLimitConfig(Config):
    quality = IntegerField("ecolor")
    type = IntegerField("ekind")
    limit = IntegerField("stlimit")
    pcount = IntegerField("pcount")

    class __Meta__:
        table = "equipadvancelimit"
        unique_together = ("quality", "type")


@register_config
class MineConfig(Config):
    level = IntegerField("house_lv", key=True)
    mine_maximum1 = IntegerField("house1_size")
    mine_productivity1 = IntegerField("house1_speed")
    mine_safety1 = IntegerField("house1_line")
    mine_maximum2 = IntegerField("house2_size")
    mine_productivity2 = IntegerField("house2_speed")
    mine_safety2 = IntegerField("house2_line")

    class __Meta__:
        table = 'resource'


@register_config
class MineProductivity(Config):
    type = IntegerField("type")
    rarity = IntegerField("rarity")
    productivity1 = IntegerField("speed1")
    productivity2 = IntegerField("speed2")

    class __Meta__:
        table = 'herospeed'
        unique_together = ("type", "rarity")


@register_config
class UproarConfig(Config):
    n = IntegerField("id", key=True)
    prev = IntegerField("upindex")
    post = IntegerField("downindex")
    k = FloatField("diffdegree")
    dropID = IntegerField("packid")
    jiutian = IntegerField("currency")
    money_base = IntegerField("coindegree")
    robot = IntegerField("robot_id")
    op = IntegerField("operation")

    class __Meta__:
        table = 'uproar'


@register_config
class UproarMallDroppackConfig(Config):
    id = IntegerField('id')
    droptype = IntegerField('droptype', groupkey=True)  # 掉落包类型
    dropprob = IntegerField('dropProb')  # 掉落权重
    itemtype = IntegerField('itemtype')  # 货币类型
    itemid = IntegerField('itemid')  # 货币id
    num = IntegerField('price')  # 货币数量
    timelimit = IntegerField('timesLimit')  # 购买限制次数
    type = IntegerField('producttype')  # 商品类型
    itemID = IntegerField('productID')  # 商品id
    amount = IntegerField('amount')  # 商品数量
    openlevel = IntegerField('openlevel')  # 开启等级

    class __Meta__:
        table = 'uproarstore'


@register_config
class LootConfig(Config):
    type = IntegerField("quality")
    min = IntegerField("snatchmin")
    max = IntegerField("snatchmax")
    prob = IntegerField("chance")

    class __Meta__:
        table = "snatchnum"


@register_config
class NewsConfig(Config):
    ID = IntegerField("id", key=True)
    type = IntegerField("newstype")
    desc = StringField("newsdesc")
    args = CustomField(
        'arg',
        decoder=default_decoder_vertical_line,
        skipzero=True)  # 条件参数

    class __Meta__:
        table = "diaonews"


@register_config
class NewsByTypeConfig(Config):
    type = IntegerField("newstype", groupkey=True)
    ID = IntegerField("id")

    class __Meta__:
        table = "diaonews"


@register_config
class TipsConfig(Config):
    ID = IntegerField("id", key=True)
    desc = StringField("tips")
    weight = IntegerField("weight")

    class __Meta__:
        table = "tipnews"


@register_config
class SpecpackConfig(Config):
    ID = IntegerField("id", key=True)
    ref_id = IntegerField("refid")
    ref_type = IntegerField("reftype")
    p_star = IntegerField("u_star")
    p_level = IntegerField("u_level")
    e_step = IntegerField("e_step")
    e_level = IntegerField("e_level")

    @classmethod
    def ref_check(cls, line, colname, alldata, refcls):
        if line[colname] not in alldata[refcls.__name__]:
            col = cls.fields[colname]
            msg = u"{} 中 ref_id 为 {} 的记录，字段 {} 引用了一个不存在于 {} 的值 {}。".format(
                cls.__Meta__.table, line["ref_id"],
                "%s(%s)" % (col.column_name, col.name),
                refcls.__Meta__.table, line[colname])
            raise ValidationError(msg)

    @classmethod
    def post_validation(cls, alldata):
        for k, pack in alldata[cls.__name__].items():
            if pack["ref_type"] == RewardItemType.Equip:
                cls.ref_check(pack, "ref_id", alldata, NewEquipConfig)
            elif pack["ref_type"] == RewardItemType.Pet:
                cls.ref_check(pack, "ref_id", alldata, PetConfig)
            else:
                raise ValidationError(
                    u"specialDrop ref_type 字段包含无效的值: {}".format(
                        pack["ref_type"]))

    class __Meta__:
        table = "specialDrop"


@register_config
class VisitConfig(Config):
    id = IntegerField("id", key=True)
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    prob = IntegerField("prob")
    flag = IntegerField("flag")

    class __Meta__:
        table = "visit"


@register_config
class VisitIncrByGroupConfig(Config):
    # id,group,count,type|itemID|amount1
    id = IntegerField("id")
    group = IntegerField("group", groupkey=True)
    count = IntegerField("count")
    drop = IntegerField("drop")
    # rewards = CustomField(
    #     'type|itemID|amount',
    #     repeated=True,
    #     range=1,
    #     decoder=decode_rewards,
    #     skipzero=True)

    class __Meta__:
        table = "visit_sever"


@register_config
class VisitRewardByGroupConfig(Config):
    pious = IntegerField("pious_require")
    group = IntegerField("group", groupkey=True)
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "visit_reward"


@register_config
class LevelPacksConfig(Config):
    id = IntegerField("id", key=True)
    level = IntegerField("level")
    drop = IntegerField("dropid")
    rewards = CustomField("rewards", decoder=validate_rewards_json)

    class __Meta__:
        table = 'levelPackage'


@register_config
class StarPacksConfig(Config):
    id = IntegerField("id", key=True)
    star = IntegerField("stars")
    sceneID = IntegerField("chapter")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = 'fbstars'


@register_config
class ComposePetConfig(Config):
    def decode_stuffs(self, v, lineno=None):
        if v in (0, '0', '', '-'):
            return []
        try:
            ret = map(int, v.split('|'))
        except ValueError as e:
            raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (
                lineno, self.column_name, self.name, str(e), repr(v)))
        return ret
    id = IntegerField("id", key=True)
    unlocklv = IntegerField("unlocklv")
    stuffs = JSONField("units1")
    money = IntegerField("coin")
    soul = IntegerField("soul")

    class __Meta__:
        table = "units_compose"


@register_config
class ComposeEquipConfig(Config):
    def decode_stuffs(self, v, lineno=None):
        if v in (0, '0', '', '-'):
            return []
        try:
            ret = map(int, v.split('|'))
        except ValueError as e:
            raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (
                lineno, self.column_name, self.name, str(e), repr(v)))
        return ret
    id = IntegerField("id", key=True)
    unlocklv = IntegerField("unlocklv")
    stuffs = JSONField("equip1")
    money = IntegerField("coin")
    soul = IntegerField("soul")

    class __Meta__:
        table = "equip_compose"


@register_config
class ComposeMatConfig(Config):
    id = IntegerField("id", key=True)  # 所需材料ID
    compose = IntegerField("stuffid")  # 合成目标ID
    count = IntegerField("count")
    money = IntegerField("coin")
    soul = IntegerField("soul")

    @classmethod
    def post_validation(cls, alldata):
        configs = alldata[cls.__name__]
        mats = alldata[MatConfig.__name__]
        error = u"{} 中 {} 为 {}， 不存在于 {} 中。"
        for id, config in configs.items():
            if config["compose"] and config["compose"] not in mats:
                col = cls.fields["compose"]
                error = error.format(
                    cls.__Meta__.table,
                    col.column_name,
                    config["compose"],
                    MatConfig.__Meta__.table)
                raise ValidationError(error)

    class __Meta__:
        table = "stuff_compose"


@register_config
class FirstRechargeConfig(Config):
    id = IntegerField("id")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    worth_gold = IntegerField("parm1")
    gift_gold = IntegerField("parm2")

    class __Meta__:
        table = 'firstup'


@register_config
class LimitedPacksConfig(Config):
    id = IntegerField("id")
    start = DatetimeField('start')
    end = DatetimeField('end')
    count = IntegerField("count")

    class __Meta__:
        table = 'limit'


@register_config
class TimeLimitedPacksConfig(Config):
    id = IntegerField("id")
    start = DatetimeField("start")
    end = DatetimeField("end")
    goodsid = IntegerField("goodsid")

    class __Meta__:
        table = "festival"


@register_config
class PvpDegreeConfig(Config):
    start = IntegerField("downscore")
    end = IntegerField("upscore")
    prob = FloatField("vsrobot")

    class __Meta__:
        table = 'vsrobot'


@register_config
class PvpRefreshConfig(Config):
    count = IntegerField('id', key=True)
    gold = IntegerField('buff_gold')

    class __Meta__:
        table = 'pvp_refresh_gold'


@register_config
class PvpResetConfig(Config):
    count = IntegerField('id', key=True)
    gold = IntegerField('pvp_gold')

    class __Meta__:
        table = 'pvp_reset_gold'


@register_config
class PvpSerialWinBuffConfig(Config):
    count = IntegerField('id', key=True)
    buffs = IntegerField('buff', repeated=True, range=1, skipzero=True)
    params = IntegerField('param', repeated=True, range=1, skipzero=True)
    cd = IntegerField('cd_time')

    class __Meta__:
        table = 'wining_buff'


@register_config
class PvpGradConfig(Config):
    ID = IntegerField("id")
    score = IntegerField('score')
    count = IntegerField('battle_num')  # 挑战次数
    ranking = IntegerField('ranking')
    win_gain = IntegerField('win_award')
    lose_gain = IntegerField('lose_award')
    grad_png = IntegerField("grad_png")

    class __Meta__:
        table = 'pvp_grad'


@register_config
class NpcConfig(Config):
    id = IntegerField('id', key=True)
    openlevel = IntegerField('open_level')
    cd = IntegerField('renovate_time')
    rewards = CustomField(
        'reward',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    group = IntegerField("group")

    class __Meta__:
        table = 'npc_renovate_time'


@register_config
class SparConfig(Config):
    ID = IntegerField("id", key=True)
    itemID = IntegerField('itemid')
    money = IntegerField('cost')
    drop = IntegerField('droppack')
    show = IntegerField('sparshow')
    onekeycount = IntegerField("ten_count")
    dropex_use_count = IntegerField("use_doprpack_count")
    dropex = IntegerField("special_droppack")
    tips = StringField("tips")
    final_tips = StringField("final_tips")

    class __Meta__:
        table = 'spar'


@register_config
class Cons(Config):
    tags = {
        "AutoFightAfterThisNormalFbID": (1, 100111),
        "DongtianCD": (2, 86400),
        "FudiCD": (3, 86400),
        "TempSilverMallCD": (4, 86400),
        "TempGoldenMallCD": (5, 86400),
        "OpenSilverMallCost": (6, 1000),
        "OpenGoldenMallCost": (7, 1000),
        "FriendfbBeInvitedCount": (8, 9999),
        "TapOnekeyVipLevel": (9, 15),
        "TapCritProb": (10, 0),
        "FactionAlterNameGold": (11, 1000),
        "TreasureRefreshGold": (12, 1000),
        "TreasureCleanCDGold": (13, 1000),

        "FactionDonateLimited": (15, 9999),
        "FactionSpDonateLimited": (16, 9999),
        "TreasureNeedBuffCount": (17, 0),
        "TreasureRoundCount": (18, 10),
        "CanCleanCampaignfbVipLevel": (20, 15),
        "PatchChangeMoneyCost": (21, 0),
        "BuyFundNeedVip": (22, 15),  # 购买开服基金所需VIP等级
        "BuyFundNeedGold": (23, 1000),  # 购买开服基金所需钻石
        "WishMaxCount": (24, 10),  # 最大许愿次数
        "CheckInMakeUpCost": (25, 1000),  # 补签消耗
        "TriggerChestDoubleCost": (26, 1000),  # 单宝箱双倍消耗
        "TriggerChestsMoreCost": (27, 1000),  # 多宝箱再开消耗
        "FundFakeNumber": (28, 0),  # 购买开服基金人数添加
        "TriggerChestMultiple": (29, 1),  # 触发单宝箱加倍倍数
        "SpeedUpFightAfterThisNormalFbID": (30, 100111),  # 对在此关卡之后的普通关卡开启战斗加速
        "WishNewPlayerExperienceFlag": (31, 1),  # 许愿池新玩家体验开关
        "WishNewPlayerExperienceTime": (32, 86400),  # 许愿池体验倒计时
        "MonthlyCardDropID": (33, 0),  # 月卡奖励掉落包ID
        "MonthlyCardInterval": (34, 30),  # 月卡时长
        "MonthlyCardAccAmount": (35, 30),  # 月卡激活需要金额
        "PvpMinRankerCount": (36, 0),  # 争霸最少参与人数
        "EnchantStoneToGold": (37, 1000),  # 钻石兑换熔石比率
        "DlcHelperCD": (38, 86400),  # Dlc助战cd
        "EnchantCostBase": (39, 1),  # 普通重铸消耗熔石基数
        "EnchantExCostBase": (40, 1),  # 高级重铸消耗熔石基数
        "EnchantFreeCount": (41, 0),  # 每日普通重铸免费次数
        "VisitFreeMaxCount": (42, 0),  # 每日拜八仙免费次数
        "VisitCost": (43, 1000),  # 每日拜八仙每次消耗
        "GveRebornCost": (44, 0),  # Gve复活消耗
        "GveBuffAddition": (45, 0),  # Gve buff 加成
        "FriendfbRebornCost": (46, 0),  # 秘境重生消耗系数
        "SwapRankCD": (47, 86400),  # PVP挑战CD时间
        "SwapRankCDCost": (48, 1000),  # 清除PVP挑战CD时间所需钻石
        "SwapMostCount": (49, 0),  # 最大挑战次数
        "MazeMostCount": (50, 9999),  # 无尽迷宫探索次数上限
        "MazeMustDropID": (51, 0),  # 无尽迷宫基础掉落包
        "MazeOnekeyPoint": (52, 9999),  # 无尽迷宫一键探索VIP等级
        "MazeOnekeyVip": (53, 15),  # 无尽迷宫一键探索成就
        "MazeMustDropMoney": (54, 0),  # 无尽迷宫基础掉落金币
        "EnableCDAfterRank": (55, 100),  # PVP排名XX以内激活战斗后CD倒计时
        "DailyRankRobot": (56, 10010),  # 每日PVP机器人id
        "DailyRed": (57, 40011),  # 每日PVP红包掉落包
        "RankingCampaignDeadlineTime": (58, 259200),  # 七天排行活动结束后延迟结束时间
        "RankingCampaignReservedTime": (59, 86400),  # 七天排行活动预告开启提前时间
        "GuideDefeat": (60, 9999),  # 首败奖励
        "DailyPVPDrop": (61, 8888),  # 每日PVP基础奖励
        "DailyDeadCD": (62, 30),  # 每日PVP复活时间
        "DailyRebornCost": (63, 50),  # 每日PVP复活所需钻石
        "CityContendFailPunish": (64, 5),  # 抢夺防守方失败惩罚
        "CityContendAttackMoney": (65, 50),  # 抢夺攻击方奖励
        "CityContendAttackSoul": (66, 10),  # 抢夺攻击方奖励
        "AmbitionUpCost": (67, 1000),  # 道馆集训普通消耗
        "AmbitionGoldUpCost": (68, 50),  # 道馆集训钻石消耗
        "MonthcardDailyGain1": (69, 40017),  # 普通月卡每日可领取（25元）
        "MonthcardGain1": (70, 250),  # 普通月卡购买后即可获得（25元）
        "MonthcardDailyGain2": (71, 40018),  # 尊贵月卡每日可领取（50元）
        "MonthcardGain2": (72, 500),  # 尊贵月卡购买即可获得（50元）
        "WeekscardDailyGain1": (73, 40019),  # 普通周卡每日可领取（25元）
        "WeekscardGain1": (74, 250),  # 普通周卡购买后即可获得（25元）
        "WeekscardDailyGain2": (75, 40020),  # 尊贵周卡每日可领取（50元）
        "WeekscardGain2": (76, 500),  # 尊贵周卡每日可领取（50元）
        "ArborDayFreeCount": (78, 10),  # 植树节遥一摇每日免费次数
        "ArborDayMaxCount": (79, 30),  # 植树节遥一摇每日最大可摇次数
        "ArborDayPayCost": (80, 50),  # 植树节遥一摇一次付费消耗
        "WateringMaxCount": (81, 5),  # 每天可以浇水的次数
        "WateringCD": (82, 600),  # 浇水的CD
        "WormingMaxCount": (83, 5),  # 每天可以除虫的次数
        "WormingCD": (84, 600),  # 除虫的CD
        "WateringReduceCD": (85, 60),  # 浇水减少的CD
        "WormingReduceCD": (86, 60),  # 除虫减少的CD
        "FlowerBossRebornCost": (87, 500),  # 除虫减少的CD
    }
    ID = IntegerField("id", key=True)
    value = IntegerField("value")

    @classmethod
    def post_validation(cls, alldata):
        configs = alldata[cls.__name__]
        supports = set()
        exists = set()
        for _, (ID, _) in cls.tags.items():
            supports.add(ID)
        for ID, config in configs.items():
            exists.add(ID)
        non_exists = supports.difference(exists)
        if non_exists:
            logger.warn("No exists {} in cons".format(non_exists))

    class __Meta__:
        table = 'cons'


def get_cons_value(tag):
    ID, default = Cons.tags[tag]
    config = get_config(Cons).get(ID)
    if not config:
        return default
    return config.value


@register_config
class ConsString(Config):
    tags = {
        "CampaignSequence": (1, ""),  # 活动按钮显示的顺序
        "CampaignWWReward_1": (2, ""),  # 活动按钮显示的顺序
        "CampaignWWReward_2": (3, ""),  # 活动按钮显示的顺序
    }
    ID = IntegerField("id", key=True)
    value = StringField("value")

    @classmethod
    def post_validation(cls, alldata):
        configs = alldata[cls.__name__]
        supports = set()
        exists = set()
        for _, (ID, _) in cls.tags.items():
            supports.add(ID)
        for ID, config in configs.items():
            exists.add(ID)
        non_exists = supports.difference(exists)
        if non_exists:
            logger.warn("No exists {} in consString".format(non_exists))

    class __Meta__:
        table = 'consString'


def get_cons_string_value(tag):
    ID, default = ConsString.tags[tag]
    config = get_config(ConsString).get(ID)
    if not config:
        return default
    return config.value


@register_config
class TreasureTypeConfig(Config):
    count = IntegerField("count", key=True)
    gold = IntegerField("gold")
    silver = IntegerField("silver")
    copper = IntegerField("copper")

    class __Meta__:
        table = "chest_prob"


@register_config
class TreasureConfig(Config):
    # id type data
    id = IntegerField("id", key=True)
    type = IntegerField("type")
    # type subtype count pos_or_times
    data = JSONField("data")

    class __Meta__:
        table = "map_configs"


@register_config
class TreasureByTypeConfig(Config):
    # id type data
    id = IntegerField("id")
    type = IntegerField("type", groupkey=True)

    class __Meta__:
        table = "map_configs"


@register_config
class TreasureChestConfig(Config):
    # id,dropid,start_reward,golden
    type = IntegerField("id", key=True)
    drop = IntegerField("dropid")
    dropex = IntegerField("start_reward")
    gold = IntegerField("golden")

    class __Meta__:
        table = "map_reward"


@register_config
class TapMonsterConfig(Config):
    id = IntegerField("id", key=True)
    monster = IntegerField("monster_id")
    size = IntegerField("monster_size")
    hp = IntegerField("monster_hp")
    prob = IntegerField("monster_prob")  # 乱入概率
    drop = IntegerField("drop_id")

    class __Meta__:
        table = "atk_monster"


@register_config
class TapLoopConfig(Config):
    id = IntegerField("id", key=True)
    monsters = CustomField(
        "monster_config", decoder=default_decoder_vertical_line)
    probs = CustomField(
        "monster_prob", decoder=default_decoder_vertical_line)

    class __Meta__:
        table = "atk_SceneInfo"


@register_config
class TriggerAfterFbConfig(Config):
    sp = IntegerField('sp')
    friendfb_prob = FloatField('relic')
    goldenmall_prob = FloatField("goldenstore")
    silvermall_prob = FloatField("silverstore")
    trigger_event_prob = FloatField("event")

    class __Meta__:
        table = 'trigger'


@register_config
class FriendfbConfig(Config):
    fbID = IntegerField('fbid', key=True)
    name = StringField('fbname')
    bossname = StringField('bossname')
    bossID = IntegerField('bossid')
    openlv = IntegerField("openlv")
    prob = IntegerField("prob")
    active_num = IntegerField('active_num')  # 推荐需要多少人
    dpr = IntegerField('dpr')
    drop = IntegerField('basedrop')
    find_kill_drop = IntegerField('find_kill_drop')
    join_kill_drop = IntegerField('join_kill_drop')
    rewards = StringField('reward')
    pname = StringField("pname")

    class __Meta__:
        table = 'relic'


@register_config
class FriendfbByLevelConfig(Config):
    fbID = IntegerField('fbid')
    openlv = IntegerField('openlv', groupkey=True)

    class __Meta__:
        table = 'relic'


@register_config
class FriendfbRewardConfig(Config):
    ID = IntegerField("id", key=True)
    fbID = IntegerField("relic_id")
    range = CustomField('ranking', decoder=default_decoder_vertical_line)
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "relicRanking"


@register_config
class FriendfbRewardByFbIDConfig(Config):
    fbID = IntegerField("relic_id", groupkey=True)
    ID = IntegerField("id")

    class __Meta__:
        table = "relicRanking"


@register_config
class FactionTaskConfig(Config):
    ID = IntegerField('ID', key=True)
    prob = IntegerField('order')

    class __Meta__:
        table = 'unionsmission'


@register_config
class MallConfig(Config):
    ID = IntegerField("id", key=True)
    type = IntegerField("type")
    pos = IntegerField("droptype")
    prob = IntegerField("dropProb")
    item_type = IntegerField("itemtype")
    itemID = IntegerField("itemid")
    cd = IntegerField("cd")
    price = IntegerField("price")
    limit = IntegerField("timesLimit")
    product_type = IntegerField("producttype")
    productID = IntegerField("productID")
    product_amount = IntegerField("amount")
    level = IntegerField("openlevel")

    class __Meta__:
        table = "shopgoods"


@register_config
class MallByTypeConfig(Config):
    ID = IntegerField("id")
    type = IntegerField("type", groupkey=True)

    class __Meta__:
        table = "shopgoods"


@register_config
class MallRefreshConfig(Config):
    type = IntegerField("type", key=True)
    daytimes = IntegerField("daytime", repeated=True, range=1, skipzero=True)
    refresh_cost_type = IntegerField("refresh_cost_type")
    cost = IntegerField("refreshs")

    class __Meta__:
        table = "shoprefresh"


@register_config
class MallRefreshSequenceConfig(Config):
    """商店刷新次数和替换奖励组对应关系"""
    ID = IntegerField("id", key=True)
    type = IntegerField("type")
    pos = IntegerField("droptype")
    group1 = IntegerField("group1")
    group2 = IntegerField("group2")
    group3 = IntegerField("group3")
    sequence = CustomField(
        u'prandom_prob',
        decoder=default_decoder_vertical_line)

    class __Meta__:
        table = 'shop_prandom'


@register_config
class MallRefreshSequenceRewardConfig(Config):
    """商店刷新次数替换奖励组"""
    group = IntegerField("group", groupkey=True)
    reward_id = IntegerField("reward_id")
    prob = IntegerField("prob")

    @classmethod
    def post_validation(cls, alldata):
        configs = alldata[cls.__name__]
        mall = alldata[MallConfig.__name__]
        error = u"{} 中 {} 为 {}， 不存在于 {} 中。"
        for items in configs.values():
            for config in items:
                if config["reward_id"] not in mall:
                    col = cls.fields["reward_id"]
                    error = error.format(
                        cls.__Meta__.table,
                        col.column_name,
                        config["reward_id"],
                        MallConfig.__Meta__.table)
                    raise ValidationError(error)

    class __Meta__:
        table = 'reward_group'


@register_config
class FactionMallUnlockConfig(Config):
    pos = IntegerField("droptype", key=True)
    cost = IntegerField("unlock_cost")

    class __Meta__:
        table = "unionstore_unlock"


@register_config
class VipPacksConfig(Config):
    ID = IntegerField("id", key=True)
    gift_type = IntegerField("gift_type")
    gift_name = StringField("gift_name")
    gift_sort = IntegerField("gift_sort")
    gift_duration = IntegerField("gift_duration")
    gift_starttime = DatetimeField("gift_starttime")
    gift_lasttime = DatetimeField("gift_lasttime")
    fixed_price_type = IntegerField("fixed_price_type")
    fixed_price = IntegerField("fixed_price")
    discount_price_type = IntegerField("discount_price_type")
    discount_price = IntegerField("discount_price")
    gifts_des = StringField("gifts_des")
    vip_level = IntegerField("vip_level")
    buy_times = IntegerField("buy_times")
    gift_name_png = StringField("gift_name_png")
    gift_label = StringField("gift_label")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "gifts"


@register_config
class VipPacksByGroupConfig(Config):
    ID = IntegerField("id")
    group = IntegerField("gift_type", groupkey=True)

    class __Meta__:
        table = 'gifts'


@register_config
class CampaignByCampaignConfig(Config):
    ID = IntegerField("id")
    campaign = IntegerField("campaign", groupkey=True)

    class __Meta__:
        table = "campaign"


@register_config
class CampaignConfig(Config):
    CampaignWish = 1
    CampaignDailyAccRecharge = 2
    CampaignCycleAccRecharge = 3
    CampaignUproar = 4
    CampaignLoot = 5
    CampaignRob = 6
    CampaignGold = 7
    CampaignMaxpower = 8
    CampaignDailyPVP = 9
    CampaignVisit = 10
    CampaignDailyRecharge = 11
    CampaignLottery = 12
    CampaignPetExchange = 13
    CampaignNormalFb = 14
    CampaignAdvancedFb = 15
    CampaignMatExchange = 16
    CampaignConsume = 17
    CampaignLogin = 18
    CampaignRed = 19
    CampaignWeeksAccRecharge = 20
    CampaignMonthAccRecharge = 21
    CampaignHotLottery = 22
    CampaignExchange = 23
    CampaignFbDrop = 24
    CampaignRefreshStore = 25
    CampaignArborDay = 26
    CampaignSeed = 27
    CampaignHandsel = 28
    CampaignFlowerBoss = 29

    ID = IntegerField("id", key=True)
    campaign = IntegerField("campaign")
    start = DatetimeField("starttime")
    end = DatetimeField("lasttime")
    group = IntegerField("group")
    reward_group = IntegerField("reward_group")
    bg = StringField("bg_pic")

    class __Meta__:
        table = "campaign"


@register_config
class RewardCampaignDescConfig(Config):
    campaign = IntegerField("campaign")
    group = IntegerField("group")
    desc = StringField("desc")

    class __Meta__:
        table = "xianjing_campaign_desc"
        unique_together = ('campaign', 'group')


@register_config
class WishConfig(Config):
    count = IntegerField("id", key=True)
    cost_type = IntegerField("coin_type")
    start = IntegerField("start")
    ending = IntegerField("end")
    cost = IntegerField("cost")
    extra = IntegerField("etra")

    class __Meta__:
        table = "wish"


@register_config
class WishProbConfig(Config):
    ID = IntegerField("id", key=True)
    multi = FloatField("multiple")
    prob = IntegerField("prob")
    isshow = BooleanField("isshow")

    class __Meta__:
        table = "wish_times"


@register_config
class AccRechargeConfig(Config):
    ID = IntegerField("ID", key=True)
    type = IntegerField("type")
    group = IntegerField("group")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    gold = IntegerField("gold")

    class __Meta__:
        table = "acc_recharge"


@register_config
class AccRechargeByTypeConfig(Config):
    ID = IntegerField("ID")
    type = IntegerField("type", groupkey=True)

    class __Meta__:
        table = "acc_recharge"


@register_config
class AccRechargeByGroupConfig(Config):

    ID = IntegerField("ID")
    group = IntegerField("group", groupkey=True)

    class __Meta__:
        table = "acc_recharge"


@register_config
class FundRewardConfig(Config):
    ID = IntegerField("id", key=True)
    type = IntegerField("type")
    parm = IntegerField("parm")
    desc = StringField("desc")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "fund_start"


@register_config
class FundRewardByTypeConfig(Config):
    ID = IntegerField("id")
    type = IntegerField("type", groupkey=True)

    class __Meta__:
        table = "fund_start"


@register_config
class CheckInConfig(Config):
    ID = IntegerField("id", key=True)
    vips = IntegerField("vip_level", repeated=True, range=1)
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards)

    class __Meta__:
        table = "daily_register"


@register_config
class CheckInCostConfig(Config):
    # replenish_sign_count,golden
    ID = IntegerField("replenish_sign_count", key=True)
    gold = IntegerField("golden")

    class __Meta__:
        table = "replenish_sign"


@register_config
class TimedStoreConfig(Config):
    ID = IntegerField("id", key=True)
    post = IntegerField("dowm_index")
    cd = IntegerField("count_down")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    cost = IntegerField("golden")
    store_png = StringField("store_png")
    fixed_price = IntegerField("fixed_price")

    class __Meta__:
        table = "limit_time_store"


@register_config
class TriggerEventConfig(Config):
    ID = IntegerField("id", key=True)
    prob = IntegerField("prob")
    event_type = IntegerField("event_type")
    event_param = IntegerField("param")
    open_level = IntegerField("openlv")

    class __Meta__:
        table = "tri_event"


@register_config
class TriggerChestConfig(Config):
    ID = IntegerField("id", key=True)
    reward = CustomField("type|itemID|amount", decoder=decode_rewards)

    class __Meta__:
        table = "tri_singChest"


@register_config
class TriggerChestsConfig(Config):
    ID = IntegerField("id", key=True)
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "tri_plChest"


@register_config
class TriggerStoreConfig(Config):
    ID = IntegerField("id", key=True)
    show_id = IntegerField("show_id")
    reward = CustomField("type|itemID|amount", decoder=decode_rewards)
    fixed_price_type = IntegerField("fixed_price_type")
    fixed_price = IntegerField("fixed_price")
    discount_price_type = IntegerField("discount_price_type")
    discount_price = IntegerField("discount_price")

    class __Meta__:
        table = "tri_chap"


@register_config
class PvpRuleConfig(Config):
    # id,score,high_score_num,low_score_num,robot_num,force_overtop,force_under,robot_level
    ID = IntegerField("id", key=True)
    score = IntegerField("score")
    high_score_count = IntegerField("high_score_num")
    low_score_count = IntegerField("low_score_num")
    robot_count = IntegerField("robot_num")
    power_up = IntegerField("force_overtop")
    power_down = IntegerField("force_under")
    robot_level = IntegerField("robot_level")

    class __Meta__:
        table = "pvp_matching_rule"


@register_config
class EquipExclusiveConfig(Config):
    #  exclid,unit1,unit2,unit3,unit4,ATK,HP,DEF,EVA,CRI
    ID = IntegerField("exclid", key=True)
    pets = IntegerField('unit', repeated=True, range=1, skipzero=True)
    ATK = IntegerField("ATK")
    HP = IntegerField("HP")
    DEF = IntegerField("DEF")
    EVA = IntegerField("EVA")
    CRI = IntegerField("CRI")

    class __Meta__:
        table = "exclusive"


@register_config
class PetExclusiveConfig(Config):
    ID = IntegerField("same")
    equips = IntegerField("equip", repeated=True, range=1, skipzero=True)

    class __Meta__:
        table = "units_equip"


@register_config
class SuitConfig(Config):
    ID = IntegerField("suitid", key=True)
    equips = IntegerField("equip", repeated=True, range=1, skipzero=True)
    ATKs = IntegerField("ATK", repeated=True, range=1)
    HPs = IntegerField("HP", repeated=True, range=1)
    DEFs = IntegerField("DEF", repeated=True, range=1)
    EVAs = IntegerField("EVA", repeated=True, range=1)
    CRIs = IntegerField("CRI", repeated=True, range=1)

    class __Meta__:
        table = "suit"


@register_config
class EnchantConfig(Config):
    ID = IntegerField("id", key=True)
    quality = IntegerField("ecolor")
    color = IntegerField("attr_color")
    type = IntegerField("attr_type")
    value = FloatField("attr_value")
    prob = IntegerField("prob")

    class __Meta__:
        table = "adv_attr"


@register_config
class EnchantByQualityConfig(Config):
    ID = IntegerField("id")
    prob = IntegerField("prob")
    gold_prob = IntegerField("gold_prob")
    quality = IntegerField("ecolor", groupkey=True)

    class __Meta__:
        table = "adv_attr"


@register_config
class RelationBySameConfig(Config):
    ID = IntegerField("id")
    same = IntegerField("same", groupkey=True)

    class __Meta__:
        table = "karma"


@register_config
class RelationConfig(Config):
    ID = IntegerField("id", key=True)
    same = IntegerField("same")
    units = IntegerField("units", repeated=True, range=1, skipzero=True)
    atk_per = IntegerField("atk_per")
    atk_abs = IntegerField("atk_abs")
    def_per = IntegerField("def_per")
    def_abs = IntegerField("def_abs")
    hp_per = IntegerField("hp_per")
    hp_abs = IntegerField("hp_abs")
    cri = FloatField("cri")
    eva = FloatField("eva")

    class __Meta__:
        table = "karma"


@register_config
class AntiRelationConfig(Config):
    ID = IntegerField("same", key=True)
    relas = IntegerField('karma', repeated=True, range=1, skipzero=True)

    class __Meta__:
        table = "karma_index"


@register_config
class DlcConfig(Config):
    ID = IntegerField("id", key=True)
    scenes = CustomField('fb_ids', decoder=default_decoder_by('|'))
    name = StringField("name")
    background = StringField("background")
    pname = StringField("pname")
    start_desc = StringField("start_desc")
    end_desc = StringField("over_desc")
    open_desc = StringField("open_desc")
    open_time = DatetimeField('open_time', required=False)

    class __Meta__:
        table = "Dlc_list"


@register_config
class DlcFbInfoConfig(Config):
    ID = IntegerField("id", key=True)
    type = IntegerField("type")
    # condition_type = IntegerField("condition_type")
    condition = CustomField(
        "condition", decoder=decode_json)
    cd = IntegerField("cd_time")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    first_rewards = CustomField(
        'first_type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    robot_group = IntegerField("rob_group")
    range = CustomField('range', decoder=default_decoder_by('|'))
    rule = IntegerField("rule")
    rob_range = CustomField('rob_range', decoder=default_decoder_by('|'))
    rob_rule = IntegerField("rob_rule")
    dlcID = IntegerField("dlc_id")

    class __Meta__:
        table = "Dlc_FbInfo"


@register_config
class DlcStarPacksByDlcConfig(Config):
    ID = IntegerField("id")
    dlcID = IntegerField("dlc_id", groupkey=True)

    class __Meta__:
        table = "achievement_reward"


@register_config
class DlcStarPacksConfig(Config):
    ID = IntegerField("id", key=True)
    dlcID = IntegerField("dlc_id")
    score = IntegerField("star_num")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "achievement_reward"


@register_config
class DlcTaskConfig(Config):
    ID = IntegerField("id", key=True)
    cd = IntegerField("mission_cd_time")
    gold = IntegerField("clear_mission_gold")
    rewards = CustomField(
        'node_reward',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)  # 节点奖励
    dlcID = IntegerField("dlc_id")
    index = IntegerField("chest_num")

    class __Meta__:
        table = "Dlc_mission"


@register_config
class DlcCampaignByDlcIDConfig(Config):
    ID = IntegerField("id")
    dlcID = IntegerField("dlc_id", groupkey=True)

    class __Meta__:
        table = "Dlc_campaign"


@register_config
class DlcCampaignConfig(Config):

    ID = IntegerField("id", key=True)
    start = DatetimeField("starttime")
    end = DatetimeField("lasttime")
    dlcID = IntegerField("dlc_id")
    task = IntegerField("mission_id")

    class __Meta__:
        table = "Dlc_campaign"


@register_config
class CountDownConfig(Config):
    ID = IntegerField("id")
    gift_png = StringField("gift_png")
    days = IntegerField("cd_time")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    particle_effect = StringField("particle_effect")

    class __Meta__:
        table = "limit_time_gift"


@register_config
class GveFbInfoConfig(Config):
    ID = IntegerField("fb_id", key=True)
    boss_hp = IntegerField("boss_hp")

    class __Meta__:
        table = "gve_FbInfo"


@register_config
class GveSceneInfoByWeekConfig(Config):
    ID = IntegerField("id")
    week = IntegerField("weeks", key=True)

    class __Meta__:
        table = "gve_SceneInfo"


@register_config
class GveSceneInfoConfig(Config):
    ID = IntegerField("id", key=True)
    week = IntegerField("weeks")
    max_damage = IntegerField("maxDamage")
    desc = StringField("desc")
    rewards = CustomField("reward", decoder=validate_rewards_json)
    name = StringField("name")
    background = StringField("background")
    banner = StringField("banner")
    unitsid = IntegerField("unitsid")

    class __Meta__:
        table = "gve_SceneInfo"


@register_config
class GveRankingRewardConfig(Config):
    ID = IntegerField("id", key=True)
    sceneID = IntegerField("Scene_id")
    range = CustomField('ranking', decoder=default_decoder_by('|'))
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "gve_ranking"


@register_config
class GveRankingRewardBySceneIDConfig(Config):
    ID = IntegerField("id")
    sceneID = IntegerField("Scene_id", groupkey=True)

    class __Meta__:
        table = "gve_ranking"


@register_config
class GveDamageRewardConfig(Config):
    ID = IntegerField("id", key=True)
    sceneID = IntegerField("Scene_id")
    damage = IntegerField("damage")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "gve_dpsReward"


@register_config
class GveDamageRewardBySceneConfig(Config):
    sceneID = IntegerField("Scene_id", groupkey=True)
    ID = IntegerField("id")

    class __Meta__:
        table = "gve_dpsReward"


@register_config
class GveCampaignConfig(Config):
    ID = IntegerField("id", key=True)
    start = CustomField("start", decoder=docode_timetime)
    end = CustomField("end", decoder=docode_timetime)

    class __Meta__:
        table = "gve_campaign"


@register_config
class BossCampaignConfig(Config):
    ID = IntegerField("id", key=True)
    start = DatetimeField("start_time")
    end = DatetimeField("end_time")
    desc = StringField("desc")
    fbID = IntegerField("fbid")

    class __Meta__:
        table = "boss_campaign"


@register_config
class MailConfig(Config):
    ID = IntegerField("id", key=True)
    title = StringField("title")
    content = StringField("desc")
    icon_not_read = IntegerField("icon_not_read")
    icon_read = IntegerField("icon_read")
    time = IntegerField("time")

    class __Meta__:
        table = "mail"


@register_config
class FusionPoolConfig(Config):
    ID = IntegerField("id")
    cls = IntegerField("class", groupkey=True)
    prototypeID = IntegerField("unitsid")
    prob = IntegerField("prob")

    class __Meta__:
        table = "fusion_pool"


@register_config
class FusionCostConfig(Config):
    cls = IntegerField("class", key=True)
    type = IntegerField("type")
    cost = IntegerField("cost")

    class __Meta__:
        table = "fusion"


@register_config
class PointAdditionConfig(Config):
    ID = IntegerField("id", key=True)
    point = IntegerField("point")
    type = StringField("pointtype")
    addition = IntegerField("reward")

    class __Meta__:
        table = "missionpoint"


@register_config
class PetLevelOrSkillLevelUpConfig(Config):
    ID = IntegerField("lv", key=True)
    cost = CustomField("units_cost1", decoder=decode_rewards)
    skill1_cost = CustomField("skills_cost1", decoder=decode_rewards)
    skill2_cost = CustomField("skills_cost2", decoder=decode_rewards)
    skill3_cost = CustomField("skills_cost3", decoder=decode_rewards)
    skill4_cost = CustomField("skills_cost4", decoder=decode_rewards)
    skill5_cost = CustomField("skills_cost5", decoder=decode_rewards)
    units_cost1 = CustomField("units_cost1", decoder=decode_rewards)
    units_cost2 = CustomField("units_cost2", decoder=decode_rewards)

    class __Meta__:
        table = "lvup_cost"


@register_config
class NewEquipConfig(Config):
    ID = IntegerField("id", key=True)
    prototypeID = IntegerField("id")
    name = StringField("name")
    type = IntegerField("type")
    init_hp = IntegerField("init_hp")
    init_atk = IntegerField("init_atk")
    init_def = IntegerField("init_def")
    init_cri = IntegerField("init_cri")
    init_dodge = IntegerField("init_dodge")
    gup_id = IntegerField("gup_id")
    icon = IntegerField("icon")
    piece_num = IntegerField("piece_num")
    units_same = IntegerField("units_same")
    desc = StringField("desc")
    enchID = IntegerField("attr_id")
    power = IntegerField("base_eff")

    class __Meta__:
        table = "new_equip"


@register_config
class EquipAdvanceConfig(Config):
    step = IntegerField("step", key=True)
    color = IntegerField("color")
    level = IntegerField("level")
    attr_mul = IntegerField("attr_mul")
    enchant_num = IntegerField("enchant_num")
    money = IntegerField("advanced_cost")

    class __Meta__:
        table = "advanced"


@register_config
class EquipAdvanceCostConfig(Config):
    ID = IntegerField("id", key=True)
    costs = CustomField("gup", repeated=True, decoder=decode_json, range=1)

    class __Meta__:
        table = "equip_gup"


@register_config
class BuySkillpointConfig(Config):
    ID = IntegerField("id", key=True)
    skillpoint = IntegerField("skill_points")
    gold = IntegerField("golden")

    class __Meta__:
        table = "buy_skill"


@register_config
class SwapRuleConfig(Config):
    ID = IntegerField("id", key=True)
    range = CustomField("ranking", decoder=default_decoder_by('|'))
    match_per1 = CustomField("match_percent1", decoder=default_decoder_by('|'))
    match_per2 = CustomField("match_per2", decoder=default_decoder_by('|'))
    match_per3 = CustomField("match_per3", decoder=default_decoder_by('|'))
    monstergroup = IntegerField("monstergroup")

    class __Meta__:
        table = "new_pvp_rule"


@register_config
class SwapRewardConfig(Config):
    ID = IntegerField("id", key=True)
    range = CustomField("ranking", decoder=default_decoder_by('|'))
    title = StringField("title")
    comment = StringField("comment")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "new_pvp_reward"


@register_config
class SwapFightRewardConfig(Config):
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "pvp_fight_reward"


@register_config
class MazeConfig(Config):
    type = IntegerField("event_type")
    argv = FloatField("event_argv")

    class __Meta__:
        table = "maze"


@register_config
class MazeCaseConfig(Config):
    level = IntegerField("openlv")
    drop = IntegerField("chest_drop")
    prob = IntegerField("prob")

    class __Meta__:
        table = "maze_chest"


@register_config
class MazeBossConfig(Config):
    level = IntegerField("openlv")
    boss = IntegerField("fb_id")
    prob = IntegerField("prob")

    class __Meta__:
        table = "maze_boss"


@register_config
class FbDropConfig(Config):
    fbID = IntegerField("id", key=True)
    drop = IntegerField("droppack")
    probs = CustomField(
        u'prandom_prob',
        decoder=default_decoder_vertical_line)

    class __Meta__:
        table = "FbDrop"


class IntimacyConfig(Config):
    # id,intimacy,atk_per,hp_per,def_per,cri,eva,reward
    intimacy = IntegerField("intimacy")
    atk_per = IntegerField("atk_per")
    hp_per = IntegerField("hp_per")
    def_per = IntegerField("def_per")
    cri = IntegerField("cri")
    eva = IntegerField("eva")

    class __Meta__:
        table = "intimacy"


@register_config
class OnlinePacksConfig(Config):
    # id,cd_time,type|itemID|amount1,type|itemID|amount2,type|itemID|amount3,type|itemID|amount4
    ID = IntegerField("id")
    cd = IntegerField("cd_time")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "online_package"


@register_config
class MaxpowerRewardConfig(Config):
    ID = IntegerField("ID", key=True)
    group = IntegerField("group")
    range = CustomField("ranking", decoder=default_decoder_by('|'))

    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "highest_power"


@register_config
class MaxpowerRewardByGroupConfig(Config):
    ID = IntegerField("ID")
    group = IntegerField("group", groupkey=True)

    class __Meta__:
        table = "highest_power"


@register_config
class RefineryConfig(Config):
    cls = IntegerField("class", key=True)
    rewards = CustomField(
        'type|itemid|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    scale = FloatField("scale")

    class __Meta__:
        table = "refinery"


@register_config
class DailyBuyCountConfig(Config):
    count = IntegerField("id", key=True)
    gold = IntegerField("golden")

    class __Meta__:
        table = "buy_dailypvp"


@register_config
class DailyRuleConfig(Config):
    ID = IntegerField("id", key=True)
    range = CustomField('range', decoder=default_decoder_vertical_line)
    score = IntegerField("score")

    class __Meta__:
        table = "pvp_level"


@register_config
class DailyRewardConfig(Config):
    ID = IntegerField("id", key=True)
    range = CustomField('ranking', decoder=default_decoder_vertical_line)
    title = StringField("title")
    comment = StringField("comment")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "dailypvp_reward"


@register_config
class DailyCampaignConfig(Config):
    ID = IntegerField("id", key=True)
    start = DatetimeField("starttime")

    class __Meta__:
        table = "dailypvp_campaign"


@register_config
class SevenConfig(Config):
    ID = IntegerField("missionid", key=True)
    day = IntegerField("daity")
    today = BooleanField("continue_finish")
    tab_desc = StringField("desc")

    class __Meta__:
        table = "start_game_mission"


@register_config
class AmbitionConfig(Config):
    # id,open_level,attr_type
    ID = IntegerField("id", key=True)
    level = IntegerField("open_level")
    attr_type = IntegerField("attr_type")

    class __Meta__:
        table = "ambition"


@register_config
class VipAmbitionConfig(Config):
    # id,open_level,attr_type
    ID = IntegerField("id", key=True)
    level = IntegerField("open_level")
    attr_type = IntegerField("attr_type")

    class __Meta__:
        table = "vip_ambition"


@register_config
class RandomAmbitionConfig(Config):
    # step,atk,def,hp,cri,doge,pro,golden_pro
    step = IntegerField("step", key=True)
    ATK = IntegerField("atk")
    DEF = IntegerField("def")
    HP = IntegerField("hp")
    CRIT = FloatField("cri")
    DODGE = FloatField("doge")
    pro = IntegerField("pro")
    golden_pro = IntegerField("golden_pro")

    class __Meta__:
        table = "random_ambition"


@register_config
class EquipStrengthenConfig(Config):
    # strengthen,level_need,base_addition,success_rate,cost,failed_level
    level = IntegerField("strengthen", key=True)
    need_level = IntegerField("level_need")
    base_addition = IntegerField("base_addition")
    rate = IntegerField("success_rate")
    cost = IntegerField("cost")
    rollback = IntegerField("failed_level")

    class __Meta__:
        table = "equip_strengthen"


@register_config
class RankingCampaignConfig(Config):
    day = IntegerField("id", key=True)
    start = DatetimeField("starttime")
    final = DatetimeField("lasttime")
    ranking = StringField("ranking_list")
    group = IntegerField("ranking_group")
    desc = StringField("ranking_dese")
    title = StringField("mail_dese")

    class __Meta__:
        table = "ranking_campaign"


@register_config
class RankingCampaignRewardConfig(Config):
    # id,ranking,group,type|itemID|amount1,type|itemID|amount2,type|itemID|amount3,type|itemID|amount4,type|itemID|amount5
    id = IntegerField("id", key=True)
    range = CustomField('ranking', decoder=default_decoder_vertical_line)
    group = IntegerField("group")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    rewards2 = CustomField(
        'typea|itemIDa|amounta',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "ranking_reward"


@register_config
class RankingCampaignRewardByGroupConfig(Config):
    id = IntegerField("id")
    group = IntegerField("group", groupkey=True)

    class __Meta__:
        table = "ranking_reward"


@register_config
class DailyRechargeConfig(Config):
    id = IntegerField("ID", key=True)
    group = IntegerField("group")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    gold = IntegerField("gold")
    count = IntegerField("daily_count")

    class __Meta__:
        table = "daily_single_recharge"


@register_config
class DailyRechargeByGroupConfig(Config):
    id = IntegerField("ID")
    group = IntegerField("group", groupkey=True)

    class __Meta__:
        table = "daily_single_recharge"


@register_config
class SwapmaxrankConfig(Config):
    # id,highest_ranking,reward
    id = IntegerField("id", key=True)
    rank = IntegerField("highest_ranking")
    gold = IntegerField("reward")

    class __Meta__:
        table = "swap_top"


@register_config
class RobotNameConfig(Config):
    id = IntegerField("id", key=True)
    name = StringField("name")

    class __Meta__:
        table = "robot_name"


@register_config
class BuySoulConfig(Config):
    id = IntegerField("id", key=True)
    gold = IntegerField("golden")
    soul = IntegerField("soul")

    class __Meta__:
        table = "soul_finger"


@register_config
class DailyWinConfig(Config):
    # id,single_desc,all_desc,multiple,horn,red_paper_count,red_paper,red_paper_desc
    id = IntegerField("id", key=True)
    single_desc = StringField("single_desc")
    all_desc = StringField("all_desc")
    multiple = IntegerField("multiple")
    horn = IntegerField("horn")
    red_paper_count = IntegerField("red_paper_count")
    red_paper = IntegerField("red_paper")
    red_paper_desc = StringField("red_paper_desc")

    class __Meta__:
        table = "dailypvp_win_broadcast"


@register_config
class DailyLoseConfig(Config):
    # id,single_lose_desc,single_win_desc,all_desc,multiple,horn
    id = IntegerField("id", key=True)
    single_lose_desc = StringField("single_lose_desc")
    single_win_desc = StringField("single_win_desc")
    all_desc = StringField("all_desc")
    multiple = IntegerField("multiple")
    horn = IntegerField("horn")

    class __Meta__:
        table = "dailypvp_lose_broadcast"


@register_config
class MatExchangeConfig(Config):
    ID = IntegerField("ID", key=True)
    group = IntegerField("group")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    count = IntegerField("daily_count")

    class __Meta__:
        table = "mat_exchange"


@register_config
class MatExchangeByGroupConfig(Config):
    ID = IntegerField("ID")
    group = IntegerField("group", groupkey=True)

    class __Meta__:
        table = "mat_exchange"


@register_config
class PetExchangeConfig(Config):
    id = IntegerField("ID", key=True)
    cla = IntegerField("class")
    attr = IntegerField("attr")
    units_id = IntegerField("units_id")
    prob = IntegerField("prob")

    class __Meta__:
        table = "pet_exchange_pool"


@register_config
class PetExchangeCostConfig(Config):
    cls = IntegerField("class", key=True)
    type = IntegerField("type")
    cost = IntegerField("cost")

    class __Meta__:
        table = "pet_exchange_cost"


@register_config
class CityCampaignConfig(Config):
    CampaignCityDungeon = 1
    CampaignCityContend = 2

    day = IntegerField("day", groupkey=True)
    type = IntegerField("type")
    start = CustomField("start", decoder=docode_timetime)
    final = CustomField("final", decoder=docode_timetime)

    class __Meta__:
        table = "city_campaign"


@register_config
class CityCampaignGroupByTypeConfig(Config):
    type = IntegerField("type", groupkey=True)

    class __Meta__:
        table = "city_campaign"


@register_config
class CityDungeonMonsterGroupConfig(Config):
    id = IntegerField("id", key=True)
    monster_lv = IntegerField("monster_lv")
    monster_skill_lv = IntegerField("monster_skill_lv")
    monster_star = IntegerField("monster_star")
    monster_id = IntegerField(
        'monster_id',
        repeated=True,
        range=1,
        skipzero=False)
    monster_group_count = IntegerField("monster_group_count")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    must_rewards = CustomField(
        'typea|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "golden_monstergroup"


@register_config
class CityDungeonRewardConfig(Config):
    # id,ranking,type|itemID|amount1,type|itemID|amount2,type|itemID|amount3,type|itemID|amount4
    id = IntegerField("id", key=True)
    range = CustomField('ranking', decoder=default_decoder_vertical_line)
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "first_unions_reward"


@register_config
class CityEventConfig(Config):
    # step,defend_event_type,defend_event_argv,attack_event_type,attack_event_argv
    step = IntegerField("step", key=True)
    defend_event_type = IntegerField("defend_event_type")
    defend_event_argv = IntegerField("defend_event_argv")
    attack_event_type = IntegerField("attack_event_type")
    attack_event_argv = IntegerField("attack_event_argv")

    class __Meta__:
        table = "basis_event"


@register_config
class CityTreasureConfig(Config):
    level = IntegerField("level", key=True)
    attack_treasure = IntegerField("attack_treasure")
    defend_treasure = IntegerField("defend_treasure")

    class __Meta__:
        table = "city_treasure"


@register_config
class CityDungeonMessageConfig(Config):
    id = IntegerField("id", key=True)
    single_lose_desc = StringField("single_lose_desc")
    single_win_desc = StringField("single_win_desc")
    unions_win_desc = StringField("unions_win_desc")
    multiple1 = BooleanField("multiple1")
    horn1 = BooleanField("horn1")
    red_paper_desc = StringField("red_paper_desc")
    multiple2 = BooleanField("multiple2")
    horn2 = BooleanField("horn2")
    red_paper_count = IntegerField("red_paper_count")
    red_paper = IntegerField("red_paper")

    class __Meta__:
        table = "golden_first_broadcast"


@register_config
class CityContendDefendMessageConfig(Config):
    id = IntegerField("id", key=True)
    single_defend_win_desc = StringField("single_defend_win_desc")
    single_defend_lose_desc = StringField("single_defend_lose_dese")
    defend_count_desc = StringField("defend_count_desc")
    multiple1 = BooleanField("multiple1")
    horn1 = BooleanField("horn1")
    red_paper_desc = StringField("red_paper_desc")
    multiple2 = BooleanField("multiple2")
    horn2 = BooleanField("horn2")
    red_paper_count = IntegerField("red_paper_count")
    red_paper = IntegerField("red_paper")

    class __Meta__:
        table = "golden_defend_broadcast"


@register_config
class CityContendAttackMessageConfig(Config):
    id = IntegerField("id", key=True)
    single_attack_win_desc = StringField("single_attack_win_desc")
    single_attack_lose_desc = StringField("single_attack_lose_desc")
    attack_count_desc = StringField("attack_count_desc")
    multiple1 = BooleanField("multiple1")
    horn1 = BooleanField("horn1")
    red_paper_desc = StringField("red_paper_desc")
    multiple2 = BooleanField("multiple2")
    horn2 = BooleanField("horn2")
    red_paper_count = IntegerField("red_paper_count")
    red_paper = IntegerField("red_paper")

    class __Meta__:
        table = "golden_attack_broadcast"


@register_config
class CityTreasureRecvConfig(Config):
    id = IntegerField("id", key=True)
    treasure_count = IntegerField("treasure_count")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "unions_treasure"


@register_config
class ConsumeCampaignByGroupConfig(Config):
    ID = IntegerField("ID")
    group = IntegerField("group", groupkey=True)

    class __Meta__:
        table = "acc_consume"


@register_config
class ConsumeCampaignConfig(Config):
    ID = IntegerField("ID", key=True)
    consume = IntegerField("consume")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    group = IntegerField("group")

    class __Meta__:
        table = "acc_consume"


@register_config
class LoginCampaignByGroupConfig(Config):
    ID = IntegerField("ID")
    group = IntegerField("group", groupkey=True)

    class __Meta__:
        table = "acc_login"


@register_config
class LoginCampaignConfig(Config):
    ID = IntegerField("ID", key=True)
    day = IntegerField("acc_login")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    group = IntegerField("group")

    class __Meta__:
        table = "acc_login"


@register_config
class ResetRechargesConfig(Config):
    times = IntegerField("times")

    class __Meta__:
        table = "reset_recharges"


@register_config
class EquRefineConfig(Config):
    ID = IntegerField("id", key=True)
    equ_rewards = CustomField(
        'equip_reward',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    mat_rewards = CustomField(
        'mat_reward',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "base_refinery"


@register_config
class PowerPacksConfig(Config):
    id = IntegerField("id", key=True)
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "efficiency_reward"


@register_config
class HotLotteryCampaignConfig(Config):
    group = IntegerField('group', groupkey=True)
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    prob = IntegerField("prob")

    class __Meta__:
        table = "hot_pet"


@register_config
class ExchangeCampaignByGroupConfig(Config):
    group = IntegerField("group", key=True)
    srcID = IntegerField("old_monster_id")
    targetID = IntegerField("new_monster_id")
    consumes = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    bg = StringField("bg")
    refresh_counts = CustomField('renovate_count', decoder=default_decoder_vertical_line)
    # refresh_counts = map(int, StringField("renovate_count").split('|'))

    class __Meta__:
        table = "monster_exchange"


@register_config
class RefreshStoreByGroupConfig(Config):
    ID = IntegerField("ID")
    group = IntegerField("group", groupkey=True)

    class __Meta__:
        table = "refresh_campaign"


@register_config
class RefreshStoreConfig(Config):
    ID = IntegerField("ID", key=True)
    group = IntegerField("group")
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    count = IntegerField("count")

    class __Meta__:
        table = "refresh_campaign"


@register_config
class ArborDayConfig(Config):
    ID = IntegerField("id", key=True)
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "yaoyiyao"


@register_config
class ArborDayYYYProbConfig(Config):
    def decode_prob(self, v, lineno=None):
        if v in (0, '0', ''):
            return []
        try:
            ret = map(int, v.split('|'))
        except ValueError as e:
            raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (
                lineno, self.column_name, self.name, str(e), repr(v)))
        return ret

    ID = IntegerField("id", key=True)
    free_probs = CustomField('free_random', decoder=decode_prob)
    pay_probs = CustomField('golden_random', decoder=decode_prob)

    class __Meta__:
        table = "yaoyiyao_random"


@register_config
class SeedConfig(Config):
    def decode_time(self, v, lineno=None):
        if v in (0, '0', ''):
            return []
        try:
            ret = map(int, v.split('|'))
        except ValueError as e:
            raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (
                lineno, self.column_name, self.name, str(e), repr(v)))
        return ret

    seed_id = IntegerField("seed_id", key=True)
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)
    times = CustomField('time', decoder=decode_time)

    class __Meta__:
        table = "plant"


@register_config
class SealSeedConfig(Config):
    def decode_prob(self, v, lineno=None):
        if v in (0, '0', ''):
            return []
        try:
            ret = map(int, v.split('|'))
        except ValueError as e:
            raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (
                lineno, self.column_name, self.name, str(e), repr(v)))
        return ret

    ID = IntegerField("id", key=True)
    probs = CustomField('random', decoder=decode_prob)

    class __Meta__:
        table = "seeling_seed"


@register_config
class ClimbTowerConfig(Config):
    ID = IntegerField("ID", key=True)
    limit = IntegerField("limit")
    description = StringField('description')
    zombie_id = CustomField(u'zombie_id', decoder=lambda s, v, _: -int(v))
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "climb_tower"

    @classmethod
    def post_validation(cls, alldata):
        configs = alldata[cls.__name__]
        zombies = alldata[PvpGroupConfig.__name__]
        error = u"{} 中 {} 为 {}， 不存在于 {} 中。"
        for id, config in configs.items():
            if config["zombie_id"] and config["zombie_id"] not in zombies:
                col = cls.fields["zombie_id"]
                error = error.format(
                    cls.__Meta__.table,
                    col.column_name,
                    config["zombie_id"],
                    PvpGroupConfig.__Meta__.table)
                raise ValidationError(error)


@register_config
class ClimbTowerAccreditConfig(Config):
    floor = IntegerField("floor", key=True)
    limit = IntegerField("limit")
    earnings = CustomField(
        'pitch_time',
        required=True,
        decoder=default_decoder_vertical_line)
    zombie_id = CustomField(u'zombie_id', decoder=lambda s, v, _: -int(v))
    tip = CustomField(
        'tip',
        required=True,
        decoder=default_decoder_vertical_line)
    top_limit = IntegerField("top_limit")
    unlock = IntegerField('unlock')

    class __Meta__:
        table = "climb_tower_accredit"

    @classmethod
    def post_validation(cls, alldata):
        configs = alldata[cls.__name__]
        zombies = alldata[PvpGroupConfig.__name__]
        error = u"{} 中 {} 为 {}， 不存在于 {} 中。"
        for id, config in configs.items():
            if config["zombie_id"] and config["zombie_id"] not in zombies:
                col = cls.fields["zombie_id"]
                error = error.format(
                    cls.__Meta__.table,
                    col.column_name,
                    config["zombie_id"],
                    PvpGroupConfig.__Meta__.table)
                raise ValidationError(error)


@register_config
class ClimbTowerChestConfig(Config):
    floor = IntegerField("floor", key=True)
    rewards = CustomField(
        'type|itemID|amount',
        repeated=True,
        range=1,
        decoder=decode_rewards,
        skipzero=True)

    class __Meta__:
        table = "climb_tower_chests"


@register_config
class GemConfig(Config):
    ID = IntegerField("id", key=True)
    kind = IntegerField("type")
    phase = IntegerField("step")
    gupr = IntegerField("gupr")
    icon = IntegerField("icon")
    atk = IntegerField("atk")
    hp = IntegerField("hp")
    defend = IntegerField("def")
    compose_consume = IntegerField("compose_need_num")

    class __Meta__:
        table = "gem"


@register_config
class GemRefineConfig(Config):
    refine_lv = IntegerField("refining_lv", key=True)
    gem_lv = IntegerField("gem_lv_limit")
    cost = IntegerField("cost")
    cost_type = IntegerField("cost_type")
    color = IntegerField("color")
    step = IntegerField("step")

    class __Meta__:
        table = "refining"


@register_config
class PlayerRefineConfig(Config):
    kind = IntegerField("type", key=True)
    gem_group = CustomField("gem_group",
                            required=True,
                            decoder=default_decoder_vertical_line)

    class __Meta__:
        table = "player_equip"


@register_config
class HandselConfig(Config):
    def decode_cost(self, v, lineno=None):
        if v in (0, '0', ''):
            return []
        try:
            ret = map(int, v.split('|'))
        except ValueError as e:
            raise ValidationError(u'在第 %s 行，字段 %s(%s) 格式错误: %s(%s)' % (
                lineno, self.column_name, self.name, str(e), repr(v)))
        return ret

    ID = IntegerField("id", key=True)
    group = IntegerField("group")
    cost_type = CustomField('cost_type', decoder=decode_cost)
    camp_count = IntegerField("fnum")
    tips = StringField("tips")

    class __Meta__:
        table = "gift_flowers"


@register_config
class HandselGroupConfig(Config):
    ID = IntegerField("id")
    group = IntegerField("group", groupkey=True)

    class __Meta__:
        table = "gift_flowers"


@register_config
class HandselMulRewardConfig(Config):
    ID = IntegerField("id", key=True)
    next_id = IntegerField("next")
    group = IntegerField("group")
    need_count = IntegerField("need_num")
    mulreward = FloatField("multiple")

    class __Meta__:
        table = "gift_goal"


@register_config
class HandselMulRewardGroupConfig(Config):
    ID = IntegerField("id")
    group = IntegerField("group", groupkey=True)

    class __Meta__:
        table = "gift_goal"


@register_config
class HandselHonorConfig(Config):
    ID = IntegerField("id", key=True)
    camp_id = StringField("campaignid")
    point = IntegerField("planvalue")
    type1 = StringField("pointtype1")
    addition1 = IntegerField("reward1")
    type2 = StringField("pointtype2")
    addition2 = IntegerField("reward2")

    class __Meta__:
        table = "glory"
