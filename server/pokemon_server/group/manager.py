# coding:utf-8
import time
import logging
logger = logging.getLogger("group")
from datetime import date as datedate
from datetime import datetime
from datetime import timedelta
from collections import OrderedDict

from yy.message.header import success_msg
from yy.utils import trie

from common import msgTips

from protocol import poem_pb
from protocol import poem_pb as msgid
from protocol.poem_pb import GveEntity

from config.configs import forbid_names_trie
from config.configs import get_config
from config.configs import GveRankingRewardBySceneIDConfig
from config.configs import GveRankingRewardConfig
from config.configs import GveSceneInfoByWeekConfig
from config.configs import GveSceneInfoConfig

from entity.manager import g_entityManager
from player.manager import g_playerManager
from campaign.manager import g_campaignManager

from pvp.manager import get_opponent_detail
from reward.manager import parse_reward

from group.model import Group
from group.model import GroupRecommendIndexing

from player.model import Player
from player.model import PlayerOnlineIndexing

from mail.manager import send_mail
from mail.manager import get_mail

from gm.proxy import proxy
from gm.proxy import urljoin
from gm.proxy import PROXY
from gm.proxy import set_query_string
from gm.proxy import get_poolmanager
from urllib import urlencode

import settings

SUCCESS = 0
MAX_MEMBERS_COUNT = 3
NAME_LENGTH_MAX = 14
NAME_LENGTH_MIN = 4
DATETIMEFMT = "%Y-%m-%d %H:%m:%S"
ONE_DAY = 86400


def recommend(groupID):
    GroupRecommendIndexing.register(groupID)


def unrecommend(groupID):
    GroupRecommendIndexing.unregister(groupID)


def isrecommend(groupID):
    return GroupRecommendIndexing.exists(groupID)


def scan_recommned(count):
    return map(int, GroupRecommendIndexing.randmembers(count=count))


def validate_name(name):
    name = name.strip()
    uname = unicode(name)
    if not uname:
        return uname, msgTips.FAIL_MSG_GROUP_NAME_EMPTY
    if len(uname) > NAME_LENGTH_MAX:
        return uname, msgTips.FAIL_MSG_GROUP_NAME_TOOLONG
    if len(uname) < NAME_LENGTH_MIN:
        return uname, msgTips.FAIL_MSG_GROUP_NAME_TOOSHORT
    if trie.trie_contains(forbid_names_trie, uname):
        return uname, msgTips.FAIL_MSG_GROUP_NAME_INVALID
    return name, SUCCESS


def join_group(entityID, groupID):
    now = int(time.time())
    p = g_entityManager.get_player(entityID)
    if not p:
        p = Player.simple_load(entityID, ["groupID", "group_last_kicked_time"])
    if p.groupID:
        return msgTips.FAIL_MSG_GROUP_ALREADY_JOINED
    if now < p.group_last_kicked_time + ONE_DAY:
        return msgTips.FAIL_MSG_GROUP_KICKED_RECENTLY
    g = Group.simple_load(groupID, ["members", "applys"])
    g.members.load()
    g.applys.load()
    if len(g.members) >= MAX_MEMBERS_COUNT:
        return msgTips.FAIL_MSG_GROUP_LIMITED_EXCEED
    if p.entityID in g.members:
        return msgTips.FAIL_MSG_GROUP_ALREADY_JOINED_THIS
    g.members[p.entityID] = {
        "jointime": now, "intimate": 0}
    if len(g.members) >= MAX_MEMBERS_COUNT:
        unrecommend(groupID)
        g.applys.clear()
    else:
        recommend(groupID)
        try:
            del g.applys[p.entityID]
        except KeyError:
            pass
    g.save()
    p.groupID = groupID
    p.save()
    return SUCCESS


