# coding:utf-8
import time
from datetime import datetime
from datetime import date as datedate
from datetime import time as timetime
from datetime import timedelta
from state.base import StartState
from state.base import StateObject
from state.base import StopStateException

from config.configs import get_config
from config.configs import CampaignConfig
from config.configs import CampaignByCampaignConfig
from config.configs import AccRechargeConfig
from config.configs import AccRechargeByTypeConfig
from config.configs import FundRewardConfig
from config.configs import FundRewardByTypeConfig
from config.configs import TimedStoreConfig
from config.configs import get_cons_value
from config.configs import AccRechargeByGroupConfig
from config.configs import RewardCampaignDescConfig
from config.configs import CountDownConfig
from config.configs import OnlinePacksConfig
from config.configs import DailyRechargeConfig
from config.configs import DailyRechargeByGroupConfig
# from config.configs import GveSceneInfoByWeekConfig
from config.configs import GveCampaignConfig
from config.configs import DailyCampaignConfig
from config.configs import CityCampaignConfig
from config.configs import CityCampaignGroupByTypeConfig
from config.configs import ConsumeCampaignByGroupConfig
from config.configs import ConsumeCampaignConfig
from config.configs import LoginCampaignByGroupConfig
from config.configs import LoginCampaignConfig
from config.configs import ResetRechargesConfig
from config.configs import HotLotteryCampaignConfig
from config.configs import RefreshStoreByGroupConfig
from config.configs import RefreshStoreConfig
from config.configs import ArborDayConfig
from config.configs import ArborDayYYYProbConfig
from config.configs import HandselMulRewardGroupConfig
from config.configs import HandselHonorConfig

from common import index

from entity.manager import g_entityManager

from .constants import AccRechargeType
from .constants import FundRewardType
from player.formulas import get_level_value

import settings
pool = settings.REDISES["index"]
FUND_BOUGHT_COUNT = index.INT_FUND_BOUGHT_COUNT.render()
FUND_RESET_TIME = "FUND_RESET_TIME{%d}{%d}" % (
    settings.SESSION["ID"], settings.REGION["ID"])

from gm.proxy import proxy
from pvp.daily import g_dailyManager
from faction.city import g_cityDungeon
from faction.city import g_cityContend


class BaseCampaign(StateObject):
    campaign_type = None

    def get_loops(self):
        camp = get_config(CampaignByCampaignConfig).get(
            self.campaign_type, [])
        cons = get_config(CampaignConfig)
        return [[i.start, i.end, i.ID] for i in [cons[i.ID] for i in camp]]

    def is_open(self):
        return isinstance(self.state, StartState)

    def get_current(self):
        if not self.is_open():
            return None
        configs = get_config(CampaignConfig)
        return configs.get(self.current_loop)

    def get_current_time(self):
        config = self.get_current()
        if not config:
            return 0, 0
        return config.start, config.end

    def get_end_time(self):
        _, end = self.get_current_time()
        return end


class AccRechargeCampaignMixin(object):
    type = None

    def get_reward_configs(self):
        if not self.current_loop:
            return []
        config = get_config(CampaignConfig).get(self.current_loop)
        if not config:
            return []
        types = get_config(AccRechargeByTypeConfig)
        types = [i.ID for i in types.get(self.type, [])]
        groups = [i.ID for i in get_config(
            AccRechargeByGroupConfig).get(config.group, [])]
        configs = get_config(AccRechargeConfig)
        result = []
        for each in sorted(set(types) & set(groups)):
            each = configs[each]
            if each.ID in types and each.ID in groups:
                result.append(each)
        return result


class WishCampaign(BaseCampaign):
    """许愿活动"""
    campaign_type = CampaignConfig.CampaignWish

    def execute_start(self):
        self.sync()

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_wish_remain_time()
            p.sync(
                'wish_remain_time',
            )


class CycleAccRechargeCampaign(BaseCampaign, AccRechargeCampaignMixin):
    """累计充值活动"""
    type = AccRechargeType.Cycle
    campaign_type = CampaignConfig.CampaignCycleAccRecharge

    def enter_start(self):
        self.reset()

    def reset(self, p=None):
        if not self.is_open():
            return
        if p:
            ps = [p]
        else:
            ps = g_entityManager.players.values()
        now = int(time.time())
        for p in ps:
            start, end = self.get_current_time()
            if p.cycle_acc_recharge_last_clean_time >= start and\
                    p.cycle_acc_recharge_last_clean_time < end:
                continue
            p.cycle_acc_recharge_amount = 0
            p.cycle_acc_recharge_last_clean_time = now
            p.cycle_acc_recharge_rewards.clear()
            p.sync()
            p.save()

    def execute_start(self):
        self.sync()

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_cycle_acc_recharge_remain_time()
            p.sync(
                'cycle_acc_recharge_remain_time',
            )

    def exit_stop(self):
        self.reset()


