# coding:utf-8
import time
import random
import logging
logger = logging.getLogger("pvp")
from datetime import datetime
from player.model import PlayerPowerRanking
from player.model import Player
from player.model import PlayerLootLock
from pvp.manager import is_zombie
from pvp.manager import get_zombies_by_power
from pvp.manager import get_opponent_detail
from pvp.manager import get_zombies
from config.configs import get_config
from config.configs import LootConfig
from yy.utils import weighted_random2
from yy.utils import choice_one
from yy.utils import convert_list_to_dict
# from yy.db.redisscripts import load_redis_script
from gm.proxy import proxy
from campaign.manager import g_campaignManager


def boardcast_loot_count():
    from entity.manager import g_entityManager
    for p in g_entityManager.players.values():
        check_loot(p)


def check_loot(player, now=None):
    p = player
    if not now:
        now = datetime.now()
    else:
        if isinstance(now, (int, float)):
            now = datetime.fromtimestamp(now)
    dt = datetime.fromtimestamp(p.loot_last_resume_time)
    dt12 = datetime(now.year, now.month, now.day, 12)
    dt18 = datetime(now.year, now.month, now.day, 18)
    if now < dt12:
        pass
    elif now >= dt12 and now < dt18:
        if dt < dt12:
            p.loot_used_count = 0
            p.loot_last_resume_time = int(time.mktime(now.timetuple()))
    elif now >= dt18:
        if dt < dt18:
            p.loot_used_count = 0
            p.loot_last_resume_time = int(time.mktime(now.timetuple()))
    p.save()
    p.sync()


def loot_refresh_targets(player):
    targets = []
    configs = get_config(LootConfig)
    best = max([cs.type for cs in configs])
    has_best = False
    length = len(configs)
    for i in range(length):
        if has_best:  # 最高品质只出一个
            c = weighted_random2([
                (c, c.prob) for c in configs if c.type != best])
        else:
            c = weighted_random2([(c, c.prob) for c in configs])
            if c.type == best:
                player.loot_reset_crit_count = 0
                has_best = True
        targets.append({
            "type": c.type,
            "count": random.randint(c.min, c.max)})
    # 最高品质必须在最中间
    mid = length / 2
    for index, target in enumerate(targets):
        if target["type"] == best:
            if index != mid:  # 不在中间则交换位置
                targets[index], targets[mid] = targets[mid], targets[index]
            break
    if player.loot_reset_crit_count and player.loot_reset_crit_count % 5 == 0:
        # 刷新设保底，每刷5次必定出一个最高品质，刷到最高品质重新计算
        if targets[mid]["type"] != best:
            cc = configs[-1]
            targets[mid] = {
                "type": cc.type,
                "count": random.randint(cc.min, cc.max)}
            player.loot_reset_crit_count = 0
    lv = player.level
    kmap = {1: 0.7, 2: 0.8, 3: 0.9}
    base = 4 * lv * (62 + 0.0045 * lv * lv + 0.18 * lv)
    for target in targets:
        curr = kmap[target['type']] * base
        pmin = curr * 0.92 - 88
        pmax = curr * 1.08 + 88
        power = random.randint(int(pmin), int(pmax))
        target['power'] = power
    player.loot_targets_cache = targets
    player.loot_reset_crit_count += 1
    player.save()
    player.sync()
    return targets


def loot_target(player, power, loot, count):
    dvalue = 100 + power * 0.06
    s, e = int(max(0, power - dvalue)), int(power + dvalue)
    samples = set(
        PlayerPowerRanking.get_range_by_score(
            s, e, count=16)
    ) - set([player.entityID])
    zombies = set(get_zombies_by_power(s, e, count=5))
    # s = max(player.level - 12, 1)
    # e = max(player.level - 6, 1)
    # samples = set(
    #     PlayerLevelRanking.get_range_by_score(
    #         s, e, count=16)
    # ) - set([player.entityID])
    # zombies = set(reduce(
    #     lambda x, y: x+y,
    #     [get_zombies_by_level(l)[:5]
    #         for l in range(s, e + 1)]))
    samples = samples.union(zombies)
    chosen = choice_one(list(samples))
    logger.debug("search targets is {}".format(samples))
    if not is_zombie(chosen):
        rest = search_targets_loot([chosen], loot)[0]
        p = Player.simple_load(chosen, "loot_protect_time")
        now = int(time.time())
        if PlayerLootLock.locked(chosen) or \
           now < p.loot_protect_time and rest < 50 and rest < count:
            chosen = choice_one(list(zombies))
    if not chosen:
        chosen = choice_one(list(get_zombies()))
    # # NOTE FIXME FOR DEBUG
    # chosen = player.entityID
    return get_opponent_detail(chosen)


