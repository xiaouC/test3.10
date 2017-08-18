# coding: utf-8
import os
import time
from datetime import date as datedate, timedelta, datetime
import logging
logger = logging.getLogger('entity')
from functools import update_wrapper

import ujson as json
import settings
from yy.message.header import fail_msg
from config.configs import CreatePlayerConfig
from config.configs import LevelupConfig
from config.configs import FbInfoByTypeConfig
from config.configs import RechargeConfig
from config.configs import get_config
from config.configs import get_cons_value

from lineup.manager import init_lineups
from player.model import Player
from user.model import User


def create_player(player):
    config = get_config(CreatePlayerConfig)[player.sex, player.career]
    player.mats[config.prototypeID] = 1
    player.prototypeID = config.prototypeID
    player.mats[config.borderID] = 1
    player.borderID = config.borderID
    player.money = config.money
    player.gold = config.gold
    player.level = config.level
    player.createtime = datetime.now()
    player.last_check_mail_time = time.mktime(player.createtime.timetuple())
    player.sp = config.sp
    player.spmax = player.sp
    player.petmax = config.petmax
    player.new_role = True
    player.add_pets(*[{"prototypeID": p} for p in config.petIDs])
    player.skillpoint = player.skillpoint_max
    player.maze_rest_count = player.maze_most_count
    player.lottery_gold_accumulating = config.accumulating
    # # 新号过滤已过期签到天数
    # player.check_in_over_count = max(player.createtime.day - 1, 0)
    # player.check_in_used_count = player.check_in_over_count
    from task.manager import trigger_seven_task
    trigger_seven_task(player)
    init_lineups(player)
    if config.drop:
        from reward.manager import open_reward, RewardType
        reward = open_reward(RewardType.CreatePlayer, config.drop)
        reward.apply(player)
    # wish
    if get_cons_value("WishNewPlayerExperienceFlag"):
        player.wish_experience_time = time.mktime(
            player.createtime.timetuple()) + get_cons_value(
                "WishNewPlayerExperienceTime")
    player.save()
    return player


def save_guide(player, guide_type):
    # 保存新手引导进度
    if not guide_type:
        return
    if guide_type in player.guide_types:
        return
    from common.log import gm_logger
    from scene.constants import FbType
    fbinfo = get_config(FbInfoByTypeConfig).get(FbType.Normal, [])
    maxfb = max(set(player.fbscores) & set(e.ID for e in fbinfo) or [0])
    gm_logger.info({"guide": {
        "entityID": player.entityID,
        "type": "guide_%s" % guide_type,
        "userID": player.userID,
        "username": player.username,
        "data": {"fbID": maxfb},
    }})
    player.guide_types.add(guide_type)
    player.set_dirty('guide_types')
    player.save()


def check_over_day():
    # 这个函数，一天内可能被调用多次
    from task.manager import on_monthly_card, on_vip_level
    from task.manager import on_login, check_sign_up
    from task.manager import on_levelup
    from campaign.manager import g_campaignManager
    from campaign.manager import reset_online_packs
    from campaign.manager import do_login_campaign
    for p in g_entityManager.players.values():
        do_login_campaign(p)
        on_monthly_card(p)
        on_vip_level(p)
        on_login(p)
        on_levelup(p)
        g_campaignManager.over_day(p)
        check_sign_up(p)
        reset_online_packs(p)
        p.sync()


def reset_on_zero():
    for p in g_entityManager.players.values():
        p.cycle()
        # 控制日冒险礼包
        if p.trigger_packs_flag:
            p.trigger_packs_flag = getattr(
                settings, "TRIGGER_PACKS_FLAG", True)
        if p.first_recharge_flag:
            p.first_recharge_flag = getattr(
                settings, "PAY", True)
        p.save()
        p.sync()


