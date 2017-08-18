# coding:utf-8
import time
import logging
logger = logging.getLogger("friend")
from datetime import datetime
from json import loads as decode
from json import dumps as encode
from gevent import sleep

from yy.utils import guess
from yy.utils import convert_list_to_dict
from yy.utils import weighted_random2
from yy.message.header import success_msg
# from yy.entity.index import SortedIndexing
from state.base import StateObject

from gm.proxy import proxy
from entity.manager import g_entityManager

from config.configs import get_config
from config.configs import LevelupConfig
from config.configs import TriggerAfterFbConfig
from config.configs import FriendfbConfig
from config.configs import FriendfbByLevelConfig
from config.configs import FriendfbRewardConfig
from config.configs import FriendfbRewardByFbIDConfig

from player.model import Player
from player.model import PlayerFriendRecommendIndexing
from player.model import PlayerFriendRecommendOnlineIndexing
from player.formulas import get_friend_max_count
from player.formulas import get_level_value
from player.manager import g_playerManager

from reward.manager import parse_reward

from mail.manager import send_mail as do_send_mail
from mail.manager import get_mail

from common import msgTips
from common import index
from explore.boss import g_bossCampaignManager
from task.constants import TaskCond
from protocol import poem_pb
import protocol.poem_pb as msgid

import settings
pool = settings.REDISES['friendfb']


FRIENDFB_INTERVAL = 4 * 60 * 60  # 秘境开启时长（单位：秒）
FRIEND_APPLY_CD = 0.5 * 86400  # 申请过期


class ListIndexing(object):
    def __init__(self, key, pool):
        self.key = key
        self.pool = pool

    def lpush(self, *args):
        return self.execute("LPUSH", self.key, *args)

    def lpop(self):
        return self.execute("LPOP", self.key)

    def rpush(self, *args):
        return self.execute("RPUSH", self.key, *args)

    def execute(self, *args):
        return self.pool.execute(*args)


FriendfbByTimeIndexing = ListIndexing(
    index.LIST_FRIEND_FB_BY_TIME.render(), pool)


def recommendp(p):
    if not get_level_value(p.level, "friend"):
        return
    if p.friend_count < p.friend_max_count:
        PlayerFriendRecommendOnlineIndexing.register(p.entityID)
        recommend(p.entityID)


def unrecommendp(p):
    PlayerFriendRecommendOnlineIndexing.unregister(p.entityID)


def recommend(entityID):
    PlayerFriendRecommendIndexing.register(entityID)


def unrecommend(entityID):
    PlayerFriendRecommendIndexing.unregister(entityID)


def getrecommends(p, count):
    count += 10  # 多取10个
    rs = set(PlayerFriendRecommendOnlineIndexing.randmembers(count=count))
    rest = count - len(rs)
    if rest:
        rs.update(PlayerFriendRecommendIndexing.randmembers(count=rest))
    rs -= {str(i) for i in p.friendset}
    rs -= {str(i) for i in p.friend_applys}
    rs -= {str(p.entityID)}
    return map(int, rs)[:count]


OK = 0


def apply_friend_offline(entityID, applyID):
    now = int(time.time())
    field = "friend_applys"
    if not Player.simple_load(entityID, []):
        return msgTips.FAIL_MSG_PLAYER_NOT_FOUND
    encode = Player.fields[field].encoder
    key = "_".join([field, "p{%d}" % entityID])
    if not Player.pool.execute(
            "HSET", key, applyID, encode({"applytime": now})):
        return msgTips.FAIL_MSG_FRIEND_ALREADY_APPLYED
    return OK


@proxy.rpc(failure=apply_friend_offline)
def apply_friend(entityID, applyID):
    now = int(time.time())
    friend = g_entityManager.get_player(entityID)
    if applyID in friend.friend_applys:
        return msgTips.FAIL_MSG_FRIEND_ALREADY_APPLYED
    friend.friend_applys[applyID] = {"applytime": now}
    friend.save()
    friend.sync()
    return OK


