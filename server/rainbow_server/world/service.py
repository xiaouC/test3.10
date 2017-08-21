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

from player.manager import g_playerManager, Peer
from entity.manager import g_entityManager

from mall.service import MallService
from mail.service import MailService
from chat.service import ChatService
from player.service import RoleService

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

import settings


def cleanup(player):
    if not player:
        return
    PlayerOnlineIndexing.unregister(player.entityID)
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
                    player = g_entityManager.load_player(userID, req.entityID)
                    logger.info("reload player")
            if player:
                if player.userID != userID:  # 检验userid
                    self.peer.close()
                    logger.error("wrong userID %r, %r", player.userID, userID)
                else:
                    # 清理上一个socket，如果有的话
                    if g_playerManager.has_player(req.entityID):
                        g_playerManager.kick_player(player.entityID)
                        PlayerOnlineIndexing.update(settings.WORLD["ID"], player.entityID)
                        player.save()
                        logger.info("close last player")
                        # FIXME 因为kick player 把player 给 unload了
                        player = g_entityManager.load_player(userID, req.entityID)
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
            g_playerManager.sendto(entityID, fail_msg(msgtype, msgTips.FAIL_MSG_KICKED))
            g_playerManager.kick_player(entityID)
        clientVersion = req.clientVersion
        featureCode = req.featureCode
        clientIP, _ = self.peer._sock.getpeername() or ('', '')
        self.player = player = g_entityManager.load_player(self.userID, entityID, clientVersion, featureCode, clientIP)
        if not player:
            self.peer.sender(fail_msg(msgtype, msgTips.FAIL_MSG_LOAD_PLAYER))
            self.peer.close()
            return
        PlayerOnlineIndexing.update(settings.WORLD["ID"], player.entityID)
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

        # 发送公告
        notice_rsp = get_notice_rsp()
        g_playerManager.sendto(player.entityID,  success_msg(msgid.NOTICE, notice_rsp))

        sync_scene_infos(player)

        rsp = poem_pb.EnterResponse()
        rsp.ENABLE_GIFTKEY = settings.ENABLE_GIFTKEY  # cdkey
        rsp.REV = settings.REV
        rsp.time = int(time.time())
        self.peer.sender(success_msg(msgtype, rsp))

        gm_logger.info({'access': {'entityID': player.entityID,
                                   'type': 'login',
                                   'userID': player.userID,
                                   'username': player.username,
                                   'onlines': g_playerManager.count(),
                                   'username_alias': player.username_alias,
                                   'channel': player.channel}})

        from common.log import role_login
        role_login(player=player)

    @rpcmethod(msgid.NOTICE)
    def notice(self, msgtype, body):
        # 公告
        rsp = get_notice_rsp()
        if not rsp:
            return fail_msg(msgtype, reason='没有公告内容')
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.HEART_BEAT)
    def heart_beat(self, msgtype, body):
        p = self.player
        req = poem_pb.HeartBeat()
        req.ParseFromString(body)
        role_heartbeat(player=self.player)

        now = int(time.time())
        if settings.KICK_ACCLERATE:
            if req.timestamp >= now + 1:
                logger.info("heart beat too fast %d" % p.entityID)
                g_playerManager.kick_player(p.entityID)
                return
        rsp = poem_pb.HeartBeat(timestamp=now)
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


class WorldService(
        BaseService,
        RoleService,
        MallService,
        MailService,
        FactionService,
        ChatService,
        RankingService):
    pass