def level_required(f=None, tag=None, level=None):
    def deco(f):
        def inner(self, msgtype, body):
            l = self.player.level
            if level and l < level:
                return fail_msg(msgtype, reason="等级不足")
            config = get_config(LevelupConfig).get(l, None)
            if tag and config:
                flag = bool(getattr(config, tag, True))
                if not flag:
                    return fail_msg(msgtype, reason="等级不足")
            return f(self, msgtype, body)
        update_wrapper(inner, f)
        return inner
    if f:
        return deco(f)
    return deco


def check_level_packs(p):
    from config.configs import get_config, LevelPacksConfig
    packs = get_config(LevelPacksConfig)
    exempts = set(p.level_packs_end).union(p.level_packs_done)
    samples = sorted(set(packs).difference(exempts))
    for i in samples:
        pack = packs[i]
        if p.level >= pack.level:
            p.level_packs_done.add(i)
        else:
            break
    p.save()
    p.sync()


def check_power_packs(p):
    from config.configs import get_config, PowerPacksConfig
    packs = get_config(PowerPacksConfig)
    exempts = set(p.power_packs_end).union(p.power_packs_done)
    samples = sorted(set(packs).difference(exempts))
    for i in samples:
        pack = packs[i]
        if p.max_power >= pack.id:
            p.power_packs_done.add(i)
        else:
            break
    p.save()
    p.sync()


def clean_yesterday_daily_taskrewards(p):
    """清除不是今天完成的每日任务奖励"""
    from config.configs import get_config, TaskConfig
    from task.constants import TaskType
    configs = get_config(TaskConfig)
    today = datedate.today()
    pending = set()
    for taskID in p.taskrewards:
        info = configs.get(taskID)
        if not info:
            continue
        if info.type != TaskType.Daily:
            continue
        task = p.tasks.get(taskID)
        if task:
            dt = datedate.fromtimestamp(task["when"])
            if dt == today:
                continue
            pending.add(taskID)
            logger.info("Cleanup task: %r", task)
    for each in pending:
        p.taskrewards.remove(each)
    p.save()


def patch_guide_fb(p):
    from scene.manager import get_fb_score, set_fb_score
    score = get_fb_score(p, 100115)
    fullscore = 3
    if score and score != fullscore:
        set_fb_score(p, 100115, fullscore)
        p.save()

_cached_player_reward = None


def get_player_reward():
    global _cached_player_reward
    if _cached_player_reward is None:
        path = os.path.join(
            os.path.dirname(__file__), '../data/player_reward.json')
        _cached_player_reward = json.load(open(path))
    return _cached_player_reward

_cached_player_level_reward = None


def get_player_level_reward():
    global _cached_player_level_reward
    if _cached_player_level_reward is None:
        path = os.path.join(
            os.path.dirname(__file__), '../data/player_level_rewards.json')
        _cached_player_level_reward = json.load(open(path))
    return _cached_player_level_reward