class WeeksAccRechargeCampaign(BaseCampaign, AccRechargeCampaignMixin):
    """累计充值活动"""
    type = AccRechargeType.Weeks
    campaign_type = CampaignConfig.CampaignWeeksAccRecharge

    def enter_start(self):
        self.reset()

    def reset(self, p=None):
        if not self.is_open():
            return
        if p:
            ps = [p]
        else:
            ps = g_entityManager.players.values()
        now = int(time.time())
        for p in ps:
            start, end = self.get_current_time()
            if p.weeks_acc_recharge_last_clean_time >= start and\
                    p.weeks_acc_recharge_last_clean_time < end:
                continue
            p.weeks_acc_recharge_amount = 0
            p.weeks_acc_recharge_last_clean_time = now
            p.weeks_acc_recharge_rewards.clear()
            p.save()
            p.sync()

    def execute_start(self):
        self.sync()

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_weeks_acc_recharge_remain_time()
            p.sync(
                'weeks_acc_recharge_remain_time',
            )

    def exit_stop(self):
        self.reset()


class MonthAccRechargeCampaign(BaseCampaign, AccRechargeCampaignMixin):
    """累计充值活动"""
    type = AccRechargeType.Month
    campaign_type = CampaignConfig.CampaignMonthAccRecharge

    def enter_start(self):
        self.reset()

    def reset(self, p=None):
        if not self.is_open():
            return
        if p:
            ps = [p]
        else:
            ps = g_entityManager.players.values()
        now = int(time.time())
        for p in ps:
            start, end = self.get_current_time()
            if p.month_acc_recharge_last_clean_time >= start and\
                    p.month_acc_recharge_last_clean_time < end:
                continue
            p.month_acc_recharge_amount = 0
            p.month_acc_recharge_last_clean_time = now
            p.month_acc_recharge_rewards.clear()
            p.sync()
            p.save()

    def execute_start(self):
        self.sync()

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_month_acc_recharge_remain_time()
            p.sync(
                'month_acc_recharge_remain_time',
            )

    def exit_wait(self):
        self.reset()


class DailyAccRechargeCampaign(BaseCampaign, AccRechargeCampaignMixin):
    """每日累计充值活动"""
    type = AccRechargeType.Daily
    campaign_type = CampaignConfig.CampaignDailyAccRecharge

    def execute_start(self):
        self.sync()

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_daily_acc_recharge_remain_time()
            p.sync(
                'daily_acc_recharge_remain_time',
            )


class RewardCampaign(BaseCampaign):

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_reward_campaign_opened()
            p.sync()

    def get_campaign_desc(self):
        current = self.get_current()
        if not current:
            return ''
        configs = get_config(RewardCampaignDescConfig)
        config = configs.get((self.campaign_type, current.group))
        if not config:
            return ''
        return config.desc

    def execute_start(self):
        self.sync()


class UproarCampaign(RewardCampaign):
    """大闹天宫活动"""
    campaign_type = CampaignConfig.CampaignUproar


class LootCampaign(RewardCampaign):
    """蓬莱夺宝活动"""
    campaign_type = CampaignConfig.CampaignLoot


class RobCampaign(RewardCampaign):
    """抢天庭活动"""
    campaign_type = CampaignConfig.CampaignRob


class GoldCampaign(RewardCampaign):
    """推图金币活动"""
    campaign_type = CampaignConfig.CampaignGold


class NormalFbCampaign(BaseCampaign):
    """普通推图掉落活动"""
    campaign_type = CampaignConfig.CampaignNormalFb


class AdvancedFbCampaign(BaseCampaign):
    """精英推图掉落活动"""
    campaign_type = CampaignConfig.CampaignAdvancedFb


class ConsumeCampaign(BaseCampaign):
    """累计消耗活动"""
    campaign_type = CampaignConfig.CampaignConsume


class LoginCampaign(BaseCampaign):
    """累计登录活动"""
    campaign_type = CampaignConfig.CampaignLogin


class RedCampaign(BaseCampaign):
    """红包返利活动"""
    campaign_type = CampaignConfig.CampaignRed


class GveCampaign(BaseCampaign):
    __start = 0
    __end = 0
    count = 0

    def get_loops(self):
        today = datedate.today()
        while True:
            camp = get_config(GveCampaignConfig)
            for _, v in camp.items():
                START_TIME = timetime(*map(int, v.start.split(":", 1)))
                FINAL_TIME = timetime(*map(int, v.end.split(":", 1)))
                date = today + timedelta(days=self.count)
                start = datetime.combine(date, START_TIME)
                final = datetime.combine(date, FINAL_TIME)
                start = time.mktime(start.timetuple())
                end = time.mktime(final.timetuple())
                self.__start = start
                self.__end = end
                yield self.__start, self.__end, "gve"
            self.count += 1

    def reset(self, *ps):
        if not ps:
            ps = g_entityManager.players.values()
        from group.manager import reset_player_gve
        from group.manager import reset_gve
        for p in ps:
            reset_player_gve(p)
            reset_gve(p.groupID)

    def sync(self, *ps):
        if not ps:
            ps = g_entityManager.players.values()
        for p in ps:
            p.clear_gve_start_time()
            p.clear_gve_end_time()
            p.sync()

    def get_end_time(self):
        return self.__end

    def get_start_time(self):
        return self.__start

    def reset_rank(self):
        from group.manager import reset_rank
        reset_rank()

    def execute_start(self):
        self.reset()
        self.sync()
        # self.reset_rank()

    def give(self, *ps):
        from group.manager import give_reward_by_mail
        if not ps:
            ps = g_entityManager.players.values()
        for p in ps:
            give_reward_by_mail(p)

    def exit_stop(self):
        # self.reset()
        self.give()
        self.sync()

    def start(self):
        self.count = 0
        super(GveCampaign, self).start()


