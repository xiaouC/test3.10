# coding:utf-8
import ujson
from yy.entity.formulas import register_formula
from equip.constants import EquipAttrType
from lineup.constants import LineupType


#  def calc_base(base, unit, rate, level):
#      return base + unit * level
#
#
#  def calc_enchant(enchant_attrs, attr_type):
#      rs = 0
#      try:
#          enchants = ujson.loads(enchant_attrs)
#      except ValueError:
#          enchants = []
#      for _, type, value in enchants:
#          if attr_type == type:
#              rs += value
#      return rs
#
#
#  @register_formula
#  def get_equip_base_hp(prototypeID, level, enchant_attrs):
#      from config.configs import get_config, EquipConfig
#      configs = get_config(EquipConfig)
#      info = configs.get(prototypeID)
#      if not info:
#          return 0
#      result = calc_base(info.HP, info.HGU, info.HGV, level)
#      return result + calc_enchant(enchant_attrs, EquipAttrType.Hp)
#
#
#  @register_formula
#  def get_equip_base_atk(prototypeID, level, enchant_attrs):
#      from config.configs import get_config, EquipConfig
#      configs = get_config(EquipConfig)
#      info = configs.get(prototypeID)
#      if not info:
#          return 0
#      result = calc_base(info.ATK, info.AGU, info.AGV, level)
#      return result + calc_enchant(enchant_attrs, EquipAttrType.Atk)
#
#
#  @register_formula
#  def get_equip_base_def(prototypeID, level, enchant_attrs):
#      from config.configs import get_config, EquipConfig
#      configs = get_config(EquipConfig)
#      info = configs.get(prototypeID)
#      if not info:
#          return 0
#      result = calc_base(info.DEF, info.DGU, info.DGV, level)
#      return result + calc_enchant(enchant_attrs, EquipAttrType.Def)
#
#
#  @register_formula
#  def get_equip_base_crit(prototypeID, level, enchant_attrs):
#      from config.configs import get_config, EquipConfig
#      configs = get_config(EquipConfig)
#      info = configs.get(prototypeID)
#      if not info:
#          return 0
#      result = calc_base(info.CRI, info.CGU, info.CGV, level)
#      return result + calc_enchant(enchant_attrs, EquipAttrType.Crt)
#
#
#  @register_formula
#  def get_equip_base_dodge(prototypeID, level, enchant_attrs):
#      from config.configs import get_config, EquipConfig
#      configs = get_config(EquipConfig)
#      info = configs.get(prototypeID)
#      if not info:
#          return 0
#      result = calc_base(info.EVA, info.EGU, info.EGV, level)
#      return result + calc_enchant(enchant_attrs, EquipAttrType.Dodge)

def calc_enchant(enchant_attrs, attr_type):
    rs = 0
    try:
        enchants = ujson.loads(enchant_attrs)
    except ValueError:
        enchants = []
    for _, type, value in enchants:
        if attr_type == type:
            rs += value
    return rs


def get_equip_base_value(prototypeID, level, step, attr):
    from config.configs import get_config
    from config.configs import NewEquipConfig
    from config.configs import EquipAdvanceConfig
    from config.configs import EquipStrengthenConfig
    equip_config = get_config(NewEquipConfig).get(prototypeID)
    strengthen_config = get_config(EquipStrengthenConfig).get(level)
    if not equip_config:
        return 0
    advance_config = get_config(EquipAdvanceConfig).get(step)
    if not advance_config:
        advance_addition = 1
    else:
        advance_addition = advance_config.attr_mul
    if not strengthen_config:
        strengthen_addition = 1
    else:
        strengthen_addition = (
            1 + strengthen_config.base_addition / float(100))
    value = getattr(equip_config, "init_%s" % attr, 0)
    return value * strengthen_addition * advance_addition


def get_equip_base_attr(prototypeID, level, step, enchant_attrs, attr):
    base = get_equip_base_value(prototypeID, level, step, attr.lower())
    ench = calc_enchant(enchant_attrs, getattr(EquipAttrType, attr.title()))
    return base + ench


@register_formula
def get_equip_base_hp(
        prototypeID, level, step, enchant_attrs,
        player_equip1, player_equip2, player_equip3,
        player_equip4, player_equip5, player_equip6, type):
    from equip.constants import EquipType
    level = {
        EquipType.Wuqi: player_equip1,
        EquipType.FangJu: player_equip2,
        EquipType.TouKui: player_equip3,
        EquipType.XueZi: player_equip4,
        EquipType.FaBao: player_equip5,
        EquipType.ZuoQi: player_equip6,
    }[type]
    return get_equip_base_attr(prototypeID, level, step, enchant_attrs, "hp")


