# coding:utf-8
import random
from itertools import repeat
from .errors import *  # NOQA
from .constants import *  # NOQA
from config.configs import get_config
from config.configs import DroppackConfig
from config.configs import SpecpackConfig
from config.configs import PetConfig
from config.configs import HotLotteryCampaignConfig

from player.model import Player
from faction.model import Faction
from protocol.poem_pb import RewardData
from protocol.poem_pb import SyncProperty
from yy.utils import DictObject
from yy.utils import getitem
from yy.utils import weighted_random3
from yy.utils import guess
from yy.utils import weighted_random2

handlers = {}


def register_handler(type):
    def inner(fn):
        handlers[type] = fn
        return fn
    return inner


def get_register_handler(type):
    return handlers[type]


def reward_is_attr(rewardItemType):
    return check_attr(get_reward_attr_name(rewardItemType))


def get_reward_attr_name(rewardItemType):
    return AntiRewardItemTypeDict[rewardItemType]


def get_reward_attr_list():
    return filter(check_attr, RewardItemTypeDict)


def getter(obj, name, *default):
    if isinstance(obj, dict):
        return getitem(obj, name, *default)
    return getattr(obj, name, *default)


def check_if_specpack(reward):
    p = getter(reward, "property", None)
    if p:
        packID = getter(p, "entityID", None)
        if packID:
            return [packID, getter(reward, "count")]
    return []


def combine_reward(rewards1, rewards2, data=None):
    if data is None:
        data = {}
    if isinstance(rewards1, dict):
        rewards1 = build_reward(rewards1)
    else:
        rewards1 = build_reward_from_array(rewards1)
    if isinstance(rewards2, dict):
        rewards2 = build_reward(rewards2)
    else:
        rewards2 = build_reward_from_array(rewards2)
    for reward in rewards1 + rewards2:
        if getter(reward, 'type') == RewardItemType.Pet:
            specpack = check_if_specpack(reward)
            if specpack:
                data.setdefault('specPacks', []).append(specpack)
            else:
                for i in range(getter(reward, 'count')):
                    data.setdefault('petList', []).append(
                        [getter(reward, 'arg'), 1])
        elif getter(reward, 'type') == RewardItemType.Patch:  # FIXME
            data.setdefault('petPatchList', []).append(
                [getter(reward, 'arg'), getter(reward, 'count')])
        elif getter(reward, 'type') == RewardItemType.Droppack:
            pass  # Do not parse droppack
        elif getter(reward, 'type') == RewardItemType.Mat:
            data.setdefault('matList', []).append(
                [getter(reward, 'arg'), getter(reward, 'count')])
        elif getter(reward, 'type') == RewardItemType.Equip:
            specpack = check_if_specpack(reward)
            if specpack:
                data.setdefault('specPacks', []).append(specpack)
            else:
                for i in range(getter(reward, 'count')):
                    data.setdefault('equipList', []).append(
                        [getter(reward, 'arg'), 1])
        elif getter(reward, 'type') == RewardItemType.Specpack:
            data.setdefault('specPacks', []).append(
                [getter(reward, 'arg'), getter(reward, 'count')])
        elif getter(reward, 'type') == RewardItemType.Gem:
            data.setdefault('gemList', []).append(
                [getter(reward, 'arg'), getter(reward, 'count')])
        else:
            attr = get_reward_attr_name(getter(reward, 'type'))
            assert check_attr(attr), 'invalid attr %s' % attr
            data[attr] = data.setdefault(attr, 0) + getter(reward, 'count')
    return data


def parse_reward(rewards):
    return combine_reward(rewards, [])


def build_reward_from_array(reward):
    result = []
    if isinstance(reward, list):
        for r in reward:
            if isinstance(r, list):
                t, a, c = r
                result.append({"type": t, "arg": a, "count": c})
            elif isinstance(r, int):
                t, a, c = reward
                result.append({"type": t, "arg": a, "count": c})
                break
            else:
                return reward
        return result
    return reward


def build_reward(reward, cls=RewardData):
    rewards = []
    from config.configs import get_config
    packs = get_config(SpecpackConfig)
    for k, v in reward.items():
        if k == 'petList':
            for petID, count in v:
                rewards.append({
                    'type': RewardItemType.Pet,
                    'arg': petID, 'count': count,
                })
        elif k == 'petPatchList':
            from config.configs import PetConfig, get_config
            petcfg = get_config(PetConfig)
            for petID, count in v:
                if petID in petcfg.keys():
                    rewards.append({
                        'type': RewardItemType.Patch,
                        'arg': petID, 'count': count
                    })
        elif k == 'matList':
            for matID, count in v:
                rewards.append({
                    'type': RewardItemType.Mat,
                    'arg': matID, 'count': count,
                })

        elif k == 'equipList':
            for equipID, count in v:
                rewards.append({
                    'type': RewardItemType.Equip,
                    'arg': equipID, 'count': count,
                })
        elif k == 'specPacks':
            for packID, count in v:
                pack = packs[packID]
                if pack.ref_type == RewardItemType.Equip:
                    rewards.append({
                        'type': pack.ref_type,
                        'arg': pack.ref_id,
                        'count': count,
                        'property': {
                            'entityID': packID,
                            'type': SyncProperty.Equip,
                            'properties': {
                                'level': pack.e_level,
                                'step': pack.e_step,
                            }
                        }
                    })
                elif pack.ref_type == RewardItemType.Pet:
                    rewards.append({
                        'type': pack.ref_type,
                        'arg': pack.ref_id,
                        'count': count,
                        'property': {
                            'entityID': packID,
                            'type': SyncProperty.Pet,
                            'properties': {
                                'level': pack.p_level,
                                'breaklevel': pack.p_star
                            }
                        }
                    })
        elif k == 'gemList':
            for gemID, count in v:
                rewards.append({
                    'type': RewardItemType.Gem,
                    'arg': gemID, 'count': count,
                })
        else:
            assert check_attr(k), 'invalid attr %s' % k
            type = RewardItemTypeDict[k]
            rewards.append({'type': type, 'arg': 0, 'count': v})
    rewards = [cls(**i) for i in rewards]
    return rewards