class EntityManager(object):

    def __init__(self):
        self.players = {}

    def load_player(
            self,
            userID,
            entityID,
            clientVersion='',
            featureCode='',
            clientIP=''):
        from reward.manager import givegoldmail
        player = self.get_player(entityID)
        if player:
            return player
        user = User.get(userID)
        # 校验entityID
        if not user or entityID not in user.roles.get(settings.REGION['ID']):
            logger.error('player crossed failed %d', entityID)
            return
        player = Player.load(entityID)
        player.userID = user.userID
        player.username = user.username
        player.username_alias = user.username_alias or ''
        player.channel = user.channel or ''
        if not player:
            return
        self.set_player(player)
        if not player.lastlogin:
            create_player(player)
            player.totallogin = 1  # 累计登陆
            player.seriallogin = 1  # 连续登陆
            givegoldmail(player)
            player.clientVersion = clientVersion
            player.featureCode = featureCode
            player.clientIP = clientIP
            from common.log import role_register
            role_register.info(player=player)
            if not user.back_reward_received:
                data = get_player_reward()
                try:
                    gold, credits = data[user.username]
                except KeyError:
                    pass
                else:
                    from mail.manager import send_mail
                    send_mail(
                        player.entityID, u'老训练师钻石大礼',
                        u' 亲爱的训练师，您好！这是您在《神奇小精灵》充值所获得钻石的返还，请查收！',
                        addition={'gold': gold})
                    player.credits = credits
                    user.back_reward_received = True
                    user.save()
        else:
            player.load_pets()
            player.load_equips()
            player.load_mails()
            player.load_faction()
            player.load_group()
            player.load_offline_attrs()
            # player.load_offline_mail()
            today = datedate.today()
            if player.lastlogin.date() != today:  # 当日重复不计算累计连续登陆
                # 永久商店还没开启的情况下每天都要清空玩家身上商品信息
                # 目的是临时商店开启时第一次有效地刷新商品信息
                clean_yesterday_daily_taskrewards(player)  # 策划要求，隔天的任务奖励全部清空
                if player.lastlogin.date() < (
                    datedate.today() -
                    timedelta(
                        days=1)):  # 昨天没登陆
                    player.seriallogin = 1
                    if player.guide_end_signal:
                        player.seriallogin_after_guide = 1
                else:
                    player.seriallogin += 1
                    if player.guide_end_signal:
                        player.seriallogin_after_guide += 1
                player.totallogin += 1
                if player.guide_end_signal:
                    player.totallogin_after_guide += 1
                player.get_serialloginreward = 0
                # 月卡减去每天登录的天数
                if player.monthly_card_30:
                    delta = today - player.lastlogin.date()
                    player.monthly_card_30 = max(
                        player.monthly_card_30 - delta.days + 1, 0)
                # {{ 新月卡
                if player.monthcard1:
                    delta = today - player.lastlogin.date()
                    player.monthcard1 = max(
                        player.monthcard1 - delta.days + 1, 0)
                if player.monthcard2:
                    delta = today - player.lastlogin.date()
                    player.monthcard2 = max(
                        player.monthcard2 - delta.days + 1, 0)
                if player.weekscard1:
                    delta = today - player.lastlogin.date()
                    player.weekscard1 = max(
                        player.weekscard1 - delta.days + 1, 0)
                if player.weekscard2:
                    delta = today - player.lastlogin.date()
                    player.weekscard2 = max(
                        player.weekscard2 - delta.days + 1, 0)
                # }}
                # build_loginreward_set(player)
                givegoldmail(player)
            # 控制日冒险礼包
            if player.trigger_packs_flag:
                player.trigger_packs_flag = getattr(
                    settings, "TRIGGER_PACKS_FLAG", True)
            from pvp.rank import g_rankManager
            g_rankManager.check_mail(player)
            g_rankManager.reset_rank(player)
            from pvp.swap import g_swapManager
            g_swapManager.give_rewards(player)
            from campaign.manager import g_campaignManager
            g_campaignManager.reset(player)
            from pvp.daily import g_dailyManager
            g_dailyManager.reset(player)
            from faction.city import g_cityDungeon
            g_cityDungeon.reset_player(player, all=True)
            from faction.city import g_cityContend
            g_cityContend.reset_player(player, all=True)
            from campaign.manager import reset_check_in_monthly
            reset_check_in_monthly(player)
            from pvp.rob import check_rob, resize_rob_history_by_time
            check_rob(player)
            from pvp.loot import check_loot
            check_loot(player)
            resize_rob_history_by_time(player)
            from campaign.manager import start_count_down
            start_count_down(player)
            from mall.manager import reset_vip_packs
            reset_vip_packs(player)
            from mall.manager import first_recharge_patch
            first_recharge_patch(player)
            from campaign.manager import reset_fund
            reset_fund(player)
            from explore.dlc import g_dlcCampaignManager
            g_dlcCampaignManager.reset_task(player)
            from group.manager import give_reward_by_mail
            give_reward_by_mail(player)
            from explore.boss import give_reward
            give_reward(player)
            from world.service import give_goods
            configs = get_config(RechargeConfig)
            # from task.manager import patch_noob_tasks
            # patch_noob_tasks(player)
            # patch_guide_fb(player)
            for g, amount in player.offline_recharges or []:
                config = configs.get(g)
                if config:
                    give_goods(player, config, amount=amount)
            player.offline_recharges = []
        from explore.ambition import reload_ambition
        reload_ambition(player)
        from explore.ambition import reload_vip_ambition
        reload_vip_ambition(player)
        from task.manager import on_monthly_card
        on_monthly_card(player)
        from task.manager import on_vip_level
        on_vip_level(player)
        from task.manager import on_login
        on_login(player)
        from task.manager import on_vip_level
        on_vip_level(player)
        from task.manager import on_levelup
        on_levelup(player)
        from task.manager import on_dlc_score
        on_dlc_score(player)
        from task.manager import on_friends_count
        on_friends_count(player)
        from campaign.manager import reset_online_packs
        reset_online_packs(player, refresh=True)
        from campaign.manager import reset_consume_campaign
        reset_consume_campaign(player)
        from campaign.manager import reset_login_campaign
        reset_login_campaign(player)
        from mail.manager import apply_condition_mail
        apply_condition_mail(player)
        from campaign.manager import do_login_campaign
        do_login_campaign(player)
        from campaign.manager import reset_recharges
        reset_recharges(player)
        check_power_packs(player)
        player.daily_first_login = True
        now = int(time.time())
        player.lastlogin = datetime.fromtimestamp(now)
        # 推荐好友
        from friend.manager import recommendp
        recommendp(player)
        if player.first_recharge_flag:
            player.first_recharge_flag = getattr(
                settings, "PAY", True)
        # 触发power计算， 更新indexing
        if not user.back_level_reward_received:
            data = get_player_level_reward()
            try:
                level, gold = data[user.username]
            except KeyError:
                pass
            else:
                from mail.manager import send_mail
                send_mail(
                    player.entityID, u'老训练师等级返利',
                    u'亲爱的训练师：  您在旧版《神奇小精灵》1月17日之前，达到[colorF:246;255;0]%d级[colorF:255;255;255]，向您奉上[colorF:246;255;0]钻石*%d[colorF:255;255;255]。祝您游戏愉快～' % (level, gold),
                    addition={'gold': gold})
                user.back_level_reward_received = True
                user.save()
        # update seed state
        from campaign.manager import g_campaignManager
        if g_campaignManager.seed_campaign.is_open():
            g_campaignManager.seed_campaign.updateSeedState(player)
        # player.update_power()
        player.save()
        return player

    # 玩家心跳检测
    def player_heartbeat(self):
        from common.log import role_heartbeat
        for _, player in self.players.items():
            if player.isLoading:
                continue
            role_heartbeat.info(player=player)

    def unload_player(self, playerId):
        try:
            del self.players[playerId]
        except KeyError:
            pass

    def get_player(self, playerId):
        return self.players.get(playerId)

    def set_player(self, player):
        self.players[player.entityID] = player

    def has_player(self, playerId):
        return playerId in self.players

    def get_players_info(self, playerIDs, attrs):
        objs = []
        pending = []
        playerIDs = list(playerIDs)
        for playerID in list(playerIDs):
            p = self.get_player(playerID)
            if p:
                objs.append(p)
            else:
                pending.append(playerID)
        from player.model import Player
        objs.extend(filter(
            lambda s: s,
            Player.batch_load(pending, Player.expend_fields(attrs))))
        result = []
        for p in objs:
            result.append({n: getattr(p, n) for n in attrs})
        return sorted(result, key=lambda s: playerIDs.index(s['entityID']))

g_entityManager = EntityManager()
