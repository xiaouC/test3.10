# coding:utf-8
import time
import ujson
import random
import logging
logger = logging.getLogger("swap")
from datetime import date as datedate
from datetime import timedelta

import settings
from credis import RedisReplyError

from yy.utils import convert_list_to_dict
from yy.db.redisscripts import load_redis_script
from yy.ranking import SwapRanking
from player.model import PlayerSwapRankRanking
from common.index import INT_SWAPRANKFLAG
SWAPRANKFLAG = INT_SWAPRANKFLAG.render()
from common.utils import copy

from config.configs import get_config
from config.configs import SwapRuleConfig
from config.configs import RobotNameConfig
from config.configs import SwapRewardConfig

from pvp.manager import get_opponent_detail
from reward.manager import parse_reward
# from pvp.manager import get_opponent_detail_all
from entity.manager import g_entityManager
from player.model import Player
from gm.proxy import proxy
from lineup.constants import LineupType
from mail.manager import send_mail
from mail.constants import MailType
from mail.manager import get_mail

SWAPRANK_REWARDS = "SWAPRANK_REWARDS{%d}{%d}" % (
    settings.SESSION["ID"], settings.REGION["ID"])

MAX_DAY_KEEP_SWAPRANK = 7  # 超过此天数不再保留排行榜
MAX_DAY_CAN_GIVE_REWARD = min(7, MAX_DAY_KEEP_SWAPRANK)  # 超过此天数，不再发奖
DATE_FMT = "%Y-%m-%d"


# @load_redis_script(pool=settings.REDISES["index"])
# def copy(key1, key2):
#     """
#     local serialized = redis.call("DUMP", KEYS[1])
#     local ok = redis.call("RESTORE", KEYS[2], 0, serialized)
#     return ok
#     """
#     return (key1, key2), tuple()


@load_redis_script(pool=settings.REDISES["index"])
def swap(s1, s2):
    """
    local s1 = redis.call('ZSCORE', KEYS[1], ARGV[1])
    local s2 = redis.call('ZSCORE', KEYS[1], ARGV[2])
    local r1 = redis.call('ZRANK', KEYS[1], ARGV[1]) + 1
    local r2 = redis.call('ZRANK', KEYS[1], ARGV[2]) + 1
    if r1 <= r2 then
        return {r1, r2}
    end
    if tonumber(ARGV[1] or 0) > 0 then
        redis.call('ZADD', KEYS[1], s2, ARGV[1])
        r1 = redis.call('ZRANK', KEYS[1], ARGV[1]) + 1
    else
        redis.call('ZREM', KEYS[1], ARGV[1])
    end
    if tonumber(ARGV[2] or 0) > 0 then
        redis.call('ZADD', KEYS[1], s1, ARGV[2])
        local r2 = redis.call('ZRANK', KEYS[1], ARGV[2]) + 1
    else
        redis.call('ZREM', KEYS[1], ARGV[2])
    end
    return {r1, r2}
    """
    return (PlayerSwapRankRanking.key, ), (s1, s2)


FIGHT_HISTORY_LIMIT = 5
HISTROY_LIMIT = 10


def add_history_offline(entityID, history, fight=None):
    history['ID'] = '%d:%d' % (history['time'], history['oppID'])
    p = Player.simple_load(entityID, ["swap_history"])
    if p:
        p.swap_history.load()
        p.swap_history.appendleft(history)
        p.swap_history.ltrim(0, HISTROY_LIMIT)
    if fight:
        Player.pool.execute(
            "HSET", "swap_fight_history_p{%d}" % entityID,
            history['ID'], fight)
        keys = Player.pool.execute(
            'HKEYS', "swap_fight_history_p{%d}" % entityID)
        if len(keys) > FIGHT_HISTORY_LIMIT:
            for key in sorted(keys)[:-FIGHT_HISTORY_LIMIT]:
                Player.pool.execute(
                    "HDEL", "swap_fight_history_p{%d}" % entityID, key)