def apply_group(entityID, groupID, applyID):
    g = Group.simple_load(groupID, ["members", "applys"])
    g.applys.load()
    if applyID in g.applys:
        return msgTips.FAIL_MSG_GROUP_ALREADY_APPLIED  # 重复
    g.members.load()
    if not len(g.members):
        return msgTips.FAIL_MSG_GROUP_DISMISSED
    if len(g.members) >= MAX_MEMBERS_COUNT:
        unrecommend(groupID)
        return msgTips.FAIL_MSG_GROUP_LIMITED_EXCEED
    a = g_entityManager.get_player(applyID)
    if not a:
        a = Player.simple_load(applyID, ["groupID"])
    if a.groupID:
        return msgTips.FAIL_MSG_GROUP_ALREADY_JOINED   # 已经加入
    now = int(time.time())
    g.applys.load()
    g.applys[applyID] = {"applytime": now}
    g.save()
    p = g_entityManager.get_player(entityID)
    if p:
        p.group_applys = g.applys
    return SUCCESS


def quit_group(entityID, groupID):
    g = Group.simple_load(groupID, ["leaderID", "members", "invites"])
    if not g:
        return msgTips.FAIL_MSG_GROUP_NOT_IN_THIS
    g.members.load()
    g.invites.load()
    p = g_entityManager.get_player(entityID)
    if not p:
        p = Player.simple_load(entityID, ["groupID", "group_last_kicked_time"])
    if not p.groupID:
        return msgTips.FAIL_MSG_GROUP_HAS_NOT_JOINED   # "未加入同门了"
    if p.entityID not in g.members:
        return msgTips.FAIL_MSG_GROUP_NOT_IN_THIS
    del g.members[p.entityID]
    if p.entityID in g.invites:
        g.invites.remove(p.entityID)
    if p.entityID == g.leaderID:
        rest = sorted(
            g.members.items(),
            key=lambda v: v[1]["jointime"])
        if rest:
            new_leaderID, _ = rest[0]
            g.leaderID = new_leaderID
    recommend(groupID)
    g.save()
    p.groupID = 0
    now = int(time.time())
    p.group_last_kicked_time = now
    p.save()
    return SUCCESS


def get_group_info(groupID):
    g = Group.simple_load(groupID, ["name", "leaderID", "members"])
    if not g:
        return {}
    g.members.load()
    intimate = 0
    members = OrderedDict(sorted(
        g.members.items(),
        key=lambda v: (v[0] == g.leaderID) or v[1]["jointime"]))
    memberlist = []
    for entityID, member in members.items():
        member.setdefault("intimate", 0)
        intimate += member["intimate"]
        member.update(get_opponent_detail(entityID))
        members[entityID] = member
        memberlist.append(member)
    rs = {
        "groupID": g.groupID,
        "name": g.name,
        "members": memberlist,
        "membercount": len(members),
        "intimate": intimate,
        "leaderID": g.leaderID}
    return rs


def kick_group_member_offline(entityID, groupID):
    rs = quit_group(entityID, groupID)
    dt = datetime.now()
    g = Group.simple_load(groupID, ["name"])
    title, content, ID = get_mail("GroupKick")
    send_mail(entityID, title, content.format(
        dt.strftime(DATETIMEFMT), g.name), configID=ID)
    return rs


@proxy.rpc(failure=kick_group_member_offline)
def kick_group_member(entityID, groupID):
    rs = quit_group(entityID, groupID)
    dt = datetime.now()
    g = Group.simple_load(groupID, ["name"])
    title, content, ID = get_mail("GroupKick")
    send_mail(entityID, title, content.format(
        dt.strftime(DATETIMEFMT), g.name), configID=ID)
    p = g_entityManager.get_player(entityID)
    if p:
        p.sync()
    return rs


def allow_group_member_offline(entityID, groupID):
    rs = join_group(entityID, groupID)
    return rs


@proxy.rpc(failure=allow_group_member_offline)
def allow_group_member(entityID, groupID):
    rs = join_group(entityID, groupID)
    p = g_entityManager.get_player(entityID)
    if p:
        p.sync()
    return rs


