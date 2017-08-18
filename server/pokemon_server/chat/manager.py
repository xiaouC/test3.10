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
        self.system_cache = deque(self.get_tips_messages(
            type=ChatType.System, count=3), 3)
        self.others_cache = deque([], 47)
        self.factions_cache = defaultdict(lambda: deque([], 50))
        self.groups_cache = defaultdict(lambda: deque([], 50))

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

    def send(
            self, type, content,
            name=None,
            entityID=None,
            rewards=None, local=False, **kwargs):
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
def broadcast_faction_message(m):
    msg = success_msg(msgid.RECV_MESSAGE, m)
    from entity.manager import g_entityManager
    p = g_entityManager.get_player(m.entityID)
    if not p:
        p = Player.simple_load(m.entityID, ["factionID"])
    from player.manager import g_playerManager
    from faction.model import Faction
    if p.factionID:
        g_chatManager.cache_message(m, factionID=p.factionID)
        f = Faction.simple_load(p.factionID, ["memberset"])
        if f:
            g_playerManager.broadcast(f.memberset, msg)


@proxy.rpc_batch
def broadcast_group_message(m):
    msg = success_msg(msgid.RECV_MESSAGE, m)
    from entity.manager import g_entityManager
    p = g_entityManager.get_player(m.entityID)
    if not p:
        p = Player.simple_load(m.entityID, ["groupID"])
    from player.manager import g_playerManager
    from group.model import Group
    if p.groupID:
        g_chatManager.cache_message(m, groupID=p.groupID)
        g = Group.simple_load(p.groupID, ["members"])
        g.members.load()
        if g:
            g_playerManager.broadcast(list(g.members), msg)


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


def send_news(type, func=None):
    def wrapper(func):
        def inner(*args):
            newses = get_configs_by_type(type)
            for news in newses:
                args_for_send = func(*list(args) + [news])
                if args_for_send:
                    g_chatManager.send(ChatType.Tips, *args_for_send)
        inner.__name__ = func.__name__
        inner.__doc__ = func.__doc__
        return inner
    if func:
        return wrapper(func)
    return wrapper


@send_news(NewsType.PetQualityLottery)
def on_news_pet_quality_lottery(p, rewards, news):
    rewards = filter_reward_by_type(rewards, RewardItemType.Pet)
    pets = get_config(PetConfig)
    rewards_ = []
    for reward in rewards:
        pet = pets.get(reward.arg)
        if not pet:
            continue
        if not pet.mtype and pet.rarity in news.args:
            rewards_.append(reward)
    if not rewards_:
        return
    return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.PetSpecialLottery)
def on_news_pet_special_lottery(p, rewards, news):
    rewards = filter_reward_by_type(rewards, RewardItemType.Pet)
    rewards_ = []
    for reward in rewards:
        if reward.arg in news.args:
            rewards_.append(reward)
    if not rewards_:
        return
    return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.PetQualityCompose)
def on_news_pet_quality_compose(p, rewards, news):
    rewards = filter_reward_by_type(rewards, RewardItemType.Pet)
    pets = get_config(PetConfig)
    rewards_ = []
    for reward in rewards:
        pet = pets.get(reward.arg)
        if not pet:
            continue
        if pet.rarity in news.args:
            rewards_.append(reward)
    if not rewards_:
        return
    return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.PetSpecialCompose)
def on_news_pet_special_compose(p, rewards, news):
    rewards = filter_reward_by_type(rewards, RewardItemType.Pet)
    rewards_ = []
    for reward in rewards:
        if reward.arg in news.args:
            rewards_.append(reward)
    if not rewards_:
        return
    return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.PetQualityEvolute)
def on_news_pet_quality_evolute(p, rewards, news):
    rewards = filter_reward_by_type(rewards, RewardItemType.Pet)
    pets = get_config(PetConfig)
    rewards_ = []
    for reward in rewards:
        pet = pets.get(reward.arg)
        if not pet:
            continue
        if pet.rarity in news.args:
            rewards_.append(reward)
    if not rewards_:
        return
    return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.EquipQualityLottery)
def on_news_equip_quality_lottery(p, rewards, news):
    return
    # rewards = filter_reward_by_type(rewards, RewardItemType.Equip)
    # equips = get_config(NewEquipConfig)
    # rewards_ = []
    # for reward in rewards:
    #     equip = equips.get(reward.arg)
    #     if not equip:
    #         continue
    #     if equip.quality in news.args:
    #         rewards_.append(reward)
    # if not rewards_:
    #     return
    # return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.EquipQualityCompose)
def on_news_equip_quality_compose(p, rewards, news):
    return
    # rewards = filter_reward_by_type(rewards, RewardItemType.Equip)
    # equips = get_config(EquipConfig)
    # rewards_ = []
    # for reward in rewards:
    #     equip = equips.get(reward.arg)
    #     if not equip:
    #         continue
    #     if equip.quality in news.args:
    #         rewards_.append(reward)
    # if not rewards_:
    #     return
    # return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.EquipStepAdvance)
