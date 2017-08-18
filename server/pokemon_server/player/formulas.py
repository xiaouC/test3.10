# coding: utf-8
'''
公式计算
'''
import ujson
import math
import logging
logger = logging.getLogger('entity')
from datetime import datetime, timedelta
from yy.entity.formulas import register_formula


def get_vip_value(vip, key):
    from config.configs import get_config, VipConfig
    configs = get_config(VipConfig)
    config = configs.get(vip)
    if not config:
        return 0
    return getattr(config, key)


def get_open_vip(key):
    from config.configs import get_config, VipConfig
    configs = get_config(VipConfig)
    for vip, config in configs.items():
        value = getattr(config, key)
        if value:
            break
    return vip


def get_level_value(level, key):
    from config.configs import get_config, LevelupConfig
    configs = get_config(LevelupConfig)
    config = configs.get(level)
    if not config:
        return 0
    return getattr(config, key)


def get_open_level(key):
    from config.configs import get_config, LevelupConfig
    configs = get_config(LevelupConfig)
    for level, config in configs.items():
        value = getattr(config, key)
        if value:
            break
    return level


@register_formula
def get_max_exp(level):
    from config.configs import LevelupConfig, get_config
    configs = get_config(LevelupConfig)
    config = configs.get(level + 1)
    if not config:
        return 0
    return config.exp


@register_formula
def get_next_exp(level):
    return get_max_exp(max(level - 1, 1))


@register_formula
def get_totalloginlen(totalloginreward_getedset):
    from config.configs import get_config, LoginRewardConfig
    items = get_config(LoginRewardConfig)
    # 读配置表获得最大的的累计登陆天数
    maxday = max(map(lambda s: s.loginday, items.values()))
    if maxday == len(totalloginreward_getedset):
        return len(totalloginreward_getedset) + 1
    else:
        return len(totalloginreward_getedset)


@register_formula
def get_serialloginlen(serialloginreward_getset):
    return len(serialloginreward_getset)


@register_formula
def get_newmailcount(mails):
    ret = 0
    for m in mails.values():
        if not m.isread:
            ret += 1
    return ret


@register_formula
def get_pvp_start_time(pvpopenflag):
    from pvp.rank import g_rankManager
    st, _, _ = g_rankManager.get_current()
    return st


@register_formula
def get_pvp_final_time(pvpopenflag):
    from pvp.rank import g_rankManager
    _, ed, _ = g_rankManager.get_current()
    return ed


@register_formula
def get_daily_start_time():
    from campaign.manager import g_campaignManager
    camp = g_campaignManager.dailypvp_campaign
    return camp.get_start_time()


@register_formula
def get_daily_final_time():
    from campaign.manager import g_campaignManager
    camp = g_campaignManager.dailypvp_campaign
    return camp.get_final_time()


@register_formula
def get_pvp_is_open(pvpopenflag):
    from pvp.rank import g_rankManager
    return g_rankManager.is_open()


def get_lottery_cost(type):
    from config.configs import get_config, LotteryFunctionConfig
    config = get_config(LotteryFunctionConfig).get(type)
    if not config:
        return 0
    return config.Price


@register_formula
def get_loterry_hero_cost_A():
    from mall.constants import LotteryType
    return get_lottery_cost(LotteryType.Lottery1)


@register_formula
def get_loterry_hero_cost_B():
    from mall.constants import LotteryType
    return get_lottery_cost(LotteryType.Lottery2)


@register_formula
def get_loterry_hero_cost_C():
    from mall.constants import LotteryType
    return get_lottery_cost(LotteryType.Lottery3)


@register_formula
def get_loterry_hero_cost_D():
    from mall.constants import LotteryType
    return get_lottery_cost(LotteryType.Lottery4)


def get_lottery_rest_count(type, used):
    from config.configs import get_config, LotteryFunctionConfig
    config = get_config(LotteryFunctionConfig).get(type)
    if not config:
        return 0
    return max(config.FreeTimes - used, 0)


@register_formula
def get_loterry_hero_rest_free_count_A(used):
    from mall.constants import LotteryType
    return get_lottery_rest_count(LotteryType.Lottery1, used)


@register_formula
def get_loterry_hero_rest_free_count_B(used):
    from mall.constants import LotteryType
    return get_lottery_rest_count(LotteryType.Lottery2, used)


@register_formula
def get_loterry_hero_rest_free_count_C(used):
    from mall.constants import LotteryType
    return get_lottery_rest_count(LotteryType.Lottery3, used)


@register_formula
def get_loterry_hero_rest_free_count_D(used):
    from mall.constants import LotteryType
    return get_lottery_rest_count(LotteryType.Lottery4, used)


@register_formula
def get_invite_faction_count(inviteFactionSet):
    return len(inviteFactionSet)


@register_formula
def get_apply_member_count(applyMemberSet):
    return len(applyMemberSet)


@register_formula
def get_vip_buy_sp_rest_count(vip, buy_sp_used_count):
    value = get_vip_value(vip, 'buy_sp_count')
    return max(value - buy_sp_used_count, 0)


@register_formula
def get_buy_sp_cost(buy_sp_used_count):
    from config.configs import get_config, BuySpCostConfig
    configs = get_config(BuySpCostConfig)
    config = configs.get(buy_sp_used_count+1)
    if not config:
        config = configs[max(configs)]
    return config.cost


@register_formula
def get_slatelen(slatereward_getedset):
    return len(slatereward_getedset)


@register_formula
def get_vip(credits):
    from config.configs import get_config, VipConfig
    configs = get_config(VipConfig)
    for k, v in configs.items()[::-1]:
        if credits >= v.amount:
            return k
    return min(configs)


@register_formula
def get_vip_refresh_fb_max_count(vip):
    return get_vip_value(vip, 'buy_advanced_fb_count')


@register_formula
def get_task_today_is_sign_up(task_last_sign_up_time):
    from datetime import date
    if not task_last_sign_up_time:
        return False
    last = date.fromtimestamp(task_last_sign_up_time)
    return date.today() == last


def get_taskrewardscount(taskrewards, type, subtype=None):
    from task.constants import TaskType
    from config.configs import get_config
    from config.configs import TaskConfig
    from config.configs import TaskByGroupConfig
    rs = []
    configs = get_config(TaskConfig)
    if type == TaskType.Daily:
        types = [TaskType.Daily, TaskType.Faction]
    else:
        types = [type]
    for i in taskrewards:
        config = configs.get(i)
        if not config or (subtype and config.subtype != subtype):
            continue
        if config.type in types:
            group = get_config(TaskByGroupConfig)[config.groupID]
            if config.type == TaskType.Noob:
                if all([i.ID in taskrewards for i in group]):
                    rs.append(config.groupID)
            else:
                rs.append(config.groupID)
    if type != TaskType.Normal:
        rs = set(rs)
    return len(rs)


