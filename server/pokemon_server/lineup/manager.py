# coding:utf-8
import time
import logging
logger = logging.getLogger('lineup')
from functools import partial

from protocol import poem_pb
from protocol.poem_pb import Lineups
from protocol.poem_pb import LINEUP_LINEUPS
from constants import LINEUP_LENGTH_LIMIT, LineupType
from yy.message.header import success_msg
from player.manager import g_playerManager
from equip.manager import get_equipeds_infos


def init_lineups(player):
    pets = sorted(player.pets.values(), key=lambda s: s.entityID)
    assert pets, 'not pet when init lineup'
    lineup = [pet.entityID for pet in pets][:LINEUP_LENGTH_LIMIT]
    while len(lineup) < LINEUP_LENGTH_LIMIT:
        lineup.append(0)
    player.lineups[LineupType.ATK] = lineup
    logger.debug("init lineup %s", lineup)


def sync_lineups(player):
    rsp = Lineups()
    for type, _lineup in player.lineups.items():
        lineup = rsp.lineups.add(line=_lineup, type=type)
        if type == LineupType.ATK:
            for index, petID in enumerate(_lineup):
                if petID:
                    for info in get_equipeds_infos(
                            player.entityID, petID, index):
                        lineup.equipeds.add(**info)
    g_playerManager.sendto(player.entityID, success_msg(LINEUP_LINEUPS, rsp))


def in_lineup(player, petID, dispatch=False, type=None):
    # 检查是否在阵上
    if not type:
        lineups = player.lineups.values()
    else:
        lineups = [player.lineups.get(type, [])]
    for lineup in lineups:
        for p in lineup:
            if p <= 0:
                continue
            if p == petID:
                return True
    if dispatch:
        pet = player.pets[petID]
        if pet.dispatched:
            now = int(time.time())
            if max(pet.dispatched - now, 0):
                return True
            else:
                for k, v in player.dlc_dispatch.items():
                    if petID in v.get("pets", []):
                        return True
    return False


def is_empty(position):
    return position == 0


def is_close(position):
    return position == -1


def validate_lineup(player, lineup, type):
    from config.configs import PetConfig, get_config
    configs = get_config(PetConfig)
    skip_empty = filter(lambda p: not is_empty(p), lineup)
    if not skip_empty and type != LineupType.ATK:
        return False
    distinct = set(skip_empty)
    if len(skip_empty) != len(distinct):
        logger.debug('duplicate id {} {}'.format(skip_empty, distinct))
        return False
    skip_same = set(
        [configs[player.pets[i].prototypeID].same for i in skip_empty])
    if len(skip_empty) != len(skip_same):  # 过滤相同将
        logger.debug('duplicate same {} {}'.format(skip_empty, skip_same))
        return False
    for entityID in skip_empty:
        if entityID not in player.pets:
            logger.debug(
                'entityID {} not in{}'.format(
                    entityID,
                    player.pets.keys()))
            return False
    mine_types = set([LineupType.Mine1, LineupType.Mine2])
    if type in mine_types:
        for entityID in skip_empty:
            # pet = player.pets[entityID]
            #  现在不需要限制品质
            #  info = configs[pet.prototypeID]
            #  if info.rarity < 3:
            #      return False
            for other in set(mine_types) - set([type]):
                if entityID in player.lineups.get(other, []):
                    return False
    return True


def change_lineup(player, lineup, type):
    if not validate_lineup(player, lineup, type):
        return False
    player.lineups[type] = list(lineup)
    from pvp.rob import on_mine1_change, on_mine2_change
    if type == LineupType.Mine1:
        on_mine1_change(player)
    elif type == LineupType.Mine2:
        on_mine2_change(player)
    player.save()
    return True


def is_equals(alineups, blineups):
    return alineups == blineups


def save_lineup(player, lineup, type):
    lineup = list(lineup)
    if lineup and not is_equals(lineup, player.lineups.get(type)):
        if not change_lineup(player, lineup, type):
            return False
    return True


def get_lineup_info(playerID, attrs, type=None):
    from player.model import Player
    from pet.model import Pet
    from entity.manager import g_entityManager
    if not type:
        type = LineupType.ATK
    p = g_entityManager.get_player(playerID)
    if p:
        pets = [p.pets.get(i, None) for i in p.lineups.get(type, [])]
    else:
        # p = Player.batch_load([playerID], ['lineups'])[0]  # FIXME
        p = Player.simple_load(playerID, ["entityID", "lineups"])
        p.lineups.load()
        if p:
            try:
                pets = Pet.batch_load(
                    p.lineups.get(type, []), Pet.expend_fields(attrs))
            except IndexError:
                pets = []
    result = []
    for pos, pet in enumerate(pets):
        if not pet:
            continue
        info = {n: getattr(pet, n) for n in attrs}
        if type == LineupType.Daily:
            if info.get("daily_restHP", 0):
                info["restHP"] = info["daily_restHP"]
        info['posIndex'] = pos
        info['isTeamLeader'] = (pos == 0)
        result.append(info)
    return result

get_lineup_defend_info = partial(get_lineup_info, type=LineupType.DEF)


def save_max_power_pet(p, lineup):
    print lineup