# @load_redis_script(pool=Player.pool)
# def search_targets_loot(targets, loot):
#     '''\
#     local key_mats = KEYS[1]
#     local key_temp = ARGV[1]
#     local loot = ARGV[2]
#     local targets = {}
#     local result = {}
#     for i, t in ipairs(ARGV) do
#         if i ~= 1 and i ~= 2 then
#             t = tonumber(t)
#             local mat_count = redis.call("HGET", string.format(key_mats, t), loot)
#             mat_count = tonumber(mat_count) or 0
#             local temp_count = redis.call("HGET", string.format(key_temp, t), loot)
#             temp_count = tonumber(temp_count) or 0
#             table.insert(result, temp_count + mat_count)
#         end
#     end
#     return result\
#     '''
#     vals = ["loot_temp_mats_p{%d}", loot] + list(targets)
#     return ("mats_p{%d}", ), tuple(vals)

def search_targets_loot(targets, loot):
    assert False, "not support"


# @load_redis_script(pool=Player.pool)
# def cost_looted_mats(entityID):
#     """\
#     local key_temp = KEYS[1]
#     local result = redis.call("HGETALL", key_temp)
#     redis.call("DEL", key_temp)
#     return result\
#     """
#     return ("loot_temp_mats_p{%d}" % entityID, ), tuple()

def cost_looted_mats(entityID):
    assert False, "not support"


def sync_looted_mats(player):
    mats = convert_list_to_dict(cost_looted_mats(player.entityID))
    for k, v in mats.items():
        player.cost_mats([[k, int(v)]])
    player.save()
    player.sync()


# @load_redis_script(pool=Player.pool)
# def cost_mats(entityID, loot, count):
#     """\
#     local key_mats = KEYS[1]
#     local key_temp = ARGV[1]
#     local loot = ARGV[2]
#     local count = tonumber(ARGV[3]) or 0
#     if loot == 0 then
#         return 0
#     end
#     if count == 0 then
#         return 1
#     end
#     local mats = redis.call("HGETALL", key_mats)
#     local temp = redis.call("HGETALL", key_temp)
#     local rest = 0
#     for i, v in ipairs(mats) do
#         if tostring(loot) == v then
#             rest = tonumber(mats[i+1])
#         end
#     end
#     for i, v in ipairs(temp) do
#         if tostring(loot) == v then
#             rest = rest - tonumber(temp[i+1])
#         end
#     end
#     if rest < 0 then
#         rest = 0
#     end
#     if rest > count then
#         count = (tonumber(temp[tostring(loot)]) or 0) + count
#         redis.call("HSET", key_temp, loot, count)
#         return 1
#     else
#         return 0
#     end\
#     """
#     return ("mats_p{%d}" % entityID, ),\
#         ("loot_temp_mats_p{%d}" % entityID, loot, count)


def cost_mats(entityID, loot, count):
    assert False, "not support"


def sync_loot_cost_offline(entityID, history):
    if not history["result"]:  # lose
        if not cost_mats(entityID, history["loot"], history["count"]):
            return
        now = int(time.time())
        Player.save_attributes(
            entityID,
            loot_protect_time=now + 3600
        )
    Player.pool.execute(
        "LPUSH",
        "loot_history_p{%d}" %
        entityID,
        Player.fields['loot_history'].encoder(history))
    Player.pool.execute("LTRIM", "loot_history_p{%d}" % entityID, 0, 10)


@proxy.rpc(failure=sync_loot_cost_offline)
def sync_loot_cost(entityID, history):
    from entity.manager import g_entityManager
    p = g_entityManager.get_player(entityID)
    if not history["result"]:  # lose
        costed = cost_mats(entityID, history["loot"], history["count"])
        if not costed:
            return
        now = int(time.time())
        p.loot_protect_time = now + 3600
    p.loot_history.appendleft(history)
    p.loot_history.ltrim(0, 10)
    p.save()
    p.sync()


def loot_reward_in_campaign(loot):
    config = g_campaignManager.loot_campaign.get_current()
    if not config:
        return loot
    return config.group * loot