def allow_friend_offline(applyID, entityID):
    p = Player.simple_load(applyID, ["friendset", "level"])
    friend_max_count = get_friend_max_count(p.level)
    if len(p.friendset) >= friend_max_count:
        return False
    if len(p.friendset) + 1 >= friend_max_count:
        unrecommend(entityID)
    add_friend_offline(applyID, entityID)
    return True


@proxy.rpc(failure=allow_friend_offline, key="applyID")
def allow_friend(applyID, entityID):
    applicant = g_entityManager.get_player(applyID)
    if len(applicant.friendset) >= applicant.friend_max_count:
        return False
    if len(applicant.friendset) + 1 >= applicant.friend_max_count:
        unrecommend(entityID)
        unrecommendp(applicant)
    add_friend(applyID, entityID)
    from task.manager import on_friends_count
    on_friends_count(applicant)
    return True


def add_friend_offline(entityID, friendID):
    p = Player.simple_load(entityID, ["friendset"])
    p.friendset.add(friendID)
    p.save()
    return True


@proxy.rpc(failure=add_friend_offline)
def add_friend(entityID, friendID):
    p = g_entityManager.get_player(entityID)
    p.friendset.add(friendID)
    p.save()
    p.sync()
    return True


def deny_friend(appID, entityID):
    p = g_entityManager.get_player(entityID)
    try:
        del p.friend_applys[appID]
    except KeyError:
        pass
    p.save()
    p.sync()
    return True


def remove_apply_friend(entityID, applyID):
    p = g_entityManager.get_player(entityID)
    try:
        del p.friend_applys[applyID]
    except KeyError:
        pass
    p.save()
    p.sync()
    return True


def remove_friend_offline(entityID, friendID):
    p = Player.simple_load(entityID, ["friendset"])
    try:
        p.friendset.remove(friendID)
        recommend(entityID)
    except KeyError:
        pass
    p.save()
    return True


@proxy.rpc(failure=remove_friend_offline)
def remove_friend(entityID, friendID):
    p = g_entityManager.get_player(entityID)
    try:
        p.friendset.remove(friendID)
        recommend(entityID)
        recommendp(p)
    except KeyError:
        pass
    p.save()
    p.sync()
    return True


def gift_friend_offline(friendID, name, rewards):
    title, content, ID = get_mail("FriendGift")
    do_send_mail(
        friendID, title,
        content.format(name), addition=rewards, configID=ID)
    return True


@proxy.rpc(failure=gift_friend_offline, key='friendID')
def gift_friend(friendID, name, rewards):
    title, content, ID = get_mail("FriendGift")
    do_send_mail(
        friendID, title,
        content.format(name), addition=rewards, configID=ID)
    return True


def invite_friend_offline(friendID, friendfbID, name, fbname):
    field = "friendfb_list"
    encode = Player.fields[field].encoder or (lambda s: s)
    key = "_".join([field, "p{%d}" % friendID])
    if not Player.pool.execute("HSET", key, encode(friendfbID), ""):
        False
    title, content, ID = get_mail("FriendInvite")
    do_send_mail(
        friendID,
        title,
        content.format(name, fbname),
        cd=FRIENDFB_INTERVAL, configID=ID)
    join_friendfb(friendfbID, friendID)
    return True


@proxy.rpc(failure=invite_friend_offline, key='friendID')
def invite_friend(friendID, friendfbID, name, fbname):
    f = g_entityManager.get_player(friendID)
    if friendfbID in f.friendfb_list:
        return False
    title, content, ID = get_mail("FriendInvite")
    do_send_mail(
        friendID,
        title,
        content.format(name, fbname),
        cd=FRIENDFB_INTERVAL, configID=ID)
    f.friendfb_list.add(friendfbID)
    join_friendfb(friendfbID, friendID)
    f.save()
    f.sync()
    return True