def check_attr(attr):
    f = Player.fields.get(attr)
    return f and f.type == 'integer'


def check_cost_attr(role, attrs):
    for attr, value in attrs.items():
        old = getattr(role, attr)
        new = old - value
        if new < 0:
            raise AttrNotEnoughError('Not enough `%s`', attr)


def check_cost_pets(role, petList):
    pass


def check_cost_equips(role, equipList):
    pass


def check_cost_gems(role, gemList):
    for gemID, count in gemList:
        if role.gems.get(gemID, 0) < count:
            raise GemNotEnoughError('Not enough gem `{}`'.format(gemID))


def check_cost_mats(role, matList):
    for matID, count in matList:
        if role.mats.get(matID, 0) < count:
            raise MatNotEnoughError('Not enough mat `{}`'.format(matID))


def cost_pets(role, petList):
    # NOTE 要去扣除一个实例化的pet，只有配置ID是不够的
    if petList:
        assert False, 'Can not cost entity in reward'
    return True


def cost_equips(role, equipList):
    # NOTE 与pet同样的问题
    if equipList:
        assert False, 'Can not cost entity in reward'
    return True


def cost_mats(role, matList):
    check_cost_mats(role, matList)
    role.cost_mats(matList)
    return True


def cost_pats(role, petPatchList):
    assert isinstance(role, Player), 'Invalid role type'
    from pet.manager import setdefault
    for patchid, num in petPatchList:
        old = setdefault(role.petPatchs, patchid)
        if old < num:
            return False
        role.petPatchs[patchid] = old - num
        # role.set_petpatch_dirty([patchid])
    role.save()
    return True


def cost_gems(role, gemList):
    check_cost_gems(role, gemList)
    role.cost_gems(gemList)
    return True


def cost_attr(role, attrs):
    for attr, value in attrs.items():
        old = getattr(role, attr)
        new = old - value
        if new < 0:
            raise AttrNotEnoughError('Not enough `%s`', attr)
        setattr(role, attr, new)
        from campaign.manager import do_consume_campaign
        do_consume_campaign(role, RewardItemTypeDict[attr], value)


def cost(role, cost, type):
    cost_ = dict(cost)
    matList = cost.pop('matList', [])
    petList = cost.pop('petList', [])
    patList = cost.pop('petPatchList', [])
    equipList = cost.pop('equipList', [])
    gemList = cost.pop('gemList', [])

    # CHECK
    check_cost_mats(role, matList)
    check_cost_pets(role, petList)
    check_cost_equips(role, equipList)
    check_cost_gems(role, gemList)
    check_cost_attr(role, cost)

    cost_mats(role, matList)
    cost_pets(role, petList)
    cost_equips(role, equipList)
    cost_gems(role, gemList)

    if not cost_pats(role, patList):
        raise PatNotEnoughError

    # {{{cost log
    from common.log import gm_logger
    if isinstance(role, Player):
        player = role
    else:
        from entity.manager import g_entityManager
        player = g_entityManager.get_player(role.masterID)

    gm_logger.info(
        {'cost': {'entityID': player.entityID, 'data': cost_, 'type': type}})
    # }}}
    cost_attr(role, cost)
    # {{{
    from common.log import role_debit
    for prototypeID, amount in petList:
        role_debit(
            player=player, debitType=role_debit.Cost,
            itemType=type, argID=prototypeID, argAmount=amount
        )
    for matID, amount in matList:
        role_debit(
            player=player, debitType=role_debit.Cost,
            itemType=type, argID=matID, argAmount=amount
        )
    for patchid, amount in patList:
        role_debit(
            player=player, debitType=role_debit.Cost,
            itemType=type, argID=-patchid, argAmount=amount
        )
    for prototypeID, amount in equipList:
        role_debit(
            player=player, debitType=role_debit.Cost,
            itemType=type, argID=prototypeID, argAmount=amount
        )
    for prototypeID, amount in gemList:
        role_debit(
            player=player, debitType=role_debit.Cost,
            itemType=type, argID=prototypeID, argAmount=amount
        )
    for attr, amount in cost.items():
        if not check_attr(attr) or amount == 0:
            continue
        role_debit(
            player=player, debitType=role_debit.Cost,
            itemType=type, currency=RewardItemTypeDict[attr],
            amount=amount, balance=getattr(player, attr, 0),
        )
    # }}}
    return cost_