def on_news_equip_step_advance(p, equip, news):
    return
    # rewards_ = []
    # info = get_config(EquipConfig).get(equip.prototypeID)
    # if info:
    #     ls = get_config(EquipAdvanceLimitConfig)
    #     try:
    #         l = ls[info.quality, info.type]
    #     except KeyError:
    #         return
    #     equipInfo = get_config(EquipConfig).get(equip.prototypeID)
    #     if equipInfo and equipInfo.quality in news.args:
    #         if equip.step == l.limit:
    #             reward = RewardData(
    #                 type=RewardItemType.Equip,
    #                 arg=equip.prototypeID,
    #                 count=1)
    #             reward.property = sync_property(equip)
    #             rewards_.append(reward)
    # if not rewards_:
    #     return
    # return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.PetBreaklevelBreak)
def on_news_pet_breaklevel_break(p, pet, news):
    rewards_ = []
    info = get_config(PetConfig).get(pet.prototypeID)
    if info:
        if pet.breaklevel == info.breaklv:
            reward = RewardData(
                type=RewardItemType.Pet,
                arg=pet.prototypeID,
                count=1)
            reward.property = sync_property(pet)
            rewards_.append(reward)
    if not rewards_:
        return
    return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.PvpFirst)
def on_news_pvp_first(p, news):
    return news.desc, p.name, p.entityID,


@send_news(NewsType.FoundFriendfb)
def on_found_friendfb(p, fbID, news):
    info = get_config(FriendfbConfig)[fbID]
    return news.desc % info.name, p.name, p.entityID


@send_news(NewsType.Wish)
def on_wish(p, rewards, news):
    rewards = build_reward(rewards)
    return news.desc, p.name, p.entityID, rewards


@send_news(NewsType.PetCompose)
def on_pet_compose(p, rewards, news):
    rewards = filter_reward_by_type(rewards, RewardItemType.Pet)
    rewards_ = []
    for reward in rewards:
        pet = reward.arg
        if pet in news.args:
            rewards_.append(reward)
    if not rewards_:
        return
    return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.EquipCompose)
def on_equip_compose(p, rewards, news):
    return
    # rewards = filter_reward_by_type(rewards, RewardItemType.Equip)
    # equips = get_config(EquipConfig)
    # rewards_ = []
    # for reward in rewards:
    #     equip = equips.get(reward.arg)
    #     if not equip:
    #         continue
    #     if equip.quality in news.args:
    #         rewards_.append(reward)
    # if not rewards_:
    #     return
    # return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.SparPet)
def on_pet_spar(p, rewards, news):
    rewards = filter_reward_by_type(rewards, RewardItemType.Pet)
    rewards_ = []
    for reward in rewards:
        pet = reward.arg
        if pet in news.args:
            rewards_.append(reward)
    if not rewards_:
        return
    return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.SparEquip)
def on_equip_spar(p, rewards, news):
    return
    # rewards = filter_reward_by_type(rewards, RewardItemType.Equip)
    # equips = get_config(EquipConfig)
    # rewards_ = []
    # for reward in rewards:
    #     equip = equips.get(reward.arg)
    #     if not equip:
    #         continue
    #     if equip.quality in news.args:
    #         rewards_.append(reward)
    # if not rewards_:
    #     return
    # return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.Visit)
def on_visit(p, rewards, news):
    rewards = filter_reward_by_type(rewards, RewardItemType.Pet)
    rewards_ = []
    for reward in rewards:
        pet = reward.arg
        if pet in news.args:
            rewards_.append(reward)
    if not rewards_:
        return
    desc = news.desc % getattr(
        rewards[0].property, "breaklevel", 1)
    return desc, p.name, p.entityID, rewards_


@send_news(NewsType.PetExchange1)
def on_pet_exchange1(p, pets, news):
    rewards_ = []
    for pet in pets:
        if pet.prototypeID in news.args:
            reward = RewardData(
                type=RewardItemType.Pet,
                arg=pet.prototypeID,
                count=1)
            reward.property = sync_property(pet)
            rewards_.append(reward)
    if not rewards_:
        return
    return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.PetExchange2)
def on_pet_exchange2(p, pets, news):
    rewards_ = []
    for pet in pets:
        if pet.prototypeID in news.args:
            reward = RewardData(
                type=RewardItemType.Pet,
                arg=pet.prototypeID,
                count=1)
            reward.property = sync_property(pet)
            rewards_.append(reward)
    if not rewards_:
        return
    return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.PetExchange3)
def on_pet_exchange3(p, pets, news):
    rewards_ = []
    for pet in pets:
        if pet.prototypeID in news.args:
            reward = RewardData(
                type=RewardItemType.Pet,
                arg=pet.prototypeID,
                count=1)
            reward.property = sync_property(pet)
            rewards_.append(reward)
    if not rewards_:
        return
    return news.desc, p.name, p.entityID, rewards_


@send_news(NewsType.PetExchange4)
def on_pet_exchange4(p, pets, news):
    rewards_ = []
    for pet in pets:
        if pet.prototypeID in news.args:
            reward = RewardData(
                type=RewardItemType.Pet,
                arg=pet.prototypeID,
                count=1)
            reward.property = sync_property(pet)
            rewards_.append(reward)
    if not rewards_:
        return
    return news.desc, p.name, p.entityID, rewards_
