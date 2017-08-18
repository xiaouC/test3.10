# coding:utf-8
import logging
logger = logging.getLogger("explore")

from config.configs import get_config
from config.configs import TreasureTypeConfig
from config.configs import TreasureConfig
from config.configs import TreasureByTypeConfig

from .constants import TreasureType
from yy.utils import choice_one
from yy.utils import weighted_random3
from protocol import poem_pb
from protocol.poem_pb import TreasureGrid


def refresh_treasure(p):
    p.treasure_refresh_count += 1
    count = p.treasure_refresh_count % 3 or 3
    prob = get_config(TreasureTypeConfig)[count]
    probs = [prob.gold, prob.silver, prob.copper]
    types = [TreasureType.Gold, TreasureType.Silver, TreasureType.Copper]
    p.treasure_type = weighted_random3(types, probs)
    p.treasure_cache = []
    p.save()
    p.sync()


EmptyGrid = [0, None, None]


def enter_treasure(p):
    rsp = poem_pb.EnterTreasure()
    if p.treasure_cache:
        grids = p.treasure_cache
    else:
        used = set()
        pending = []
        grids = [EmptyGrid] * 25
        treasure = choice_one(
            get_config(TreasureByTypeConfig)[p.treasure_type])
        logger.debug("treasure.id %r", treasure.id)
        treasure = get_config(TreasureConfig)[treasure.id]
        for type, subtype, count, pos_or_times in treasure.data:
            if pos_or_times > 0:
                # pos_or_times means position
                pos = pos_or_times - 1
                grids[pos] = [type, subtype, count]
                used.add(pos)
            else:
                # pos_or_times means appear times
                # 零算一次
                times = abs(pos_or_times or 1)
                for i in range(times):
                    pending.append([type, subtype, count])
        rest = list(set(range(0, 25)).difference(used))
        for index, each in enumerate(pending):
            want = choice_one(rest)
            if not want:
                break
            pos = rest.pop(rest.index(want))
            grids[pos] = pending[index]
        p.treasure_cache = grids
    for type, subtype, count in grids:
        data = {"type": type}
        if type == TreasureGrid.TreasureGridTypeChest:
            data["chest"] = p.treasure_type
        elif type == TreasureGrid.TreasureGridTypeMonster:
            data["monster"] = subtype
        elif type == TreasureGrid.TreasureGridTypeBuff:
            data["buff"] = subtype
        elif type == TreasureGrid.TreasureGridTypeReward:
            data["reward"] = poem_pb.RewardData(
                type=subtype, count=count)
        rsp.grids.add(**data)
    p.save()
    return rsp