@register_formula
def get_equip_base_atk(
        prototypeID, level, step, enchant_attrs,
        player_equip1, player_equip2, player_equip3,
        player_equip4, player_equip5, player_equip6, type):
    from equip.constants import EquipType
    level = {
        EquipType.Wuqi: player_equip1,
        EquipType.FangJu: player_equip2,
        EquipType.TouKui: player_equip3,
        EquipType.XueZi: player_equip4,
        EquipType.FaBao: player_equip5,
        EquipType.ZuoQi: player_equip6,
    }[type]
    return get_equip_base_attr(prototypeID, level, step, enchant_attrs, "atk")


@register_formula
def get_equip_base_def(
        prototypeID, level, step, enchant_attrs,
        player_equip1, player_equip2, player_equip3,
        player_equip4, player_equip5, player_equip6, type):
    from equip.constants import EquipType
    level = {
        EquipType.Wuqi: player_equip1,
        EquipType.FangJu: player_equip2,
        EquipType.TouKui: player_equip3,
        EquipType.XueZi: player_equip4,
        EquipType.FaBao: player_equip5,
        EquipType.ZuoQi: player_equip6,
    }[type]
    return get_equip_base_attr(prototypeID, level, step, enchant_attrs, "def")


@register_formula
def get_equip_base_crit(
        prototypeID, level, step, enchant_attrs,
        player_equip1, player_equip2, player_equip3,
        player_equip4, player_equip5, player_equip6, type):
    from equip.constants import EquipType
    level = {
        EquipType.Wuqi: player_equip1,
        EquipType.FangJu: player_equip2,
        EquipType.TouKui: player_equip3,
        EquipType.XueZi: player_equip4,
        EquipType.FaBao: player_equip5,
        EquipType.ZuoQi: player_equip6,
    }[type]
    return get_equip_base_attr(prototypeID, level, step, enchant_attrs, "cri")


@register_formula
def get_equip_base_dodge(
        prototypeID, level, step, enchant_attrs,
        player_equip1, player_equip2, player_equip3,
        player_equip4, player_equip5, player_equip6, type):
    from equip.constants import EquipType
    level = {
        EquipType.Wuqi: player_equip1,
        EquipType.FangJu: player_equip2,
        EquipType.TouKui: player_equip3,
        EquipType.XueZi: player_equip4,
        EquipType.FaBao: player_equip5,
        EquipType.ZuoQi: player_equip6,
    }[type]
    return get_equip_base_attr(
        prototypeID, level, step, enchant_attrs, "dodge")


@register_formula
def get_slugs(step):
    from config.configs import get_config, EquipAdvanceConfig
    configs = get_config(EquipAdvanceConfig)
    slugs = 0
    for i in range(1, step + 1):
        config = configs.get(i)
        if not config:
            continue
        slugs += config.enchant_num
    return slugs


@register_formula
def get_enchant_attrs(prototypeID, slugs, enchants):
    if not slugs:
        cc = []
    else:
        from config.configs import get_config
        from config.configs import EnchantConfig
        from config.configs import NewEquipConfig
        info = get_config(NewEquipConfig).get(prototypeID)
        if not info:
            cc = []
        configs = get_config(EnchantConfig)
        if not enchants:
            cc = [configs[info.enchID] for i in range(slugs)]
        else:
            cc = [configs[i] for i in enchants]
            if len(cc) < slugs:
                cc += [configs[info.enchID]] * (slugs - len(cc))
    return ujson.dumps([[i.color, i.type, i.value] for i in cc])


@register_formula
def get_equipeds_json(equipeds):
    result = []
    if equipeds:
        result = equipeds.values()
    return ujson.dumps(result)


@register_formula
def get_equip_base_power(
        entityID,
        prototypeID,
        masterID,
        baseHP, baseATK, baseDEF, baseCRI, baseEVA):
    base = baseHP / 5 + baseATK + baseDEF * 2 + baseCRI * 15 + baseEVA * 25
    from entity.manager import g_entityManager
    p = g_entityManager.get_player(masterID)
    if p:
        pet_id = p.equipeds.get(entityID, 0)
        if pet_id in p.lineups.get(LineupType.ATK, []):
            p.clear_equip_power()
            p.clear_power()
    return base