class MaxPowerCampaign(BaseCampaign):
    campaign_type = CampaignConfig.CampaignMaxpower


class PetExchangeCampaign(BaseCampaign):
    campaign_type = CampaignConfig.CampaignPetExchange

    def execute_start(self):
        self.sync()

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_pet_exchange_cd()
            p.sync(
                'pet_exchange_cd',
            )


class MatExchangeCampaign(BaseCampaign):
    campaign_type = CampaignConfig.CampaignMatExchange

    def execute_start(self):
        self.sync()

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_mat_exchange_campaign_cd()
            p.sync(
                'mat_exchange_campaign_cd',
            )


class LotteryCampaign(BaseCampaign):
    campaign_type = CampaignConfig.CampaignLottery

    def sync(self, *ps):
        for p in g_entityManager.players.values():
            p.clear_lottery_campaign_cd()
            p.clear_lottery_campaign_discount()
            p.sync()

    def execute_start(self):
        self.sync()


class HotLotteryCampaign(BaseCampaign):
    campaign_type = CampaignConfig.CampaignHotLottery

    def get_hot(self):
        if not self.is_open():
            return ""
        config = self.get_current()
        return config.bg


class DailyPVPCampaign(BaseCampaign):
    campaign_type = CampaignConfig.CampaignDailyPVP
    __start = 0
    __final = 0

    def get_loops(self):
        while True:
            campaigns = get_config(DailyCampaignConfig)
            ignore_first_group = set()
            for k, campaign in campaigns.items():
                d = datetime.fromtimestamp(campaign.start).date()
                ignore_first_group.add(d.strftime("%Y-%m-%d"))
            self.count = 0
            while True:
                index = 0
                for (hour1, minute1), (hour2, minute2) in [
                        ((13, 00), (13, 30)),
                        ((21, 30), (22, 00)),
                        ((23, 30), (23, 59))]:
                    now = datetime.now()
                    today = now.date()
                    date = today + timedelta(days=self.count)
                    index += 1
                    start_time = timetime(hour1, minute1)
                    final_time = timetime(hour2, minute2)
                    start = datetime.combine(date, start_time)
                    final = datetime.combine(date, final_time)
                    if now > final:
                        continue
                    if date.strftime("%Y-%m-%d") in ignore_first_group:
                        if index == 1:
                            continue
                    self.__start = time.mktime(start.timetuple())
                    self.__final = time.mktime(final.timetuple())
                    yield self.__start, self.__final, None
                self.count += 1

    def get_final_time(self):
        return self.__final

    def get_start_time(self):
        return self.__start

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_daily_start_time()
            p.clear_daily_final_time()
            p.sync(
                'daily_start_time',
                'daily_final_time'
            )

    def exit_stop(self):
        g_dailyManager.reset()
        self.sync()

    def enter_stop(self):
        g_dailyManager.cleanup()
        self.sync()

    def execute_stop(self):
        self.sync()

    def enter_start(self):
        self.sync()


class VisitCampaign(BaseCampaign):
    campaign_type = CampaignConfig.CampaignVisit

    def enter_stop(self):
        pass


class DailyRechargeCampaign(BaseCampaign):
    campaign_type = CampaignConfig.CampaignDailyRecharge

    def execute_start(self):
        self.sync()

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_daily_recharge_remain_time()
            p.sync(
                'daily_recharge_remain_time',
            )

    def get_reward_configs(self):
        if not self.current_loop:
            return []
        config = get_config(CampaignConfig).get(self.current_loop)
        if not config:
            return []
        group = get_config(DailyRechargeByGroupConfig).get(config.group)
        configs = get_config(DailyRechargeConfig)
        configs = [configs[i.id] for i in group]
        return configs


class CityCampaign(StateObject):
    city_campaign_type = None
    __start = 0
    __final = 0

    def get_loops(self):
        configs = get_config(CityCampaignGroupByTypeConfig).get(
            self.city_campaign_type, [])
        if not configs:
            raise StopIteration
        configs = get_config(CityCampaignConfig)
        now = datetime.now()
        today = now.date()
        day = today.weekday() + 1
        count = 0
        while True:
            weekday = (day + count) % 7 or 7
            for config in configs.get(weekday, []):
                if config.type != self.city_campaign_type:
                    continue
                now = datetime.now()
                today = now.date()
                date = today + timedelta(days=count)
                __start_time = timetime(*map(int, config.start.split(":", 1)))
                __final_time = timetime(*map(int, config.final.split(":", 1)))
                start = datetime.combine(date, __start_time)
                final = datetime.combine(date, __final_time)
                if now > final:
                    continue
                self.__start = time.mktime(start.timetuple())
                self.__final = time.mktime(final.timetuple())
                yield self.__start, self.__final, None
            count += 1

    def is_open(self):
        return isinstance(self.state, StartState)

    def get_final_time(self):
        return self.__final

    def get_start_time(self):
        return self.__start


