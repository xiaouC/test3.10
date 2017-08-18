# coding:utf-8
import random
from datetime import date as datedate
from datetime import timedelta
import logging
logger = logging.getLogger("pvp")

from config.configs import get_config
from config.configs import UproarConfig
from config.configs import LevelupConfig

from reward.manager import RewardType
from reward.manager import open_reward
from reward.manager import apply_reward
from reward.manager import combine_reward

from campaign.manager import g_campaignManager
import settings
from player.model import PlayerPowerRanking
from player.model import PlayerMaxPowerRanking
from pvp.manager import get_opponent_detail


def validate_prev(player, id):
    config = get_config(UproarConfig)[min(id, 11)]
    if not config.prev:
        return True
    return config.prev in player.uproar_targets_done


def get_detail(targetID):
    return get_opponent_detail(targetID)


def cleanup_ranking(date=None):
    if not date:
        date = datedate.today() - timedelta(days=2)
    key = "RANK_UPROAR{%d}{%d}{%s}" % (
        settings.SESSION["ID"], settings.REGION["ID"], date),
    pool = settings.REDISES['index']
    return pool.execute("DEL", key)


def uproar_reset(p):
    """训练家之丘重置"""
    configs = get_config(UproarConfig)
    p.uproar_targets.clear()
    p.uproar_chests.clear()
    map(p.uproar_targets.pop, p.uproar_targets.keys())
    map(p.uproar_chests.pop, p.uproar_chests.keys())
    for n, config in configs.items()[:10]:
        targetID = -config.robot
        p.uproar_targets[n] = targetID
        money = int(p.level * (config.money_base + random.randint(0, 10)))
        must = {'jiutian': config.jiutian, 'money': money}
        reward = open_reward(RewardType.Uproar, config.dropID, {})
        drop = reward.apply_after()
        p.uproar_chests[n] = {"must": must, "drop": drop}

    p.uproar_targets_cache = []
    p.uproar_chests_cache = []
    p.uproar_details_cache.clear()
    for targetID in p.uproar_targets.values():
        if targetID > 0:
            target = get_detail(targetID)
            if target:
                p.uproar_details_cache[targetID] = target
    p.uproar_chests_cache = []
    p.uproar_targets_done = set()
    p.uproar_chests_done = set()
    p.uproar_targets_team.clear()
    for pet in p.pets.values():
        if pet.uproar_dead:
            pet.uproar_dead = False
        pet.restHP = 0
        pet.save()
        pet.sync()
    # 重置敌方属性加成
    p.uproar_enemy_buff = 0
    p.uproar_enemy_min_power = 0
    p.save()
    p.sync()


def uproar_forward(p):
    """匹配玩家"""
    configs = get_config(UproarConfig)
    ranking = PlayerPowerRanking

    # 前 10 级宝箱未领取完不处理
    if max(p.uproar_chests_done | set([0])) < 10:
        return

    # 检查等级限制
    level = get_config(LevelupConfig).get(p.level, None)
    if level and not level.uproar:
        return

    # 战力向下浮动 20% 取玩家
    if p.uproar_enemy_min_power == 0:
        p.uproar_enemy_min_power = p.max_power - (p.max_power * 0.3)

    current_floor = max(p.uproar_targets_done | set([0]))
    if current_floor == 10:
        # 通关前 10 首次匹配
        p.uproar_targets.clear()
        p.uproar_chests.clear()
        map(p.uproar_targets.pop, p.uproar_targets.keys())
        map(p.uproar_chests.pop, p.uproar_chests.keys())

        targets = ranking.get_by_score_range(p.uproar_enemy_min_power, '+inf',
                                             desc=False, limit=15)
        if len(targets):
            p.uproar_enemy_min_power = targets[-1][1]
        else:
            # 匹配不到重复第一名
            target = ranking.get_by_rank(1)
            power = ranking.get_score(target)
            targets = [(target, power)]

        # NOTE 假数据
        while len(targets) < 15:
            targets.append(targets[-1])
        logger.debug('enter uproar no limit mode')

        config = configs.values()[-1]
        for n, (target, power) in enumerate(targets, start=11):
            p.uproar_targets[n] = target
            money = int(p.level * (config.money_base + random.randint(0, 10)))
            must = {'jiutian': config.jiutian, 'money': money}
            reward = open_reward(RewardType.Uproar, config.dropID, {})
            drop = reward.apply_after()
            p.uproar_chests[n] = {"must": must, "drop": drop}
        p.uproar_details_cache.clear()
        p.uproar_targets_team.clear()
    else:
        # 保留三个已通关历史
        logger.debug('uproar forward')
        prev = set(sorted(p.uproar_targets.keys())[:6])
        if prev & p.uproar_targets_done == prev:
            limit = 3
            targets = ranking.get_by_score_range(p.uproar_enemy_min_power, '+inf',
                                                 desc=False, limit=limit)
            if len(targets):
                p.uproar_enemy_min_power = targets[-1][1]
            else:
                # 匹配不到重复第一名
                target = ranking.get_by_rank(1)
                power = ranking.get_score(target)
                targets = [(target, power)] * limit

            # 删除前三个，再补三个
            droped = min(len(targets), limit)
            to_drop = sorted(list(prev))[:droped]
            for k in to_drop:
                p.uproar_details_cache.pop(p.uproar_targets[k], None)
                p.uproar_targets_team.pop(p.uproar_targets[k], None)
            map(p.uproar_targets.pop, to_drop)

            start = max(p.uproar_targets.keys()) + 1
            config = configs.values()[-1]
            for n, (target, power) in enumerate(targets, start=start):
                p.uproar_targets[n] = target
                money = int(p.level * (config.money_base + random.randint(0, 10)))
                must = {'jiutian': config.jiutian, 'money': money}
                reward = open_reward(RewardType.Uproar, config.dropID, {})
                drop = reward.apply_after()
                p.uproar_chests[n] = {"must": must, "drop": drop}

    for targetID in p.uproar_targets.values():
        if targetID > 0:
            target = get_detail(targetID)
            if target:
                p.uproar_details_cache[targetID] = target
    for pet in p.pets.values():
        if pet.uproar_dead:
            pet.uproar_dead = False
        pet.restHP = 0
        pet.save()
        pet.sync()

    # 打过了第一名，每一关敌方属性加成 10%
    last_target = p.last_target in p.uproar_targets
    first = ranking.get_by_rank(1)
    if last_target and p.uproar_targets[p.last_target] == first:
        p.uproar_enemy_buff += 10

    p.save()
    p.sync()


def uproar_reward_in_campaign(must=None, drop=None):
    config = g_campaignManager.uproar_campaign.get_current()
    result = {}
    if not must:
        must = {}
    else:
        must = dict(must)
    if not drop:
        drop = {}
    else:
        drop = dict(drop)
    if not config:
        result = drop
        result.update(must)
        return drop
    cmoney, cjiutian, cdrop = str(config.group)
    cmoney = int(cmoney)
    cjiutian = int(cjiutian)
    cdrop = int(cdrop)
    if must.get("money"):
        must["money"] *= cmoney
    if must.get("jiutian"):
        must["jiutian"] *= cjiutian
    result.update(must)
    for i in range(cdrop):
        combine_reward(drop, [], data=result)
    return result


def open_chest(player, index):
    chest = player.uproar_chests[index]
    must = chest.get("must", {})
    drop = chest.get("drop", {})
    drop = uproar_reward_in_campaign(must, drop)
    result = apply_reward(player, drop, type=RewardType.Uproar)
    player.save()
    player.sync()
    return result
