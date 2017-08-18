# coding:utf-8

import time
import msgpack
import logging
logger = logging.getLogger('scene')
from datetime import date as datedate
from yy.message.header import success_msg
from yy.utils import convert_list_to_dict

import settings

from config.configs import ExSceneInfoConfig, FbInfoConfig
from config.configs import GroupConfig
from config.configs import get_config, FbInfoByTypeConfig
from config.configs import SceneInfoConfig, BuyFbCostConfig
from config.configs import DlcFbInfoConfig

from protocol import poem_pb
from protocol.poem_pb import SceneInfos
from protocol.poem_pb import SCENE_INFOS

from player.manager import g_playerManager
from player.model import PlayerStarRanking
from player.model import PlayerAdvancedRanking
from scene.constants import FbType, CycleType


from reward.manager import apply_reward
from reward.manager import build_reward
from reward.manager import open_reward
from reward.manager import combine_reward
from reward.constants import RewardType

from gm.proxy import proxy

from player.formulas import get_vip_value


def validate_prevs(player, fbID):
    if not fbID:
        return fbID
    configs = get_config(FbInfoConfig)
    config = configs[fbID]
    if config.type == FbType.Dlc:
        for prev in config.prev:  # 检查前置
            info = get_config(DlcFbInfoConfig).get(fbID)
            if not info:
                return 0
            if prev and configs[prev].sceneID == config.sceneID \
                    and prev not in player.dlc_progress.get(info.dlcID, []):
                return 0
    for prev in config.prev:  # 检查前置
        if prev not in player.fbscores:
            fbID = 0
            break
    return fbID


def get_scene_list(player, fbs):
    configs = get_config(FbInfoConfig)
    scenes = set()
    for fb in fbs:
        config = configs[fb]
        scenes.add(config.sceneID)
    return sorted(scenes)


def get_fb_list(player, type):
    fbs = player.fbscores.keys()
    fbs_by_type = get_config(FbInfoByTypeConfig)
    if type == FbType.Normal:
        normal_fbs = fbs_by_type.get(FbType.Normal, [])
        guide_fbs = fbs_by_type.get(FbType.Guide, [])
        fbs = sorted(
            set(fbs).intersection([n.ID for n in normal_fbs + guide_fbs]))
    elif type == FbType.Advanced:
        advanced_fbs = fbs_by_type.get(type, [])
        fbs = sorted(set(fbs).intersection(set([a.ID for a in advanced_fbs])))
    elif type == FbType.Campaign:  # NOTE
        campaign_fbs = filter(
            lambda s: validate_prevs(player, s),
            [e.ID for e in fbs_by_type.get(type, [])])
        return sorted(set(fbs) & set(campaign_fbs)), \
            sorted(set(campaign_fbs) - set(fbs))
    else:
        raise NotImplementedError
    nexts = []
    configs = get_config(FbInfoConfig)
    if fbs:
        # 尝试获取下一关卡
        curr = configs[fbs[-1]]
        for p in curr.post:
            if validate_prevs(player, p):
                if type == configs[p].type:  # 过滤不同类型的副本
                    nexts.append(p)
    else:
        # 尝试获取第一个可以打的关卡
        if type == FbType.Normal:
            configs = fbs_by_type.get(FbType.Guide, []) + \
                fbs_by_type.get(FbType.Normal, [])
        elif type == FbType.Advanced:
            configs = fbs_by_type[FbType.Advanced]
        else:
            configs = fbs_by_type[type]
        if configs:
            if validate_prevs(player, configs[0].ID):
                nexts = [configs[0].ID]
    if type == FbType.Normal:
        # 过滤引导关卡
        if all([(g.ID in player.fbscores) for g in guide_fbs]):
            fbs = sorted(list(set(fbs).difference([g.ID for g in guide_fbs])))
    return fbs, nexts


