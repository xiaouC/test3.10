# coding:utf-8
'''
>>> from yy.utils import load_settings
>>> load_settings()
>>> import settings
>>> from test.mockup import c_Player as PlayerBase
>>> from yy.config.cache import load_config
>>> from config.configs import get_registereds
>>> load_config(get_registereds())

>>> #Not enough attr 货币不足的情况
>>> reward = open_reward(RewardType.Test, 2001)
>>> player = PlayerBase()
>>> player.money = 100
>>> player.gold  = 100
>>> player.exp   = 0
>>> player.gp   = 0
>>> reward.cost_after(player, gold=50, money=101)
Traceback (most recent call last):
    ...
AttrNotEnoughError: Not enough `money`
>>> reward.apply(player)
Traceback (most recent call last):
    ...
AttrNotEnoughError: Not enough `money`
>>> player.exp
0
>>> #
>>> #Success 成功的例子
>>> reward = open_reward(RewardType.Test, 2001)
>>> player = PlayerBase()
>>> player.money = 100
>>> player.gold  = 100
>>> player.exp   = 400
>>> player.gp   = 0
>>> reward.cost_after(player, gold=50, money=50)
{'money': 50, 'gold': 50}
>>> reward.apply(player)
{'exp': 100}
>>> print player.money, player.gold, player.exp, player.level
50 50 76 2
>>> #
>>> #
>>> reward = open_reward(RewardType.Test, 2001)
>>> player = PlayerBase()
>>> player.money = 100
>>> player.gold  = 100
>>> player.exp   = 0
>>> player.gp   = 0
>>> reward.cost_after(player, gold=50, money=50)
{'money': 50, 'gold': 50}
>>> player.money = 0 #临时扣除
>>> reward.apply(player)
Traceback (most recent call last):
    ...
AttrNotEnoughError: Not enough `money`
>>> player.exp
0
>>> #
>>> #
>>> #apply after 消耗和奖励分开
>>> reward = open_reward(RewardType.Test, 2001)
>>> player = PlayerBase()
>>> player.money = 100
>>> player.gold  = 100
>>> player.exp   = 0
>>> player.gp   = 0
>>> reward.cost_after(player, money=50, gold=50)
{'money': 50, 'gold': 50}
>>> reward.cost()#消耗
>>> r = reward.apply_after()
>>> print r
{'exp': 100}
>>> apply_reward(player, r)#奖励
{'exp': 100}
>>> print player.money, player.gold, player.exp
50 50 100
>>> #
>>> #直接调用apply_reward
>>> player = PlayerBase()
>>> player.money = 100
>>> player.gold  = 100
>>> player.exp   = 0
>>> player.gp   = 0
>>> apply_reward(player, {"gold":30, "exp":10, "gp":10}, cost={"money":30}, type=RewardType.Test)  # NOQA
{'gold': 30, 'exp': 10, 'gp': 10}
>>> print player.money, player.gold, player.exp, player.gp
70 130 10 10
'''

from base import *  # NOQA
from errors import *  # NOQA
from constants import *  # NOQA


def open_reward(type, *args, **kwargs):
    reward = Reward(type)
    reward.handle(*args, **kwargs)
    return reward


def parse_reward_msg(rsp):
    return parse_reward(rsp.rewards)


def build_reward_msg(rsp, reward):
    # 还没有物品,增加物品到rsp中
    rsp.rewards = build_reward(reward)


def compare_reward(reward1, reward2):
    for k, v in reward1.items():
        if isinstance(v, (int, long)):
            if v > reward2.get(k, 0):
                return False
        elif isinstance(v, (list, tuple)):
            d1 = dict(v)
            d2 = dict(reward2.get(k, []))
            for kk, vv in d1.items():
                if vv > d2.get(kk, 0):
                    return False
        else:
            raise NotImplementedError
    return True


def givegoldmail(player):
    import time
    from config.configs import get_config, GiveGoldConfig
    from mail.manager import send_mail
    config = get_config(GiveGoldConfig)[0]
    now = int(time.time())
    if config.start <= now and now < config.end:
        if config.rewards:
            send_mail(
                player.entityID,
                config.title,
                config.desc,
                addition=parse_reward(config.rewards))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