class CityDungeonCampaign(CityCampaign):
    city_campaign_type = CityCampaignConfig.CampaignCityDungeon

    def __init__(self, *args, **kwargs):
        self.__start = 0
        self.__final = 0
        super(CityDungeonCampaign, self).__init__(*args, **kwargs)

    def sync(self):
        for p in g_entityManager.players.values():
            p.clear_city_dungeon_start_time()
            p.clear_city_dungeon_final_time()
            p.sync(
                'city_dungeon_start_time',
                'city_dungeon_final_time',
            )

    def enter_start(self):
        self.sync()
        g_cityDungeon.reset()

    def enter_wait(self):
        pass
        # self.sync()

    def exit_stop(self):
        g_cityDungeon.reset()
        self.sync()


class CityContendCampaign(CityCampaign):
    city_campaign_type = CityCampaignConfig.CampaignCityContend

    def __init__(self, *args, **kwargs):
        self.__start = 0
        self.__final = 0
        super(CityContendCampaign, self).__init__(*args, **kwargs)
        self.sync()

    def enter_start(self):
        top_faction = g_cityDungeon.get_top_faction()
        if not top_faction:
            raise StopStateException
        g_cityContend.set_top_faction(top_faction)
        g_cityContend.reset()
        self.sync()

    def sync(self):
        for p in g_entityManager.players.values():
            p.clear_city_contend_start_time()
            p.clear_city_contend_final_time()
            p.sync(
                'city_contend_start_time',
                'city_contend_final_time',
            )

    def enter_wait(self):
        pass
        # self.sync()

    def enter_stop(self):
        g_cityContend.reset()
        self.sync()


class FbDropCampaign(BaseCampaign):
    campaign_type = CampaignConfig.CampaignFbDrop

    # {(scene.type, scene.subtype): campaign.group}
    # 分别对应 普通副本 经营副本 树岛森林 双子岛
    kind = {(1, 0): 1, (2, 0): 2, (3, 0): 4, (3, 1): 8, (3, 2): 8}


class ExchangeCampaign(BaseCampaign):
    """神将置换活动"""
    campaign_type = CampaignConfig.CampaignExchange

    def execute_start(self):
        self.sync()

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_exchange_campaign_remain_time()
            p.sync(
                'exchange_campaign_remain_time',
            )


class RefreshStoreCampaign(BaseCampaign):
    campaign_type = CampaignConfig.CampaignRefreshStore

    def execute_start(self):
        self.sync()

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_refresh_store_campaign_remain_time()
            p.sync(
                'refresh_store_campaign_remain_time',
            )


class ArborDayCampaign(BaseCampaign):
    """植树节活动"""
    campaign_type = CampaignConfig.CampaignArborDay

    def execute_start(self):
        self.sync()

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_arbor_day_campaign_remain_time()
            p.sync(
                'arbor_day_campaign_remain_time',
            )

    def randomYYY(self, p, is_free):
        prob_config = get_config(ArborDayYYYProbConfig).get(p.shake_tree_prob_id)
        r_configs = get_config(ArborDayConfig)
        if is_free:
            r_id = prob_config.free_probs[p.shake_tree_reward_free_next_index]
            config = r_configs.get(r_id)
            if not config:
                r_id = prob_config.free_probs[0]
                config = r_configs.get(r_id)

            ret_index = 1
            for ID in r_configs:
                if ID == r_id:
                    break
                ret_index += 1

            p.shake_tree_reward_free_next_index += 1

            return ret_index, config.rewards
        else:
            r_id = prob_config.pay_probs[p.shake_tree_reward_pay_next_index]
            config = r_configs.get(r_id)
            if not config:
                r_id = prob_config.pay_probs[0]
                config = r_configs.get(r_id)

            ret_index = 1
            for ID in r_configs:
                if ID == r_id:
                    break
                ret_index += 1

            p.shake_tree_reward_pay_next_index += 1

            return ret_index, config.rewards


