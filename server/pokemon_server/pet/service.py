# coding: utf-8
import logging
logger = logging.getLogger('world')

from collections import defaultdict

import protocol.poem_pb as msgid

from common import msgTips
from yy.rpc import RpcService
from yy.rpc import rpcmethod
from yy.message.header import fail_msg
from yy.message.header import success_msg
from yy.utils import weighted_random2
from config.configs import get_config
from config.configs import PetConfig
from config.configs import PetBySameConfig
from config.configs import FusionPoolConfig
from config.configs import FusionCostConfig
from config.configs import PetLevelOrSkillLevelUpConfig
from config.configs import GrowthConfig
from reward.manager import apply_reward
from reward.manager import RewardType
from reward.manager import AttrNotEnoughError
from reward.manager import MatNotEnoughError
from reward.manager import parse_reward
from reward.manager import combine_reward
from protocol.poem_pb import ResponseHeroEvolution
from protocol.poem_pb import RequestHeroEvolution
from protocol import poem_pb
from entity.manager import level_required
from lineup.manager import in_lineup
from lineup.constants import LineupType
from lineup.manager import save_lineup

# from .manager import breed_cost
from .manager import break_cost
from .manager import break_star
from .manager import break_money
from equip.constants import EquipType


def have_break_level(player, petID):
    pet = player.pets.get(petID)
    return True if pet.breaklevel > 1 else False


