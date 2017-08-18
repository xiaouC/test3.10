# coding:utf-8
import time
import logging
logger = logging.getLogger("faction")
from datetime import datetime

from gm.proxy import proxy

from entity.manager import g_entityManager

from player.model import Player
from mail.manager import send_mail
from mail.manager import get_mail

from faction.model import Faction
from faction.model import FactionRankRanking
from faction.model import FactionRecommendIndexing

from common import msgTips

from yy.utils import trie
from yy.utils import weighted_random2
# from yy.entity.index import DuplicateIndexException

from config.configs import get_config
from config.configs import forbid_names_trie
from config.configs import TaskConfig
from config.configs import FactionTaskConfig
from config.configs import CanStrengthenConfig
from config.configs import FactionDonateConfig
from config.configs import FactionLimitConfig

from common.log import gm_logger

# from state.base import StateObject

SUCCESS = 0
NAME_LENGTH_MAX = 7
NAME_LENGTH_MIN = 2
APPLYFACTIONCD = 86400 * 2
QUITFACTIONCD = 0  # 86400 * 1
THRONEFACTIONCD = 86400 * 3
DISMISSFACTIONCD = 86400 * 3

INVITE_LEVEL_LIMIT = 8


def clean_faction(entityID):
    p = g_entityManager.get_player(entityID)
    if not p:
        p = Player.simple_load(entityID, ['factionID', 'applyFactions'])
    if p.factionID:
        faction = Faction.simple_load(p.factionID, ['memberset'])
        if faction:
            safe_remove(faction.memberset, p.entityID)
            faction.save()
        p.last_factionID = p.factionID
        gm_logger.info({'faction': {
            'entityID': p.entityID, 'type': 'quit_faction',
            'factionID': p.factionID,
        }})
    p.factionID = 0
    p.fp = 0
    p.faction_name = ''
    p.faction_level = 0
    p.faction_is_leader = False
    p.applyFactions.clear()
    # p.applyFactionTime = 0
    p.save()
    if g_entityManager.get_player(entityID):
        p.sync()


def join_faction(entityID, factionID):
    faction = Faction.simple_load(
        factionID, [
            "level", "name",
            "memberset", "inviteset",
            "applyset",
            "strengthen_hp_level",
            "strengthen_at_level",
            "strengthen_ct_level",
            "strengthen_df_level"])
    # recommend
    level = FactionRankRanking.get_score(factionID) or 1
    limit = get_config(FactionLimitConfig)[level].limit
    if limit - len(faction.memberset) <= 1:
        unrecommend(factionID)
    clean_faction(entityID)
    p = g_entityManager.get_player(entityID)
    if not p:
        p = Player.simple_load(
            entityID, [
                'inviteFactionSet',
                'factionID',
                'last_factionID',
                'strengthen_at_level',
                'strengthen_hp_level',
                'strengthen_ct_level',
                'strengthen_df_level',
                ])
    p.factionID = faction.factionID
    p.faction_name = faction.name
    p.faction_level = level
    now = int(time.time())
    p.joinFactionTime = now
    # FIXME
    for fid in p.inviteFactionSet:
        f = Faction.simple_load(fid, ['inviteset'])
        safe_remove(f.inviteset, p.entityID)
        f.save()
    p.inviteFactionSet.clear()
    if p.factionID != p.last_factionID:
        p.totalfp = 0
        p.todayfp_donate = 0
        p.todayfp_task = 0
        p.todayfp_sp = 0
    faction.memberset.add(p.entityID)
    safe_remove(faction.applyset, p.entityID)
    safe_remove(faction.inviteset, p.entityID)
    if g_entityManager.get_player(entityID):
        p.load_faction()
        p.sync()
    p.save()
    faction.save()
    gm_logger.info({'faction': {
        'entityID': p.entityID, 'type': 'join_faction',
        'factionID': faction.factionID,
    }})


def update_strengthen_level(p, factionID):
    faction = Faction.simple_load(
        factionID, [
            "strengthen_hp_level",
            "strengthen_at_level",
            "strengthen_ct_level",
            "strengthen_df_level"])
    p.strengthen_at_level = min(
        p.strengthen_at_max_level, faction.strengthen_at_level)
    p.strengthen_hp_level = min(
        p.strengthen_hp_max_level, faction.strengthen_hp_level)
    p.strengthen_ct_level = min(
        p.strengthen_ct_max_level, faction.strengthen_ct_level)
    p.strengthen_df_level = min(
        p.strengthen_df_max_level, faction.strengthen_df_level)


def notify_strengthen_change(factionID):
    faction = Faction.simple_load(
        factionID, ['memberset'])
    for e in faction.memberset:
        proxy.sync_strengthen(e, factionID)