class SeedCampaign(BaseCampaign):
    campaign_type = CampaignConfig.CampaignSeed

    def execute_start(self):
        self.sync()

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_arbor_day_campaign_remain_time()
            p.sync(
                'arbor_day_campaign_remain_time',
            )

    def updateSeedState(self, p):
        from protocol import poem_pb
        if p.seed_state == poem_pb.SeedStateNormal or\
                p.seed_state == poem_pb.SeedStateRipening or\
                p.seed_state == poem_pb.SeedStateRoot:
            return

        import time
        now = int(time.time())

        def check_sapling(player):
            from config.configs import SeedConfig
            config = get_config(SeedConfig).get(p.seed_id)

            remain_time = player.seed_state_next_change_time - now
            if remain_time <= 0 and player.seed_state == poem_pb.SeedStateSeed:
                player.seed_state = poem_pb.SeedStateSapling
                player.seed_state_last_change_time = int(time.time()) + remain_time
                player.seed_state_next_change_time = player.seed_state_last_change_time + config.times[1]

        def check_tree(player):
            from config.configs import SeedConfig
            config = get_config(SeedConfig).get(p.seed_id)

            remain_time = player.seed_state_next_change_time - now
            if remain_time <= 0 and player.seed_state == poem_pb.SeedStateSapling:
                player.seed_state = poem_pb.SeedStateTree
                player.seed_state_last_change_time = int(time.time()) + remain_time
                player.seed_state_next_change_time = player.seed_state_last_change_time + config.times[2]

        # 成熟了
        if p.seed_state_ripening_time - now <= 0:
            if p.seed_state != poem_pb.SeedStateRoot:
                p.seed_state = poem_pb.SeedStateRipening
                p.seed_state_last_change_time = 0
                p.seed_state_next_change_time = 0
                p.seed_state_ripening_time = 0
        else:
            check_sapling(p)
            check_tree(p)

    def checkWaterWormReward(self, p):
        from protocol import poem_pb
        rsp = poem_pb.SeedWateringWormingResponse()
        if p.watering_used_count >= p.watering_max_count and p.worming_used_count >= p.worming_max_count:
            import random
            from config.configs import get_cons_string_value
            rt = random.randint(1, 2)
            ww_reward = get_cons_string_value("CampaignWWReward_" + str(rt))
            tmp = map(int, ww_reward.split('|'))
            info = {}
            info["type"] = tmp[0]
            info["arg"] = tmp[1]
            info["count"] = tmp[2]
            rsp.rewards.add(**info)

            from reward.manager import RewardType
            from reward.manager import apply_reward
            from reward.manager import parse_reward
            apply_reward(p, parse_reward([info]), type=RewardType.SeedWaterWormCampaign)

        return rsp


class HandselCampaign(BaseCampaign):
    campaign_type = CampaignConfig.CampaignHandsel
    pool = settings.REDISES["index"]
    COUNTER_FLAG = "HANDSEL_CAMP_COUNTER_INCR_FLAG{%d}{%d}" % (
        settings.SESSION["ID"], settings.REGION["ID"])
    MULREWARD_FLAG = "HANDSEL_CAMP_MULREWARD_FLAG{%d}{%d}" % (
        settings.SESSION["ID"], settings.REGION["ID"])
    LAST_TIME_FLAG = "HANDSEL_CAMP_LAST_TIME_FLAG{%d}{%d}" % (
        settings.SESSION["ID"], settings.REGION["ID"])
    RESET_TIME_FLAG = "HANDSEL_CAMP_RESET_TIME_FLAG{%d}{%d}" % (
        settings.SESSION["ID"], settings.REGION["ID"])
    RANKING_FLAG = "HANDSEL_CAMP_RANKING_FLAG{%d}{%d}" % (
        settings.SESSION["ID"], settings.REGION["ID"])

    from yy.ranking.manager import NaturalRankingWithJoinOrder
    handsel_ranking = NaturalRankingWithJoinOrder(RANKING_FLAG, pool)

    def execute_start(self):
        self.reset()
        self.sync()

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_handsel_campaign_remain_time()
            p.sync(
                'handsel_campaign_remain_time',
            )

    def reset(self):
        start_time, final_time = self.get_current_time()
        reset = int(float(pool.execute("GET", self.RESET_TIME_FLAG) or 0))

        mr_id = pool.execute("GET", self.MULREWARD_FLAG)
        if not mr_id:
            current = self.get_current()
            groups = get_config(HandselMulRewardGroupConfig).get(current.group)
            mr_ids = [i.ID for i in groups]
            mr_id = mr_ids[0]
        pool.execute("SET", self.MULREWARD_FLAG, mr_id)

        if reset < start_time:
            pool.execute("SET", self.RESET_TIME_FLAG, start_time+1)

            pool.execute("SET", self.COUNTER_FLAG, 0)
            pool.execute("DEL", self.MULREWARD_FLAG)

            # TODO 重置排行榜
            self.handsel_ranking.clear_raw()

    def update_counter(self, count):
        return (pool.execute("INCRBY", self.COUNTER_FLAG, count) or 0)

    def get_counter(self):
        return (pool.execute("GET", self.COUNTER_FLAG) or 0)

    def set_mulreward_id(self, mr_id):
        pool.execute("SET", self.MULREWARD_FLAG, mr_id)

    def get_mulreward_id(self, default_mr_id):
        if not default_mr_id:
            current = self.get_current()
            groups = get_config(HandselMulRewardGroupConfig).get(current.group)
            mr_ids = [i.ID for i in groups]
            default_mr_id = mr_ids[0]
        return (pool.execute("GET", self.MULREWARD_FLAG) or default_mr_id)

    def get_short_ranking(self):
        from yy.utils import convert_list_to_dict
        from collections import OrderedDict
        rankers = convert_list_to_dict(
            self.handsel_ranking.get_range_by_score(
                "-inf", "+inf", count=5, withscores=True),
            dictcls=OrderedDict)

        from player.model import Player
        players = Player.batch_load(
            rankers.keys(),
            ["entityID", "name"])

        for player in players:
            score = rankers[player.entityID]
            rankers[player.entityID] = {
                "name": player.name,
                "score": score,
                }

        return rankers

    def get_full_ranking(self):
        return self.handsel_ranking


