# coding:utf-8
import time
import random
import logging
logger = logging.getLogger("pvp")
from functools import reduce

from yy.utils import choice_one
from yy.entity.storage.redis import make_key
from yy.db.redisscripts import load_redis_script

from common import msgTips
from gm.proxy import proxy
from entity.manager import g_entityManager
from protocol import poem_pb
from pvp.manager import get_opponent_detail
from pvp.manager import get_zombies_by_level
from pvp.manager import is_zombie
from pvp.manager import get_zombies
from config.configs import get_config
from config.configs import PvpGroupConfig
from config.configs import MineConfig
from config.configs import MineProductivity
from config.configs import PetConfig
from player.model import Player
from player.model import PlayerMineLock
from player.model import PlayerLevelRanking
from player.formulas import get_mine_level
from player.formulas import get_mine_safety
from player.formulas import get_mine_maximum
from player.formulas import get_open_level
from campaign.manager import g_campaignManager
from lineup.constants import LineupType


def sync_products_offline(entityID, history):
    from player.model import Player
    # pkey = make_key(Player.store_tag, entityID)
    cc, _, _ = cost_products(
        entityID,
        history['level'],
        history['booty'],
        history['type']
    )
    if cc:
        Player.pool.execute(
            "LPUSH",
            "mine_rob_history_p{%d}" %
            entityID,
            Player.fields["mine_rob_history"].encoder(history))
        now = int(time.time())
        Player.save_attributes(
            entityID,
            mine_protect_time=now +
            3600 * history['protect_time']
        )
    return "FAILURE"


@proxy.rpc(failure=sync_products_offline)
def sync_products(entityID, history):
    from entity.manager import g_entityManager
    p = g_entityManager.get_player(entityID)
    cc, _, _ = cost_player_products(p, history["booty"], history['type'])
    if cc:
        now = int(time.time())
        p.mine_protect_time = now + 3600 * history['protect_time']
        p.mine_rob_history.appendleft(history)
        p.mine_rob_history_flag = True
        p.save()
        p.sync()
    return 'SUCCESS'


def init_rob_count(player):
    if not player.mine_time1 and not player.mine_time2:
        player.mine_rob_count = player.mine_rob_max_count


def check_rob(player):
    if player.mine_level1:
        init_rob_count(player)
        cost_player_products(player, 0, poem_pb.MineType1)
    if player.mine_level2:
        init_rob_count(player)
        cost_player_products(player, 0, poem_pb.MineType2)


def cost_player_products(player, cost, type):
    result = cost_products(
        player.entityID,
        player.level,
        cost,
        type
    )
    products, gain, now = result
    setattr(player, "mine_products%d" % type, products)
    setattr(player, "mine_time%d" % type, now)
    player.remove_dirty(["mine_products%d" % type, "mine_time%d" % type])
    return products, gain, now


def resize_rob_history_by_time(player, last=7 * 3600):
    # 7日
    now = int(time.time())
    i = len(player.mine_rob_history)
    for i, h in enumerate(player.mine_rob_history):
        if now - h['time'] > last:
            break
    if i < len(player.mine_rob_history) - 1:
        player.mine_rob_history.ltrim(0, i)
        player.save()


def get_lineuptype_by_type(type):
    return {
        poem_pb.MineType1: LineupType.Mine1,
        poem_pb.MineType2: LineupType.Mine2
    }[type]


def on_mine_change(player, type=None):
    if not type:
        types = [poem_pb.MineType1, poem_pb.MineType2]
    else:
        types = [type]
    for type in types:
        pets = [player.pets[p] for p in player.lineups.get(
            get_lineuptype_by_type(type), []) if p]
        if not pets:
            return
        mine_level = getattr(player, 'mine_level%d' % type)
        if not mine_level:
            return
        config = get_config(MineConfig).get(mine_level)
        if not config:
            return
        curr_productivity = getattr(player, "mine_productivity%d" % type)
        productivity = getattr(config, "mine_productivity%d" % type)
        pet_configs = get_config(PetConfig)
        infos = [pet_configs[i.prototypeID] for i in pets]
        configs = get_config(MineProductivity)
        percent = 0
        for info in infos:
            c = configs[info.mtype, info.rarity]
            percent += getattr(c, "productivity%d" % type)
        productivity = int(productivity * (1 + (percent / float(100))))
        if curr_productivity != productivity:
            # 改变前先将计算当前产出
            init_rob_count(player)
            cost_player_products(player, 0, type)
            assert productivity, "not productivity"
            setattr(player, "mine_productivity%d" % type, productivity)
    player.save()
    player.sync()


def on_mine1_change(player):
    on_mine_change(player, poem_pb.MineType1)


def on_mine2_change(player):
    on_mine_change(player, poem_pb.MineType2)


