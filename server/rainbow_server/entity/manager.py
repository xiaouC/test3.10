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
    player.prototypeID = config.prototypeID
    player.borderID = config.borderID
    player.money = config.money
    player.gold = config.gold
    player.level = config.level
    player.createtime = datetime.now()
    player.last_check_mail_time = time.mktime(player.createtime.timetuple())
    player.new_role = True
    player.save()
    return player


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
        p.save()
        p.sync()


class EntityManager(object):

    def __init__(self):
        self.players = {}

    def load_player(self, userID, entityID, clientVersion='', featureCode='', clientIP=''):
        player = self.get_player(entityID)
        if player:
            return player
        user = User.get(userID)
        # 校验entityID
        if not user or entityID not in user.roles.get(settings.REGION['ID']):
            logger.error('player crossed failed %d', entityID)
            return
        player = Player.load(entityID)
        if not player:
            return
        player.userID = user.userID
        player.username = user.username
        player.username_alias = user.username_alias or ''
        player.channel = user.channel or ''
        self.set_player(player)
        if not player.lastlogin:
            create_player(player)
            player.totallogin = 1  # 累计登陆
            player.seriallogin = 1  # 连续登陆
            player.clientVersion = clientVersion
            player.featureCode = featureCode
            player.clientIP = clientIP
            from common.log import role_register
            role_register.info(player=player)
        else:
            player.load_mails()
            today = datedate.today()
            if player.lastlogin.date() != today:  # 当日重复不计算累计连续登陆
                if player.lastlogin.date() < (datedate.today() - timedelta(days=1)):  # 昨天没登陆
                    player.seriallogin = 1
                else:
                    player.seriallogin += 1
                player.totallogin += 1
                # 月卡减去每天登录的天数
                if player.monthly_card_30:
                    delta = today - player.lastlogin.date()
                    player.monthly_card_30 = max(player.monthly_card_30 - delta.days + 1, 0)
                # {{ 新月卡
                if player.monthcard1:
                    delta = today - player.lastlogin.date()
                    player.monthcard1 = max(player.monthcard1 - delta.days + 1, 0)
                if player.monthcard2:
                    delta = today - player.lastlogin.date()
                    player.monthcard2 = max(player.monthcard2 - delta.days + 1, 0)
                if player.weekscard1:
                    delta = today - player.lastlogin.date()
                    player.weekscard1 = max(player.weekscard1 - delta.days + 1, 0)
                if player.weekscard2:
                    delta = today - player.lastlogin.date()
                    player.weekscard2 = max(player.weekscard2 - delta.days + 1, 0)
                # }}
        player.daily_first_login = True
        now = int(time.time())
        player.lastlogin = datetime.fromtimestamp(now)
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
        objs.extend(filter(lambda s: s, Player.batch_load(pending, Player.expend_fields(attrs))))
        result = []
        for p in objs:
            result.append({n: getattr(p, n) for n in attrs})
        return sorted(result, key=lambda s: playerIDs.index(s['entityID']))

g_entityManager = EntityManager()