@register_formula
def get_taskrewardscount1(taskrewards, task_sp_daily_receiveds):
    from task.constants import TaskType
    # 领能量改为化缘
    # from protocol.poem_pb import Task
    # from task.manager import _get_daily_sp_tasks
    # daily_sp_tasks = _get_daily_sp_tasks(task_sp_daily_receiveds)
    # daily_sp_count = len(filter(lambda s:s.get('state') == Task.Done, daily_sp_tasks))
    return get_taskrewardscount(taskrewards, TaskType.Daily)  # + daily_sp_count


@register_formula
def get_taskrewardscountsubtype1(taskrewards):
    from task.constants import TaskType
    from task.constants import TaskSubType
    return get_taskrewardscount(taskrewards, TaskType.Normal, TaskSubType.Growth)


@register_formula
def get_taskrewardscountsubtype2(taskrewards):
    from task.constants import TaskType
    from task.constants import TaskSubType
    return get_taskrewardscount(taskrewards, TaskType.Normal, TaskSubType.Resource)


@register_formula
def get_taskrewardscountsubtype3(taskrewards):
    from task.constants import TaskType
    from task.constants import TaskSubType
    return get_taskrewardscount(taskrewards, TaskType.Normal, TaskSubType.Team)


@register_formula
def get_taskrewardscountsubtype4(taskrewards):
    from task.constants import TaskType
    from task.constants import TaskSubType
    return get_taskrewardscount(taskrewards, TaskType.Normal, TaskSubType.Battle)


@register_formula
def get_beg_flag(taskrewards, task_sp_daily_receiveds):
    from protocol.poem_pb import Task
    from task.manager import _get_daily_sp_tasks
    daily_sp_tasks = _get_daily_sp_tasks(task_sp_daily_receiveds)
    return any(s.get('state') == Task.Done for s in daily_sp_tasks)


@register_formula
def get_taskrewardscount2(taskrewards):
    from task.constants import TaskType
    return get_taskrewardscount(taskrewards, TaskType.Normal)


@register_formula
def get_taskrewardscount3(taskrewards):
    from task.constants import TaskType
    return get_taskrewardscount(taskrewards, TaskType.Achieve)


@register_formula
def get_taskrewardscount4(taskrewards):
    from task.constants import TaskType
    return get_taskrewardscount(taskrewards, TaskType.Sign)


@register_formula
def get_taskrewardscount5(taskrewards):
    from task.constants import TaskType
    return get_taskrewardscount(taskrewards, TaskType.Noob)


@register_formula
def get_taskrewardscount6(taskrewards):
    from task.constants import TaskType
    return get_taskrewardscount(taskrewards, TaskType.Faction)


@register_formula
def get_taskrewardscount7(taskrewards):
    from task.constants import TaskType
    return get_taskrewardscount(taskrewards, TaskType.Trigger)


@register_formula
def get_taskrewardscount12(taskrewards):
    from task.constants import TaskType
    return get_taskrewardscount(taskrewards, TaskType.DailyPVP)


@register_formula
def get_taskrewardscount13(taskrewards):
    from task.constants import TaskType
    return get_taskrewardscount(taskrewards, TaskType.Seven)


@register_formula
def get_taskrewardscount14(taskrewards):
    from task.constants import TaskType
    return get_taskrewardscount(taskrewards, TaskType.Progress)


@register_formula
def get_taskrewardsdone14(entityID, tasks, taskrewards):
    from datetime import date
    from task.manager import is_done
    from task.constants import TaskType
    from entity.manager import g_entityManager
    from config.configs import get_config, TaskConfig
    p = g_entityManager.get_player(entityID)
    if not p:
        return 0
    count = 0
    today = date.today()
    configs = get_config(TaskConfig)
    for k, v in tasks.items():
        config = configs.get(k)
        if not config:
            continue
        if config.type == TaskType.Progress:
            if is_done(p, config.ID, today) \
                    and config.prev not in taskrewards:
                count += 1
    return count


@register_formula
def get_taskrewardscountnew(taskrewards):
    # 领取能量任务已经加入到化缘中，所以这里不判断领取能量任务
    from config.configs import get_config, TaskConfig
    count = 0
    configs = get_config(TaskConfig)
    for i in taskrewards:
        config = configs.get(i)
        if not config:
            continue
        if config.push:
            count += 1
    return count


@register_formula
def get_task_noob_flag(entityID, taskrewards):
    from task.manager import get_plan
    from task.manager import get_sorted_noob_group
    from entity.manager import g_entityManager
    from config.configs import TaskByGroupConfig
    from config.configs import get_config
    from config.configs import TaskConfig
    from datetime import date
    p = g_entityManager.get_player(entityID)
    configs = get_config(TaskConfig)
    if p:
        today = date.today()
        for g in get_sorted_noob_group():
            group = get_config(TaskByGroupConfig).get(g)
            for task in group:
                task = configs.get(task.ID)
                if not task:
                    continue
                if get_plan(p, task.ID, today) < task.goal:
                    return True
                if task.ID in taskrewards:
                    return True
    return False


@register_formula
def get_task_noob_undo(entityID, taskrewards):
    from task.manager import is_done
    from task.manager import get_current_day
    from task.manager import get_sorted_noob_group
    from config.configs import get_config
    from config.configs import TaskByGroupConfig
    from entity.manager import g_entityManager
    from datetime import date
    p = g_entityManager.get_player(entityID)
    if not p:
        return False
    day, _ = get_current_day(p)
    try:
        group = get_sorted_noob_group()[day-1]
    except IndexError:
        return False
    group = get_config(TaskByGroupConfig).get(group)
    if not group:
        return False
    today = date.today()
    return not all([is_done(p, i.ID, today) for i in group])


@register_formula
def resolvegold_level():
    from config.configs import get_config, GoldFingerLvLimitConfig
    resolvegold = get_config(GoldFingerLvLimitConfig)[1]
    return resolvegold.openlv


@register_formula
def get_mine_rob_max_count(vip):
    from config.configs import get_config, VipConfig
    vipcfg = get_config(VipConfig)[vip]
    return vipcfg.rob_max_count


@register_formula
def get_past_time(t):
    if not t:
        return 9999
    import time
    n = int(time.time())
    return n - t


@register_formula
def get_mine_level(t, level):
    from protocol import poem_pb
    from config.configs import get_config, LevelupConfig
    configs = get_config(LevelupConfig)
    try:
        config = configs[level]
    except KeyError:
        config = configs[max(configs)]
    if t == poem_pb.MineType1:
        return config.mine1
    elif t == poem_pb.MineType2:
        return config.mine2
    return 0