# @load_redis_script(pool=Player.pool)
# def cost_products(entityID, level, cost, type):
#     '''\
#     local key = KEYS[1]
#     local key_products = ARGV[1]
#     local key_productivity = ARGV[2]
#     local key_time = ARGV[3]
#     local cost = tonumber(ARGV[4])
#     local now = tonumber(ARGV[5])
#     local safety = tonumber(ARGV[6] or 0)
#     local maximum = tonumber(ARGV[7] or 0)
#     local products, productivity, time = unpack(redis.call("HMGET", key, key_products, key_productivity, key_time))
#     time = tonumber(time or 0)
#     if time == 0 then
#         products = 0 --maximum
#     else
#         products = tonumber(products or 0)
#         productivity = tonumber(productivity or 0)
#         products = math.floor(products + (now - time) / (3600 / productivity))
#         if products > maximum then
#             products = maximum
#         end
#     end
#     if (products < cost) or (cost < 0) then
#         cost = products
#         products = 0
#     else
#         products = products - cost
#     end
#     redis.call("HMSET", key, key_products, products, key_time, now)
#     return {products, cost, now}\
#     '''
#     # 返回剩余，消耗，时间
#     # @cost 为负数，表示扣除所有products
#     keys = (make_key(Player.store_tag, entityID), )
#     mine_level = get_mine_level(type, level)
#     safety = get_mine_safety(type, mine_level)
#     maximum = get_mine_maximum(type, mine_level)
#     vals = []
#     for f in ("mine_products%d", "mine_productivity%d", "mine_time%d"):
#         vals.append(f % type)
#     vals.extend((cost, int(time.time()), safety, maximum))
#     vals = tuple(vals)
#     return keys, vals


def cost_products(entityID, level, cost, type):
    p = g_entityManager.get_player(entityID)
    key_products = "mine_products%d" % type
    key_productivity = "mine_productivity%d" % type
    key_time = "mine_time%d" % type
    sync = True
    if not p:
        sync = False
        p = Player.simple_load(entityID, [
            key_products,
            key_productivity,
            key_time
        ])
    mine_level = get_mine_level(type, level)
    # safety = get_mine_safety(type, mine_level)
    maximum = get_mine_maximum(type, mine_level)
    products = getattr(p, key_products, 0)
    productivity = getattr(p, key_productivity, 0)
    mine_time = getattr(p, key_time, 0)
    now = int(time.time())
    if not mine_time or not productivity:
        products = 0
    else:
        products = int(
            products + (now - mine_time) / (3600 / float(productivity)))
        if products > maximum:
            products = maximum
    if (products < cost) or (cost < 0):
        cost = products
        products = 0
    else:
        products -= cost
    setattr(p, key_products, products)
    setattr(p, key_time, now)
    p.save()
    if sync:
        p.sync()
    return products, cost, now


def calc_booty(
        now,
        mine_products,
        mine_time,
        mine_productivity,
        mine_maximum,
        mine_safety):
    return min(
        int(mine_products +
            (now - mine_time) * float(mine_productivity) / 3600),
        mine_maximum
    ) - mine_safety


def get_curr_products(entityID, now, type):
    p = Player.simple_load(entityID, [
        'level',
        'mine_products%d' % type,
        'mine_time%d' % type,
        'mine_productivity%d' % type,
    ])
    mine_level = get_mine_level(type, p.level)
    safety = get_mine_safety(type, mine_level)
    maximum = get_mine_maximum(type, mine_level)
    curr = calc_booty(
        now,
        getattr(p, 'mine_products%d' % type),
        getattr(p, 'mine_time%d' % type),
        getattr(p, 'mine_productivity%d' % type),
        maximum,
        safety,
    )
    return curr


def rob_target(player, targetID, booty, type):
    if is_zombie(targetID):
        detail = get_opponent_detail(targetID)
        return ('', booty, detail), 0
    now = int(time.time())
    # 检查保护
    t = Player.simple_load(targetID, ['mine_protect_time'])
    if t.mine_protect_time > now:
        return None, msgTips.FAIL_MSG_ROB_ALREADY_IN_PROTECTION
    try:  # 检查是否正在战斗
        unlocking_key = PlayerMineLock.lock(targetID)
        curr = get_curr_products(targetID, now, type)
        if booty is not None:
            if curr < booty:
                PlayerMineLock.unlock(targetID, unlocking_key)
                return None, msgTips.FAIL_MSG_ROB_ALREADY_HARVESTED
        else:
            booty = curr
        booty = max(booty, 0)
        detail = get_opponent_detail(
            targetID, type=get_lineuptype_by_type(type))
        return (unlocking_key, booty, detail), 0
    except PlayerMineLock.LockedError:
        return None, msgTips.FAIL_MSG_ROB_ALREADY_ROBBED