def invite_group_member_offline(entityID, groupID, name):
    now = int(time.time())
    g = Group.simple_load(groupID, ["invites", "gve_last_kick_time"])
    if now < g.gve_last_kick_time + ONE_DAY:
        return msgTips.FAIL_MSG_GROUP_KICK_TOO_FREQUENTLY_TO_INVITED
    g.invites.load()
    if entityID in g.invites:
        return msgTips.FAIL_MSG_GROUP_ALREADY_INVITED   # 已经邀请过了
    title, content, ID = get_mail("GroupInvite")
    send_mail(
        entityID, title,
        content.format(name, groupID),
        cd=ONE_DAY, configID=ID)
    return SUCCESS


@proxy.rpc(failure=invite_group_member_offline)
def invite_group_member(entityID, groupID, name):
    now = int(time.time())
    g = Group.simple_load(groupID, ["invites", "gve_last_kick_time"])
    if now < g.gve_last_kick_time + ONE_DAY:
        return msgTips.FAIL_MSG_GROUP_KICK_TOO_FREQUENTLY_TO_INVITED
    g.invites.load()
    if entityID in g.invites:
        return msgTips.FAIL_MSG_GROUP_ALREADY_INVITED   # 已经邀请过了
    title, content, ID = get_mail("GroupInvite")
    send_mail(
        entityID, title,
        content.format(name, groupID),
        cd=ONE_DAY, configID=ID)
    p = g_entityManager.get_player(entityID)
    if p:
        p.sync()
    return SUCCESS


def apply_group_member_failure(entityID, groupID, applyID):
    rs = apply_group(entityID, groupID, applyID)
    return rs


@proxy.rpc(failure=apply_group_member_failure)
def apply_group_member(entityID, groupID, applyID):
    p = g_entityManager.get_player(entityID)
    rs = apply_group(entityID, groupID, applyID)
    if p:
        p.sync()
    return rs


# GVE

def get_group_ranking_key(sceneID, date=None):
    return "GVE_DAMAGE_RANKS_{%d}{%d}{%s}" % (
        sceneID, settings.SESSION["ID"], date)


def get_group_key(groupID):
    return "%d.%d" % (settings.REGION["ID"], groupID)


def update_group_damage(sceneID, groupID, damage, date=None):
    if not date:
        date = datedate.today()
    key = get_group_ranking_key(sceneID, date=date)
    g = Group.simple_load(groupID, ["gve_max_damage"])
    groupID = get_group_key(groupID)
    pool = settings.REDISES["index"]
    with pool.ctx() as conn:
        damage = int(conn.execute("ZINCRBY", key, damage, groupID))
    if damage > g.gve_max_damage:
        g.gve_max_damage = damage
        g.save()
    return damage


def sync_group_damage(groupID, damage):
    g = Group.simple_load(groupID, ["gve_activateds"])
    g.gve_activateds.load()
    for entityID in g.gve_activateds:
        proxy.update_player_group_damage(entityID, damage)


@proxy.rpc
def update_player_group_damage(entityID, damage):
    p = g_entityManager.get_player(entityID)
    if not p:
        return
    p.gve_groupdamage = damage
    p.save()
    p.sync()


def get_group_rank(sceneID, groupID,  date=None):
    if not date:
        date = datedate.today()
    key = get_group_ranking_key(sceneID, date=date)
    groupID = get_group_key(groupID)
    pool = settings.REDISES["index"]
    with pool.ctx() as conn:
        rank = int(conn.execute("ZREVRANK", key, groupID) or 0) + 1
    return rank


def get_group_score(sceneID, groupID, date=None):
    if not date:
        date = datedate.today()
    key = get_group_ranking_key(sceneID, date=date)
    groupID = get_group_key(groupID)
    pool = settings.REDISES["index"]
    with pool.ctx() as conn:
        damage = int(conn.execute("ZSCORE", key, groupID) or 0)
    return damage