_cost = cost


def apply_reward(
        role,
        reward,
        cost=None,
        type=RewardType.Undefined,
        force=True, extra=None):
    # reward like {'gold':10, 'exp':10, 'petList':[[30000001, 1]]}
    # force 不检查限制
    reward = dict(reward or {})
    reward_ = dict(reward or {})
    petList = reward.pop('petList', [])
    matList = reward.pop('matList', [])
    patList = reward.pop('petPatchList', [])  # FIXME
    equipList = reward.pop('equipList', [])
    gemList = reward.pop('gemList', [])
    specPacks = reward.pop('specPacks', [])
    p_in_specPacks = 0
    e_in_specPacks = 0
    from config.configs import get_config
    packs = get_config(SpecpackConfig)
    for packID, count in specPacks:
        pack = packs[packID]
        if pack.ref_type == RewardItemType.Equip:
            e_in_specPacks += count
        elif pack.ref_type == RewardItemType.Pet:
            p_in_specPacks += count
    if not force:
        if petList:
            if not check_add_pets(role, len(petList) + p_in_specPacks):
                raise PetExceedError
        if matList:
            if not check_add_mats(role, len(matList)):
                raise MatExceedError
        if equipList:
            if not check_add_equips(role, len(equipList) + e_in_specPacks):
                raise EquipExceedError
        if gemList:
            if not check_add_gems(role, len(gemList)):
                raise GemExceedError
    if cost:
        _cost(role, cost, type)
    if reward_:
        add_pets(role, petList, extra=extra)
        add_mats(role, matList)
        add_pats(role, patList)  # FIXME 已经不再使用
        add_attr(role, reward)
        add_equips(role, equipList, extra=extra)
        add_specpacks(role, specPacks)
        add_gems(role, gemList)
        # {{{
        from common.log import gm_logger
        if isinstance(role, Player):
            player = role
        else:
            from entity.manager import g_entityManager
            player = g_entityManager.get_player(role.masterID)
        gm_logger.info(
            {'gain': {
                'entityID': player.entityID, 'data': reward_, 'type': type}})
        from common.log import role_debit
        for prototypeID, amount in petList:
            role_debit(
                player=player, debitType=role_debit.Gain,
                itemType=type, argID=prototypeID, argAmount=amount
            )
        for prototypeID, amount in equipList:
            role_debit(
                player=player, debitType=role_debit.Gain,
                itemType=type, argID=prototypeID, argAmount=amount
            )
        for matID, amount in matList:
            role_debit(
                player=player, debitType=role_debit.Gain,
                itemType=type, argID=matID, argAmount=amount
            )
        for gemID, amount in gemList:
            role_debit(
                player=player, debitType=role_debit.Gain,
                itemType=type, argID=gemID, argAmount=amount
            )
        for attr, amount in reward.items():
            if not check_attr(attr) or amount == 0:
                continue
            role_debit(
                player=player, debitType=role_debit.Gain,
                itemType=type, currency=RewardItemTypeDict[attr],
                amount=amount, balance=getattr(player, attr, 0),
            )
        # }}}
    role.save()
    return reward_


def add_specpacks(role, specPacks):
    from config.configs import get_config
    packs = get_config(SpecpackConfig)
    equipList = []
    petList = []
    args_for_equips = []
    args_for_pets = []
    for packID, count in specPacks:
        pack = packs[packID]
        if pack.ref_type == RewardItemType.Equip:
            equipList.append([pack.ref_id, count])
            args_for_equips.append({
                'level': pack.e_level,
                'step': pack.e_step,
            })
        elif pack.ref_type == RewardItemType.Pet:
            petList.append([pack.ref_id, count])
            petInfo = get_config(PetConfig)[pack.ref_id]
            add_star = (pack.p_star - 1) * petInfo.need_patch
            args_for_pets.append({
                'level': pack.p_level,
                'breaklevel': pack.p_star,
                'add_star': add_star
            })
    result = {}
    if equipList:
        result.update(add_equips(role, equipList, args=args_for_equips))
    if petList:
        result.update(add_pets(role, petList, args=args_for_pets))
    return result


def add_pets(role, petList, args=None, extra=None):
    from player.model import Player
    assert isinstance(role, Player), 'Invalid role type'
    infos = []
    # range(count) 可以忽略count为负数的情况
    if not args:
        for p, count in petList:
            for i in range(count):
                infos.append({"prototypeID": p})
    else:
        assert len(petList) == len(args), "Not enough args for list"
        for index, (p, count) in enumerate(petList):
            for i in range(count):
                info = {"prototypeID": p}
                info.update(args[index])
                infos.append(info)
    ranking_pet_count = 0
    for info in infos:
        petInfo = get_config(PetConfig).get(
            info["prototypeID"])
        if not petInfo:
            continue
        if petInfo.cls >= 3:
            ranking_pet_count += 1
    pets = role.add_pets(*infos)
    if extra is not None:
        extra["pets"] = pets
    result = [[p.prototypeID, 1] for p in pets]
    role.ranking_pet_count += ranking_pet_count
    from task.manager import on_best_pet
    on_best_pet(role, pets)
    return {'petList': result}


