# -*- coding: utf-8 -*-

import time
import random
import logging
import settings
from datetime import datetime
from collections import defaultdict
from config.configs import get_config
from config.configs import Cons
from config.configs import ClimbTowerConfig
from config.configs import ClimbTowerAccreditConfig
from common.index import IndexString
from yy.entity.index import SortedIndexing, UniqueIndexing, SetIndexing
from entity.manager import g_entityManager
from pvp.manager import get_opponent_detail
from reward.constants import RewardType
from reward.manager import parse_reward, apply_reward
from mail.manager import get_mail, send_mail
from gm.proxy import proxy
from player.model import Player, OfflineAttrType
from tower.model import Floor
logger = logging.getLogger('climb_tower')

HISTORY_LIMIT = 10
LOCK_TIME = 120


def add_climb_tower_history_offline(entityID, history, fight=None):
    history['ID'] = '%d:%d' % (history['time'], history['oppID'])
    p = Player.simple_load(entityID, ["climb_tower_history"])
    if p:
        p.climb_tower_history.load()
        p.climb_tower_history.appendleft(history)
        p.climb_tower_history.ltrim(0, HISTORY_LIMIT)
    if fight:
        Player.pool.execute(
            "HSET", "climb_tower_fight_history_p{%d}" % entityID,
            history['ID'], fight)
        keys = Player.pool.execute(
            'HKEYS', "climb_tower_fight_history_p{%d}" % entityID)
        if len(keys) > HISTORY_LIMIT:
            for key in sorted(keys)[:-HISTORY_LIMIT]:
                Player.pool.execute(
                    "HDEL", "climb_tower_fight_history_p{%d}" % entityID, key)
        p.save()


@proxy.rpc(failure=add_climb_tower_history_offline)
def add_climb_tower_history(entityID, history, fight=None):
    history['ID'] = '%d:%d' % (history['time'], history['oppID'])
    p = g_entityManager.get_player(entityID)
    if p:
        p.climb_tower_history.appendleft(history)
        p.climb_tower_history.ltrim(0, HISTORY_LIMIT)
        if fight:  # clean fight history
            p.climb_tower_fight_history[history['ID']] = fight
            if len(p.climb_tower_fight_history) > HISTORY_LIMIT:
                for key in sorted(p.climb_tower_fight_history)[:-HISTORY_LIMIT]:
                    del p.climb_tower_fight_history[key]
        p.save()
        p.sync()


def discredit_offline(manager, entityID, current_floor):
    now = int(time.time())
    floor = manager.avail_floor(current_floor)

    attrs = ['climb_tower_accredit_earnings',
             'climb_tower_floor',
             'climb_tower_accredit_stash_time',
             'climb_tower_accredit_cd']
    p = Player.simple_load(entityID, Player.expend_fields(attrs))
    if p:
        if floor:
            value = p.climb_tower_accredit_earnings
            # 结束时间作为 score
            score = p.climb_tower_accredit_cd

            p.climb_tower_accredit_stash_earnings += value
            p.climb_tower_accredit_floor = floor
            p.climb_tower_accredit_stash_time = now
            # 取消当前层派驻
            manager.floors[current_floor].idx.unregister(p.entityID)
            manager.floors[floor].idx.register(p.entityID, score)

        else:
            p.climb_tower_accredit_cd = now
            manager.floors[current_floor].idx.unregister(p.entityID)
        p.save()


@proxy.rpc(failure=discredit_offline)
def discredit(manager, entityID, current_floor):
    """以当前派驻层向下查找可派驻层，暂存收益并派驻或结算派驻收益"""
    now = int(time.time())
    floor = manager.avail_floor(current_floor)

    p = g_entityManager.get_player(entityID)
    if p:
        if floor:
            # 可派驻，暂存当前派驻层收益
            manager.stash_earnings(p)
            p.climb_tower_accredit_floor = floor
            p.climb_tower_accredit_stash_time = now
            # 结束时间作为 score
            score = int(p.climb_tower_accredit_cd)
            # 取消当前层派驻
            manager.floors[current_floor].idx.unregister(p.entityID)
            manager.floors[floor].idx.register(p.entityID, score)
        else:
            # 取消派驻
            manager.floors[current_floor].idx.unregister(p.entityID)
            p.climb_tower_accredit_cd = now
            # 结算派驻收益
            manager.tally_up(p)
        p.save()
        p.sync()


