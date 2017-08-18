# coding:utf-8
import random
import logging
logger = logging.getLogger('pet')
# from .constants import ExploreType
from .constants import SubAttr
from .constants import MType
# from .constants import PatchType
# from .constants import ClassType
from config.configs import get_config
from config.configs import PetConfig
from config.configs import BreakConfig
from config.configs import RelationBySameConfig
from config.configs import RelationConfig
from config.configs import AntiRelationConfig


def setdefault(_dict, key):
    v = _dict.get(key, 0)
    if v == 0:
        _dict[key] = 0
        return 0
    else:
        return v


def in_explore(player, petID):
    return petID in filter(
        lambda s: s, [
            player.explore1, player.explore2, player.explore3])

# 副属性计算
POINTSLIMIT = (100, 1000, 10000)  # 开启属性阶级所需累计值
RARITY2POINT = {1: 4, 2: 8, 3: 12, 4: 25, 5: 50}  # 星级对应增长积分值
LIMITBALANCE = POINTSLIMIT[0]  # 置换所需差值


def get_attr(attr):
    return attr % 10


def get_real_attr(phase, attr):
    # 根据阶和属性枚举，获得进阶后的属性枚举
    return phase * 10 + attr


def is_same_attr(attr1, attr2):
    # 是否同一属性
    return attr1 % 10 == attr2 % 10


def is_same_attr_group(attr1, attr2):
    # 是否同类属性
    # 火水木， 光暗
    guang_and_an = (SubAttr.Guang, SubAttr.An)
    return len(
        set(map(lambda s: s in guang_and_an, [attr1 % 10, attr2 % 10]))) == 1


def subattr_addition(t_pet, pets):
    logger.debug('before pet.subattr1 %d', t_pet.subattr1)
    logger.debug('before pet.subattr2 %d', t_pet.subattr2)
    logger.debug('before pet.subattr_point1 %d', t_pet.subattr_point1)
    logger.debug('before pet.subattr_point2 %d', t_pet.subattr_point2)
    logger.debug('before pet.subattr_point3 %d', t_pet.subattr_point3)
    logger.debug('before pet.subattr_point4 %d', t_pet.subattr_point4)
    logger.debug('before pet.subattr_point5 %d', t_pet.subattr_point5)
    for pet in pets:
        info = get_config(PetConfig)[pet.prototypeID]
        if info.mtype == MType.Evolution:  # 吞噬进化怪，不加属性积分
            continue
        add_point = RARITY2POINT[info.rarity]
        point = getattr(t_pet, 'subattr_point%d' % info.attr) + add_point
        setattr(t_pet, 'subattr_point%d' % info.attr, point)

        for phase, limit in enumerate(POINTSLIMIT):
            if point < limit:
                logger.debug('point < limit')
                break
            # 是否达到属性累计值
            if (not t_pet.subattr1) or is_same_attr(t_pet.subattr1, info.attr):
                # 开启第一个副属性，或进阶第一个副属性
                t_pet.subattr1 = get_real_attr(phase, info.attr)
            elif ((not t_pet.subattr2) and (not is_same_attr_group(t_pet.subattr1, info.attr)))\
                    or is_same_attr(t_pet.subattr2, info.attr):
                # 如果已经有一个副属性，开启第二个副属性, 或进阶第二个副属性
                t_pet.subattr2 = get_real_attr(phase, info.attr)

            if t_pet.subattr1 \
               and is_same_attr_group(t_pet.subattr1, info.attr) \
               and not is_same_attr(t_pet.subattr1, info.attr):
                # 是否发生置换
                if point >= getattr(
                    t_pet, 'subattr_point%d' %
                    get_attr(
                        t_pet.subattr1)) + LIMITBALANCE:
                    # 清空被置换的积分
                    setattr(
                        t_pet,
                        'subattr_point%d' %
                        get_attr(
                            t_pet.subattr1),
                        0)
                    t_pet.subattr1 = get_real_attr(phase, info.attr)
            elif t_pet.subattr2 \
                    and is_same_attr_group(t_pet.subattr2, info.attr) \
                    and not is_same_attr(t_pet.subattr2, info.attr):
                # 是否发生置换
                if point >= getattr(
                    t_pet, 'subattr_point%d' %
                    get_attr(
                        t_pet.subattr2)) + LIMITBALANCE:
                    # 清空被置换的积分
                    setattr(
                        t_pet,
                        'subattr_point%d' %
                        get_attr(
                            t_pet.subattr2),
                        0)
                    t_pet.subattr2 = get_real_attr(phase, info.attr)
    logger.debug('after pet.subattr1 %d', t_pet.subattr1)
    logger.debug('after pet.subattr2 %d', t_pet.subattr2)
    logger.debug('after pet.subattr_point1 %d', t_pet.subattr_point1)
    logger.debug('after pet.subattr_point2 %d', t_pet.subattr_point2)
    logger.debug('after pet.subattr_point3 %d', t_pet.subattr_point3)
    logger.debug('after pet.subattr_point4 %d', t_pet.subattr_point4)
    logger.debug('after pet.subattr_point5 %d', t_pet.subattr_point5)


