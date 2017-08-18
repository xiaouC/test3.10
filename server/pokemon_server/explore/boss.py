# coding:utf-8
import time
import cPickle
import gevent
from yy.ranking import NaturalRanking

import settings
from state.base import StateObject, StartState
from config.configs import get_config
from config.configs import BossCampaignConfig
from config.configs import FriendfbRewardByFbIDConfig
from config.configs import FriendfbRewardConfig
from config.configs import FriendfbConfig
from common.index import INDEX_BOSS_REWARD
from entity.manager import g_entityManager
from mail.manager import send_mail
from mail.manager import get_mail
from reward.manager import parse_reward
from gm.proxy import proxy
from player.model import Player
from player.model import PlayerLevelRanking


pool = settings.REDISES["index"]
BOSS_REWARD = INDEX_BOSS_REWARD.render(
    regionID=settings.REGION["ID"],
    sessionID=settings.SESSION["ID"])


class BossCampaign(StateObject):
    def __init__(self, manager, config):
        super(BossCampaign, self).__init__()
        self.manager = manager
        self.config = config
        self.BOSS_CAMPAIGN = "BOSS_CAMPAIGN{%d}_{%d}{%d}" % (
            self.config.ID, settings.SESSION["ID"], settings.REGION["ID"])
        self.BOSS_CAMPAIGN_FLAG = "BOSS_CAMPAIGN_FLAG{%d}_{%d}{%d}" % (
            self.config.ID, settings.SESSION["ID"], settings.REGION["ID"])
        self.BOSS_CAMPAIGN_RANKING = "BOSS_CAMPAIGN_RANKING{%d}_{%d}{%d}" % (
            self.config.ID, settings.SESSION["ID"], settings.REGION["ID"])
        self.BossCampaignRanking = NaturalRanking(
            self.BOSS_CAMPAIGN_RANKING, pool)
        self.identification = "%d_%d_%d" % (
            self.config.start, self.config.end, self.config.ID)

    # {{ Override
    def get_loops(self):
        return [[self.config.start, self.config.end, self.config.ID]]

    def enter_start(self):
        origin = pool.execute(
            "GETSET", self.BOSS_CAMPAIGN_FLAG, self.identification)
        # 为了只初始化一次
        if origin == self.identification:
            return
        self.init_boss()
        self.BossCampaignRanking.clear_raw()

    def execute_start(self):
        self.sync()

    def execute_wait(self):
        # self.give_rewards()  # BOSS死亡才能发奖励
        pass

    def execute_stop(self):
        # 活动结束自动清除自己
        self.stop()

    def stop(self):
        try:
            from campaign.manager import g_campaignManager
            if self.config.ID != g_campaignManager.flower_boss_campaign.flower_boss_config_id:
                del self.manager.campaigns[self.config.ID]
        except KeyError:
            pass
        super(BossCampaign, self).stop()

    def is_open(self):
        if self.state:
            return isinstance(self.state, StartState)
        return False
    # }}

    def init_boss(self):
        self.config.fbID
        info = get_config(FriendfbConfig)[self.config.fbID]
        rs = PlayerLevelRanking.get_range_by_score(
            "-inf", "+inf", count=1, withscores=True)
        if not rs:
            level = 1
        else:
            _, level = rs
        hp = info.active_num * info.dpr * level * level
        pool.execute_pipeline(
            ["DEL",  self.BOSS_CAMPAIGN_RANKING],
            ["HMSET", self.BOSS_CAMPAIGN,
             "HP_%d" % self.config.ID, hp,
             "MAXHP_%d" % self.config.ID, hp])

    def get_boss(self):
        hp, maxhp = pool.execute(
            "HMGET", self.BOSS_CAMPAIGN,
            "HP_%d" % self.config.ID,
            "MAXHP_%d" % self.config.ID)
        return {"hp": int(hp or 0), "maxhp": int(maxhp or 0)}

    def sync(self):
        for p in g_entityManager.players.values():
            p.clear_boss_campaign_opened()
            p.sync()

    def get_by_rank(self, rank):
        return self.BossCampaignRanking.get_by_rank(1)

    def give_rewards(self):
        #  耗时，另起线程
        def run():
            ranks = self.BossCampaignRanking.get_range_by_score(
                "-inf", "+inf", withscores=True)
            configs = get_config(FriendfbRewardConfig)
            group = get_config(
                FriendfbRewardByFbIDConfig).get(self.config.fbID, [])
            configs = [configs[e.ID] for e in group]
            rank = 1
            for index, entityID in enumerate(ranks, 0):
                if index % 2 == 1:
                    continue
                for r in configs:
                    start, end = r.range
                    if rank >= start and (not end or rank <= end):
                        p = g_entityManager.get_player(entityID)
                        rewards = {
                            self.identification: {
                                "rewards": r.rewards,
                                "damage": ranks[rank],
                                "rank": rank
                            }
                        }
                        if p:
                            give_reward(p, rewards=rewards)
                        else:
                            keep_reward(entityID, rewards)
                        break
                rank += 1
        gevent.spawn(run)

    def hurt_boss(self, p, damage):
        rs = int(pool.execute(
            "HINCRBY", self.BOSS_CAMPAIGN,
            "HP_%d" % self.config.ID, -damage))
        total_damage = int(self.BossCampaignRanking.incr_score(
            p.entityID, damage))
        if total_damage > p.friendfb_damages.get(self.config.fbID, 0):
            p.friendfb_damages[self.config.fbID] = total_damage
        return rs

    def load_ranks(self, count=50):
        rankscores = self.BossCampaignRanking.get_range_by_score(
            "-inf", "+inf", count=count, withscores=True,
        )
        ranks = []
        for index, c in enumerate(rankscores):
            if index % 2 == 0:
                p = Player.simple_load(c, [
                    "name", "prototypeID",
                    "level", "borderID",
                    "faction_name"])
                ranks.append({
                    "entityID": p.entityID,
                    "name": p.name,
                    "prototypeID": p.prototypeID,
                    "level": p.level,
                    "borderID": p.borderID,
                    "faction_name": p.faction_name,
                })
            else:
                ranks[-1]["damage"] = c
        return ranks

    def load_rank(self, entityID):
        rank = self.BossCampaignRanking.get_rank(entityID)
        if not rank:
            return {}
        damage = self.BossCampaignRanking.get_score(entityID)
        p = g_entityManager.get_player(entityID)
        if not p:
            p = Player.simple_load(entityID, [
                "name", "prototypeID", "level", "borderID"])
        return {
            "entityID": p.entityID,
            "name": p.name,
            "prototypeID": p.prototypeID,
            "rank": rank,
            "damage": damage,
            "level": p.level,
            "borderID": p.borderID
        }