class FlowerBossCampaign(BaseCampaign):
    campaign_type = CampaignConfig.CampaignFlowerBoss
    flower_boss_config_id = 315

    def execute_start(self):
        self.sync()

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_flower_boss_campaign_remain_time()
            p.sync(
                'flower_boss_campaign_remain_time',
            )

    def get_mulreward_id(self):
        current = self.get_current()
        return int(float(g_campaignManager.handsel_campaign.get_mulreward_id(current.reward_group)))

    def execute_stop(self):
        from friend.manager import flowerboss_give_reward
        flower_boss_friendfbID = "bosscampaign:%d" % self.flower_boss_config_id
        flowerboss_give_reward(flower_boss_friendfbID)


class CampaignManager(object):

    def __init__(self):
        self.wish_campaign = WishCampaign()
        self.daily_acc_recharge_campaign = DailyAccRechargeCampaign()
        self.cycle_acc_recharge_campaign = CycleAccRechargeCampaign()
        self.weeks_acc_recharge_campaign = WeeksAccRechargeCampaign()
        self.month_acc_recharge_campaign = MonthAccRechargeCampaign()
        self.uproar_campaign = UproarCampaign()
        self.loot_campaign = LootCampaign()
        self.rob_campaign = RobCampaign()
        self.gold_campaign = GoldCampaign()
        self.reward_campaigns = [
            self.uproar_campaign, self.loot_campaign, self.rob_campaign]
        self.gve_campaign = GveCampaign()
        self.maxpower_campaign = MaxPowerCampaign()
        self.dailypvp_campaign = DailyPVPCampaign()
        self.visit_campaign = VisitCampaign()
        self.daily_recharge_campaign = DailyRechargeCampaign()
        self.pet_exchange_campaign = PetExchangeCampaign()
        self.normal_fb_campaign = NormalFbCampaign()
        self.advanced_fb_campaign = AdvancedFbCampaign()
        self.lottery_campaign = LotteryCampaign()
        self.mat_exchange_campaign = MatExchangeCampaign()
        self.city_dungeon_campaign = CityDungeonCampaign()
        self.city_contend_campaign = CityContendCampaign()
        self.consume_campaign = ConsumeCampaign()
        self.login_campaign = LoginCampaign()
        self.hot_lottery_campaign = HotLotteryCampaign()
        self.fb_drop_campaign = FbDropCampaign()
        self.exchange_campaign = ExchangeCampaign()
        self.refresh_store_campaign = RefreshStoreCampaign()
        self.arbor_day_campaign = ArborDayCampaign()
        self.seed_campaign = SeedCampaign()
        self.handsel_campaign = HandselCampaign()
        self.flower_boss_campaign = FlowerBossCampaign()

    def reset(self, p):
        self.cycle_acc_recharge_campaign.reset(p=p)
        self.weeks_acc_recharge_campaign.reset(p=p)
        self.month_acc_recharge_campaign.reset(p=p)
        self.gve_campaign.reset(p)

    def over_day(self, p):
        reset_check_in_monthly(p)
        p.clear_monthly_card()

    def start(self):
        self.wish_campaign.start()
        self.daily_acc_recharge_campaign.start()
        self.cycle_acc_recharge_campaign.start()
        self.weeks_acc_recharge_campaign.start()
        self.month_acc_recharge_campaign.start()
        self.uproar_campaign.start()
        self.loot_campaign.start()
        self.rob_campaign.start()
        self.gold_campaign.start()
        self.gve_campaign.start()
        self.maxpower_campaign.start()
        self.dailypvp_campaign.start()
        self.visit_campaign.start()
        self.daily_recharge_campaign.start()
        self.pet_exchange_campaign.start()
        self.normal_fb_campaign.start()
        self.advanced_fb_campaign.start()
        self.lottery_campaign.start()
        self.mat_exchange_campaign.start()
        self.city_dungeon_campaign.start()
        self.city_contend_campaign.start()
        self.consume_campaign.start()
        self.login_campaign.start()
        self.hot_lottery_campaign.start()
        self.fb_drop_campaign.start()
        self.exchange_campaign.start()
        self.refresh_store_campaign.start()
        self.arbor_day_campaign.start()
        self.seed_campaign.start()
        self.handsel_campaign.start()
        self.flower_boss_campaign.start()