def sync_scene_infos(player, type=FbType.Normal):
    fbInfos = get_config(FbInfoConfig)
    fbs, nexts = get_fb_list(player, type)
    rsp = SceneInfos()
    today_ts = int(time.mktime(datedate.today().timetuple()))
    for f in fbs:  # 过滤引导关卡
        count = get_today_remain_count(player, f, today=today_ts)
        rsp.fbs.add(**get_fb_info(player, f, today=today_ts))
    for next in nexts:
        count = get_today_remain_count(player, next, today=today_ts)
        info = fbInfos[next]
        rsp.fbs.add(fbID=next, count=count, isNew=True, openlv=info.openlv)
    for s in get_scene_list(player, fbs + nexts):
        rsp.scenes.add(**get_scene_info(player, s))
    rsp.type = type
    logger.debug(rsp)
    g_playerManager.sendto(player.entityID, success_msg(SCENE_INFOS, rsp))


def get_scene_info(player, sceneID, today=None):
    if not today:
        today = int(time.mktime(datedate.today().timetuple()))
    sceneInfos = get_config(SceneInfoConfig)
    exInfos = get_config(ExSceneInfoConfig)
    sceneInfo = sceneInfos[sceneID]._asdict()
    sceneInfo['count'] = -1
    sceneInfo['sceneID'] = sceneID
    exInfo = exInfos.get(sceneID)
    if exInfo:
        exInfo = exInfo._asdict()
        sceneInfo.update(exInfo)
        if exInfo['max'] != -1:
            used_count = 0
            for f in sceneInfo['fbs']:
                used_count += get_today_count(player, f, today=today)
            if sceneInfo["subtype"]:
                vip_count = get_vip_value(player.vip, "twinIsland_count")
            else:
                vip_count = get_vip_value(player.vip, "treeIsland_count")
            rest_count = max(exInfo['max'] + vip_count - used_count, 0)
            sceneInfo['count'] = rest_count
    return dict(sceneInfo)


def get_scene_today_remain_count(player, sceneID, today=None):
    if not today:
        today = int(time.mktime(datedate.today().timetuple()))
    return get_scene_info(player, sceneID, today=today)['count']


def get_fb_score(player, fbID):
    userfb = player.fbscores.get(fbID)
    if userfb:
        return userfb['score']
    else:
        return 0


def set_fb_score(player, fbID, score):
    userfb = player.fbscores.get(fbID)
    today_ts = int(time.mktime(datedate.today().timetuple()))
    if userfb:
        if userfb['date'] < today_ts:  # new day
            userfb['count'] = 1
            userfb['date'] = today_ts
        else:  # curr day
            userfb['count'] += 1
        if score > userfb['score']:
            userfb['score'] = score
        if score == 3:
            userfb['fullScoreCount'] += 1
        userfb['totalCount'] += 1
    else:
        userfb = {
            'score': score,
            'count': 1,
            'totalCount': 1,
            'fullScoreCount': (score == 3 and 1 or 0),
            'date': today_ts,
            'refreshCount': 0,  # 已用刷新次数
            'refreshDate': today_ts,
        }
    player.fbscores[fbID] = userfb
    player.save()
    # 遍历通关副本计算，星数和精英副本进度
    configs = get_config(FbInfoConfig)
    star_score = 0
    advanced_score = 0
    for k, v in player.fbscores.items():
        config = configs.get(k)
        if not config:
            continue
        if config.type in (FbType.Normal, FbType.Advanced):
            star_score += v.get('score', 0)
        if config.type == FbType.Advanced and k > advanced_score:
            advanced_score = k
    if star_score:
        PlayerStarRanking.update_score(player.entityID, star_score)
    if advanced_score:
        PlayerAdvancedRanking.update_score(player.entityID, advanced_score)
    return userfb


def refresh_fb(player, fbID, today=None):
    if not today:
        today = int(time.mktime(datedate.today().timetuple()))
    userfb = player.fbscores[fbID]
    userfb['refreshCount'] = get_refresh_used_count(
        player, fbID, today=today) + 1
    userfb['refreshDate'] = today
    userfb['count'] = 0
    player.fbscores[fbID] = userfb
    player.save()
    return userfb