def get_group_count(sceneID, date=None):
    if not date:
        date = datedate.today()
    key = get_group_ranking_key(sceneID, date=date)
    # groupID = get_group_key(groupID)
    pool = settings.REDISES["index"]
    with pool.ctx() as conn:
        damage = int(conn.execute("ZCOUNT", key, "-inf", "+inf"))
    return damage


def get_group_ranking(sceneID, count=10, date=None):
    if not date:
        date = datedate.today()
    key = get_group_ranking_key(sceneID, date=date)
    pool = settings.REDISES["index"]
    with pool.ctx() as conn:
        rs = conn.execute(
            "ZREVRANGEBYSCORE", key, "+inf", "-inf",
            "WITHSCORES", "LIMIT", 0, count)
        ranks = []
        for index, c in enumerate(rs):
            if index % 2 == 0:
                regionID, entityID = map(int, c.split(".", 1))
                ranks.append([regionID, entityID, None])
            else:
                ranks[-1][2] = int(c)
    return ranks


def get_gve_entity(entityID):
    p = g_entityManager.get_player(entityID)
    if not p:
        p = Player.simple_load(
            entityID, [
                "gve_index",
                "gve_target",
                "gve_state",
                "name",
                "prototypeID"])
    return {
        "id": entityID,
        "index": p.gve_index,
        "target": p.gve_target,
        "state": p.gve_state,
        "name": p.name,
        "prototypeID": p.prototypeID,
    }


def sync_gve_entity(players, entityID, state=None):
    if players:
        info = get_gve_entity(entityID)
        if state is not None:
            info["state"] = state
        rsp = poem_pb.GveEntity(**info)
        logger.debug(rsp)
        msg = success_msg(msgid.SYNC_GVE_ENTITY, rsp)
        boardcast_gve_entity(players, msg)


def sync_gve_entity_index(players):
    for p in players:
        proxy.update_gve_entity_index(p)


@proxy.rpc
def update_gve_entity_index(entityID):
    p = g_entityManager.get_player(entityID)
    if p:
        g = Group.simple_load(p.groupID, ["gve_joineds"])
        if g:
            g.gve_joineds.load()
            try:
                p.gve_index = g.gve_joineds.index(entityID)
                p.save()
            except ValueError:
                pass


def boardcast_gve_entity(players, message):
    __boardcast_gve_entity(players, message)


def __boardcast_gve_entity(players, message):
    for player in players:
        proxy.notify_gve_entity(player, message)


@proxy.rpc
def notify_gve_entity(entityID, message):
    g_playerManager.sendto(entityID, message)


def leave_gve(p):
    if not p.groupID:
        return
    g = Group.simple_load(
        p.groupID, [
            "gve_joineds", "gve_activateds"])
    g.gve_joineds.load()
    g.gve_activateds.load()
    if p.entityID not in g.gve_joineds:
        return
    if p.entityID not in g.gve_activateds:
        return
    set_gve_state(p, GveEntity.GveEntityStateLeave)
    sync_gve_entity(g.gve_joineds, p.entityID)
    p.save()


def quit_gve(p):
    if not p.groupID:
        return
    g = Group.simple_load(
        p.groupID, [
            "gve_joineds", "gve_activateds"])
    g.gve_joineds.load()
    g.gve_activateds.load()
    if p.entityID not in g.gve_joineds:
        return
    if p.entityID in g.gve_activateds:
        return
    try:
        g.gve_joineds.remove(p.entityID)
        g.save()
    except ValueError:
        pass
    set_gve_state(p, GveEntity.GveEntityStateQuit)
    sync_gve_entity(g.gve_joineds, p.entityID)
    p.save()


#  def quit_gve(p):
#      if not p.groupID:
#          return
#      g = Group.simple_load(
#          p.groupID, [
#              "gve_joineds", "gve_activateds"])
#      g.gve_joineds.load()
#      g.gve_activateds.load()
#      if p.entityID in g.gve_joineds:
#          if p.entityID not in g.gve_activateds:
#              try:
#                  g.gve_joineds.remove(p.entityID)
#              except ValueError:
#                  pass
#              g.save()
#              set_gve_state(p, GveEntity.GveEntityStateQuit)
#          else:
#              set_gve_state(p, GveEntity.GveEntityStateLeave)
#          sync_gve_entity(g.gve_joineds, p.entityID)
#          p.save()