def add_equips(role, equipList, args=None, extra=None):
    from player.model import Player
    assert isinstance(role, Player), 'Invalid role type'
    infos = []
    # range(count) 可以忽略count为负数的情况
    if not args:
        for e, count in equipList:
            for i in range(count):
                infos.append({"prototypeID": e})
    else:
        assert len(equipList) == len(args), "Not enough args for list"
        for index, (e, count) in enumerate(equipList):
            for i in range(count):
                info = {"prototypeID": e}
                info.update(args[index])
                infos.append(info)
    equips = role.add_equips(*infos)
    if extra is not None:
        extra["equips"] = equips
    result = [[e.prototypeID, 1] for e in equips]
    from task.manager import on_collect_equip
    on_collect_equip(role, equips)
    return {'equipList': result}


def add_mats(role, matList):
    from player.model import Player
    assert isinstance(role, Player), 'Invalid role type'
    role.add_mats(matList)
    return {'matList': matList}

# FIXME


def add_pats(role, petPatchList):
    from player.model import Player
    from pet.manager import setdefault
    assert isinstance(role, Player), 'Invalid role type'
    result = {}
    for p, count in petPatchList:
        result[p] = count
        old = setdefault(role.petPatchs, p)
        role.petPatchs[p] = old + count
        # role.set_petpatch_dirty([p])
    return {'petPatchList': list(result.items())}


def add_gems(role, gemList):
    from player.model import Player
    assert isinstance(role, Player), 'Invalid role type'
    role.add_gems(gemList)
    return {'gemList': gemList}


def add_attr(role, attrs):
    adds = {}
    for attr, value in attrs.items():
        assert value >= 0
        if attr == 'exp':
            set_exp(role, value)
        else:
            old = getattr(role, attr)
            new = old + value
            setattr(role, attr, new)
        if attr == 'totalfp':
            role.todayfp_task += value
            if role.factionID:
                Faction.incr_attribute(
                    role.factionID, 'totalfp', value)
        if attr == 'money':
            from task.manager import on_money
            on_money(role, value)
        elif attr == "gold":
            from task.manager import on_gold
            on_gold(role, value)
        elif attr == "soul":
            from task.manager import on_soul
            on_soul(role, value)
        adds[attr] = value
    return adds


def calcExpOfLv(cexp, currLv):
    if currLv <= 1:
        return 0
    else:
        __exp = int(math.pow(currLv + 1, 3) * cexp * 0.0099 + 0.5)
        return __exp


def levelup(role):
    from config.configs import LevelupConfig, get_config
    if isinstance(role, Player):
        # 升级对象为玩家时
        configs = get_config(LevelupConfig)
        maxLevel = len(configs)
        nxtLevel = role.level + 1
        if nxtLevel > maxLevel:
            return False
        next = configs[nxtLevel]
        if role.exp >= next.exp:
            role.level = nxtLevel
            role.exp -= next.exp
            role.spmax += next.add_spmax
            # role.power += next.add_power
            role.sp += next.add_sp
            from player.formulas import get_level_value
            if get_level_value(role.level, "count_down"):
                from campaign.manager import start_count_down
                start_count_down(role)
            levelup(role)
            return True
    elif isinstance(role, Pet):
        # 升级对象为怪物时
        from pet.service import calcExpOfLv
        from config.configs import PetConfig, get_config
        item = get_config(PetConfig)[role.prototypeID]
        cexp = item.cexp
        level = role.level
        rqexp = calcExpOfLv(cexp,
                            level + 1) - calcExpOfLv(cexp,
                                                     level)  # 升级所需经验值
        if role.level == item.lvMax:
            # 怪物已达最大等级
            return False
        if role.exp >= rqexp:
            # 怪物当前经验大于等于升级所需经验
            role.level += 1
            role.exp = role.exp - rqexp
            levelup(role)
            return True
        else:
            return False


def set_exp(role, exp):
    '''增加经验，如果可以升级，设置等级'''
    # 试用账户有升级上限
    if isinstance(role, Player) and role.lock_level > 0 and role.level >= role.lock_level:
        from player.manager import g_playerManager
        from yy.message.header import fail_msg
        g_playerManager.sendto(role.entityID, fail_msg(0, reason='该帐号为体验帐号，只能在注册时使用的设备上登录！体验帐号等级上限为%s级，使用正常帐号登录可体验完整的游戏内容！再次感谢您的配合！' % role.lock_level))
        return False
    role.exp += exp
    rs = levelup(role)
    if rs:
        if isinstance(role, Player):
            from task.manager import on_levelup, on_login
            on_levelup(role)
            on_login(role)
            from pvp.rob import on_mine_change, check_rob
            on_mine_change(role)
            check_rob(role)
            from entity.manager import check_level_packs
            check_level_packs(role)
            from player.model import PlayerLevelRanking
            PlayerLevelRanking.update_score(role.entityID, role.level)
            from friend.manager import recommendp
            recommendp(role)
            from campaign.manager import reset_online_packs
            reset_online_packs(role)
            from explore.ambition import reload_ambition
            reload_ambition(role)
    return rs