SAMPLE_COUNT = 30
DETAIL_COUNT = 10
SEARCH_COUNT = 3


def search_targets(player):
    # dvalue = 100 + player.power * 0.06
    # s, e = int(max(0, player.power - dvalue)), int(player.power + dvalue)
    # sample = set(
    #     PlayerPowerRanking.get_range_by_score(
    #         s, e, count=SAMPLE_COUNT)
    # ) - set([player.entityID])
    s, e = max(0, player.level - 2), player.level + 2
    sample = set(
        PlayerLevelRanking.get_range_by_score(
            s, e, count=SAMPLE_COUNT)
    ) - set([player.entityID])
    try:
        sample = random.sample(sample, DETAIL_COUNT)
    except ValueError:
        pass
    logger.debug("random sample is {}".format(sample))
    from player.formulas import get_mine_level
    # 过滤未开启的
    types = [i for i in poem_pb.MineType1, poem_pb.MineType2
             if get_mine_level(i, player.level) > 0] or [poem_pb.MineType1]
    targets = g_entityManager.get_players_info(sample, [
        "entityID", "name", "level", "prototypeID", 'mine_protect_time'
    ] + reduce(lambda x, y: x + y, [[
        "mine_products%d" % t,
        "mine_productivity%d" % t,
        "mine_time%d" % t,
        "mine_maximum%d" % t,
        "mine_safety%d" % t,
    ] for t in types]))
    _targets = []
    for target in targets:
        for t in types:
            _target = dict(target)
            _target['type'] = t
            _target['mine_products'] = _target['mine_products%d' % t]
            _target['mine_productivity'] = _target['mine_productivity%d' % t]
            _target['mine_time'] = _target['mine_time%d' % t]
            mine_level = get_mine_level(t, _target['level'])
            _target['mine_safety'] = get_mine_safety(t, mine_level)
            _target['mine_maximum'] = get_mine_maximum(t, mine_level)
            if not _target['mine_productivity']:
                continue
            _targets.append(_target)
    now = int(time.time())
    targets = sorted(_targets, key=lambda s: int(s['mine_time'] or now))
    chosens = []
    filterset = set()  # 过滤重复的玩家, 只能被匹配一次
    for t in targets:
        if t['entityID'] in filterset:
            continue
        if PlayerMineLock.locked(t["entityID"]):
            continue
        if t['mine_protect_time'] > now:
            continue
        if len(chosens) >= SEARCH_COUNT:
            break
        booty = calc_booty(now,
                           t['mine_products'],
                           t['mine_time'],
                           t['mine_productivity'],
                           t['mine_maximum'],
                           t['mine_safety']
                           )
        if booty > 0:
            chosens.append({
                'booty': max(booty, 0),
                'fought': False,
                'entityID': t['entityID'],
                'name': t['name'],
                'prototypeID': t['prototypeID'],
                'level': t['level'],
                'type': t['type'],
            })
            filterset.add(t['entityID'])
        if len(chosens) >= 2:
            break
    if len(chosens) < SEARCH_COUNT:
        lv = get_open_level("get_money1")
        zombies1 = get_zombies_by_level(max(player.level - 2, lv), hide=True)
        lv = get_open_level("get_exp1")
        zombies2 = get_zombies_by_level(max(player.level - 2, lv), hide=True)

        if not zombies1:
            zombies1 = get_zombies()
        logger.debug("zombies1 is {}".format(zombies1))
        if not zombies2:
            zombies2 = get_zombies()
        logger.debug("zombies2 is {}".format(zombies2))
        if zombies1 or zombies2:
            configs = get_config(PvpGroupConfig)
            while len(chosens) < SEARCH_COUNT:
                type = choice_one(types)
                if type == poem_pb.MineType1:
                    zombies = zombies1
                    booty_field = "rob_money"
                else:
                    zombies = zombies2
                    booty_field = "rob_soul"
                if not zombies1 and not zombies2:
                    break
                got = choice_one(zombies)
                config = configs[got]
                if not config.visible:
                    continue
                booty = getattr(config, booty_field, 0)
                zombies.remove(got)
                chosens.append({
                    'booty': booty,
                    'fought': False,
                    'entityID': config.ID,
                    'name': config.name,
                    'prototypeID': config.monster_id1,
                    'level': config.level,
                    'type': type,
                })
    random.shuffle(chosens)
    logger.debug("search targets is {}".format(chosens))
    player.mine_targets_detail_cache = chosens
    player.save()
    player.sync()
    return chosens


def rob_reward_in_campaign(gain):
    config = g_campaignManager.rob_campaign.get_current()
    if not config:
        return gain
    return config.group * gain