def give_reward(p, rewards=None):
    if not rewards:
        rs = pool.execute("HGET", BOSS_REWARD, p.entityID)
        if rs:
            rewards = cPickle.loads(rs)
        else:
            return
    for key, info in rewards.items():
        if key in p.boss_campaign_rewards:
            continue
        title, content, ID = get_mail("BossKill")
        content = content.format(info.get("damage", 0), info.get("rank", 0))
        send_mail(
            p.entityID, title, content,
            addition=parse_reward(info.get("rewards", {})),
            configID=ID)
        p.boss_campaign_rewards.add(key)
        p.save()
    pool.execute("HDEL", BOSS_REWARD, p.entityID)


def keep_reward(entityID, rewards):
    rs = pool.execute("HGET", BOSS_REWARD, entityID)
    if rs:
        _rewards = cPickle.loads(rs)
    else:
        _rewards = {}
    _rewards.update(rewards)
    pool.execute("HSET", BOSS_REWARD, entityID, cPickle.dumps(_rewards))


class BossCampaignManager(object):
    def __init__(self):
        self.campaigns = {}

    def start(self):
        now = int(time.time())
        configs = get_config(BossCampaignConfig)
        # 为了start可以重复运行
        # 需要先清除上一个start开始的campaign
        for v in self.campaigns.values():
            v.stop()
        for v in configs.values():
            # 过滤已经过期的活动
            if now > v.end:
                continue
            bc = BossCampaign(self, v)
            bc.start()
            self.campaigns[v.ID] = bc

g_bossCampaignManager = BossCampaignManager()


@proxy.rpc_batch
def notify_boss_campaign_end(campaignID):
    bc = g_bossCampaignManager.campaigns.get(campaignID)
    bc.give_rewards()