def add_pack(
        pack,
        obj,
        itemID=None,
        matID=None,
        skillk=None,
        skip_pet=False,
        **kwargs):
    if not itemID:
        itemID = pack.itemID
    if skillk:
        attr = get_reward_attr_name(pack.type)
        amount = int(pack.amount * skillk.get(attr, 1))
    else:
        amount = pack.amount
    if pack.type == RewardItemType.Pet:
        if not skip_pet:
            petList = [[itemID, 1] for i in range(amount)]
            obj.petList.extend(petList)
            obj.computedDropPacks.setdefault('petList', []).extend(petList)
    elif pack.type == RewardItemType.Patch:  # FIXME
        assert False, '道具取代了碎片，请添加道具 {}'.format(pack)
        patchs = [itemID, amount]
        obj.petPatchList.append(patchs)
        obj.computedDropPacks.setdefault('petPatchList', []).append(patchs)
    elif pack.type == RewardItemType.Droppack:
        compute(pack.itemID, obj, **kwargs)
    elif pack.type == RewardItemType.Mat:
        if not matID:
            matID = pack.itemID
        matList = [[matID, pack.amount]]
        obj.matList.extend(matList)
        obj.computedDropPacks.setdefault('matList', []).extend(matList)
    elif pack.type == RewardItemType.Equip:
        equipList = [[pack.itemID, 1] for i in range(amount)]
        obj.equipList.extend(equipList)
        obj.computedDropPacks.setdefault('equipList', []).extend(equipList)
    elif pack.type == RewardItemType.Specpack:
        specPacks = [[pack.itemID, 1] for i in range(amount)]
        obj.specPacks.extend(specPacks)
        obj.computedDropPacks.setdefault('specPacks', []).extend(specPacks)
    elif pack.type == RewardItemType.Gem:
        gemList = [[pack.itemID, 1] for i in range(amount)]
        obj.gemList.extend(gemList)
        obj.computedDropPacks.setdefault('gemList', []).extend(gemList)
    else:
        attr = get_reward_attr_name(pack.type)
        assert check_attr(attr), 'invalid attr %s' % attr
        obj.attrReward[attr] = obj.attrReward.setdefault(attr, 0) + amount
        obj.computedDropPacks[attr] = obj.computedDropPacks.setdefault(
            attr,
            0) + amount

BASENUMBER = 10000


def compute(drop, obj, **kargs):
    configs = get_config(DroppackConfig)
    packs = configs[drop]
    if not packs:
        return
    weight_packs = []
    independent_packs = []
    remain_packs = []
    for pack in packs:
        if pack.randomtype == RandomType.Weight:
            weight_packs.append(pack)
        else:
            independent_packs.append(pack)
    for pack in independent_packs:
        prob = pack.dropProb / float(BASENUMBER)
        if guess(prob):
            remain_packs.append(pack)
    if weight_packs:
        dropProbs = [i.dropProb for i in weight_packs]
        weighted = weighted_random3(
            weight_packs + [None],
            dropProbs + [BASENUMBER - sum(dropProbs)]
        )
        if weighted:
            remain_packs.append(weighted)
    for pack in remain_packs:
        add_pack(pack, obj, **kargs)
    return


class Reward(object):

    def __init__(self, type):
        self.type = type
        self.attrReward = DictObject()
        self.matList = []
        self.petList = []
        self.equipList = []
        self.dropPacks = []
        self.petPatchList = []  # FIXME
        self.specPacks = []
        self.gemList = []

        self.computedDropPacks = DictObject()
        self.need_cost = False
        self.applied = False
        self.base_rewards = {}

    def add(self, rewards):
        combine_reward(rewards, [], data=self.base_rewards)

    @property
    def reward(self):
        d = self.base_rewards
        if self.matList:
            d['matList'] = list(self.matList)
        if self.petList:
            d['petList'] = list(self.petList)
        if self.equipList:
            d["equipList"] = list(self.equipList)
        if self.petPatchList:
            d['petPatchList'] = list(self.petPatchList)  # FIXME
        if self.specPacks:
            d['specPacks'] = list(self.specPacks)
        if self.gemList:
            d['gemList'] = list(self.gemList)
        if self.attrReward:
            d.update(dict(self.attrReward))
        return d

    def cost_after(self, payer, **costs):
        # apply时才真正从payer身上扣除
        assert isinstance(payer, Player), "payer must be Player"
        if costs:
            self.need_cost = True
            self.payer = payer
            self.costs = costs
            # do check
            costs_ = dict(costs)
            check_cost_pets(payer, costs_.pop('petList', []))
            check_cost_mats(payer, costs_.pop('matList', []))
            check_cost_gems(payer, costs_.pop('gemList', []))
            check_cost_attr(payer, costs_)
        return costs

    def cost(self):
        # 真正的从payer身上扣除
        assert self.need_cost, 'Not need cost, or costed already.'
        cost(self.payer, self.costs, self.type)
        self.need_cost = False

    def apply_after(self):
        # 返回一个reward字典, 并不真正添加reward
        # compute TODO
        return self.reward

    def apply(self, role, force=True, extra=None):
        assert not self.applied, 'Already applied.'
        if self.need_cost:
            cost = self.costs
        else:
            cost = None
        data = apply_reward(
            role, self.reward, cost, self.type, force=True, extra=extra)
        self.applied = True
        return data

    def compute_droppacks(self):
        for packID, count in self.dropPacks:
            for i in range(count):
                compute(packID, self)

    def clean_compute_droppacks(self):
        self.computedDropPacks = DictObject()

    def handle(self, *args, **kwargs):
        handler = get_register_handler(self.type)
        if not handler:
            raise NotImplementedError('Not registered handler')
        reward = handler(self, *args, **kwargs)
        # compute droppacks
        self.compute_droppacks()
        return reward


