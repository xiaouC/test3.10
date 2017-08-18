# coding: utf-8
import logging
from functools import reduce
logger = logging.getLogger('world')
from bson import objectid
import time
import ujson
import gevent
# from datetime import datetime
from datetime import date as datedate

import protocol.poem_pb as msgid

from protocol import poem_pb
from yy.rpc import RpcService, rpcmethod
from session.sessstore import SessionStore
from yy.entity.storage.redis import make_key
from yy.message.header import clean_msgtype
from yy.message.header import success_msg, fail_msg

from common import msgTips
from common import get_session_pool
from common.log import gm_logger
from common.log import role_custom, role_credit
from common.log import role_heartbeat

from entity.sync import multi_sync_property
from scene.manager import sync_scene_infos
from player.manager import g_playerManager, Peer
from entity.manager import g_entityManager
from lineup.manager import sync_lineups

from pet.service import PetService
from pvp.service import PvpService
from pvp.manager import send_fight_verify
from mall.service import MallService
from mail.service import MailService
from chat.service import ChatService
from equip.service import EquipService
from player.service import RoleService
from explore.service import ExploreService
from faction.service import FactionService
from friend.service import FriendService
from campaign.service import CampaignService
from ranking.service import RankingService
from group.service import GroupService
from mat.service import MatService
from gem.service import GemService

from session.utils import username2type, username2label

from player.model import Player
from player.model import PlayerOnlineIndexing
from config.configs import get_config
from config.configs import VipConfig
from config.configs import FbInfoConfig
from config.configs import SceneInfoConfig
from config.configs import RechargeConfig
from config.configs import RechargeByTypeConfig
from config.configs import RechargeByLabelConfig
from config.configs import RechargeBySdktypeConfig
from config.configs import get_cons_value

from reward.manager import apply_reward
from reward.manager import open_reward
from reward.manager import RewardType
from reward.manager import MatNotEnoughError
from reward.manager import build_reward
from reward.manager import parse_reward
from reward.manager import build_reward_msg

from friend.manager import unrecommendp


from scene.manager import cleanfbs
from scene.manager import get_fb_score
from scene.manager import get_today_remain_count

from scene.constants import FbType

import settings


def cleanup(player):
    if not player:
        return
    from group.manager import quit_gve
    from group.manager import leave_gve
    leave_gve(player)
    quit_gve(player)
    from friend.manager import unlisten
    unlisten(player.entityID)
    PlayerOnlineIndexing.unregister(player.entityID)
    unrecommendp(player)
    player.save_on_quit()
    logger.info('player quit %d', player.entityID)
    g_entityManager.unload_player(player.entityID)
    g_playerManager.close_player(player.entityID)
    logger.info('clean up %d', player.entityID)
    if player.lastlogin and player.lastlogout:
        onlinetimes = (player.lastlogout - player.lastlogin).total_seconds()
    else:
        onlinetimes = 0
    gm_logger.info({'access': {
        'entityID': player.entityID, 'type': 'logout', 'userID': player.userID,
        'username': player.username, 'onlinetimes': onlinetimes,
        'username_alias': player.username_alias, 'channel': player.channel}
    })


def get_notice_rsp():
    from config.configs import NoticeConfig, get_config, LotteryNoticeConfig
    from protocol.poem_pb import Notice, NoticeStruct
    items = get_config(NoticeConfig)
    rsp = Notice()
    if not items:
        return ''
    for k, v in items.items():
        noticestruct = NoticeStruct()
        noticestruct.ID = k
        noticestruct.title = v.title
        noticestruct.content = v.content
        rsp.notices.append(noticestruct)
    rsp.lottery = get_config(LotteryNoticeConfig)[1].notice
    return rsp


def record_cost_sp(p, sp):
    if not p.mall_golden_opened:
        p.golden_sp += sp
    if not p.mall_silver_opened:
        p.silver_sp += sp
    p.friend_total_sp += sp
    if p.factionID:
        p.faction_sp += sp
    p.trigger_event_sp += sp
    p.save()


def get_limited_packs_time(now=None):
    from config.configs import LimitedPacksConfig
    if not now:
        now = int(time.time())
    times = get_config(LimitedPacksConfig)
    for t in times:
        if t.start < now and t.end >= now:
            return t
    return None


def get_timelimited_packs_time(now=None):
    from config.configs import TimeLimitedPacksConfig
    if not now:
        now = int(time.time())
    times = get_config(TimeLimitedPacksConfig)
    for t in times:
        if t.start < now and t.end >= now:
            return t
    return None


MonthCardDays = 30
WeeksCardDays = 7


class RechargeType:
    Normal = 1  # 普通充值
    MonthlyCard30 = 2  # 月卡
    LimitedPacks = 3  # 限购礼包
    TimeLimitedPacks = 4  # 限时礼包
    TriggerPacks1 = 5  # 日冒险礼包
    TriggerPacks2 = 6  # 日多选一礼包
    Monthcard1 = 7
    Monthcard2 = 8
    Weekscard1 = 9
    Weekscard2 = 10


def pay_handler(entityID, username, goodsid, amount=None):
    goodsid = str(goodsid)  # 必须是字符串
    label = username2label(username)
    sdktype = username2type(username)
    sdkconfigs = get_config(RechargeBySdktypeConfig).get(sdktype, [])
    labconfigs = get_config(RechargeByLabelConfig).get(label, [])
    configs = get_config(RechargeConfig)
    ids = {e.id for e in sdkconfigs} & {e.id for e in labconfigs}
    good = {configs[e].goodsid: configs[e] for e in ids}.get(goodsid)
    if not good:
        logger.error("error goodsid %r", goodsid)
        return
    p = g_entityManager.get_player(entityID)
    if p:
        level = p.level
        reward = give_goods(p, good, amount=amount)
        get_gold = reward.get("gold", 0)
    else:
        # patch 离线玩家，需要计算可获得金额
        p = Player.simple_load(entityID, [
            "userID", "level",
            "bought_recharges",
            "offline_recharges"])
        level = p.level
        if p.offline_recharges:
            p.offline_recharges.append([good.id, amount])
        else:
            p.offline_recharges = [[good.id, amount]]
        is_first = (good.id not in (p.bought_recharges or set())) \
            and (good.id not in ({i for i, j in p.offline_recharges} or set()))
        from reward.manager import open_reward, RewardType
        reward = open_reward(RewardType.Recharge, good, is_first, amount)
        rs = reward.apply_after()  # 仅计算可获金额，并不发货
        get_gold = rs.get("gold", 0)
        p.save()
    return {"username": username, "level": level, "get_gold": get_gold}


def sdk_pay(entityID, orderid, amount, rechargegold, sdata, sdktype, goods, delay=0):
    from session.utils import sdk_username
    from sdk.payment import end_payment, get_payment
    GOOD_GOLD = 0

    if orderid:
        sdkorderid = sdk_username(sdktype, orderid)
        payment = get_payment(sdkorderid)
        if len(payment) == 0:
            logger.error('orderid {} not exists.'.format(orderid))
            return False
        # 如果交易完成直接返回成功
        if payment.get('status', None) == 'SUCCESS':
            return True

        if not end_payment(sdkorderid):
            logger.error('insert callback pay record failed %s' % sdkorderid)
            return False
        goodsid = payment["goodsid"]

    elif sdktype == poem_pb.SDK_YYB:
        sdkorderid = sdk_username(sdktype, '')
        ids = get_config(RechargeBySdktypeConfig).get(sdktype, [])
        configs = [get_config(RechargeConfig)[e.id] for e in ids]
        goodsid = max(configs, key=lambda o: o.amount).goodsid

    else:
        logger.error('orderid {} is empty.'.format(orderid))
        return False

    amount = amount / 10.0
    gold = rechargegold
    if goods == GOOD_GOLD:
        data = {
            "clientVersion": "",
            "amount": gold,
            "orderNO": sdkorderid,
            "_level": "",
            "_username": "",
            "_userID": 0,
            "_entityID": entityID,
            "result": 1}
        player = g_entityManager.get_player(entityID)
        if player:
            username = player.username
            userID = player.userID
            playername = player.name
            channel = player.channel
        else:
            p = Player.simple_load(entityID, ["username", "userID", "name", "channel"])
            username = p.username
            userID = p.userID
            playername = p.name
            channel = p.channel
        rs = pay_handler(entityID, username, goodsid, amount=amount)
        if not rs:
            return False
        get_gold = rs["get_gold"]
        username = rs["username"]
        level = rs["level"]
        if player:
            rsp = poem_pb.PayResult(
                success=True, roleID=entityID, userID=userID,
                payID=orderid, goods=0,
                count=get_gold, data=sdata)
            if delay == 0:
                g_playerManager.sendto(
                    player.entityID, success_msg(msgid.SDK_PAY_RESULT, rsp))
            else:
                def do_send():
                    gevent.sleep(delay)
                    g_playerManager.sendto(
                        player.entityID, success_msg(msgid.SDK_PAY_RESULT, rsp))
                gevent.spawn(do_send)
        data.update(_username=username, _level=level)
        data.update(_gold=get_gold)
        role_credit(**data)
        gm_logger.info({'pay': {
                        'entityID': entityID,
                        'amount': amount,
                        'userID': userID,
                        'playername': playername,
                        'channel': channel,
                        'gold': get_gold,
                        'username': username,
                        'transaction_id': orderid
                        },
                       'payID': sdkorderid})
        return True
    logger.error('unknown goods %d', goods)
    return False