@register_formula
def get_mine_safety(t, mine_level):
    from protocol import poem_pb
    from config.configs import get_config, MineConfig
    config = get_config(MineConfig).get(mine_level)
    if not config:
        return 0
    if t == poem_pb.MineType1:
        return config.mine_safety1
    elif t == poem_pb.MineType2:
        return config.mine_safety2
    return 0


@register_formula
def get_mine_maximum(t, mine_level):
    from protocol import poem_pb
    from config.configs import get_config, MineConfig
    config = get_config(MineConfig).get(mine_level)
    if not config:
        return 0
    if t == poem_pb.MineType1:
        return config.mine_maximum1
    elif t == poem_pb.MineType2:
        return config.mine_maximum2
    return 0


@register_formula
def get_uproar_refresh_max_count(vip):
    from config.configs import get_config, VipConfig
    vipcfg = get_config(VipConfig)[vip]
    return vipcfg.uproar_count


@register_formula
def get_uproar_last_target(uproar_targets_done):
    if not uproar_targets_done:
        return 0
    return max(uproar_targets_done)


@register_formula
def get_uproar_last_chest(uproar_chests_done):
    if not uproar_chests_done:
        return 0
    return max(uproar_chests_done)


@register_formula
def get_level_packs_flag(level_packs_done, level_packs_end):
    from config.configs import get_config, LevelPacksConfig
    configs = get_config(LevelPacksConfig)
    if level_packs_done:
        return True
    return len(configs) != len(level_packs_end)


@register_formula
def get_power_packs_flag(power_packs_done, power_packs_end):
    from config.configs import get_config, PowerPacksConfig
    configs = get_config(PowerPacksConfig)
    if power_packs_done:
        return True
    return len(configs) != len(power_packs_end)


@register_formula
def get_totallogin_flag(totallogin_end):
    from config.configs import get_config, LoginRewardConfig
    configs = get_config(LoginRewardConfig)
    return len(configs) != len(totallogin_end)


@register_formula
def get_faction_hp(level):
    from config.configs import get_config, FactionStrengthenConfig
    configs = get_config(FactionStrengthenConfig)
    info = configs.get(level)
    if not info:
        return 0
    return info.HP


@register_formula
def get_faction_atk(level):
    from config.configs import get_config, FactionStrengthenConfig
    configs = get_config(FactionStrengthenConfig)
    info = configs.get(level)
    if not info:
        return 0
    return info.ATK


@register_formula
def get_faction_def(level):
    from config.configs import get_config, FactionStrengthenConfig
    configs = get_config(FactionStrengthenConfig)
    info = configs.get(level)
    if not info:
        return 0
    return info.DEF


@register_formula
def get_faction_crit(level):
    from config.configs import get_config, FactionStrengthenConfig
    configs = get_config(FactionStrengthenConfig)
    info = configs.get(level)
    if not info:
        return 0.0
    return info.CRI


def hp2power(HP):
    return HP / float(5)


def atk2power(ATK):
    return ATK


def def2power(DEF):
    return DEF * 2


def cri2power(CRI):
    return CRI * 15


def eva2power(EVA):
    return EVA * 25


@register_formula
def get_faction_power(
        factionHP,
        factionATK,
        factionDEF,
        factionCRI,
        factionEVA):
    result = hp2power(factionHP)
    result += atk2power(factionATK)
    result += def2power(factionDEF)
    result += cri2power(factionCRI)
    result += eva2power(factionEVA)
    return result


@register_formula
def get_power(
        entityID,
        base_power,
        equip_power,
        faction_power,
        ambition_power,
        point_power,
        gems_power,
        honor_power):
    from player.model import PlayerPowerRanking
    from lineup.constants import LineupType
    from entity.manager import g_entityManager
    self = g_entityManager.get_player(entityID)
    if not self:
        return 0
    count = len(filter(lambda s: s, self.lineups.get(LineupType.ATK, [])))
    power = base_power + \
        equip_power + \
        point_power + \
        gems_power + \
        honor_power + \
        faction_power * count + \
        ambition_power * count
    PlayerPowerRanking.update_score(entityID, power)
    from lineup.constants import LineupType
    from entity.utils import get_pet_total_power
    self.power_cache = power
    # 记录最高战力的精灵
    lineup = self.lineups.get(LineupType.ATK, [])
    for each in lineup:
        pet = self.pets.get(each)
        if not pet:
            continue
        pet_power = get_pet_total_power(self, pet)
        if pet_power > self.ranking_pet_power:
            self.ranking_pet_power = pet_power
            self.ranking_pet_power_entityID = pet.entityID
            self.ranking_pet_power_prototypeID = pet.prototypeID
            self.ranking_pet_power_breaklevel = pet.breaklevel
    if not self:
        return 0
    if power > self.max_power:
        self.max_power = power
        from entity.manager import check_power_packs
        check_power_packs(self)
        from player.model import PlayerMaxPowerRanking
        PlayerMaxPowerRanking.update_score(entityID, power)
        self.save()

    # from yy.message.header import fail_msg
    # import protocol.poem_pb as msgid
    # from player.manager import g_playerManager
    # g_playerManager.sendto(
    #     entityID, fail_msg(msgid.TOAST, reason="战斗力: %d" % power)
    # )
    return math.floor(power)


@register_formula
def get_equip_power(entityID, lineups):
    from config.configs import get_config
    from config.configs import NewEquipConfig
    from config.configs import PetConfig
    from entity.manager import g_entityManager
    from lineup.constants import LineupType
    from equip.formulas import get_equip_base_value
    from equip.constants import EquipType
    self = g_entityManager.get_player(entityID)
    if not self:
        return 0
    equip_configs = get_config(NewEquipConfig)
    pet_configs = get_config(PetConfig)
    lineup = self.lineups.get(LineupType.ATK, [])
    pets = [self.pets[i] for i in lineup if i]
    result = 0
    attrs = ["hp", "atk", "def", "cri", "dodge"]
    for pet in pets:
        pet_info = pet_configs.get(pet.prototypeID)
        if not pet_info:
            continue
        power = 0
        for type, equip_prototypeID in enumerate(
                [pet_info.excl_equip] + pet_info.equips):
            if type == 0:  # 专属装备
                type = EquipType.FaBao
                initial = False  # 不初始化
            else:
                initial = True
            if not equip_prototypeID:
                continue
            if type not in pet.equipeds and initial:
                equip_info = equip_configs.get(equip_prototypeID)
                if not equip_info:
                    continue
                equip_power = 0
                for tag in attrs:
                    value = get_equip_base_value(
                        equip_prototypeID, 0, 1, tag)
                    equip_power += {
                        "hp": hp2power,
                        "atk": atk2power,
                        "def": def2power,
                        "cri": cri2power,
                        "dodge": eva2power,
                    }[tag](value)
            else:
                e = pet.equipeds.get(type)
                if not e:
                    continue
                equip = self.equips.get(e)
                if not equip:
                    continue
                equip_power = equip.base_power
            power += equip_power
        result += power
    return result