def get_fb_info(player, fbID, today=None):
    if not today:
        today = int(time.mktime(datedate.today().timetuple()))
    fb = get_config(FbInfoConfig).get(fbID)
    if not fb:
        openlv = 0
    else:
        openlv = fb.openlv
    return {
        'fbID': fbID,
        'count': get_today_remain_count(player, fbID, today=today),
        'cost_count': get_remain_cost_count(player, fbID, today=today),
        'cost': get_cost_count_cost(player, fbID, today=today),
        'refresh_count': get_refresh_used_count(player, fbID, today=today),
        'refresh_cost': get_refresh_cost(player, fbID, today=today),
        'scores': get_fb_score(player, fbID),
        'openlv': openlv,
        'sceneID': fb.sceneID,
    }


def get_refresh_used_count(player, fbID, today=None):
    if not today:
        today = int(time.mktime(datedate.today().timetuple()))
    userfb = player.fbscores.get(fbID)
    if userfb:
        if userfb.get('refreshDate', 0) == today:
            return userfb.get('refreshCount', 0)
    return 0


def get_refresh_rest_count(player, fbID, today=None):
    used = get_refresh_used_count(player, fbID, today)
    return max(player.vip_refresh_fb_max_count - used, 0)


def get_refresh_cost(player, fbID, today=None):
    from config.configs import get_config, RefreshFbCostConfig
    configs = get_config(RefreshFbCostConfig)
    used = get_refresh_used_count(player, fbID, today)
    configs = get_config(RefreshFbCostConfig)
    config = configs.get(used + 1)
    if not config:
        config = configs[max(configs)]
    return config.cost


def get_today_count(player, fbID, today=None):
    if not today:
        today = int(time.mktime(datedate.today().timetuple()))
    userfb = player.fbscores.get(fbID)
    if userfb:
        if userfb['date'] == today:
            return userfb.get('count', 0)
    return 0


def get_today_remain_count(player, fbID, today=None):
    today_count = get_today_count(player, fbID, today=today)
    config = get_config(FbInfoConfig).get(fbID)
    if not config:
        return 0
    return max(config.max - today_count, 0)


def get_cost_count(player, fbID, today=None):
    today_count = get_today_count(player, fbID, today=today)
    config = get_config(FbInfoConfig).get(fbID)
    if not config:
        return 0
    return max(0, today_count - config.max)


def get_remain_cost_count(player, fbID, today=None):
    cost_count = get_cost_count(player, fbID, today=today)
    configs = get_config(BuyFbCostConfig)
    config = configs[max(configs)]
    return max(0, config.count - cost_count)


def get_cost_count_cost(player, fbID, today=None):
    cost_count = get_cost_count(player, fbID, today=today)
    configs = get_config(BuyFbCostConfig)
    config = configs.get(cost_count + 1)
    if not config:
        config = configs[max(configs)]
    return config.cost


def is_today_first(player, fbID, today=None):
    return get_today_count(player, fbID, today=today) == 0


def is_first(player, fbID):
    return fbID not in player.fbscores


def is_open(cycle, days, today=None):
    if not today:
        today = datedate.today()
    if cycle == CycleType.Week:
        if today.isoweekday() in days:
            return True
    return False


def get_monster_groups(fbID):
    groups = {}
    fbinfos = get_config(FbInfoConfig)
    groupinfos = get_config(GroupConfig)
    groupcount = 5
    monstercount = 4
    fbinfo = fbinfos[fbID]
    for groupindex in range(1, groupcount + 1):
        groupID = getattr(fbinfo, 'group{}'.format(groupindex))
        if not groupID:
            break
        groupinfo = groupinfos[groupID]
        monsters = {}
        realindex = 0
        for monsterindex in range(1, monstercount + 1):
            monsterID = getattr(groupinfo, 'monster_id{}'.format(monsterindex))
            monsterlevel = getattr(
                groupinfo,
                'monster_level{}'.format(monsterindex))
            if not monsterID:
                continue
            else:
                realindex += 1
            monsters[realindex] = (monsterlevel, monsterID)
        groups[groupindex] = monsters
    return groups


def is_last_of_scene(player, fbID):
    curr = get_config(FbInfoConfig)[fbID]
    scene = get_config(SceneInfoConfig)[curr.sceneID]
    if not scene.fbs:
        return False
    if fbID == scene.fbs[-1]:
        return all(map(lambda s: s in player.fbscores, scene.fbs[:-1]))
    return False