@proxy.rpc(failure=add_history_offline)
def add_history(entityID, history, fight=None):
    history['ID'] = '%d:%d' % (history['time'], history['oppID'])
    p = g_entityManager.get_player(entityID)
    if p:
        p.swap_history.appendleft(history)
        p.swap_history.ltrim(0, HISTROY_LIMIT)
        if fight:  # clean fight history
            p.swap_fight_history[history['ID']] = fight
            if len(p.swap_fight_history) > FIGHT_HISTORY_LIMIT:
                for key in sorted(p.swap_fight_history)[:-FIGHT_HISTORY_LIMIT]:
                    del p.swap_fight_history[key]
        p.swaprank = g_swapManager.get_rank(p.entityID)
        p.save()
        p.sync()


class SwapManager(object):
    def __init__(self):
        self.init_robots()
        self.load_rewards()

    def init_robots(self):
        pool = settings.REDISES["index"]
        no_exist = pool.execute("SETNX", SWAPRANKFLAG, 1)
        configs = get_config(SwapRuleConfig).values()
        if no_exist:
            logger.info("Swap init robots")
            with pool.ctx() as conn:
                for config in configs:
                    start, end = config.range
                    e = config.monstergroup
                    for r in range(start, end + 1):
                        r = r - 1
                        if r >= 10000:
                            break
                        id = "-{}{}".format(e, ("%4d" % r).replace(" ", "0"))
                        conn.execute("ZADD", PlayerSwapRankRanking.key, r, id)

    def backup_key(self, date=None):
        if not date:
            date = datedate.today()
        suffix = datedate.strftime(date, DATE_FMT)
        return "%s{%s}" % (PlayerSwapRankRanking.key, suffix)

    def backup(self):
        key1 = PlayerSwapRankRanking.key
        key2 = self.backup_key()
        assert copy(key1, key2)

    def cleanup(self):
        keys = [self.backup_key(
            datedate.today() - timedelta(days=i)) for i in range(
                MAX_DAY_KEEP_SWAPRANK, MAX_DAY_KEEP_SWAPRANK*2)]
        pool = settings.REDISES["index"]
        pool.execute("DEL", *keys)

    def swap_ranks(self, p, targetID):
        # v1, v2 = PlayerSwapRankRanking.swap(p, targetID)
        v1, v2 = swap(p.entityID, targetID)
        return v1, v2

    def get_target_detail(self, entityID, detail=True):
        originID = entityID
        swaprank = self.get_rank(entityID)
        name = None
        if entityID < 0:
            entityID = int(str(entityID)[:-4])
            config = get_config(RobotNameConfig).get(swaprank)
            if config:
                name = config.name
        if detail:
            detail = get_opponent_detail(entityID, type=LineupType.DEF)
            if not detail.get("pets"):
                detail = get_opponent_detail(entityID, type=LineupType.ATK)
        else:
            detail = g_entityManager.get_players_info([entityID], [
                'entityID', 'name',
                'level',
                'prototypeID',
                'vip',
                'borderID',
                'point',
                'faction_name',
            ])
            if detail:
                detail = detail[0]
        if detail:
            detail['swaprank'] = swaprank
            detail["entityID"] = originID
            if name:
                detail["name"] = name
        return detail

    def swap_refresh(self, p):
        configs = get_config(SwapRuleConfig)
        swaprank = self.get_rank(p.entityID)
        if not swaprank:
            swaprank = PlayerSwapRankRanking.count()
        config = None
        for _, v in configs.items():
            start, end = v.range
            if swaprank >= start and (not end or swaprank <= end):
                config = v
                break
        if not config:
            config = configs[max(configs)]
        result = set([swaprank])
        for i in [1, 2, 3]:
            pers, pere = getattr(config, "match_per%d" % i)
            pers = pers or 1
            pere = pere or 1
            if pers == 0:
                start = config.range[0]
            else:
                start = int(swaprank * (pers / float(100))) or 1
            if pere == 0:
                final = PlayerSwapRankRanking.count()
            else:
                final = int(swaprank * (pere / float(100))) or 1
            if start and final:
                result.add(random.randint(start, final))
        # ugly FIXME
        count = 0
        while len(result) < 4:
            result.add(random.randint(*config.range))
            count += 1
            if count >= 10:
                break
        result.remove(swaprank)
        p.swap_targets = PlayerSwapRankRanking.get_by_ranks(result)
        return p.swap_targets

    def get_rank(self, entityID):
        return PlayerSwapRankRanking.get_rank(entityID)

    def register(self, p):
        try:
            PlayerSwapRankRanking.register(p)
        except RedisReplyError:
            pass
        else:
            p.swap_register_time = int(time.time())
            p.save()

    def add_history(self, entityID, history, fight=None):
        return proxy.add_history(entityID, history, fight=fight)

    def load_rewards(self):
        self.rewards = {}
        pool = settings.REDISES["index"]
        data = convert_list_to_dict(
            pool.execute("HGETALL", SWAPRANK_REWARDS))
        for k, v in data.items():
            self.rewards[k] = ujson.loads(v)

    def dump_rewards(self, key):
        pool = settings.REDISES["index"]
        configs = get_config(SwapRewardConfig)
        rewards = {}
        for k, v in configs.items():
            rewards[k] = v._asdict()
        now = int(time.time())
        self.rewards[key] = [now, rewards]
        cmds = []
        cmds.append((
            "HSETNX", SWAPRANK_REWARDS, key, ujson.dumps([now, rewards])))
        if len(self.rewards) > MAX_DAY_CAN_GIVE_REWARD:
            to_remove = sorted(
                self.rewards.items(),
                key=lambda t: t[0].split("}{")[1].strip("}"),
            )[:-MAX_DAY_CAN_GIVE_REWARD]
            for k, _ in to_remove:
                del self.rewards[k]
                cmds.append(("HDEL",  SWAPRANK_REWARDS, k))
        return pool.execute_pipeline(*cmds)

    def give_rewards(self, p):
        for k in sorted(self.rewards):
            try:
                tm, _ = self.rewards[k]
                dt = datedate.fromtimestamp(tm)
                rg = datedate.fromtimestamp(p.swap_register_time)
                if rg > dt:
                    continue
            except IndexError:
                pass
            self.give_reward(k, p)

    def give_reward(self, key=None, p=None):
        if not key:
            date = datedate.today() - timedelta(days=1)
            key = self.backup_key(date)
            if key not in self.rewards:
                self.dump_rewards(key)
        ranking = SwapRanking(
            Player, 'swaprank',
            pool=settings.REDISES['index'],
            register_on_create=False,
            key=key)
        if key not in self.rewards:
            self.dump_rewards(key)
        # ranking = PlayerSwapRankRanking
        if p:
            ps = [p]
        else:
            ps = g_entityManager.players.values()
        t, configs = self.rewards[key]
        for p in ps:
            if key in p.pvprankreceiveds:
                continue
            rank = ranking.get_rank(p.entityID)
            if not rank:
                continue
            for config in configs.values():
                start, end = config["range"]
                if start:
                    if start > rank:
                        continue
                if end:
                    if end < rank:
                        continue
                rewards = parse_reward(config["rewards"])
                tm = datedate.fromtimestamp(t).strftime(DATE_FMT)
                title, content, ID = get_mail("SwapRank")
                content = content.format(tm, rank)
                self.send_mail(p, title, content, rewards, key, ID)
                break

    def send_mail(self, player, title, content, rewards, key, ID):
        if key in player.pvprankreceiveds:
            return
        send_mail(
            player.entityID,
            title,
            content,
            addition=rewards,
            configID=ID,
            type=MailType.Pvp)
        player.pvprankreceiveds.add(key)  # 防止重复添加
        player.save()
        player.sync()

    def get_rank_list(
            self, rank, page=0, count=50, yesterday=False, detail=True):
        # TODO detail不需要那么多信息
        if yesterday:
            key = self.backup_key(datedate.today() - timedelta(days=1))
            ranking = SwapRanking(
                Player, 'swaprank',
                pool=settings.REDISES['index'],
                register_on_create=False,
                key=key)
        else:
            ranking = PlayerSwapRankRanking

        if rank <= count:
            start = 0
            end = start + count
            offset = count * page
            rankers = ranking.get_by_range(
                start, end,
            )
            offset += 1
        else:
            start = max(rank + count * page, 0)
            end = start + count
            rankers = ranking.get_by_range(
                start, end,
            )
            offset = start
        thumbs = []
        for rank, i in enumerate(rankers, 1):
            detail = self.get_target_detail(i, detail=detail)
            if detail:
                detail['swaprank'] = rank
                thumbs.append(detail)
        return thumbs
g_swapManager = SwapManager()