@register_handler(RewardType.Test)
def testHandler(reward, fbID):
    reward.attrReward.exp = 100
    # reward.dropPacks = [[1001, 1]]
    return reward


@register_handler(RewardType.FB)
def fbHandler(reward, player, fbID, isfirst, rsp):
    from config.configs import FbInfoConfig
    from config.configs import SceneInfoConfig
    from config.configs import RandomMonsterConfig
    from config.configs import PetConfig
    from config.configs import FbDropConfig
    from scene.manager import get_monster_groups
    from scene.constants import FbType
    from campaign.manager import g_campaignManager
    monsters = get_monster_groups(fbID)
    sumsoul = 0
    summoney = 0
    petinfos = get_config(PetConfig)
    randomms = get_config(RandomMonsterConfig)
    config = get_config(FbInfoConfig)[fbID]
    scene = get_config(SceneInfoConfig)[config.sceneID]
    rewards = {}
    drop_fields = (
        'itemfirst_id',
        'itemdrops_id',
        'exp_reward',
        'monster_drop',
        'gold_reward')
    for i in drop_fields:
        rewards[i] = getattr(config, i)
    # 怪物掉落
    droped_pets_count = 0  # 已经掉落葫芦数
    layer_count = len(monsters.items())

    mulriple = 1  # 倍数
    if g_campaignManager.fb_drop_campaign.is_open():
        cfg = g_campaignManager.fb_drop_campaign.get_current()
        kind = (scene.type, scene.subtype)
        flag = g_campaignManager.fb_drop_campaign.kind.get(kind, None)
        if flag and flag & cfg.group > 0:
            mulriple = cfg.reward_group

    for layer, group in monsters.items():
        monster_count = len(group)
        for monsterindex, (monsterlevel, monsterID) in group.items():
            if monsterID < 0:  # 负数代表需要随机
                sample = randomms[monsterID]
                monsterID = weighted_random3(
                    sample.monsters + [None],
                    sample.weights + [BASENUMBER - sum(sample.weights)]
                )
                if not monsterID:  # 可能不出现
                    continue
                rsp.replaces.append(monsterID)
            monster = petinfos[monsterID]
            drop = rsp.drops.add(index=monsterindex, layer=layer)
            # 必掉
            # 金币 = sqrt(level)*coinUp/4+50
            # 水晶 = sqrt(level)*expUp/7+30
            money = monster.coinUp
            soul = monster.expUp
            # money = int(
            #     math.sqrt(monsterlevel) * monster.coinUp / float(4) + 50)
            # soul = int(
            #     math.sqrt(monsterlevel) * monster.expUp / float(7) + 30)
            drop.must.add(type=RewardItemType.Money, count=money)
            drop.must.add(type=RewardItemType.Soul, count=soul)
            summoney += money
            sumsoul += soul

            # boss
            if layer == layer_count and monsterindex == monster_count:
                alter_flag = False
                if isfirst:
                    droppack = 0
                else:
                    droppack = config.boss_drop
            else:
                if monster.dtype == 0:
                    # 从关卡配置中读取怪物掉落
                    droppack = rewards['monster_drop']
                else:
                    # 从怪物表本身读取怪物掉落
                    droppack = monster.droppack
                alter_flag = True
            # 可能掉
            # print monster.name
            # print 'dtype', monster.dtype
            # print 'droppack', droppack
            if droppack:
                pets = zip(
                    filter(
                        lambda s: s, [
                            monster.drop1, monster.drop2, monster.drop3]), [
                        monster.num1, monster.num2, monster.num3])
                if alter_flag:
                    if pets:
                        petID = weighted_random2(pets)
                    else:
                        petID = None
                    matID = monster.drop_piece
                else:
                    petID = None
                    matID = None
                if droped_pets_count >= 4:  # 留一个位置给最后一波
                    if layer == layer_count:
                        skip_pet = (droped_pets_count >= 10)
                    else:
                        skip_pet = True
                else:
                    skip_pet = False  # not petID
                compute(
                    droppack,
                    reward,
                    itemID=petID,
                    matID=matID,
                    skip_pet=skip_pet)
                if reward.computedDropPacks:
                    # 多倍掉落
                    if mulriple > 1:
                        for k, v in reward.computedDropPacks.items():
                            if isinstance(v, int):
                                reward.computedDropPacks[k] = v * mulriple
                                reward.attrReward[k] = v * mulriple
                            elif isinstance(v, (list, tuple)):
                                # computedDropPacks 并不是最终给的，所以要应用到 reward 上
                                reward.computedDropPacks[k] = [[item, count * mulriple] for (item, count) in v]
                                items = getattr(reward, k)
                                for (item, count) in reward.computedDropPacks[k]:
                                    for repl in items:
                                        if repl[0] == item:
                                            repl[1] += (mulriple - 1)
                    drop.maybe = build_reward(reward.computedDropPacks)
                    for m in drop.maybe:
                        if m.type in (
                                RewardItemType.Pet,
                                RewardItemType.Mat,
                                RewardItemType.Equip):
                            droped_pets_count += 1
                    reward.clean_compute_droppacks()
    if summoney:
        reward.attrReward['money'] = reward.attrReward.setdefault(
            'money',
            0) + summoney
    # reward.attrReward['exp'] = reward.attrReward.setdefault('exp', 0)
    if sumsoul:
        reward.attrReward['soul'] = reward.attrReward.setdefault(
            'soul',
            0) + sumsoul
    fb_exp = int(rewards['exp_reward'])
    if fb_exp:
        reward.attrReward['exp'] = reward.attrReward.setdefault(
            'exp', 0) + fb_exp
        rsp.rewards.add(type=RewardItemType.EXP, count=fb_exp)
    fb_gold = int(rewards['gold_reward'])
    if g_campaignManager.gold_campaign.is_open() and fb_gold:
        reward.attrReward['gold'] = reward.attrReward.setdefault(
            'gold', 0) + fb_gold
        rsp.rewards.add(type=RewardItemType.Gold, count=fb_gold)
    campaign_drop = 0
    if config.type == FbType.Normal:
        if g_campaignManager.normal_fb_campaign.is_open():
            current = g_campaignManager.normal_fb_campaign.get_current()
            if current:
                campaign_drop = current.group
    elif config.type == FbType.Advanced:
            current = g_campaignManager.advanced_fb_campaign.get_current()
            if current:
                campaign_drop = current.group
    if campaign_drop:
        compute(campaign_drop, reward)
        for each in build_reward(reward.computedDropPacks, cls=dict):
            rsp.rewards.add(**each)
        reward.clean_compute_droppacks()
    # 关卡奖励
    if isfirst:  # 首通关卡
        reward.clean_compute_droppacks()
        # # 场景首通
        # if all(
        #         map(lambda s: s in player.fbscores or s == fbID, scene.fbs)):
        #     # 是否该场景全通
        #     if scene.drop:
        #         compute(scene.drop, reward)
        #     rsp.first = build_reward(reward.computedDropPacks)
        if rewards['itemfirst_id']:  # 关卡首通
            compute(rewards['itemfirst_id'], reward)
    else:
        if rewards['itemdrops_id']:
            # 多倍掉落
            reward.dropPacks = [[rewards['itemdrops_id'], mulriple]]
    # 假概率掉落
    config = get_config(FbDropConfig).get(fbID)
    if config:
        totalCount = player.fbscores.get(fbID, {}).get("totalCount", 0)
        index = totalCount % len(config.probs)
        prob = config.probs[index]
        if guess(prob):
            # 多倍掉落
            reward.dropPacks.append([config.drop, mulriple])
    return reward