@proxy.rpc
def sync_strengthen(entityID, factionID):
    from entity.manager import g_entityManager
    p = g_entityManager.get_player(entityID)
    update_strengthen_level(p, factionID)
    p.save()
    p.sync()


def get_faction_info(factionID):
    faction = Faction.get(factionID)
    if not faction:
        return {}
    player = Player.simple_load(faction.leaderID, [
        'prototypeID',
        'name'
    ])
    return dict(
        factionID=factionID,
        name=faction.name,
        level=FactionRankRanking.get_score(faction.factionID) or 1,
        mcount=len(faction.memberset),
        acount=len(faction.applyset),
        totalfp=faction.totalfp,
        todayfp=faction.todayfp,
        rank=FactionRankRanking.get_rank(factionID),
        prototypeID=player.prototypeID,
        leader=player.name,
        createtime=faction.createtime,
        notice=faction.notice,
        mode=faction.mode,
        strengthen_hp_level=faction.strengthen_hp_level,
        strengthen_at_level=faction.strengthen_at_level,
        strengthen_ct_level=faction.strengthen_ct_level,
        strengthen_df_level=faction.strengthen_df_level,
        can_strengthen=get_config(CanStrengthenConfig)[1].can,
        leaderID=faction.leaderID,
        dflag=faction.dflag,
    )


def get_faction_thumb(factionID):
    faction = Faction.get(factionID)
    if not faction:
        return {}
    player = Player.simple_load(faction.leaderID, [
        'prototypeID'
    ])
    return {
        'factionID': faction.factionID,
        'name': faction.name,
        'totalfp': faction.totalfp,
        'todayfp': faction.todayfp,
        'prototypeID': player.prototypeID,
        'mcount': len(faction.memberset),
    }


def validate_name(name):
    name = name.strip()
    uname = unicode(name)
    if not uname:
        return uname, msgTips.FAIL_MSG_FACTION_NAME_EMPTY
    if len(uname) > NAME_LENGTH_MAX:
        return uname, msgTips.FAIL_MSG_FACTION_NAME_TOOLONG
    if len(uname) < NAME_LENGTH_MIN:
        return uname, msgTips.FAIL_MSG_FACTION_NAME_TOOSHORT
    if trie.trie_contains(forbid_names_trie, uname):
        return uname, msgTips.FAIL_MSG_FACTION_NAME_INVALID
    return name, SUCCESS


def safe_remove(set, key):
    try:
        set.remove(key)
    except KeyError:
        pass


def recommend(factionID):
    FactionRecommendIndexing.register(factionID)


def unrecommend(factionID):
    FactionRecommendIndexing.unregister(factionID)


def isrecommend(factionID):
    return FactionRecommendIndexing.exists(factionID)


def scan_recommned(count):
    return map(int, FactionRecommendIndexing.randmembers(count=count))


def is_apply(player, factionID):
    return factionID in player.applyFactions


def is_applied(player):
    return player.applyFactions


def allow_apply_failure(factionID, entityID):
    faction = Faction.simple_load(
        factionID, ['applyset', 'memberset', 'leaderID'])
    safe_remove(faction.applyset, entityID)
    faction.save()
    proxy.sync_apply(faction.leaderID)
    player = Player.simple_load(entityID, [
        'factionID',
        'applyFactions',
        # 'applyFactionTime',
        'inviteFactionSet',
    ])
    if not isrecommend(factionID):
        return msgTips.FAIL_MSG_FACTION_MEMBERS_LIMIT_EXCEED
    if is_apply(player, factionID) and not player.factionID:  # 玩家还没有取消申请
        join_faction(player.entityID, factionID)
        faction.save()
        player.save()
        return SUCCESS
    return msgTips.FAIL_MSG_FACTION_ALREADY_CANCEL_APPLY


@proxy.rpc(failure=allow_apply_failure)
def allow_apply(factionID, entityID):
    faction = Faction.simple_load(
        factionID, ['applyset', 'memberset', 'leaderID'])
    safe_remove(faction.applyset, entityID)
    faction.save()
    proxy.sync_apply(faction.leaderID)
    player = g_entityManager.get_player(entityID)
    if not isrecommend(factionID):
        return msgTips.FAIL_MSG_FACTION_MEMBERS_LIMIT_EXCEED
    if is_apply(player, factionID) and not player.factionID:
        # 玩家还没有取消申请
        join_faction(player.entityID, factionID)
        player.save()
        player.sync()
        faction.save()
        return SUCCESS
    return msgTips.FAIL_MSG_FACTION_ALREADY_CANCEL_APPLY