@register_formula
def get_base_power(entityID, lineups):
    from entity.manager import g_entityManager
    self = g_entityManager.get_player(entityID)
    from lineup.constants import LineupType
    if not self:  # player offline
        return 0
    lineup = self.lineups.get(LineupType.ATK, [])
    pets = [self.pets[i] for i in lineup if i]
    base_power = sum(i.base_power for i in pets)
    return base_power


@register_formula
def get_first_recharge_recv(bought_recharges, first_recharge_flag):
    return bool(bought_recharges) and first_recharge_flag


@register_formula
def get_limited_packs_flag():
    import time
    from config.configs import get_config, LimitedPacksConfig
    now = int(time.time())
    times = get_config(LimitedPacksConfig)
    for t in times:
        if t.start < now and t.end >= now:
            return True
    return False


@register_formula
def get_limited_packs_rest_count(limited_packs_used_count):
    import time
    from config.configs import get_config, LimitedPacksConfig
    now = int(time.time())
    times = get_config(LimitedPacksConfig)
    for t in times:
        if t.start < now and t.end >= now:
            return max(t.count - limited_packs_used_count, 0)
    return 0


@register_formula
def get_timelimited_packs_rest_time():
    import time
    from config.configs import get_config
    from config.configs import TimeLimitedPacksConfig
    times = get_config(TimeLimitedPacksConfig)
    now = int(time.time())
    for t in times:
        if t.start < now and t.end >= now:
            return t.end - now
    return 0


@register_formula
def get_timelimited_packs_rest_count(timelimited_packs_last_time):
    import time
    from config.configs import get_config
    from config.configs import TimeLimitedPacksConfig
    times = get_config(TimeLimitedPacksConfig)
    ts = timelimited_packs_last_time
    now = int(time.time())
    for t in times:
        if t.start < now and t.end >= now:
            if t.start > ts or t.end <= ts:
                return 1
            else:
                return 0
    return 0


@register_formula
def get_rank_reset_rest_count(vip, rank_reset_used_count):
    reset_max_count = get_vip_value(vip, "pvp_reset_count")
    return max(reset_max_count - rank_reset_used_count, 0)


@register_formula
def get_rank_reset_cost(rank_reset_used_count):
    from config.configs import get_config
    from config.configs import PvpResetConfig
    configs = get_config(PvpResetConfig)
    config = configs.get(rank_reset_used_count + 1)
    if not config:
        config = configs[max(configs)]
    return config.gold


@register_formula
def get_rank_refresh_cost(rank_refresh_used_count):
    from config.configs import get_config
    from config.configs import PvpRefreshConfig
    configs = get_config(PvpRefreshConfig)
    config = configs.get(rank_refresh_used_count + 1)
    if not config:
        config = configs[max(configs)]
    return config.gold


@register_formula
def get_friend_max_count(level):
    return get_level_value(level, "friends_num")


@register_formula
def get_treasure_max_count(vip):
    return get_vip_value(vip, "treasure_max_count")


@register_formula
def get_treasure_chest_gold(type):
    from config.configs import get_config
    from config.configs import TreasureChestConfig
    config = get_config(TreasureChestConfig).get(type)
    if not config:
        return 0
    return config.gold


@register_formula
def get_friend_gift_max_count(level):
    return get_level_value(level, "gift_num")


@register_formula
def get_todayfp_sp_max():
    from config.configs import get_cons_value
    return get_cons_value("FactionSpDonateLimited")


@register_formula
def get_todayfp_donate_max():
    from config.configs import get_cons_value
    return get_cons_value("FactionDonateLimited")


@register_formula
def get_faction_level_rewards_count(
        faction_level_rewards_received, faction_level):
    return int(not faction_level_rewards_received)


@register_formula
def get_mall_golden_open_vip():
    return get_open_vip("golden_king_shop")


@register_formula
def get_mall_golden_open_cost(vip, level, mall_golden_opened):
    from config.configs import get_cons_value
    if get_vip_value(vip, "golden_king_shop") and\
            get_level_value(level, "goldenstore") and\
            not mall_golden_opened:
        return get_cons_value("OpenGoldenMallCost")
    return 0


@register_formula
def get_mall_silver_open_vip():
    return get_open_vip("silver_king_shop")


@register_formula
def get_mall_silver_open_cost(vip, level, mall_silver_opened):
    from config.configs import get_cons_value
    if get_vip_value(vip, "silver_king_shop") and\
            get_level_value(level, "sliverstore") and\
            not mall_silver_opened:
        return get_cons_value("OpenSilverMallCost")
    return 0


@register_formula
def get_tap_onekey(vip):
    from config.configs import get_cons_value
    return get_cons_value("TapOnekeyVipLevel")


@register_formula
def get_clean_campaign_vip(vip):
    from config.configs import get_cons_value
    return get_cons_value("CanCleanCampaignfbVipLevel")


@register_formula
def get_friendfb_remain_count(friendfb_used_count):
    from config.configs import get_cons_value
    return max(
        get_cons_value("FriendfbBeInvitedCount") - friendfb_used_count, 0)


@register_formula
def get_wish_remain_time():
    from campaign.manager import g_campaignManager
    if not g_campaignManager.wish_campaign.is_open():
        return 0
    return g_campaignManager.wish_campaign.get_end_time()


@register_formula
def get_wish_rest_count(wish_used_count):
    from config.configs import get_cons_value
    return max(get_cons_value("WishMaxCount") - wish_used_count, 0)


@register_formula
def get_daily_acc_recharge_remain_time():
    from campaign.manager import g_campaignManager
    if not g_campaignManager.daily_acc_recharge_campaign.is_open():
        return 0
    return g_campaignManager.daily_acc_recharge_campaign.get_end_time()


@register_formula
def get_daily_acc_recharge_can_receive(daily_acc_recharge_rewards):
    from campaign.manager import g_campaignManager
    if not g_campaignManager.daily_acc_recharge_campaign.is_open():
        return False
    return bool(daily_acc_recharge_rewards)


@register_formula
def get_daily_recharge_remain_time():
    from campaign.manager import g_campaignManager
    if not g_campaignManager.daily_recharge_campaign.is_open():
        return 0
    return g_campaignManager.daily_recharge_campaign.get_end_time()


@register_formula
def get_cycle_acc_recharge_remain_time():
    from campaign.manager import g_campaignManager
    if not g_campaignManager.cycle_acc_recharge_campaign.is_open():
        return 0
    return g_campaignManager.cycle_acc_recharge_campaign.get_end_time()


