# coding:utf-8
import time
import ujson
import logging
logger = logging.getLogger('mall')
from datetime import datetime, time as timetime
from datetime import date as datedate
from datetime import timedelta

import protocol.poem_pb as msgid
from protocol import poem_pb

from yy.rpc import RpcService, rpcmethod
from yy.message.header import success_msg
from yy.message.header import fail_msg

from config.configs import get_config
from config.configs import PetConfig
from config.configs import SparConfig
from config.configs import LotteryFunctionConfig
from config.configs import AttributeDroppackConfig
from config.configs import MallConfig
from config.configs import MallRefreshConfig
from config.configs import get_cons_value
from config.configs import FactionMallUnlockConfig
from config.configs import VipPacksConfig
from config.configs import VipPacksByGroupConfig
from config.configs import VipConfig
from config.configs import PetLevelOrSkillLevelUpConfig
from config.configs import GrowthConfig
from config.configs import BreakConfig
from config.configs import HotLotteryCampaignConfig

from reward.manager import RewardType
from reward.manager import open_reward
from reward.manager import apply_reward
from reward.manager import parse_reward
from reward.manager import build_reward
from reward.manager import build_reward_msg
from reward.manager import AttrNotEnoughError
from reward.manager import MatNotEnoughError
from reward.manager import combine_reward

from chat.manager import on_pet_spar
from chat.manager import on_equip_spar

from mall.constants import LotteryType
from mall.constants import MallType
from common import msgTips
from common.log import role_custom

from entity.manager import level_required

from mall.manager import refresh_mall, check_open

from faction.model import Faction
from player.formulas import get_vip_value

from .constants import VipPackType
# from .constants import VipPackDurationType
from .manager import get_vip_pack_rest_count
from .manager import set_vip_packs_limits
from lineup.constants import LineupType
from lineup.manager import save_lineup

from yy.utils import weighted_random2