# {{{ activists, invitees


def join_friendfb(friendfbID, entityID):
    #  已邀请列表
    key = "%s_invitees" % friendfbID
    with pool.ctx() as conn:
        return bool(int(conn.execute("HSET", key, entityID, "")))


def load_friendfb_invitees(friendfbID):
    key = "%s_invitees" % friendfbID
    with pool.ctx() as conn:
        return set(map(int, conn.execute("HKEYS", key)))


def done_friendfb(friendfbID, entityID):
    #  已挑战列表
    key = "%s_activists" % friendfbID
    with pool.ctx() as conn:
        return bool(int(conn.execute("HSET", key, entityID, "")))


def load_friendfb_activists(friendfbID):
    key = "%s_activists" % friendfbID
    with pool.ctx() as conn:
        return set(map(int, conn.execute("HKEYS", key)))
# }}}


def if_boss(friendfbID):
    return "bosscampaign" in friendfbID


def get_boss_campaign(friendfbID):
    if not if_boss(friendfbID):
        return None
    _, campaignID = friendfbID.split(":", 1)
    campaignID = int(campaignID)
    return g_bossCampaignManager.campaigns.get(campaignID)


def if_boss_campaign_opened(friendfbID):
    bc = get_boss_campaign(friendfbID)
    if bc:
        return bc.is_open()
    return False


def load_friendfb(friendfbID):
    now = int(time.time())
    if if_boss(friendfbID):
        friendfb = {}
        campaign = get_boss_campaign(friendfbID)
        if campaign:
            friendfb.update(**{
                'friendfbID': friendfbID,
                'ownerID': 0,  # 发现者
                'fbID': campaign.config.fbID,
                'owner': '',
                'activists': [],
                'createtime': now,
                'remain': max(campaign.config.end - now, 0),
                'desc': campaign.config.desc,
            })
            friendfb.update(**campaign.get_boss())
    else:
        rs = convert_list_to_dict(pool.execute("HGETALL", friendfbID))
        logger.debug("%r", rs)
        if not rs:
            return rs
        friendfb = {k: decode(v) for k, v in rs.items()}
        friendfb.setdefault('friendfbID', friendfbID)
        friendfb['activists'] = load_friendfb_activists(friendfbID)
        friendfb['invitees'] = load_friendfb_invitees(friendfbID)
        logger.debug("%r", friendfb)
        friendfb['remain'] = \
            FRIENDFB_INTERVAL - (now - friendfb['createtime'])
        friendfb['hp'] = max(friendfb['hp'], 0)
    return friendfb


def player_is_dead(p, friendfbID):
    is_dead = friendfbID in p.friendfb_deads
    campaign = get_boss_campaign(friendfbID)
    if campaign:
        if campaign.config.fbID in p.friendfb_deadtimes:
            dead_time = p.friendfb_deadtimes[campaign.config.fbID]
            if dead_time < campaign.config.start or dead_time > campaign.config.end:
                del p.friendfb_deadtimes[campaign.config.fbID]
                is_dead = False
            else:
                is_dead = True
        else:
            is_dead = False
    return is_dead


FRIEND_LISTENERS = {}


def listen(entityID, friendID):
    FRIEND_LISTENERS[entityID] = friendID


def unlisten(entityID):
    try:
        del FRIEND_LISTENERS[entityID]
    except KeyError:
        pass


def send_friend_message_failure(friendID, content, senderID, **extra):
    now = time.time()
    message = {
        "time": now,
        "content": content,
    }
    message.update(extra)
    p = Player.simple_load(friendID, ['friend_messages'])
    p.friend_messages.load()
    messages = p.friend_messages.get(senderID, [])
    messages.append(message)
    p.friend_messages[senderID] = messages
    p.save()
    return True