def on_recharge(p, gold):
    """累计充值"""
    flag = False
    configs = get_config(AccRechargeConfig)
    now = datetime.now()
    now_ts = time.mktime(now.timetuple())
    if g_campaignManager.daily_acc_recharge_campaign.is_open():
        origin = p.daily_acc_recharge_amount
        p.daily_acc_recharge_amount += gold
        current = p.daily_acc_recharge_amount
        reward_configs = g_campaignManager.\
            daily_acc_recharge_campaign.get_reward_configs()
        for each in reward_configs:
            config = configs[each.ID]
            if origin < config.gold and current >= config.gold:
                p.daily_acc_recharge_rewards.add(each.ID)
        flag = True
    if g_campaignManager.cycle_acc_recharge_campaign.is_open():
        origin = p.cycle_acc_recharge_amount
        p.cycle_acc_recharge_amount += gold
        current = p.cycle_acc_recharge_amount
        reward_configs = g_campaignManager.\
            cycle_acc_recharge_campaign.get_reward_configs()
        for each in reward_configs:
            config = configs[each.ID]
            if origin < config.gold and current >= config.gold:
                p.cycle_acc_recharge_rewards.add(each.ID)
        p.cycle_acc_recharge_last_clean_time = now_ts
        flag = True
    if g_campaignManager.weeks_acc_recharge_campaign.is_open():
        origin = p.weeks_acc_recharge_amount
        p.weeks_acc_recharge_amount += gold
        current = p.weeks_acc_recharge_amount
        reward_configs = g_campaignManager.\
            weeks_acc_recharge_campaign.get_reward_configs()
        for each in reward_configs:
            config = configs[each.ID]
            if origin < config.gold and current >= config.gold:
                p.weeks_acc_recharge_rewards.add(each.ID)
        p.weeks_acc_recharge_last_clean_time = now_ts
        flag = True
    if g_campaignManager.month_acc_recharge_campaign.is_open():
        origin = p.month_acc_recharge_amount
        p.month_acc_recharge_amount += gold
        current = p.month_acc_recharge_amount
        reward_configs = g_campaignManager.\
            month_acc_recharge_campaign.get_reward_configs()
        for each in reward_configs:
            config = configs[each.ID]
            if origin < config.gold and current >= config.gold:
                p.month_acc_recharge_rewards.add(each.ID)
        p.month_acc_recharge_last_clean_time = now_ts
        flag = True
    if g_campaignManager.daily_recharge_campaign.is_open():
        reward_configs = g_campaignManager.\
            daily_recharge_campaign.get_reward_configs()
        for config in reward_configs:
            if gold == config.gold:
                used = p.daily_recharge_useds.get(config.id, 0)
                if used < config.count:
                    p.daily_recharge_useds[config.id] = used + 1
                    p.daily_recharge_rewards.append(config.id)
                    p.touch_daily_recharge_useds()
                    p.touch_daily_recharge_rewards()
                break
    if not p.monthly_card:
        p.monthly_card_acc_amount += gold / 10
        if p.monthly_card_acc_amount >= get_cons_value("MonthlyCardAccAmount"):
            p.monthly_card_time = now
            p.monthly_card_acc_amount = 0
            p.monthly_card_received = False  # 到期后同一日再次购买时重置
        flag = True
    if flag:
        p.save()
        p.sync()


def get_bought_fund_count():
    """开服基金购买人数"""
    with pool.ctx() as conn:
        return int(conn.execute("GET", FUND_BOUGHT_COUNT) or 0) +\
            get_cons_value("FundFakeNumber")


def incr_bought_fund_count():
    """递增开服基金购买人数"""
    with pool.ctx() as conn:
        return int(conn.execute("INCR", FUND_BOUGHT_COUNT))


def on_fund_bought_count_change(origin, current):
    """开服基金购买触发全民福利广播"""
    types = get_config(FundRewardByTypeConfig).get(
        FundRewardType.Full, [])
    configs = get_config(FundRewardConfig)
    for each in types:
        config = configs[each.ID]
        if origin < config.parm and current >= config.parm:
            proxy.boardcast_fund_change()
            break


@proxy.rpc_batch
def boardcast_fund_change():
    """广播全民福利奖励"""
    for p in g_entityManager.players.values():
        p.clear_fund_full_rewards_can_receive()
        p.sync(
            'fund_full_rewards_can_receive',
        )


def reset_fund(p):
    with pool.ctx() as conn:
        t = int(conn.execute("GET", FUND_RESET_TIME) or 0)
    if p.fund_reset_time < t:
        p.fund_bought_flag = False
        p.fund_rewards_received.clear()
        p.fund_reset_time = t
        p.save()


def reset_check_in_monthly(p, now=None):
    """每月重置签到"""
    if not now:
        now = datetime.now()
    last = p.check_in_last_time
    if not last:
        return
    if (last.year, last.month) != (now.year, now.month):
        # if p.check_in_used_count or p.check_in_over_count:
        #     p.check_in_used_count = 0
        #     p.check_in_over_count = 0
        #     p.save()
        if p.check_in_used_count:
            p.check_in_used_count = 0
            p.save()


def trigger_timed_store(p, now=None):
    """触发限时商店"""
    if not now:
        now = datetime.now()
    now = time.mktime(now.timetuple())
    configs = get_config(TimedStoreConfig)
    if p.timed_store_id and p.timed_store_id in configs:
        id = configs[p.timed_store_id].post
    else:
        id = min(configs)
    if not id or id not in configs:
        p.timed_store_id = 0
        p.timed_store_cd = 0
    else:
        config = configs[id]
        p.timed_store_cd = now + config.cd
        p.timed_store_id = id
    p.save()
    p.sync()


def get_count_down(p):
    configs = get_config(CountDownConfig)
    try:
        config = configs[p.count_down_index]
    except IndexError:
        config = None
    return config


