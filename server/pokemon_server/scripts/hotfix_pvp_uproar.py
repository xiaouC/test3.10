#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pvp.uproar import *  # NOQA
import pvp.uproar


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

pvp.uproar.uproar_forward = uproar_forward