@proxy.rpc(failure=send_friend_message_failure, key='friendID')
def send_friend_message(friendID, content, senderID, **extra):
    now = time.time()
    message = {
        "time": now,
        "content": content,
        "senderID": senderID,
    }
    message.update(extra)
    p = g_entityManager.get_player(friendID)
    listen_to = FRIEND_LISTENERS.get(friendID, 0)
    if listen_to == senderID:
        rsp = poem_pb.FriendMessages()
        rsp.messages.add(**message)
        rsp.senderID = senderID
        msg = success_msg(
            msgid.LISTEN_FRIEND, rsp)
        g_playerManager.sendto(friendID, msg)
        return
    messages = p.friend_messages.get(senderID, [])
    messages.append(message)
    p.friend_messages[senderID] = messages
    p.save()
    p.sync()
    return True


class DoesNotExistsException(Exception):
    pass


def simple_load_friendfb(friendfbID, *args):
    assert args, "Not args supply"
    if if_boss(friendfbID):
        f = load_friendfb(friendfbID)
        rs = [f[a] for a in args]
    else:
        try:
            with pool.ctx() as conn:
                rs = map(decode, conn.execute("HMGET", friendfbID, *args))
        except TypeError:
            raise DoesNotExistsException
        try:
            idx = args.index('hp')
            rs[idx] = max(rs[idx], 0)
        except ValueError:
            pass
    if len(args) == 1:
        return rs[0]
    return rs


def __save_friendfb(ffID, **kwargs):
    args = []
    for k, v in kwargs.items():
        args.extend([k, encode(v)])
    with pool.ctx() as conn:
        return conn.execute('HMSET', ffID, *args)


FRIENDFB_PREFIX = "friendfb_"


def create_friendfb(p, fbID):
    now = int(time.time())
    info = get_config(FriendfbConfig)[fbID]
    maxhp = info.active_num * info.dpr * p.level * p.level
    friendfbID = '%s%d:%d' % (FRIENDFB_PREFIX, now, p.entityID)
    friendfb = {
        'friendfbID': friendfbID,
        'createtime': now,
        'ownerID': p.entityID,  # 发现者
        'fbID': fbID,
        'maxhp': maxhp,
        'hp': maxhp,
        'owner': p.name,
    }
    assert __save_friendfb(friendfbID, **friendfb), "Create friendfb fail"
    FriendfbByTimeIndexing.rpush(friendfbID), "Register friendfb fail"
    assert join_friendfb(friendfbID, p.entityID), "Join friendfb fail"
    return friendfb


def delete_friendfb(friendfbID):
    with pool.ctx() as conn:
        conn.execute_pipeline(
            ("DEL", friendfbID),
            ("DEL", "%s_activists" % friendfbID),
            ("DEL", "%s_ranklist" % friendfbID),
        )


def trigger_friendfb(p):
    if p.trigger_packs_flag:
        return None
    now = datetime.now()
    ts = time.mktime(now.timetuple())
    if not p.friendfb_remain_count:
        return None
    lconfig = get_config(LevelupConfig).get(p.level)
    if not lconfig or not lconfig.friendfb:
        return None
    if now.hour > 23 or now.hour < 9:
        return None
    last = p.friendfb_last_trigger_time
    # 同一时间只存在一个秘境副本
    if last and ts < last + FRIENDFB_INTERVAL:
        return None
    if not p.friendfb_triggered_count:
        prob = 1
    else:
        prob = 0
        triggers = get_config(TriggerAfterFbConfig)
        for tg in triggers:
            if p.friend_total_sp >= tg.sp:
                prob = tg.friendfb_prob
            else:
                break
    if not guess(prob):
        return None
    configs = get_config(FriendfbConfig)
    samples = []
    ffs_by_level = None
    ffs_by_levels = get_config(FriendfbByLevelConfig)
    for k in sorted(ffs_by_levels):
        if p.level >= k:
            ffs_by_level = ffs_by_levels[k]
    if not ffs_by_level:
        ffs_by_level = ffs_by_levels[min(ffs_by_levels)]
    for ff in ffs_by_level:
        if p.friendfb_last_trigger_fbID and \
                p.friendfb_last_trigger_fbID == ff.fbID:
            continue
        ff = configs[ff.fbID]
        samples.append([ff.fbID, ff.prob])
    assert samples, "impossible"
    fbID = weighted_random2(samples)
    info = get_config(FriendfbConfig)[fbID]
    friendfb = create_friendfb(p, info.fbID)
    p.friendfb_list.add(friendfb['friendfbID'])
    p.friend_total_sp = 0
    p.friendfb_last_trigger_time = ts
    p.friendfb_last_trigger_fbID = fbID
    p.friendfb_triggered_count += 1
    p.save()
    p.sync()
    return friendfb


