# coding:utf-8
import time
import math
import ujson
import logging
logger = logging.getLogger("group")
from yy.rpc import RpcService
from yy.rpc import rpcmethod

from yy.message.header import success_msg
from yy.message.header import fail_msg

from yy.entity.index import DuplicateIndexException
from yy.entity.base import EntityExistsException

import protocol.poem_pb as msgid
from protocol import poem_pb
from protocol.poem_pb import GveEntity

from pvp.manager import get_opponent_detail

from group.model import Group
from group.model import GroupnameIndexing


from .manager import get_group_info
from .manager import join_group
from .manager import quit_group
from .manager import scan_recommned
from .manager import recommend
from .manager import validate_name
from .manager import boardcast_gve_entity
from .manager import sync_gve_entity
from .manager import quit_gve
from .manager import leave_gve
from .manager import get_gve_entity
from .manager import get_group_rank
from .manager import get_group_score
from .manager import get_group_count
from .manager import update_group_damage
from .manager import get_group_ranking
from .manager import get_group_member_ranking
from .manager import get_group_member_score
from .manager import get_group_member_rank
from .manager import update_group_member_damage
from .manager import set_gve_state
from .manager import gve_is_open
from .manager import gve_is_end
from .manager import gve_is_started
from .manager import give_reward_by_mail
from .manager import sync_gve_entity_index
from .manager import reset_gve
from .manager import reset_player_gve
from .manager import sync_group_damage
from .manager import get_sceneID
from .manager import get_last_date_by_sceneID
from .manager import ONE_DAY

from campaign.manager import g_campaignManager

from config.configs import get_config
from config.configs import SceneInfoConfig
from config.configs import GveFbInfoConfig
from config.configs import GveSceneInfoConfig
from config.configs import GveRankingRewardConfig
from config.configs import GveDamageRewardConfig
from config.configs import GveDamageRewardBySceneConfig
from config.configs import get_cons_value

from reward.manager import apply_reward
from reward.manager import RewardType
from reward.manager import AttrNotEnoughError

from player.model import Player
from player.model import PlayerFightLock

from gm.proxy import proxy
from common import msgTips

import settings
from session.regions import g_regions


def get_region_name(regionID):
    r = g_regions.get(regionID)
    if not r:
        return ""
    return getattr(r, "name", "")


