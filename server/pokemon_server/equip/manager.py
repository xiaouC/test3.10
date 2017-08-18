# coding:utf-8
from common import msgTips
from config.configs import get_config
from config.configs import EquipAdvanceConfig
from config.configs import NewEquipConfig
from config.configs import EquipAdvanceCostConfig
from config.configs import EnchantByQualityConfig
from config.configs import EquipStrengthenConfig
from config.configs import PetConfig
from reward.manager import parse_reward
from reward.manager import MatNotEnoughError
from reward.manager import apply_reward
from reward.manager import RewardType
from reward.manager import AttrNotEnoughError
from reward.manager import combine_reward
from yy.utils import weighted_random2
from yy.utils import guess

from .constants import EquipType

SUCCESS = 0


def get_or_create_equip(p, pet, equipID):
    # 由于每个精灵出生身上会有四件基础装备
    # 四件基础装备都是固定的
    # 所以服务器只在需要时创建
    if equipID < 0:
        equip_config = get_config(
            NewEquipConfig).get(-equipID)
        if equip_config.type in (EquipType.FaBao, EquipType.ZuoQi):
            # 两种类型的装备不自动创建
            return None
        equip, = p.add_equips({"prototypeID": -equipID})
        err = install_equip(p, pet.entityID, equip.entityID)
        if err:
            return None
    else:
        equip = p.equips.get(equipID)
    return equip


def strengthen_equip(p, petID, equipID):
    pet = p.pets.get(petID)
    if not pet:
        return msgTips.FAIL_MSG_INVALID_REQUEST, 0
    equip = get_or_create_equip(p, pet, equipID)
    if not equip:
        return msgTips.FAIL_MSG_INVALID_REQUEST, 0
    equip_config = get_config(NewEquipConfig).get(equip.prototypeID)
    if not equip_config:
        return msgTips.FAIL_MSG_INVALID_REQUEST, 0
    binding = p.equipeds.get(equip.entityID)
    if petID != binding:
        return msgTips.FAIL_MSG_INVALID_REQUEST, 0
    strengthen_configs = get_config(EquipStrengthenConfig)
    strengthen_config = strengthen_configs.get(equip.level + 1)
    if not strengthen_config:
        return msgTips.FAIL_MSG_INVALID_REQUEST, 0
    if p.level < strengthen_config.need_level:
        return msgTips.FAIL_MSG_INVALID_REQUEST, 0
    cost = {"money": strengthen_config.cost}
    try:
        apply_reward(p, {}, cost, type=RewardType.StrengthenEquip)
    except AttrNotEnoughError:
        return msgTips.FAIL_MSG_INVALID_REQUEST, 0
    if guess(strengthen_config.rate / float(100)):
        equip.level += 1
        rollback = False
    else:
        equip.level = strengthen_config.rollback
        rollback = True
    update_ranking_equip(p, equip)
    equip.save()
    equip.sync()
    from task.manager import on_strengthen_equip
    on_strengthen_equip(p, equip)
    p.save()
    p.sync()
    return SUCCESS, rollback


def advance_equip(p, petID, equipID, equips):
    pet = p.pets.get(petID)
    if not pet:
        return msgTips.FAIL_MSG_INVALID_REQUEST
    equip = get_or_create_equip(p, pet, equipID)
    if not equip:
        return msgTips.FAIL_MSG_INVALID_REQUEST
    equip_config = get_config(NewEquipConfig).get(equip.prototypeID)
    if not equip_config:
        return msgTips.FAIL_MSG_INVALID_REQUEST
    binding = p.equipeds.get(equip.entityID)
    if petID != binding:
        return msgTips.FAIL_MSG_INVALID_REQUEST
    advance_configs = get_config(EquipAdvanceConfig)
    advance_config = advance_configs.get(equip.step)
    if equip.step + 1 > max(advance_configs):
        return msgTips.FAIL_MSG_INVALID_REQUEST
    # 宠物必须满足等级要求
    if pet.level < advance_config.level:
        return msgTips.FAIL_MSG_INVALID_REQUEST
    advance_cost_config = get_config(
        EquipAdvanceCostConfig).get(equip_config.gup_id)
    if not advance_cost_config:
        return msgTips.FAIL_MSG_INVALID_REQUEST
    cost = parse_reward(advance_cost_config.costs[equip.step - 1])
    combine_reward({"money": advance_config.money}, {}, data=cost)
    equipList = sorted([i[0] for i in cost.pop("equipList", [])])
    try:  # 扣除装备，宠物 TODO
        equips = [p.equips[i] for i in equips]
        equips_prototypeID = sorted([i.prototypeID for i in equips])
        if len(equips_prototypeID) != len(equipList):
            raise KeyError
        for i in range(len(equips_prototypeID)):
            if equips_prototypeID[i] != equipList[i]:
                raise KeyError
        apply_reward(p, {}, cost, type=RewardType.EquipAdvance)
        p.del_equips(*equips)
    except KeyError:
        return msgTips.FAIL_MSG_INVALID_REQUEST
    except (AttrNotEnoughError or MatNotEnoughError):
        return msgTips.FAIL_MSG_INVALID_REQUEST
    equip.step += 1
    from task.manager import on_advance_equip
    on_advance_equip(p, equip)
    update_ranking_equip(p, equip)
    equip.save()
    equip.sync()
    p.save()
    p.sync()
    return SUCCESS