# {{{ rank list

def add_rank(p, fbID, friendfbID, damage):
    key = "%s_ranklist" % friendfbID
    with pool.ctx() as conn:
        info = conn.execute("HGET", key, p.entityID)
    if not info:
        info = {
            'entityID': p.entityID,
            'name': p.name,
            'damage': damage,
            'prototypeID': p.prototypeID,
            "borderID": p.borderID,
            "faction_name": p.faction_name,
            "level": p.level,
        }
    else:
        info = decode(info)
        info["damage"] += damage
    if info["damage"] > p.friendfb_damages.get(fbID, 0):
        p.friendfb_damages[fbID] = info["damage"]
    with pool.ctx() as conn:
        return conn.execute("HSET", key, p.entityID, encode(info))


def load_rank(friendfbID, entityID):
    if if_boss(friendfbID):
        bc = get_boss_campaign(friendfbID)
        if not bc:
            return {}
        return bc.load_rank(entityID)
    return {}


def load_ranks(friendfbID):
    if if_boss(friendfbID):
        bc = get_boss_campaign(friendfbID)
        if not bc:
            return []
        return bc.load_ranks()
    else:
        key = "%s_ranklist" % friendfbID
        with pool.ctx() as conn:
            rs = convert_list_to_dict(conn.execute("HGETALL", key))
        rs = map(decode, rs.values())
        rs = sorted(rs, key=lambda s: s['damage'], reverse=True)
    return rs
# }}}


def hurt_boss(p, fbID, friendfbID, damage):
    if if_boss(friendfbID):
        campaign = get_boss_campaign(friendfbID)
        rs = campaign.hurt_boss(p, damage)
    else:
        with pool.ctx() as conn:
            rs = int(conn.execute('HINCRBY', friendfbID, 'hp', -damage))
        # rank list
        add_rank(p, fbID, friendfbID, damage)
    return rs


def friendfbID2time(friendfbID):
    s = friendfbID.replace(FRIENDFB_PREFIX, '')
    time, _ = s.split(':', 1)
    return int(time)


def give_reward(friendfbID):
    friendfb = load_friendfb(friendfbID)
    if friendfb['hp'] > 0:
        return
    ranks = load_ranks(friendfbID)
    group = get_config(FriendfbRewardByFbIDConfig).get(friendfb['fbID'], [])
    reward_list = []
    for rank, each in enumerate(ranks, 1):
        entityID = each.get("entityID", 0)
        if not entityID:
            continue
        if rank == 1:
            proxy.sync_on_task_change(
                entityID, TaskCond.FriendfbFirst, friendfb['fbID'])
        for config in group:
            config = get_config(FriendfbRewardConfig)[config.ID]
            start, end = config.range
            if rank >= start and (not end or rank <= end):
                reward_list.append([
                    entityID, config.ID, rank, each.get("damage")])
                break
    for entityID, configID, rank, damage in reward_list:
        proxy.send_mail(entityID, configID, rank, damage)


