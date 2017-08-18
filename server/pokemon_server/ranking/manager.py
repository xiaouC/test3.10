# coding:utf-8
import time
import settings
from gevent import Greenlet
from datetime import date as datedate
from collections import OrderedDict
from yy.ranking.manager import NaturalRankingWithJoinOrder
from player import model as player_model
from state.base import StateObject
from state.base import StartState
from gm.proxy import proxy
from config.configs import get_config
from config.configs import RankingCampaignConfig
from config.configs import RankingCampaignRewardConfig
from config.configs import RankingCampaignRewardByGroupConfig
from config.configs import get_cons_value
from player.model import Player
from mail.manager import get_mail
from mail.manager import send_mail
from faction.model import Faction
from faction.model import FactionSkillRanking
from faction.model import FactionRankRanking
from entity.manager import g_entityManager
from yy.utils import convert_list_to_dict
from reward.manager import parse_reward
from yy.utils import convert_dict_to_list


BACKUP_POSTFIX = '_BACKUP'
EXTRA_POSTFIX = '_EXTRA'

RANKING_EXTRA_KEYS = {
    'EQUIPMAXPOWER': [
        'entityID',
        'ranking_equip_power_entityID',
        'ranking_equip_power_prototypeID',
        'ranking_equip_power_step',
        'ranking_equip_power_level'
    ],
    'PETMAXPOWER': [
        'entityID',
        'ranking_pet_power_entityID',
        'ranking_pet_power_prototypeID',
        'ranking_pet_power_breaklevel'
    ],
}

RankingTypes = OrderedDict([
    ("STAR", (60, player_model.PlayerStarRanking)),
    ("PROGRESS", (60, player_model.PlayerProgressRanking)),
    ("ADVANCED", (None, player_model.PlayerAdvancedRanking)),
    ("MAXPOWER", (10000, player_model.PlayerMaxPowerRanking)),
    ("FACTIONLEVEL", (None, FactionRankRanking)),
    ("FACTIONSKILL", (None, FactionSkillRanking)),
    ("ROBMINE1", (None, player_model.PlayerRobmine1Ranking)),
    ("ROBMINE2", (None, player_model.PlayerRobmine2Ranking)),
    ("BOSSKILL", (None, player_model.PlayerBossKillRanking)),
    ("LEVEL", (6, player_model.PlayerLevelRanking)),
    ("AMBITION", (None, player_model.PlayerAmbitionCountRanking)),
    ("PETCOUNT", (25, player_model.PlayerPetCountRanking)),
    ("PETMAXPOWER", (1000, player_model.PlayerBestPetRanking)),
    ("EQUIPMAXPOWER", (100, player_model.PlayerBestEquipRanking)),
    ("CLIMB_TOWER", (100, player_model.PlayerClimbTowerRanking)),
])


def get_ranking_key(type):
    _, ranking = RankingTypes[type]
    return ranking.key


def get_ranking_limit(type):
    limit, _ = RankingTypes[type]
    return limit


def get_ranking(type):
    try:
        _, ranking = RankingTypes[type]
    except KeyError:
        return None
    return ranking


def get_ranking_backup_key(type):
    return get_ranking_key(type) + BACKUP_POSTFIX


def get_ranking_backup(type):
    key = get_ranking_backup_key(type)
    ranking = NaturalRankingWithJoinOrder(
        key, settings.REDISES["index"])
    return ranking


def get_faction_types():
    return ["FACTIONLEVEL", "FACTIONSKILL"]


class RankingCampaignManager(object):
    def __init__(self):
        self.campaigns = {}
        self.deadline = 0
        self.reserved = 0
        configs = get_config(RankingCampaignConfig)
        for day, config in configs.items():
            campaign = self.campaigns[config.ranking] = RankingCampaign(config)
            campaign.start()
            deadline = config.final + get_cons_value(
                "RankingCampaignDeadlineTime")
            reserved = config.start + get_cons_value(
                "RankingCampaignReservedTime")
            if deadline > self.deadline:
                self.deadline = deadline
            if not reserved or reserved < self.reserved:
                self.reserved = reserved

    def started(self, now=None):
        if not now:
            now = int(time.time())
        return now >= self.reserved and now < self.deadline

    def reload(self):
        for ranking, campaign in self.campaigns.items():
            campaign.stop()
        self.__init__()


