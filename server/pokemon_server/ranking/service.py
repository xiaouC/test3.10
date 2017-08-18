# coding:utf-8
import time

from yy.rpc import RpcService, rpcmethod
from yy.message.header import success_msg
from yy.message.header import fail_msg
from yy.utils import convert_list_to_dict
from collections import OrderedDict

import protocol.poem_pb as msgid
from protocol import poem_pb

from pvp.manager import get_opponent_detail

from faction.model import Faction
from player.model import Player
from equip.model import Equip

from .manager import get_ranking
from .manager import get_faction_types
from .manager import g_rankingCampaignManager
from .manager import RANKING_EXTRA_KEYS
from .manager import ranking_extra_encode
from .manager import get_ranking_backup
from .manager import get_ranking_backup_key
from .manager import EXTRA_POSTFIX

from config.configs import get_config
from config.configs import RankingCampaignConfig
from config.configs import RankingCampaignRewardConfig
from config.configs import RankingCampaignRewardByGroupConfig

from common import msgTips
from pet.model import Pet
from protocol.poem_pb import RewardData
from faction.model import FactionRankRanking


class RankingService(RpcService):

    def build_player_item(self, entityID, item):
        detail = get_opponent_detail(entityID)
        item.detail = poem_pb.TargetDetailResponse(**detail)
        item.name = item.detail.name
        item.prototypeID = item.detail.prototypeID

    def build_faction_item(self, factionID, item):
        f = Faction.simple_load(
            factionID, ["name", "leaderID", "memberset"]
        )
        if f:
            l = Player.simple_load(f.leaderID, ["prototypeID"])
            item.name = f.name
            item.prototypeID = l.prototypeID
            item.faction_count = len(f.memberset)
            item.faction_level = FactionRankRanking.get_score(factionID) or 1
            item.entityID = factionID

    @rpcmethod(msgid.RANKING_LIST)
    def ranking_list(self, msgtype, body):
        req = poem_pb.RankingListRequest()
        req.ParseFromString(body)
        p = self.player
        backup = False
        if req.from_campaign:
            campaign = g_rankingCampaignManager.campaigns.get(req.type)
            if campaign and campaign.is_open():
                ranking = get_ranking(req.type)
            else:
                ranking = get_ranking_backup(req.type)
                backup = True
        else:
            ranking = get_ranking(req.type)
        if not ranking:
            return fail_msg(msgtype, reason="没有这个排行榜")
        rankers = convert_list_to_dict(ranking.get_range_by_score(
            "-inf", "+inf", count=30, withscores=True),
            dictcls=OrderedDict).items()
        extras = {}
        key = get_ranking_backup_key(req.type)
        if req.type in RANKING_EXTRA_KEYS:
            entityIDs = [
                int(entityID) for entityID, _ in rankers if entityID
            ]
            if p.entityID not in entityIDs:
                entityIDs.append(p.entityID)
            if entityIDs:
                if backup:
                    extra_key = key + EXTRA_POSTFIX
                    extras.update(
                        zip(entityIDs, ranking.pool.execute(
                            'hmget', extra_key, *entityIDs)))
                else:
                    for obj in Player.batch_load(
                            entityIDs, RANKING_EXTRA_KEYS[req.type]):
                        if obj:
                            extras[obj.entityID] = ranking_extra_encode(
                                obj, req.type)
        rsp = poem_pb.RankingList()
        faction_types = get_faction_types()
        self_rank = None
        for rank, (entityID, score) in enumerate(rankers, 1):
            entityID = int(entityID)
            score = int(float(score))
            if not score:
                continue
            item = rsp.items.add(rank=rank, score=score)
            item.extra = extras.get(entityID)
            if req.type not in faction_types:
                self.build_player_item(entityID, item)
                if entityID == p.entityID:
                    self_rank = rsp.self = item
            else:
                self.build_faction_item(entityID, item)
                if entityID == p.factionID:
                    self_rank = rsp.self = item
        if not self_rank:
            if req.type not in faction_types:
                rank = ranking.get_rank(p.entityID)
                if rank:
                    item = rsp.self
                    item.rank = rank
                    item.score = ranking.get_score(p.entityID)
                    item.extra = extras.get(p.entityID)
                    self.build_player_item(p.entityID, item)
            else:
                rank = ranking.get_rank(p.factionID)
                if rank:
                    item = rsp.self
                    item.rank = rank
                    item.score = ranking.get_score(p.factionID)
                    self.build_faction_item(p.factionID, item)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.RANKING_EXTRA_INFO)
    def ranking_extra_info(self, msgtype, body):
        req = poem_pb.RankingExtraInfoRequest()
        req.ParseFromString(body)
        rsp = poem_pb.RankingExtraInfoResponse()
        if req.type == "PETMAXPOWER":
            try:
                entityID, petID, prototypeID, breaklevel = req.extra.split("_")
                attrs = [
                    'entityID', 'prototypeID', 'level', 'breaklevel',
                    'skill', "relations", "skill1", "skill2", "skill3",
                    "skill4", "skill5"]
                pet = Pet.simple_load(int(petID), Pet.expend_fields(attrs))
                if pet:
                    pet = {a: getattr(pet, a) for a in attrs}
                else:
                    pet = {
                        "prototypeID": int(prototypeID),
                        "breaklevel": int(breaklevel)
                    }
                rsp.pet = pet
            except ValueError:
                return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        elif req.type == "EQUIPMAXPOWER":
            try:
                entityID, equipID, prototypeID, step, level = \
                    req.extra.split("_")
                attrs = [
                    "entityID", "equipID",
                    "prototypeID", "step",
                    "level", "enchant_attrs"]
                equip = Equip.simple_load(
                    int(equipID), Equip.expend_fields(attrs))
                if equip:
                    equip = {a: getattr(equip, a) for a in attrs}
                else:
                    equip = {
                        "prototypeID": int(prototypeID),
                    }
                equip["index"] = 0
                rsp.equip = equip
            except ValueError:
                return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        else:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.RANKING_CAMPAIGN_INFO)
    def ranking_campaign_info(self, msgtype, body):
        now = int(time.time())
        rsp = poem_pb.RankingCampaignList(now=now)
        for k, config in get_config(RankingCampaignConfig).items():
            info = config._asdict()
            campaign = g_rankingCampaignManager.campaigns.get(
                config.ranking)
            if campaign and campaign.is_open():
                ranking = get_ranking(config.ranking)
            else:
                ranking = get_ranking_backup(config.ranking)
            info["rank"] = ranking.get_rank(self.player.entityID)
            rsp.campaigns.add(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.RANKING_CAMPAIGN_REWARD)
    def ranking_campaign_reward(self, msgtype, body):
        req = poem_pb.RankingCampaignRewardListRequest()
        req.ParseFromString(body)
        config = get_config(RankingCampaignConfig).get(req.day)
        if config:
            rewards = get_config(RankingCampaignRewardConfig)
            configs = get_config(
                RankingCampaignRewardByGroupConfig
            ).get(config.group, [])
            configs = [rewards[i.id] for i in configs]
        else:
            configs = []
        rsp = poem_pb.RankingCampaignRewardListResponse()
        for config in configs:
            item = rsp.items.add(**config._asdict())
            item.rewards = [RewardData(**r) for r in config.rewards]
            item.start, item.final = config.range
        return success_msg(msgtype, rsp)