def start_count_down(p):
    if not p.count_down_cd:  # 旧号
        p.count_down_cd = p.count_down_time
    if p.count_down_index or p.count_down_time:
        return
    config = get_count_down(p)
    if not config:
        return
    if not p.count_down_time:
        now = int(time.time())
        today = datedate.fromtimestamp(now)
        p.count_down_time = time.mktime(
            (today + timedelta(days=config.days)).timetuple())
    if not p.count_down_cd:  # 新号
        p.count_down_cd = p.count_down_time


def count_down_next(p):
    p.count_down_index += 1
    config = get_count_down(p)
    if not config:
        return
    min_config = get_config(CountDownConfig)[0]
    base = datedate.fromtimestamp(
        p.count_down_time) - timedelta(days=min_config.days)
    p.count_down_cd = time.mktime((
        base + timedelta(days=config.days)).timetuple())


def trigger_online_packs(p, now=None, refresh=False):
    if not get_level_value(p.level, "online_packs"):
        return
    if not now:
        now = int(time.time())
    try:
        config = get_config(OnlinePacksConfig)[p.online_packs_index]
    except IndexError:
        return None
    p.online_packs_cd = now + config.cd
    return config


def reset_consume_campaign(p):
    camp = g_campaignManager.consume_campaign
    opened = camp.is_open()
    start, final = camp.get_current_time()
    flag = False
    if opened:
        if p.consume_campaign_reset_time < start or \
                p.consume_campaign_reset_time > final:
            flag = True
    else:
        flag = True
    if flag:
        if p.consume_campaign_rewards or p.consume_campaign_amount:
            p.consume_campaign_rewards.clear()
            p.consume_campaign_amount = 0
        p.consume_campaign_reset_time = start
        p.save()
        p.sync()


def do_consume_campaign(p, type, value):
    camp = g_campaignManager.consume_campaign
    if camp.is_open():
        current = camp.get_current()
        if current.reward_group == type:
            origin = p.consume_campaign_amount
            p.consume_campaign_amount += value
            group = get_config(
                ConsumeCampaignByGroupConfig).get(current.group, [])
            configs = get_config(ConsumeCampaignConfig)
            configs = sorted(
                [configs[i.ID] for i in group],
                key=lambda s: s.consume, reverse=True)
            for config in configs:
                if origin < config.consume and \
                        p.consume_campaign_amount >= config.consume:
                    p.consume_campaign_rewards.add(config.ID)


def reset_login_campaign(p):
    camp = g_campaignManager.login_campaign
    opened = camp.is_open()
    start, final = camp.get_current_time()
    flag = False
    if opened:
        if p.login_campaign_reset_time < start or \
                p.login_campaign_reset_time > final:
            flag = True
    else:
        flag = True
    if flag:
        if p.login_campaign_rewards or p.login_campaign_amount:
            p.login_campaign_rewards.clear()
            p.login_campaign_amount = 0
        p.login_campaign_reset_time = start
        p.save()
        p.sync()


def do_login_campaign(p):
    camp = g_campaignManager.login_campaign
    if camp.is_open():
        today = datedate.today()
        if not p.lastlogin or p.lastlogin.date() != today:
            current = camp.get_current()
            origin = p.login_campaign_amount
            p.login_campaign_amount += 1
            group = get_config(
                LoginCampaignByGroupConfig).get(current.group, [])
            configs = get_config(LoginCampaignConfig)
            configs = sorted(
                [configs[i.ID] for i in group],
                key=lambda s: s.day, reverse=True)
            for config in configs:
                if origin < config.day and \
                        p.login_campaign_amount >= config.day:
                    p.login_campaign_rewards.add(config.ID)


def reset_online_packs(p, refresh=False):
    # 等级触发
    # 领取触发
    # 昨天全部领取完 重新从0开始
    # 昨天没有全部领取完 (在线) 再领取一个后重新从0开始
    # 昨天没有全部领取完 (离线) 重新从0开始
    if not get_level_value(p.level, "online_packs"):
        return
    now = int(time.time())
    today = datedate.fromtimestamp(now)
    if p.online_packs_reset:
        reset = datedate.fromtimestamp(p.online_packs_reset)
        if today == reset:
            return
        else:
            if p.online_packs_last_recv:
                last = datedate.fromtimestamp(p.online_packs_last_recv)
                if last < today:  # 昨天
                    if p.online_packs_done:  # 全部领取完
                        p.online_packs_index = 0
                        p.online_packs_done = False
                    else:
                        if refresh:  # 上线时或玩家主动领取时调用
                            p.online_packs_index = 0
                            p.online_packs_done = False
                        else:  # 在线玩家，等待玩家自己领取
                            return
            elif refresh:
                p.online_packs_index = 0
                p.online_packs_done = False
    triggered = trigger_online_packs(p, now=now, refresh=refresh)
    p.online_packs_reset = now
    p.save()
    p.sync()
    return triggered


def reset_recharges(p):
    config = get_config(ResetRechargesConfig)[0]
    if not config.times:
        return
    if p.reset_recharges_seq < config.times:
        p.bought_recharges.clear()
        p.reset_recharges_seq = config.times
        p.first_recharge_flag = True
        p.timed_store_cd = 0
        p.timed_store_id = 0
        p.save()
        p.sync()


g_campaignManager = CampaignManager()