@register_formula
def get_cycle_acc_recharge_can_receive(cycle_acc_recharge_rewards):
    from campaign.manager import g_campaignManager
    if not g_campaignManager.cycle_acc_recharge_campaign.is_open():
        return False
    return bool(cycle_acc_recharge_rewards)


@register_formula
def get_weeks_acc_recharge_remain_time():
    from campaign.manager import g_campaignManager
    if not g_campaignManager.weeks_acc_recharge_campaign.is_open():
        return 0
    return g_campaignManager.weeks_acc_recharge_campaign.get_end_time()


@register_formula
def get_weeks_acc_recharge_can_receive(weeks_acc_recharge_rewards):
    from campaign.manager import g_campaignManager
    if not g_campaignManager.weeks_acc_recharge_campaign.is_open():
        return False
    return bool(weeks_acc_recharge_rewards)


@register_formula
def get_month_acc_recharge_remain_time():
    from campaign.manager import g_campaignManager
    if not g_campaignManager.month_acc_recharge_campaign.is_open():
        return 0
    return g_campaignManager.month_acc_recharge_campaign.get_end_time()


@register_formula
def get_month_acc_recharge_can_receive(month_acc_recharge_rewards):
    from campaign.manager import g_campaignManager
    if not g_campaignManager.month_acc_recharge_campaign.is_open():
        return False
    return bool(month_acc_recharge_rewards)


@register_formula
def get_fund_open_rewards_can_receive(
        fund_bought_flag, fund_rewards_received, level):
    if not fund_bought_flag:
        return False
    from config.configs import get_config
    from config.configs import FundRewardConfig
    from config.configs import FundRewardByTypeConfig
    from campaign.constants import FundRewardType
    types = get_config(FundRewardByTypeConfig).get(FundRewardType.Open, [])
    configs = get_config(FundRewardConfig)
    plan = level
    for each in types:
        config = configs[each.ID]
        if plan >= config.parm:
            if config.ID not in fund_rewards_received:
                return True
    return False


@register_formula
def get_fund_full_rewards_can_receive(fund_rewards_received):
    from config.configs import get_config
    from config.configs import FundRewardConfig
    from config.configs import FundRewardByTypeConfig
    from campaign.constants import FundRewardType
    from campaign.manager import get_bought_fund_count
    types = get_config(FundRewardByTypeConfig).get(FundRewardType.Full, [])
    configs = get_config(FundRewardConfig)
    plan = get_bought_fund_count()
    for each in types:
        config = configs[each.ID]
        if plan >= config.parm:
            if config.ID not in fund_rewards_received:
                return True
    return False


@register_formula
def get_check_in_rest_count(
        createtime, check_in_used_count, check_in_today):
    from datetime import date as datedate
    date = datedate.today()
    check_in_count = int(not check_in_today)  # 可以签到的天数
    createdate = createtime.date()
    if (createdate.year, createdate.month) == (date.year, date.month):
        # 今日 - (建号日-1) - 已签到 - 可签到 = 可补签
        return max(
            date.day - (
                createdate.day - 1
            ) - check_in_used_count - check_in_count, 0)
        # 今日 - 已签到 - 可签到 = 可补签
    return max(
        date.day - check_in_used_count - check_in_count, 0)


@register_formula
def get_pvprankcount():
    from pvp.rank import get_pvprankcount
    return get_pvprankcount()


@register_formula
def get_monthly_card_remain_amount(monthly_card_acc_amount):
    from config.configs import get_cons_value
    return max(
        get_cons_value("MonthlyCardAccAmount") - monthly_card_acc_amount, 0)


@register_formula
def get_monthly_card(monthly_card_time, monthly_card_received):
    from config.configs import get_cons_value
    from datetime import date as datedate
    date = datedate.today()
    if not monthly_card_time:
        return 0
    pass_days = (date - monthly_card_time.date()).days
    return max(get_cons_value(
        "MonthlyCardAccAmount") - pass_days - int(monthly_card_received), 0)


@register_formula
def get_skip_guide():
    import settings
    return settings.SKIP_GUIDE


@register_formula
def get_dlc_tasks():
    from explore.dlc import g_dlcCampaignManager
    from config.configs import get_config
    from config.configs import TaskConfig
    configs = get_config(TaskConfig)
    dd = {}

    def get_tasks(taskID):
        tasks = []
        config = configs.get(taskID)
        if not config:
            return tasks
        tasks.append(taskID)
        tasks.extend(get_tasks(config.post))
        return tasks
    for k, v in g_dlcCampaignManager.campaigns.items():
        if v.is_open():
            dd[k] = get_tasks(v.get_start_task())
    return dd


@register_formula
def get_sames(pets):
    from config.configs import PetConfig
    from config.configs import get_config
    configs = get_config(PetConfig)
    dd = {}
    for p in pets.values():
        info = configs.get(p.prototypeID)
        if not info:
            continue
        dd.setdefault(info.same, []).append(p.entityID)
    return dd


@register_formula
def get_enchant_stone_cost():
    from config.configs import get_cons_value
    return get_cons_value("EnchantCostBase")


@register_formula
def get_ex_enchant_stone_cost():
    from config.configs import get_cons_value
    return get_cons_value("EnchantExCostBase")


@register_formula
def get_enchant_stone_to_gold():
    from config.configs import get_cons_value
    return get_cons_value("EnchantStoneToGold")


@register_formula
def get_enchant_free_rest_count(enchant_free_used_count):
    from config.configs import get_cons_value
    return max(get_cons_value("EnchantFreeCount") - enchant_free_used_count, 0)


@register_formula
def get_dlc_opened():
    from explore.dlc import g_dlcCampaignManager
    for camp in g_dlcCampaignManager.campaigns.values():
        if camp.is_open():
            return True
    return False


@register_formula
def get_reward_campaign_opened():
    from campaign.manager import g_campaignManager
    for camp in g_campaignManager.reward_campaigns:
        if camp.is_open():
            return True
    return False


@register_formula
def get_visit_free_rest_count(visit_free_used_count):
    from config.configs import get_cons_value
    return max(get_cons_value("VisitFreeMaxCount") - visit_free_used_count, 0)


@register_formula
def get_visit_cost():
    from config.configs import get_cons_value
    return get_cons_value("VisitCost")


@register_formula
def get_count_down_flag(entityID, level, count_down_index):
    from entity.manager import g_entityManager
    self = g_entityManager.get_player(entityID)
    if not self:
        return False
    from campaign.manager import get_count_down
    if get_level_value(level, "count_down"):
        if get_count_down(self):
            return True
    return False


