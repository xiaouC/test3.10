#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mall.service import *  # NOQA
from world.service import *  # NOQA


@rpcmethod(msgid.REFINING)
@level_required(tag="refine")
def refining(self, msgtype, body):
    from lineup.manager import in_lineup
    from config.configs import get_config
    from config.configs import RefineryConfig
    req = poem_pb.RefiningRequest()
    req.ParseFromString(body)
    player = self.player
    from entity.manager import save_guide
    save_guide(player, req.guide_type)  # 保存新手引导进度

    # 统计材料的种类和数量
    total_mat = 0
    mats = {}
    for matInfo in req.materials:
        total_mat += 1
        if matInfo.id in mats:
            mats[matInfo.id] += matInfo.count
        else:
            mats[matInfo.id] = matInfo.count

    if len(req.pet_ids) + len(req.equip_ids) + total_mat > 6:
        return fail_msg(msgtype, reason='总共可以炼化6个精灵和装备')
    if len(req.pet_ids) != len(set(req.pet_ids)):
        return fail_msg(msgtype, reason='重复的精灵实体ID')
    if len(req.equip_ids) != len(set(req.equip_ids)):
        return fail_msg(msgtype, reason='重复的装备实体ID')
    refining_pet = []
    configs = get_config(RefineryConfig)
    rewards = {}
    for petID in req.pet_ids:
        pet = player.pets.get(petID)
        if not pet:
            return fail_msg(msgtype, reason='找不到精灵炼化')
        if in_lineup(player, pet.entityID) and \
                not in_lineup(player, pet.entityID, type=LineupType.ATK):
            return fail_msg(msgtype, reason='阵上将不可作为材料')
        petInfo = get_config(PetConfig)[pet.prototypeID]
        if not petInfo:
            return fail_msg(msgtype, msgTips.FAIL_MSG_PET_NOTCONFIG)
        refinery = configs.get(petInfo.cls)
        if not refinery:
            return fail_msg(msgtype, msgTips.FAIL_MSG_PET_NOTCONFIG)
        addition_rewards = {}
        # 升级消耗
        level_configs = get_config(PetLevelOrSkillLevelUpConfig)
        level_configs = [level_configs[i] for i in filter(
            lambda s: s < pet.level, level_configs)]
        for each in level_configs:
            combine_reward(
                [each.units_cost1, each.units_cost2],
                {}, data=addition_rewards)
        # 技能消耗
        level_configs = get_config(PetLevelOrSkillLevelUpConfig)
        for l in [1, 2, 3, 4, 5]:
            slevel = getattr(pet, "skill%d" % l, 1)
            skilllevel_configs = [
                level_configs[i] for i in filter(
                    lambda s: s < slevel, level_configs)]
            for each in skilllevel_configs:
                combine_reward(
                    [getattr(each, "skill%d_cost" % l, {})],
                    {}, data=addition_rewards)
        # 升阶消耗
        step = petInfo.rarity * 10 + petInfo.step
        grow_configs = get_config(GrowthConfig)
        grow_configs = [grow_configs[i] for i in filter(
            lambda s: s < step, grow_configs)]
        for each in grow_configs:
            combine_reward(
                {"money": int(each.evo_cost * petInfo.cexp)},
                {}, data=addition_rewards)
        # 升星消耗
        break_configs = get_config(BreakConfig)
        break_configs = [break_configs[i] for i in filter(
            lambda s: s < pet.breaklevel, break_configs)]
        for each in break_configs:
            combine_reward(
                {"money": each.money},
                {}, data=addition_rewards)
        for k, v in addition_rewards.items():
            if isinstance(v, int):
                addition_rewards[k] = int(v * refinery.scale)
        for i in range(pet.star // petInfo.need_patch):
            combine_reward(refinery.rewards, {}, data=rewards)
        combine_reward(addition_rewards, {}, data=rewards)
        refining_pet.append(pet)

    # 神将身上的装备
    equips = []
    for pet in refining_pet:
        for e in pet.equipeds.values():
            equips.append(player.equips[e])

    from config.configs import EquRefineConfig
    equ_refine_config = get_config(EquRefineConfig)

    # 单个分解的装备
    for equID in req.equip_ids:
        equ = player.equips[equID]
        if not equ:
            return fail_msg(msgtype, reason='找不到装备炼化')

        equips.append(equ)

        _equ_refine_config = equ_refine_config.get(equ.prototypeID)
        if not _equ_refine_config:
            return fail_msg(msgtype, msgTips.FAIL_MSG_PET_NOTCONFIG)

        combine_reward(_equ_refine_config.equ_rewards, {}, data=rewards)

    # 单个分解的材料
    matList = []
    for matID, count in mats.iteritems():
        mat1 = player.mats.get(matID, 0)
        if mat1 < count:
            return fail_msg(msgtype, reason='材料数量不足炼化')

        matList.append([matID, count])

        mat_refine_config = equ_refine_config.get(matID)
        if not mat_refine_config:
            return fail_msg(msgtype, msgTips.FAIL_MSG_PET_NOTCONFIG)

        for i in range(0, count):
            combine_reward(mat_refine_config.mat_rewards, {}, data=rewards)

    l = list(player.lineups.get(LineupType.ATK, [0, 0, 0, 0]))
    # 攻击阵型可以被炼化
    flag = False
    for each in refining_pet:
        if in_lineup(player, each.entityID, type=LineupType.ATK):
            flag = True
            l[l.index(each.entityID)] = 0
    if flag:
        save_lineup(player, l, LineupType.ATK)

    player.del_pets(*refining_pet)
    player.del_equips(*equips)
    apply_reward(player, rewards, cost={"matList": matList}, type=RewardType.REFINING)
    player.save()
    player.sync()
    rsp = poem_pb.RefiningResponse()
    build_reward_msg(rsp, rewards)
    logger.debug(rsp)
    return success_msg(msgtype, rsp)

WorldService._method_map[msgid.REFINING] = refining