def flowerboss_give_reward(friendfbID):
    friendfb = load_friendfb(friendfbID)
    ranks = load_ranks(friendfbID)
    group = get_config(FriendfbRewardByFbIDConfig).get(friendfb['fbID'], [])
    reward_list = []
    for rank, each in enumerate(ranks, 1):
        entityID = each.get("entityID", 0)
        if not entityID:
            continue
        if rank == 1:
            proxy.sync_on_task_change(
                entityID, TaskCond.FriendfbFirst, friendfb['fbID'])
        for config in group:
            config = get_config(FriendfbRewardConfig)[config.ID]
            start, end = config.range
            if rank >= start and (not end or rank <= end):
                reward_list.append([
                    entityID, config.ID, rank, each.get("damage")])
                break
    for entityID, configID, rank, damage in reward_list:
        proxy.send_flower_boss_mail(entityID, configID, rank, damage)


def send_mail_offline(entityID, configID, rank, damage):
    if not configID:
        return
    p = Player.simple_load(entityID, ['friendfb_kill_count'])
    p.friendfb_kill_count += 1
    config = get_config(FriendfbRewardConfig).get(configID)
    rewards = {}
    if config:
        rewards = parse_reward(config.rewards)
    p.save()
    title, content, ID = get_mail("FriendfbKill")
    content = content.format(damage, rank)
    do_send_mail(entityID, title, content, addition=rewards, configID=ID)
    return True


@proxy.rpc(failure=send_mail_offline)
def send_mail(entityID, configID, rank, damage):
    if not configID:
        return
    p = g_entityManager.get_player(entityID)
    p.friendfb_kill_count += 1
    p.save()
    p.sync()
    config = get_config(FriendfbRewardConfig).get(configID)
    rewards = {}
    if config:
        rewards = parse_reward(config.rewards)
    title, content, ID = get_mail("FriendfbKill")
    content = content.format(damage, rank)
    do_send_mail(entityID, title, content, addition=rewards, configID=ID)
    return True


def send_flower_boss_mail_offline(entityID, configID, rank, damage):
    if not configID:
        return
    p = Player.simple_load(entityID, ['friendfb_kill_count'])
    p.friendfb_kill_count += 1
    config = get_config(FriendfbRewardConfig).get(configID)
    rewards = {}
    if config:
        rewards = parse_reward(config.rewards)
    p.save()
    title, content, ID = get_mail("FlowerBoss")
    content = content.format(damage, rank)
    do_send_mail(entityID, title, content, addition=rewards, configID=ID)
    return True


@proxy.rpc(failure=send_mail_offline)
def send_flower_boss_mail(entityID, configID, rank, damage):
    if not configID:
        return
    p = g_entityManager.get_player(entityID)
    p.friendfb_kill_count += 1
    p.save()
    p.sync()
    config = get_config(FriendfbRewardConfig).get(configID)
    rewards = {}
    if config:
        rewards = parse_reward(config.rewards)
    title, content, ID = get_mail("FlowerBoss")
    content = content.format(damage, rank)
    do_send_mail(entityID, title, content, addition=rewards, configID=ID)
    return True


class FriendManager(StateObject):
    # 好友副本发奖
    def __init__(self):
        super(FriendManager, self).__init__(wait_interval=0)

    def get_loops(self):
        while True:
            sleep(30)
            friendfbID = FriendfbByTimeIndexing.lpop()
            if friendfbID:
                start = friendfbID2time(friendfbID) + FRIENDFB_INTERVAL
                now = time.time()
                if now < start:
                    FriendfbByTimeIndexing.lpush(friendfbID)
                    logger.info("friendfb loop sleep %r", start - now)
                end = now + 1
            else:
                start = 0
                end = 0
            yield [start, end, friendfbID]

    def exit_start(self):
        self.current_loop = None

    def execute_start(self):
        if self.current_loop:
            # give reward
            # give_reward(self.current_loop)
            # clean
            delete_friendfb(self.current_loop)

g_friendManager = FriendManager()
