# coding: utf-8
import time
import logging
logger = logging.getLogger('property')

from yy.message.header import success_msg
from protocol.poem_pb import MultiSyncProperty, SyncProperty
import protocol.poem_pb as msgid


def sync_property(role, fields=None, isme=False):
    '''构造属性同步信息'''
    rsp = SyncProperty()
    rsp.entityID = role.entityID
    if isme:
        rsp.type = SyncProperty.Me
    else:
        from pet.model import Pet
        from equip.model import Equip
        if isinstance(role, Pet):
            rsp.type = SyncProperty.Pet
        elif isinstance(role, Equip):
            rsp.type = SyncProperty.Equip
        else:
            rsp.type = SyncProperty.Player

    fields_map = role.__class__.fields
    if fields is None:
        fields = role.__class__.fields_list
    else:
        fields = [fields_map[name] for name in fields]

    now = int(time.time())
    for field in fields:
        if field.sync:
            value = None
            try:
                value = getattr(role, field.name)
                if value is None:
                    continue
                if field.syncTimeout:
                    value -= now
                    if value < 0:
                        value = 0
                try:
                    setattr(rsp.properties, field.name, value)
                except (TypeError, ValueError):
                    setattr(rsp.properties, field.name, int(value))
            except (TypeError, AttributeError, ValueError):
                # NOTE 可能是没定义对应模块的formulas
                logger.error("attribute typeError:%s %s %s %s" % (
                    value, type(value), field.type, field.name))
    logger.debug(rsp)
    return rsp


def multi_sync_property(roles, fields=None, isme=False):
    rsp = MultiSyncProperty()
    for role in roles:
        rsp.entities.append(sync_property(role, fields, isme))
    logger.debug(rsp)
    return rsp


def sync_property_msg(role, fields=None, isme=False):
    '构造属性同步的消息'
    rsp = sync_property(role, fields, isme)
    return success_msg(msgid.SYNC_PROPERTY, rsp)


def multi_sync_property_msg(roles, fields=None, isme=False):
    rsp = multi_sync_property(roles, fields, isme)
    return success_msg(msgid.MULTI_SYNC_PROPERTY, rsp)


from collections import defaultdict
from config.configs import get_config
from config.configs import AmbitionConfig
from config.configs import VipAmbitionConfig
from config.configs import RandomAmbitionConfig
from config.configs import PointAdditionConfig
from config.configs import NewEquipConfig
from config.configs import PetConfig
from config.configs import FactionStrengthenConfig
from equip.constants import EquipType
from gem.manager import get_gems_addition
from config.configs import EquipAdvanceConfig


def get_ambition_additions_by_raw(ambition, vip_ambition):
    additions = defaultdict(int)
    random_ambitions = get_config(RandomAmbitionConfig)
    attrs = {
        1: "ATK",
        2: "DEF",
        3: "HP",
        4: "CRIT",
        5: "DODGE",
    }
    for configs, ambition_value in [
            (get_config(AmbitionConfig), ambition),
            (get_config(VipAmbitionConfig), vip_ambition)]:
        for index, each in enumerate(ambition_value or '', 1):
            config = configs.get(index)
            if not config:
                continue
            attr = attrs.get(config.attr_type)
            if not attr:
                continue
            step = int(each)
            random_ambition = random_ambitions.get(step)
            if not random_ambition:
                continue
            value = getattr(random_ambition, attr)
            additions[attr.lower()] += value
    return additions


def get_ambition_additions(p):
    return get_ambition_additions_by_raw(p.ambition, p.vip_ambition)


def get_point_additions(p):
    point_addition = defaultdict(int)
    for k, config in get_config(PointAdditionConfig).items():
        if p.point >= config.point:
            point_addition[config.type] += config.addition
    return point_addition


def get_faction_additions(p):
    configs = get_config(FactionStrengthenConfig)
    TRANS = {
        "hp": ("hp", "uhp"),
        "atk": ("at", "uatk"),
        "crit": ("ct", "ubj"),
        "def": ("df", "udef"),
        "dodge": ("dg", "udg"),
    }
    additions = {}
    attrs = ["hp", "atk", "def", "crit", "dodge"]
    for tag in attrs:
        lv = getattr(p, "strengthen_%s_level" % TRANS[tag][0], 0)
        if not lv:
            continue
        config = configs.get(lv)
        if not config:
            continue
        value = getattr(config, TRANS[tag][1], 0)
        additions[tag] = value
    return additions


def hp2power(HP):
    return HP / float(5)


def atk2power(ATK):
    return ATK


def def2power(DEF):
    return DEF * 2


def cri2power(CRI):
    return CRI * 15


def eva2power(EVA):
    return EVA * 25


def get_power(HP, ATK, DEF, CRI, EVA):
    result = hp2power(HP)
    result += atk2power(ATK)
    result += def2power(DEF)
    result += cri2power(CRI)
    result += eva2power(EVA)
    return result


def get_equip_powers(p, pet):
    power = 0
    petInfo = get_config(PetConfig).get(pet.prototypeID)
    if not petInfo:
        return power
    equipInfos = get_config(NewEquipConfig)
    types = ["Wuqi", "FangJu", "TouKui", "XueZi", "FaBao", "ZuoQi"]
    for type in [getattr(EquipType, i) for i in types]:
        equipID = pet.equipeds.get(type)
        if not equipID:
            equipID = petInfo.equips[type - 1]
            if not equipID:
                continue
            equipInfo = equipInfos.get(equipID)
            if not equipInfo:
                continue
            advance_config = get_config(EquipAdvanceConfig).get(1)
            if not advance_config:
                advance_addition = 1
            else:
                advance_addition = advance_config.attr_mul
            strengthen_addition = 1

            values = []
            attrs = ["hp", "atk", "def", "crit", "dodge"]
            for tag in attrs:
                value = getattr(equipInfo, "init_%s" % tag, 0)
                value = value * strengthen_addition * advance_addition
                values.append(value)
            power += get_power(*values)
        else:
            equip = p.equips.get(equipID)
            if not equip:
                continue
            power += equip.power
    return power


def get_pet_total_power(p, pet):
    TRANS = {
        "ATK": "ATK",
        "DEF": "DEF",
        "HP": "HP",
        "CRIT": "CRI",
        "DODGE": "EVA",
    }
    attrs = ["hp", "atk", "def", "crit", "dodge"]
    ambitions = get_ambition_additions(p)
    points = get_point_additions(p)
    factions = get_faction_additions(p)
    values = []
    inlay = [getattr(p, 'inlay%d' % i, 0) for i in range(1, 6)]
    for tag in attrs:
        base = getattr(pet, "base%s" % TRANS[tag.upper()], 0)
        point = int(base * (points.get(
            "per_%s" % tag, 0)) / float(100)
            ) + points.get("abs_%s" % tag, 0)
        ambition = ambitions.get(tag, 0)
        faction = factions.get(tag, 0)
        gems_addition = get_gems_addition(*inlay, tag={'def': 'defend'}.get(tag, tag))
        value = base + point + ambition + faction + gems_addition
        values.append(value)
    equip_power = get_equip_powers(p, pet)
    from pet.formulas import skill_power_addition
    skill_power = 0
    for i in range(1, 6):
        skill_power += skill_power_addition(
            pet.prototypeID, getattr(pet, "skill%d" % i), i)
    power = get_power(*values) + equip_power + skill_power
    return int(power)