def ranking_extra_encode(p, type):
    if type not in RANKING_EXTRA_KEYS:
        return
    return '_'.join(map(str, (
        getattr(p, f) for f in RANKING_EXTRA_KEYS[type])))


def backup_extras(type, ranking, backup_key, count=30):
    extra_key = backup_key + EXTRA_POSTFIX
    entityIDs = ranking.get_by_range(0, count)
    extras = {}
    for p in Player.batch_load(entityIDs, RANKING_EXTRA_KEYS[type]):
        if p is None:
            continue
        extras[p.entityID] = ranking_extra_encode(p, type)
    ranking.pool.execute_pipeline(
        ('del', extra_key),
        ['hmset', extra_key] + list(convert_dict_to_list(extras)),
    )


class RankingCampaign(StateObject):

    def __init__(self, config):
        super(RankingCampaign, self).__init__()
        self.type = config.ranking
        self.config = config
        self.loop = None

    def is_open(self):
        return isinstance(self.state, StartState)

    def get_loops(self):
        return [[self.config.start, self.config.final, self.config.day]]

    def backup(self):
        if self.type not in RankingTypes:
            return
        ranking = get_ranking(self.type)
        backup_key = get_ranking_backup_key(self.type)
        ranking.pool.execute(
            'ZUNIONSTORE', backup_key, 1, ranking.key)
        if self.type in RANKING_EXTRA_KEYS:
            backup_extras(self.type, ranking, backup_key)

    def give_reward(self, date=None):
        if not date:
            now = int(time.time())
            tm = date = datedate.fromtimestamp(now).strftime("%Y-%m-%d")
        else:
            tm = date
        ranking = get_ranking_backup(self.type)
        key = ranking.key
        ll = get_config(RankingCampaignRewardByGroupConfig).get(
            self.config.group, [])
        configs = get_config(RankingCampaignRewardConfig)
        configs = [configs[i.id] for i in ll]
        key = "%s{%s}" % (key, tm)
        limit = get_ranking_limit(self.type)
        if limit is not None:
            rankers = ranking.get_range_by_score(
                limit, "+inf", withscores=True)
        else:
            rankers = ranking.get_range_by_score(
                "-inf", "+inf", withscores=True)
        rankers = convert_list_to_dict(
            rankers, dictcls=OrderedDict).items()
        for rank, (entityID, score) in enumerate(rankers, 1):
            config = None
            for c in configs:
                start, end = c.range
                if start:
                    if start > rank:
                        continue
                if end:
                    if end < rank:
                        continue
                config = c
            if not config:
                continue
            title, content, ID = get_mail("RankingReward")
            content = content.format(
                self.config.day, self.config.title, rank)
            if self.type in get_faction_types():
                f = Faction.simple_load(entityID, [
                    "leaderID", "memberset"])
                for i in set(f.memberset):
                    if i == f.leaderID:
                        rewards = parse_reward(config.rewards)
                    else:
                        rewards = parse_reward(config.rewards2)
                    try:
                        proxy.ranking_send_mail(
                            i, title, content, rewards, key, ID)
                    except AttributeError:
                        pass
            else:
                rewards = parse_reward(config.rewards)
                try:
                    proxy.ranking_send_mail(
                        entityID, title, content, rewards, key, ID)
                except AttributeError:
                    pass

    def enter_stop(self):
        self.backup()
        self.loop = Greenlet.spawn(self.give_reward)


def ranking_send_mail_offline(entityID, title, content, rewards, key, ID):
    p = Player.simple_load(entityID, ["rankingreceiveds"])
    if p:
        if key in p.rankingreceiveds:
            return
    if not int(Player.pool.execute(
            "HSET", "ranking_receiveds_p{%d}" % entityID, key, ""
            ) or 0):
        return
    send_mail(entityID, title, content, addition=rewards, configID=ID)


@proxy.rpc(failure=ranking_send_mail_offline)
def ranking_send_mail(entityID, title, content, rewards, key, ID):
    if not int(Player.pool.execute(
            "HSET", "ranking_receiveds_p{%d}" % entityID, key, ""
            ) or 0):
        return
    p = g_entityManager.get_player(entityID)
    if p:
        if key in p.rankingreceiveds:
            return
        p.ranking_receiveds.load()
        send_mail(
            p.entityID,
            title,
            content,
            addition=rewards,
            configID=ID)
        p.save()
        p.sync()


g_rankingCampaignManager = RankingCampaignManager()
