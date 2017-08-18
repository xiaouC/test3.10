# coding:utf-8
import time
import calendar
import logging
logger = logging.getLogger("campaign")
from datetime import date as datedate
from datetime import datetime

from yy.rpc import RpcService
from yy.rpc import rpcmethod

from yy.message.header import success_msg
from yy.message.header import fail_msg

import protocol.poem_pb as msgid
from protocol import poem_pb

from yy.utils import weighted_random2

from config.configs import get_config
from config.configs import get_cons_value
from config.configs import WishConfig
from config.configs import WishProbConfig
from config.configs import AccRechargeConfig
# from config.configs import AccRechargeByTypeConfig
from config.configs import FundRewardConfig
from config.configs import FundRewardByTypeConfig
from config.configs import LevelPacksConfig
from config.configs import CheckInConfig
from config.configs import CheckInCostConfig
from config.configs import TimedStoreConfig
from config.configs import OnlinePacksConfig
from config.configs import DailyRechargeConfig
from config.configs import ConsumeCampaignByGroupConfig
from config.configs import ConsumeCampaignConfig
from config.configs import LoginCampaignByGroupConfig
from config.configs import LoginCampaignConfig
from config.configs import ExchangeCampaignByGroupConfig
from config.configs import PowerPacksConfig
# from config.configs import CampaignConfig
from config.configs import PetExchangeConfig
from config.configs import PetExchangeCostConfig
from config.configs import PetConfig
from config.configs import RefreshStoreByGroupConfig
from config.configs import RefreshStoreConfig
from config.configs import SeedConfig
from config.configs import SealSeedConfig
from config.configs import ArborDayYYYProbConfig
from config.configs import HandselGroupConfig
from config.configs import HandselConfig
from config.configs import HandselMulRewardGroupConfig
from config.configs import HandselMulRewardConfig
from lineup.manager import in_lineup
from lineup.constants import LineupType
from lineup.manager import save_lineup

from reward.manager import RewardType
from reward.manager import open_reward
from reward.manager import apply_reward
from reward.manager import build_reward
from reward.manager import parse_reward
from reward.manager import build_reward_msg
from reward.manager import combine_reward
from reward.manager import AttrNotEnoughError
from reward.manager import MatNotEnoughError
from reward.manager import RewardItemType

from chat.manager import on_wish

from .manager import g_campaignManager
from .manager import get_bought_fund_count
from .manager import incr_bought_fund_count
from .manager import on_fund_bought_count_change
from .manager import trigger_timed_store
from .manager import reset_check_in_monthly
from .manager import get_count_down
from .manager import count_down_next
from .manager import trigger_online_packs
from .manager import reset_online_packs
from .constants import AccRechargeType
from .constants import FundRewardType

from common import msgTips


def wish_info(p):
    configs = get_config(WishConfig)
    config = configs.get(p.wish_used_count + 1)
    if not config:
        config = configs[max(configs)]
    rsp = poem_pb.WishInfo(**config._asdict())
    return rsp