def give_goods(player, goods, amount=None):
    rest = 0
    famount = float(goods.amount)
    if amount is not None and famount != amount:
        if amount > famount:
            rest = amount - famount
        else:  # 当充值金额不足，选择同类型的满足金额的商品，多出金额返还
            sdktype = username2type(player.username)
            label = username2label(player.username)
            sdkconfigs = get_config(RechargeBySdktypeConfig).get(sdktype, [])
            labconfigs = get_config(RechargeByLabelConfig).get(label, [])
            typconfigs = get_config(RechargeByTypeConfig).get(goods.type, [])
            ids = {e.id for e in sdkconfigs} & {e.id for e in labconfigs}
            ids = ids & {e.id for e in typconfigs}
            configs = get_config(RechargeConfig)
            configs = [configs[e] for e in ids]
            configs = sorted(
                configs, key=lambda s: float(s.amount), reverse=True)
            for config in configs:
                if float(config.amount) < amount:
                    goods = config
                    rest = amount - famount
                    break
            else:
                goods = None
                rest = amount
    if goods:
        is_first = goods.id not in player.bought_recharges
        if goods.type == RechargeType.LimitedPacks:
            reward_type = RewardType.LimitedPacks
        elif goods.type == RechargeType.TimeLimitedPacks:
            reward_type = RewardType.TimeLimitedPacks
        elif goods.type == RechargeType.TriggerPacks1:
            reward_type = RewardType.TriggerPacks1
        elif goods.type == RechargeType.TriggerPacks2:
            reward_type = RewardType.TriggerPacks2
        else:
            reward_type = RewardType.Recharge
        credits = (famount + rest) * 10
    else:
        is_first = False
        reward_type = RewardType.Recharge
        credits = rest * 10
    reward = open_reward(reward_type, goods, is_first, rest * 10)
    result = reward.apply(player)
    logger.debug("recharge result {}".format(result))
    # 不使用golden是因为有些商品是礼包，不包含钻石
    __vip = player.vip
    player.credits += credits
    if player.vip != __vip:
        # VIP改变导致活动副本次数改变
        from scene.manager import sync_scene_infos
        sync_scene_infos(player, FbType.Campaign)
    from explore.ambition import reload_vip_ambition
    reload_vip_ambition(player)
    if not player.bought_recharges:
        player.first_recharge_numb = result.get("gold", 0)
    if goods:
        if goods.type == RechargeType.MonthlyCard30:
            if not player.monthly_card_30:
                player.monthly_card_30 = 30
                from task.manager import on_monthly_card
                on_monthly_card(player)
        elif goods.type == RechargeType.Monthcard1:
            player.monthcard1 += MonthCardDays
        elif goods.type == RechargeType.Monthcard2:
            player.monthcard2 += MonthCardDays
        elif goods.type == RechargeType.Weekscard1:
            player.weekscard1 += WeeksCardDays
        elif goods.type == RechargeType.Weekscard2:
            player.weekscard2 += WeeksCardDays
        elif goods.type == RechargeType.LimitedPacks:
            now = int(time.time())
            player.limited_packs_used_count += 1
            player.limited_packs_last_time = now
        elif goods.type == RechargeType.TimeLimitedPacks:
            now = int(time.time())
            player.timelimited_packs_last_time = now
        elif goods.type in (
                RechargeType.TriggerPacks1,
                RechargeType.TriggerPacks2):
            # 支付回调问题  # NOTE
            # player.trigger_packs_buy_count += 1
            pass
        # 记录首次充值获得的金额数
        player.bought_recharges.add(goods.id)
        from campaign.manager import on_recharge
        on_recharge(player, goods.golden)
    from task.manager import on_vip_level
    on_vip_level(player)
    player.save()
    player.sync()
    return result