class MallService(RpcService):

    @rpcmethod(msgid.LOTTERY)
    def lottery(self, msgtype, body):
        req = poem_pb.LotteryRequest()
        req.ParseFromString(body)
        p = self.player
        from entity.manager import save_guide
        save_guide(p, req.guide_type)  # 保存新手引导进度
        logger.debug("req: {}".format(req))
        LOTTERY_ID2TYPE = {
            LotteryType.Lottery1: ("A", "ball", 1),
            LotteryType.Lottery2: ("B", "ball", 10),
            LotteryType.Lottery3: ("C", "gold", 1),
            LotteryType.Lottery4: ("D", "gold", 10),
        }
        kind_cfg = get_config(LotteryFunctionConfig)[req.type]
        if req.type not in LOTTERY_ID2TYPE:
            return fail_msg(msgtype, reason="类型不对")
        if p.level < kind_cfg.level:
            return fail_msg(msgtype, reason="等级不足")
        kind, cost_type, cost_count = LOTTERY_ID2TYPE[req.type]
        cost = kind_cfg.Price
        if req.type == LotteryType.Lottery2:
            if p.ball < 10:
                cost_count = p.ball
                cost = p.ball
        now = time.time()
        loterry_hero_count = getattr(
            p, "loterry_hero_count_{}".format(kind))
        loterry_hero_gold_first = getattr(
            p, "loterry_hero_gold_first_{}".format(kind))
        loterry_hero_used_free_count = getattr(
            p, "loterry_hero_used_free_count_{}".format(kind)) or 0
        loterry_hero_cd = getattr(
            p, "loterry_hero_cd_{}".format(kind))
        cd = datetime.fromtimestamp(loterry_hero_cd).strftime('%Y-%m-%d %H:%M')
        logger.debug('loterry_hero_cd: {}'.format(cd))
        cd = datetime.fromtimestamp(loterry_hero_cd).strftime('%Y-%m-%d %H:%M')
        logger.debug('loterry_hero_cd: {}'.format(cd))
        key = "NormalGold{}".format(kind)
        if loterry_hero_cd <= now and \
           loterry_hero_used_free_count < kind_cfg.FreeTimes:  # 免费
            if not loterry_hero_count:  # 引导抽
                key = "FirstFree{}".format(kind)
                ID = kind_cfg.rangeset[1]
            elif loterry_hero_count == 1:  # 首抽
                key = "NormalFree{}".format(kind)
                ID = kind_cfg.rangeset[2]
            else:  # 普通
                key = "NormalFree{}".format(kind)
                ID = kind_cfg.rangeset[0]
        else:  # 付费
            if not loterry_hero_count:  # 引导抽
                key = "FirstGold{}".format(kind)
                ID = kind_cfg.rangeset[1]
                if not ID:
                    ID = kind_cfg.rangeset[2]
            elif loterry_hero_count == 1:  # 首抽
                key = "FirstGold{}".format(kind)
                ID = kind_cfg.rangeset[2]
            else:
                key = "NormalGold{}".format(kind)
                ID = kind_cfg.rangeset[0]
        loterry_hero_count += 1
        logger.debug(
            '\nused_free_count_A: {},\
             \nused_free_count_B: {},\
             \nused_free_count_C: {},\
             \nused_free_count_D: {}'.format(
                p.loterry_hero_used_free_count_A,
                p.loterry_hero_used_free_count_B,
                p.loterry_hero_used_free_count_C,
                p.loterry_hero_used_free_count_D))
        logger.debug('loterry_hero_key: {}'.format(key))
        costs = {}
        if "Free" in key:
            cost = 0
            loterry_hero_used_free_count += 1
            loterry_hero_cd = now + kind_cfg.ColdDown
        else:
            costs = {cost_type: cost}
            if p.lottery_campaign_discount < 10:
                gold = costs.get("gold", 0)
                if gold:
                    gold = int(gold * p.lottery_campaign_discount / float(10))
                    costs["gold"] = gold
            try:
                from reward.base import check_cost_attr
                check_cost_attr(p, costs)
            except AttrNotEnoughError:
                return fail_msg(msgtype, reason="材料不足")
            loterry_hero_gold_first = False
        if not ID:
            ID = kind_cfg.rangeset[0]
        attr_drop = get_config(AttributeDroppackConfig)[ID]
        dropID = attr_drop.RewardDroppack
        if cost_type == "gold":
            if cost_count > 1:
                if p.lottery_gold_accumulating10 >= abs(
                        attr_drop.Accumulating):
                    dropID = attr_drop.AccumDroppack
                    if attr_drop.Accumulating > 0:
                        p.lottery_gold_accumulating10 -= attr_drop.Accumulating
            else:
                if p.lottery_gold_accumulating >= abs(
                        attr_drop.Accumulating):
                    dropID = attr_drop.AccumDroppack
                    if attr_drop.Accumulating > 0:
                        p.lottery_gold_accumulating -= attr_drop.Accumulating
        else:
            if cost_count > 1:
                if p.lottery_money_accumulating10 >= abs(
                        attr_drop.Accumulating):
                    dropID = attr_drop.AccumDroppack
                    if attr_drop.Accumulating > 0:
                        p.lottery_money_accumulating10 -= \
                            attr_drop.Accumulating
            else:
                if p.lottery_money_accumulating >= abs(
                        attr_drop.Accumulating):
                    dropID = attr_drop.AccumDroppack
                    if attr_drop.Accumulating > 0:
                        p.lottery_money_accumulating -= attr_drop.Accumulating
        logger.debug("DropID:{}".format(dropID))
        rsp = poem_pb.LotteryResponse()
        reward = open_reward(RewardType.Lottery, rsp, dropID, cost_count)
        from campaign.manager import g_campaignManager
        if g_campaignManager.hot_lottery_campaign.is_open() and\
                req.type == LotteryType.Lottery4:
            campaign_config = g_campaignManager.hot_lottery_campaign.\
                get_current()
            hot_configs = get_config(HotLotteryCampaignConfig).get(
                campaign_config.group, [])
            hot_rewards = weighted_random2([
                [i.rewards, i.prob] for i in hot_configs])
            reward.add(parse_reward(hot_rewards))
            rsp.hot_rewards = hot_rewards
        reward.cost_after(p, **costs)
        extra = {}
        result = reward.apply(p, extra=extra)
        logger.debug("result {}:".format(result))
        # Save
        setattr(
            p, "loterry_hero_count_{}".format(kind),
            loterry_hero_count)
        setattr(
            p, "loterry_hero_gold_first_{}".format(kind),
            loterry_hero_gold_first)
        setattr(
            p, "loterry_hero_used_free_count_{}".format(kind),
            loterry_hero_used_free_count)
        setattr(
            p, "loterry_hero_cd_{}".format(kind), loterry_hero_cd)
        is_first_consume = int(not p.consume_count and bool(
            p.lottery_count) and (cost_type == "gold"))
        role_custom.info(player=p, type=role_custom.Consume, arg1=ujson.dumps({
            "type": RewardType.Lottery,
            "kind": req.type,
            "cost": costs,
            "is_first_consume": is_first_consume,
        }))
        p.lottery_count += cost_count
        from task.manager import on_lottery
        on_lottery(p, cost_count, (cost_type == "gold"))
        if kind == "D":
            from task.manager import on_lottery10
            on_lottery10(p)
        ACCUMULATING_DELTA = 1
        if cost_type == "gold":
            if cost_count > 1:
                p.lottery_gold_accumulating10 += \
                    ACCUMULATING_DELTA * kind_cfg.Price
            else:
                p.lottery_gold_accumulating += \
                    ACCUMULATING_DELTA * kind_cfg.Price
            p.consume_count += 1
        else:
            if cost_count > 1:
                p.lottery_money_accumulating10 += \
                    ACCUMULATING_DELTA * kind_cfg.Price
            else:
                p.lottery_money_accumulating += \
                    ACCUMULATING_DELTA * kind_cfg.Price
        if "FirstFree" not in key:
            save_guide(p, "FAKE_GOLDEN_LOTTERY")
        from task.manager import on_collect_pet1
        from task.manager import on_collect_pet2
        pets = extra.get("pets", [])
        on_collect_pet1(p, *pets)
        on_collect_pet2(p, *pets)
        p.save()
        p.sync()
        from chat.manager import on_news_pet_quality_lottery
        from chat.manager import on_news_pet_special_lottery
        from chat.manager import on_news_equip_quality_lottery
        on_news_pet_quality_lottery(p, rsp.rewards)
        on_news_pet_special_lottery(p, rsp.rewards)
        on_news_equip_quality_lottery(p, rsp.rewards)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.BUY_SP)
    def buy_sp(self, msgtype, body):
        player = self.player
        req = poem_pb.BuySPRequest()
        req.ParseFromString(body)
        sprest = player.spmax - player.sp
        if sprest <= 0:
            return fail_msg(msgtype, reason="能量已满")
        try:
            if req.usegold:
                cost = {'gold': player.buy_sp_cost}
                gain = {'sp': 120}  # 能量恢复120点
                if not player.buy_sp_rest_count:
                    return fail_msg(
                        msgtype,
                        msgTips.FAIL_MSG_MALL_EXCEED_BUY_SP_LIMIT)
                player.buy_sp_used_count += 1
            else:
                cost = {'spprop': 1}
                gain = {'sp': 60}  # 恢复药恢复60能量
            apply_reward(player, gain, cost, type=RewardType.BuySP)
        except AttrNotEnoughError as e:
            if e.attr == 'gold':
                return fail_msg(msgtype, reason="钻石不足")
            elif e.attr == 'spprop':
                return fail_msg(msgtype, reason="恢复药不足")
        if 'gold' in cost:
            from task.manager import on_buy_sp
            on_buy_sp(player)
            role_custom.info(
                player=player,
                type=role_custom.Consume,
                arg1=ujson.dumps({
                    'type': RewardType.BuySP,
                    'cost': cost,
                    'is_first_consume': int(not player.consume_count)
                })
            )
        player.consume_count += 1
        player.save()
        player.sync()
        return fail_msg(msgtype, reason='能量恢复{}点！'.format(gain['sp']))

    @rpcmethod(msgid.EXPAND_PET_BOX)
    def expand_pet_box(self, msgtype, body):
        player = self.player
        cost = {'gold': 50}
        try:
            apply_reward(
                player, {
                    'petmax': 5}, cost, type=RewardType.ExpandPetBox)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="钻石不足")
        role_custom.info(
            player=player,
            type=role_custom.Consume,
            arg1=ujson.dumps({
                'type': RewardType.ExpandPetBox,
                'cost': cost,
                'is_first_consume': int(not player.consume_count),
            })
        )
        player.consume_count += 1
        player.save()
        player.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.RESOLVE_GOLD_MSG)
    def resolve_gold_msg(self, msgtype, body):
        # 炼银信息请求
        from protocol.poem_pb import ResolveGoldMsgResponse
        from config.configs import GoldenFingerConfig, VipConfig, get_config
        player = self.player
        rsp = ResolveGoldMsgResponse()
        items = get_config(GoldenFingerConfig)
        vipcfg = get_config(VipConfig)
        golden_finger_count = vipcfg[player.vip].golden_finger_count
        resolvegold_time = player.resolvegold_time

        rsp.maxtime = golden_finger_count
        if resolvegold_time == golden_finger_count:
            rsp.time = 0
        else:
            rsp.time = golden_finger_count - resolvegold_time
        try:
            rsp.golden = items[resolvegold_time + 1].golden
            rsp.silver = items[resolvegold_time + 1].silver
        except KeyError:
            rsp.golden = items[resolvegold_time].golden
            rsp.silver = items[resolvegold_time].silver
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.RESOLVE_GOLD)
    @level_required(tag="golden_finger")
    def resolve_gold(self, msgtype, body):
        # 炼银处理
        from config.configs import get_config
        from config.configs import VipConfig
        from config.configs import GoldenFingerConfig
        from config.configs import GoldFingerLvLimitConfig
        p = self.player
        items = get_config(GoldenFingerConfig)
        vipcfg = get_config(VipConfig)
        resolvegold = get_config(GoldFingerLvLimitConfig)[1]
        golden_finger_count = vipcfg[p.vip].golden_finger_count
        cur_time = p.resolvegold_time + 1
        if p.level < resolvegold.openlv:
            return fail_msg(msgtype, reason='等级不足')
        if p.resolvegold_time >= golden_finger_count:
            return fail_msg(msgtype, reason='炼银次数已用尽')
        item = items[cur_time]
        if p.gold < item.golden:
            return fail_msg(msgtype, reason='钻石不足')
        from reward.base import apply_reward
        from reward.constants import RewardType
        cost = dict(gold=item.golden)
        reward = dict(money=item.silver)
        apply_reward(p, reward, cost, type=RewardType.ResolveGold)
        p.resolvegold_time += 1
        from task.manager import on_golden_finger
        on_golden_finger(p)
        p.save()
        p.sync()
        return self.resolve_gold_msg(msgtype, "")

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

    @rpcmethod(msgid.SPAR_INFO)
    def spar_info(self, msgtype, body):
        p = self.player
        configs = get_config(SparConfig)
        rsp = poem_pb.SparInfo()
        for k, config in configs.items():
            count = config.dropex_use_count - p.spar_counts.get(k, 0)
            info = config._asdict()
            if count == 0:
                info['tips'] = config.final_tips
            else:
                info['tips'] = config.tips.format(count + 1)
            rsp.items.add(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SPAR_REQUEST)
    def spar_request(self, msgtype, body):
        p = self.player
        req = poem_pb.SparRequest()
        req.ParseFromString(body)
        config = get_config(SparConfig).get(req.ID)
        if not config:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        logger.debug(req)
        spar_count = p.spar_counts.get(req.ID, 0)
        count = config.onekeycount if req.onekey else 1
        # cost = config.onekeycost if req.onekey else 1
        if not count:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        drops = []
        for i in range(count):
            if spar_count >= config.dropex_use_count:
                drops.append(config.dropex)
                spar_count = 0
            else:
                drops.append(config.drop)
                spar_count += 1
        if not drops:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        try:
            reward = open_reward(RewardType.Spar, *drops)
            reward.cost_after(
                p,
                matList=[[config.itemID, count]],
                money=config.money*count)
            result = reward.apply(p)
        except AttrNotEnoughError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        except MatNotEnoughError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        rsp = poem_pb.SparResponse()
        build_reward_msg(rsp, result)
        on_pet_spar(p, rsp.rewards)
        on_equip_spar(p, rsp.rewards)
        p.spar_counts[req.ID] = spar_count
        from task.manager import on_spar_count
        on_spar_count(p, spar_count)
        p.save()
        p.sync()
        logger.debug(rsp)
        count = config.dropex_use_count - p.spar_counts.get(req.ID, 0)
        info = config._asdict()
        if count == 0:
            info['tips'] = config.final_tips
        else:
            info['tips'] = config.tips.format(count + 1)
        rsp.item = poem_pb.SparItem(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.MALL_INFO)
    def mall_info(self, msgtype, body):
        p = self.player
        req = poem_pb.MallInfoRequest()
        req.ParseFromString(body)
        logger.debug(req)
        type = req.type
        if not check_open(p, type):
            # 限制
            return fail_msg(msgtype, reason="商店未开启")
        refresh_info = get_config(MallRefreshConfig)[type]
        times = p.mall_refresh_times.get(type, 0)
        now = int(time.time())
        need_refresh = not p.malls.get(type)
        if req.refresh:
            cost_amount = refresh_info.cost
            try:
                if p.shopping > 0:
                    cost = {"shopping": 1}
                else:
                    cost = parse_reward([{
                        'type': refresh_info.refresh_cost_type,
                        'count': cost_amount,
                    }])
                apply_reward(
                    p, {}, cost, type=RewardType.RefreshMall)
            except AttrNotEnoughError:
                return fail_msg(msgtype, reason="消耗不足")
            need_refresh = True
            # 增加刷新次数
            times += 1
            p.mall_refresh_times[type] = times
            from task.manager import on_refresh_shop
            on_refresh_shop(p)

            # 刷新商店的时候
            from campaign.manager import g_campaignManager
            if g_campaignManager.exchange_campaign.is_open():
                start_time, end_time = g_campaignManager.exchange_campaign.get_current_time()
                if p.exchange_campaign_last_time < start_time or p.exchange_campaign_last_time > end_time:
                    p.exchange_campaign_counter = 0
                p.exchange_campaign_counter = p.exchange_campaign_counter + 1
                p.exchange_campaign_last_time = now

                current = g_campaignManager.exchange_campaign.get_current()
                from config.configs import ExchangeCampaignByGroupConfig
                group = get_config(ExchangeCampaignByGroupConfig).get(current.group)

                ex_rsp = poem_pb.ExchangeCampaignItemResponse()

                rewards = {}
                for i in range(0, len(group.consumes)):
                    tmp_count = group.refresh_counts[i]
                    if not tmp_count or tmp_count <= 0:
                        continue

                    if p.exchange_campaign_counter % tmp_count == 0:
                        tmp_config = group.consumes[i]
                        print tmp_config
                        r = parse_reward([{
                            "arg": tmp_config["arg"],
                            "type": tmp_config["type"],
                            "count": 1,
                        }])
                        combine_reward(r, {}, rewards)

                        info = {}
                        info["arg"] = tmp_config["arg"]
                        info["type"] = tmp_config["type"]
                        info["count"] = 1
                        ex_rsp.items.add(**info)

                if len(rewards) > 0:
                    apply_reward(p, rewards, type=RewardType.RefreshMall)

                    from player.manager import g_playerManager
                    ex_msg = success_msg(msgid.EXCHANGE_CAMPAIGN_ITEM_RESULT, ex_rsp)
                    g_playerManager.sendto(p.entityID, ex_msg)

            if g_campaignManager.refresh_store_campaign.is_open():
                start_time, end_time = g_campaignManager.refresh_store_campaign.get_current_time()
                if p.refresh_store_campaign_last_time < start_time or p.refresh_store_campaign_last_time > end_time:
                    p.refresh_store_campaign_counter = 0
                p.refresh_store_campaign_counter = p.refresh_store_campaign_counter + 1
                p.refresh_store_campaign_last_time = now

                from config.configs import RefreshStoreConfig
                packs = get_config(RefreshStoreConfig)
                exempts = set(p.refresh_reward_end).union(p.refresh_reward_done)
                samples = sorted(set(packs).difference(exempts))
                for i in samples:
                    pack = packs[i]
                    if p.refresh_store_campaign_counter >= pack.count:
                        p.refresh_reward_done.add(i)
                    else:
                        break
                p.clear_refresh_reward_done_count()

        next = None
        dt = datetime.fromtimestamp(now)
        # NOTE 跨天问题
        last_ts = p.mall_last_refresh.get(type, 0)
        if not last_ts:
            need_refresh = True
            last_ts = now
        last = datetime.fromtimestamp(last_ts)
        logger.debug("上次刷新时间 %s", last)
        flag = False
        for date, daytimes in (
                [last.date(), refresh_info.daytimes],
                # 跨天不刷新
                [last.date() + timedelta(days=1), refresh_info.daytimes],
                [dt.date(), refresh_info.daytimes],
                [dt.date() + timedelta(days=1), refresh_info.daytimes]):
            for each in daytimes:
                refresh_dt = datetime.combine(date, timetime(each))
                if not flag and dt < refresh_dt:
                    next = refresh_dt
                    flag = True
                if last < refresh_dt and refresh_dt <= dt:
                    need_refresh = True
        # 临时商店不自动刷新
        if type == MallType.Golden:
            if now < p.mall_golden_open_remain:
                need_refresh = False or req.refresh
        elif type == MallType.Silver:
            if now < p.mall_silver_open_remain:
                need_refresh = False or req.refresh
        if need_refresh or not p.malls.get(type):
            refresh_mall(p, type)
            p.mall_last_refresh[type] = now
        mall = p.malls.get(type, [])
        configs = get_config(MallConfig)
        default_locked = (type == MallType.Faction)
        if default_locked:
            if p.factionID:
                mall_products = Faction.simple_load(
                    p.factionID, ['mall_products']).mall_products
        else:
            mall_products = set()
        unlock_costs = {type: {k: v.cost for k, v in get_config(
            FactionMallUnlockConfig).items()}}
        rsp = poem_pb.MallInfoResponse()
        for productID in mall:
            config = configs[productID]
            count = p.mall_limits.get(productID, 0)
            last = p.mall_times.get(productID, 0)
            remain = 0
            if last and config.cd:
                remain = max(config.cd - (now - last), 0)
            product = config._asdict()
            locked = default_locked and (config.pos not in mall_products)
            rsp.products.add(
                unlock_cost=unlock_costs.get(type, {}).get(config.pos, 0),
                count=count, remain=remain, locked=locked, **product)
        if next:
            rsp.time = next.hour
            rsp.cd = int(time.mktime(next.timetuple()) - now)
        else:
            # 不自动刷新
            rsp.time = 25
        logger.debug("下次刷新时间 %s", next)
        rsp.cost = refresh_info.cost
        rsp.cost_type = refresh_info.refresh_cost_type
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.MALL_BUY_PRODUCT)
    def mall_buy_product(self, msgtype, body):
        p = self.player
        req = poem_pb.MallBuyProduct()
        req.ParseFromString(body)
        logger.debug(req)
        config = get_config(MallConfig)[req.ID]
        if not check_open(p, config.type):
            return fail_msg(msgtype, reason="商店未开启")
        # 限制
        count = p.mall_limits.get(req.ID, 0)
        if config.limit > 0 and count >= config.limit:
            return fail_msg(msgtype, reason="超过购买次数")
        now = int(time.time())
        last = p.mall_times.get(req.ID, 0)
        if last and now < last + config.cd:
            return fail_msg(msgtype, reason="购买冷却中")
        reward = parse_reward([{
            'type': config.product_type,
            'arg': config.productID,
            'count': config.product_amount}])
        cost = parse_reward([{
            'type': config.item_type,
            'count': config.price,
        }])
        try:
            apply_reward(
                p, reward, cost,
                type=RewardType.MallBuy)
        except AttrNotEnoughError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)

        from campaign.manager import g_campaignManager
        if g_campaignManager.exchange_campaign.is_open():
            start_time, end_time = g_campaignManager.exchange_campaign.get_current_time()
            if p.exchange_campaign_last_time < start_time or p.exchange_campaign_last_time > end_time:
                p.exchange_campaign_counter = 0
            p.exchange_campaign_counter = p.exchange_campaign_counter + 1
            p.exchange_campaign_last_time = now

            current = g_campaignManager.exchange_campaign.get_current()
            from config.configs import ExchangeCampaignByGroupConfig
            group = get_config(ExchangeCampaignByGroupConfig).get(current.group)

            ex_rsp = poem_pb.ExchangeCampaignItemResponse()

            rewards = {}
            for i in range(0, len(group.consumes)):
                tmp_count = group.refresh_counts[i]
                if not tmp_count or tmp_count <= 0:
                    continue

                if p.exchange_campaign_counter % tmp_count == 0:
                    tmp_config = group.consumes[i]
                    print tmp_config
                    r = parse_reward([{
                        "arg": tmp_config["arg"],
                        "type": tmp_config["type"],
                        "count": 1,
                    }])
                    combine_reward(r, {}, rewards)

                    info = {}
                    info["arg"] = tmp_config["arg"]
                    info["type"] = tmp_config["type"]
                    info["count"] = 1
                    ex_rsp.items.add(**info)

            if len(rewards) > 0:
                apply_reward(p, rewards, type=RewardType.RefreshMall)

                from player.manager import g_playerManager
                ex_msg = success_msg(msgid.EXCHANGE_CAMPAIGN_ITEM_RESULT, ex_rsp)
                g_playerManager.sendto(p.entityID, ex_msg)

        #if g_campaignManager.refresh_store_campaign.is_open():
        #    start_time, end_time = g_campaignManager.refresh_store_campaign.get_current_time()
        #    if p.refresh_store_campaign_last_time < start_time or p.refresh_store_campaign_last_time > end_time:
        #        p.refresh_store_campaign_counter = 0
        #    p.refresh_store_campaign_counter = p.refresh_store_campaign_counter + 1
        #    p.refresh_store_campaign_last_time = now

        #    from config.configs import RefreshStoreConfig
        #    packs = get_config(RefreshStoreConfig)
        #    exempts = set(p.refresh_reward_end).union(p.refresh_reward_done)
        #    samples = sorted(set(packs).difference(exempts))
        #    for i in samples:
        #        pack = packs[i]
        #        if p.refresh_store_campaign_counter >= pack.count:
        #            p.refresh_reward_done.add(i)
        #        else:
        #            break
        #    p.clear_refresh_reward_done_count()

        p.mall_limits[req.ID] = count + 1
        p.mall_times[req.ID] = now
        from task.manager import on_shopping
        on_shopping(p)
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.MALL_OPEN)
    def mall_open(self, msgtype, body):
        p = self.player
        req = poem_pb.MallOpen()
        req.ParseFromString(body)
        logger.debug(req)
        cost = 0
        if req.type == MallType.Golden:
            if p.mall_golden_open_cost:
                cost = p.mall_golden_open_cost
            f = 'mall_golden_opened'
            n = 'OpenGoldenMallCost'
        elif req.type == MallType.Silver:
            if p.mall_silver_open_cost:
                cost = p.mall_silver_open_cost
            f = 'mall_silver_opened'
            n = 'OpenSilverMallCost'
        if not cost:
            return fail_msg(msgtype, reason="不满足开启条件")
        try:
            apply_reward(
                p, {}, {'gold': get_cons_value(n)}, type=RewardType.MallOpen)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="钻石不足")
        setattr(p, f, True)
        refresh_mall(p, req.type)
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.VIP_PACKS_INFO)
    def vip_packs_info(self, msgtype, body):
        req = poem_pb.VipPacksInfoRequest()
        req.ParseFromString(body)
        rsp = poem_pb.VipPacksInfo()
        p = self.player
        now = int(time.time())
        today = datedate.fromtimestamp(now)
        configs = get_config(VipPacksConfig)
        if req.type == VipPackType.Daily:
            try:
                config = get_config(VipConfig)[req.vip or p.vip]
            except KeyError:
                config = get_config(VipConfig)[p.vip]
            group = [config.day_giftID]
        else:
            group = [i.ID for i in get_config(
                VipPacksByGroupConfig).get(req.type, [])]
        for each in group:
            config = configs[each]
            if config.gift_type != VipPackType.Daily:
                if now < config.gift_starttime or now > config.gift_lasttime:
                    continue
            info = dict(config._asdict())
            info["rewards"] = build_reward(parse_reward(info["rewards"]))
            #  同组共用一个限购数据
            count = get_vip_pack_rest_count(p, each, today=today)
            info["count"] = count
            rsp.packs.add(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.VIP_PACKS_BUY)
    def vip_packs_buy(self, msgtype, body):
        req = poem_pb.VipPacksBuyRequest()
        req.ParseFromString(body)
        p = self.player
        from entity.manager import save_guide
        save_guide(p, req.guide_type)  # 保存新手引导进度
        now = int(time.time())
        today = datedate.fromtimestamp(now)
        config = get_config(VipPacksConfig).get(req.ID)
        if not config:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if config.gift_type != VipPackType.Daily:
            if now < config.gift_starttime or now > config.gift_lasttime:
                return fail_msg(msgtype, msgTips.FAIL_MSG_VIP_PACKS_EXPIRED)
        rest = get_vip_pack_rest_count(p, req.ID, today=today)
        if rest != -1 and rest <= 0:
            return fail_msg(msgtype, reason="次数不足")
        if p.vip < config.vip_level:
            return fail_msg(msgtype, reason="VIP不足")
        cost = parse_reward([{
            'count': config.discount_price,
            'type': config.discount_price_type}])
        gain = parse_reward(config.rewards)
        try:
            apply_reward(p, gain, cost=cost, type=RewardType.VipPacks)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="消耗不足")
        set_vip_packs_limits(p, config.ID, now)
        p.vip_packs_today_bought_count += 1
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.BUY_SKILLPOINT)
    def buy_point(self, msgtype, body):
        p = self.player
        if not p.buy_rest_skillpoint_count:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        try:
            apply_reward(
                p, {"skillpoint": p.buy_skillpoint_gain},
                {"gold": p.buy_skillpoint_cost},
                type=RewardType.BuySkillpoint)
        except AttrNotEnoughError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        p.buy_used_skillpoint_count += 1
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.BUY_SOUL)
    def buy_soul(self, msgtype, body):
        p = self.player
        if not p.buy_rest_soul_count:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        try:
            apply_reward(
                p, {"soul": p.buy_soul_gain},
                {"gold": p.buy_soul_cost},
                type=RewardType.BuySoul)
        except AttrNotEnoughError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        p.buy_used_soul_count += 1
        p.save()
        p.sync()
        return success_msg(msgtype, "")