class ClimbTowerManager(object):
    """派驻存储方式

    `entityID` 作为 `member`
    `timestamp` 作为 `score`

    这样可以非常方便的使用 score 来清理过期派驻
    """
    def __init__(self):
        self.floors = dict()
        self.tip_earnings = dict()

        # 每个类型的打赏收益分开
        # 全服结算时只需要结算与当前配置不同的类型
        index = IndexString('C_T_{$regionID}_k')
        self.tip_types = SetIndexing(index.render(), settings.REDISES['index'])

        # 保存所有的打赏类型
        types = [c.tip[0] for c in get_config(ClimbTowerAccreditConfig).values()]
        types.extend(self.tip_types.getall())
        for t in map(int, types):
            self.tip_types.register(t)
            index = IndexString('C_T_{$regionID}_t%d' % t)
            self.tip_earnings[t] = UniqueIndexing(index.render(), settings.REDISES['index'])

        # 保存所有的派驻层，在派驻层关闭时踢出所有派驻，并结算派驻奖励
        # 同时保存一个结算时间用于玩家上线时结算奖励
        index = IndexString('C_T_{$regionID}_h')
        self.floors_all = SetIndexing(index.render(), settings.REDISES['index'])
        for floor in get_config(ClimbTowerAccreditConfig):
            self.floors_all.register(floor)

        # 每一层的派驻索引
        for f in sorted(map(int, self.floors_all.getall())):
            entityID = int('{:3d}{:03d}'.format(settings.REGION['ID'], f))
            try:
                floor = Floor.load(entityID)
            except:
                floor = Floor.create(entityID=entityID, floor=f)
            config = get_config(ClimbTowerAccreditConfig).get(f, None)
            if config:
                floor.payoff = 0
                floor.limit = config.top_limit

            will_close = any([not config, floor.is_closed(),
                              config and floor.limit > config.top_limit])
            if will_close:
                logger.info('accredit floor %d will kick all players now' % floor.floor)
                # 提前结束派驻
                floor.idx.clear_raw()
                floor.idx_p.clear_raw()
                floor.lock.clear_raw()
                floor.payoff = int(time.time())

            floor.save()
            self.floors[f] = floor

    def avail_floor(self, current_floor):
        floor = None
        floors = sorted(self.floors.keys(), reverse=True)
        for _floor in filter(lambda x: x < current_floor, floors):
            f = self.floors[_floor]
            if f.is_closed() or f.is_full():
                continue
            floor = _floor
            break
        return floor

    def stash_earnings(self, player):
        """改变派驻楼层暂存收益"""
        player.climb_tower_accredit_stash_earnings += player.climb_tower_accredit_earnings
        player.climb_tower_accredit_stash_time = int(time.time())
        player.save()
        player.sync()

    def tally_up(self, player):
        """结算收益"""
        if not player:
            return
        cd = player.climb_tower_accredit_cd
        floor = player.climb_tower_accredit_floor

        if floor in self.floors:
            # 统一的结束时间
            payoff = self.floors[floor].payoff
            if payoff > player.climb_tower_accredit_stash_time and payoff < cd:
                player.climb_tower_accredit_cd = cd = payoff
                player.save()

        if floor > 0 and cd > 0 and cd <= int(time.time()):
            # 派驻到期
            config = get_config(ClimbTowerAccreditConfig)[floor]
            payload = dict(type=config.earnings[0], arg=config.earnings[0],
                           count=player.climb_tower_accredit_acc_earnings)
            rewards = [payload] if payload['count'] > 0 else []
            clear = []
            fields = ['t%d' % player.entityID, player.entityID]

            # 结算所有类型打赏收益
            for kind, idx in self.tip_earnings.items():
                tip = int(idx.pool.execute('HGET', idx.key, player.entityID) or 0)
                if tip > 0:
                    earnings = dict(type=kind,
                                    arg=kind,
                                    count=tip)
                    rewards.append(earnings)
                    clear.append(idx)

            logger.info('tally_up: %d, %s' % (player.entityID, rewards))
            reward = parse_reward(rewards)
            title, content, ID = get_mail('ClimbTowerAccredit')
            dt = datetime.fromtimestamp(cd)
            send_mail(player.entityID, title=title,
                      content=content.format(dt.strftime('%Y-%m-%d')),
                      addition=reward, configID=ID)
            self.floors[floor].idx.unregister(player.entityID)
            player.climb_tower_accredit_stash_time = 0
            player.climb_tower_accredit_cd = 0
            player.climb_tower_accredit_stash_earnings = 0
            player.climb_tower_accredit_floor = 0
            player.save()
            player.sync()

            for idx in clear:
                idx.pool.execute('HDEL', idx.key, *fields)

    def lock_target(self, player):
        """锁定对手
        派驻达到上限才需要锁定对手"""
        floor = player.climb_tower_floor
        if self.floors[floor].is_full() and player.climb_tower_last_target > 0:
            self.floors[floor].lock.register(player.climb_tower_last_target,
                                             int(time.time()) + LOCK_TIME)

    def pre_accredit(self, player):
        """进入派驻保护期"""
        floor = player.climb_tower_floor
        if floor not in get_config(ClimbTowerAccreditConfig):
            return
        self.floors[floor].cleanup()
        if self.floors[floor].is_full():
            # 满了，直接重新派驻对手
            self.discredit(player.climb_tower_last_target,
                           floor)
        f = self.floors[floor].idx_p
        f.register(player.entityID, int(time.time()) + LOCK_TIME)

    def discredit(self, entityID, current_floor):
        """重新派驻"""
        logger.info('discredit %d, %d' % (entityID, current_floor))
        proxy.discredit(self, entityID, current_floor)

    def accredit(self, player, lineup):
        """派驻"""
        p = player
        floor = p.climb_tower_floor
        logger.info('before accredit: %r' % self.floors[floor].idx_p.exists(p.entityID))
        target = p.climb_tower_last_target

        self.floors[floor].cleanup()
        if not self.floors[floor].idx_p.exists(p.entityID):
            # 不在保护期
            assert not self.floors[floor].is_full()

        # 取消其它层的派驻
        for f in self.floors.values():
            if f.idx.exists(p.entityID):
                f.idx.unregister(p.entityID)
                self.stash_earnings(p)
            if f.idx_p.exists(p.entityID):
                f.idx_p.unregister(p.entityID)

        now = int(time.time())
        p.climb_tower_accredit_floor = floor
        p.climb_tower_accredit_stash_time = now
        # 改变派驻层不重置 CD
        if p.climb_tower_accredit_cd <= 0:
            p.climb_tower_accredit_cd = now + get_config(Cons)[77].value
        p.save()
        p.sync()
        # 结束时间作为 score
        score = int(p.climb_tower_accredit_cd)
        logger.debug('accredit: %d, %d, %d' % (floor, p.entityID, score))
        logger.info('accredit: %d, %d, %d, %d, %d' % (floor, p.entityID, score,
                                                      self.floors[floor].idx.count(),
                                                      self.floors[floor].idx_p.count()))
        # 解锁对手
        self.floors[floor].lock.unregister(target)
        return self.floors[floor].idx.register(p.entityID, score)

    def challenge(self, player):
        """挑战"""
        from lineup.constants import LineupType
        p = player
        floor = p.climb_tower_floor + 1
        max_retry = 5
        retry = 0

        config = get_config(ClimbTowerAccreditConfig).get(floor, None)
        if not config:
            config = get_config(ClimbTowerConfig)[floor]

        t = config.zombie_id
        if floor in self.floors:
            self.floors[floor].cleanup()
            f = self.floors[floor].idx
            # 如果派驻满了而且有空闲对手
            while retry < max_retry and self.floors[floor].is_full() \
                    and f.count() > self.floors[floor].lock.count():
                start = random.randint(0, f.count())
                targets = f.pool.execute('ZRANGE', f.key, start, start + 10)
                logger.debug('climb_tower targets: %s' % targets)
                for m in targets:
                    if int(m) == player.entityID or self.floors[floor].lock.exists(m):
                        continue
                    logger.debug('challenge player')
                    return get_opponent_detail(int(m), type=LineupType.Accredit)
                retry += 1
        logger.debug('challenge zombie')
        return get_opponent_detail(t)

    def tip(self, player):
        """打赏
        这部分最麻烦的是打赏的类型会根据配置变化，配置变化时必须结算当前打赏收益
        """
        config = get_config(ClimbTowerAccreditConfig)[player.climb_tower_floor + 1]
        cost = dict(zip(['type', 'arg', 'count'], config.tip))
        apply_reward(player, {}, parse_reward([cost]), type=RewardType.ClimbTower)

        target = self.challenge(player)
        if target['entityID'] > 0:
            # 保存打赏收益及次数
            idx = self.tip_earnings[config.tip[0]]
            idx.pool.execute('HINCRBY', idx.key,
                             target['entityID'], config.tip[2])
            idx.pool.execute('HINCRBY', idx.key,
                             't%d' % target['entityID'], 1)

            now = int(time.time())
            self.add_history(target['entityID'], {
                "oppID": player.entityID,
                "name": player.name,
                "prototypeID": player.prototypeID,
                "borderID": player.borderID,
                "level": player.level,
                "faction_name": player.faction_name,
                "isWin": False,
                "isActive": True, "time": now,
                "isRevenge": False,
                "tip_type": config.tip[0],
                "tip_count": config.tip[2],
            })

    def add_history(self, entityID, history, fight=None):
        """保存驻守历史"""
        proxy.add_climb_tower_history(entityID, history, fight)

g_climbTowerManager = ClimbTowerManager()
