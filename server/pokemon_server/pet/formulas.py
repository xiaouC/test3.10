import ujson
from lineup.constants import LineupType
from yy.entity.formulas import register_formula


def calc_base(base, unit, lv):
    return base + unit * max(lv - 1, 0)


def get_rela_value(base, activated_relations, type):
    from config.configs import get_config
    from config.configs import RelationConfig
    relation_infos = get_config(RelationConfig)
    rela = 0
    for each, multi in activated_relations.items():
        relation = relation_infos.get(each)
        if not relation:
            continue
        if type in ("cri", "eva"):
            rela += getattr(relation, type) * multi
        else:
            rela += base * getattr(relation, "%s_per" % type) / float(100) * multi
            rela += getattr(relation, "%s_abs" % type) * multi
    return rela


@register_formula
def get_pet_base_hp(prototypeID, level, breaklevel, activated_relations):
    from config.configs import get_config, PetConfig, BreakConfig
    info = get_config(PetConfig)[prototypeID]
    binfo = get_config(BreakConfig).get(breaklevel)
    if not binfo:
        binfo = get_config(BreakConfig)[max(get_config(BreakConfig))]
    bk = getattr(info, "%s_break" % "hp", [0, 0, 0, 0, 0])[breaklevel - 1]
    base = calc_base(info.hpMin, info.mhp*binfo.bhp/float(100), level) + bk
    return base + get_rela_value(base, activated_relations, "hp")


@register_formula
def get_pet_base_atk(prototypeID, level, breaklevel, activated_relations):
    from config.configs import get_config
    from config.configs import PetConfig
    from config.configs import BreakConfig
    info = get_config(PetConfig)[prototypeID]
    binfo = get_config(BreakConfig).get(breaklevel)
    if not binfo:
        binfo = get_config(BreakConfig)[max(get_config(BreakConfig))]
    bk = getattr(info, "%s_break" % "atk", [0, 0, 0, 0])[breaklevel - 1]
    base = calc_base(info.atkMin, info.matk*binfo.batk/float(100), level) + bk
    return base + get_rela_value(base, activated_relations, "atk")


@register_formula
def get_pet_base_def(prototypeID, level, breaklevel, activated_relations):
    from config.configs import get_config, PetConfig, BreakConfig
    info = get_config(PetConfig)[prototypeID]
    binfo = get_config(BreakConfig).get(breaklevel)
    if not binfo:
        binfo = get_config(BreakConfig)[max(get_config(BreakConfig))]
    bk = getattr(info, "%s_break" % "def", [0, 0, 0, 0])[breaklevel - 1]
    base = calc_base(info.defMin, info.mdef*binfo.bdef/float(100), level) + bk
    return base + get_rela_value(base, activated_relations, "def")


@register_formula
def get_pet_base_crit(prototypeID, level, breaklevel, activated_relations):
    from config.configs import get_config, PetConfig, BreakConfig
    info = get_config(PetConfig)[prototypeID]
    binfo = get_config(BreakConfig).get(breaklevel)
    if not binfo:
        binfo = get_config(BreakConfig)[max(get_config(BreakConfig))]
    unit = info.mcrit*binfo.bcrit/float(100)
    base = calc_base(info.critMin, unit, level) / float(100)
    return base + get_rela_value(base, activated_relations, "cri")


@register_formula
def get_pet_base_dodge(prototypeID, level, breaklevel, activated_relations):
    from config.configs import get_config, PetConfig, BreakConfig
    info = get_config(PetConfig)[prototypeID]
    binfo = get_config(BreakConfig).get(breaklevel)
    if not binfo:
        binfo = get_config(BreakConfig)[max(get_config(BreakConfig))]
    unit = info.mdodge*binfo.bdodge/float(100)
    base = calc_base(info.dodgeMin, unit, level) / float(100)
    return base + get_rela_value(base, activated_relations, "eva")


def skill_power_addition(prototypeID, skill, index):
    from config.configs import get_config
    from config.configs import PetConfig
    info = get_config(PetConfig)[prototypeID]
    base = getattr(info, "skill_base%d" % index)
    incr = getattr(info, "skill_incr%d" % index)
    return base + (skill - 1) * incr


@register_formula
def get_pet_base_power(
        entityID,
        prototypeID,
        masterID,
        baseHP, baseATK, baseDEF, baseCRI, baseEVA,
        skill1, skill2, skill3, skill4, skill5):
    base = baseHP / 5 + baseATK + baseDEF * 2 + baseCRI * 15 + baseEVA * 25
    skill = skill_power_addition(prototypeID, skill1, 1) + \
        skill_power_addition(prototypeID, skill2, 2) + \
        skill_power_addition(prototypeID, skill3, 3) + \
        skill_power_addition(prototypeID, skill4, 4) + \
        skill_power_addition(prototypeID, skill5, 5)
    from entity.manager import g_entityManager
    p = g_entityManager.get_player(masterID)
    if p:
        if entityID in p.lineups.get(LineupType.ATK, []):
            p.clear_base_power()
            p.clear_power()
    return base + skill


@register_formula
def get_breaklevel(prototypeID, star):
    from config.configs import get_config
    from config.configs import PetConfig
    from pet.manager import break_cost
    config = get_config(PetConfig)[prototypeID]
    star = star - config.need_patch
    breaklevel = 1
    while star:
        try:
            need = break_cost(prototypeID, breaklevel + 1)
        except KeyError:
            return min(breaklevel, config.breaklv)
        if star >= need:
            star -= need
            breaklevel += 1
        else:
            break
    return min(breaklevel, config.breaklv)


@register_formula
def get_star(base_star, add_star):
    return base_star + add_star


@register_formula
def get_base_star(prototypeID):
    from config.configs import get_config
    from config.configs import PetConfig
    config = get_config(PetConfig)[prototypeID]
    return config.need_patch


@register_formula
def get_relations(activated_relations):
    return ujson.encode(activated_relations)


@register_formula
def get_max_level(breaklevel):
    from config.configs import get_config
    from config.configs import BreakConfig
    configs = get_config(BreakConfig)
    info = configs.get(breaklevel)
    if not info:
        return 0
    return info.max_level


@register_formula
def get_next_max_level(breaklevel):
    from config.configs import get_config
    from config.configs import BreakConfig
    configs = get_config(BreakConfig)
    info = configs.get(breaklevel + 1)
    if not info:
        return 0
    return info.max_level