@proxy.rpc_across
def get_group_across_region(regionID, groupID):
    assert regionID == settings.REGION["ID"]
    g = Group.simple_load(groupID, ["name", "leaderID", "members"])
    g.members.load()
    members = []
    for k in g.members:
        p = Player.simple_load(k, ["prototypeID"])
        members.append({
            "entityID": p.entityID,
            "prototypeID": p.prototypeID
        })
    return {
        "name": g.name,
        "groupID": groupID,
        "regionID": regionID,
        "members": members,
    }


@proxy.rpc_across
def get_group_member_detail_across_region(regionID, entityID):
    assert regionID == settings.REGION["ID"]
    detail = get_opponent_detail(entityID)
    return detail


# GVE rank memebr

def get_group_member_ranking_key(sceneID, date=None):
    return "GVE_DAMAGE_MEMBER_RANKS_{%d}{%d}{%s}" % (
        sceneID, settings.SESSION["ID"], date)


def get_group_member_key(entityID):
    return "%d.%d" % (settings.REGION["ID"], entityID)


def update_group_member_damage(sceneID, entityID, damage, date=None):
    if not date:
        date = datedate.today()
    key = get_group_member_ranking_key(sceneID, date=date)
    entityID = get_group_member_key(entityID)
    pool = settings.REDISES["index"]
    with pool.ctx() as conn:
        damage = int(conn.execute("ZINCRBY", key, damage, entityID))
    return damage


def get_group_member_rank(sceneID, entityID,  date=None):
    if not date:
        date = datedate.today()
    key = get_group_member_ranking_key(sceneID, date=date)
    entityID = get_group_member_key(entityID)
    pool = settings.REDISES["index"]
    with pool.ctx() as conn:
        rank = int(conn.execute("ZREVRANK", key, entityID) or 0) + 1
    return rank


def get_group_member_score(sceneID, entityID, date=None):
    if not date:
        date = datedate.today()
    key = get_group_member_ranking_key(sceneID, date=date)
    entityID = get_group_member_key(entityID)
    pool = settings.REDISES["index"]
    with pool.ctx() as conn:
        damage = int(conn.execute("ZSCORE", key, entityID) or 0)
    return damage


def get_group_member_count(sceneID, date=None):
    if not date:
        date = datedate.today()
    key = get_group_member_ranking_key(sceneID, date=date)
    # entityID = get_group_member_key(entityID)
    pool = settings.REDISES["index"]
    with pool.ctx() as conn:
        damage = int(conn.execute("ZCOUNT", key, "-inf", "+inf"))
    return damage


def get_group_member_ranking(sceneID, count=10, date=None):
    if not date:
        date = datedate.today()
    key = get_group_member_ranking_key(sceneID, date=date)
    pool = settings.REDISES["index"]
    with pool.ctx() as conn:
        rs = conn.execute(
            "ZREVRANGEBYSCORE", key, "+inf", "-inf",
            "WITHSCORES", "LIMIT", 0, count)
        ranks = []
        for index, c in enumerate(rs):
            if index % 2 == 0:
                regionID, entityID = map(int, c.split(".", 1))
                ranks.append([regionID, entityID, None])
            else:
                ranks[-1][2] = int(c)
    return ranks


@proxy.rpc_across
def get_group_member_across_region(regionID, entityID):
    assert regionID == settings.REGION["ID"]
    p = Player.simple_load(entityID, ["name", "prototypeID", "groupID"])
    return {
        "name": p.name,
        "groupID": p.groupID,
        "regionID": regionID,
        "prototypeID": p.prototypeID,
        "entityID": entityID,
    }


