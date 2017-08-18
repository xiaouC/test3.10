# coding:utf-8
import logging
logger = logging.getLogger("tap")
from yy.utils import guess
from yy.utils import weighted_random3
from yy.utils import weighted_random2

from config.configs import get_config
from config.configs import TapLoopConfig
from config.configs import TapMonsterConfig
from config.configs import get_cons_value

from reward.manager import open_reward, RewardType

HURT_NORM = 1
HURT_CRIT = 10


def next_monster(p):
    rest_prob = 100
    monsters = get_config(TapMonsterConfig)
    rushers = []
    for k, v in monsters.items():
        if v.prob:
            rushers.append([k, v.prob])
            rest_prob -= v.prob
    rushers.append([None, rest_prob])
    rusher = weighted_random2(rushers)
    if rusher:
        # 乱入
        p.tap_monster = rusher
    else:
        loops = get_config(TapLoopConfig)
        # 取当前循环到的关卡
        loop = loops[p.tap_loop_count % len(loops) + 1]
        p.tap_monster = weighted_random3(loop.monsters, loop.probs)
        p.tap_loop_count += 1
    p.tap_hurts_index = 0
    monster = monsters[p.tap_monster]
    p.tap_hurts = get_hurts(monster)
    return monster


def get_hurts(monster):
    prob = get_cons_value("TapCritProb") / float(100)
    hurts = []
    while sum(hurts) < monster.hp:
        if guess(prob):
            hurts.append(HURT_CRIT)
        else:
            hurts.append(HURT_NORM)
    return hurts


def start_tap(p):
    if p.tap_hurts:
        return
    next_monster(p)
    p.save()
    p.sync()


def end_tap(p, count):
    if p.tap_rest_count < count:
        return False
    hurts = p.tap_hurts[:p.tap_hurts_index + count]
    monster = get_config(TapMonsterConfig).get(p.tap_monster)
    if sum(hurts) < monster.hp:
        return False
    reward = open_reward(RewardType.Tap, monster.drop)
    result = reward.apply(p)
    p.tap_hurts_index = 0
    p.tap_rest_count -= count
    p.tap_hurts = []
    p.save()
    p.sync()
    return result


def save_tap(p, count):
    if p.tap_rest_count < count:
        return False
    assert p.tap_hurts_index + count < len(p.tap_hurts), \
        "tap_hurts_index %d, count %d" % (p.tap_rest_count, count)
    p.tap_hurts_index += count
    p.tap_rest_count -= count
    p.save()
    p.sync()
    return True


def onekey_tap(p):
    drops = []
    counting = 0
    while p.tap_rest_count:
        # 杀死当前怪需要多少次点击
        need = len(p.tap_hurts[p.tap_hurts_index:])
        counting += need
        logger.debug("tap rest count %r", p.tap_rest_count)
        logger.debug("need tap %r", need)
        if p.tap_rest_count >= need:  # kill
            count = need
            monster = get_config(TapMonsterConfig)[p.tap_monster]
            drops.append(monster.drop)
            next_monster(p)
            logger.debug("kill monster")
        else:
            count = p.tap_rest_count
            p.tap_hurts_index += count
        logger.debug("hit monster %r times", count)
        p.tap_rest_count -= count
        logger.debug("tap rest count %r", p.tap_rest_count)
        logger.debug("tap hurts index %r", p.tap_hurts_index)
    reward = open_reward(RewardType.Tap, *drops)
    result = reward.apply(p)
    p.save()
    p.sync()
    return result, counting