def get_loterry_hero_tips(type, count, accu):
    from config.configs import get_config
    from config.configs import LotteryFunctionConfig
    from config.configs import AttributeDroppackConfig
    kind_cfg = get_config(LotteryFunctionConfig)[type]
    if not count:
        index = 1
    elif count == 1:
        index = 2
    else:
        index = 0
    ID = kind_cfg.rangeset[index]
    attr_drop = get_config(AttributeDroppackConfig)[ID]
    tips = ""
    # print "accu %d, attr_drop.Accumulating %d" % (accu, attr_drop.Accumulating)
    if accu >= abs(attr_drop.Accumulating):
        if attr_drop.arg:
            tips = attr_drop.tips1 % attr_drop.arg
        else:
            tips = attr_drop.tips1
    else:
        # print attr_drop.Accumulating, accu, kind_cfg.Price
        rest = math.ceil(
            (abs(attr_drop.Accumulating) - accu) / float(kind_cfg.Price))
        # print "Price %d, count %d" % (kind_cfg.Price, count)
        # print "rest %d" % rest
        if attr_drop.arg:
            tips = attr_drop.tips2 % (rest + 1, attr_drop.arg)
        else:
            tips = attr_drop.tips2
    # print tips
    return tips


@register_formula
def get_loterry_hero_tips_A(count, accu):
    # print "A"
    from mall.constants import LotteryType
    return get_loterry_hero_tips(LotteryType.Lottery1, count, accu)


@register_formula
def get_loterry_hero_tips_B(count, accu):
    # print "B"
    from mall.constants import LotteryType
    return get_loterry_hero_tips(LotteryType.Lottery2, count, accu)


@register_formula
def get_loterry_hero_tips_C(count, accu):
    # print "C"
    from mall.constants import LotteryType
    return get_loterry_hero_tips(LotteryType.Lottery3, count, accu)


@register_formula
def get_loterry_hero_tips_D(count, accu):
    from mall.constants import LotteryType
    # print "D"
    return get_loterry_hero_tips(LotteryType.Lottery4, count, accu)


@register_formula
def get_basereward(gve_groupdamage):
    from config.configs import get_config
    from config.configs import GveDamageRewardConfig
    from config.configs import GveDamageRewardBySceneConfig
    from group.manager import get_sceneID
    sceneID = get_sceneID()
    group = get_config(GveDamageRewardBySceneConfig).get(sceneID, [])
    configs = get_config(GveDamageRewardConfig)
    rewards = {}
    for each in group:
        config = configs.get(each.ID)
        if not config:
            return
        if gve_groupdamage >= config.damage:
            rewards = config.rewards
        else:
            break
    return ujson.dumps(rewards)


@register_formula
def get_gve_start_time():
    from campaign.manager import g_campaignManager
    g_campaignManager.gve_campaign.get_start_time()
    return max(g_campaignManager.gve_campaign.get_start_time(), 0)


@register_formula
def get_gve_end_time():
    from campaign.manager import g_campaignManager
    g_campaignManager.gve_campaign.get_end_time()
    return max(g_campaignManager.gve_campaign.get_end_time(), 0)


@register_formula
def get_gve_buff_addition():
    from config.configs import get_cons_value
    return get_cons_value("GveBuffAddition")


@register_formula
def get_gve_reborn_cost():
    from config.configs import get_cons_value
    return get_cons_value("GveRebornCost")


@register_formula
def get_boss_campaign_opened():
    from explore.boss import g_bossCampaignManager
    from campaign.manager import g_campaignManager
    for e in g_bossCampaignManager.campaigns.values():
        if e.config.ID != g_campaignManager.flower_boss_campaign.flower_boss_config_id and e.is_open():
            return True
    return False


@register_formula
def get_point_addition(point):
    from config.configs import get_config, PointAdditionConfig
    configs = get_config(PointAdditionConfig)
    for k, v in configs.items()[::-1]:
        if point >= v.point:
            return k
    return 0


@register_formula
def get_skillpoint_max(vip):
    return get_vip_value(vip, "skill_up_count")


@register_formula
def get_buy_rest_skillpoint_count(vip, buy_used_skillpoint_count):
    return max(get_vip_value(
        vip, "buy_skill_count") - buy_used_skillpoint_count, 0)


def get_skillpoint_config(buy_used_skillpoint_count):
    from config.configs import get_config
    from config.configs import BuySkillpointConfig
    configs = get_config(BuySkillpointConfig)
    info = configs.get(buy_used_skillpoint_count + 1)
    if not info:
        info = configs[max(configs)]
    return info


@register_formula
def get_buy_skillpoint_cost(buy_used_skillpoint_count):
    info = get_skillpoint_config(buy_used_skillpoint_count)
    return info.gold


@register_formula
def get_buy_skillpoint_gain(buy_used_skillpoint_count):
    info = get_skillpoint_config(buy_used_skillpoint_count)
    return info.skillpoint


@register_formula
def get_swap_refresh_cd_cost():
    from config.configs import get_cons_value
    return get_cons_value("SwapRankCDCost")


@register_formula
def get_swap_rest_count(swap_most_count, swap_used_count):
    return swap_most_count - swap_used_count


@register_formula
def get_swap_most_count():
    from config.configs import get_cons_value
    return get_cons_value("SwapMostCount")


@register_formula
def get_swap_rest_reset_count(swap_most_reset_count,  swap_used_reset_count):
    return swap_most_reset_count - swap_used_reset_count


@register_formula
def get_swap_most_reset_count(vip):
    return get_vip_value(vip, "pvp_reset_count")


@register_formula
def get_swap_reset_count_cost(swap_used_reset_count):
    from config.configs import get_config
    from config.configs import PvpResetConfig
    configs = get_config(PvpResetConfig)
    config = configs.get(swap_used_reset_count + 1)
    if not config:
        config = configs[max(configs)]
    return config.gold


@register_formula
def get_maze_most_count():
    from config.configs import get_cons_value
    return get_cons_value("MazeMostCount")


@register_formula
def get_maze_time_flag(mazes):
    time = 0
    for each in mazes:
        time = max(each.get("time"), time)
    return time


@register_formula
def get_maze_case_cost():
    from config.configs import get_cons_value
    return get_cons_value("TriggerChestDoubleCost")


@register_formula
def get_maze_onekey_vip():
    from config.configs import get_cons_value
    return get_cons_value("MazeOnekeyVip")


@register_formula
def get_maze_onekey_point():
    from config.configs import get_cons_value
    return get_cons_value("MazeOnekeyPoint")


@register_formula
def get_friend_messages_count(friend_messages):
    count = 0
    for k, v in friend_messages.items():
        count += len(v)
    return count


@register_formula
def get_online_packs_flag(level, online_packs_done):
    return get_level_value(level, "online_packs") and not online_packs_done


@register_formula
def get_vip_packs_flag(vip, vip_packs_today_bought_count):
    return not vip_packs_today_bought_count


@register_formula
def get_daily_buy_rest_count(vip, daily_buy_used_count):
    value = get_vip_value(vip, "daily_buy_most_count") - daily_buy_used_count
    return max(0, value)