def deny_apply_failure(factionID, entityID):
    faction = Faction.simple_load(factionID, ['applyset', 'leaderID'])
    safe_remove(faction.applyset, entityID)
    faction.save()
    proxy.sync_apply(faction.leaderID)
    player = Player.simple_load(
        entityID, ['applyFactions'])
    if is_apply(player, factionID):  # 玩家还没有取消申请
        safe_remove(player.applyFactions, factionID)
        # player.applyFactionTime = 0
        faction.save()
        player.save()
        return SUCCESS
    return msgTips.FAIL_MSG_FACTION_ALREADY_CANCEL_APPLY


@proxy.rpc(failure=deny_apply_failure)
def deny_apply(factionID, entityID):
    player = g_entityManager.get_player(entityID)
    faction = Faction.simple_load(factionID, ['applyset', 'leaderID'])
    safe_remove(faction.applyset, entityID)
    faction.save()
    proxy.sync_apply(faction.leaderID)
    if is_apply(player, factionID):  # 玩家还没有取消申请
        safe_remove(player.applyFactions, factionID)
        # player.applyFactionID = 0
        # player.applyFactionTime = 0
        faction.save()
        player.save()
        player.sync()
        return SUCCESS
    return msgTips.FAIL_MSG_FACTION_ALREADY_CANCEL_APPLY


def invite_member_failure(factionID, entityID):
    faction = Faction.simple_load(factionID, ['inviteset'])
    player = Player.simple_load(entityID, [
        'factionID',
        # 'applyFactionID',
        # 'applyFactionTime',
        'inviteFactionSet',
        'level'
    ])
    if player.factionID:
        return msgTips.FAIL_MSG_FACTION_ALREADY_HAD_FACTION
    if player.level < INVITE_LEVEL_LIMIT:
        return msgTips.FAIL_MSG_FACTION_NOT_ENOUGH_LEVEL
    faction.inviteset.add(player.entityID)
    faction.save()
    player.inviteFactionSet.add(factionID)
    player.save()
    return SUCCESS


@proxy.rpc(failure=invite_member_failure)
def invite_member(factionID, entityID):
    player = g_entityManager.get_player(entityID)
    faction = Faction.simple_load(factionID, ['inviteset'])
    if player.factionID:
        return msgTips.FAIL_MSG_FACTION_ALREADY_HAD_FACTION
    # if player.applyFactionTime and \
    #         player.applyFactionTime < int(time.time()):
    #     return msgTips.FAIL_MSG_FACTION_ALREADY_APPLYED
    if player.level < INVITE_LEVEL_LIMIT:
        return msgTips.FAIL_MSG_FACTION_NOT_ENOUGH_LEVEL
    faction.inviteset.add(player.entityID)
    faction.save()
    player.inviteFactionSet.add(factionID)
    player.save()
    player.sync()
    return SUCCESS


def kick_member_failure(factionID, entityID):
    faction = Faction.simple_load(factionID, ['name', 'memberset'])
    player = Player.simple_load(
        entityID, ['factionID', 'joinFactionTime', 'mailset'])
    if player.factionID == factionID:
        now = int(time.time())
        if player.joinFactionTime and \
                (now - player.joinFactionTime) < QUITFACTIONCD:
            return msgTips.FAIL_MSG_FACTION_CAN_NOT_LEAVE
        clean_faction(player.entityID)
        faction.save()
        dt = datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S")
        title, content, ID = get_mail("FactionKick")
        send_mail(
            entityID, title, content.format(dt, faction.name), configID=ID)
        return SUCCESS
    return msgTips.FAIL_MSG_FACTION_MEMBER_ALREADY_QUIT


@proxy.rpc(failure=kick_member_failure)
def kick_member(factionID, entityID):
    player = g_entityManager.get_player(entityID)
    faction = Faction.simple_load(factionID, ['name', 'memberset'])
    if player.factionID == factionID:
        now = int(time.time())
        if player.joinFactionTime and \
                (now - player.joinFactionTime) < QUITFACTIONCD:
            return msgTips.FAIL_MSG_FACTION_CAN_NOT_LEAVE
        clean_faction(player.entityID)
        player.load_faction()
        faction.save()
        dt = datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S")
        title, content, ID = get_mail("FactionKick")
        send_mail(
            entityID, title, content.format(dt, faction.name), configID=ID)
        player.save()
        player.sync()
        return SUCCESS
    return msgTips.FAIL_MSG_FACTION_MEMBER_ALREADY_QUIT


