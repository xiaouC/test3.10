# coding:utf-8
import time
from collections import deque
from collections import defaultdict

from yy.message.header import success_msg
from yy.utils import weighted_random2_multi

from protocol.poem_pb import Message
from protocol.poem_pb import RewardData
from protocol import poem_pb as msgid

from config.configs import get_config
from config.configs import PetConfig
from config.configs import TipsConfig
from config.configs import NewsConfig
from config.configs import NewEquipConfig
from config.configs import FriendfbConfig
from config.configs import NewsByTypeConfig
from config.configs import EquipAdvanceLimitConfig

from player.model import Player

from reward.constants import RewardItemType
from reward.manager import build_reward


from entity.utils import sync_property
# from itertools import chain
from .constants import ChatType, NewsType
from gm.proxy import proxy


class ChatManager(object):

    def __init__(self):
        self.system_cache = deque(self.get_tips_messages(type=ChatType.System, count=3), 3)
        self.others_cache = deque([], 47)

        self.rate_limited = {}

    def check_limited(self, key):
        if len(self.rate_limited) >= 500:  # 防止数据过多
            self.rate_limited.clear()
        ts, count = self.rate_limited.get(key, (None, 0))
        now = int(time.time())
        # 一分钟内最多说5句话
        if ts is None or (now - ts) >= 60:
            self.rate_limited[key] = (now, 1)
            return True
        elif count >= 5:
            return False
        else:
            self.rate_limited[key] = (ts, count + 1)
            return True

    def send(self, type, content, name=None, entityID=None, rewards=None, local=False, **kwargs):
        m = Message(type=type, content=content, **kwargs)
        if name is not None:
            m.name = name
        if entityID is not None:
            m.entityID = entityID
        prototypeID = kwargs.get("prototypeID")
        if prototypeID is not None:
            m.prototypeID = prototypeID
        is_faction_leader = kwargs.get("is_faction_leader")
        if is_faction_leader is not None:
            m.is_faction_leader = is_faction_leader
        if rewards is not None:
            m.rewards = rewards
        if m.type == ChatType.Faction:
            if local:
                broadcast_faction_message(m)
            else:
                proxy.broadcast_faction_message(m)
        elif m.type == ChatType.Group:
            if local:
                broadcast_group_message(m)
            else:
                proxy.broadcast_group_message(m)
        else:
            if local:
                broadcast_message(m)
            else:
                proxy.broadcast_message(m)

    def cache_message(self, m, factionID=None, groupID=None):
        if m.type == ChatType.System:
            self.system_cache.append(m)
        elif m.type == ChatType.Faction:
            assert factionID
            self.factions_cache[factionID].append(m)
        elif m.type == ChatType.Group:
            assert groupID
            self.groups_cache[groupID].append(m)
        else:
            self.others_cache.append(m)

    def get_cache_messages(self, type, factionID=None, groupID=None):
        if type == ChatType.System:
            return self.system_cache
        if type == ChatType.Faction:
            return self.factions_cache[factionID]
        if type == ChatType.Group:
            return self.groups_cache[groupID]
        return self.others_cache

    def get_tips_messages(self, type=ChatType.Tips, count=1):
        configs = get_config(TipsConfig)
        samples = [[i, i.weight] for i in configs.values()]
        configs = weighted_random2_multi(samples, count=count)
        result = []
        for config in configs:
            m = Message(type=type, content=config.desc)
            result.append(m)
        return result

    def clear_blocked_message(self, entityID):

        def _remove_one_cache(d, entityID):
            to_be_removed = []
            for msg in d:
                if msg.entityID == entityID:
                    to_be_removed.append(msg)
            for msg in to_be_removed:
                d.remove(msg)

        _remove_one_cache(self.system_cache, entityID)
        _remove_one_cache(self.others_cache, entityID)
        for d in self.factions_cache.values():
            _remove_one_cache(d, entityID)


g_chatManager = ChatManager()


def send_system_message(content, duration=2):
    g_chatManager.send(ChatType.System, content, duration=duration, local=True)


@proxy.rpc_batch
def broadcast_message(m):
    g_chatManager.cache_message(m)
    msg = success_msg(msgid.RECV_MESSAGE, m)
    from player.manager import g_playerManager
    g_playerManager.broadcast(g_playerManager.peers.keys(), msg)


@proxy.rpc_batch
def clear_blocked_message(entityID):
    g_chatManager.clear_blocked_message(entityID)


def get_configs_by_type(type):
    types = get_config(NewsByTypeConfig).get(type, [])
    configs = get_config(NewsConfig)
    configs_ = []
    for t in types:
        c = configs.get(t.ID)
        if c:
            configs_.append(c)
    return configs_


def filter_reward_by_type(rewards, type):
    return filter(lambda s: s.type == type, rewards)


