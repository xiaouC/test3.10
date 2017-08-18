# coding:utf-8
import logging
logger = logging.getLogger("fightverifier")
from collections import defaultdict
import settings
from config.configs import get_config
from config.configs import PetConfig
from config.configs import BreakConfig
from config.configs import NewEquipConfig
from config.configs import EquipAdvanceConfig
from config.configs import PointAdditionConfig
from config.configs import EquipStrengthenConfig
# from config.configs import AmbitionConfig
# from config.configs import VipAmbitionConfig
# from config.configs import FactionStrengthenConfig
from entity.utils import get_ambition_additions
from gem.manager import get_gems_addition
from player.formulas import get_honor_additions

TRANS = {
    "ATK": "ATK",
    "DEF": "DEF",
    "HP": "HP",
    "CRIT": "CRI",
    "DODGE": "EVA",
}


def get_point_additions(p):
    point_addition = defaultdict(int)
    for k, config in get_config(PointAdditionConfig).items():
        if p.point >= config.point:
            point_addition[config.type] += config.addition
    return point_addition


# def get_ambition_additions(p):
#     additions = defaultdict(int)
#     config = get_config(AmbitionConfig).get(p.ambition)
#     attrs = ["hp", "atk", "def", "crit", "dodge"]
#     if config:
#         additions.update(dict(zip(attrs, config.addition)))
#     config = get_config(VipAmbitionConfig).get(p.vip_ambition)
#     if config:
#         for k, v in dict(zip(attrs, config.addition)).items():
#             additions[k] += v
#     return additions


def verify_base_attr(player, pet, fighter, deviation=0):
    """校验基础属性，基础属性中已经包含了情缘加成"""
    info = get_config(PetConfig).get(fighter.config_id)
    if not info:
        logger.error("not pet config %d" % fighter.config_id)
        return False
    binfo = get_config(BreakConfig).get(pet.breaklevel)
    if not binfo:
        logger.error("not break config %d" % pet.breaklevel)
        return False

    # 成就加成
    point_additions = get_point_additions(player)
    ambition_additions = get_ambition_additions(player)
    inlay = [getattr(player, 'inlay%d' % i, 0) for i in range(1, 6)]
    honor_additions = get_honor_additions(player)

    for tag in ("atk", "def", "hp", "crit", "dodge"):
        actual_value = int(getattr(fighter.base_attr, "_%s" % tag))
        base = int(getattr(pet, "base%s" % TRANS.get(tag.upper())))

        # 成就加成
        point = int(base * point_additions.get(
            "per_%s" % tag, 0) / float(100)
            ) + point_additions.get("abs_%s" % tag, 0)
        # 荣誉加成
        honor = int(base * honor_additions.get(
            "per_%s" % tag, 0) / float(100)
            ) + honor_additions.get("abs_%s" % tag, 0)
        # 野望加成
        ambition = ambition_additions.get(tag, 0)
        gems_addition = get_gems_addition(*inlay, tag={'def': 'defend'}.get(tag, tag))
        logger.debug('gems_addition: %s, %d' % (tag, gems_addition))
        except_value = base + point + honor + ambition + gems_addition
        if abs(actual_value - except_value) > deviation:
            logger.error(
                "base %d, point %d, honor %d, ambition %d",
                base, point, honor, ambition)
            logger.error(
                "pet %r, point %r, honor %r, ambition %r, vip_ambition %r, entityID %r",
                pet.name, player.point, player.campaign_honor_point, player.ambition,
                player.vip_ambition, player.entityID
            )
            logger.error(
                "%d + %d * %d / 100 * %d" % (
                    getattr(info, "%sMin" % tag),
                    getattr(info, "m%s" % tag),
                    getattr(binfo, "b%s" % tag), max(pet.level - 1, 0)))
            logger.error(
                "%s %r", "p.base%s" % TRANS.get(
                    tag.upper()), except_value)
            logger.error(
                "%s %r",
                "fighter.base_attr._%s" % tag, actual_value)
            return False
    return True


def verify_equip_attr(player, fighter, deviation=0):
    pet = player.pets.get(fighter.real_entity_id)
    pinfo = get_config(PetConfig).get(pet.prototypeID)
    advance_configs = get_config(EquipAdvanceConfig)
    if not pinfo:
        return False
    equip_configs = get_config(NewEquipConfig)
    equips = []  # 装备实例
    equips_temp = []  # 未操作过的装备，没有实例，直接读配置
    for e in fighter.equipeds:
        equip = player.equips.get(e)
        if not equip:
            if e > 0:
                return False
            else:
                equip_temp = equip_configs.get(-e)
                if equip_temp:
                    equips_temp.append(equip_temp)
        else:
            equips.append(equip)
    for tag in ("atk", "def", "hp", "crit", "dodge"):
        except_value = 0
        for equip in equips:
            value = getattr(equip, "base%s" % TRANS.get(tag.upper()))
            except_value += value
        for equip_temp in equips_temp:
            ttag = TRANS.get(tag.upper(), "").lower()
            player_equip = getattr(
                player, "player_equip%d" % equip_temp.type, 0)
            strengthen_config = get_config(
                EquipStrengthenConfig).get(player_equip)
            value = getattr(equip_temp, "init_%s" % ttag, 0)
            if strengthen_config:
                value *= (1 + strengthen_config.base_addition / float(100))
            advance_config = advance_configs.get(1)
            except_value += value * advance_config.attr_mul
        except_value = int(except_value)
        actual_value = int(getattr(fighter.equip_attr, "_%s" % tag))
        if abs(actual_value - except_value) > deviation:
            logger.error(
                "%s %r", "equip.base%s" % TRANS.get(
                    tag.upper()), except_value)
            logger.error(
                "%s %r",
                "fighter.equip_attr._%s" % tag, actual_value)
            return False
    return True


def verify(player, fight):
    if not settings.DIRECT_FIGHT_VERIFY:
        return True
    for f in fight.replay.player_fighters:
        p = player.pets.get(f.real_entity_id)
        if not p:
            logger.error(
                "not found f.real_entity_id %d" % f.real_entity_id)
            return False
        if not verify_base_attr(player, p, f, deviation=10):
            return False
        if not verify_equip_attr(player, f, deviation=10):
            return False
    return True