def filter_cleanfb_reward(reward):
    filter_reward = reward.apply_after()
    filter_items = ['slate']
    for item in filter_items:
        if item in filter_reward:
            filter_reward.pop(item)
    return filter_reward


def cleanfbs(p, fbID, count, cost):
    assert count > 0
    items = []
    rewards = {}
    useless = poem_pb.EnterFbResponse()
    # cost_ = dict(cost)
    # cost.clear()
    for i in range(count):
        item = poem_pb.CleanFbRspStruct()
        set_fb_score(p, fbID, 3)
        item.curFbInfo = poem_pb.FbInfo(
            **get_fb_info(p, fbID)
        )
        reward = open_reward(RewardType.FB, p, fbID, False, useless)
        result = filter_cleanfb_reward(reward)
        item.rewards = build_reward(result)
        rewards = combine_reward(rewards, result)
        # combine_reward(cost_, [], cost)
        items.append(item)
    apply_reward(p, rewards, cost=cost, type=RewardType.CleanFB)
    p.save()
    p.sync()
    return items


def reset_player_total_sp(player, cost):
    '''重置玩家今天消耗的总能量'''
    if not isinstance(cost, dict):
        return
    if 'sp' in cost:
        player.total_sp += cost['sp']
        player.save()
        return


def get_total_fb_scores(player):
    configs = get_config(FbInfoConfig)
    scores = 0
    for k in player.fbscores.keys():
        config = configs.get(k)
        if not config:
            continue
        if config.type in (FbType.Normal, FbType.Advanced):
            scores += get_fb_score(player, k)
    return scores


def get_fb_scores_by_chapter(player, chapter):
    configs = get_config(FbInfoConfig)
    scores = 0
    for k in player.fbscores.keys():
        config = configs.get(k)
        if not config:
            continue
        if config.type not in (FbType.Normal, FbType.Advanced):
            continue
        if config.sceneID == chapter:
            scores += get_fb_score(player, k)
    return scores

best_clearances = {}


def get_best_clearances_key():
    return "BEST_CLEARANCES{%d}{%d}" % \
        (settings.SESSION["ID"], settings.REGION["ID"])


def load_best_clearances(fbID=None):
    pool = settings.REDISES["index"]
    if fbID:
        with pool.ctx() as conn:
            rs = conn.execute("HGET", get_best_clearances_key(), fbID)
            if rs:
                rs = [fbID, rs]
            else:
                rs = []
    else:
        with pool.ctx() as conn:
            rs = conn.execute("HGETALL", get_best_clearances_key())
    dd = convert_list_to_dict(rs)
    result = {}
    for k, v in dd.items():
        if v:
            result[int(k)] = msgpack.loads(v)
    return result


def set_best_clearance(fbID, info):
    global best_clearances
    best_clearances[fbID] = info
    pool = settings.REDISES["index"]
    with pool.ctx() as conn:
        rs = conn.execute(
            "HSET", get_best_clearances_key(),
            fbID, msgpack.dumps(info))
    return rs


def update_best_clearance(fbID, info):
    clear = get_best_clearance(fbID)
    if not clear:
        flag = True
    else:
        #  获取星星多的 → 等级低的 → 通关时间早 → ID大小。
        flag = False
        if info.get("score", 0) > clear.get("score", 0):
            flag = True
        elif info.get("score", 0) == clear.get("score", 0):
            if info.get("level", 0) < clear.get("level", 0):
                flag = True
            elif info.get("level", 0) == clear.get("level", 0):
                if info.get("entityID", 0) < clear.get("entityID", 0):
                    flag = True
    if flag:
        set_best_clearance(fbID, info)
    return flag


def get_best_clearance(fbID):
    global best_clearances
    if not best_clearances:
        best_clearances = load_best_clearances()
        clear = best_clearances.get(fbID)
    else:
        clear = best_clearances.get(fbID)
        if not clear:
            clear = load_best_clearances(fbID)
    return clear


@proxy.rpc_batch
def sync_best_clearance(fbID):
    global best_clearances
    best_clearances.update(load_best_clearances(fbID=fbID))