@register_handler(RewardType.Lottery)
def lotteryHandler(reward, rsp, dropID, count):
    configs = get_config(DroppackConfig)
    packs = configs[dropID]
    weight_packs = []
    independent_packs = []
    remain_packs = []
    if count <= len(packs):
        random.shuffle(packs)
        packs = packs[:count]
    for pack in packs:
        if pack.randomtype == RandomType.Weight:
            weight_packs.append(pack)
        else:
            independent_packs.append(pack)
    for pack in independent_packs:
        prob = pack.dropProb / float(BASENUMBER)
        if guess(prob):
            remain_packs.append(pack)
    if weight_packs:
        dropProbs = [i.dropProb for i in weight_packs]
        weighted = weighted_random3(
            weight_packs,
            dropProbs
        )
        if weighted:
            remain_packs.append(weighted)
    for pack in remain_packs:
        add_pack(pack, reward)
        if reward.computedDropPacks:
            rsp.rewards.extend(build_reward(reward.computedDropPacks))
            reward.clean_compute_droppacks()
    random.shuffle(rsp.rewards)
    return reward


@register_handler(RewardType.ExplorePlayerReward)
def explore_playerrewardHandler(reward, rarity, exploretimetype):
    # 构建探索玩家奖励
    # exploretimetype：探索时间类型
    from config.configs import get_config, ExploreRewardConfig
    item = get_config(ExploreRewardConfig)[rarity, exploretimetype]
    reward.dropPacks = [[item.packID, 1]]
    return reward