class GroupService(RpcService):

    @rpcmethod(msgid.GROUP_INFO)
    def group_info(self, msgtype, body):
        p = self.player
        req = poem_pb.GroupInfoRequest()
        req.ParseFromString(body)
        groupID = req.groupID or p.groupID
        info = get_group_info(groupID)
        if not info:
            return fail_msg(msgtype, msgTips.FAIL_MSG_GROUP_NOT_FOUND)
        rsp = poem_pb.GroupInfo(**info)
        if groupID == p.groupID:
            intimate = info.get("intimate", 0)
            if intimate != p.group_total_intimate:
                p.group_total_intimate = intimate
                p.save()
                p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.GROUP_CREATE)
    def group_create(self, msgtype, body):
        p = self.player
        if p.groupID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_GROUP_ALREADY_JOINED)
        req = poem_pb.GroupCreate()
        req.ParseFromString(body)
        name, err = validate_name(req.name)
        if err:
            return fail_msg(msgtype, err)
        try:
            GroupnameIndexing.register(0, name)  # 占位
        except DuplicateIndexException:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_GROUP_DUPLICATE_FACTION_NAME)
        try:
            g = Group.create(
                name=name, leaderID=p.entityID)
            g.save()
        except EntityExistsException:
            GroupnameIndexing.unregister(name)
            return fail_msg(msgtype, msgTips.FAIL_MSG_GROUP_CREATE_FAIL)
        err = join_group(p.entityID, g.groupID)
        if err:
            GroupnameIndexing.unregister(name)
            return fail_msg(msgtype, err)
        GroupnameIndexing.pool.execute(
            'HSET', GroupnameIndexing.key, name, g.groupID)  # 更新
        recommend(g.groupID)
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.GROUP_ALTER_NAME)
    def group_alter_name(self, msgtype, body):
        p = self.player
        req = poem_pb.GroupAlterName()
        req.ParseFromString(body)
        name, err = validate_name(req.name)
        if err:
            return fail_msg(msgtype, err)
        try:
            GroupnameIndexing.register(0, name)  # 占位
        except DuplicateIndexException:
            GroupnameIndexing.unregister(name)
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_GROUP_DUPLICATE_FACTION_NAME)
        g = Group.simple_load(p.groupID, ["name"])
        g.name = name
        g.save()
        GroupnameIndexing.pool.execute(
            'HSET', GroupnameIndexing.key, name, g.groupID)  # 更新
        return success_msg(msgtype, '')

    @rpcmethod(msgid.GROUP_SEARCH)
    def group_search(self, msgtype, body):
        rsp = poem_pb.GroupInfos()
        groups = scan_recommned(25)
        for groupID in groups:
            info = get_group_info(groupID)
            if not info:
                continue
            rsp.infos.add(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.GROUP_QUIT)
    def group_quit(self, msgtype, body):
        p = self.player
        err = quit_group(p.entityID, p.groupID)
        if err:
            return fail_msg(msgtype, err)
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.GROUP_KICK)
    def group_kick(self, msgtype, body):
        p = self.player
        req = poem_pb.GroupKick()
        req.ParseFromString(body)
        g = Group.simple_load(p.groupID, ["leaderID", "gve_last_kick_time"])
        if p.entityID != g.leaderID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_GROUP_PERMISSION_DENIED)
        now = int(time.time())
        if now < g.gve_last_kick_time + ONE_DAY:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_GROUP_KICK_TOO_FREQUENTLY)
        err = proxy.kick_group_member(req.entityID, p.groupID)
        if err:
            return fail_msg(msgtype, err)
        g.gve_last_kick_time = now
        g.save()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.GROUP_ALLOW)
    def group_allow(self, msgtype, body):
        p = self.player
        req = poem_pb.GroupAllow()
        req.ParseFromString(body)
        g = Group.simple_load(p.groupID, [
            "leaderID", "applys", "gve_last_kick_time"])
        if p.entityID != g.leaderID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_GROUP_PERMISSION_DENIED)
        now = int(time.time())
        if now < g.gve_last_kick_time + ONE_DAY:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_GROUP_KICK_TOO_FREQUENTLY_TO_ALLOW)
        err = proxy.allow_group_member(req.entityID, p.groupID)
        if err:
            return fail_msg(msgtype, err)
        g.applys.load()
        p.group_applys = g.applys
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.GROUP_DENY)
    def group_deny(self, msgtype, body):
        p = self.player
        req = poem_pb.GroupDeny()
        req.ParseFromString(body)
        g = Group.simple_load(p.groupID, ["leaderID", "applys"])
        g.applys.load()
        if p.entityID != g.leaderID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_GROUP_PERMISSION_DENIED)
        try:
            del g.applys[req.entityID]
        except KeyError:
            pass
        p.group_applys = g.applys
        g.save()
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.GROUP_INVITE)
    def group_invite(self, msgtype, body):
        p = self.player
        req = poem_pb.GroupInvite()
        req.ParseFromString(body)
        err = proxy.invite_group_member(req.entityID, p.groupID, p.name)
        if err:
            return fail_msg(msgtype, err)
        g = Group.simple_load(p.groupID, "invites")
        g.invites.load()
        g.invites.add(req.entityID)
        g.save()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.GROUP_APPLY)
    def group_apply(self, msgtype, body):
        p = self.player
        req = poem_pb.GroupApply()
        req.ParseFromString(body)
        g = Group.simple_load(req.groupID, ["leaderID"])
        now = int(time.time())
        if now < p.group_last_kicked_time + ONE_DAY:
            return fail_msg(msgtype, msgTips.FAIL_MSG_GROUP_KICKED_RECENTLY)
        err = proxy.apply_group_member(g.leaderID, req.groupID, p.entityID)
        if err:
            return fail_msg(msgtype, err)
        return success_msg(msgtype, "")

    @rpcmethod(msgid.GROUP_APPLY_LIST)
    def group_apply_list(self, msgtype, body):
        p = self.player
        g = Group.simple_load(p.groupID, ["leaderID"])
        if p.entityID != g.leaderID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_GROUP_PERMISSION_DENIED)
        rsp = poem_pb.GroupApplyList()
        for i in p.group_applys or []:
            info = get_opponent_detail(i)
            rsp.members.add(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.GVE_JOIN)
    def gve_join(self, msgtype, body):
        p = self.player
        sceneID = get_sceneID()
        g = Group.simple_load(p.groupID, ["gve_joineds", "gve_activateds"])
        # reset_gve(g.groupID)
        g.gve_joineds.load()
        if p.entityID not in g.gve_joineds:
            g.gve_joineds.append(p.entityID)
            g.save()
        joiners = []
        rsp = poem_pb.GveJoinResponse()
        for index, e in enumerate(g.gve_joineds):
            info = {
                "id": e, "index": index,
                "state": GveEntity.GveEntityStateNormal
            }
            if e == p.entityID:
                p.gve_index = index
                if not gve_is_open(p) and gve_is_end(p):
                    p.gve_state = GveEntity.GveEntityStateNormal
                set_gve_state(p, GveEntity.GveEntityStateNormal)
                info.update(
                    prototypeID=p.prototypeID,
                    name=p.name)
            else:
                joiner = Player.simple_load(
                    e, ["prototypeID", "name"])
                info.update(
                    prototypeID=joiner.prototypeID,
                    name=joiner.name)
            rsp.entities.add(**info)
            joiners.append(e)
        rsp.sceneID = sceneID
        g.gve_activateds.load()
        rsp.activateds = g.gve_activateds
        rsp.is_end = gve_is_end(p)
        p.save()
        # if p.entityID not in g.gve_activateds:
        sync_gve_entity_index(joiners)
        # if p.gve_state == GveEntity.GveEntityStateDead:
        #     sync_gve_entity(joiners, p.entityID)
        # else:
        #     sync_gve_entity(
        #         joiners, p.entityID, GveEntity.GveEntityStateNormal)
        sync_gve_entity(joiners, p.entityID, GveEntity.GveEntityStateJoin)
        logger.debug("join")
        logger.debug(rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.GVE_QUIT)
    def gve_quit(self, msgtype, body):
        logger.debug("quit")
        p = self.player
        quit_gve(p)
        return success_msg(msgtype, '')

    @rpcmethod(msgid.GVE_LEAVE)
    def gve_leave(self, msgtype, body):
        logger.debug("leave")
        p = self.player
        leave_gve(p)
        return success_msg(msgtype, '')

    @rpcmethod(msgid.GVE_START)
    def gve_start(self, msgtype, body):
        p = self.player
        if not gve_is_open(p):
            return fail_msg(msgtype, msgTips.FAIL_MSG_GROUP_GVE_NOT_OPEN)
        if gve_is_end(p):
            return fail_msg(msgtype, msgTips.FAIL_MSG_GROUP_GVE_ALREADY_END)
        sceneID = get_sceneID()
        g = Group.simple_load(p.groupID, [
            "leaderID", "gve_joineds",
            "gve_activateds", "gve_start_time",
            "gve_progress", "gve_end_cd"])
        scene = get_config(SceneInfoConfig)[sceneID]
        now = int(time.time())
        if not gve_is_started(p):
            if p.entityID != g.leaderID:
                return fail_msg(
                    msgtype, msgTips.FAIL_MSG_GROUP_PERMISSION_DENIED)
            g.gve_joineds.load()
            if len(g.gve_joineds) <= 1:
                return fail_msg(
                    msgtype, msgTips.FAIL_MSG_GROUP_GVE_START_SOLO)
            g.gve_activateds.load()
            g.gve_activateds.clear()
            g.gve_activateds.extend(g.gve_joineds)
            g.gve_progress.load()
            g.gve_progress.clear()
            for fb in scene.fbs:
                config = get_config(GveFbInfoConfig)[fb]
                g.gve_progress[fb] = config.boss_hp
            g.gve_end_cd = g_campaignManager.gve_campaign.get_end_time()
            g.gve_start_time = now
            g.save()
            set_gve_state(p, GveEntity.GveEntityStateNormal, force=True)
            p.save()
            sendto = list(g.gve_activateds)
        else:
            g.gve_activateds.load()
            if p.entityID not in g.gve_activateds:
                return fail_msg(
                    msgtype, msgTips.FAIL_MSG_GROUP_GVE_ALREADY_STARTED)
            p.gve_groupdamage = get_group_score(sceneID, p.groupID)
            g.gve_joineds.load()
            g.gve_progress.load()
            set_gve_state(p, GveEntity.GveEntityStateNormal)
            sync_gve_entity(list(g.gve_activateds), p.entityID)
            sendto = [p.entityID]
        rsp = poem_pb.GveStartResponse()
        for e in g.gve_activateds:
            info = get_gve_entity(e)
            rsp.entities.add(**info)
        configs = get_config(GveFbInfoConfig)
        for index, fb in enumerate(scene.fbs, 3):
            fb = configs[fb]
            hp = g.gve_progress.get(fb.ID, fb.boss_hp)
            if hp > 0:
                state = GveEntity.GveEntityStateNormal
            else:
                state = GveEntity.GveEntityStateDead
            info = {
                "id": fb.ID,
                "state": state,
                "index": index,
                "hp": hp,
                "maxhp": fb.boss_hp
            }
            rsp.entities.add(**info)
        rsp.sceneID = sceneID
        rsp.rest = max(g_campaignManager.gve_campaign.get_end_time() - now, 0)
        boardcast_gve_entity(sendto, success_msg(msgtype, rsp))

    @rpcmethod(msgid.GVE_FIGHT)
    def gve_fight(self, msgtype, body):
        p = self.player
        if not gve_is_open(p):
            return fail_msg(msgtype, msgTips.FAIL_MSG_GROUP_GVE_NOT_OPEN)
        if gve_is_end(p):
            return fail_msg(msgtype, msgTips.FAIL_MSG_GROUP_GVE_ALREADY_END)
        req = poem_pb.GveFight()
        req.ParseFromString(body)
        g = Group.simple_load(
            p.groupID, ["gve_activateds", "gve_progress"])
        g.gve_progress.load()
        config = get_config(GveFbInfoConfig)[req.fbID]
        maxhp = config.boss_hp
        hp = g.gve_progress.get(req.fbID, maxhp)
        if hp <= 0:
            return fail_msg(msgtype, reason="目标已经死亡")
        rsp = poem_pb.GveFightResponse(hp=hp, maxhp=maxhp)
        p.gve_state = GveEntity.GveEntityStateFight
        p.gve_target = req.fbID
        p.save()
        g.gve_activateds.load()
        sync_gve_entity(g.gve_activateds, p.entityID)
        rsp.verify_code = PlayerFightLock.lock(p.entityID, force=True)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.GVE_FIGHT_END)
    def gve_fight_end(self, msgtype, body):
        p = self.player
        error_code = 0
        if not gve_is_open(p):
            error_code = msgTips.FAIL_MSG_GROUP_GVE_NOT_OPEN
        elif gve_is_end(p):
            error_code = msgTips.FAIL_MSG_GROUP_GVE_ALREADY_END
        elif not p.gve_target:
            error_code = msgTips.FAIL_MSG_GROUP_GVE_ALREADY_END
        else:
            sceneID = get_sceneID()
            req = poem_pb.GveFightEnd()
            req.ParseFromString(body)
            if not PlayerFightLock.unlock(p.entityID, req.verify_code):
                return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
            hurt = req.fight.total_damage or 1
            win = req.fight.fightResult
            hp = int(Group.pool.execute(
                "HINCRBY", "gve_progress_g{%s}" % p.groupID,
                p.gve_target, -hurt))
            update_group_damage(sceneID, p.groupID, hurt)
            update_group_member_damage(sceneID, p.entityID, hurt)
            fbID = p.gve_target
            scene = get_config(SceneInfoConfig)[sceneID]
            index = scene.fbs.index(fbID) + 3
            config = get_config(GveFbInfoConfig)[fbID]
            maxhp = config.boss_hp
            g = Group.simple_load(
                p.groupID, [
                    "gve_end_cd",
                    "gve_activateds",
                    "gve_deads",
                    "gve_rewards",
                    "gve_activateds_detail"])
            g.gve_activateds.load()
            if not win:
                p.gve_target = 0
                set_gve_state(p, GveEntity.GveEntityStateDead, force=True)
                g.gve_deads.load()
                g.gve_deads.add(p.entityID)
                count = len(g.gve_deads)
                if count >= len(g.gve_activateds):
                    g.gve_end_cd = int(time.time()) + 19
                g.save()
            else:
                p.gve_target = 0
                set_gve_state(
                    p, GveEntity.GveEntityStateNormal, force=True)
            boss_state = GveEntity.GveEntityStateNormal \
                if hp > 0 else GveEntity.GveEntityStateDead
            p.gve_damage += hurt
            total_damage = max(
                p.gve_damage, get_group_score(sceneID, p.groupID))
            sync_group_damage(p.groupID, total_damage)
            gve_scene = get_config(GveSceneInfoConfig)[sceneID]
            max_damage = gve_scene.max_damage
            p.gve_score = int(10000 * p.gve_damage / float(max_damage))
            x = p.gve_damage / float(total_damage)
            p.gve_addition = int((
                0.25 * (pow(
                    x, 3) - 7 * pow(
                        x, 2) + 7 * x) + p.gve_damage / float(
                            max_damage)) * 100)
            p.gve_groupdamage = total_damage
            g.gve_rewards.load()
            rewards = ujson.loads(p.gve_basereward)
            g.gve_rewards[p.entityID] = [
                rewards, g.gve_end_cd, p.gve_addition]
            for k in g.gve_activateds:
                if k in g.gve_rewards:
                    v = g.gve_rewards[k]
                    v[1] = g.gve_end_cd
                    g.gve_rewards[k] = v
            g.gve_activateds_detail.load()
            g.gve_activateds_detail[p.entityID] = {
                "addition": p.gve_addition,
                "damage": p.gve_damage,
                "score": p.gve_score,
                "total_damage": p.gve_groupdamage,
            }
            g.save()
            #  a = 个人总伤害
            #  b = 团队总伤害
            #  x = a/b
            #  max = 理论最大伤害（配在gve副本表中，每个副本都有相应的max值）
            #
            #  奖励加成
            #  y = 0.25 * ( x^3 - 7*x^2 + 7*x ) + a/max
            #  保留2位小数，换算成百分比可得 XX%
            #
            #  个人评分
            #  评分 = int(10000*a/max)
            p.save()
            p.sync()
            sync_gve_entity(g.gve_activateds, p.entityID)
            boardcast_gve_entity(
                g.gve_activateds, success_msg(
                    msgid.SYNC_GVE_ENTITY, poem_pb.GveEntity(**{
                        "id": fbID,
                        "index": index,
                        "state": boss_state,
                        "hp": hp,
                        "maxhp": maxhp,
                    })))
        rsp = poem_pb.GveFightEndResponse()
        rsp.error_code = error_code
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.GVE_REBORN)
    def gve_reborn(self, msgtype, body):
        p = self.player
        if not gve_is_open(p):
            return fail_msg(msgtype, msgTips.FAIL_MSG_GROUP_GVE_NOT_OPEN)
        if gve_is_end(p):
            return fail_msg(msgtype, msgTips.FAIL_MSG_GROUP_GVE_ALREADY_END)
        end_time = g_campaignManager.gve_campaign.get_end_time()
        if p.gve_state != GveEntity.GveEntityStateDead:
            return fail_msg(msgtype, reason="没有死亡")
        if p.gve_reborn_rest_count <= 0:
            return fail_msg(msgtype, reason="没有复活次数了")
        try:
            apply_reward(
                p, {},
                cost={"gold": get_cons_value("GveRebornCost")},
                type=RewardType.GveReborn)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="钻石不足")
        count = int(Group.pool.execute(
            "SREM", "gve_deads_g{%s}" % p.groupID, p.entityID))
        g = Group.simple_load(
            p.groupID, ["gve_end_cd", "gve_activateds"])
        g.gve_activateds.load()
        if count < len(g.gve_activateds):
            g.gve_end_cd = end_time
            g.save()
        p.gve_state = GveEntity.GveEntityStateNormal
        p.gve_buff = get_cons_value("GveBuffAddition")
        p.gve_reborn_rest_count -= 1
        sync_gve_entity(g.gve_activateds, p.entityID)
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.GVE_END_PANEL)
    def gve_end_panel(self, msgtype, body):
        p = self.player
        now = int(time.time())
        g = Group.simple_load(
            p.groupID, [
                "gve_end_cd",
                "gve_max_damage",
                "gve_end_activateds",
                "gve_activateds_detail"])
        if now >= g.gve_end_cd:
            basereward = p.gve_basereward
            addition = p.gve_addition
            reset_player_gve(p)
            reset_gve(p.groupID)
            sceneID = get_sceneID()
            damage = get_group_score(sceneID, p.groupID)
            rank = get_group_rank(sceneID, p.groupID)
            count = get_group_count(sceneID)
            if count == 0:
                percent = 0
            else:
                percent = math.ceil(rank / float(count) * 100)
            maxdamage = g.gve_max_damage
            rsp = poem_pb.GveEndPanel(
                damage=damage, rank=rank,
                count=count, percent=percent,
                maxdamage=maxdamage,
                rewards=basereward,
                addition=addition,
            )
            g.gve_end_activateds.load()
            g.gve_activateds_detail.load()
            for i in g.gve_end_activateds:
                info = get_gve_entity(i)
                info.update(g.gve_activateds_detail.get(i, {}))
                rsp.members.add(entityID=i, **info)
            give_reward_by_mail(p)
            return success_msg(msgtype, rsp)
        else:
            return fail_msg(msgtype, reason="活动还没有结束")

    @rpcmethod(msgid.GVE_GROUP_RANKING)
    def gve_group_ranking(self, msgtype, body):
        p = self.player
        req = poem_pb.GroupRankingRequest()
        req.ParseFromString(body)
        sceneID = req.sceneID
        if not sceneID:
            sceneID = get_sceneID()
            ranks = get_group_ranking(sceneID, count=10)
        else:
            dt = get_last_date_by_sceneID(sceneID)
            ranks = get_group_ranking(sceneID, count=10, date=dt)
        rsp = poem_pb.GroupRanking()
        for rank, (regionID, groupID, score) in enumerate(ranks):
            info = proxy.get_group_across_region(regionID, groupID)
            info.update(
                region=get_region_name(regionID),
                score=score,
                regionID=regionID,
            )
            rsp.items.add(**info)
        score = get_group_score(sceneID, p.groupID)
        if score and p.groupID:
            regionID = settings.REGION["ID"]
            info = proxy.get_group_across_region(
                regionID, p.groupID)
            info.update({
                "score": score,
                "rank": get_group_rank(sceneID, p.groupID),
                "region": get_region_name(regionID),
            })
            rsp.self = info
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.GVE_GROUP_MEMBER_DETAIL)
    def gve_group_member_detail(self, msgtype, body):
        req = poem_pb.GroupMemberDetailAcrossRegion()
        req.ParseFromString(body)
        detail = proxy.get_group_member_detail_across_region(
            req.regionID, req.entityID)
        rsp = poem_pb.TargetDetailResponse(**detail)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.GVE_GROUP_MEMBER_RANKING)
    def gve_group_member_ranking(self, msgtype, body):
        p = self.player
        req = poem_pb.GroupMemberRankingRequest()
        req.ParseFromString(body)
        sceneID = req.sceneID
        if not sceneID:
            sceneID = get_sceneID()
            ranks = get_group_member_ranking(sceneID, count=10)
        else:
            dt = get_last_date_by_sceneID(sceneID)
            ranks = get_group_member_ranking(sceneID, count=10, date=dt)
        rsp = poem_pb.GroupMemberRanking()
        for rank, (regionID, entityID, score) in enumerate(ranks):
            info = proxy.get_group_member_across_region(regionID, entityID)
            info.update(
                score=score,
                region=get_region_name(regionID),
            )
            rsp.items.add(**info)
        score = int(get_group_member_score(sceneID, p.entityID))
        if score:
            regionID = settings.REGION["ID"]
            info = proxy.get_group_member_across_region(
                regionID, p.entityID)
            info.update({
                "score": score,
                "rank": get_group_member_rank(sceneID, p.entityID),
                "region": get_region_name(regionID),
            })
            rsp.self = info
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.GVE_GROUP_RANKING_REWARD)
    def gve_group_ranking_reward(self, msgtype, body):
        p = self.player
        req = poem_pb.GroupRankingRewardRequest()
        req.ParseFromString(body)
        sceneID = req.sceneID
        if not sceneID:
            sceneID = get_sceneID()
        damage = get_group_score(sceneID, p.groupID)
        rsp = poem_pb.GroupRankingReward()
        rank = get_group_rank(sceneID, p.groupID)
        g = Group.simple_load(
            p.groupID, ["gve_max_damage"])
        maxdamage = g.gve_max_damage
        rsp.damage = damage
        if damage:
            rsp.rank = rank
        rsp.maxdamage = maxdamage
        configs = get_config(GveRankingRewardConfig)
        sceneID = get_sceneID()
        for k, v in configs.items():
            if v.sceneID != sceneID:
                continue
            start, final = v.range
            rsp.items.add(
                rewards=v.rewards,
                start=start, final=final)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.GVE_GROUP_DAMAGE_REWARD)
    def gve_group_damage_reward(self, msgtype, body):
        sceneID = get_sceneID()
        group = get_config(GveDamageRewardBySceneConfig).get(sceneID, [])
        configs = get_config(GveDamageRewardConfig)
        rsp = poem_pb.GroupDamageReward()
        for each in group:
            config = configs.get(each.ID)
            rsp.items.add(
                damage=config.damage,
                rewards=config.rewards)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.GVE_SCENE_LIST)
    def gve_scene_list(self, msgtype, body):
        sceneID = get_sceneID()
        configs = get_config(GveSceneInfoConfig)
        rsp = poem_pb.GveSceneList()
        flag = False
        for k, v in configs.items():
            if not flag and k != sceneID:
                continue
            elif k == sceneID:
                flag = True
                continue
            rsp.scenes.add(sceneID=k, **v._asdict())
        for k, v in configs.items():
            if k == sceneID:
                break
            rsp.scenes.add(sceneID=k, **v._asdict())
        return success_msg(msgtype, rsp)