def set_gve_state(p, state, force=False):
    if force or p.gve_state != GveEntity.GveEntityStateDead:
        p.gve_state = state


def gve_group_is_open(groupID):
    return g_campaignManager.gve_campaign.is_open()


def gve_group_is_end(groupID):
    if gve_group_is_open(groupID):
        if gve_group_is_started(groupID):
            # 活动开始了，则如果当前大于活动结束时间，则活动已经结束
            now = int(time.time())
            g = Group.simple_load(groupID, ["gve_end_cd"])
            if not g.gve_end_cd:
                return False
            return now >= g.gve_end_cd
    # 活动未开启，则不可能已经结束
    return False


def gve_group_is_started(groupID):
    if g_campaignManager.gve_campaign.is_open():
        g = Group.simple_load(groupID, ["gve_start_time"])
        if not g.gve_start_time:
            return False
        if g.gve_start_time >= \
                g_campaignManager.gve_campaign.get_start_time() and\
                g.gve_start_time <= \
                g_campaignManager.gve_campaign.get_end_time():
            return True
    return False


def gve_is_open(p):
    return gve_group_is_open(p)


def gve_is_end(p):
    return gve_group_is_end(p.groupID)


def gve_is_started(p):
    return gve_group_is_started(p.groupID)


def reset_player_gve(p):
    if not p.groupID:
        return
    now = int(time.time())
    g = Group.simple_load(p.groupID, ["gve_end_cd"])
    flag = False
    if g_campaignManager.gve_campaign.is_open():
        if p.gve_last_reset_time < \
                g_campaignManager.gve_campaign.get_start_time() or \
                p.gve_last_reset_time > \
                g_campaignManager.gve_campaign.get_end_time():
            flag = True
            ts = now
        elif gve_is_end(p) and p.gve_last_reset_time < g.gve_end_cd:
            flag = True
            ts = g.gve_end_cd
    elif p.gve_last_reset_time < g.gve_end_cd:
        flag = True
        ts = g.gve_end_cd
    if flag:
        logger.info("%d reseted", p.entityID)
        p.gve_damage = 0
        p.gve_score = 0
        # p.gve_index = 0
        p.gve_target = 0
        p.gve_state = GveEntity.GveEntityStateNormal
        p.gve_addition = 0
        p.gve_groupdamage = 0
        p.gve_buff = 0
        # gve_basereward
        p.gve_reborn_rest_count = 1  # TODO
        p.gve_last_reset_time = ts
        p.save()


def reset_gve(groupID):
    if not groupID:
        return
    g = Group.load(groupID)
    now = int(time.time())
    flag = False
    if g_campaignManager.gve_campaign.is_open():
        # 活动开启时，如果上次重置时间不在活动期间，则重置
        if g.gve_last_reset_time < \
                g_campaignManager.gve_campaign.get_start_time() or\
                g.gve_last_reset_time > \
                g_campaignManager.gve_campaign.get_end_time():
            logger.debug("in period")
            flag = True
            ts = now
        elif gve_group_is_end(groupID) and\
                g.gve_last_reset_time < g.gve_end_cd:
            logger.debug("is end")
            flag = True
            ts = g.gve_end_cd
    elif g.gve_last_reset_time < g.gve_end_cd:
        # 活动未开启时，如果上次重置时间小于上次的活动结束时间，则重置
        logger.debug("not open")
        flag = True
        ts = g.gve_end_cd
    if flag:
        logger.debug("group reseted")
        g.gve_last_reset_time = ts
        g.save()
        #  g.gve_start_time = 0
        #  g.gve_end_cd = 0
        # g.gve_joineds.clear()
        # clean up on online player
        for i in g.gve_joineds:
            if not PlayerOnlineIndexing.get_pk(i):
                g.gve_joineds.remove(i)
        # 为了结束后还能知道，谁参加过
        g.gve_end_activateds.clear()
        g.gve_end_activateds.extend(g.gve_activateds)
        g.gve_activateds.clear()
        g.gve_progress.clear()
        g.gve_deads.clear()
        g.save()