@register_handler(RewardType.ExplorePetReward)
def explore_petrewardHandler(reward, player, teamID):
    # 构建探索宠物奖励
    # exploretimetype：探索时间类型
    from config.configs import get_config, ExploreRewardConfig, PetConfig
    import time
    exploreid = getattr(player, 'explore%d' % teamID)
    exploretimetype = getattr(player, 'exploretimetype%d' % teamID)
    pet = player.pets[exploreid]
    rarity = get_config(PetConfig)[pet.prototypeID].rarity
    item = get_config(ExploreRewardConfig)[rarity, exploretimetype]
    # 探索宠物EXP处理
    now = int(time.time())
    if now <= getattr(player, 'exploredoubletime%d' % teamID):
        expGet = item.expGet * 2
    else:
        expGet = item.expGet
    reward.attrReward['exp'] = expGet
    return reward


@register_handler(RewardType.Recharge)
@register_handler(RewardType.LimitedPacks)
@register_handler(RewardType.TimeLimitedPacks)
@register_handler(RewardType.TriggerPacks1)
@register_handler(RewardType.TriggerPacks2)
def rechargeHandler(reward, goods, is_first, gold):
    if goods:
        if is_first:
            if goods.first_drop:
                reward.dropPacks = [[goods.first_drop, 1]]
        else:
            if goods.general_drop:
                reward.dropPacks = [[goods.general_drop, 1]]
        reward.attrReward['gold'] = goods.golden
    if gold:
        reward.attrReward['gold'] = \
            reward.attrReward.setdefault('gold', 0) + int(gold)
    return reward


@register_handler(RewardType.PetPaltform)
def petpaltHandler(reward, droppackID, special_reward):
    from reward.constants import RewardItemType
    COUNT = 5
    reward.dropPacks = [[droppackID, COUNT]]  # 必定会掉的五个葫芦
    if special_reward['type'] == RewardItemType.Mat:
        reward.matList.append([special_reward['arg'], special_reward['count']])
    elif special_reward['type'] == RewardItemType.Pet:
        reward.petList.append([special_reward['arg'], special_reward['count']])
    return reward


@register_handler(RewardType.Giftkey)
def giftkeyHandler(reward, gift):
    reward.dropPacks = zip(gift.dropPacks, gift.dropPacks_count)
    reward.matList = zip(gift.mats, gift.mats_count)
    reward.equipList = zip(gift.equips, gift.equips_count)
    reward.specPacks = zip(gift.specPacks, gift.specPacks_count)
    reward.petList = zip(gift.pets, gift.pets_count)
    reward.attrReward.update(gift.attrs)
    return reward


@register_handler(RewardType.Uproar)
def uproarChestHandler(reward, dropID, rewards):
    reward.attrReward.update(rewards)
    if dropID:
        reward.dropPacks = [[dropID, 1]]
    return reward


@register_handler(RewardType.FirstRecharge)
def firstRechargeHandler(reward, dropID, gold):
    reward.dropPacks = [[dropID, 1]]
    # 首充礼包不再赠送钻石
    # if gold:
    #     reward.attrReward["gold"] = gold
    return reward


@register_handler(RewardType.Compose)
def compose(reward, pet=None, equip=None, mat=None):
    if pet:
        reward.petList = [[pet, 1]]
    if equip:
        reward.equipList = [[equip, 1]]
    if mat:
        reward.matList = [[mat, 1]]
    return reward


@register_handler(RewardType.UseMat)
def use_drop(reward, drop):
    if drop:
        reward.dropPacks = [[drop, 1]]
    return reward


@register_handler(RewardType.MonthlyCard)
@register_handler(RewardType.CreateRole)  # 不删档时，封测用户创建新角色给礼包
@register_handler(RewardType.Visit)
@register_handler(RewardType.Friendfb)
@register_handler(RewardType.Treasure)
@register_handler(RewardType.StarPacks)
@register_handler(RewardType.LevelPacks)
@register_handler(RewardType.CreatePlayer)
@register_handler(RewardType.DailyRed)
@register_handler(RewardType.GuideDefeat)
@register_handler(RewardType.SceneRewards)
@register_handler(RewardType.DailyPVP)
@register_handler(RewardType.CityContendDefend)
@register_handler(RewardType.CityContend)
@register_handler(RewardType.CityContendAttack)
@register_handler(RewardType.Monthcard)
def simple_drop(reward, drop):
    reward.dropPacks = [[drop, 1]]
    return reward


@register_handler(RewardType.Flower315Campaign)
def multiple_drop(reward, drop, count):
    reward.dropPacks = [[drop, count]]
    return reward


@register_handler(RewardType.Task)
@register_handler(RewardType.Tap)
@register_handler(RewardType.Spar)
@register_handler(RewardType.MazeDrop)
def simple_drops(reward, *drops):
    reward.dropPacks = map(list, zip(drops, repeat(1)))
    return reward