class CampaignService(RpcService):

    @rpcmethod(msgid.WISH_INFO)
    def wish_info(self, msgtype, body):
        p = self.player
        now = int(time.time())
        if not g_campaignManager.wish_campaign.is_open() and \
                now > p.wish_experience_time:
            return fail_msg(msgtype, reason="活动未开启")
        start, end = g_campaignManager.wish_campaign.get_current_time()
        if now > p.wish_experience_time:  # 因为有体验时间的存在，每个玩家重置时间略有不同
            if p.wish_last_reset_time < start or p.wish_last_reset_time > end:
                p.wish_used_count = 0
                p.wish_last_reset_time = now
                p.save()
                p.sync()
        rsp = wish_info(p)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.WISH)
    def wish(self, msgtype, body):
        p = self.player
        now = int(time.time())
        if not g_campaignManager.wish_campaign.is_open() and \
                now > p.wish_experience_time:
            return fail_msg(msgtype, reason="活动未开启")
        if not p.wish_rest_count:
            return fail_msg(msgtype, reason="次数不足")
        configs = get_config(WishConfig)
        config = configs.get(p.wish_used_count + 1)
        if not config:
            config = configs[max(configs)]
        probs = get_config(WishProbConfig)
        k = weighted_random2([[k, v.prob] for k, v in probs.items()])
        prob = probs[k]
        logger.debug("prob: %r", prob)
        amount = int(config.cost * prob.multi + config.extra)
        logger.debug(" %r * %r + %r" % (config.cost, prob.multi, config.extra))
        gain = parse_reward([{
            'count': amount,
            'type': config.cost_type}])
        cost = parse_reward([{
            'count': config.cost,
            'type': config.cost_type
        }])
        try:
            apply_reward(p, gain, cost=cost, type=RewardType.Wish)
        except AttrNotEnoughError as e:
            if e.attr == 'gold':
                return fail_msg(msgtype, reason="钻石不足")
            return fail_msg(msgtype, reason="金币不足")
        if prob.isshow and config.cost_type == RewardItemType.Gold:
            on_wish(p, gain)
        p.wish_used_count += 1
        p.save()
        p.sync()
        rsp = wish_info(p)
        rsp.result = amount
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.ACC_RECHARGE_INFO)
    def acc_recharge_info(self, msgtype, body):
        p = self.player
        req = poem_pb.AccRechargeInfoRequest()
        req.ParseFromString(body)
        logger.debug(req)
        configs = get_config(AccRechargeConfig)
        rsp = poem_pb.AccRechargeInfo()
        if req.type == AccRechargeType.Daily:
            plan = p.daily_acc_recharge_amount
            acc_recharge_rewards = p.daily_acc_recharge_rewards
            reward_configs = g_campaignManager.\
                daily_acc_recharge_campaign.get_reward_configs()
        elif req.type == AccRechargeType.Cycle:
            plan = p.cycle_acc_recharge_amount
            acc_recharge_rewards = p.cycle_acc_recharge_rewards
            reward_configs = g_campaignManager.\
                cycle_acc_recharge_campaign.get_reward_configs()
        elif req.type == AccRechargeType.Weeks:
            plan = p.weeks_acc_recharge_amount
            acc_recharge_rewards = p.weeks_acc_recharge_rewards
            reward_configs = g_campaignManager.\
                weeks_acc_recharge_campaign.get_reward_configs()
        elif req.type == AccRechargeType.Month:
            plan = p.month_acc_recharge_amount
            acc_recharge_rewards = p.month_acc_recharge_rewards
            reward_configs = g_campaignManager.\
                month_acc_recharge_campaign.get_reward_configs()
        else:
            raise NotImplementedError
        for each in reward_configs:
            config = configs.get(each.ID)
            if not config:
                continue
            info = config._asdict()
            info["rewards"] = build_reward(
                parse_reward(config.rewards))
            # ugly TODO
            if acc_recharge_rewards and config.ID in acc_recharge_rewards:
                state = poem_pb.AccRechargeItem.AccRechargeItemStateFinish
            elif plan >= config.gold:
                state = poem_pb.AccRechargeItem.AccRechargeItemStateEnding
            else:
                state = poem_pb.AccRechargeItem.AccRechargeItemStateNormal
            info["state"] = state
            rsp.items.add(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.RECV_ACC_RECHARGE_REWARD)
    def recv_acc_recharge_reward(self, msgtype, body):
        p = self.player
        req = poem_pb.RecvAccRechargeRewardRequest()
        req.ParseFromString(body)
        logger.debug(req)
        configs = get_config(AccRechargeConfig)
        config = configs.get(req.ID)
        if not config:
            return fail_msg(msgtype, reason="不存在的奖励")
        if config.type == AccRechargeType.Daily:
            attr = "daily_acc_recharge_rewards"
        elif config.type == AccRechargeType.Cycle:
            attr = "cycle_acc_recharge_rewards"
        elif config.type == AccRechargeType.Weeks:
            attr = "weeks_acc_recharge_rewards"
        elif config.type == AccRechargeType.Month:
            attr = "month_acc_recharge_rewards"
        else:
            raise NotImplementedError
        if not getattr(p, attr) or req.ID not in getattr(p, attr):
            return fail_msg(msgtype, reason="没有达成条件，不能领取这个奖励")
        gain = parse_reward(config.rewards)
        apply_reward(p, gain, type=RewardType.AccRechargeReward)
        acc_recharge_rewards = getattr(p, attr)
        acc_recharge_rewards.remove(req.ID)
        setattr(p, attr, acc_recharge_rewards)
        p.save()
        p.sync()
        rsp = poem_pb.RecvAccRechargeRewardResponse()
        rsp.more = False
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FUND_INFO)
    def fund_info(self, msgtype, body):
        req = poem_pb.FundInfoRequest()
        req.ParseFromString(body)
        type = req.type or FundRewardType.Open
        types = get_config(FundRewardByTypeConfig).get(type, [])
        configs = get_config(FundRewardConfig)
        p = self.player
        rsp = poem_pb.FundInfo()
        rsp.vip = get_cons_value("BuyFundNeedVip")
        rsp.gold = get_cons_value("BuyFundNeedGold")
        rsp.count = get_bought_fund_count()
        if type == FundRewardType.Open:
            plan = p.level
            flag = p.fund_bought_flag  # 需要购买才能领取
        else:
            plan = rsp.count
            flag = True  # 不需要购买也能领取
        for each in types:
            config = configs[each.ID]
            info = config._asdict()
            info["rewards"] = build_reward(
                parse_reward(config.rewards))
            if flag and config.ID in p.fund_rewards_received:
                state = poem_pb.FundRewardItem.FundRewardItemStateEnding
            elif flag and plan >= config.parm:
                state = poem_pb.FundRewardItem.FundRewardItemStateFinish
            else:
                state = poem_pb.FundRewardItem.FundRewardItemStateNormal
            info["state"] = state
            rsp.items.add(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.RECV_FUND_REWARD)
    def recv_fund_reward(self, msgtype, body):
        req = poem_pb.RecvFundRewardRequest()
        req.ParseFromString(body)
        p = self.player
        configs = get_config(FundRewardConfig)
        config = configs.get(req.ID)
        if not config:
            return fail_msg(msgtype, reason="没有这个奖励")
        if req.ID in p.fund_rewards_received:
            return fail_msg(msgtype, reason="已经领取过这个奖励了")
        if config.type == FundRewardType.Open:
            plan = p.level
        else:
            plan = get_bought_fund_count()
        if plan < config.parm:
            return fail_msg(msgtype, reason="没有达成可以领取的条件")
        gain = parse_reward(config.rewards)
        apply_reward(p, gain, type=RewardType.FundReward)
        p.fund_rewards_received.add(req.ID)
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.BUY_FUND)
    def buy_fund(self, msgtype, body):
        p = self.player
        if p.fund_bought_flag:
            return fail_msg(msgtype, reason="已经购买过开服基金了")
        gold = get_cons_value("BuyFundNeedGold")
        try:
            apply_reward(p, {}, cost={"gold": gold}, type=RewardType.BuyFund)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="钻石不足")
        p.fund_bought_flag = True
        p.save()
        p.sync()
        origin = get_bought_fund_count()
        current = incr_bought_fund_count()
        on_fund_bought_count_change(origin, current)
        return self.fund_info(msgtype, body)

    @rpcmethod(msgid.LEVEL_PACKS_INFO)
    def level_packs_info(self, msgtype, body):
        p = self.player
        configs = get_config(LevelPacksConfig)
        rsp = poem_pb.LevelPacksInfo()
        for _, config in configs.items():
            info = config._asdict()
            if config.id in p.level_packs_end:
                state = poem_pb.LevelPacksItem.LevelPacksItemStateEnding
            elif config.id in p.level_packs_done:
                state = poem_pb.LevelPacksItem.LevelPacksItemStateFinish
            else:
                state = poem_pb.LevelPacksItem.LevelPacksItemStateNormal
            info["state"] = state
            rsp.items.add(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.LEVEL_PACKS_RECV)
    def level_packs_recv(self, msgtype, body):
        req = poem_pb.LevelPacksRecv()
        req.ParseFromString(body)
        p = self.player
        if req.id not in p.level_packs_done:
            return fail_msg(msgtype, reason="无法领取")
        packs = get_config(LevelPacksConfig)
        pack = packs.get(req.id)
        if not pack:
            return fail_msg(msgtype, reason="无法领取")
        reward = open_reward(RewardType.LevelPacks, pack.drop)
        reward.apply(p)
        p.level_packs_end.add(req.id)
        p.level_packs_done.remove(req.id)
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.CHECK_IN_INFO)
    def check_in_info(self, msgtype, body):
        date = datedate.today()
        configs = get_config(CheckInConfig)
        config = configs[date.day]
        index = (date.month - 1) % len(config.rewards)
        rsp = poem_pb.CheckInInfo()
        _, mr = calendar.monthrange(date.year, date.month)
        cost_configs = get_config(CheckInCostConfig)
        for day, (k, config) in enumerate(configs.items()[:mr], 1):
            info = {}
            reward = config.rewards[index]
            info["rewards"] = build_reward(
                parse_reward([reward]))
            info["vip"] = config.vips[index]
            cost = cost_configs.get(day)
            if cost:
                info["cost"] = cost.gold
            else:
                info["cost"] = get_cons_value("CheckInMakeUpCost")
            rsp.items.add(**info)
        # rsp.cost = get_cons_value("CheckInMakeUpCost")
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CHECK_IN)
    def check_in(self, msgtype, body):
        p = self.player
        if p.check_in_today and not p.check_in_rest_count:
            return fail_msg(msgtype, reason="已经签到过，且不能补签了")
        if not p.check_in_today:
            cost = {}
        else:
            cost_configs = get_config(CheckInCostConfig)
            cost = cost_configs.get(p.check_in_used_count + 1)
            if cost:
                gold = cost.gold
            else:
                gold = get_cons_value("CheckInMakeUpCost")
            cost = {"gold": gold}
        configs = get_config(CheckInConfig)
        config = configs[p.check_in_used_count + 1]
        date = datedate.today()
        index = (date.month - 1) % len(config.rewards)
        vip = config.vips[index]
        reward = config.rewards[index]
        if vip == -1 or p.vip < vip:
            reward = parse_reward([reward])
        else:
            reward = combine_reward([reward], [reward])
        try:
            apply_reward(p, reward, cost=cost, type=RewardType.CheckInMakeUp)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="钻石不足")
        reset_check_in_monthly(p)
        p.check_in_today = True
        p.check_in_used_count += 1
        p.check_in_last_time = datetime.now()
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.TIMED_STORE_INFO)
    def timed_store_info(self, msgtype, body):
        p = self.player
        now = datetime.now()
        timestamp = time.mktime(now.timetuple())
        if p.timed_store_cd < timestamp:
            return fail_msg(msgtype, reason="限时商店未开启")
        configs = get_config(TimedStoreConfig)
        if not p.timed_store_id or p.timed_store_id not in configs:
            return fail_msg(msgtype, reason="没有这个商店")
        config = configs[p.timed_store_id]
        info = config._asdict()
        rsp = poem_pb.TimedStoreInfo(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.TIMED_STORE_BUY)
    def timed_store_buy(self, msgtype, body):
        p = self.player
        now = datetime.now()
        timestamp = time.mktime(now.timetuple())
        if p.timed_store_cd < timestamp:
            return fail_msg(msgtype, reason="限时商店未开启")
        configs = get_config(TimedStoreConfig)
        if not p.timed_store_id or p.timed_store_id not in configs:
            return fail_msg(msgtype, reason="没有这个商店")
        config = configs[p.timed_store_id]
        rewards = parse_reward(config.rewards)
        cost = {"gold": config.cost}
        try:
            apply_reward(p, rewards, cost=cost, type=RewardType.TimedStore)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="钻石不足")
        trigger_timed_store(p, now=now)
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.MONTHLY_CARD_INFO)
    def monthly_card_info(self, msgtype, body):
        reward = open_reward(
            RewardType.MonthlyCard, get_cons_value("MonthlyCardDropID"))
        result = reward.apply_after()
        rsp = poem_pb.MonthlyCardInfo()
        rsp.need = get_cons_value("MonthlyCardAccAmount")
        rsp.gold = result.get("gold", 0)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.RECV_MONTHLY_CARD)
    def recv_monthly_card(self, msgtype, body):
        p = self.player
        if not p.monthly_card:
            return fail_msg(msgtype, reason="没有激活月卡")
        if p.monthly_card_received:
            return fail_msg(msgtype, reason="已经领取月卡奖励了")
        reward = open_reward(
            RewardType.MonthlyCard, get_cons_value("MonthlyCardDropID"))
        result = reward.apply(p)
        p.monthly_card_received = True
        p.save()
        p.sync()
        rsp = poem_pb.RecvMonthlyCard()
        build_reward_msg(rsp, result)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.REWARD_CAMPAIGN_INFO)
    def reward_campaign_info(self, msgtype, body):
        rsp = poem_pb.RewardCampaignInfo()
        from campaign.manager import g_campaignManager
        for camp in g_campaignManager.reward_campaigns:
            rsp.items.add(
                opened=camp.is_open(),
                desc=camp.get_campaign_desc())
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.COUNT_DOWN_INFO)
    def count_down_info(self, msgtype, body):
        p = self.player
        config = get_count_down(p)
        if not config:
            return fail_msg(msgtype, reason="没有下一个了")
        info = config._asdict()
        rsp = poem_pb.CountDownInfo(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.COUNT_DOWN_RECV)
    def count_down_recv(self, msgtype, body):
        p = self.player
        p.count_down_time
        now = int(time.time())
        if now < p.count_down_cd:
            return fail_msg(msgtype, reason="还不能领取")
        config = get_count_down(p)
        if not config:
            return fail_msg(msgtype, reason="没有下一个了")
        apply_reward(
            p, parse_reward(config.rewards),
            type=RewardType.CountDown)
        count_down_next(p)
        p.save()
        p.sync()
        next = get_count_down(p)
        info = {}
        if next:
            info = config._asdict()
        rsp = poem_pb.CountDownInfo(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.ONLINE_PACKS_INFO)
    def online_packs_info(self, msgtype, body):
        p = self.player
        config = get_config(OnlinePacksConfig)[p.online_packs_index]
        rsp = poem_pb.OnlinePacksInfo()
        build_reward_msg(rsp, parse_reward(config.rewards))
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.ONLINE_PACKS_RECV)
    def online_packs_recv(self, msgtype, body):
        now = int(time.time())
        p = self.player
        config = get_config(OnlinePacksConfig)[p.online_packs_index]
        if now < p.online_packs_cd:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        result = apply_reward(
            p,
            parse_reward(config.rewards),
            type=RewardType.OnlinePacks)
        rsp = poem_pb.OnlinePacksRecv()
        build_reward_msg(rsp, result)
        p.online_packs_index += 1
        is_last = not trigger_online_packs(p, now=now)
        if is_last:
            p.online_packs_done = True
        triggered = reset_online_packs(p, refresh=True)
        if triggered:
            is_last = False
        rsp.is_last = is_last
        p.online_packs_last_recv = now
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DAILY_RECHARGE_INFO)
    def daily_recharge_info(self, msgtype, body):
        p = self.player
        configs = g_campaignManager.daily_recharge_campaign.\
            get_reward_configs()
        rsp = poem_pb.DailyRechargeInfo()
        for config in configs:
            info = config._asdict()
            used = p.daily_recharge_useds.get(config.id, 0)
            info["used"] = used
            info["can_receive"] = config.id in p.daily_recharge_rewards
            rsp.items.add(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DAILY_RECHARGE_RECV)
    def recv_daily_recharge_reward(self, msgtype, body):
        p = self.player
        req = poem_pb.RecvDailyRechargeRequest()
        req.ParseFromString(body)
        config = get_config(DailyRechargeConfig).get(req.id)
        if not config or req.id not in p.daily_recharge_rewards:
            return fail_msg(msgtype, reason="不存在的奖励")
        gain = parse_reward(config.rewards)
        apply_reward(p, gain, type=RewardType.DailyRechargeReward)
        p.daily_recharge_rewards.remove(req.id)
        p.touch_daily_recharge_rewards()
        rsp = poem_pb.RecvDailyRechargeResponse()
        rsp.more = req.id in p.daily_recharge_rewards
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.PET_EXCHANGE_INFO)
    def recv_pet_exchange_info(self, msgtype, body):
        if not g_campaignManager.pet_exchange_campaign.is_open():
            return fail_msg(msgtype, reason="活动未开启")
        config = g_campaignManager.pet_exchange_campaign.get_current()
        if not config:
            return fail_msg(msgtype, reason="不存在的精灵兑换配置")
        rsp = poem_pb.PetExchangeInfoResponse()
        rsp.open_type = config.group
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.PET_EXCHANGE)
    def recv_pet_exchange(self, msgtype, body):
        if not g_campaignManager.pet_exchange_campaign.is_open():
            return fail_msg(msgtype, reason="活动未开启")
        p = self.player
        req = poem_pb.PetExchangeRequest()
        req.ParseFromString(body)
        config = get_config(PetExchangeConfig)
        pet_configs = get_config(PetConfig)
        cost_configs = get_config(PetExchangeCostConfig)
        rsp = poem_pb.PetExchangeResponse()
        cost = {}
        gain = {"petList": []}
        origin = p.free_pet_exchange
        pets = []
        for pet_id in req.pets:
            pet = p.pets[pet_id]
            pet_class = pet_configs.get(pet.prototypeID).cls
            cost_config = cost_configs.get(pet_class)
            if not cost_config:
                return fail_msg(msgtype, reason="没有这个精灵")
            if in_lineup(p, pet):
                if not in_lineup(p, pet, type=LineupType.ATK):
                    return fail_msg(msgtype, reason="精灵还在阵上哦！")
            pets.append(pet)
        sorted_pets = sorted(
            pets, reverse=True,
            key=lambda s: pet_configs.get(s.prototypeID).cls)
        for pet in sorted_pets:
            pet_class = pet_configs.get(pet.prototypeID).cls
            units_id = 0
            if req.exchange_type != 4:
                samples = []
                for k, v in config.items():
                    if v.cla == pet_class and v.attr == req.exchange_type:
                        samples.append([v.units_id, v.prob])
                units_id = weighted_random2(samples)
            else:
                samples = []
                for k, v in config.items():
                    if v.cla == pet_class:
                        samples.append([v.units_id, v.prob])
                units_id = weighted_random2(samples)
            if p.free_pet_exchange > 0:
                p.free_pet_exchange -= 1
            else:
                cost_config = cost_configs[pet_class]
                combine_reward(
                    parse_reward([{
                        "type": cost_config.type,
                        "count": cost_config.cost}
                    ]), {}, cost)
            gain["petList"].append([units_id, 1])
        extra = {}
        try:
            apply_reward(
                p, gain, cost, type=RewardType.PetExchange, extra=extra)
        except AttrNotEnoughError:
            p.free_pet_exchange = origin
            return fail_msg(msgtype, reason="消耗不足")
        extra_pets = extra.get("pets", [])
        for pp in extra_pets:
            pet_id = pp.entityID
            pet_exchange = poem_pb.PetExchange()
            pet_exchange.pet_id = pet_id
            pet_exchange.config_id = pp.prototypeID
            rsp.pets.append(pet_exchange)
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
        p.save()
        p.sync()
        from chat.manager import on_pet_exchange1
        on_pet_exchange1(p, extra_pets)
        from chat.manager import on_pet_exchange2
        on_pet_exchange2(p, extra_pets)
        from chat.manager import on_pet_exchange3
        on_pet_exchange3(p, extra_pets)
        from chat.manager import on_pet_exchange4
        on_pet_exchange4(p, extra_pets)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.MAT_EXCHANGE_INFO)
    def mat_exchange_info(self, msgtype, body):
        from campaign.manager import g_campaignManager
        from config.configs import get_config
        from config.configs import MatExchangeConfig
        from config.configs import MatExchangeByGroupConfig
        campaign = g_campaignManager.mat_exchange_campaign
        if not campaign.is_open():
            return fail_msg(msgtype, reason="活动未开启")
        current = campaign.get_current()
        configs = get_config(MatExchangeConfig)
        groups = get_config(MatExchangeByGroupConfig).get(current.group)
        configs = [configs[i.ID] for i in groups]
        rsp = poem_pb.MatExchangeInfo()
        p = self.player
        for config in configs:
            used = p.mat_exchange_limits.get(config.ID, 0)
            rsp.items.add(
                id=config.ID,
                rewards=config.rewards,
                count=config.count,
                rest=max(config.count - used, 0),
            )
        rsp.bg = current.bg
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.MAT_EXCHANGE)
    def mat_exchange(self, msgtype, body):
        from config.configs import get_config
        from config.configs import MatExchangeConfig
        req = poem_pb.MatExchangeRequest()
        req.ParseFromString(body)
        config = get_config(MatExchangeConfig).get(req.id)
        if not config:
            return fail_msg(msgtype, reason="没有这一项")
        p = self.player
        try:
            apply_reward(
                p, parse_reward(config.rewards[1:]),
                parse_reward([config.rewards[0]]),
                type=RewardType.MatExchange)
        except (AttrNotEnoughError, MatNotEnoughError):
            return fail_msg(msgtype, reason="道具不足")
        count = p.mat_exchange_limits.get(req.id, 0)
        p.mat_exchange_limits[req.id] = count + 1
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.LOGIN_CAMPAIGN_INFO)
    def login_campaign_info(self, msgtype, body):
        camp = g_campaignManager.login_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")
        p = self.player
        current = camp.get_current()
        group = get_config(
            LoginCampaignByGroupConfig).get(current.group)
        configs = get_config(LoginCampaignConfig)
        configs = sorted(
            [configs[i.ID] for i in group], key=lambda s: s.day)
        rsp = poem_pb.LoginCampaignInfo()
        rsp.tip = current.bg
        for config in configs:
            item = rsp.items.add(**config._asdict())
            if p.login_campaign_amount >= config.day:
                if config.ID in p.login_campaign_rewards:
                    state = 1  # 可领取
                else:
                    state = 2  # 已领取
            else:
                state = 0
            item.state = state
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.LOGIN_CAMPAIGN_RECV)
    def login_campaign_recv(self, msgtype, body):
        camp = g_campaignManager.login_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")
        req = poem_pb.LoginCampaignRecv()
        req.ParseFromString(body)
        p = self.player
        if req.ID not in p.login_campaign_rewards:
            return fail_msg(msgtype, reason="没有这个奖励")
        config = get_config(LoginCampaignConfig).get(req.ID)
        if not config:
            return fail_msg(msgtype, reason="无效的ID")
        apply_reward(
            p, parse_reward(config.rewards),
            type=RewardType.LoginCampaign)
        p.login_campaign_rewards.remove(req.ID)
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.CONSUME_CAMPAIGN_INFO)
    def consume_campaign_info(self, msgtype, body):
        camp = g_campaignManager.consume_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")
        p = self.player
        current = camp.get_current()
        group = get_config(
            ConsumeCampaignByGroupConfig).get(current.group)
        configs = get_config(ConsumeCampaignConfig)
        configs = sorted(
            [configs[i.ID] for i in group], key=lambda s: s.consume)
        rsp = poem_pb.ConsumeCampaignInfo()
        rsp.consume_type = current.reward_group
        rsp.tip = current.bg
        for config in configs:
            item = rsp.items.add(**config._asdict())
            if p.consume_campaign_amount >= config.consume:
                if config.ID in p.consume_campaign_rewards:
                    state = 1  # 可领取
                else:
                    state = 2  # 已领取
            else:
                state = 0
            item.state = state
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CONSUME_CAMPAIGN_RECV)
    def consume_campaign_recv(self, msgtype, body):
        camp = g_campaignManager.consume_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")
        req = poem_pb.ConsumeCampaignRecv()
        req.ParseFromString(body)
        p = self.player
        if req.ID not in p.consume_campaign_rewards:
            return fail_msg(msgtype, reason="没有这个奖励")
        config = get_config(ConsumeCampaignConfig).get(req.ID)
        if not config:
            return fail_msg(msgtype, reason="无效的ID")
        apply_reward(
            p, parse_reward(config.rewards),
            type=RewardType.ConsumeCampaign)
        p.consume_campaign_rewards.remove(req.ID)
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.POWER_PACKS_INFO)
    def power_packs_info(self, msgtype, body):
        p = self.player
        configs = get_config(PowerPacksConfig)
        rsp = poem_pb.PowerPacksInfo()
        for _, config in configs.items():
            info = config._asdict()
            if config.id in p.power_packs_end:
                state = poem_pb.PowerPacksItem.PowerPacksItemStateEnding
            elif config.id in p.power_packs_done:
                state = poem_pb.PowerPacksItem.PowerPacksItemStateFinish
            else:
                state = poem_pb.PowerPacksItem.PowerPacksItemStateNormal
            info["state"] = state
            rsp.items.add(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.POWER_PACKS_RECV)
    def power_packs_recv(self, msgtype, body):
        req = poem_pb.PowerPacksRecv()
        req.ParseFromString(body)
        p = self.player
        if req.id not in p.power_packs_done:
            return fail_msg(msgtype, reason="无法领取")
        packs = get_config(PowerPacksConfig)
        pack = packs.get(req.id)
        if not pack:
            return fail_msg(msgtype, reason="无法领取")
        apply_reward(
            p, parse_reward(pack.rewards),
            type=RewardType.PowerPacks)
        p.power_packs_end.add(req.id)
        p.power_packs_done.remove(req.id)
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.EXCHANGE_CAMPAIGN_INFO)
    def exchange_campaign_info(self, msgtype, body):
        camp = g_campaignManager.exchange_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")
        current = camp.get_current()
        group = get_config(ExchangeCampaignByGroupConfig).get(current.group)
        rsp = poem_pb.ExchangeCampaignInfo()
        rsp.sourcePrototypeID = group.srcID
        rsp.targetPrototypeID = group.targetID
        rsp.desc = current.bg       # 活动描述
        rsp.bg = group.bg           # 活动使用的图片
        for config in group.consumes:
            rsp.mats.append(config)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.EXCHANGE_CAMPAIGN_REQUEST)
    def exchange_campaign_recv(self, msgtype, body):
        camp = g_campaignManager.exchange_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")
        req = poem_pb.ExchageCampaignRequest()
        req.ParseFromString(body)

        pet = self.player.pets.get(req.hero_id)
        if not pet:
            return fail_msg(msgtype, reason='找不到置换的精灵')

        pet_config_list = get_config(PetConfig)
        pet_config = pet_config_list[pet.prototypeID]

        current = camp.get_current()
        group = get_config(ExchangeCampaignByGroupConfig).get(current.group)
        src_pet_config = pet_config_list[group.srcID]

        if pet_config.same != src_pet_config.same:
            return fail_msg(msgtype, reason='这个精灵不能置换')

        star_count = pet.star / pet_config.need_patch

        matList = []
        for tmp_config in group.consumes:
            need_count = tmp_config["count"] * star_count
            count = self.player.mats.get(tmp_config["arg"], 0)
            if count < need_count:
                return fail_msg(msgtype, reason='置换材料不足')

            matList.append([tmp_config["arg"], need_count])

        new_config_id = group.targetID
        new_pet_config = pet_config_list[new_config_id]
        while True:
            if not new_pet_config:
                return fail_msg(msgtype, reason='错误的精灵')

            if new_pet_config.rarity == pet_config.rarity and new_pet_config.step == pet_config.step:
                break

            new_config_id = new_pet_config.gupr
            new_pet_config = pet_config_list[new_config_id]

        pet.prototypeID = new_config_id

        add_star_count = pet.add_star / pet_config.need_patch
        pet.add_star = new_pet_config.need_patch * add_star_count

        apply_reward(self.player, {}, cost={"matList": matList}, type=RewardType.ExchageCampaign)

        pet.save()
        pet.sync()
        self.player.save()
        self.player.sync()

        return success_msg(msgtype, "")

    @rpcmethod(msgid.REFRESH_STORE_CAMPAIGN_INFO)
    def refresh_store_campaign_info(self, msgtype, body):
        camp = g_campaignManager.refresh_store_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")

        current = camp.get_current()
        groups = get_config(RefreshStoreByGroupConfig).get(current.group)
        configs = get_config(RefreshStoreConfig)
        configs = [configs[i.ID] for i in groups]

        rsp = poem_pb.RefreshStoreInfo()
        rsp.desc = current.bg       # 活动描述
        for config in configs:
            item = {}
            item["ID"] = config.ID
            item["count"] = config.count
            item["rewards"] = build_reward(parse_reward(config.rewards))
            if config.ID in self.player.refresh_reward_end:
                item["state"] = poem_pb.RefreshRewardItem.RefreshRewardItemStateEnding
            elif config.ID in self.player.refresh_reward_done:
                item["state"] = poem_pb.RefreshRewardItem.RefreshRewardItemStateFinish
            else:
                item["state"] = poem_pb.RefreshRewardItem.RefreshRewardItemStateNormal
            rsp.items.add(**item)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.REFRESH_STORE_CAMPAIGN_RECV)
    def refresh_store_recv(self, msgtype, body):
        req = poem_pb.RefreshStoreRecv()
        req.ParseFromString(body)
        p = self.player
        if req.ID not in p.refresh_reward_done:
            return fail_msg(msgtype, reason="无法领取")
        packs = get_config(RefreshStoreConfig)
        pack = packs.get(req.ID)
        if not pack:
            return fail_msg(msgtype, reason="无法领取")

        apply_reward(p, parse_reward(pack.rewards), type=RewardType.RefreshStoreCampaign)
        p.refresh_reward_end.add(req.ID)
        p.refresh_reward_done.remove(req.ID)
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.ARBOR_DAY_CAMPAIGN_YYY)
    def arbor_day_yyy_recv(self, msgtype, body):
        camp = g_campaignManager.arbor_day_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")

        p = self.player
        if p.shake_tree_used_count >= p.shake_tree_max_count:
            return fail_msg(msgtype, reason="今天摇树的次数已经用完了")

        import random
        start_time, end_time = camp.get_current_time()
        if p.shake_tree_prob_campaign_last_time < start_time or p.shake_tree_prob_campaign_last_time > end_time:
            yyy_configs = get_config(ArborDayYYYProbConfig)
            yyy_configs = [ID for ID in yyy_configs]
            prob_index = random.randint(0, len(yyy_configs)-1)
            p.shake_tree_prob_id = yyy_configs[prob_index]
            p.shake_tree_reward_free_next_index = 0
            p.shake_tree_reward_pay_next_index = 0

        p.shake_tree_prob_campaign_last_time = int(time.time())

        is_free = p.shake_tree_used_count < p.shake_tree_free_count
        cost = {}
        if not is_free:
            combine_reward(
                parse_reward([{
                    "type": 2,
                    "count": p.shake_tree_cost}
                    ]), {}, cost)

        index, rewards = camp.randomYYY(p, is_free)

        p.shake_tree_used_count = p.shake_tree_used_count + 1

        rsp = poem_pb.ArborDayYYYResponse()
        rsp.index = index
        for reward in rewards:
            r = {}
            r["type"] = reward["type"]
            r["arg"] = reward["arg"]
            r["count"] = reward["count"]
            rsp.rewards.add(**r)

        try:
            apply_reward(p, parse_reward(rewards), cost, type=RewardType.ArborDayYYYCampaign)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="钻石不足")

        p.save()
        p.sync()

        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SEED_CROP)
    def seed_crop(self, msgtype, body):
        camp = g_campaignManager.seed_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")

        p = self.player
        if p.seed_state != poem_pb.SeedStateNormal:
            return fail_msg(msgtype, reason="已经种植了")

        req = poem_pb.SeedCropRequest()
        req.ParseFromString(body)

        count = self.player.mats.get(req.seedID, 0)
        if count <= 0:
            return fail_msg(msgtype, reason="材料不足")

        config = get_config(SeedConfig).get(req.seedID)
        if not config:
            return fail_msg(msgtype, reason="这个种子当前不能种植")

        now = int(time.time())

        # 初始化封印种子的随机索引
        import random
        start_time, end_time = camp.get_current_time()
        if p.seal_seed_prob_campaign_last_time < start_time or p.seal_seed_prob_campaign_last_time > end_time:
            ss_configs = get_config(SealSeedConfig)
            ss_configs = [ID for ID in ss_configs]
            prob_index = random.randint(0, len(ss_configs)-1)
            p.seal_seed_prob_id = ss_configs[prob_index]
            p.seal_seed_reward_next_index = 0
            p.seal_seed_prob_campaign_last_time = now

        matList = []
        matList.append([req.seedID, 1])

        apply_reward(p, {}, cost={"matList": matList}, type=RewardType.SeedCropCampaign)
        p.seed_state = poem_pb.SeedStateSeed
        p.seed_id = req.seedID

        def random_index(index_list, length):
            tmp_index = str(random.randint(0, length-1))
            if tmp_index not in index_list:
                index_list.append(tmp_index)
            else:
                random_index(index_list, length)

        if len(config.rewards) >= 6:
            index_list = []
            random_index(index_list, len(config.rewards)/2)
            random_index(index_list, len(config.rewards)/2)
            random_index(index_list, len(config.rewards)/2)
            p.seed_reward_index = "|".join(index_list)
        elif len(config.rewards) == 4:  # 封印种子
            ss_configs = get_config(SealSeedConfig).get(p.seal_seed_prob_id)
            r_index = ss_configs.probs[p.seal_seed_reward_next_index]
            if not r_index:
                r_index = 0
            p.seal_seed_reward_next_index += 1
            p.seed_reward_index = str(r_index)
        else:
            index_list = []
            random_index(index_list, len(config.rewards)/2)
            p.seed_reward_index = "|".join(index_list)

        p.seed_state_last_change_time = now
        p.seed_state_next_change_time = int(time.time()) + config.times[0]
        p.seed_state_plant_time = now
        p.seed_state_ripening_time = now + config.times[0] + config.times[1] + config.times[2]

        p.save()
        p.sync()

        return success_msg(msgtype, "")

    @rpcmethod(msgid.SEED_WATERING)
    def seed_watering(self, msgtype, body):
        import time

        camp = g_campaignManager.seed_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")

        p = self.player
        if p.seed_state == poem_pb.SeedStateNormal:
            return fail_msg(msgtype, reason="没有种植任何种植，不能浇水")

        if p.seed_state == poem_pb.SeedStateRipening:
            return fail_msg(msgtype, reason="已经成熟，不需要浇水")

        if p.seed_state == poem_pb.SeedStateRoot:
            return fail_msg(msgtype, reason="已经收割，不需要浇水")

        if p.watering_used_count >= p.watering_max_count:
            return fail_msg(msgtype, reason="浇水次数不足，无法浇水")

        if p.watering_time - int(time.time()) > 0:
            return fail_msg(msgtype, reason="浇水 CD 中，无法浇水")

        reduce_cd_time = get_cons_value("WateringReduceCD")
        p.seed_state_next_change_time -= reduce_cd_time
        p.seed_state_ripening_time -= reduce_cd_time
        p.watering_time = int(time.time()) + get_cons_value("WateringCD")
        p.watering_used_count += 1

        rsp = camp.checkWaterWormReward(p)
        camp.updateSeedState(p)

        p.save()
        p.sync()

        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SEED_WORMING)
    def seed_worming(self, msgtype, body):
        import time

        camp = g_campaignManager.seed_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")

        p = self.player
        if p.seed_state == poem_pb.SeedStateNormal:
            return fail_msg(msgtype, reason="没有种植任何种植，不能除虫")

        if p.seed_state == poem_pb.SeedStateRipening:
            return fail_msg(msgtype, reason="已经成熟，不需要除虫")

        if p.seed_state == poem_pb.SeedStateRoot:
            return fail_msg(msgtype, reason="已经收割，不需要除虫")

        if p.worming_used_count >= p.worming_max_count:
            return fail_msg(msgtype, reason="除虫次数不足，无法除虫")

        if p.worming_time - int(time.time()) > 0:
            return fail_msg(msgtype, reason="除虫 CD 中，无法除虫")

        reduce_cd_time = get_cons_value("WormingReduceCD")
        p.seed_state_next_change_time -= reduce_cd_time
        p.seed_state_ripening_time -= reduce_cd_time
        p.worming_time = int(time.time()) + get_cons_value("WormingCD")
        p.worming_used_count += 1

        rsp = camp.checkWaterWormReward(p)
        camp.updateSeedState(p)

        p.save()
        p.sync()

        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SEED_REAP)
    def seed_reap(self, msgtype, body):
        camp = g_campaignManager.seed_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")

        p = self.player
        if p.seed_state != poem_pb.SeedStateRipening:
            return fail_msg(msgtype, reason="无法收割")

        req = poem_pb.SeedReapRequest()
        req.ParseFromString(body)

        reward_index = req.index

        config = get_config(SeedConfig).get(p.seed_id)
        length = len(config.rewards)
        if reward_index < 0 or reward_index >= length / 2:
            return fail_msg(msgtype, reason="选择的索引错误")

        p.seed_state = poem_pb.SeedStateRoot
        p.clean_reward_index = reward_index + length / 2

        apply_reward(p, parse_reward([config.rewards[reward_index]]), type=RewardType.SeedReapCampaign)

        p.save()
        p.sync()

        return success_msg(msgtype, "")

    @rpcmethod(msgid.SEED_CLEAN)
    def seed_clean(self, msgtype, body):
        camp = g_campaignManager.seed_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")

        p = self.player
        if p.seed_state != poem_pb.SeedStateRoot:
            return fail_msg(msgtype, reason="无法清理")

        config = get_config(SeedConfig).get(p.seed_id)
        if not config:
            return fail_msg(msgtype, reason="无法清理")

        length = len(config.rewards)
        if p.clean_reward_index < length / 2 or p.clean_reward_index >= length:
            return fail_msg(msgtype, reason="索引错误")

        p.seed_id = 0
        p.seed_state = poem_pb.SeedStateNormal

        reward = config.rewards[p.clean_reward_index]
        apply_reward(p, parse_reward([reward]), type=RewardType.SeedCleanCampaign)

        rsp = poem_pb.SeedCleanResponse()
        rsp.rewards.add(**reward)

        p.save()
        p.sync()

        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CHECK_SEED_STATE)
    def check_seed_state(self, msgtype, body):
        if g_campaignManager.seed_campaign.is_open():
            g_campaignManager.seed_campaign.updateSeedState(self.player)
            self.player.save()
            self.player.sync()

        return success_msg(msgtype, "")

    @rpcmethod(msgid.HANDSEL_CAMPAIGN_INFO)
    def handsel_campaign_info(self, msgtype, body):
        camp = g_campaignManager.handsel_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")

        current = camp.get_current()
        groups = get_config(HandselGroupConfig).get(current.group)
        configs = get_config(HandselConfig)
        configs = [configs[i.ID] for i in groups]

        mr_configs = get_config(HandselMulRewardConfig)

        mr_id = int(float(camp.get_mulreward_id(None)))
        mr_config = mr_configs[mr_id]
        mr_next_config = None
        if mr_config.next_id != 0:
            mr_next_config = mr_configs[mr_config.next_id]
        if not mr_next_config:
            mr_next_config = mr_config

        start_time, end_time = camp.get_current_time()
        if self.player.handsel_campaign_last_time < start_time or self.player.handsel_campaign_last_time > end_time:
            self.player.handsel_campaign_counter = 0
            self.player.save()
            self.player.sync()

        rsp = poem_pb.HandselCampaignInfo()
        rsp.personal_count = self.player.handsel_campaign_counter
        rsp.total_count = int(float(camp.get_counter()))
        rsp.next_lv_count = mr_next_config.need_count
        rsp.reward_multiple = int(mr_config.mulreward * 100)
        rsp.next_reward_multiple = int(mr_next_config.mulreward * 100)
        for config in configs:
            item = {}
            item["item_id"] = config.ID
            item["cost_type"] = {}
            item["cost_type"]["type"] = config.cost_type[0]
            item["cost_type"]["arg"] = config.cost_type[1]
            item["cost_type"]["count"] = config.cost_type[2]
            item["camp_count"] = config.camp_count
            rsp.items.add(**item)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.HANDSEL_CAMPAIGN_SEND)
    def handsel_campaign_send(self, msgtype, body):
        camp = g_campaignManager.handsel_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")

        req = poem_pb.HandselOperation()
        req.ParseFromString(body)
        config = get_config(HandselConfig).get(req.item_id)
        if not config:
            return fail_msg(msgtype, reason="赠送错误")

        cost = parse_reward([{
            'type': config.cost_type[0],
            'arg': config.cost_type[1],
            'count': config.cost_type[2] * req.count,
        }])

        try:
            apply_reward(self.player, {}, cost=cost, type=RewardType.Flower315Campaign)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason=config.tips)

        start_time, end_time = camp.get_current_time()
        if self.player.handsel_campaign_last_time < start_time or self.player.handsel_campaign_last_time > end_time:
            self.player.handsel_campaign_counter = 0

        self.player.handsel_campaign_last_time = int(time.time())

        mr_configs = get_config(HandselMulRewardConfig)
        mr_id = int(float(camp.get_mulreward_id(None)))

        mr_config = mr_configs[mr_id]
        mr_next_config = None
        if mr_config.next_id != 0:
            mr_next_config = mr_configs[mr_config.next_id]
        if not mr_next_config:
            mr_next_config = mr_config

        tmp_count = req.count * config.camp_count
        self.player.handsel_campaign_counter += tmp_count

        ranking = camp.get_full_ranking()
        ranking.update_score(self.player.entityID, self.player.handsel_campaign_counter)

        if not self.player.campaign_honor_point or self.player.campaign_honor_point.strip() == '':
            self.player.campaign_honor_point = "{}"

        camp_id = str(camp.get_current().ID)
        import json
        honor_json = json.loads(self.player.campaign_honor_point)
        if camp_id not in honor_json:
            honor_json[camp_id] = 0
        honor_json[camp_id] += tmp_count

        self.player.campaign_honor_point = json.dumps(honor_json)

        camp_counter = int(float(camp.update_counter(tmp_count)))

        def update_next_mr(mr_configs, mr_id, mr_config, mr_next_config, count):
            if mr_config.next_id == mr_next_config.next_id:
                return mr_id, mr_config, mr_next_config

            if count >= mr_next_config.need_count:
                tmp_mr_id = mr_config.next_id
                mr_config = mr_next_config

                if mr_config.next_id != 0:
                    mr_next_config = mr_configs[mr_config.next_id]

                if not mr_next_config:
                    mr_next_config = mr_config

                return update_next_mr(mr_configs, tmp_mr_id, mr_config, mr_next_config, count)

            return mr_id, mr_config, mr_next_config

        new_mr_id, mr_config, mr_next_config = update_next_mr(mr_configs, mr_id, mr_config, mr_next_config, camp_counter)
        if new_mr_id != mr_id:
            camp.set_mulreward_id(new_mr_id)

        self.player.save()
        self.player.sync()

        rsp = poem_pb.HandselOpResponse()
        rsp.personal_count = self.player.handsel_campaign_counter
        rsp.total_count = camp_counter
        rsp.next_lv_count = mr_next_config.need_count
        rsp.reward_multiple = int(mr_config.mulreward * 100)
        rsp.next_reward_multiple = int(mr_next_config.mulreward * 100)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.HANDSEL_CAMPAIGN_RANK_S)
    def handsel_campaign_rank_s(self, msgtype, body):
        camp = g_campaignManager.handsel_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")

        rsp = poem_pb.PvpTargets()

        rankers = camp.get_short_ranking()
        for entityID, v in rankers.iteritems():
            target = {}
            target["entityID"] = entityID
            target["name"] = v["name"]
            target["handsel_counter"] = v["score"]
            rsp.targets.add(**target)

        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.HANDSEL_CAMPAIGN_RANK_F)
    def handsel_campaign_rank_f(self, msgtype, body):
        camp = g_campaignManager.handsel_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")

        from yy.utils import convert_list_to_dict
        from collections import OrderedDict
        from pvp.manager import get_opponent_detail

        p = self.player
        ranking = camp.get_full_ranking()
        rankers = convert_list_to_dict(ranking.get_range_by_score(
            "-inf", "+inf", count=30, withscores=True),
            dictcls=OrderedDict).items()

        def build_player_item(entityID, item):
            detail = get_opponent_detail(entityID)
            item.detail = poem_pb.TargetDetailResponse(**detail)
            item.name = item.detail.name
            item.prototypeID = item.detail.prototypeID

        rsp = poem_pb.RankingList()
        self_rank = None
        for rank, (entityID, score) in enumerate(rankers, 1):
            entityID = int(entityID)
            score = int(float(score))
            if not score:
                continue
            item = rsp.items.add(rank=rank, score=score)
            build_player_item(entityID, item)
            if entityID == p.entityID:
                self_rank = rsp.self = item
        if not self_rank:
            rank = ranking.get_rank(p.entityID)
            if rank:
                item = rsp.self
                item.rank = rank
                item.score = ranking.get_score(p.entityID)
                build_player_item(p.entityID, item)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FLOWER_BOSS_CAMPAIGN_INFO)
    def flower_boss_campaign_info(self, msgtype, body):
        camp = g_campaignManager.flower_boss_campaign
        if not camp.is_open():
            return fail_msg(msgtype, reason="活动未开启")

        p = self.player

        mr_configs = get_config(HandselMulRewardConfig)
        mr_config = mr_configs[camp.get_mulreward_id()]

        from config.configs import FriendfbConfig
        from explore.boss import g_bossCampaignManager
        from friend.manager import load_friendfb
        cur_hp, max_hp = g_bossCampaignManager.campaigns[camp.flower_boss_config_id].get_boss()

        friendfbID = "bosscampaign:%d" % camp.flower_boss_config_id
        friendfb = load_friendfb(friendfbID)
        fb_config = get_config(FriendfbConfig)[camp.flower_boss_config_id]
        friendfb.update(**fb_config._asdict())

        start_time, end_time = camp.get_current_time()
        if p.flower_boss_campaign_last_time < start_time or p.flower_boss_campaign_last_time > end_time:
            p.flower_boss_campaign_total_hurt = 0

        from friend.manager import player_is_dead
        rsp = poem_pb.FlowerBossCampaignInfo()
        rsp.total_hurt = p.flower_boss_campaign_total_hurt
        rsp.total_count = int(float(g_campaignManager.handsel_campaign.get_counter()))
        rsp.reward_multiple = int(mr_config.mulreward * 100)
        rsp.fbDetail.friendfb = poem_pb.Friendfb(**friendfb)
        rsp.fbDetail.rewards = fb_config.rewards
        rsp.fbDetail.is_dead = player_is_dead(p, friendfbID)
        rsp.fbDetail.reborn_cost = (p.friendfb_reborn_counts.get(
            friendfbID, 0) + 1) * get_cons_value("FlowerBossRebornCost")
        return success_msg(msgtype, rsp)