def reset_rank():
    from campaign.manager import g_campaignManager
    sceneID = g_campaignManager.gve_campaign.get_sceneID()
    pool = settings.REDISES["index"]
    date = datedate.today()
    with pool.ctx() as conn:
        logger.info("DEL %s", get_group_ranking_key(sceneID, date=date))
        conn.execute("DEL", get_group_ranking_key(sceneID, date=date))
        logger.info("DEL %s", get_group_member_ranking_key(sceneID, date=date))
        conn.execute("DEL", get_group_member_ranking_key(sceneID, date=date))


def give_reward_by_mail(p):
    now = int(time.time())
    if not p.groupID:
        return
    g = Group.simple_load(p.groupID, [
        "name", "gve_rewards",
        "members", "gve_activateds_detail"])
    g.gve_rewards.load()
    g.gve_activateds_detail.load()
    if p.entityID not in g.gve_rewards:
        return
    rewards, lock, addition = g.gve_rewards[p.entityID]
    detail = g.gve_activateds_detail.get(p.entityID, {})
    addition = detail.get("addition", 0)
    score = detail.get("score", 0)
    damage = detail.get("damage", 0)
    total_damage = detail.get("total_damage", 0)
    title, content, ID = get_mail("GroupBaseReward")
    content = content.format(
        g.name, total_damage, damage, score, addition)
    if now >= lock:
        for reward in rewards:
            reward["count"] = int(
                reward["count"] * (1 + addition / float(100)))
        rewards = parse_reward(rewards)
        if rewards:
            send_mail(
                p.entityID, title, content,
                addition=rewards, configID=ID)
        del g.gve_rewards[p.entityID]
        g.members.load()
        member = g.members[p.entityID]
        member["intimate"] = member.get("intimate", 0) + 10
        g.members[p.entityID] = member
        g.save()


def get_sceneID(date=None):
    if not date:
        date = datedate.today()
    week = date.weekday() + 1
    configs = get_config(GveSceneInfoByWeekConfig)
    config = configs.get(week)
    if not config:
        config = configs[max(configs)]
    return config.ID


def get_last_date_by_sceneID(sceneID, date=None):
    if not date:
        date = datedate.today()
    config = get_config(GveSceneInfoConfig)[sceneID]
    week = date.weekday() + 1
    if week >= config.week:
        days = week - config.week
    else:
        days = week - config.week + 7
    target = datedate.today() - timedelta(days=days)
    return target


def encode_utf8(string):
    try:
        string = string.encode("utf-8")
    except UnicodeDecodeError:
        pass
    return string


def give_ranking_reward(sdate=None):
    if sdate:
        date = datetime.strptime(sdate, "%Y-%m-%d").date()
    else:
        date = datedate.today()
        sdate = datetime.strftime(date, "%Y-%m-%d")
    sceneID = get_sceneID(date=date)
    url = "/".join([
        urljoin(PROXY["host"], PROXY["port"]), "give_gve_ranking_reward"])
    pending = []
    group = get_config(GveRankingRewardBySceneIDConfig).get(sceneID)
    configs = get_config(GveRankingRewardConfig)
    for rank, (regionID, groupID, score) in enumerate(
            get_group_ranking(sceneID, count=50, date=date), 1):
        for config in group:
            config = configs.get(config.ID)
            start, end = config.range
            if rank >= start and rank <= end:
                g = Group.simple_load(groupID, ["name", "members"])
                g.members.load()
                data = {
                    "group_name": encode_utf8(g.name),
                    "group_damage": score,
                    "group_rank": rank,
                    "configID": config.ID,
                    "date": sdate,
                }
                for entityID in g.members:
                    uri = "/".join([url, str(entityID)])
                    uri = set_query_string(
                        uri, regionID=regionID)
                    pending.append([uri, data])
    for uri, data in pending:
        get_poolmanager().urlopen("POST", uri, body=urlencode(data))
