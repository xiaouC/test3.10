# coding:utf-8
import time
import logging
logger = logging.getLogger("mall")

from datetime import date as datedate

from config.configs import get_config
from config.configs import MallConfig
from config.configs import MallByTypeConfig
from config.configs import TriggerAfterFbConfig
from config.configs import get_cons_value
from config.configs import VipPacksConfig
from config.configs import VipPacksByGroupConfig
from config.configs import MallRefreshSequenceConfig
from config.configs import MallRefreshSequenceRewardConfig

from player.formulas import get_open_level

from collections import defaultdict

from yy.utils import guess
from yy.utils import weighted_random2

from mall.constants import MallType
from mall.constants import VipPackType
from mall.constants import VipPackDurationType
import settings


def refresh_mall(p, type):
    mall_types = get_config(MallByTypeConfig)[type]
    seq_config = get_config(MallRefreshSequenceConfig)
    seq_reward_config = get_config(MallRefreshSequenceRewardConfig)
    configs = get_config(MallConfig)
    samples = defaultdict(list)
    times = p.mall_refresh_times.get(type, 0)
    for each in mall_types:
        config = configs[each.ID]
        if p.level < config.level:
            continue
        samples[config.pos].append(
            [config.ID, config.prob])

    # 根据刷新次数替随机序列
    pos_to_group = dict([(x.pos, x.ID) for x in seq_config.values() if x.type == type])
    if times > 0:
        for pos in samples:
            if pos not in pos_to_group:
                continue
            c = seq_config[pos_to_group[pos]]
            idx = times % len(c.sequence) - 1 if times >= len(c.sequence) else times - 1
            group_idx = c.sequence[idx]
            group = getattr(c, 'group%d' % group_idx, None)
            if not group:
                continue
            seq = [(x.reward_id, x.prob) for x in seq_reward_config[group]]
            logger.debug('pos: %d, times: %d, %s to %s' % (pos, times,
                                                           samples[pos], seq))
            if not seq:
                continue
            samples[pos] = seq

    result = []
    for pos in sorted(samples.keys()):
        sample = samples[pos]
        productID = weighted_random2(sample)
        result.append(productID)
    p.malls[type] = result
    for each in mall_types:
        try:
            del p.mall_limits[each.ID]
        except KeyError:
            pass
    p.save()
    return result


def trigger_mall_by_type(p, type):
    if p.trigger_packs_flag:
        return 0
    if type == MallType.Golden:
        level = get_open_level("goldenstore")
        cd = get_cons_value("TempGoldenMallCD")
        attr = "golden"

    else:
        level = get_open_level("sliverstore")
        cd = get_cons_value("TempSilverMallCD")
        attr = "silver"
    if p.level < level:
        return 0
    if getattr(p, "mall_%s_opened" % attr):
        return 0
    now = int(time.time())
    if getattr(p, "mall_%s_open_remain" % attr) > now:
        return 0
    prob = 0
    triggers = get_config(TriggerAfterFbConfig)
    for tg in triggers:
        if getattr(p, "%s_sp" % attr, 0) >= tg.sp:
            prob = getattr(tg, "%small_prob" % attr)
        else:
            break
    if not guess(prob):
        return 0
    setattr(p, "mall_%s_open_remain" % attr, now + cd)
    setattr(p, "%s_sp" % attr, 0)
    refresh_mall(p, type)
    p.save()
    p.sync()
    return type


def trigger_mall(p, rsp):
    rsp.goldenMall = bool(trigger_mall_by_type(p, MallType.Golden))
    rsp.silverMall = bool(trigger_mall_by_type(p, MallType.Silver))


def check_open(p, type):
    # level TODO
    if type == MallType.Silver:
        if not p.mall_silver_open_remain and not p.mall_silver_opened:
            return False
    elif type == MallType.Golden:
        if not p.mall_golden_open_remain and not p.mall_golden_opened:
            return False
    elif type == MallType.Faction:
        if not p.factionID:
            return False
    return True


def distinct_pack(packID):
    configs = get_config(VipPacksConfig)
    config = configs.get(packID)
    if not config:
        return
    if config.gift_type == VipPackType.Daily:
        group = [i.ID for i in get_config(
            VipPacksByGroupConfig).get(config.gift_type, [])]
        config = configs[min(group)]
    return config


def get_vip_pack_rest_count(p, packID, today=None):
    if not today:
        today = datedate.today()
    config = distinct_pack(packID)
    if config.buy_times == -1:
        count = -1
    else:
        last, bcount = p.vip_packs_limits.get(config.ID, (0, 0))
        if config.gift_duration == VipPackDurationType.Daily:
            if last:
                if datedate.fromtimestamp(last) != today:
                    bcount = 0
    count = max(config.buy_times - bcount, 0)
    return count


def set_vip_packs_limits(p, packID, now):
    config = distinct_pack(packID)
    ts, count = p.vip_packs_limits.get(config.ID, (0, 0))
    date = datedate.fromtimestamp(ts)
    if date == datedate.fromtimestamp(now):
        count = count + 1
    else:
        count = 1
    p.vip_packs_limits[config.ID] = (now, count)


def reset_vip_packs(p):
    if not p.vip_packs_limits_reset_flag and settings.REGION["ID"] < 104:  #  5区之后的不需要
        limits = dict(p.vip_packs_limits)
        for k, v in limits.items():
            config = distinct_pack(k)
            if config:
                if config.gift_type == VipPackType.Vip:
                    del p.vip_packs_limits[k]
    p.vip_packs_limits_reset_flag = True
    p.save()


def first_recharge_patch(p):
    from mail.manager import send_mail
    if p.bought_recharges and not p.first_recharge_patch and settings.REGION["ID"] < 104:  # 5区之后的不需要
        send_mail(
            p.entityID,
            "首充礼包奖励补发",
            "亲爱的训练师:您现在可以重新领取VIP礼包!最新版首充礼包比原版礼包多出的商品请查收附件！祝您训练家旅途愉快",
            addition={
                'money': 50000,
                'petList': [
                    [1000356, 4],
                    [1000350, 4]
                ]
            }, cd=86400*30)
    p.first_recharge_patch = True
    p.save()