@register_formula
def get_daily_buy_count_cost(daily_buy_used_count):
    from config.configs import DailyBuyCountConfig
    from config.configs import get_config
    configs = get_config(DailyBuyCountConfig)
    config = configs.get(daily_buy_used_count + 1)
    if not config:
        config = configs[max(configs)]
    return config.gold


@register_formula
def get_daily_win_count(entityID):
    import settings
    pool = settings.REDISES["entity"]
    return int(pool.execute(
        "GET", "daily_win_count_p{%d}" % entityID) or 0)


@register_formula
def get_daily_buff(daily_max_win_count):
    if daily_max_win_count >= 10:
        value = int(daily_max_win_count/10) + 10
    else:
        value = 0
    return min(value, 30)


@register_formula
def get_daily_dead(entityID):
    import settings
    pool = settings.REDISES["entity"]
    return bool(pool.execute(
        "GET", "daily_dead_p{%d}" % entityID) or 0)


@register_formula
def get_buy_rest_soul_count(vip, buy_used_soul_count):
    return max(get_vip_value(
        vip, "buy_soul_count") - buy_used_soul_count, 0)


def get_soul_config(buy_used_soul_count):
    from config.configs import get_config
    from config.configs import BuySoulConfig
    configs = get_config(BuySoulConfig)
    info = configs.get(buy_used_soul_count + 1)
    if not info:
        info = configs[max(configs)]
    return info


@register_formula
def get_soul_cost(buy_used_soul_count):
    info = get_soul_config(buy_used_soul_count)
    return info.gold


@register_formula
def get_soul_gain(buy_used_soul_count):
    info = get_soul_config(buy_used_soul_count)
    return info.soul


@register_formula
def get_daily_reborn_cost():
    from config.configs import get_cons_value
    return get_cons_value("DailyRebornCost")


@register_formula
def get_ambition_power(ambition, vip_ambition):
    from entity.utils import get_ambition_additions_by_raw
    additions = get_ambition_additions_by_raw(ambition, vip_ambition)
    # from config.configs import get_config
    # from config.configs import AmbitionConfig
    # from config.configs import VipAmbitionConfig
    # additions = defaultdict(int)
    # config = get_config(AmbitionConfig).get(ambition)
    # attrs = ["hp", "atk", "def", "crit", "dodge"]
    # if config:
    #     additions.update(dict(zip(attrs, config.addition)))
    # config = get_config(VipAmbitionConfig).get(vip_ambition)
    # if config:
    #     for k, v in dict(zip(attrs, config.addition)).items():
    #         additions[k] += v
    result = hp2power(additions["hp"])
    result += atk2power(additions["atk"])
    result += def2power(additions["def"])
    result += cri2power(additions["crit"])
    result += eva2power(additions["dodge"])
    return result


@register_formula
def get_honor_power(entityID):
    from entity.manager import g_entityManager
    self = g_entityManager.get_player(entityID)
    if not self:
        return 0

    honor_additions = get_honor_additions(self)

    TRANS = {
        "ATK": "ATK",
        "DEF": "DEF",
        "HP": "HP",
        "CRIT": "CRI",
        "DODGE": "EVA",
    }
    from lineup.constants import LineupType
    lineup = self.lineups.get(LineupType.ATK, [])
    pets = [self.pets[i] for i in lineup if i]
    attrs = ["hp", "atk", "def", "crit", "dodge"]
    result = 0
    for pet in pets:
        power = 0
        for tag in attrs:
            base = getattr(pet, "base%s" % TRANS[tag.upper()], 0)
            point = base * (honor_additions.get(
                "per_%s" % tag, 0) / float(100)
                ) + honor_additions.get("abs_%s" % tag, 0)
            power += {
                "hp": hp2power,
                "atk": atk2power,
                "def": def2power,
                "crit": cri2power,
                "dodge": eva2power,
            }[tag](point)
        result += power
    return result


@register_formula
def get_point_power(entityID, point, lineups):
    from entity.manager import g_entityManager
    self = g_entityManager.get_player(entityID)
    if not self:
        return 0

    from collections import defaultdict
    from config.configs import get_config
    from lineup.constants import LineupType
    from config.configs import PointAdditionConfig
    additions = defaultdict(int)
    for k, config in get_config(PointAdditionConfig).items():
        if point >= config.point:
            additions[config.type] += config.addition
    TRANS = {
        "ATK": "ATK",
        "DEF": "DEF",
        "HP": "HP",
        "CRIT": "CRI",
        "DODGE": "EVA",
    }
    lineup = self.lineups.get(LineupType.ATK, [])
    pets = [self.pets[i] for i in lineup if i]
    attrs = ["hp", "atk", "def", "crit", "dodge"]
    result = 0
    for pet in pets:
        power = 0
        for tag in attrs:
            base = getattr(pet, "base%s" % TRANS[tag.upper()], 0)
            point = base * (additions.get(
                "per_%s" % tag, 0) / float(100)
                ) + additions.get("abs_%s" % tag, 0)
            power += {
                "hp": hp2power,
                "atk": atk2power,
                "def": def2power,
                "crit": cri2power,
                "dodge": eva2power,
            }[tag](point)
        result += power
    return result


@register_formula
def get_pet_exchange_cd():
    from campaign.manager import g_campaignManager
    return g_campaignManager.pet_exchange_campaign.get_end_time()


@register_formula
def get_lottery_campaign_discount():
    from campaign.manager import g_campaignManager
    campaign = g_campaignManager.lottery_campaign
    if not campaign.is_open():
        return 10
    return g_campaignManager.lottery_campaign.get_current().group


@register_formula
def get_lottery_campaign_cd():
    from campaign.manager import g_campaignManager
    return g_campaignManager.lottery_campaign.get_end_time()


@register_formula
def get_lottery_campaign_hot():
    from campaign.manager import g_campaignManager
    return g_campaignManager.hot_lottery_campaign.get_hot()


@register_formula
def get_lottery_campaign_hot_cd():
    from campaign.manager import g_campaignManager
    return g_campaignManager.hot_lottery_campaign.get_end_time()


@register_formula
def get_mat_exchange_campaign_cd():
    from campaign.manager import g_campaignManager
    return g_campaignManager.mat_exchange_campaign.get_end_time()


@register_formula
def get_city_dungeon_start_time():
    from campaign.manager import g_campaignManager
    return max(g_campaignManager.city_dungeon_campaign.get_start_time(), 0)


@register_formula
def get_city_dungeon_final_time():
    from campaign.manager import g_campaignManager
    return max(g_campaignManager.city_dungeon_campaign.get_final_time(), 0)


@register_formula
def get_city_contend_start_time():
    from campaign.manager import g_campaignManager
    return max(g_campaignManager.city_contend_campaign.get_start_time(), 0)