# def skill_addition(t_pet, pets):
#     logger.debug('before skill %d' % t_pet.skill)
#     same_count = 0
#     skillID = get_config(PetConfig)[t_pet.prototypeID].skillID
#     for pet in pets:
#         info = get_config(PetConfig)[pet.prototypeID]
#         if skillID == info.skillID:
#             same_count += 1
#     if same_count:
#         probs = get_config(SkillupConfig)[same_count].probs
#         prob = probs[min(5, t_pet.skill) - 1] / float(100)
#     else:
#         prob = 0
#     if prob:
#         if guess(prob):
#             if skillID:
#                 skill = get_config(SkillConfig).get(skillID)
#                 if skill:
#                     t_pet.skill += 1
#                     # 最大等级调为6级
#                     t_pet.skill = min(6, t_pet.skill)
#     logger.debug('after skill %d' % t_pet.skill)


def random_level(pets):
    d = []
    from entity.sync import multi_sync_property
    for pet in pets:
        config = get_config(PetConfig)[pet.prototypeID]
        # 随机初始等级
        if config.init_lv:
            start = config.init_lv[0]
            end = config.init_lv[-1] + 1
            pet.level = random.choice(range(start, end))
            pet.save()
            d.append(pet)
    if d:
        multi_sync_property(d)


def is_evolution_pet(petID):
    from config.configs import get_config, PetConfig
    from pet.constants import MType
    petcfg = get_config(PetConfig)[petID]
    if petcfg.mtype == MType.Evolution:
        return True
    else:
        return False


def breed_cost_once(level, k):
    money = 150 + pow(level, 2.25) * k
    soul = 200 + pow(level, 2.56) * k
    return int(money), int(soul)


def breed_cost(k, start, end):
    '''
    修改精灵升级消耗公式
      金币 = int(150 + power(精灵当前等级,2.25))
      水晶 = int(200 + power(精灵当前等级,2.56))
    '''
    assert end >= start
    money = 0
    soul = 0
    for l in range(start, end):
        money_, soul_ = breed_cost_once(l, k)
        money += money_
        soul += soul_
    return money, soul


def break_cost(prototypeID, breaklevel):
    """突破所需材料数*系数*piece_amount/100=升到breaklevel级所需要的星魄数"""
    b_config = get_config(BreakConfig)[breaklevel - 1]
    p_config = get_config(PetConfig)[prototypeID]
    # need_patch is piece_amount
    cost = p_config.need_patch * p_config.camount * b_config.amount / 100
    return cost


def break_money(prototypeID, breaklevel):
    b_config = get_config(BreakConfig)[breaklevel - 1]
    p_config = get_config(PetConfig)[prototypeID]
    return int(b_config.money * p_config.cexp)


def break_star(prototypeID, breaklevel):
    p_config = get_config(PetConfig)[prototypeID]
    star = p_config.need_patch
    assert breaklevel, "Error breaklevel %r" % breaklevel
    if breaklevel == 1:
        return star
    for i in range(1, breaklevel):
        need = break_cost(prototypeID, i + 1)
        star += need
    return star


def reload_relations(p, sames):
    # {{ 取出该批同名将修改所影响的同名将
    same_to_relations = get_config(AntiRelationConfig)  # 同名将对应羁绊
    relation_configs = get_config(RelationConfig)  # 羁绊配置
    pet_configs = get_config(PetConfig)
    need_reloads = set()
    for s in sames:
        relations = same_to_relations.get(s)
        if not relations:
            continue
        relations = relations.relas
        for each in relations:
            relation = relation_configs.get(each)
            if not relation:
                continue
            need_reloads.add(relation.same)
    # }}
    relas_by_same = get_config(RelationBySameConfig)  # 同名将
    dd = {}
    for same in need_reloads:
        same_pets = p.sames.get(same, [])
        if not same_pets:
            continue
        relations = relas_by_same.get(same, [])
        if not relations:
            continue
        relations_data = {}
        for relation in relations:
            relation = relation_configs.get(relation.ID)
            needs = set()
            for need in relation.units:
                needs.add(pet_configs[need].same)
            multi = 1
            if len(needs & set(p.sames)) == len(needs):
                bests = {}
                for need in needs:
                    for each in p.sames.get(need, []):
                        pet = p.pets.get(each)
                        if not pet:
                            continue
                        info = pet_configs.get(pet.prototypeID)
                        if not bests.get(need, False):
                            bests[need] = (info.rarity >= 5)
                if all(bests.values()):
                    multi = 2
                relations_data[relation.ID] = multi
        for each in same_pets:
            pet = p.pets.get(each)
            if not pet:
                continue
            dd.setdefault(each, {}).update(relations_data)
    dirty_pets = []
    for k, v in dd.items():
        pet = p.pets[k]
        if pet.activated_relations != v:
            pet.activated_relations = v
            dirty_pets.append(pet)
    return dirty_pets
