import urllib
import bisect
import logging
logger = logging.getLogger('pvp')

import gevent
import gevent.queue
from config.configs import get_config
from config.configs import PvpGroupConfig
from config.configs import PvpGroupByLevelConfig
from config.configs import PvpGroupEquipsConfig
from config.configs import PvpGroupByPowerConfig
from config.configs import PvpGroupByGroupConfig
# from player.model import Player
from player.model import PlayerOnlineIndexing
from gm.proxy import proxy
import settings
from session.utils import username2sdk


def index(a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    raise ValueError


def find_le(a, x):
    'Find rightmost value less than or equal to x'
    i = bisect.bisect_right(a, x)
    if i:
        return a[:i-1]
    return []


def find_ge(a, x):
    'Find leftmost item greater than or equal to x'
    i = bisect.bisect_left(a, x)
    if i != len(a):
        return a[i:]
    return []

__sorted_powers = None


def get_power_range(lo=None, hi=None):
    global __sorted_powers
    if not __sorted_powers:
        __sorted_powers = sorted(get_config(PvpGroupByPowerConfig))
    powers = __sorted_powers
    if lo is not None:
        powers = find_ge(powers, lo)
    if hi is not None:
        powers = find_le(powers, hi)
    return powers


def get_zombie(zombieID):
    config = get_config(PvpGroupConfig)[zombieID]
    equips = get_config(PvpGroupEquipsConfig)
    zombie = {
        'entityID': config.ID,
        'name': config.name,
        'level': config.level,
        'career': config.career,
        'prototypeID': config.monster_id1,
        'equipeds': [],
        'power': config.power,
        'totalbp': config.score,
        'rank_win_count': 2,
        'pvpgrad': 1,
        'faction_name': '',
    }
    pets = zombie['pets'] = []
    for pos, (monster, level, star, equip) in \
            enumerate(zip(
                config.monsters,
                config.levels,
                config.stars,
                config.equips)):
        if not monster:
            continue
        skill1, skill2, skill3, skill4, skill5 = config.skills[pos]
        pets.append({
            'prototypeID': monster,
            'level': level or 1,
            'skill': 1,
            'skill1': skill1,
            'skill2': skill2,
            'skill3': skill3,
            'skill4': skill4,
            'skill5': skill5,
            'subattr1': 0,
            'subattr2': 0,
            'posIndex': pos,
            'isTeamLeader': (pos == 0),
            'breaklevel': star or 1,
        })
        equip = equips.get(equip)
        if not equip:
            continue
        for e in equip.equips:
            zombie["equipeds"].append({
                "index": pos,
                "equipID": 0,
                "prototypeID": e[0],
                "level": e[1],
                "step": e[2],
            })
    return zombie


def get_zombies_by_level(level, hide=True, group=None):
    levels = get_config(PvpGroupByLevelConfig)
    configs = get_config(PvpGroupConfig)
    groups = []
    if group is not None:
        groups = {i.ID for i in get_config(PvpGroupByGroupConfig)[group]}
    if hide:
        result = [i.ID for i in levels.get(level, []) if configs[i.ID].visible]
    else:
        result = [i.ID for i in levels.get(level, [])]
    if group is not None:
        result = list(set(result) & set(groups))
    result = sorted(result, key=lambda k: configs[k].power)
    return result


def get_zombies_by_power(
        low_or_current, high=None,
        count=None, hide=True, group=None, must=False):
    if count == 0:
        return
    configs = get_config(PvpGroupConfig)
    power_range = get_power_range(low_or_current, high)
    powers = get_config(PvpGroupByPowerConfig)
    result = []
    for power in power_range:
        by_power = powers.get(power, [])
        for each in by_power:
            config = configs.get(each.ID)
            if count is not None and len(result) >= count:
                break
            if not config:
                continue
            if hide and not config.visible:
                continue
            if group and config.group != group:
                continue
            result.append(config.ID)
    return result


def get_zombies():
    return get_config(PvpGroupConfig).keys()


def is_zombie(zombieID):
    return zombieID < 0

pet_required_fields = [
    'entityID', 'prototypeID', 'level', 'breaklevel',
    'skill', "relations",
    "skill1", "skill2", "skill3", "skill4", "skill5", "daily_restHP",
]


def update_onlines(details):
    entityIDs = [i["entityID"] for i in details]
    if not entityIDs:
        return []
    onlines = PlayerOnlineIndexing.pool.execute(
        'HMGET', PlayerOnlineIndexing.key, *entityIDs)
    for index, v in enumerate(onlines):
        details[index].update(online=bool(v or 0))
    return details


def get_opponent_detail(oppID, type=None):
    if is_zombie(oppID):
        return get_zombie(oppID)
    from lineup.manager import get_lineup_info
    from equip.manager import get_equipeds_infos
    from entity.manager import g_entityManager
    pets = []
    try:
        pets = get_lineup_info(oppID,  pet_required_fields, type=type)
    except AttributeError:
        logger.error("Not exists oppID %d", oppID)
        return None
    for pos, pet in enumerate(pets):
        # pet['posIndex'] = pos
        pet['isTeamLeader'] = (pos == 0)
    detail = g_entityManager.get_players_info([oppID], [
        'entityID', 'name',
        'level', 'career',
        'prototypeID',
        'strengthen_hp_level',
        'strengthen_at_level',
        'strengthen_ct_level',
        'strengthen_df_level',
        'rank_win_count',
        'vip',
        'credits',
        'faction_name',
        'lastlogin',
        # 'worldID',
        'pvpgrad',
        'groupID',
        'borderID',
        'point',
        'swap_win_count',
        'power_cache',
        'daily_kill_count',
        'daily_inspire_buff',
        'daily_max_win_count',
        'ambition',
        'vip_ambition',
        'player_equip1',
        'player_equip2',
        'player_equip3',
        'player_equip4',
        'player_equip5',
        'player_equip6',
        'inlay1',
        'inlay2',
        'inlay3',
        'inlay4',
        'inlay5',
        'inlay6',
        'fbprocess',
        'fbadvance',
        'campaign_honor_point',
    ])[0]
    detail['power'] = detail['power_cache']
    detail['pets'] = pets
    detail["equipeds"] = []
    for pet in pets:
        if pet:
            detail["equipeds"].extend(
                get_equipeds_infos(
                    oppID, pet["entityID"], pet["posIndex"], detail=True))
    # detail["online"] = PlayerOnlineIndexing.get_pk(detail["entityID"])
    return detail


def get_opponent_detail_all(oppID):
    from lineup.manager import get_lineup_defend_info
    detail = get_opponent_detail(oppID)
    if is_zombie(oppID):
        pets = detail["pets"]
    else:
        try:
            pets = get_lineup_defend_info(oppID, pet_required_fields)
        except AttributeError:
            logger.error("Not exists oppID %d", oppID)
            return None
        if not pets:
            pets = detail["pets"]
    detail["pets2"] = pets
    return detail


@proxy.rpc_batch
def get_players():
    from entity.manager import g_entityManager
    result = []
    for p in g_entityManager.players.values():
        result.append({
            "entityID": p.entityID,
            "name": p.name,
            "level": p.level,
            "career": p.career,
            "prototypeID": p.prototypeID,
            "borderID": p.borderID,
        })
    return result


def npc2zombie(index, level):
    return - (index * 1000 + level)

try:
    settings.FIGHT_VERIFY_URL
except AttributeError:
    verify_queue = None
else:
    verify_queue = gevent.queue.Queue()


def fight_verify_worker():
    from geventhttpclient import HTTPClient
    verify_client = HTTPClient.from_url(settings.FIGHT_VERIFY_URL)
    counter = 0

    while True:
        task = verify_queue.get()
        if not task:
            break

        counter += 1
        if counter % settings.FIGHT_VERIFY_SKIP != 0:
            continue

        try:
            player, fight, fbID = task
            args = {
                'entityID': player.entityID,
                'name': player.name.encode('utf-8'),
                'worldID': settings.REGION['ID'],
                'sdkType': username2sdk(player.username),
                'fbID': fbID,
            }
            body = fight.SerializeToString()
            verify_client.post('/?'+urllib.urlencode(args), body)
        except:
            logger.exception('fight verify worker')


def remove_verify_queue(t):
    global verify_queue
    logger.error('verify thread dead, remove verify queue.')
    verify_queue = None


if verify_queue:
    verify_workers = [gevent.spawn(fight_verify_worker) for i in range(settings.FIGHT_VERIFY_WORKERS)]
    for t in verify_workers:
        t.link(remove_verify_queue)
else:
    verify_workers = []


def send_fight_verify(player, fight, fbID=0):
    if verify_queue and fight.fightResult:
        verify_queue.put((player, fight.replay, fbID))