@register_formula
def get_city_contend_final_time():
    from campaign.manager import g_campaignManager
    return max(g_campaignManager.city_contend_campaign.get_final_time(), 0)


@register_formula
def get_ambition_cost():
    from config.configs import get_cons_value
    return get_cons_value("AmbitionUpCost")


@register_formula
def get_ambition_gold_cost():
    from config.configs import get_cons_value
    return get_cons_value("AmbitionGoldUpCost")


@register_formula
def get_consume_campaign_rest_time():
    from campaign.manager import g_campaignManager
    return max(g_campaignManager.consume_campaign.get_end_time(), 0)


@register_formula
def get_login_campaign_rest_time():
    from campaign.manager import g_campaignManager
    return max(g_campaignManager.login_campaign.get_end_time(), 0)


@register_formula
def get_climb_tower_max_count(vip):
    from config.configs import get_config, VipConfig
    configs = get_config(VipConfig)
    config = configs.get(vip)
    if not config:
        return 0
    return config.climb_tower_reset_count


@register_formula
def get_climb_tower_accredit_earnings(stash_time, cd, floor):
    if stash_time == 0 or cd == 0:
        return 0
    from config.configs import get_config, ClimbTowerAccreditConfig, Cons
    config = get_config(ClimbTowerAccreditConfig).get(floor, None)
    if not config:
        return 0
    cd = datetime.fromtimestamp(cd)
    delta = min(datetime.now(), cd) - datetime.fromtimestamp(stash_time)
    assert delta.total_seconds() >= 0
    minutes = int(delta.total_seconds() / 60.0)
    return config.earnings[-1] * minutes


@register_formula
def get_climb_tower_accredit_raw_lineup(entityID, lineups, climb_tower_accredit_cd):
    import time
    from lineup.constants import LineupType
    from entity.manager import g_entityManager
    line = lineups.get(LineupType.Accredit, [])
    if climb_tower_accredit_cd <= int(time.time()):
        # 派驻到期，重置派驻阵容
        player = g_entityManager.get_player(entityID)
        if line and player:
            player.lineups[LineupType.Accredit] = []
            player.save()
        line = []
    return ','.join(map(str, line))


@register_formula
def get_climb_tower_total_floor():
    from config.configs import get_config, ClimbTowerConfig
    return max(get_config(ClimbTowerConfig).keys())


@register_formula
def get_exchange_campaign_remain_time():
    from campaign.manager import g_campaignManager
    if not g_campaignManager.exchange_campaign.is_open():
        return 0
    return g_campaignManager.exchange_campaign.get_end_time()


@register_formula
def get_refresh_store_campaign_remain_time():
    from campaign.manager import g_campaignManager
    if not g_campaignManager.refresh_store_campaign.is_open():
        return 0
    return g_campaignManager.refresh_store_campaign.get_end_time()


@register_formula
def get_gems_power(entityID, point, lineups):
    from lineup.constants import LineupType
    from entity.manager import g_entityManager
    self = g_entityManager.get_player(entityID)
    if not self:
        return 0
    inlay = [getattr(self, 'inlay%d' % i, 0) for i in range(1, 6)]
    lineup = self.lineups.get(LineupType.ATK, [])
    pets = [self.pets[i] for i in lineup if i]
    from gem.manager import get_gems_addition
    attrs = ["hp", "atk", "def", "crit", "dodge"]
    result = 0
    for pet in pets:
        power = 0
        for tag in attrs:
            point = get_gems_addition(*inlay, tag={'def': 'defend'}.get(tag, tag))
            power += {
                "hp": hp2power,
                "atk": atk2power,
                "def": def2power,
                "crit": cri2power,
                "dodge": eva2power,
            }[tag](point)
        result += power
    return result


@register_formula
def get_arbor_day_campaign_remain_time():
    from campaign.manager import g_campaignManager
    if not g_campaignManager.arbor_day_campaign.is_open():
        return 0
    return g_campaignManager.arbor_day_campaign.get_end_time()


@register_formula
def get_shake_tree_free_count():
    from config.configs import get_cons_value
    return get_cons_value("ArborDayFreeCount")


@register_formula
def get_shake_tree_max_count():
    from config.configs import get_cons_value
    return get_cons_value("ArborDayMaxCount")


@register_formula
def get_shake_tree_cost():
    from config.configs import get_cons_value
    return get_cons_value("ArborDayPayCost")


@register_formula
def get_seed_campaign_remain_time():
    from campaign.manager import g_campaignManager
    if not g_campaignManager.seed_campaign.is_open():
        return 0
    return g_campaignManager.seed_campaign.get_end_time()


@register_formula
def get_seed_state_change_remain_time(seed_state_last_change_time, seed_state_next_change_time):
    return seed_state_next_change_time - seed_state_last_change_time


@register_formula
def get_seed_state_ripening_remain_time(seed_state_ripening_time):
    import time
    return seed_state_ripening_time - int(time.time())


@register_formula
def get_watering_max_count():
    from config.configs import get_cons_value
    return get_cons_value("WateringMaxCount")


@register_formula
def get_watering_remain_time(watering_time):
    import time
    remain_time = watering_time - int(time.time())
    if remain_time < 0:
        remain_time = 0

    return remain_time


@register_formula
def get_worming_max_count():
    from config.configs import get_cons_value
    return get_cons_value("WateringMaxCount")


@register_formula
def get_worming_remain_time(worming_time):
    import time
    remain_time = worming_time - int(time.time())
    if remain_time < 0:
        remain_time = 0

    return remain_time


@register_formula
def get_handsel_campaign_remain_time():
    from campaign.manager import g_campaignManager
    if not g_campaignManager.handsel_campaign.is_open():
        return 0
    return g_campaignManager.handsel_campaign.get_end_time()


@register_formula
def get_flower_boss_campaign_remain_time():
    from campaign.manager import g_campaignManager
    if not g_campaignManager.flower_boss_campaign.is_open():
        return 0
    return g_campaignManager.flower_boss_campaign.get_end_time()


def get_honor_additions(p):
    from collections import defaultdict
    honor_addition = defaultdict(int)

    from config.configs import get_config, HandselHonorConfig
    honor_configs = get_config(HandselHonorConfig)

    if not p.campaign_honor_point or p.campaign_honor_point.strip() == '':
        p.campaign_honor_point = "{}"

    import json
    honor_json = json.loads(p.campaign_honor_point)
    for h_config in honor_configs.values():
        if h_config.camp_id in honor_json:
            point = honor_json[h_config.camp_id]
            if point >= h_config.point:
                if h_config.type1:
                    honor_addition[h_config.type1] += h_config.addition1
                if h_config.type2:
                    honor_addition[h_config.type2] += h_config.addition2

    return honor_addition