class PetService(RpcService):

    # @rpcmethod(msgid.HERO_SALE)
    # def sale_pets(self, msgtype, body):
    #     from protocol.poem_pb import RequestHeroSale
    #     from lineup.manager import in_lineup
    #     from pet.manager import in_explore
    #     req = RequestHeroSale()
    #     req.ParseFromString(body)
    #     player = self.player
    #     petIDs = req.heroIDs
    #     if len(petIDs) == 0:
    #         return fail_msg(msgtype, reason='没有可以出售的将')
    #     # 检查是否有重复ID在列表
    #     assert len(petIDs) == len(set(petIDs)), 'Duplicate pet'
    #     price = 0
    #     sales = []
    #     for petID in petIDs:
    #         pet = player.pets[petID]
    #         if in_lineup(player, pet.entityID):
    #             return fail_msg(msgtype, reason='阵上将不可出售')
    #         if in_explore(player, pet.entityID):
    #             return fail_msg(msgtype, reason='探索中不可出售')
    #         petInfo = get_config(PetConfig)[pet.prototypeID]
    #         if not petInfo:
    #             return fail_msg(msgtype, msgTips.FAIL_MSG_PET_NOTCONFIG)
    #         price += petInfo.sellk * pet.level
    #         sales.append(pet)
    #     # 删除英雄
    #     player.del_pets(*sales)
    #     # 返还金钱
    #     apply_reward(player, {"money": price}, type=RewardType.SalePet)
    #     player.save()
    #     player.sync()

    #     # 物品数据包
    #     from protocol.poem_pb import ResponseHeroSale
    #     msg = ResponseHeroSale(totalPrice=price)
    #     return success_msg(msgtype, msg)

    @rpcmethod(msgid.HERO_EVOLUTION)
    @level_required(tag="evo")
    def evolute(self, msgtype, body):
        from lineup.manager import in_lineup
        from reward.constants import RewardItemType
        req = RequestHeroEvolution()
        req.ParseFromString(body)
        player = self.player
        from entity.manager import save_guide
        save_guide(player, req.guide_type)  # 保存新手引导进度
        pet = player.pets.get(req.targetHeroID)
        if not pet:
            return fail_msg(msgtype, reason='找不到对应的将')
        configs = get_config(PetConfig)
        info = configs.get(pet.prototypeID)
        grow = get_config(GrowthConfig)[info.rarity * 10 + info.step]
        if not info:
            return fail_msg(msgtype, reason='找不到对应的将')
        if pet.level < grow.hero_lv:  # 检查等级是否为满级
            return fail_msg(msgtype, reason='等级不足')
        # if in_lineup(player, pet.entityID) and \
        #         not in_lineup(player, pet.entityID, type=LineupType.ATK):
        #     return fail_msg(msgtype, reason='阵上将不可作为材料')
        price = int(grow.evo_cost * info.cexp)  # 取得开销
        logger.debug(
            'ID {}, price {}'.format(
                info.rarity *
                10 +
                info.step,
                price))
        gups = zip(info.gups, info.guptypes, info.gupnums)
        need_mats, need_pets = {}, {}
        for gup, guptype, gupnum in gups:
            if guptype == RewardItemType.Mat:
                need_mats[gup] = need_mats.setdefault(gup, 0) + gupnum
            elif guptype == RewardItemType.Pet:
                need_pets[gup] = need_pets.setdefault(gup, 0) + gupnum
            else:
                continue
        all_pets = {}
        for petID, p in player.pets.items():
            all_pets.setdefault(p.prototypeID, []).append(petID)
        pets, mats = [], [list(i) for i in need_mats.items()]
        for k, v in need_pets.items():
            ps = filter(
                lambda s: not in_lineup(
                    player, s) and not have_break_level(
                    player, s), all_pets.get(
                    k, []))
            if len(ps) < v:
                return fail_msg(msgtype, reason='材料不足')
            pets.extend([player.pets[i] for i in ps[:v]])
        assert len(pets) == len(set(pets)), '有重复的pet'
        try:
            apply_reward(
                player,
                {},
                cost={
                    'matList': mats,
                    'money': price},
                type=RewardType.EvolutionPet)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason='金币不足')
        except MatNotEnoughError:
            return fail_msg(msgtype, reason='材料不足')
        else:
            # 删除材料英雄
            equips = []
            for each in pets:
                for k, v in each.equipeds.items():
                    e = player.equips.get(v)
                    if e:
                        equips.append(e)
            l = list(player.lineups.get(LineupType.ATK, [0, 0, 0, 0]))
            # 攻击阵型可以被炼化
            flag = False
            for each in pets:
                if in_lineup(player, each.entityID, type=LineupType.ATK):
                    flag = True
                    l[l.index(each.entityID)] = 0
            if flag:
                save_lineup(player, l, LineupType.ATK)
            player.del_pets(*pets)
            player.del_equips(*equips)

        # 进阶, 精灵等级,精灵突破等级，精灵技能等级要进行继承
        pet.prototypeID = info.gupr
        # 情缘
        # FIXME
        from config.configs import AntiRelationConfig
        from config.configs import RelationConfig
        sames_info = get_config(AntiRelationConfig)
        relas_info = get_config(RelationConfig)
        same = sames_info.get(info.same)
        if same:
            for each in same.relas:
                rela = relas_info.get(each)
                if not rela:
                    continue
                if rela.same in player.sames:
                    needs = set()
                    for i in rela.units:
                        ii = configs.get(i)
                        if not ii:
                            continue
                        needs.add(ii.same)
                    if len(needs & set(player.sames)) == len(needs):
                        flag = False
                        for same in needs:
                            if same == rela.same:
                                continue
                            for petID in player.sames.get(same, []):
                                ii = configs[player.pets[petID].prototypeID]
                                if ii.rarity == 5:
                                    flag = True
                                    break
                            if not flag:
                                break
                        for petID in player.sames[rela.same]:
                            pp = player.pets[petID]
                            this_flag = True
                            if flag:
                                if configs[pp.prototypeID].rarity != 5:
                                    this_flag = False
                            if flag and this_flag:
                                multi = 2
                            else:
                                multi = 1
                            pp.activated_relations[rela.ID] = multi
                            pp.save()
                            pp.sync()
        pet.exp = 0
        pet.save()
        pet.sync()
        # 扣除金钱
        from task.manager import on_evolution
        on_evolution(player, pet)
        from task.manager import on_collect_pet1
        on_collect_pet1(player, pet)
        # player.update_power()
        player.save()
        player.sync()
        msg = ResponseHeroEvolution(costHeroIDs=[i.entityID for i in pets])
        return success_msg(msgtype, msg)

    @rpcmethod(msgid.HERO_BREED)
    @level_required(tag="levelup")
    def breed(self, msgtype, body):
        from protocol.poem_pb import BreedRequest
        req = BreedRequest()
        req.ParseFromString(body)
        player = self.player
        from entity.manager import save_guide
        save_guide(player, req.guide_type)  # 保存新手引导进度
        c = req.count or 1
        pet = player.pets.get(req.petID)
        if not pet:
            return fail_msg(msgtype, reason='精灵不存在')
        if pet.level + c > pet.max_level:
            return fail_msg(msgtype, reason='超过最大等级')
        # info = get_config(PetConfig)[pet.prototypeID]
        # money, soul = breed_cost(info.cexp, pet.level, pet.level + c)
        cost = {}
        for level in range(pet.level, pet.level + c):
            linfo = get_config(PetLevelOrSkillLevelUpConfig)[level]
            combine_reward(
                [linfo.units_cost1, linfo.units_cost2], {},
                data=cost)
        try:
            apply_reward(
                player, None, cost=cost,
                type=RewardType.BreedPet)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="金币或水晶不足")
        pet.level += c
        pet.save()
        from task.manager import on_breed
        on_breed(player, pet)
        # player.update_power()
        player.save()
        pet.sync()
        player.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.BREAK)
    @level_required(tag="star")
    def pet_break(self, msgtype, body):
        from config.configs import get_config
        from config.configs import PetConfig
        from lineup.manager import in_lineup
        p = self.player
        req = poem_pb.BreakRequest()
        req.ParseFromString(body)
        from entity.manager import save_guide
        save_guide(p, req.guide_type)  # 保存新手引导进度
        if len(req.pets) != len(set(req.pets)):
            return fail_msg(msgtype, reason="重复的精灵ID")
        if req.petID in req.pets:
            return fail_msg(msgtype, reason="重复的精灵ID")
        # 检查是否存在
        pet = p.pets.get(req.petID)
        if not pet:
            return fail_msg(msgtype, reason="精灵不存在")
        pets = []
        configs = get_config(PetConfig)
        config = configs[pet.prototypeID]
        for pt in req.pets:
            pt = p.pets.get(pt)
            if in_lineup(p, pt.entityID) and \
                    not in_lineup(p, pt.entityID, type=LineupType.ATK):
                return fail_msg(msgtype, reason='阵上将不可作为材料')
            if not pt:
                return fail_msg(msgtype, reason="精灵不存在")
            c = configs.get(pt.prototypeID)
            if c.same != config.same:
                return fail_msg(msgtype, reason="只能消耗同种类精灵")
            pets.append(pt)
        mats = defaultdict(int)
        mats_ = dict(zip(req.mats, req.mats_count))
        for k, v in mats_.items():
            mats[k] += v
        for k, v in mats.items():
            if p.mats.get(k, 0) < v:
                return fail_msg(msgtype, reason="碎片数量不足")
        # 计算提供的星魄数
        star = sum(mats.values())
        for pt in pets:
            star += break_star(pt.prototypeID, pt.breaklevel)
        star_ = star
        rest_star = pet.add_star
        for i in range(1, pet.breaklevel):
            rest_star -= break_cost(pet.prototypeID, i + 1)
        logger.debug("rest_star %r", rest_star)
        star_ += rest_star
        breaklevel = pet.breaklevel
        incr = 0
        money = 0
        while star_:
            logger.debug("star_ %d", star_)
            logger.debug("breaklevel %d", breaklevel)
            try:
                need = break_cost(pet.prototypeID, breaklevel + 1)
                money_ = break_money(pet.prototypeID, breaklevel + 1)
            except KeyError:
                break
            logger.debug("need %d %d", need, money_)
            logger.debug("star_ - need >= 0 is %r" % (star_ - need >= 0))
            if star_ - need >= 0:
                incr += 1
                breaklevel += 1
                star_ -= need
                money += money_
                logger.debug("money %r", money)
            else:
                break
            logger.debug("incr %d" % incr)
        logger.debug("result star_ incr %d %d", star_, incr)
        matList = [[k, v] for k, v in mats.items()]
        cost = {'money': money, 'matList': matList}
        try:
            apply_reward(p, {}, cost, type=RewardType.Break)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="金币不足")
        l = list(p.lineups.get(LineupType.ATK, [0, 0, 0, 0]))
        flag = False
        for each in pets:
            if in_lineup(p, each.entityID, type=LineupType.ATK):
                flag = True
                l[l.index(each.entityID)] = 0
        if flag:
            save_lineup(p, l, LineupType.ATK)
        equips = []
        for each in pets:
            for k, v in each.equipeds.items():
                e = p.equips.get(v)
                if e:
                    equips.append(e)
        p.del_pets(*pets)
        p.del_equips(*equips)
        pet.add_star += star
        pet.save()
        pet.sync()
        from task.manager import on_break_pet
        on_break_pet(p, pet)
        # p.update_power()
        p.save()
        p.sync()
        from chat.manager import on_news_pet_breaklevel_break
        on_news_pet_breaklevel_break(p, pet)
        return success_msg(msgtype, '')

    @rpcmethod(msgid.GET_PET_BOOK)
    def book(self, msgtype, body):
        from protocol.poem_pb import PetBook
        rsp = PetBook()
        rsp.book = self.player.book
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SAVE_PET_BOOK)
    def save_book(self, msgtype, body):
        from protocol.poem_pb import PetBook
        req = PetBook()
        req.ParseFromString(body)
        for ID in req.book:
            if ID > 0:
                try:
                    self.player.book.remove(-ID)
                except KeyError:
                    pass
            self.player.book.add(ID)
        self.player.save()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.GET_EXPLORE_INFOS)
    def get_explore_infos(self, msgtype, body):
        # 获取探索界面基本信息
        from protocol.poem_pb import ResponseExploreInfo
        from constants import ExploreType
        import time
        player = self.player
        now = int(time.time())
        rsp = ResponseExploreInfo()

        for i in [ExploreType.Explore1,
                  ExploreType.Explore2,
                  ExploreType.Explore3]:
            # 检测有哪些宠物正在探索
            explore = getattr(player, 'explore%d' % i)
            if explore:
                end = getattr(player, 'exploretime%d' % i)
                exploretimetype = getattr(player, 'exploretimetype%d' % i)
                if now >= end:
                    # 探索结束，可以领取奖品
                    setattr(rsp, 'cdTime%d' % i, 0)
                else:
                    # 搜索未结束
                    setattr(rsp, 'cdTime%d' % i, end - now)
                setattr(rsp, 'cdType%d' % i, exploretimetype)
        player.save()
        player.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.PET_SKILL_UP)
    def skill_up(self, msgtype, body):
        req = poem_pb.SkillUpRequest()
        req.ParseFromString(body)
        error = fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        p = self.player
        pet = p.pets.get(req.petID)
        if not pet:
            return error
        configs = get_config(PetLevelOrSkillLevelUpConfig)
        skill_level = getattr(pet, "skill%d" % req.skill, None)
        if skill_level is None:
            return error
        count = req.count or 1
        if skill_level + count > pet.level:
            return error
        cost = {}
        for l in range(skill_level,  skill_level + count):
            config = configs[l]
            combine_reward([getattr(
                config, "skill%d_cost" % req.skill, {})], [], cost)
            cost["skillpoint"] = cost.setdefault("skillpoint", 0) + 1
        try:
            apply_reward(p, {}, cost, type=RewardType.PetSkillUp)
        except AttrNotEnoughError:
            return error
        setattr(pet, "skill%d" % req.skill, skill_level + count)
        from task.manager import on_skillup
        on_skillup(p, count)
        # p.update_power()
        pet.save()
        pet.sync()
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.PET_FUSION)
    def fusion(self, msgtype, body):
        req = poem_pb.FusionRequest()
        req.ParseFromString(body)
        p = self.player
        from entity.manager import save_guide
        save_guide(p, req.guide_type)  # 保存新手引导进度
        configs = get_config(PetConfig)
        cls = None  # 品级
        maxLevel = 1
        maxStep = 0
        maxSkill1 = 1
        maxSkill2 = 1
        maxSkill3 = 1
        maxSkill4 = 1
        maxSkill5 = 1
        error = fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        pets = []
        bestEquips = {}
        equipsNeedDelete = []
        if len(req.pets) != 6:
            return error
        star = 0
        for t in req.pets:
            pet = p.pets.get(t)
            if not pet:
                return error
            if in_lineup(p, t):
                if not in_lineup(p, t, type=LineupType.ATK):
                    return error
            pets.append(pet)
            config = configs.get(pet.prototypeID)
            if not config:
                return error
            if cls and config.cls != cls:  # 校验全部品级相同
                return error
            cls = config.cls  # 上一个品级
            if cls >= 6:
                return error
            for i in pet.equipeds.values():
                equip = p.equips.get(i)
                if not equip:
                    continue
                if equip.type in (EquipType.FaBao, EquipType.ZuoQi):
                    equipsNeedDelete.append(equip)
                else:
                    best = bestEquips.get(equip.type)
                    if not best or equip.step > best.step:  # 比之前的装备好
                        bestEquips[equip.type] = equip
                        if best:
                            equipsNeedDelete.append(best)
                    else:
                        equipsNeedDelete.append(equip)
            maxLevel = max(maxLevel, pet.level)  # 继承最大等级
            maxStep = max(maxStep, config.herostep)  # 继承最大阶级
            maxSkill1 = max(maxSkill1, pet.skill1)
            maxSkill2 = max(maxSkill2, pet.skill2)
            maxSkill3 = max(maxSkill3, pet.skill3)
            maxSkill4 = max(maxSkill4, pet.skill4)
            maxSkill5 = max(maxSkill5, pet.skill5)
            star += pet.star / float(config.need_patch)
        pool = get_config(FusionPoolConfig).get(cls + 1, [])
        if not pool:
            return error
        t = weighted_random2([[c.prototypeID, c.prob] for c in pool])
        config = configs.get(t)
        if not config:
            return error
        same = config.same
        #  继承阶级
        config = None
        for t in get_config(PetBySameConfig).get(same):
            pp = configs.get(t.prototypeID)
            if not pp:
                return error
            if pp.herostep == maxStep:
                config = pp
                break
        if not config:
            return error
        fusion_cost = get_config(FusionCostConfig).get(cls)
        if not fusion_cost:
            return error
        cost = parse_reward([{
            "type": fusion_cost.type, "count": fusion_cost.cost}])
        gain = {'petList': [[config.prototypeID, 1]]}
        extra = {}
        try:
            apply_reward(p, gain, cost, type=RewardType.Fusion, extra=extra)
        except AttrNotEnoughError:
            return error
        except MatNotEnoughError:
            return error
        pet = extra.get("pets")[0]
        # 继承等级
        for _, equip in bestEquips.items():
            from equip.manager import install_equip
            install_equip(
                p, pet.entityID,
                equip.entityID, force=True, sync=False)
        pet.level = maxLevel
        # 继承星级
        star = int(star / float(6) * config.need_patch)
        pet.add_star = star - pet.base_star
        # 继承技能
        pet.skill1 = maxSkill1
        pet.skill2 = maxSkill2
        pet.skill3 = maxSkill3
        pet.skill4 = maxSkill4
        pet.skill5 = maxSkill5
        l = list(p.lineups.get(LineupType.ATK, [0, 0, 0, 0]))
        # 攻击阵型可以被炼化
        flag = False
        for each in pets:
            if in_lineup(p, each.entityID, type=LineupType.ATK):
                flag = True
                l[l.index(each.entityID)] = 0
        if flag:
            save_lineup(p, l, LineupType.ATK)
        p.del_pets(*pets)
        p.del_equips(*equipsNeedDelete)
        from task.manager import on_collect_pet2
        on_collect_pet2(p, pet)
        from task.manager import on_pet_fusion_count
        on_pet_fusion_count(p, pet)
        pet.save()
        pet.sync()
        rsp = poem_pb.FustionResponse()
        rsp.pet_entity_id = pet.entityID
        # p.update_power()
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)