class BaseService(RpcService):

    '世界接口 进入游戏 切换场景 退出游戏等'

    def __init__(self, server, sock):
        self.userID = None
        self.peer = Peer(sock)
        self.server = server
        self.player = None
        self.orderindex = 0
        super(BaseService, self).__init__()

    def rpccall(self, key, *args, **kwargs):
        player = self.player
        if player:
            gm_logger.info({
                'behavior': {
                    'entityID': player.entityID,
                    'msgid': clean_msgtype(key),
                    'level': player.level,
                    'fbprocess': player.fbprocess,
                    'vip': player.vip
                }
            })
        return super(BaseService, self).rpccall(key, *args, **kwargs)

    def method_not_found(self, key, *args, **kwargs):
        logger.warn('msgid %s not found' % key)

    def connection_closed(self):
        cleanup(self.player)

    @rpcmethod(msgid.RECONNECT)
    def reconnect(self, msgtype, body):
        req = poem_pb.Reconnect()
        req.ParseFromString(body)
        rsp = poem_pb.ReconnectResponse()
        ok = False
        session = SessionStore(get_session_pool(), str(req.verify_code))
        userID = session.uid
        if userID:
            player = g_entityManager.get_player(req.entityID)
            if not player:
                # 检查worldid
                worldID = PlayerOnlineIndexing.get_pk(req.entityID)
                if worldID != settings.WORLD["ID"]:
                    # 说明，上次关服，玩家没有收到退出的消息
                    # 或者IOS锁屏，socket关闭，player被cleanup
                    # 现在无法区分这两种情况
                    logger.error("has not worldID")
                else:
                    player = g_entityManager.load_player(
                        userID, req.entityID)
                    logger.info("reload player")
            if player:
                if player.userID != userID:  # 检验userid
                    self.peer.close()
                    logger.error(
                        "wrong userID %r, %r", player.userID, userID)
                else:
                    # 清理上一个socket，如果有的话
                    if g_playerManager.has_player(req.entityID):
                        g_playerManager.kick_player(player.entityID)
                        PlayerOnlineIndexing.update(
                            settings.WORLD["ID"], player.entityID)
                        player.save()
                        logger.info("close last player")
                        # FIXME 因为kick player 把player 给 unload了
                        player = g_entityManager.load_player(
                            userID, req.entityID)
                        logger.info("reload player")
                    # 注册新socket
                    g_playerManager.register(req.entityID, self.peer)
                    self.userID = userID
                    self.player = player
                    ok = True
                    logger.info("reconnect success")
        else:
            logger.error("invalid verify_code %s", req.verify_code)
        rsp.result = ok
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.ENTER_SCENE)
    def enter(self, msgtype, body):
        req = poem_pb.EnterRequest()
        req.ParseFromString(body)
        entityID = req.entityID
        # 不允许重新登录
        if g_playerManager.has_player(entityID):
            if g_playerManager.peers[entityID].key == self.peer.key:
                return
            # 给已登录的发送重复登录消息
            g_playerManager.sendto(
                entityID,
                fail_msg(msgtype, msgTips.FAIL_MSG_KICKED))
            g_playerManager.kick_player(entityID)
        clientVersion = req.clientVersion
        featureCode = req.featureCode
        clientIP, _ = self.peer._sock.getpeername() or ('', '')
        self.player = player = g_entityManager.load_player(
            self.userID,
            entityID,
            clientVersion,
            featureCode,
            clientIP)
        if not player:
            self.peer.sender(fail_msg(msgtype, msgTips.FAIL_MSG_LOAD_PLAYER))
            self.peer.close()
            return
        PlayerOnlineIndexing.update(
            settings.WORLD["ID"], player.entityID)
        player.clientVersion = clientVersion
        player.featureCode = featureCode
        player.clientIP = clientIP
        player.appid = req.deviceInfo.appid
        player.UDID = req.deviceInfo.UDID
        player.idfa = req.deviceInfo.idfa
        player.IMEI = req.deviceInfo.IMEI
        player.MAC = req.deviceInfo.MAC
        player.save()
        g_playerManager.register(player.entityID, self.peer)
        player.sync(all=True)
        entities = player.pets.values() + player.equips.values()
        multi_sync_property(entities, masterID=player.entityID)
        # 新手引导
        rsp = poem_pb.guideResponse()
        rsp.guide_types = player.guide_types
        g_playerManager.sendto(
            player.entityID,
            success_msg(msgid.GUIDE_TYPE_SAVED, rsp))
        # 发送公告
        notice_rsp = get_notice_rsp()
        g_playerManager.sendto(
            player.entityID,  success_msg(msgid.NOTICE, notice_rsp))

        sync_lineups(player)
        sync_scene_infos(player)
        from scene.constants import FbType
        sync_scene_infos(player, FbType.Advanced)
        sync_scene_infos(player, FbType.Campaign)
        rsp = poem_pb.EnterResponse()
        rsp.ENABLE_GIFTKEY = settings.ENABLE_GIFTKEY  # cdkey
        rsp.REV = settings.REV
        from ranking.manager import g_rankingCampaignManager
        rsp.ENABLE_RANKING_CAMPAIGN = g_rankingCampaignManager.started()
        rsp.time = int(time.time())
        from config.configs import get_cons_string_value
        rsp.campaign_sequence = get_cons_string_value("CampaignSequence")
        self.peer.sender(success_msg(msgtype, rsp))
        gm_logger.info({'access': {'entityID': player.entityID,
                                   'type': 'login',
                                   'userID': player.userID,
                                   'username': player.username,
                                   'onlines': g_playerManager.count(),
                                   'username_alias': player.username_alias,
                                   'channel': player.channel}})
        from entity.manager import check_level_packs
        check_level_packs(player)
        from common.log import role_login
        role_login(player=player)

    @rpcmethod(msgid.SAVE_LINEUPS)
    def save_lineups(self, msgtype, body):
        from lineup.manager import save_lineup
        from entity.manager import save_guide
        req = poem_pb.ChangeLineup()
        req.ParseFromString(body)
        p = self.player
        save_guide(p, req.guide_type)  # 保存新手引导进度
        lineup = req.lineup.line
        rsp = poem_pb.ChangeLineupResponse()
        if not save_lineup(p, lineup, req.lineup.type):
            rsp.isSuccess = False
        else:
            p.clear_base_power()
            p.clear_equip_power()
            p.clear_faction_power()
            # p.update_power()
            from task.manager import on_maxpower
            on_maxpower(p, p.max_power)
            p.save()
            p.sync()
            rsp.isSuccess = True
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.ENTER_FB)
    def enter_fb(self, msgtype, body):
        from reward.manager import open_reward, RewardType, build_reward
        from config.configs import FbInfoConfig, RusherConfig
        from config.configs import ExSceneInfoConfig
        from config.configs import SceneInfoConfig
        from scene.manager import is_first
        # from scene.manager import get_campaign_remain_time
        from scene.manager import get_scene_today_remain_count
        from scene.manager import is_open
        from scene.manager import get_today_count, validate_prevs
        from scene.manager import get_remain_cost_count, get_cost_count_cost
        from scene.constants import FbType
        from scene.constants import SceneSubType
        player = self.player
        req = poem_pb.EnterFbRequest()
        req.ParseFromString(body)
        configs = get_config(FbInfoConfig)
        config = configs[req.fbID]
        if player.level < config.openlv:
            return fail_msg(msgtype, reason='等级不足')
        scene_info = get_config(SceneInfoConfig)[config.sceneID]
        if player.level < scene_info.openlv:
            return fail_msg(msgtype, reason='等级不足')
        if player.is_pets_full():
            return fail_msg(msgtype, reason='用户携带怪物数量已到上限')
        if config.sp > player.sp:
            return fail_msg(msgtype, reason='能量不足')
        # if player.currentfbID:
        #    return fail_msg(msgtype, reason='已经进入关卡了')
        # if config.type == FbType.Campaign:
        #     # 活动副本检查时间
        #     timestamp = time.time()
        #     if not get_campaign_remain_time(config.ID, timestamp):
        #         return fail_msg(msgtype, reason='活动还没有开启')
        if config.type == FbType.Campaign:
            scene = get_config(ExSceneInfoConfig).get(config.sceneID)
            if not scene:
                return fail_msg(msgtype, reason='活动还没有开启')
            if not is_open(scene.cycle, scene.days):
                return fail_msg(msgtype, reason='活动还没有开启')
            if not get_scene_today_remain_count(player, config.sceneID):
                return fail_msg(msgtype, reason='超过今日最大挑战次数')
            now = int(time.time())
            sceneInfo = get_config(SceneInfoConfig).get(config.sceneID)
            if not sceneInfo:
                return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
            if sceneInfo.subtype == SceneSubType.Dongtian:
                cd = player.dongtian_cd
            elif sceneInfo.subtype == SceneSubType.Fudi:
                cd = player.fudi_cd
            else:
                cd = 0  # pass below
            if cd and cd > now:
                return fail_msg(msgtype, reason='挑战CD冷却中')
        elif config.type == FbType.Guide:
            if req.fbID in player.fbscores:
                return fail_msg(msgtype, reason='引导关卡已经通过了')
        elif config.type == FbType.Trigger:
            from explore.trigger import check_trigger_event_type
            from explore.trigger import check_trigger_event_param
            from explore.constants import EventType
            if not check_trigger_event_type(player, EventType.Fb):
                return fail_msg(msgtype, reason="无触发事件或错误的事件类型")
            if not check_trigger_event_param(player, req.fbID):
                return fail_msg(msgtype, reason="错误的事件参数")
        elif config.type == FbType.Dlc:
            from explore.dlc import validate_start
            from explore.dlc import validate_dlc_fb
            if not validate_start(
                    player, req.fbID, req.pets, req.dlc_helperID):
                return fail_msg(msgtype, reason="DLC校验失败")
            if not validate_dlc_fb(player, req.fbID):
                return fail_msg(msgtype, reason="此关已通")
        elif config.type == FbType.Maze:
            try:
                event = player.mazes[req.maze_event_index]
                if event["argv"] != req.fbID:
                    return fail_msg(msgtype, reason="Maze校验失败")
            except IndexError:
                return fail_msg(msgtype, reason="Maze校验失败")
            else:
                player.maze_boss_cache = req.maze_event_index
        if get_today_count(player, config.ID) >= config.max:
            # 次数限制
            if not req.usegold:
                return fail_msg(msgtype, reason='超过今日最大挑战次数')
            else:
                if not get_remain_cost_count(player, config.ID):
                    return fail_msg(msgtype, reason='超过今日最大挑战次数')
                elif get_cost_count_cost(player, config.ID) > player.gold:
                    return fail_msg(msgtype, reason='钻石不足')
        # 校验前置
        if not validate_prevs(player, config.ID):
            return fail_msg(msgtype, reason='前置关卡还没有通关')

        player.currentfbID = req.fbID
        rsp = poem_pb.EnterFbResponse()
        rsp.buffid = config.buffid
        rsp.buffpose = config.buffpose
        from player.model import PlayerFightLock
        rsp.verify_code = PlayerFightLock.lock(player.entityID, force=True)
        s = player.fbreward.get(req.fbID)
        from entity.manager import save_guide
        if config.type == FbType.Campaign:
            save_guide(player, "FAKE_FIRST_CAMPAIGN_FB")  # 第1次 活动本
        elif config.type == FbType.Advanced:
            save_guide(player, "FAKE_FIRST_ADVANCED_FB")  # 第1次 精英本
        if s:
            verify_code = rsp.verify_code
            rsp.ParseFromString(str(s))
            rsp.verify_code = verify_code
        else:
            isFirst = is_first(player, req.fbID)
            reward = open_reward(RewardType.FB, player, req.fbID, isFirst, rsp)
            # player.fbreward = reward.apply_reward_after()
            # build_reward_msg(rsp, player.fbreward)
            fbdrop = dict(reward.computedDropPacks)
            rsp.rewards.extend(build_reward(fbdrop))
            from explore.dlc import apply_dlc_reward
            dlc_reward = apply_dlc_reward(
                req.fbID, isfirst=isFirst)
            rsp.rewards.extend(build_reward(dlc_reward))
            logger.debug(rsp)
            # 剧情乱入
            if isFirst:
                configs = get_config(RusherConfig).get(req.fbID, [])
                for c in configs:
                    for rusher in c.rusher:
                        rsp.rushers.add(layer=c.layer, **rusher)
            s = player.fbreward[req.fbID] = rsp.SerializeToString()
        if config.type == FbType.Normal:
            if req.fbID >= get_cons_value("AutoFightAfterThisNormalFbID"):
                player.autofight = True
            if req.fbID >= get_cons_value("SpeedUpFightAfterThisNormalFbID"):
                player.speedUpfight = True
        if config.type == FbType.Dlc:
            if req.dlc_helperID:
                player.dlc_helpers[req.dlc_helperID] = int(time.time())
        rsp.is_first = req.fbID not in player.fbscores
        player.clear_power()
        player.save()
        player.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.RETRY_FB)
    def retry_fb(self, msgtype, body):
        from protocol.poem_pb import RetryFbResponse
        from reward.manager import apply_reward, RewardType, AttrNotEnoughError
        rsp = RetryFbResponse()
        player = self.player
        try:
            apply_reward(player, {}, {'gold': 50}, RewardType.RetryFB)
        except AttrNotEnoughError:
            rsp.success = False
        else:
            is_first = int(not player.retry_fb_count)  # 玩家第一次花费钻石战斗复活通关关卡
            is_consume_first = int(not player.consume_count)
            role_custom(player=player,
                        type=role_custom.Retry,
                        arg1=ujson.dumps({'fbID': player.currentfbID,
                                          'is_consume_first': is_consume_first,
                                          'is_first': is_first,
                                          }))
            player.consume_count += 1
            player.retry_fb_count += 1
            from task.manager import on_retry_fb
            on_retry_fb(player)
            player.save()
            player.sync()
            rsp.success = True
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.REFRESH_FB)
    def refresh_fb(self, msgtype, body):
        from protocol.poem_pb import RefreshFbRequest, RefreshFbResponse
        from reward.manager import apply_reward, RewardType, AttrNotEnoughError
        from scene.manager import get_fb_info, get_refresh_rest_count
        from scene.manager import get_refresh_cost, refresh_fb
        req = RefreshFbRequest()
        req.ParseFromString(body)
        player = self.player
        today_ts = int(time.mktime(datedate.today().timetuple()))
        if get_refresh_rest_count(player, req.fbID, today=today_ts) <= 0:
            return fail_msg(msgtype, reason='刷新次数已用完')
        if req.fbID not in player.fbscores:
            return fail_msg(msgtype, reason='无效的副本ID')
        try:
            apply_reward(
                player,
                {},
                cost={
                    'gold': get_refresh_cost(
                        player,
                        req.fbID,
                        today=today_ts)},
                type=RewardType.RefreshFB)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason='钻石不足')
        refresh_fb(player, req.fbID)
        player.save()
        player.sync()
        rsp = RefreshFbResponse(fbInfo=poem_pb.FbInfo(
            **get_fb_info(player, req.fbID, today=today_ts)
        ))
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.BEST_CLEARANCE)
    def best_clearance(self, msgtype, body):
        from scene.manager import get_best_clearance
        req = poem_pb.BestClearanceRequest()
        req.ParseFromString(body)
        rsp = poem_pb.BestClearanceResponse()
        info = get_best_clearance(req.fbID)
        if info:
            info = dict(info)
            fight = poem_pb.Fight()
            try:
                fight.ParseFromString(info.pop("fight"))
                info["fight"] = fight
                rsp.info = poem_pb.BestClearance(**info)
            except KeyError:
                pass
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.END_FB)
    def end_fb(self, msgtype, body):
        '''关卡结算'''
        from reward.manager import parse_reward_msg, RewardType
        from reward.manager import parse_reward
        from config.configs import FbInfoConfig, PetConfig, get_config
        from config.configs import SceneInfoConfig
        from config.configs import DlcFbInfoConfig
        from scene.manager import set_fb_score, validate_prevs, is_first
        from scene.manager import is_last_of_scene, get_fb_info
        from scene.manager import get_today_count, get_cost_count_cost
        from scene.manager import get_scene_info
        from scene.constants import TransFbType, FbType
        from scene.constants import SceneSubType
        from explore.constants import DlcFbType
        from fight.cache import cache_fight_response
        from fight.cache import get_cached_fight_response
        t = time.time()
        player = self.player
        req = poem_pb.EndFbRequest()
        req.ParseFromString(body)
        from entity.manager import save_guide
        save_guide(player, req.guide_type)  # 保存新手引导进度
        if req.fbID not in settings.FIGHT_VERIFY_SKIP_FB:
            from fightverifier.direct_verifier import verify
            send_fight_verify(player, req.fight, req.fbID)
            dlc_config = get_config(DlcFbInfoConfig).get(req.fbID)
            if dlc_config and dlc_config.type == DlcFbType.Social:
                pass
            else:
                if not verify(player, req.fight):
                    return fail_msg(
                        msgtype, msgTips.FAIL_MSG_FIGHT_VERIFY_FAILED)
        from player.model import PlayerFightLock
        if not PlayerFightLock.unlock(player.entityID, req.verify_code):
            logger.debug("invalid verify_code: {}".format(req.verify_code))
            cached = get_cached_fight_response(player, req.verify_code)
            if cached is not None:
                rsp = poem_pb.EndFbResponse()
                rsp.ParseFromString(cached)
                return success_msg(msgtype, rsp)
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if req.fbID != player.currentfbID:
            if req.fbID not in player.fbreward:
                return fail_msg(msgtype, reason='无效的关卡ID:{}'.format(req.fbID))
        reward = parse_reward_msg(req)
        s = player.fbreward.get(req.fbID)
        if not s:
            return fail_msg(msgtype, reason='没有进入副本，无效的通关')
        enter_rsp = poem_pb.EnterFbResponse()
        enter_rsp.ParseFromString(str(s))
        combine = []
        for d in enter_rsp.drops:
            combine.extend(d.must + d.maybe)
        real_reward = parse_reward(
            enter_rsp.rewards + combine
        )
        # assert reward < fbreward
        logger.debug('want %r', reward)
        logger.debug('real %r', real_reward)
        slate = reward.get('slate', 0)  # 只比对客户端的slate
        if slate:
            logger.debug('want %r', reward)
            logger.debug('real %r', real_reward)
            assert slate <= real_reward.get('slate', 0)
        else:
            try:
                del real_reward['slate']
            except KeyError:
                pass
        configs = get_config(FbInfoConfig)
        config = configs.get(req.fbID)
        if config.sp:
            cost = {'sp': config.sp}
        else:
            cost = {}
        today_ts = int(time.mktime(datedate.today().timetuple()))
        # 付费次数消耗
        if get_today_count(player, req.fbID) >= config.max:
            cost['gold'] = get_cost_count_cost(
                player,
                req.fbID,
                today=today_ts)
            # 付费购买次数记录
            role_custom(
                player=player,
                type=role_custom.Consume,
                arg1=ujson.dumps({
                    'type': RewardType.FB,
                    'cost': cost,
                    'is_first_consume': int(not player.consume_count),
                }))
            player.consume_count += 1
        # o_pets = set(player.pets.keys())
        first = is_first(player, req.fbID)
        result = apply_reward(
            player,
            real_reward,
            cost=cost,
            type=RewardType.FB)
        record_cost_sp(player, config.sp)
        rsp = poem_pb.EndFbResponse()
        # 检测是否该场景最后一关
        last = is_last_of_scene(player, req.fbID)
        rsp.isFirst = first and last
        player.currentfbID = 0
        if not req.fight.player_death_count:
            score = 3
        elif req.fight.player_death_count in (1, 2):
            score = 2
        else:
            score = 1
        if config.type == FbType.Dlc:
            # NOTE 最高score为1，与副本不一致
            score = 1
        # patch guide fb
        if req.fbID == 100115:
            score = 3
        set_fb_score(player, req.fbID, score)
        if config.type == FbType.Dlc:
            from explore.dlc import set_dlc_progress
            set_dlc_progress(player, req.fbID)
            from task.manager import on_end_dlc_fb, on_dlc_score
            on_end_dlc_fb(player, req.fbID)
            on_dlc_score(player)
        # 任务在set_fb_score前操作是因为任务有一个开启副本的条件
        from task.manager import on_end_fb_count, on_end_spec_fb_count
        on_end_fb_count(player, req.fbID)
        on_end_spec_fb_count(player, req.fbID)
        for post in config.post:  # 检查新开启的关卡
            if validate_prevs(player, post):
                if first:  # 只在刚开启时发送
                    info = get_fb_info(player, post, today=today_ts)
                    rsp.newFbInfos.add(isNew=True, **info)
                    if last:
                        rsp.newSceneInfo = get_scene_info(
                            player, info['sceneID'])
                if configs[post].type == configs[req.fbID].type:
                    rsp.nextID = post  # 取得相同类型的下一关卡
        # 返回当前副本信息
        rsp.curFbInfo = poem_pb.FbInfo(
            **get_fb_info(player, req.fbID, today=today_ts)
        )
        rsp.stars = score  # 当前星星数
        rsp.curSceneInfo = poem_pb.SceneInfo(
            **get_scene_info(player, config.sceneID, today=today_ts)
        )
        try:
            del player.fbreward[req.fbID]
        except KeyError:
            pass
        player.save()
        player.sync()
        gm_logger.info({"fb": {
            "entityID": player.entityID,
            'type': TransFbType.get(config.type, config.type),
            "data": {"fbID": req.fbID}}})
        # 特殊精灵需要额外记录
        petList = result.get('petList', [])
        spec = []
        for each in petList:
            ID, _ = each
            info = get_config(PetConfig).get(ID)
            if info and not info.dtype:
                continue
            spec.append(each)
        role_custom(player=player, type=role_custom.FB, arg1=ujson.dumps({
            'fbID': req.fbID,
            'data': result,
            'ftype': config.type,
            'spec': spec,
        }))
        if config.type == FbType.Normal and req.fbID > player.fbprocess:
            player.fbprocess = req.fbID
        elif config.type == FbType.Campaign:
            now = int(time.time())
            scene = get_config(SceneInfoConfig).get(config.sceneID)
            if scene:
                if scene.subtype == SceneSubType.Dongtian:
                    player.dongtian_cd = now + get_cons_value("DongtianCD")
                elif scene.subtype == SceneSubType.Fudi:
                    player.fudi_cd = now + get_cons_value("FudiCD")
            from task.manager import on_dongtian_fudi_money
            on_dongtian_fudi_money(player, result.get("money", 0))
            from task.manager import on_dongtian_fudi_soul
            on_dongtian_fudi_soul(player, result.get("soul", 0))
        elif config.type == FbType.Trigger:
            player.trigger_event = 0
        elif config.type == FbType.Advanced:
            # from scene.manager import update_best_clearance
            # from gm.proxy import proxy
            # if update_best_clearance(req.fbID, {
            #         "entityID": player.entityID, "score": score,
            #         "level": player.level, "name": player.name,
            #         "time": t, "fight": str(req.fight.SerializeToString())}):
            #     proxy.sync_best_clearance(req.fbID)
            if req.fbID > player.fbadvance:
                player.fbadvance = req.fbID
        elif config.type == FbType.Maze:
            player.mazes.remove(player.mazes[player.maze_boss_cache])
            player.touch_mazes()
            player.maze_boss_cache = -1
        from mall.manager import trigger_mall
        trigger_mall(player, rsp)
        from faction.manager import donate_sp
        donate_sp(player, config.sp)
        from explore.trigger import trigger_event
        rsp.event_type = trigger_event(player)
        from friend.manager import trigger_friendfb
        friendfb = trigger_friendfb(player)
        if friendfb:
            from chat.manager import on_found_friendfb
            on_found_friendfb(player, friendfb['fbID'])
            rsp.openedFriendfb = True
        player.save()
        player.sync()
        t = time.time() - t
        logger.debug('end fb cost time %d' % t)
        cache_fight_response(player, req.verify_code, rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.RESUME_SP)
    def resume_sp(self, msgtype, body):
        '''在线玩家恢复“恢复类型”的属性'''
        p = self.player
        p.cycle([
            'sp',
            'mine_rob_count',
            'rank_rest_count',
            'treasure_count',
            'tap_rest_count',
            "skillpoint",
            "maze_rest_count",
        ])
        p.sync()
        p.save()
        return success_msg(msgtype, '')

    # @rpcmethod(msgid.TEST_PAY)
    def test_pay(self, msgtype, body):
        player = self.player
        req = poem_pb.TestPay()
        req.ParseFromString(body)
        assert req.count
        player.gold += req.count
        player.credits += req.count * 10
        player.save()
        player.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.GUIDE_TYPE_END)
    def save_guide_type(self, msgtype, body):
        from protocol.poem_pb import guideEnd
        req = guideEnd()
        req.ParseFromString(body)
        from entity.manager import save_guide
        save_guide(self.player, req.guide_type)
        return success_msg(msgtype, '')

    @rpcmethod(msgid.NOTICE)
    def notice(self, msgtype, body):
        # 公告
        rsp = get_notice_rsp()
        if not rsp:
            return fail_msg(msgtype, reason='没有公告内容')
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SLATE_INIT)
    def slateinit(self, msgtype, body):
        # 处理残晶领取奖励面板的初始化
        from protocol.poem_pb import ResponseSlateInit
        player = self.player
        rsp = ResponseSlateInit()

        for i in player.slatereward_getedset:
            rsp.ID.append(i)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SLATE_REWARD)
    def slatereward(self, msgtype, body):
        # 处理残晶奖励
        from config.configs import get_config, SlateRewardConfig
        from protocol.poem_pb import RequestSlateReward
        from reward.base import parse_reward, apply_reward
        from reward.constants import RewardType
        player = self.player
        req = RequestSlateReward()
        req.ParseFromString(body)
        items = get_config(SlateRewardConfig)
        if req.ID in player.slatereward_getedset:
            # 奖品已经领取过
            return fail_msg(msgtype, reason='该奖励已领取过')
        if player.slate < items[req.ID].number:
            # 用户所持有的残晶数不能少于对应奖励所需残晶数
            return fail_msg(msgtype, reason='用户所持残晶数不足')
        reward = parse_reward([{'type': items[req.ID].type,
                                'arg': items[req.ID].itemID,
                                'count': items[req.ID].amount}])
        apply_reward(player, reward, type=RewardType.SlateReward)
        player.slatereward_getedset.add(req.ID)
        player.set_dirty('slatereward_getedset')
        player.save()
        player.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.HEART_BEAT)
    def heart_beat(self, msgtype, body):
        from pvp.climb_tower import g_climbTowerManager
        p = self.player
        req = poem_pb.HeartBeat()
        req.ParseFromString(body)
        role_heartbeat(player=self.player)

        # 派驻结算
        g_climbTowerManager.tally_up(self.player)

        now = int(time.time())
        if settings.KICK_ACCLERATE:
            if req.timestamp >= now + 1:
                logger.info("heart beat too fast %d" % p.entityID)
                g_playerManager.kick_player(p.entityID)
                return
        rsp = poem_pb.HeartBeat(timestamp=now)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.VIP_DESCRIPTION)
    def vip_description(self, msgtype, body):
        from protocol.poem_pb import VipDescRequest, VipDescResponse
        from config.configs import VipPacksConfig
        from config.configs import get_config, VipConfig
        from mall.manager import get_vip_pack_rest_count
        p = self.player
        req = VipDescRequest()
        req.ParseFromString(body)
        configs = get_config(VipConfig)
        if req.vip not in configs:
            vip = configs[min(configs)]
        else:
            vip = configs[req.vip]
        rsp = VipDescResponse(desc=vip.description)
        config = get_config(VipPacksConfig)[configs[req.vip].giftID]
        info = dict(config._asdict())
        info["rewards"] = build_reward(parse_reward(info["rewards"]))
        info["count"] = get_vip_pack_rest_count(p, config.ID)
        rsp.pack = poem_pb.VipPack(**info)
        return success_msg(msgtype, rsp)

    # {{{ 充值
    @rpcmethod(msgid.RECHARGE_LIST)
    def recharge_list(self, msgtype, body):
        p = self.player
        sdktype = username2type(p.username)
        label = username2label(p.username)
        logger.debug("sdktype {}".format(sdktype))
        if not sdktype:
            logger.warning("Unknown sdktype %s", p.username)
        req = poem_pb.RechargeListRequest()
        req.ParseFromString(body)
        rsp = poem_pb.RechargeListResponse()
        logger.debug("recharge list {}".format(req))
        if req.type == RechargeType.LimitedPacks:
            info = get_limited_packs_time()
            if not info:
                return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
            if info.start > p.limited_packs_last_time or \
                    info.end <= p.limited_packs_last_time:
                p.limited_packs_used_count = 0
                p.sync()
                p.save()
            rsp.start = info.start
            rsp.end = info.end
        elif req.type == RechargeType.TimeLimitedPacks:
            info = get_timelimited_packs_time()
            if not info:
                return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        elif req.type in (
                RechargeType.TriggerPacks1, RechargeType.TriggerPacks2):
            if not p.trigger_packs_flag or p.trigger_packs_buy_count >= 1:
                return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
            # 只触发一次
            if p.trigger_packs_flag:
                p.trigger_packs_flag = False
                p.save()
                p.sync()
        # if not req.type or req.type in (
        #         RechargeType.MonthlyCard30,
        #         RechargeType.Normal):
        #     types = (RechargeType.MonthlyCard30, RechargeType.Normal)
        else:
            types = [
                RechargeType.Normal,
                RechargeType.Monthcard1,
                RechargeType.Monthcard2,
                RechargeType.Weekscard1,
                RechargeType.Weekscard2]
        sdkconfigs = get_config(RechargeBySdktypeConfig).get(sdktype, [])
        labconfigs = get_config(RechargeByLabelConfig).get(label, [])
        ids = {e.id for e in sdkconfigs} & {e.id for e in labconfigs}
        configs = get_config(RechargeConfig)
        if "lj" in settings.SDK:
            lj_callback = settings.SDK['lj']['callback'] if label else ""
        else:
            lj_callback = ""
        for id in sorted(list(ids)):
            item = configs[id]
            payload = item._asdict()
            payload.pop('sdktype', None)
            is_first = payload['id'] not in self.player.bought_recharges
            if item.type in types:
                if item.type == RechargeType.MonthlyCard30:
                    if self.player.monthly_card_30:
                        payload['general_cmd'] = '月卡生效中，剩余%s天' %\
                            self.player.monthly_card_30
                        payload['cmd1'] = payload['general_cmd']
                elif item.type == RechargeType.Monthcard1:
                    if p.monthcard1:
                        payload['general_cmd'] = payload['general_cmd'].format(
                            p.monthcard1
                        )
                        payload["cmd1"] = payload['general_cmd']
                    else:
                        # payload['cmd1'] = payload['cmd1'].format(
                        #     get_cons_value("MonthcardGain1"),
                        #     get_cons_value("MonthcardDailyGain1")
                        # )
                        payload['general_cmd'] = payload['cmd1']
                elif item.type == RechargeType.Monthcard2:
                    if p.monthcard2:
                        payload['general_cmd'] = payload['general_cmd'].format(
                            p.monthcard2
                        )
                        payload['cmd1'] = payload['general_cmd']
                    else:
                        # payload['cmd1'] = payload['cmd1'].format(
                        #     get_cons_value("MonthcardGain2"),
                        #     get_cons_value("MonthcardDailyGain2")
                        # )
                        payload['general_cmd'] = payload['cmd1']
                elif item.type == RechargeType.Weekscard1:
                    if p.weekscard1:
                        payload['general_cmd'] = payload['general_cmd'].format(
                            p.weekscard1
                        )
                        payload['cmd1'] = payload['general_cmd']
                    else:
                        # payload['cmd1'] = payload['cmd1'].format(
                        #     get_cons_value("WeekscardGain1"),
                        #     get_cons_value("WeekscardDailyGain1")
                        # )
                        payload['general_cmd'] = payload['cmd1']
                elif item.type == RechargeType.Weekscard2:
                    if p.weekscard2:
                        payload['general_cmd'] = payload['general_cmd'].format(
                            p.weekscard2
                        )
                        payload['cmd1'] = payload['general_cmd']
                    else:
                        # payload['cmd1'] = payload['cmd1'].format(
                        #     get_cons_value("WeekscardGain2"),
                        #     get_cons_value("WeekscardDailyGain2")
                        # )
                        payload['general_cmd'] = payload['cmd1']
                rsp.items.add(
                    is_first=is_first,
                    lj_callback=lj_callback,
                    **payload)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SDK_PAY_ENABLE)
    def sdk_pay_enable(self, msgtype, body):
        rsp = poem_pb.SDKPayEnable()
        rsp.pay = settings.PAY
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SDK_PAY_START)
    def sdk_pay_start(self, msgtype, body):
        assert settings.PAY, "充值关闭"
        req = poem_pb.SDKStartPayRequest()
        req.ParseFromString(body)
        p = self.player
        logger.debug("request: {}".format(req))
        allows = (poem_pb.SDK_YY, poem_pb.SDK_YY_IOS, )
        configs = get_config(RechargeConfig)
        sdktype = username2type(p.username)
        label = username2label(p.username)
        sdkconfigs = get_config(RechargeBySdktypeConfig).get(sdktype, [])
        labconfigs = get_config(RechargeByLabelConfig).get(label, [])
        ids = {e.id for e in sdkconfigs} & {e.id for e in labconfigs}
        if not ids:
            return fail_msg(msgtype, msgTips.SUCCESS_MSG_PAY_FAIL)
        configs = {configs[c].goodsid: configs[c] for c in ids}
        goods = configs.get(req.goodsid)
        if not goods:
            return fail_msg(msgtype, msgTips.SUCCESS_MSG_PAY_FAIL)
        if goods.type == RechargeType.MonthlyCard30:
            if p.monthly_card_30:
                msg = fail_msg(msgid.SDK_PAY_START, reason='已经购买过月卡了。')
                g_playerManager.sendto(p.entityID, msg)
                return
        elif goods.type == RechargeType.LimitedPacks:
            now = int(time.time())
            info = get_limited_packs_time(now)
            if not info:
                return fail_msg(msgtype, msgTips.SUCCESS_MSG_PAY_FAIL)
            if p.limited_packs_used_count >= info.count:
                return fail_msg(msgtype, msgTips.SUCCESS_MSG_PAY_FAIL)
        elif goods.type == RechargeType.TimeLimitedPacks:
            now = int(time.time())
            info = get_timelimited_packs_time(now)
            if not info:
                return fail_msg(msgtype, msgTips.SUCCESS_MSG_PAY_FAIL)
            if p.timelimited_packs_last_time >= info.start and\
                    p.timelimited_packs_last_time < info.end:
                return fail_msg(msgtype, msgTips.SUCCESS_MSG_PAY_FAIL)
        elif goods.type in (
                RechargeType.TriggerPacks1,
                RechargeType.TriggerPacks2):
            if p.trigger_packs_buy_count >= 1:
                return fail_msg(msgtype, reason="已经购买过了。")
            from config.configs import LevelupConfig
            info = get_config(LevelupConfig).get(p.level)
            if not info:
                return fail_msg(msgtype, msgTips.SUCCESS_MSG_PAY_FAIL)
            if goods.type == RechargeType.TriggerPacks2:
                if p.level < info.triggerPacks2:
                    return fail_msg(msgtype, msgTips.SUCCESS_MSG_PAY_FAIL)
            elif goods.type == RechargeType.TriggerPacks1:
                if p.level < info.triggerPacks1:
                    return fail_msg(msgtype, msgTips.SUCCESS_MSG_PAY_FAIL)
            # NOTE 支付回调问题 不让重复买
            p.trigger_packs_buy_count += 1
            p.save()
            p.sync()
        # 测试模式充值
        if req.sdkType in allows and req.goodsid is not None and getattr(
                settings,
                'TEST_PAY',
                False):
            sid = ''
            rs = give_goods(p, goods)
            rsp = poem_pb.PayResult(
                success=True, roleID=p.entityID, userID=0,
                payID=sid, goods=0,
                count=rs["gold"], data="")
            g_playerManager.sendto(
                p.entityID,
                success_msg(msgtype, poem_pb.SDKStartPayResponse(serialNo=sid)))
            g_playerManager.sendto(
                p.entityID, success_msg(msgid.SDK_PAY_RESULT, rsp))
            return
        else:
            # 唯一且包含时间戳信息
            sid = str(objectid.ObjectId())
            from sdk.payment import gen_payment
            from session.utils import sdk_username
            sdkorderid = sdk_username(req.sdkType, sid)
            # 记录支付订单号
            result = gen_payment(
                sdkorderid,
                p.entityID,
                req.sdkType,
                req.goodsid,
                goods.amount)
            if not result:
                return fail_msg(
                    msgid.SDK_PAY_START,
                    msgTips.FAIL_MSG_SDK_START_PAY_FAILED)
            self.orderindex += 1
        logger.info("orderid `%s`", sid)
        return success_msg(msgtype, poem_pb.SDKStartPayResponse(serialNo=sid))

    @rpcmethod(msgid.TASK_LIST)
    def task_list(self, msgtype, body):
        from task.manager import get_task_list_by_type
        from protocol.poem_pb import TaskListRequest, TaskList
        req = TaskListRequest()
        req.ParseFromString(body)
        rsp = TaskList()
        today = datedate.today()
        get_task_list_by_type(
            self.player, req.type,
            req.subtype, today, rsp=rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.TASK_RECV_REWARD)
    def task_recv_reward(self, msgtype, body):
        from protocol.poem_pb import TaskRecvRewardRequest
        from protocol.poem_pb import TaskRecvRewardResponse
        from protocol.poem_pb import Task
        from config.configs import get_config
        from config.configs import TaskConfig
        from config.configs import TaskByTypeConfig
        from config.configs import TaskByGroupConfig
        from reward.manager import RewardType
        from reward.manager import open_reward
        from reward.manager import combine_reward
        from task.manager import get_task_info
        from task.manager import is_end
        from task.manager import get_daily_sp_info
        from task.manager import TaskType
        from task.manager import DailySPState
        from task.manager import is_open
        req = TaskRecvRewardRequest()
        req.ParseFromString(body)
        from entity.manager import save_guide
        save_guide(self.player, req.guide_type)
        configs = get_config(TaskConfig)
        config = configs.get(req.ID)
        if not config:
            return fail_msg(msgtype, reason='没有这个任务。')
        # 检查组，同组都完成，才可以领取
        if config.type == TaskType.Noob:
            group = get_config(TaskByGroupConfig).get(config.groupID, [])
        else:
            group = [config]
        if config.type == TaskType.DailySP:
            index, state = get_daily_sp_info()
            if state != DailySPState.Open:
                return fail_msg(msgtype, reason='已经超过领取时间了。')
            types = get_config(TaskByTypeConfig).get(TaskType.DailySP, [])
            if not types:
                return fail_msg(msgtype, reason='没有完成这个任务。')
            if [i.ID for i in types].index(req.ID) != index:
                return fail_msg(msgtype, reason='还没有到达领取的时间。')
            if req.ID in self.player.task_sp_daily_receiveds:
                return fail_msg(msgtype, reason='已经领取过这个奖励了。')
            self.player.task_sp_daily_receiveds.add(req.ID)
        elif not all([i.ID in self.player.taskrewards for i in group]):
            return fail_msg(msgtype, reason='没有完成这个任务。')
        elif not config:
            return fail_msg(msgtype, reason='没有完成这个任务。')
        rsp = TaskRecvRewardResponse()
        drops = filter(
            lambda s: s, [j.drop for j in [configs[i.ID] for i in group]])
        reward = open_reward(RewardType.Task, *drops)
        result = reward.apply_after()
        from explore.dlc import get_campaign_info
        from config.configs import get_config
        from config.configs import DlcTaskConfig
        dlc_task = get_config(DlcTaskConfig).get(req.ID)
        if dlc_task:
            result = combine_reward(result, dlc_task.rewards)
        apply_reward(self.player, result, type=RewardType.Task)
        # result = reward.apply(self.player)
        logger.debug('recv task reward {}'.format(result))
        today = datedate.today()
        try:
            for i in group:
                self.player.taskrewards.remove(i.ID)
        except KeyError:
            pass
        from task.manager import on_dlc_score
        on_dlc_score(self.player)
        if config.type == TaskType.Dlc:
            if dlc_task:
                result = combine_reward(result, dlc_task.rewards)
                cd = dlc_task.cd
                dlcID = dlc_task.dlcID
                now = int(time.time())
                self.player.dlc_tasks_cd[dlcID] = now + cd
                rsp.campaign = get_campaign_info(self.player, dlc_task.dlcID)
        if not is_end(self.player, req.ID, today):
            next = req.ID
        elif config.post:
            next = config.post
        else:
            next = None
        if next and is_open(self.player, next):
            rsp.next = Task(**get_task_info(self.player, next, today))
        # logger.debug('recv task rsp {}'.format(rsp))
        # 重置任务进度
        from task.manager import on_point
        on_point(self.player, result.get("point", 0))
        self.player.save()
        self.player.sync()
        logger.debug('recv campaign {}'.format(rsp.campaign))
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.TASK_SIGN_UP)
    def task_sign_up(self, msgtype, body):
        from protocol.poem_pb import TaskSignUpRequest, TaskRecvRewardResponse
        from task.manager import on_sign_up
        req = TaskSignUpRequest()
        req.ParseFromString(body)
        player = self.player
        rsp = TaskRecvRewardResponse()
        if req.patch:
            from reward.manager import apply_reward, RewardType, AttrNotEnoughError
            if player.task_rest_patch_sign_up_count:
                try:
                    apply_reward(player, {}, {'gold': 20}, RewardType.Signup)
                except AttrNotEnoughError:
                    return fail_msg(msgtype, reason='钻石不足')
                on_sign_up(player)
                player.task_used_patch_sign_up_count += 1
            else:
                return fail_msg(msgtype, reason='没有补签次数了')
        else:
            today = datedate.today()
            if player.task_last_sign_up_time:
                last = datedate.fromtimestamp(player.task_last_sign_up_time)
            else:
                last = None
            if last != today:
                on_sign_up(player)
                player.task_last_sign_up_time = int(
                    time.mktime(
                        today.timetuple()))
            else:
                return fail_msg(msgtype, reason='今日已经签到过了')
        player.save()
        player.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CLEANFB)
    def cleanfb(self, msgtype, body):
        req = poem_pb.CleanFbRequest()
        req.ParseFromString(body)
        count = req.cleantime or 1
        CLEAN_GOLD = 1 * count
        p = self.player
        from entity.manager import save_guide
        save_guide(p, req.guide_type)
        info = get_config(FbInfoConfig)[req.fbID]
        if get_fb_score(p, info.ID) != 3:
            return fail_msg(msgtype, reason='三星通关副本才能扫荡')
        if p.is_pets_full():
            return fail_msg(msgtype, reason='背包已满，请扩充背包')
        if get_today_remain_count(p, info.ID) < count:
            return fail_msg(msgtype, reason='扫荡次数大于该副本今日剩余挑战次数')
        if p.sp < (info.sp * count):
            return fail_msg(msgtype, reason='能量不足')
        # scene = get_config(SceneInfoConfig)[info.sceneID]
        # if scene.subtype:
        #     return fail_msg(msgtype, reason="不允许扫荡")
        if info.type == FbType.Campaign:
            from config.configs import ExSceneInfoConfig
            ex_scene = get_config(ExSceneInfoConfig).get(info.sceneID)
            if not ex_scene:
                return fail_msg(msgtype, reason='活动还没有开启')
            from scene.manager import is_open
            if not is_open(ex_scene.cycle, ex_scene.days):
                return fail_msg(msgtype, reason='活动还没有开启')
            from scene.manager import get_scene_today_remain_count
            if count > get_scene_today_remain_count(p, info.sceneID):
                return fail_msg(msgtype, reason='超过今日最大挑战次数')
            once_need_vip = True
            enough_vip = bool(p.vip >= p.clean_campaign_vip)
            CLEAN_LIMIT = 10
        else:
            once_need_vip = False
            enough_vip = bool(get_config(VipConfig)[p.vip].can_cleanfb)
            CLEAN_LIMIT = 10
        if req.usegold:
            # count = 1
            if p.gold + p.cleanfb < CLEAN_GOLD:
                return fail_msg(msgtype, reason='钻石不足')
            if p.cleanfb:
                cleanfb = min(count, p.cleanfb)
                gold = CLEAN_GOLD - cleanfb
                cost = {
                    'sp': info.sp * count,
                    'cleanfb': cleanfb,
                    'gold': gold,
                }
            else:
                cost = {
                    'sp': info.sp * count,
                    'gold': CLEAN_GOLD,
                }
        else:
            if count > min(CLEAN_LIMIT, info.max) or count <= 0:
                return fail_msg(msgtype, reason='无效扫荡次数')
            cost = {'cleanfb': count, 'sp': info.sp * count}
        if count == 1:
            # 活动副本单次扫荡也需要vip
            if once_need_vip and not enough_vip:
                return fail_msg(msgtype, reason='vip等级不足')
        else:
            if not enough_vip:
                return fail_msg(msgtype, reason='vip等级不足')
        rsp = poem_pb.CleanFbResponse()
        rsp.cleanfbresult = cleanfbs(p, info.ID, count, cost)
        sp = cost.get('sp', 0)
        record_cost_sp(p, sp)
        from mall.manager import trigger_mall
        trigger_mall(p, rsp)
        from faction.manager import donate_sp
        donate_sp(p, sp)
        from explore.trigger import trigger_event
        rsp.event_type = trigger_event(p)
        from friend.manager import trigger_friendfb
        friendfb = trigger_friendfb(p)
        if friendfb:
            from chat.manager import on_found_friendfb
            on_found_friendfb(p, friendfb['fbID'])
            rsp.openedFriendfb = True
        from task.manager import on_end_fb_count, on_end_spec_fb_count
        on_end_fb_count(p, info.ID, count)
        on_end_spec_fb_count(p, info.ID, count)
        p.clear_power()
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.GIFTKEY)
    def giftkey(self, msgtype, body):
        from protocol.poem_pb import Giftkey, GiftkeyResponse
        from config.configs import get_config, GiftkeyConfig
        from reward.manager import open_reward, build_reward_msg, RewardType
        from giftkey import use_key, InvalidGiftkeyError, ExceedUseCountError, ExceedDeallineError
        player = self.player
        req = Giftkey()
        req.ParseFromString(body)
        try:
            giftID = use_key(player, req.key)
        except InvalidGiftkeyError:
            return fail_msg(msgtype, reason='无效的兑换码')
        except ExceedUseCountError:
            return fail_msg(msgtype, reason='已经达到最大兑换次数了')
        except ExceedDeallineError:
            return fail_msg(msgtype, reason='已经超过有效期了')
        gift = get_config(GiftkeyConfig)[giftID]
        reward = open_reward(RewardType.Giftkey, gift)
        result = reward.apply(player)
        player.save()
        player.sync()
        rsp = GiftkeyResponse()
        build_reward_msg(rsp, result)
        gm_logger.info(
            {'giftkey': {'entityID': player.entityID, 'giftkey': req.key}})
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.PET_PATCH_CHANGE)
    def patch_change(self, msgtype, body):
        '''精灵兑换'''
        from config.configs import get_config
        from config.configs import MatConfig, PetConfig, NewEquipConfig
        player = self.player
        req = poem_pb.RequestChange()
        req.ParseFromString(body)
        from entity.manager import save_guide
        save_guide(player, req.guide_type)
        mat_configs = get_config(MatConfig)
        if req.id not in mat_configs:
            return fail_msg(msgtype, reason='不存在的物品ID')
        mat_config = mat_configs[req.id]
        from reward.base import apply_reward
        from reward.constants import RewardType
        from pet.constants import MType
        from mat.constants import MatType
        if mat_config.type == MatType.EquipPatch:
            equip_config = get_config(NewEquipConfig)[mat_config.arg]
            mat = player.mats.get(mat_config.ID, 0)
            if mat < equip_config.piece_num:
                count = 1
            else:
                count = mat // equip_config.piece_num
            gain = {"equipList": [[
                equip_config.prototypeID, count]]}
            cost = {"matList": [[
                mat_config.ID, equip_config.piece_num * count]]}
        else:
            pet_configs = get_config(PetConfig)
            pet_config = pet_configs[mat_config.arg]
            mat = player.mats.get(mat_config.ID, 0)
            if mat < pet_config.need_patch:
                count = 1
            else:
                count = mat // pet_config.need_patch
            if pet_config.mtype == MType.Normal:
                if player.is_pets_full():
                    return fail_msg(msgtype, reason='无法兑换精灵，请扩容背包')
                gain = {'petList': [[pet_config.prototypeID, count]]}
            else:
                gain = {'matList': [[mat_config.arg2, count]]}
            cost = {'matList': [[
                mat_config.ID, pet_config.need_patch * count]]}
        try:
            extra = {}
            apply_reward(
                player, gain,
                cost=cost,
                type=RewardType.PatchChange,
                extra=extra)
        except MatNotEnoughError:
            return fail_msg(msgtype, reason='碎片不足，不能兑换')
        player.save()
        player.sync()
        rewards = build_reward(gain)
        from chat.manager import on_news_pet_quality_compose
        on_news_pet_quality_compose(player, rewards)
        from chat.manager import on_news_pet_special_compose
        on_news_pet_special_compose(player, rewards)
        from chat.manager import on_news_equip_quality_compose
        on_news_equip_quality_compose(player, rewards)
        from task.manager import on_patch_exchange
        for each in extra.get("pets"):
            on_patch_exchange(player, each)
        return success_msg(msgtype, '')

    @rpcmethod(msgid.TOTAL_LOGIN_REWARD)
    def total_login_reward(self, msgtype, body):
        p = self.player
        from config.configs import get_config, LoginRewardConfig
        from reward.manager import parse_reward, RewardType, apply_reward
        configs = get_config(LoginRewardConfig)
        ungets = sorted(set(configs).difference(p.totallogin_end))
        curr = None
        gets = []  # 可以领取
        for id in ungets:
            config = configs[id]
            if p.totallogin >= config.loginday:
                curr = config.dropID
                gets.append(config)
            else:
                break
        if gets:
            rewards = parse_reward([{
                "type": i.type,
                "arg": i.itemID,
                "count": i.amount} for i in gets])
            apply_reward(p, rewards, type=RewardType.TotalLoginReward)
            for i in gets:
                p.totallogin_end.add(i.dropID)
            p.save()
            p.sync()
        if not curr:
            if p.totallogin_end:
                curr = max(p.totallogin_end)
            else:
                curr = min(configs)
        rsp = poem_pb.LoginRewardResponse()
        for k, v in configs.items():
            received = k in p.totallogin_end
            rsp.rewards.add(
                ID=v.dropID, reward={
                    "type": v.type,
                    "arg": v.itemID,
                    "count": v.amount,
                }, received=received)
        rsp.curr = curr
        rsp.pop = bool(gets)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.STAR_PACKS_INFO)
    def star_packs_info(self, msgtype, body):
        from config.configs import get_config, StarPacksConfig
        from scene.manager import get_fb_scores_by_chapter
        rsp = poem_pb.StarPacksInfo()
        p = self.player

        # 重置旧的数据
        if p.star_packs_version == 0:
            p.star_packs_end = set()
            p.star_packs_version = 1
            p.save()
            p.sync()

        logger.debug(p.star_packs_end)
        for k, v in get_config(StarPacksConfig).items():
            pack = rsp.packs.add(**v._asdict())
            rewards = [[x['type'], x['arg'], x['count']] for x in pack.rewards]
            pack.rewards = ujson.dumps(rewards)
            if k in p.star_packs_end:
                pack.state = poem_pb.StarPack.Taken
            elif get_fb_scores_by_chapter(p, v.sceneID) >= v.star:
                pack.state = poem_pb.StarPack.Available
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.STAR_PACKS_RECV)
    def star_packs_recv(self, msgtype, body):
        p = self.player
        req = poem_pb.StarPacksRecv()
        req.ParseFromString(body)
        from entity.manager import save_guide
        save_guide(p, req.guide_type)
        from config.configs import get_config, StarPacksConfig
        configs = get_config(StarPacksConfig)
        config = configs.get(req.id)
        if not config:
            return fail_msg(msgtype,
                            code=msgTips.FAIL_MSG_STAR_PACKS_NOT_EXISTS)
        if req.id in p.star_packs_end:
            return fail_msg(msgtype,
                            code=msgTips.FAIL_MSG_STAR_PACKS_TAKEN)
        from scene.manager import get_fb_scores_by_chapter
        star = get_fb_scores_by_chapter(p, config.sceneID)
        if star < config.star:
            return fail_msg(msgtype,
                            code=msgTips.FAIL_MSG_STAR_PACKS_UNAVAILABLE)
        from reward.manager import RewardType, parse_reward, apply_reward
        rewards = parse_reward(config.rewards)
        rewards = apply_reward(p, rewards, type=RewardType.StarPacks)
        p.star_packs_end.add(req.id)
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.COMPOSE)
    def compose(self, msgtype, body):
        from config.configs import ComposeMatConfig
        from config.configs import ComposePetConfig
        from config.configs import ComposeEquipConfig
        from config.configs import PetConfig
        from collections import defaultdict
        from reward.manager import open_reward, RewardType, NotEnoughError
        from lineup.manager import in_lineup
        req = poem_pb.ComposeRequest()
        req.ParseFromString(body)
        p = self.player
        pets, equips = [], []
        error_code = msgTips.FAIL_MSG_COMPOSE_NOT_ENOUGH_STUFFS
        if req.type == poem_pb.ComposeRequest.ComposePet:
            infos = get_config(PetConfig)
            configs = get_config(ComposePetConfig)
            config = configs[req.id]
            needs = {infos[i[0]].same: i for i in config.stuffs}
            pets = [p.pets[s] for s in req.stuffs]
            for pet in pets:
                if in_lineup(p, pet.entityID):
                    return fail_msg(msgtype, reason='阵上将不可作为材料')
                info = infos[pet.prototypeID]
                try:
                    prototypeID, breaklevel = needs[info.same]
                    info_ = infos[prototypeID]
                    quality = info_.rarity * 10 + info_.step
                    if info.rarity * 10 + info.step < quality:
                        return fail_msg(msgtype, error_code)
                except KeyError:
                    return fail_msg(msgtype, error_code)
                if pet.breaklevel < breaklevel:
                    return fail_msg(msgtype, error_code)
            if len(pets) != len(needs):
                return fail_msg(msgtype, error_code)
            reward = open_reward(RewardType.Compose, pet=config.id)
            reward.cost_after(p, money=config.money, soul=config.soul)
        elif req.type == poem_pb.ComposeRequest.ComposeEquip:
            config = get_config(ComposeEquipConfig).get(req.id)
            if not config:
                return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
            needs = {i[0]: i for i in config.stuffs}
            equips = [p.equips[s] for s in req.stuffs]
            groups = defaultdict(list)
            # 不会有两个一样的装备 NOTE
            for equip in equips:
                each = [equip.level, equip.step]
                groups[equip.prototypeID].append(each)
            for group, eqs in groups.items():
                _, need_level, need_step, need_count = needs.get(group)
                if need_count != len(eqs):
                    return fail_msg(msgtype, error_code)
                for equip_level, equip_step in eqs:
                    if equip_level < need_level or equip_step < need_step:
                        return fail_msg(msgtype, error_code)
            if len(equips) != len(needs):
                return fail_msg(msgtype, error_code)
            reward = open_reward(RewardType.Compose, equip=config.id)
            reward.cost_after(p, money=config.money, soul=config.soul)
        elif req.type == poem_pb.ComposeRequest.ComposeMat:
            configs = get_config(ComposeMatConfig)
            if not req.stuffs:
                return fail_msg(msgtype, error_code)
            stuff = req.stuffs[0]
            configs = get_config(ComposeMatConfig)
            config = configs[stuff]
            if not config.compose:
                return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
            if p.mats.get(stuff, 0) < config.count:
                return fail_msg(msgtype, error_code)
            reward = open_reward(RewardType.Compose, mat=config.compose)
            reward.cost_after(
                p, money=config.money, soul=config.soul,
                matList=[[stuff, config.count]])
        else:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        try:
            result = reward.apply(p)
        except NotEnoughError:
            return fail_msg(msgtype, error_code)
        if pets:
            p.del_pets(*pets)
        if equips:
            p.del_equips(*equips)
        rewards = build_reward(result)
        from chat.manager import on_pet_compose, on_equip_compose
        on_pet_compose(p, rewards)
        on_equip_compose(p, rewards)
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.FIRST_RECHARGE_INFO)
    def first_recharge_info(self, msgtype, body):
        from reward.manager import build_reward_msg
        from config.configs import FirstRechargeConfig
        config = get_config(FirstRechargeConfig)[0]
        p = self.player
        if not p.first_recharge_flag:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        rsp = poem_pb.FirstRechargeInfo(**config._asdict())
        build_reward_msg(rsp, parse_reward(config.rewards))
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FIRST_RECHARGE_RECV)
    def first_recharge_recv(self, msgtype, body):
        from reward.manager import RewardType
        from config.configs import FirstRechargeConfig
        from campaign.manager import trigger_timed_store
        config = get_config(FirstRechargeConfig)[0]
        p = self.player
        if p.first_recharge_recv:
            apply_reward(
                p, parse_reward(config.rewards),
                type=RewardType.FirstRecharge)
            p.first_recharge_flag = False
            trigger_timed_store(p)
            p.save()
            p.sync()
            return success_msg(msgtype, "")
        return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)

    @rpcmethod(msgid.GUIDE_REWARD_RECV)
    def guide_reward_recv(self, msgtype, body):
        p = self.player
        if p.guide_reward_flag:
            return fail_msg(msgtype, reason="已经领取过了")
        req = poem_pb.GuideRewardRecvRequest()
        req.ParseFromString(body)
        from entity.manager import save_guide
        save_guide(self.player, req.guide_type)
        result = apply_reward(
            p, {"gold": 888}, type=RewardType.GuideReward)
        rsp = poem_pb.GuideRewardRecvResponse()
        build_reward_msg(rsp, result)
        from task.manager import trigger_seven_task
        trigger_seven_task(p)
        from task.manager import on_login
        on_login(p)
        p.guide_reward_flag = True
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.GUIDE_DEFEAT_RECV)
    def guide_defeat_recv(self, msgtype, body):
        p = self.player
        if p.guide_defeat_flag:
            return fail_msg(msgtype, reason="已经领取过了")
        reward = open_reward(
            RewardType.GuideDefeat, get_cons_value("GuideDefeat"))
        result = reward.apply(p)
        rsp = poem_pb.GuideDefeatRecvResponse()
        build_reward_msg(rsp, result)
        p.guide_defeat_flag = True
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SCENE_REWARD_INFO)
    def scene_rewards_info(self, msgtype, body):
        from config.configs import get_config
        from config.configs import SceneInfoConfig
        req = poem_pb.SceneRewardsInfoReqeust()
        req.ParseFromString(body)
        config = get_config(SceneInfoConfig).get(req.id)
        if not config:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        reward = open_reward(RewardType.SceneRewards, config.drop)
        result = reward.apply_after()
        rsp = poem_pb.SceneRewardsInfoResponse()
        build_reward_msg(rsp, result)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SCENE_REWARD_RECV)
    def scene_rewards_recv(self, msgtype, body):
        p = self.player
        req = poem_pb.SceneRewardsRecvReqeust()
        req.ParseFromString(body)
        from entity.manager import save_guide
        save_guide(p, req.guide_type)  # 保存新手引导进度
        c = get_config(SceneInfoConfig).get(req.id)
        if not c:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if req.id in p.scene_rewards:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        rsp = poem_pb.SceneRewardsRecvResponse()
        if all(map(lambda s: s in p.fbscores, c.fbs)):
            if c.drop:
                reward = open_reward(RewardType.SceneRewards, c.drop)
                result = reward.apply(p)
            else:
                result = {}
            p.scene_rewards.add(req.id)
            p.save()
            p.sync()
            build_reward_msg(rsp, result)
        return success_msg(msgtype, rsp)

    def itunes_iap_validation_handle(self, msgtype, req):
        from itunesiap import Request, set_verification_mode
        from itunesiap.exceptions import InvalidReceipt, ItunesServerNotAvailable
        from session.utils import sdk_username
        from sdk.payment import end_payment, get_payment, gen_payment
        player = self.player
        try:
            # set_verification_mode('sandbox')
            request = Request(req.receipt)
            with request.verification_mode('review'):
                receipt = request.verify()
            logger.info(receipt)
            configs = get_config(RechargeConfig)
            goods = filter(lambda item: item.goodsid == receipt.product_id and item.sdktype == poem_pb.SDK_APP_IOS, configs.values())
            if len(goods) != 1:
                logger.error('Invalid goodsid: {},{}'.format(player.entityID, receipt.product_id))
                return False
            goods = goods[0]
            logger.debug(goods)
            sdkorderid = sdk_username(poem_pb.SDK_APP_IOS, receipt.transaction_id)
            payment = get_payment(sdkorderid)
            if not payment:
                result = gen_payment(
                    sdkorderid,
                    player.entityID,
                    poem_pb.SDK_APP_IOS,
                    receipt.product_id)
                payment = get_payment(sdkorderid)
            if payment.get('status', None) != 'SUCCESS':
                if not end_payment(sdkorderid):
                    logger.error('insert callback pay record failed %s' % sdkorderid)
                    return False
                payment = get_payment(sdkorderid)
                logger.debug(payment)
                data = {
                    "clientVersion": "",
                    "amount": goods.amount,
                    "orderNO": sdkorderid,
                    "_level": "",
                    "_username": "",
                    "_userID": 0,
                    "_entityID": player.entityID,
                    "result": 1}
                username = player.username
                userID = player.userID
                idfa = player.idfa
                appid = player.appid
                rs = pay_handler(player.entityID, username, payment["goodsid"], amount=int(goods.amount))
                if not rs:
                    return False
                logger.debug(rs)
                get_gold = rs["get_gold"]
                username = rs["username"]
                level = rs["level"]
                rsp = poem_pb.PayResult(
                    success=True, roleID=player.entityID, userID=0,
                    payID=receipt.transaction_id, goods=0,
                    count=get_gold, data=req.receipt)
                g_playerManager.sendto(
                    player.entityID, success_msg(msgid.SDK_PAY_RESULT, rsp))
                data.update(_username=username, _level=level)
                data.update(_gold=get_gold)
                role_credit(**data)
                gm_logger.info({'pay': {
                    'transaction_id': receipt.transaction_id,
                    'userID': userID,
                    'entityID': player.entityID,
                    'channel': player.channel,
                    'amount': goods.amount,
                    'gold': get_gold,
                    'idfa': idfa,
                    'appid': appid,
                    'username': username},
                    'payID': sdkorderid})
            if payment.get('status', None) == 'SUCCESS':
                response = poem_pb.iTunesStoreReceiptResponse()
                response.transaction_id = receipt.transaction_id
                response.successed = True
                g_playerManager.sendto(player.entityID, success_msg(msgtype, response))
        except InvalidReceipt:
            logger.warning('invalid receipt')

    @rpcmethod(msgid.ITUNES_IAP_VALIDATION)
    def itunes_iap_validation(self, msgtype, body):
        req = poem_pb.iTunesStoreReceiptRequest()
        req.ParseFromString(body)
        gevent.spawn(self.itunes_iap_validation_handle, msgtype, req)

    @rpcmethod(msgid.CHANGE_AVATAR_OR_BORDER)
    def change_avatar_or_border(self, msgtype, body):
        from mat.constants import MatType
        from config.configs import MatConfig
        p = self.player
        req = poem_pb.ChangeAvatarOrBorderRequest()
        req.ParseFromString(body)
        if not p.mats.get(req.id, 0):
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        config = get_config(MatConfig).get(req.id)
        if config.type == MatType.Avatar:
            p.prototypeID = req.id
        elif config.type == MatType.Border:
            p.borderID = req.id
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.MONTHCARD_INFO)
    def monthcard_info(self, msgtype, body):
        req = poem_pb.MonthcardInfoRequest()
        req.ParseFromString(body)
        if req.type == 1:
            types = (RechargeType.Monthcard1, RechargeType.Monthcard2)
        else:
            types = (RechargeType.Weekscard1, RechargeType.Weekscard2)
        rsp = poem_pb.MonthcardInfo()
        for type in types:
            if type == RechargeType.Monthcard1:
                item = rsp.items.add(
                    id=type, gain=get_cons_value("MonthcardGain1"),
                )
                daily_gain = get_cons_value("MonthcardDailyGain1")
            elif type == RechargeType.Monthcard2:
                item = rsp.items.add(
                    id=type, gain=get_cons_value("MonthcardGain2"),
                )
                daily_gain = get_cons_value("MonthcardDailyGain2")
            elif type == RechargeType.Weekscard1:
                item = rsp.items.add(
                    id=type, gain=get_cons_value("WeekscardGain1"),
                )
                daily_gain = get_cons_value("WeekscardDailyGain1")
            elif type == RechargeType.Weekscard2:
                item = rsp.items.add(
                    id=type, gain=get_cons_value("WeekscardGain2"),
                )
                daily_gain = get_cons_value("WeekscardDailyGain2")
            reward = open_reward(
                RewardType.Monthcard, daily_gain).apply_after()
            item.daily_gain = build_reward(reward)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.MONTHCARD_RECV)
    def monthcard_recv(self, msgtype, body):
        req = poem_pb.MonthcardRecv()
        req.ParseFromString(body)
        mapping = {
            RechargeType.Monthcard1: ('month', 1),
            RechargeType.Monthcard2: ('month', 2),
            RechargeType.Weekscard1: ("weeks", 1),
            RechargeType.Weekscard2: ("weeks", 2),
        }
        tags = mapping.get(req.id)
        if not tags:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        p = self.player
        monthcard_recv = getattr(p, "%scard_recv%d" % tags, 0)
        if monthcard_recv:
            return fail_msg(msgtype, reason="已领取")
        monthcard = getattr(p, "%scard%d" % tags, 0)
        if monthcard <= 0:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        drop = get_cons_value(
            "%scardDailyGain%d" % (tags[0].title(), tags[1]))
        reward = open_reward(RewardType.Monthcard, drop)
        result = reward.apply(p)
        setattr(p, "%scard%d" % tags, monthcard - 1)
        setattr(p, "%scard_recv%d" % tags, True)
        p.save()
        p.sync()
        rsp = poem_pb.MonthcardRecvResponse()
        build_reward_msg(rsp, result)
        return success_msg(msgtype, rsp)


class WorldService(
        BaseService,
        RoleService,
        MallService,
        PetService,
        MailService,
        PvpService,
        FactionService,
        EquipService,
        ChatService,
        ExploreService,
        FriendService,
        CampaignService,
        RankingService,
        GroupService,
        MatService,
        GemService):
    pass