def throne_member_failure(factionID, entityID):
    faction = Faction.simple_load(factionID, ['entityID', 'memberset'])
    player = Player.simple_load(entityID, [
        'factionID', 'joinFactionTime', 'faction_is_leader'])
    if player.factionID == factionID:
        if int(time.time()) - player.joinFactionTime <= THRONEFACTIONCD:
            return msgTips.FAIL_MSG_FACTION_CAN_NOT_THRONE_TO_NEWER
        faction.leaderID = player.entityID
        faction.save()
        player.faction_is_leader = True
        player.save()
        gm_logger.info({'faction': {
            'entityID': player.entityID, 'type': 'throne_faction',
            'factionID': faction.factionID,
        }})
        return SUCCESS
    return msgTips.FAIL_MSG_FACTION_IS_NOT_IN_FACTION


@proxy.rpc(failure=throne_member_failure)
def throne_member(factionID, entityID):
    player = g_entityManager.get_player(entityID)
    faction = Faction.simple_load(factionID, ['entityID', 'memberset'])
    if player.factionID == factionID:
        if int(time.time()) - player.joinFactionTime <= THRONEFACTIONCD:
            return msgTips.FAIL_MSG_FACTION_CAN_NOT_THRONE_TO_NEWER
        faction.leaderID = player.entityID
        faction.save()
        player.faction_is_leader = True
        player.save()
        player.sync()
        gm_logger.info({'faction': {
            'entityID': player.entityID, 'type': 'throne_faction',
            'factionID': faction.factionID,
        }})
        return SUCCESS
    return msgTips.FAIL_MSG_FACTION_IS_NOT_IN_FACTION


@proxy.rpc
def sync_apply(entityID):
    player = g_entityManager.get_player(entityID)
    if player:
        faction = Faction.simple_load(
            player.factionID, ['applyset', 'leaderID'])
        player.applyMemberSet = faction.applyset
        player.sync()
    return SUCCESS


def donate_sp(p, sp):
    # 并不消耗人物的能量
    # 推图等消耗能量后，贡献公会贡献
    if not p.factionID:
        return
    if p.todayfp_sp >= p.todayfp_sp_max:
        return
    configs = get_config(FactionDonateConfig)
    # 能量兑换贡献
    config = configs[4]
    mul = p.faction_sp / config.arg1
    base = config.arg2 * mul
    rest = p.todayfp_sp_max - p.todayfp_sp
    # 不能超过上限
    if base > rest:
        base = rest
    # 重新计算，需要消耗多少能量
    cost = base / config.arg2 * config.arg1
    # 贡献兑换声望
    fpconfig = configs[3]
    fp = base / fpconfig.arg1 * fpconfig.arg2
    logger.debug("donate sp %r", sp)
    logger.debug("faction_sp %r", p.faction_sp)
    logger.debug("cost sp %r", cost)
    p.faction_sp -= cost
    logger.debug("remain sp %r", p.faction_sp)
    p.fp += fp
    logger.debug("gain fp %r", fp)
    p.todayfp_sp += base
    logger.debug("donate %r", base)
    p.totalfp += base
    logger.debug("todayfp_sp %r", p.todayfp_sp)
    p.save()
    p.sync()
    Faction.incr_attribute(p.factionID, 'totalfp', base)


def notify_change(factionID):
    faction = Faction.simple_load(
        factionID, ['level', 'name', 'memberset', 'leaderID'])
    level = FactionRankRanking.get_score(factionID) or 1
    for e in faction.memberset:
        proxy.sync_faction(e, factionID, level, faction.name)


def sync_faction_offline(entityID, factionID, level, name):
    p = Player.simple_load(
        entityID,
        ['factionID', 'faction_level', 'faction_name'])
    if p.factionID == factionID:
        p.faction_level = level
        p.faction_name = name
        p.save()
        p.sync()
    return True


@proxy.rpc(failure=sync_faction_offline)
def sync_faction(entityID, factionID, level, name):
    from entity.manager import g_entityManager
    p = g_entityManager.get_player(entityID)
    if p.factionID == factionID:
        p.faction_level = level
        p.faction_name = name
        from task.manager import on_faction_level
        on_faction_level(p, level)
        p.save()
        p.sync()
    return True


def refresh_faction_task(p):
    configs = get_config(FactionTaskConfig)
    infos = get_config(TaskConfig)
    samples = []
    for taskID, c in configs.items():
        task = infos.get(taskID)
        if not task:
            continue
        if p.level < task.openlevel:
            continue
        if task.openfb:
            for f in task.openfb:
                if f not in p.fbscores:
                    continue
        samples.append([taskID, c.prob])
    # samples = [[k, v.prob] for k, v in configs.items()]
    taskID = weighted_random2(samples)
    p.faction_taskID = taskID
    p.save()
    p.sync()