def install_equip(p, petID, equipID, force=False, sync=True):
    pet = p.pets.get(petID)
    if not pet:
        return msgTips.FAIL_MSG_INVALID_REQUEST
    equip = p.equips.get(equipID)
    if not equip:
        return msgTips.FAIL_MSG_EQUIP_NOT_FOUND
    if equipID in p.equipeds and not force:
        return msgTips.FAIL_MSG_INVALID_REQUEST
    if equip.type in pet.equipeds and not force:
        return msgTips.FAIL_MSG_INVALID_REQUEST
    pet.equipeds[equip.type] = equipID
    p.equipeds[equipID] = petID
    if sync:
        pet.save()
        pet.sync()
    return SUCCESS


def enchant_equip(p, equipID, locks=None, ex=False):
    if not locks:
        locks = []
    equip = p.equips[equipID]
    info = get_config(NewEquipConfig).get(equip.prototypeID)
    if not info:
        return
    advance_config = get_config(EquipAdvanceConfig).get(equip.step)
    if not advance_config:
        return
    configs = get_config(EnchantByQualityConfig)
    group = configs.get(advance_config.color)
    if not group:
        return
    if ex:
        prob = "gold_prob"
    else:
        prob = "prob"
    for index in range(equip.slugs):
        if index in locks:
            try:
                attr = equip.enchants[index]
            except IndexError:
                attr = info.enchID
        else:
            attr = weighted_random2([[i.ID, getattr(i, prob)] for i in group])
        try:
            equip.enchants[index] = attr
        except IndexError:
            equip.enchants.append(attr)
    update_ranking_equip(p, equip)
    from task.manager import on_enhant_equip
    on_enhant_equip(p)
    equip.save()
    equip.sync()


def get_equipeds_infos(entityID, petID, index, detail=False):
    from pet.model import Pet
    from equip.model import Equip
    from entity.manager import g_entityManager
    p = g_entityManager.get_player(entityID)
    equips = {}
    if not p:
        pet = Pet.simple_load(petID, ["prototypeID", "equipeds"])
        pet.equipeds.load()
        ids = [i for i in pet.equipeds.values()]
        if detail:
            equips = dict(zip(ids, Equip.batch_load(
                ids,
                ["prototypeID", "level", "step"] + list(Equip.expend_fields([
                    "enchant_attrs"]))
            )))
    else:
        pet = p.pets[petID]
        equips = p.equips
    infos = []
    petInfo = get_config(PetConfig)[pet.prototypeID]
    for type, prototypeID in enumerate(petInfo.equips, 1):
        equipID = pet.equipeds.get(type)
        if not equipID:
            if not prototypeID:
                continue
            d = {
                "index": index,
                "type": type,
                "equipID": prototypeID,
                "prototypeID": prototypeID,
                "level": 0,
                "step": 1,
                "enchant_attrs": "",
            }
        else:
            d = {
                "index": index,
                "type": type,
                "equipID": equipID,
            }
            e = equips.get(equipID)
            if not e:
                continue
            d["prototypeID"] = e.prototypeID
            d["level"] = e.level
            d["step"] = e.step
            d["enchant_attrs"] = e.enchant_attrs
        infos.append(d)
    return infos


def update_ranking_equip(p, e):
    if p.ranking_equip_power_entityID == e.entityID or\
            e.power > p.ranking_equip_power:
        p.ranking_equip_power = e.power
        p.ranking_equip_power_entityID = e.entityID
        p.ranking_equip_power_prototypeID = e.prototypeID
        p.ranking_equip_power_step = e.step
        p.ranking_equip_power_level = e.level
        p.save()
