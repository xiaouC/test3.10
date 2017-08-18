# coding:utf-8
import time
import logging
logger = logging.getLogger('pvp')
from datetime import date as datedate
from datetime import timedelta
import protocol.poem_pb as msgid
from yy.rpc import RpcService, rpcmethod
from yy.message.header import success_msg, fail_msg

from common import msgTips
from rank import g_rankManager, sync_rank
from reward.constants import RewardType
from protocol.poem_pb import (
    RewardData, ResponsePvpRank, RequestPvpRank,
    RequestPvpRewards, ResponsePvpRewards, PvpHistoryList,
    PvpReplayRequest
)
from player.model import PlayerRankRanking
from player.model import PlayerFightLock
from player.model import PlayerMineLock
# from player.model import PlayerLootLock
from player.model import PlayerSwapLock
from player.model import LockedError
from player.model import SWAP_LOCK_CD
from player.model import PlayerDailyLock
from player.model import PlayerRobmine1Ranking
from player.model import PlayerRobmine2Ranking
from player.model import PlayerDailyRankRanking
from player.model import PlayerClimbTowerRanking
from entity.manager import level_required
from reward.manager import apply_reward, build_reward_msg, build_reward
# from reward.manager import MatNotEnoughError
from reward.manager import AttrNotEnoughError
from reward.manager import parse_reward
from reward.manager import open_reward
from reward.manager import combine_reward
from gm.proxy import proxy
from player.manager import g_playerManager

from protocol import poem_pb
from rob import cost_player_products, search_targets, rob_target
from rob import get_curr_products
from rob import get_lineuptype_by_type

from pvp.manager import get_zombie
from pvp.manager import get_opponent_detail
from pvp.manager import get_opponent_detail_all
from pvp.manager import is_zombie
from pvp.manager import npc2zombie
from pvp.manager import send_fight_verify

from pvp.rank import get_pvprankcount
from pvp.rank import get_need_rank_by_ranking
from pvp.rank import get_grad

# from faction.model import Faction
from player.model import Player

from config.configs import get_config
from config.configs import PvpGradConfig
from config.configs import PvpGroupConfig
from config.configs import PvpSerialWinBuffConfig
from config.configs import NpcConfig
from config.configs import SwapFightRewardConfig
from config.configs import get_cons_value
from config.configs import SwapmaxrankConfig
from config.configs import ClimbTowerConfig
from config.configs import ClimbTowerChestConfig
from config.configs import ClimbTowerAccreditConfig
from pvp.constants import BuffType
from fightverifier.direct_verifier import verify
from fight.cache import get_cached_fight_response
from fight.cache import cache_fight_response
from lineup.constants import LineupType
from pvp.swap import g_swapManager
from pvp.daily import g_dailyManager
from campaign.manager import g_campaignManager
from chat.red import g_redManager
from player.model import PlayerAccreditLock

RANK_CD_INTERVAL = 10 * 60


class PvpService(RpcService):

    # {{{ 神魔争霸
    @rpcmethod(msgid.PVP_CLEAN_SEASON_REWARD)
    def pvp_clean_season_reward(self, msgtype, body):
        # 赛季奖励发放后， 发送确认信息
        p = self.player
        rsp = poem_pb.PvpReward()
        rsp.title = p.pvpseasonreward["title"]
        rsp.grad = p.pvpseasonreward.get("grad", 0)
        build_reward_msg(rsp, p.pvpseasonreward["reward"])
        p.pvpseasonreward = {}
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.PVP_CLEAN_CD)
    def clean_cd(self, msgtype, body):
        player = self.player
        try:
            apply_reward(player, {}, {'gold': 20}, RewardType.CleanRankCD)
            player.rank_cd = 0
            player.save()
            player.sync()
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason='钻石不足')
        return success_msg(msgtype, '')

    @rpcmethod(msgid.PVP_RANK_LIST)
    def get_rank_list(self, msgtype, body):
        req = RequestPvpRank()
        req.ParseFromString(body)
        player = self.player
        if req.type == RequestPvpRank.Top:
            count = 1
        else:
            count = 50
        if req.type == RequestPvpRank.Last:
            rankers = g_rankManager.get_last_rank_list(count=count)
        else:
            player.pvprank = PlayerRankRanking.get_rank(player.entityID)
            player.save()
            player.sync()
            if req.type == RequestPvpRank.Self:
                score = player.pvprank
            else:
                score = 0
            # NOTE req.index(page) -1 代表上一页， 1代表下一页
            # NOTE 现在只能查看当前页
            rankers = g_rankManager.get_rank_list(score, page=0, count=count)
        rsp = ResponsePvpRank()
        if not rankers:
            return success_msg(msgtype, rsp)
        # factionIDs = [i["factionID"] for i in rankers]
        # factions = Faction.batch_load(factionIDs, ["entityID", "name"])
        for i, ranker in enumerate(rankers[:count]):
            # faction = factions[i]
            # if not faction:
            #     faction_name = ''
            # else:
            #     faction_name = faction.name
            rsp.opponents.add(**ranker)
        if len(rankers) > count:
            rsp.hasnext = True
        logger.debug(rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.PVP_REWARD_LIST)
    def get_reward_list(self, msgtype, body):
        from config.configs import get_config
        from config.configs import PvpRewardConfig
        from config.configs import PvpRewardByGroupConfig
        configs = get_config(PvpRewardConfig)
        req = RequestPvpRewards()
        req.ParseFromString(body)
        rsp = ResponsePvpRewards()
        _, _, group = g_rankManager.get_current()
        IDs = [i.ID for i in get_config(PvpRewardByGroupConfig)[group]]
        for ID in IDs:
            config = configs[ID]
            rsp.items.add(
                title=config.content,
                rewards=[RewardData(**r) for r in config.rewards],
                start=config.condition[0],
                end=config.condition[1],
                grad_png=config.grad_png,
            )
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.PVP_HISTORY)
    def pvp_history(self, msgtype, body):
        rsp = PvpHistoryList()
        p = self.player
        for each in p.rank_history:
            #  可否复仇
            can_revenge = True
            if each['isActive'] or each['isWin'] or\
                    each['ID'] in p.rank_revenged_targets:
                can_revenge = False
            rsp.items.add(can_revenge=can_revenge, **each)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.PVP_REPLAY)
    def pvp_replay(self, msgtype, body):
        req = PvpReplayRequest()
        req.ParseFromString(body)
        raw = self.player.rank_fight_history.get(req.ID)
        if not raw:
            return fail_msg(msgtype, msgTips.FAIL_MSG_PVP_FIGHT_HISTORY_MISSED)
        rsp = poem_pb.PvpEndFightRequest()
        rsp.ParseFromString(raw)
        self.player.rank_passive_offline_count = 0  # 竞技场，离线期间被打次数
        self.player.save()
        self.player.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.PVP_PLAYER_LINEUPS)
    def pvp_player_lineup_details(self, msgtype, body):
        req = poem_pb.TargetDetailRequest()
        req.ParseFromString(body)
        detail = get_opponent_detail_all(req.entityID)
        if not detail:
            return fail_msg(msgtype, msgTips.FAIL_MSG_PLAYER_NOT_FOUND)
        totalbp = PlayerRankRanking.get_score(req.entityID) or 0
        detail['totalbp'] = totalbp
        detail['beMyFriend'] = req.entityID in self.player.friendset
        p = Player.simple_load(req.entityID, ['friend_applys'])
        p.friend_applys.load()
        detail['applied'] = self.player.entityID in p.friend_applys
        rsp = poem_pb.TargetDetailResponse(**detail)
        if not rsp:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        return success_msg(msgtype, rsp)

    # }}}

    # {{{ 神魔争霸 new
    @rpcmethod(msgid.PVP_RESET)
    @level_required(tag="pvp")
    def pvp_reset(self, msgtype, body):
        p = self.player
        if not p.rank_reset_rest_count:
            return fail_msg(msgtype, reason="重置次数不足")
        try:
            apply_reward(
                p, {}, {'gold': p.rank_reset_cost}, RewardType.PvpReset)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="钻石不足")
        p.rank_rest_count = p.fields['rank_rest_count'].default
        p.rank_reset_used_count += 1
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.PVP_TARGETS)
    @level_required(tag="pvp")
    def pvp_targets(self, msgtype, body):
        req = poem_pb.PvpTargetsRequest()
        req.ParseFromString(body)
        p = self.player
        logger.debug(req)
        if req.refresh:
            if req.usegold:
                try:
                    apply_reward(
                        p, {}, {"gold": p.rank_refresh_cost},
                        RewardType.PvpRefresh)
                except AttrNotEnoughError:
                    return fail_msg(msgtype, reason="钻石不足")
                else:
                    p.rank_refresh_used_count += 1
            else:
                now = int(time.time())
                if now < p.rank_refresh_cd:
                    return fail_msg(msgtype, reason="免费刷新冷却中")
                p.rank_refresh_cd = now + 10 * 60
                p.rank_serial_win_count = 0
                p.rank_serial_win_count_cd = 0
            p.rank_targets = []
            p.rank_defeated_targets.clear()
            p.save()
            p.sync()
        rsp = poem_pb.PvpTargets()
        targets = g_rankManager.get_rank_targets(p)
        players = [i for i in targets if not is_zombie(i)]
        scores = dict(zip(players, PlayerRankRanking.get_scores(players)))
        for t in targets:
            defeated = (t in p.rank_defeated_targets)
            details = get_opponent_detail(t, type=LineupType.DEF)
            details['defeated'] = defeated
            score = scores.get(details['entityID'])
            if score:
                details['totalbp'] = score
            rsp.targets.add(**details)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.PVP_START_FIGHT)
    @level_required(tag="pvp")
    def pvp_start_fight(self, msgtype, body):
        if not g_rankManager.is_open():
            return fail_msg(msgtype, msgTips.FAIL_MSG_PVP_CLOSED)
        p = self.player
        if not p.rank_rest_count:
            return fail_msg(msgtype, reason='挑战次数不足')
        req = poem_pb.PvpStartFightRequest()
        req.ParseFromString(body)
        if req.revenge:
            ID = "%d:%d" % (req.timestamp, req.id)
            for hist in p.rank_history:
                if hist['ID'] == ID:
                    if hist['isActive'] or hist["isWin"] \
                            or ID in p.rank_revenged_targets:
                        return fail_msg(
                            msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
                    else:
                        targetID = hist['oppID']
                    break
            else:
                return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
            p.rank_revenged_targets.add(ID)
        else:
            if req.id not in p.rank_targets:
                return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
            if req.id in p.rank_defeated_targets:
                return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
            targetID = req.id
        detail = get_opponent_detail(targetID, type=LineupType.DEF)
        if req.revenge:
            detail['isRevenge'] = True
        rsp = poem_pb.TargetDetailResponse(**detail)
        rsp.verify_code = PlayerFightLock.lock(p.entityID, force=True)
        p.rank_detail_cache = detail
        p.rank_rest_count -= 1
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.PVP_FINAL_FIGHT)
    @level_required(tag="pvp")
    def pvp_end_fight(self, msgtype, body):
        if g_rankManager.is_close():
            return success_msg(msgtype, poem_pb.PvpEndFightResponse(
                getBP=0, errorcode=msgTips.FAIL_MSG_PVP_CLOSED))
        p = self.player
        logger.info('end_fight %d' % p.entityID)
        req = poem_pb.PvpEndFightRequest()
        req.ParseFromString(body)
        send_fight_verify(p, req.fight)
        if not verify(p, req.fight):
            return fail_msg(msgtype, msgTips.FAIL_MSG_FIGHT_VERIFY_FAILED)
        if not PlayerFightLock.unlock(p.entityID, req.verify_code):
            cached = get_cached_fight_response(p, req.verify_code)
            if cached is not None:
                rsp = poem_pb.PvpEndFightResponse()
                rsp.ParseFromString(cached)
                return success_msg(msgtype, rsp)
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if not p.rank_detail_cache:
            return success_msg(msgtype, poem_pb.PvpEndFightResponse(
                getBP=0, errorcode=msgTips.FAIL_MSG_PVP_CLOSED))
        now = int(time.time())
        oppID = p.rank_detail_cache['entityID']
        if is_zombie(oppID):
            cfgs = get_config(PvpGroupConfig)
            cfg = cfgs.get(oppID)
            if not cfg:
                ototalbp = 1000
            else:
                ototalbp = cfg.score
        else:
            ototalbp = PlayerRankRanking.get_score(oppID)
        mtotalbp = PlayerRankRanking.get_score(p.entityID)
        '''
        积分计算公式：
        胜利加成=10+（防御者积分-攻击者积分）/10
        失败递减=10-（防御者积分-攻击者积分）/10
        上面分数计算后，最大值限定为25，最小值限定为5；
        '''
        k = (ototalbp - mtotalbp) / 10
        win = req.fight.fightResult
        if win:
            bp = min(max(10 + k, 5), 25)
        else:
            bp = max(min(-(10 - k), -5), -25)
        logger.info('sync_rank %d' % p.entityID)
        isRevenge = p.rank_detail_cache.get('isRevenge', False)
        sync_rank(p.entityID, {
            'oppID': p.rank_detail_cache['entityID'],
            'name': p.rank_detail_cache['name'],
            'prototypeID': p.rank_detail_cache.get('prototypeID')
            or p.rank_detail_cache.get('prototypeID'),
            'level': p.rank_detail_cache['level'],
            'score': bp, 'isActive': True, 'isWin': win, 'time': now,
            'isRevenge': isRevenge,
        }, fight=body)
        if not is_zombie(oppID):
            proxy.sync_rank(oppID, {
                'oppID': p.entityID,
                'name': p.name,
                'level': p.level,
                'prototypeID': p.prototypeID,
                'score': -bp,
                'isActive': False, 'isWin': (not win), 'time': now,
            }, fight=body)
        awards = get_config(PvpGradConfig)
        gp = 0
        buffInfos = get_config(PvpSerialWinBuffConfig)
        pvprankcount = get_pvprankcount()
        for award in awards[::-1]:
            if p.totalbp < award.score:
                continue
            if p.rank_active_count < award.count:
                continue
            need_rank = get_need_rank_by_ranking(
                pvprankcount, award.ranking)
            logger.debug("rank:%d, need_rank:%d", p.pvprank, need_rank)
            if need_rank and p.pvprank > need_rank:
                continue
            if win:
                gp = award.win_gain
            else:
                gp = award.lose_gain
            scount = p.rank_serial_win_count
            if p.rank_serial_win_count > max(buffInfos):
                scount = max(buffInfos)
            buffInfo = buffInfos.get(scount)
            # 复仇不加功勋
            if buffInfo and not isRevenge:
                buffs = zip(buffInfo.buffs, buffInfo.params)
                for btype, bvalue in buffs:
                    if btype == BuffType.GP:
                        gp += bvalue
            apply_reward(p, {'gp': gp}, {}, RewardType.PvpGain)
            break
        # 全部打完自动刷新
        if len(p.rank_targets) == len(p.rank_defeated_targets):
            p.rank_targets = []
            p.rank_defeated_targets.clear()
        p.pvpgrad = get_grad(p.pvprank, p.totalbp, p.rank_active_count)
        p.save()
        p.sync()
        rsp = poem_pb.PvpEndFightResponse(getBP=bp, gp=gp, errorcode=0)
        cache_fight_response(p, req.verify_code, rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.NPC_TARGETS)
    def npc_targets(self, msgtype, body):
        p = self.player
        configs = get_config(NpcConfig)
        now = int(time.time())
        rsp = poem_pb.NpcTargets()
        for k, v in configs.items():
            info = v._asdict()
            cd = p.npc_targets_cd.get(str(k), 0)
            if cd:
                cd = cd - now
            info['cd'] = cd
            zid = npc2zombie(v.group, p.level)
            zombie = get_zombie(zid)
            info.update(**zombie['pets'][0])
            info.update(**zombie)
            rsp.targets.add(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.NPC_TARGET_DETAIL)
    def npc_target_detail(self, msgtype, body):
        p = self.player
        req = poem_pb.NpcTargetDetailRequest()
        req.ParseFromString(body)
        config = get_config(NpcConfig)[req.index]
        zid = npc2zombie(config.group, p.level)
        try:
            detail = get_zombie(zid)
        except KeyError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        rsp = poem_pb.TargetDetailResponse(**detail)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.NPC_START_FIGHT)
    def npc_start_fight(self, msgtype, body):
        p = self.player
        req = poem_pb.PvpStartFightRequest()
        req.ParseFromString(body)
        config = get_config(NpcConfig)[req.id]
        zid = npc2zombie(config.group, p.level)
        cd = p.npc_targets_cd.get(str(req.id), 0)
        now = int(time.time())
        if cd and now < cd:
            return fail_msg(msgtype, reason='挑战冷却中')
        if not p.rank_rest_count:
            return fail_msg(msgtype, reason='挑战次数不足')
        config = get_config(NpcConfig).get(req.id)
        if not config:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if p.level < config.openlevel:
            return fail_msg(msgtype, reason="等级不足")
        detail = get_zombie(zid)
        rsp = poem_pb.TargetDetailResponse(**detail)
        rsp.verify_code = PlayerFightLock.lock(p.entityID, force=True)
        p.npc_target_cache = req.id
        p.rank_rest_count -= 1
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.NPC_END_FIGHT)
    def npc_end_fight(self, msgtype, body):
        p = self.player
        req = poem_pb.PvpEndFightRequest()
        req.ParseFromString(body)
        send_fight_verify(p, req.fight)
        if not verify(p, req.fight):
            return fail_msg(msgtype, msgTips.FAIL_MSG_FIGHT_VERIFY_FAILED)
        if not PlayerFightLock.unlock(p.entityID, req.verify_code):
            cached = get_cached_fight_response(p, req.verify_code)
            if cached is not None:
                rsp = poem_pb.PvpEndFightResponse()
                rsp.ParseFromString(cached)
                return success_msg(msgtype, rsp)
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if not p.npc_target_cache:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        config = get_config(NpcConfig).get(p.npc_target_cache)
        if not config:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        result = apply_reward(
            p, parse_reward(config.rewards), {}, RewardType.NpcFight)
        rsp = poem_pb.PvpEndFightResponse()
        rsp.cd = config.cd
        build_reward_msg(rsp, result)
        now = int(time.time())
        p.npc_targets_cd[str(p.npc_target_cache)] = now + config.cd
        p.save()
        p.sync()
        cache_fight_response(p, req.verify_code, rsp)
        return success_msg(msgtype, rsp)
    # }}}

    # {{{ 掠夺
    @rpcmethod(msgid.MINE_COLLECT)
    def mine_collect(self, msgtype, body):
        '''采集'''
        from rob import rob_reward_in_campaign
        req = poem_pb.MineCollectRequest()
        req.ParseFromString(body)
        player = self.player
        type = req.type
        count = getattr(player, "mine_free_collect_count%d" % type, 0)
        sp = (1 if count <= 0 else 0)
        if player.sp < sp:  # 消耗
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_ROB_NOT_ENOUGH_TO_COLLECT)
        # 全部采集
        _, gain, _ = cost_player_products(player, -1, type)
        gain = rob_reward_in_campaign(gain)
        if type == poem_pb.MineType1:
            apply_reward(
                player, {
                    "money": gain}, {
                    "sp": sp}, RewardType.MineCollect)
            from task.manager import on_collect
            on_collect(player, gain, type)
        elif type == poem_pb.MineType2:
            apply_reward(
                player, {
                    "soul": gain}, {
                    "sp": sp}, RewardType.MineCollect)
            from task.manager import on_collect
            on_collect(player, gain, type)
        else:
            raise NotImplementedError("Unknow mine type {}".format(type))
        if count:
            setattr(player, "mine_free_collect_count%d" % type, count - 1)
        player.save()
        player.sync()
        return success_msg(msgtype, poem_pb.MineCollectResponse(booty=gain))

    @rpcmethod(msgid.MINE_ROB_LIST)
    def rob_list(self, msgtype, body):
        '''掠夺列表'''
        req = poem_pb.MineRobListRequest()
        req.ParseFromString(body)
        player = self.player
        targets = player.mine_targets_detail_cache
        if req.refresh:
            try:
                apply_reward(
                    player, None, {
                        'sp': 0}, RewardType.RefreshRobList)
            except AttrNotEnoughError:
                return fail_msg(
                    msgtype,
                    msgTips.FAIL_MSG_ROB_NOT_ENOUGH_TO_REFRESH_ROB_LIST)
        if not targets or req.refresh:
            targets = search_targets(player)
        rsp = poem_pb.MineRobListResponse()
        for i, target in enumerate(targets):
            rsp.targets.add(ID=i, **target)
        player.save()
        player.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.MINE_ROB_GET_CURR_PRODUCTS)
    def rob_get_curr_products(self, msgtype, body):
        '''复仇前必须先发送这条消息'''
        req = poem_pb.PvpStartFightRequest()
        req.ParseFromString(body)
        try:
            if req.revenge:
                t = self.player.mine_rob_history[-req.id]
            else:
                t = self.player.mine_targets_detail_cache[req.id]
        except IndexError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_ROB_INVALID_TARGET)
        from pvp.manager import is_zombie
        if is_zombie(t["entityID"]):
            curr = t["booty"]
        else:
            now = int(time.time())
            curr = max(
                get_curr_products(
                    t['entityID'],
                    now,
                    t['type']
                ), 0
            )
            self.player.mine_revenge_booty_cache = curr
        self.player.save()
        return success_msg(msgtype, poem_pb.RobGetCurrProducts(curr=curr))

    @rpcmethod(msgid.MINE_ROB_START_FIGHT)
    @level_required(tag="get_money1")
    def rob_start_fight(self, msgtype, body):
        '''掠夺'''
        req = poem_pb.PvpStartFightRequest()
        req.ParseFromString(body)
        player = self.player
        if req.revenge:
            history = player.mine_rob_history[-req.id]
            if history['fought']:
                return fail_msg(msgtype, msgTips.FAIL_MSG_ROB_ALREADY_FOUGHT)
            if history['revenge']:
                return fail_msg(msgtype, msgTips.FAIL_MSG_ROB_INVALID_TARGET)
            if player.mine_revenge_booty_cache == -1:
                return fail_msg(msgtype, msgTips.FAIL_MSG_ROB_INVALID_TARGET)
            targetID, type = history['entityID'], history['type']
            booty = None
            rob_count = 0
            # history["fought"] = True
            # player.mine_rob_history[-req.id] = history
            player.save()
            player.sync()
        else:
            if player.mine_rob_count <= 0:
                return fail_msg(
                    msgtype, msgTips.FAIL_MSG_ROB_NOT_ENOUGH_ROB_COUNT)
            target = player.mine_targets_detail_cache[req.id]
            if target['fought']:
                return fail_msg(msgtype, msgTips.FAIL_MSG_ROB_ALREADY_FOUGHT)
            targetID, booty, type = target[
                'entityID'], target['booty'], target['type']
            rob_count = 1
            target["fought"] = True
            player.mine_targets_detail_cache[req.id] = target
            player.mine_curr_target_cache = req.id
            # player.touch_mine_targets_detail_cache()
            player.save()
            player.sync()
        data, err = rob_target(player, targetID, booty, type)
        if err:
            return fail_msg(msgtype, err)
        unlocking_key, booty, detail = data
        rsp = poem_pb.TargetDetailResponse(**detail)
        rsp.verify_code = unlocking_key
        player.mine_rob_count -= rob_count
        player.mine_protect_time = 0
        if not req.revenge:
            from task.manager import on_rob_count
            on_rob_count(player)
        player.save()
        player.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.MINE_ROB_END_FIGHT)
    @level_required(tag="get_money1")
    def rob_end_fight(self, msgtype, body):
        from pvp.manager import is_zombie
        req = poem_pb.PvpEndFightRequest()
        req.ParseFromString(body)
        p = self.player
        send_fight_verify(p, req.fight)
        if not verify(p, req.fight):
            return fail_msg(msgtype, msgTips.FAIL_MSG_FIGHT_VERIFY_FAILED)
        if req.revenge:
            d = p.mine_rob_history[-req.targetID]
            if d['revenge']:
                rsp = poem_pb.PvpEndFightResponse(
                    errorcode=msgTips.FAIL_MSG_ROB_INVALID_TARGET)
                return success_msg(msgtype, rsp)
            targetID, type = d['entityID'], d['type']
            if p.mine_revenge_booty_cache == -1:
                rsp = poem_pb.PvpEndFightResponse(
                    errorcode=msgTips.FAIL_MSG_ROB_INVALID_TARGET)
                return success_msg(msgtype, rsp)
            booty = p.mine_revenge_booty_cache
            d["fought"] = True
            p.mine_rob_history[-req.targetID] = d
            p.save()
            p.sync()
        else:
            d = p.mine_targets_detail_cache[p.mine_curr_target_cache]
            if not d:
                rsp = poem_pb.PvpEndFightResponse(
                    errorcode=msgTips.FAIL_MSG_ROB_INVALID_TARGET)
                return success_msg(msgtype, rsp)
            targetID, type, booty = d['entityID'], d['type'], d['booty']
        if not is_zombie(targetID):
            yes = PlayerMineLock.can_unlock(targetID, req.verify_code)
            logger.debug("locking %r" % yes)
            if not yes:  # 超时或恶意请求， 有缓存，取缓存，没缓存当超时处理
                cached = get_cached_fight_response(p, req.verify_code)
                if cached is not None:
                    rsp = poem_pb.PvpEndFightResponse()
                    rsp.ParseFromString(cached)
                    return success_msg(msgtype, rsp)
                else:
                    rsp = poem_pb.PvpEndFightResponse(
                        errorcode=msgTips.FAIL_MSG_ROB_TIMEOUT)
                    g_playerManager.sendto(  # 让客户端清除本地战斗缓存
                        p.entityID, fail_msg(
                            msgtype, msgTips.FAIL_MSG_INVALID_REQUEST))
                cache_fight_response(p, req.verify_code, rsp)
                return success_msg(msgtype, rsp)
        now = int(time.time())
        if not req.fight.fightResult:
            protect_time = 1
        else:
            if req.fight.player_death_count > 0:
                protect_time = 6
            else:
                protect_time = 12
        if req.fight.fightResult:
            player_members_count = len(req.fight.replay.player_fighters)
            rate = (float(req.fight.enemy_death_count) /
                    float(req.fight.enemy_members_count)) * ((
                        float(player_members_count) -
                        float(req.fight.player_death_count) * 0.5) /
                        float(player_members_count))
        else:
            rate = 0
        assert (rate <= 1 and rate >= 0)
        real_booty = int(rate * booty)
        logger.debug("enemy_death_count: {}".format(
            req.fight.enemy_death_count))
        logger.debug("enemy_members_count: {}".format(
            req.fight.enemy_members_count))
        logger.debug("player_members_count - player_death_count: {}".format(
            req.fight.player_members_count - req.fight.player_death_count
        ))
        logger.debug("player_members_count: {}".format(
            req.fight.player_members_count))
        logger.debug("fight win {}".format(req.fight.fightResult))
        logger.debug("{} * {} = {}".format(booty, rate, real_booty))
        if not is_zombie(targetID):
            if req.fight.fightResult:
                proxy.sync_products(targetID, {
                    'prototypeID': p.prototypeID,
                    'entityID': p.entityID,
                    'level': p.level,
                    'name': p.name,
                    'time': now,
                    'booty': real_booty,
                    'type': type,
                    'revenge': bool(req.revenge),
                    'fought': False,
                    'protect_time': protect_time,
                    'fight': req,
                })
        if type == poem_pb.MineType1:
            gain = {'money': real_booty}
        elif type == poem_pb.MineType2:
            gain = {'soul': real_booty}
        else:
            raise NotImplementedError
        if real_booty:
            apply_reward(p, gain, type=RewardType.Rob)
            from task.manager import on_rob
            on_rob(p, real_booty, type)
        # d['fought'] = True
        if req.revenge:
            # p.mine_rob_history[-req.targetID] = d
            p.mine_revenge_booty_cache = -1
        # else:
        #     p.mine_targets_detail_cache[req.targetID] = d
        #     p.touch_mine_targets_detail_cache()
        if real_booty:
            today = datedate.today()
            if type == poem_pb.MineType1:
                p.mine_rob_by_date1[str(today)] = \
                    p.mine_rob_by_date1.get(str(today), 0) + real_booty
                score = 0
                for i in range(3):
                    dt = today - timedelta(days=i + 1)
                    score += p.mine_rob_by_date1.get(str(dt), 0)
                if score:
                    PlayerRobmine1Ranking.update_score(p.entityID, score)
            elif type == poem_pb.MineType2:
                p.mine_rob_by_date2[str(today)] = \
                    p.mine_rob_by_date2.get(str(today), 0) + real_booty
                score = 0
                for i in range(3):
                    dt = today - timedelta(days=i + 1)
                    score += p.mine_rob_by_date2.get(str(dt), 0)
                if score:
                    PlayerRobmine2Ranking.update_score(p.entityID, score)

        p.save()
        p.sync()
        rsp = poem_pb.PvpEndFightResponse(booty=real_booty)
        if not is_zombie(targetID):
            PlayerMineLock.unlock(targetID, req.verify_code)
        cache_fight_response(p, req.verify_code, rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.MINE_ROBBED_HISTORY)
    def robbed_history(self, msgtype, body):
        '''战报'''
        player = self.player
        rsp = poem_pb.RobHistoryList()
        history = player.mine_rob_history[::-1]
        for i, r in enumerate(history, 1):
            rsp.items.add(ID=i, **r)
        if player.mine_rob_history_flag:
            player.mine_rob_history_flag = False
            player.save()
            player.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.MINE_ROBBED_REPLAY)
    def robbed_replay(self, msgtype, body):
        '''重播'''
        req = poem_pb.RobReplayRequest()
        req.ParseFromString(body)
        player = self.player
        h = player.mine_rob_history[-req.ID]
        raw = h['fight']
        if not raw:
            return fail_msg(msgtype, msgTips.FAIL_MSG_PVP_FIGHT_HISTORY_MISSED)
        rsp = poem_pb.PvpEndFightResponse()
        rsp.ParseFromString(raw)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.MINE_ROB_DETAIL)
    def rob_detail(self, msgtype, body):
        req = poem_pb.PvpStartFightRequest()
        req.ParseFromString(body)
        p = self.player
        if req.revenge:
            d = p.mine_rob_history[-req.id]
            if d['fought']:
                return fail_msg(msgtype, msgTips.FAIL_MSG_ROB_ALREADY_FOUGHT)
            if d['revenge']:
                return fail_msg(msgtype, msgTips.FAIL_MSG_ROB_INVALID_TARGET)
        else:
            d = p.mine_targets_detail_cache[req.id]
            if not d:
                return fail_msg(msgtype, msgTips.FAIL_MSG_ROB_INVALID_TARGET)
            if d['fought']:
                return fail_msg(msgtype, msgTips.FAIL_MSG_ROB_ALREADY_FOUGHT)
        detail = get_opponent_detail(
            d["entityID"], type=get_lineuptype_by_type(d["type"]))
        rsp = poem_pb.TargetDetailResponse(**detail)
        return success_msg(msgtype, rsp)
    # }}}

    # {{{ 大闹天宫
    @rpcmethod(msgid.UPROAR_REFRESH_TARGETS)
    def uproar_refresh_targets(self, msgtype, body):
        from uproar import uproar_reset
        p = self.player
        if not p.uproar_refresh_rest_count:
            return fail_msg(msgtype, reason='重置次数不足')
        p.uproar_refresh_used_count += 1
        uproar_reset(p)
        from task.manager import on_uproar_reset
        on_uproar_reset(p)
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.UPROAR_OPEN_CHEST)
    def uproar_open_chest(self, msgtype, body):
        req = poem_pb.UproarOpenChestRequest()
        req.ParseFromString(body)
        p = self.player
        if req.index in p.uproar_chests_done:
            return fail_msg(msgtype, reason="已经领取过了")
        if req.index not in p.uproar_targets_done:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        from uproar import open_chest
        reward = open_chest(p, req.index)
        rsp = poem_pb.UproarOpenChestResponse()
        build_reward_msg(rsp, reward)
        p.uproar_chests_done.add(req.index)
        from task.manager import on_jiutian
        on_jiutian(p, reward.get("jiutian", 0))
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.UPROAR_START_FIGHT)
    @level_required(tag="ticket")
    def uproar_start_fight(self, msgtype, body):
        req = poem_pb.PvpStartFightRequest()
        req.ParseFromString(body)
        p = self.player
        if req.id in p.uproar_targets_done:
            return fail_msg(msgtype, reason="打过了")
        from uproar import validate_prev
        if not validate_prev(p, req.id):
            return fail_msg(msgtype, reason="未通关前置关卡")
        if req.id > 10:
            return fail_msg(msgtype,
                            reason="由于系统存在严重bug，训练家之丘无尽模式暂时关闭，敬请期待")
        # 校验阵型
        for i in req.lineup.line:
            if i:
                pet = p.pets[i]
                if pet.uproar_dead:
                    return fail_msg(msgtype, reason="已阵亡的精灵不可参战")
        t = p.uproar_targets[req.id]
        if p.uproar_targets_team.get(t):  # 使用替换缓存
            rsp = poem_pb.TargetDetailResponse()
            rsp.ParseFromString(p.uproar_targets_team[t])
        else:
            if t in p.uproar_details_cache:
                detail = p.uproar_details_cache[t]
            else:
                detail = get_opponent_detail(t)
            rsp = poem_pb.TargetDetailResponse(**detail)
        p.uproar_target_cache = t
        p.save()
        rsp.verify_code = PlayerFightLock.lock(p.entityID, force=True)
        logger.debug(rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.UPROAR_END_FIGHT)
    @level_required(tag="ticket")
    def uproar_end_fight(self, msgtype, body):
        from uproar import uproar_forward
        req = poem_pb.PvpEndFightRequest()
        req.ParseFromString(body)
        p = self.player
        send_fight_verify(p, req.fight)
        if not verify(p, req.fight):
            return fail_msg(msgtype, msgTips.FAIL_MSG_FIGHT_VERIFY_FAILED)
        if not PlayerFightLock.unlock(p.entityID, req.verify_code):
            cached = get_cached_fight_response(p, req.verify_code)
            if cached is not None:
                rsp = poem_pb.PvpEndFightResponse()
                rsp.ParseFromString(cached)
                return success_msg(msgtype, rsp)
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        try:
            index = max(set(p.uproar_targets_done).union({0})) + 1
            if p.uproar_targets[index] != p.uproar_target_cache:
                return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        except IndexError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if not p.uproar_target_cache:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if req.fight.fightResult:
            p.uproar_targets_done.add(index)
            uproar_forward(p)
            p.uproar_targets_team.clear()
            from task.manager import on_uproar_count, on_uproar_serial_count
            on_uproar_count(p)
            on_uproar_serial_count(p)
        else:
            detail = get_opponent_detail(p.uproar_target_cache)
            d = poem_pb.TargetDetailResponse(**detail)
            d.pets = req.fight.enemy_team
            logger.debug(d)
            p.uproar_targets_team[p.uproar_target_cache] = \
                str(d.SerializeToString())
        for each in req.fight.player_team:
            pet = p.pets[each.entityID]
            if each.restHP == 0:
                pet.uproar_dead = True
            else:
                pet.restHP = each.restHP
            pet.save()
            pet.sync()
        rsp = poem_pb.PvpEndFightResponse()
        try:
            del p.uproar_details_cache[p.uproar_target_cache]
        except KeyError:
            pass
        p.save()
        p.sync()
        cache_fight_response(p, req.verify_code, rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.UPROAR_TARGET_DETAIL)
    def uproar_target_detail(self, msgtype, body):
        req = poem_pb.UproarTargetDetailRequest()
        req.ParseFromString(body)
        p = self.player
        t = p.uproar_targets[req.index]
        if p.uproar_targets_team.get(t):  # 使用替换缓存
            rsp = poem_pb.TargetDetailResponse()
            rsp.ParseFromString(p.uproar_targets_team[t])
        else:
            if t in p.uproar_details_cache:
                detail = p.uproar_details_cache[t]
            else:
                detail = get_opponent_detail(t)
            if req.index in p.uproar_targets_done:
                for pet in detail["pets"]:
                    pet["restHP"] = 0
            rsp = poem_pb.TargetDetailResponse(**detail)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.UPROAR_TARGETS_THUMB)
    def uproar_targets_thumb(self, msgtype, body):
        from uproar import uproar_reset, uproar_forward
        from pvp.manager import is_zombie
        from entity.manager import g_entityManager
        from uproar import uproar_reward_in_campaign
        p = self.player

        # 旧的相对数据迁移到新的绝对数据结构
        if p.uproar_targets_cache:
            p.uproar_targets.clear()
            for i, v in enumerate(p.uproar_targets_cache[1:], start=1):
                p.uproar_targets[i] = v
            p.uproar_targets_cache = []
            p.save()
        if p.uproar_chests_cache:
            p.uproar_chests.clear()
            for i, v in enumerate(p.uproar_chests_cache[1:], start=1):
                p.uproar_chests[i] = v
            p.uproar_chests_cache = []
            p.save()

        if not p.uproar_targets or not p.uproar_chests:
            uproar_reset(p)
            p.uproar_refresh_used_count += 1
            p.save()
            p.sync()

        if max(p.uproar_chests_done | set([0])) == 10:
            uproar_forward(p)

        # if not all(p.uproar_targets_cache[1:]):
        #     return fail_msg(
        #         msgtype, msgTips.FAIL_MSG_PVP_UPROAR_NOT_ENOUGH_POWER)
        rsp = poem_pb.UproarTargetsThumb()
        for floor, z in sorted(p.uproar_targets.items())[-15:]:
            name = ''
            pet = dict()
            if z is None:
                continue
            else:
                if is_zombie(z):
                    prototypeID = get_zombie(z)['prototypeID']
                else:
                    ps = g_entityManager.get_players_info([z], [
                        "entityID",
                        "prototypeID",
                        "name"
                    ])
                    if ps:
                        prototypeID = ps[0]["prototypeID"]
                        name = ps[0]["name"]
                        if z in p.uproar_details_cache:
                            detail = p.uproar_details_cache[z]
                        else:
                            detail = get_opponent_detail(z)
                        pet = detail['pets'][0]
                    else:
                        prototypeID = 6000002
            chest = p.uproar_chests[floor]
            must = chest.get("must", {})
            must = uproar_reward_in_campaign(must)
            item = rsp.items.add(floor=floor, prototypeID=prototypeID,
                                 name=name, pet=pet)
            item.chest.rewards = build_reward(must)
        logger.debug(rsp)
        return success_msg(msgtype, rsp)
    # }}}

    #  # {{{ 夺宝
    #  @rpcmethod(msgid.LOOT_TARGETS_LIST)
    #  def loot_targets_list(self, msgtype, body):
    #      from pvp.loot import loot_refresh_targets
    #      req = poem_pb.LootListRequest()
    #      req.ParseFromString(body)
    #      p = self.player
    #      if not p.loot_targets_cache or \
    #              all([i.get("type", 0) == 0 for i in p.loot_targets_cache if i]) or \
    #              req.refresh:
    #          if req.refresh:
    #              try:
    #                  apply_reward(
    #                      p, {}, cost={"soul": 100},
    #                      type=RewardType.LootRefresh)
    #              except AttrNotEnoughError:
    #                  return fail_msg(msgtype, reason="水晶不足")
    #          loot_refresh_targets(p)
    #      # type为零是空位
    #      targets = [i if i else {"type": 0} for i in p.loot_targets_cache]
    #      rsp = poem_pb.LootListResponse(targets=targets)
    #      p.save()
    #      p.sync()
    #      return success_msg(msgtype, rsp)

    #  @rpcmethod(msgid.LOOT_START_FIGHT)
    #  @level_required(tag="rob")
    #  def loot_start_fight(self, msgtype, body):
    #      from pvp.manager import is_zombie
    #      from pvp.loot import loot_target
    #      from config.configs import get_config, MatConfig
    #      req = poem_pb.PvpStartFightRequest()
    #      req.ParseFromString(body)
    #      p = self.player
    #      t = p.loot_targets_cache[req.id]
    #      if not t:
    #          return fail_msg(msgtype, reason="已经掠夺过了")
    #      if not p.loot_rest_count:
    #          return fail_msg(msgtype, reason="次数不足")
    #      configs = get_config(MatConfig)
    #      if req.cub not in p.mats:
    #          return fail_msg(msgtype, reason="没有图纸")
    #      t["loot"] = configs[req.cub].arg
    #      if not t.get("entityID"):
    #          detail = loot_target(p, t["power"], t["loot"], t["count"])
    #          t["entityID"] = detail["entityID"]
    #      else:
    #          detail = get_opponent_detail(t["entityID"])
    #      if not is_zombie(t["entityID"]):
    #          unlocking_key = PlayerLootLock.lock(t["entityID"], force=True)
    #      else:
    #          unlocking_key = PlayerFightLock.lock(p.entityID, force=True)
    #      rsp = poem_pb.TargetDetailResponse(**detail)
    #      rsp.verify_code = unlocking_key
    #      p.loot_targets_cache[req.id] = t
    #      p.touch_loot_targets_cache()
    #      p.loot_current_target = req.id
    #      p.save()
    #      return success_msg(msgtype, rsp)

    #  @rpcmethod(msgid.LOOT_END_FIGHT)
    #  @level_required(tag="rob")
    #  def loot_end_fight(self, msgtype, body):
    #      from pvp.manager import is_zombie
    #      from loot import loot_reward_in_campaign
    #      req = poem_pb.PvpEndFightRequest()
    #      req.ParseFromString(body)
    #      p = self.player
    #      send_fight_verify(p, req.fight)
    #      if not verify(p, req.fight):
    #          return fail_msg(msgtype, msgTips.FAIL_MSG_FIGHT_VERIFY_FAILED)
    #      t = p.loot_targets_cache[p.loot_current_target]
    #      if not is_zombie(t["entityID"]):
    #          tid = t["entityID"]
    #          lock = PlayerLootLock
    #      else:
    #          tid = p.entityID
    #          lock = PlayerFightLock
    #      if not lock.unlock(tid, req.verify_code):
    #          cached = get_cached_fight_response(p, req.verify_code)
    #          if cached is not None:
    #              rsp = poem_pb.PvpEndFightResponse()
    #              rsp.ParseFromString(cached)
    #              return success_msg(msgtype, rsp)
    #          return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
    #      rsp = poem_pb.PvpEndFightResponse()
    #      if req.fight.fightResult:
    #          rsp.loot_count = loot_reward_in_campaign(t["count"])
    #          apply_reward(
    #              p, {
    #                  "matList": [
    #                      [t["loot"], loot_reward_in_campaign(t["count"])]]},
    #              type=RewardType.Loot)
    #          p.loot_used_count += 1
    #          from task.manager import on_loot_count
    #          on_loot_count(p)
    #          dd = p.loot_targets_cache[p.loot_current_target]
    #          dd["type"] = 0
    #          p.loot_targets_cache[p.loot_current_target] = dd
    #          # p.touch_loot_targets_cache()
    #      if not is_zombie(t["entityID"]):
    #          proxy.sync_loot_cost(t["entityID"], {
    #              "entityID": p.entityID,
    #              "name": p.name,
    #              "level": p.level, "prototypeID": p.prototypeID,
    #              "loot": t["loot"] if req.fight.fightResult else 0,
    #              "count": t["count"] if req.fight.fightResult else 0,
    #              "result": (not req.fight.fightResult),
    #          })
    #      p.save()
    #      p.sync()
    #      cache_fight_response(p, req.verify_code, rsp)
    #      return success_msg(msgtype, rsp)

    #  @rpcmethod(msgid.LOOT_COMPOSE)
    #  def loot_compose(self, msgtype, body):
    #      from pvp.loot import sync_looted_mats
    #      from config.configs import get_config, MatConfig, EquipConfig
    #      req = poem_pb.LootComposeRequest()
    #      req.ParseFromString(body)
    #      p = self.player
    #      sync_looted_mats(p)
    #      p.save()
    #      p.sync()
    #      configs = get_config(MatConfig)
    #      cub = configs[req.cub]
    #      assert cub.type in (MatType.FaBaoCub, MatType.ZuoQiCub), "Invalid type"
    #      patch = configs[cub.arg]
    #      equip = get_config(EquipConfig)[cub.arg2]
    #      try:
    #          gain = {"equipList": [[equip.prototypeID, 1]]}
    #          apply_reward(
    #              p, gain,
    #              {"matList": [[cub.ID, 1], [patch.ID, equip.need_patch]]},
    #              RewardType.LootCompose)
    #          from equip.constants import EquipType
    #          from task.manager import on_loot_compose_zuoqi
    #          from task.manager import on_loot_compose_fabao
    #          if equip.type == EquipType.ZuoQi:
    #              on_loot_compose_zuoqi(p, equip.quality)
    #          elif equip.type == EquipType.FaBao:
    #              on_loot_compose_fabao(p, equip.quality)
    #          from chat.manager import on_news_equip_quality_compose
    #          on_news_equip_quality_compose(p, build_reward(gain))
    #      except MatNotEnoughError:
    #          return fail_msg(msgtype, reason="材料不足")
    #      p.save()
    #      p.sync()
    #      return success_msg(msgtype, "")

    #  @rpcmethod(msgid.LOOT_RESET_COUNT)
    #  def loot_reset_count(self, msgtype, body):
    #      p = self.player
    #      gold = (p.loot_reset_count + 1) * 100
    #      try:
    #          apply_reward(
    #              p, {}, cost={"gold": gold},
    #              type=RewardType.LootReset)
    #      except AttrNotEnoughError:
    #          return fail_msg(msgtype, reason="钻石不足")
    #      p.loot_used_count = 0
    #      p.loot_reset_count += 1
    #      p.save()
    #      p.sync()
    #      return success_msg(msgtype, "")

    #  @rpcmethod(msgid.LOOT_HISTORY_LIST)
    #  def loot_history_list(self, msgtype, body):
    #      rsp = poem_pb.LootHistoryList()
    #      p = self.player
    #      for h in p.loot_history:
    #          rsp.items.add(**h)
    #      return success_msg(msgtype, rsp)
    #  # }}}

    # {{{
    @rpcmethod(msgid.FAKE_START_FIGHT)
    def fake_start_fight(self, msgtype, body):
        req = poem_pb.PvpStartFightRequest()
        req.ParseFromString(body)
        detail = get_opponent_detail(req.id)
        rsp = poem_pb.TargetDetailResponse(**detail)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FAKE_FIGHT_LIST)
    def fake_fight_list(self, msgtype, body):
        ps = proxy.get_players()
        rsp = poem_pb.ResponsePvpRank()
        for p in ps:
            rsp.opponents.add(**p)
        return success_msg(msgtype, rsp)
    # }}}

    # {{{ swap
    # 截榜发奖励 TODO
    @rpcmethod(msgid.SWAP_INFO)
    def swap_info(self, msgtype, body):
        req = poem_pb.SwapInfoRequest()
        req.ParseFromString(body)
        p = self.player
        p.swaprank = g_swapManager.get_rank(p.entityID)
        if p.swaprank:
            p.sync()
        #  # targets里面的机器人会被刷出排行榜，所以每次打开都刷新
        #  if not p.swap_targets or req.refresh:
        #      g_swapManager.swap_refresh(p)
        g_swapManager.swap_refresh(p)
        rsp = poem_pb.PvpTargets()
        for i in p.swap_targets:
            # TODO 不需要detail所有的数据
            detail = g_swapManager.get_target_detail(i)
            rsp.targets.add(**detail)
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SWAP_TARGET_DETAIL)
    def swap_target_detail(self, msgtype, body):
        req = poem_pb.SwapTargetRequest()
        req.ParseFromString(body)
        p = self.player
        if req.targetID in p.swap_targets:
            detail = g_swapManager.get_target_detail(req.targetID)
            if detail:
                rsp = poem_pb.TargetDetailResponse(**detail)
                return success_msg(msgtype, rsp)
        return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)

    @rpcmethod(msgid.SWAP_START_CHALLENGE)
    def swap_start_challenge(self, msgtype, body):
        p = self.player
        if p.swap_rest_count <= 0:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        req = poem_pb.SwapStartChallengeRequest()
        req.ParseFromString(body)
        # 检查次数
        if p.swap_rest_count <= 0:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if req.targetID not in p.swap_targets:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if not filter(lambda s: s, p.lineups.get(LineupType.DEF, [])):
            return fail_msg(msgtype, reason="请先设置防守阵容")
        # 检查cd
        now = int(time.time())
        if now < p.swap_cd:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        # 检查排名是否改变
        if g_swapManager.get_rank(req.targetID) != req.swaprank:
            g_swapManager.swap_refresh(p)
            rsp = poem_pb.PvpTargets()
            for i in p.swap_targets:
                # TODO 不需要detail所有的数据
                detail = g_swapManager.get_target_detail(i)
                rsp.targets.add(**detail)
                msg = success_msg(msgid.SWAP_INFO, rsp)
            g_playerManager.sendto(p.entityID, msg)
            return fail_msg(msgtype, reason="排名已变化")
        try:
            verify_code = PlayerSwapLock.lock(req.targetID)
        except LockedError:
            return fail_msg(msgtype, reason="对手正在被挑战中")
        if p.swap_lock_cd > now:
            return fail_msg(msgtype, reason="您正在挑战中")
        p.swap_used_count += 1
        if p.swap_rest_count:
            p.swaprank = g_swapManager.get_rank(p.entityID)
            if p.swaprank and p.swaprank <= get_cons_value(
                    "EnableCDAfterRank"):
                p.swap_cd = now + get_cons_value("SwapRankCD")
        p.swap_lock_cd = now + SWAP_LOCK_CD
        p.save()
        p.sync()
        rsp = poem_pb.SwapStartChallengeResponse(
            cd=PlayerSwapLock.timeout,
            verify_code=verify_code,
        )
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SWAP_FINAL_CHALLENGE)
    def swap_challenge(self, msgtype, body):
        req = poem_pb.SwapFinalChallengeRequest()
        req.ParseFromString(body)
        p = self.player
        if not p.swaprank:
            g_swapManager.register(p)
        p.swaprank = g_swapManager.get_rank(p.entityID)
        if not p.swapmaxrank:
            p.swapmaxrank = p.swaprank
        before_rank = p.swaprank
        now = int(time.time())
        if not PlayerSwapLock.unlock(req.targetID, req.verify_code):
            return fail_msg(msgtype, reason="校验失败")
        isWin = req.fight.fightResult
        if isWin:
            send_fight_verify(p, req.fight)
            if not verify(p, req.fight):
                return fail_msg(msgtype, msgTips.FAIL_MSG_FIGHT_VERIFY_FAILED)
            r1, r2 = g_swapManager.swap_ranks(p, req.targetID)
            p.swaprank = g_swapManager.get_rank(p.entityID)
            from task.manager import on_swap_rank
            on_swap_rank(p, p.swaprank)
        else:
            pass
        from task.manager import on_swap_rank_count
        on_swap_rank_count(p)
        after_rank = p.swaprank
        maxrank_reward = {}
        swapmaxrank = 0
        if after_rank < p.swapmaxrank:
            swapmaxrank = p.swapmaxrank
            configs = get_config(SwapmaxrankConfig)
            lo = None
            hi = None
            for k, config in configs.items():
                if not hi and swapmaxrank < config.rank:
                    hi = config.id - 1
                if not lo and after_rank < config.rank:
                    lo = config.id
                if lo and hi:
                    break
            if lo and hi and lo == hi:
                maxrank_reward = {"gold": configs[lo].gold}
            else:
                maxrank_reward = {"gold": sum([
                    configs[i].gold for i in range(lo, hi)]) or 1}
            p.swapmaxrank = after_rank

        if isWin:
            p.swap_win_count += 1
            from task.manager import on_swap_rank_win_count
            on_swap_rank_win_count(p)
        # 刷新列表
        g_swapManager.swap_refresh(p)
        # 存储战斗回放
        detail = g_swapManager.get_target_detail(req.targetID)
        proxy.add_history(p.entityID, {
            "oppID": req.targetID,
            "name": detail["name"],
            "prototypeID": detail.get("prototypeID", 0)
            or detail.get("prototypeID", 0),
            "level": detail["level"],
            "faction_name": detail["faction_name"],
            "isWin": isWin,
            "isActive": True, "time": now,
            "isRevenge": False,
            "before_rank": before_rank,
            "after_rank": after_rank,
        }, fight=body)
        win_rewards, lose_rewards = get_config(SwapFightRewardConfig)
        win_rewards = win_rewards.rewards
        lose_rewards = lose_rewards.rewards
        if isWin:
            apply_reward(
                p, combine_reward(win_rewards, maxrank_reward),
                type=RewardType.SwapFight)
            result = parse_reward(win_rewards)
        else:
            result = apply_reward(
                p, parse_reward(lose_rewards),
                type=RewardType.SwapFight)
        p.swap_lock_cd = 0
        if not p.swap_register_time:
            p.swap_register_time = int(time.time())
        p.save()
        p.sync()
        if req.targetID > 0:
            # 刷新对方排名
            proxy.add_history(req.targetID, {
                "oppID": p.entityID,
                "name": p.name,
                "level": p.level,
                "faction_name": p.faction_name,
                "prototypeID": p.prototypeID,
                "isActive": False, "isWin": (not isWin),
                "time": now, "isRevenge": False,
                "before_rank": after_rank,
                "after_rank": before_rank,
            }, fight=body)
        rsp = poem_pb.SwapFinalChallengeResponse(
            before=before_rank,
            after=after_rank)
        if maxrank_reward:
            rsp.swapmaxrank_info.swapmaxrank = swapmaxrank
            rsp.swapmaxrank_info.rewards = build_reward(maxrank_reward)
        build_reward_msg(rsp, result)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SWAP_REFRESH_CD)
    def swap_refresh_cd(self, msgtype, body):
        p = self.player
        try:
            apply_reward(
                p, {}, cost={"gold": get_cons_value("SwapRankCDCost")},
                type=RewardType.SwapRefreshCD)
        except AttrNotEnoughError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        p.swap_cd = 0
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.SWAP_REFRESH_COUNT)
    def swap_refresh_count(self, msgtype, body):
        p = self.player
        if not p.swap_rest_reset_count:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        try:
            apply_reward(
                p, {}, cost={"gold": p.swap_reset_count_cost},
                type=RewardType.SwapResetCount)
        except AttrNotEnoughError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        p.swap_used_reset_count += 1
        p.swap_used_count = 0
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.SWAP_RANK_LIST)
    def swap_rank_list(self, msgtype, body):
        req = RequestPvpRank()
        req.ParseFromString(body)
        if req.type != RequestPvpRank.Top:
            count = 50
            detail = True
        else:
            count = 1
            detail = False
        yesterday = bool(req.type == RequestPvpRank.Last)
        rankers = g_swapManager.get_rank_list(
            0, count=count, yesterday=yesterday, detail=detail)
        rsp = ResponsePvpRank()
        for i, ranker in enumerate(rankers[:count]):
            rsp.opponents.add(**ranker)
        if len(rankers) > count:
            rsp.hasnext = True
        logger.debug(rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SWAP_HISTORY)
    def swap_history(self, msgtype, body):
        rsp = PvpHistoryList()
        p = self.player
        for each in p.swap_history:
            rsp.items.add(**each)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SWAP_REPLAY)
    def swap_replay(self, msgtype, body):
        req = PvpReplayRequest()
        req.ParseFromString(body)
        raw = self.player.swap_fight_history.get(req.ID)
        if not raw:
            return fail_msg(msgtype, msgTips.FAIL_MSG_PVP_FIGHT_HISTORY_MISSED)
        rsp = poem_pb.SwapFinalChallengeRequest()
        rsp.ParseFromString(raw)
        self.player.save()
        self.player.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SWAP_REWARD)
    def swap_reward(self, msgtype, body):
        from config.configs import SwapRewardConfig
        rsp = poem_pb.ResponsePvpRewards()
        configs = get_config(SwapRewardConfig)
        for config in configs.values():
            start, end = config.range
            rsp.items.add(
                title=config.title,
                rewards=[RewardData(**r) for r in config.rewards],
                start=start,
                final=end,
            )
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DAILY_INFO)
    def daily_info(self, msgtype, body):
        p = self.player
        rsp = poem_pb.DailyInfoResponse()
        rankers = g_dailyManager.get_rankers(count=3)
        if rankers:
            for detail in rankers:
                rsp.targets.add(**detail)
        rsp.registers = PlayerDailyRankRanking.count()
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DAILY_REGISTER)
    def daily_register(self, msgtype, body):
        p = self.player
        g_dailyManager.register(p)
        p.daily_registered = True
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.DAILY_PANEL)
    def daily_panel(self, msgtype, body):
        p = self.player
        if not g_campaignManager.dailypvp_campaign.is_open():
            return fail_msg(msgtype, msgTips.FAIL_MSG_DAILY_CAMPAIGN_CLOSED)
        g_dailyManager.register(p)
        p.daily_registered = True
        rsp = poem_pb.DailyPanelResponse()
        g_dailyManager.get_panel(p, rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DAILY_TARGET_DETAIL)
    def daily_target_detail(self, msgtype, body):
        p = self.player
        now = int(time.time())
        if not p.daily_count or (
                now > p.daily_dead_cd and p.daily_dead_resume < p.daily_dead_cd
                ):
            g_dailyManager.reborn(p)
            p.daily_dead_resume = now
        if not g_campaignManager.dailypvp_campaign.is_open():
            return fail_msg(msgtype, msgTips.FAIL_MSG_DAILY_CAMPAIGN_CLOSED)
        p = self.player
        detail = g_dailyManager.get_target(p)
        if not detail:
            return fail_msg(msgtype, msgTips.FAIL_MSG_DAILY_NOT_TARGET)
        rsp = poem_pb.TargetDetailResponse(**detail)
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DAILY_START_FIGHT)
    def daily_start_fight(self, msgtype, body):
        p = self.player
        now = int(time.time())
        if not filter(lambda s: s, p.lineups.get(LineupType.Daily, None)):
            return fail_msg(msgtype, reason="请先设置阵容")
        if not g_campaignManager.dailypvp_campaign.is_open():
            return fail_msg(msgtype, msgTips.FAIL_MSG_DAILY_CAMPAIGN_CLOSED)
        if now < p.daily_dead_cd:
            return fail_msg(msgtype, reason="你已经死亡")
        rsp = poem_pb.DailyStartFightResponse()
        rsp.verify_code = PlayerDailyLock.lock(p.entityID, force=True)
        rsp.cd = PlayerDailyLock.timeout
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DAILY_FINAL_FIGHT)
    def daily_final_fight(self, msgtype, body):
        if not g_campaignManager.dailypvp_campaign.is_open():
            return fail_msg(msgtype, msgTips.FAIL_MSG_DAILY_CAMPAIGN_CLOSED)
        p = self.player
        req = poem_pb.DailyFinalFightRequest()
        req.ParseFromString(body)
        if not PlayerDailyLock.unlock(p.entityID, req.verify_code):
            return fail_msg(msgtype, reason="战斗超时")
        from fightverifier.direct_verifier import verify
        send_fight_verify(p, req.fight)
        if not verify(p, req.fight):
            return fail_msg(msgtype, msgTips.FAIL_MSG_FIGHT_VERIFY_FAILED)
        rsp = poem_pb.DailyFinalFightResponse()
        g_dailyManager.battle(
            p, p.daily_cache_targetID, req.fight, body, rsp)
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    # @rpcmethod(msgid.DAILY_BUY_COUNT)
    # def daily_buy_count(self, msgtype, body):
    #     if not g_campaignManager.dailypvp_campaign.is_open():
    #         return fail_msg(msgtype, reason="活动未开启")
    #     p = self.player
    #     if p.daily_count and not p.daily_buy_rest_count:
    #         return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
    #     p.daily_count = 10
    #     p.daily_buy_used_count += 1
    #     apply_reward(
    #         p, {"gold": p.daily_buy_count_cost},
    #         type=RewardType.DailyBuyCount)
    #     p.save()
    #     p.sync()
    #     return success_msg(msgtype, "")

    # @rpcmethod(msgid.DAILY_REWARD_LIST)
    # def daily_reward_list(self, msgtype, body):
    #     from config.configs import get_config
    #     from config.configs import DailyRewardConfig
    #     configs = get_config(DailyRewardConfig)
    #     rsp = poem_pb.DailyRewardListResponse()
    #     for k, config in configs.items():
    #         item = rsp.items.add(**config._asdict())
    #         item.rewards = [RewardData(**r) for r in config.rewards]
    #         item.start, item.final = config.range
    #     return success_msg(msgtype, rsp)

    # @rpcmethod(msgid.DAILY_RANK_LIST)
    # def daily_rank_list(self, msgtype, body):
    #     req = poem_pb.DailyRankListRequest()
    #     req.ParseFromString(body)
    #     if req.type == 1:
    #         rankers = g_dailyManager.get_rankers()
    #     else:
    #         rankers = g_dailyManager.get_red_rankers()
    #     rsp = poem_pb.DailyRankListResponse()
    #     for ranker in rankers:
    #         rsp.rankers.add(**ranker)
    #     return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DAILY_HISTORY_LIST)
    def daily_history_list(self, msgtype, body):
        p = self.player
        rsp = poem_pb.DailyHistoryList()
        for each in p.daily_histories:
            rsp.histories.add(**each)
        p.daily_history_flag = False
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DAILY_REPLAY)
    def daily_replay(self, msgtype, body):
        p = self.player
        req = poem_pb.DailyReplayRequest()
        req.ParseFromString(body)
        history = p.daily_histories[req.index]
        fight = history.get("fight", 0)
        if not fight:
            return fail_msg(msgtype, reason="战斗录像已经损坏")
        rsp = poem_pb.DailyFinalFightRequest()
        rsp.ParseFromString(fight.decode("base64"))
        return success_msg(msgtype, rsp)

    # @rpcmethod(msgid.DAILY_RED_LIST)
    # def daily_red_list(self, msgtype, body):
    #     rsp = poem_pb.RedInfoList()
    #     for red in g_dailyManager.get_red_list():
    #         rsp.reds.add(**red)
    #     for ranker in g_dailyManager.get_red_rankers(count=3):
    #         rsp.rankers.add(**ranker)
    #     return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DAILY_RED_INFO)
    def daily_red_info(self, msgtype, body):
        req = poem_pb.RedInfoRequest()
        req.ParseFromString(body)
        info = g_dailyManager.get_red(req.red)
        rsp = poem_pb.RedInfo(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DAILY_RED_RECV)
    def daily_red_recv(self, msgtype, body):
        p = self.player
        req = poem_pb.RedRecvRequest()
        req.ParseFromString(body)
        rs = g_redManager.recv_red(req.red)
        # if rs == -1:
        #     return fail_msg(msgtype, msgTips.FAIL_MSG_DAILY_RED_NOT_ENOUGH)
        # elif rs == 0:
        #     return fail_msg(msgtype, msgTips.FAIL_MSG_DAILY_RED_TIMEOUT)
        if rs <= 0:
            return fail_msg(msgtype, msgTips.FAIL_MSG_DAILY_RED_NOT_ENOUGH)
        reward = open_reward(RewardType.DailyRed, rs)
        result = reward.apply(p)
        rsp = poem_pb.RedRecvResponse()
        build_reward_msg(rsp, result)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DAILY_END_PANEL)
    def daily_end_panel(self, msgtype, body):
        p = self.player
        rsp = poem_pb.DailyEndPanel(**p.daily_end_panel)
        if p.daily_end_panel:
            p.daily_end_panel.clear()
            p.save()
            p.sync()
        return success_msg(msgtype, rsp)
    # }}}

    # {{{ 爬塔
    @rpcmethod(msgid.CLIMB_TOWER_INFO)
    def climb_tower_info(self, msgtype, body):
        from pvp.manager import get_opponent_detail
        from pvp.climb_tower import g_climbTowerManager
        req = poem_pb.ClimbTowerInfoRequest()
        req.ParseFromString(body)
        rsp = poem_pb.ClimbTowerInfoResponse()
        p = self.player
        floor = p.climb_tower_floor
        configs = get_config(ClimbTowerConfig)

        for idx in range(floor + 1, floor + 6):
            if idx not in configs:
                break
            f = poem_pb.ClimbTowerFloor(floor=idx)
            config = configs.get(idx, None)
            f.limit = config.limit
            f.description = config.description
            target = config.zombie_id
            detail = get_opponent_detail(target)
            cfg = get_config(ClimbTowerAccreditConfig).get(idx, None)
            if cfg:
                config = cfg
                target = cfg.zombie_id
                f.tip_type, _, f.tip_cost = cfg.tip
                f.is_accredit = True
                detail = g_climbTowerManager.challenge(p)
                f.accredit_max_count = config.top_limit
                count = g_climbTowerManager.floors[idx].count()
                f.accredit_count = count
            f.target = poem_pb.TargetDetailResponse(**detail)
            rsp.floors.append(f)

        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CLIMB_TOWER_CHESTS)
    def climb_tower_chests(self, msgtype, body):
        p = self.player
        rsp = poem_pb.ClimbTowerChestsResponse()
        for config in get_config(ClimbTowerChestConfig).values():
            chest = poem_pb.ClimbTowerChest(floor=config.floor)
            chest.rewards = [RewardData(**r) for r in config.rewards]
            if config.floor in p.climb_tower_chests:
                chest.state = poem_pb.ClimbTowerChest.Taken
            elif p.climb_tower_floor >= config.floor:
                chest.state = poem_pb.ClimbTowerChest.Available
            rsp.chests.append(chest)

        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CLIMB_TOWER_RESET)
    def climb_tower_reset(self, msgtype, body):
        p = self.player
        if p.climb_tower_max_count - p.climb_tower_used_count <= 0:
            return fail_msg(msgtype, reason='今日重置次数已经用完')

        p.climb_tower_floor = 0
        p.climb_tower_chests = set()
        p.climb_tower_tip_floors = set()
        p.climb_tower_used_count += 1
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.CLIMB_TOWER_TIP)
    def climb_tower_tip(self, msgtype, body):
        from pvp.climb_tower import g_climbTowerManager
        from reward.base import get_reward_attr_name
        p = self.player
        floor = p.climb_tower_floor + 1
        config = get_config(ClimbTowerAccreditConfig).get(floor, None)
        if not config:
            return fail_msg(msgtype, code=msgTips.FAIL_MSG_INVALID_REQUEST)
        if floor in p.climb_tower_tip_floors:
            return fail_msg(msgtype, reason="打赏过了")
        try:
            g_climbTowerManager.tip(p)
        except AttrNotEnoughError:
            attr = get_reward_attr_name(config.tip[0])
            name = Player.fields[attr].description
            return fail_msg(msgtype, reason="%s不足" % name)

        p.climb_tower_tip_floors.add(floor)
        p.climb_tower_floor += 1
        if p.climb_tower_floor > p.climb_tower_max_floor:
            p.climb_tower_max_floor = p.climb_tower_floor
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.CLIMB_TOWER_START_FIGHT)
    @level_required(tag="ticket")
    def climb_tower_start_fight(self, msgtype, body):
        from pvp.climb_tower import g_climbTowerManager
        req = poem_pb.PvpStartFightRequest()
        req.ParseFromString(body)
        p = self.player
        floor = p.climb_tower_floor + 1

        is_accredit = floor in get_config(ClimbTowerAccreditConfig)
        # 对手派驻层变了
        if req.id > 0 and is_accredit and not g_climbTowerManager.floors[floor].idx.exists(req.id):
            return fail_msg(msgtype,
                            code=msgTips.FAIL_MSG_CLIMB_TOWER_TARGET_UNAVAILABLE)

        config = get_config(ClimbTowerConfig)[floor]
        line = filter(lambda x: x is not None, req.lineup.line)
        if len(line) > config.limit:
            return fail_msg(msgtype,
                            reason="上阵精灵超过限制数量")
        # 校验阵型
        lineup = p.lineups.get(LineupType.Accredit, [])
        for i in line:
            pet = p.pets[i]
            if pet.entityID in lineup:
                return fail_msg(msgtype,
                                reason="已派驻的精灵不可参战")
        detail = get_opponent_detail(req.id)
        if req.id > 0:
            detail = get_opponent_detail(req.id, type=LineupType.Accredit)
        p.climb_tower_last_target = req.id
        rsp = poem_pb.TargetDetailResponse(cd=300, **detail)
        p.save()
        rsp.verify_code = PlayerFightLock.lock(p.entityID, force=True)
        if req.id > 0:
            try:
                p.climb_tower_verify_code = PlayerAccreditLock.lock(req.id,
                                                                    force=False)
                p.save()
            except LockedError:
                return fail_msg(msgtype, reason='该玩家正在战斗中，请等待')
        logger.debug(rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CLIMB_TOWER_END_FIGHT)
    @level_required(tag="ticket")
    def climb_tower_end_fight(self, msgtype, body):
        from pvp.climb_tower import g_climbTowerManager
        from pvp.manager import get_opponent_detail
        req = poem_pb.PvpEndFightRequest()
        req.ParseFromString(body)
        rsp = poem_pb.ClimbTowerEndFightResponse()
        p = self.player
        send_fight_verify(p, req.fight)
        if not verify(p, req.fight):
            return fail_msg(msgtype, msgTips.FAIL_MSG_FIGHT_VERIFY_FAILED)

        # 解锁 target
        target = p.climb_tower_last_target
        if target > 0:
            PlayerAccreditLock.unlock(target, p.climb_tower_verify_code)

        if not PlayerFightLock.unlock(p.entityID, req.verify_code):
            cached = get_cached_fight_response(p, req.verify_code)
            if cached is not None:
                rsp = poem_pb.ClimbTowerEndFightResponse()
                rsp.ParseFromString(cached)
                return success_msg(msgtype, rsp)
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)

        # 保存战斗记录
        try:
            floor = p.climb_tower_floor + 1
            if floor in get_config(ClimbTowerAccreditConfig):
                now = int(time.time())
                detail = get_opponent_detail(p.climb_tower_last_target)
                history = {
                    "oppID": p.climb_tower_last_target,
                    "name": detail["name"],
                    "prototypeID": detail.get("prototypeID", 0),
                    "borderID": detail.get("borderID", 0),
                    "level": detail["level"],
                    "faction_name": detail["faction_name"],
                    "isWin": req.fight.fightResult,
                    "isActive": True, "time": now,
                    "isRevenge": False,
                }
                g_climbTowerManager.add_history(p.entityID, history, fight=body)
                if p.climb_tower_last_target > 0:
                    history.update({
                        "oppID": p.entityID,
                        "name": p.name,
                        "prototypeID": p.prototypeID,
                        "borderID": p.borderID,
                        "level": p.level,
                        "faction_name": p.faction_name,
                        "isWin": not history['isWin'],
                    })
                    g_climbTowerManager.add_history(p.climb_tower_last_target,
                                                    history, fight=body)
        except Exception as e:
            logger.exception(e)

        if req.fight.fightResult:
            p.climb_tower_floor += 1
            if p.climb_tower_floor > p.climb_tower_max_floor:
                p.climb_tower_max_floor = p.climb_tower_floor
            config = get_config(ClimbTowerConfig)[p.climb_tower_floor]
            rewards = parse_reward(config.rewards)
            result = apply_reward(p, rewards, {}, RewardType.ClimbTower)
            build_reward_msg(rsp, result)
            c = get_config(ClimbTowerAccreditConfig).get(p.climb_tower_floor, None)
            if c:
                rsp.limit = c.limit
                # 进入保护期
                g_climbTowerManager.pre_accredit(p)
                # 锁定对手，如果派驻达到上限
                # g_climbTowerManager.lock_target(p)

            # 更新排行榜
            score = PlayerClimbTowerRanking.get_score(p.entityID)
            if score < p.climb_tower_floor:
                PlayerClimbTowerRanking.update_score(p.entityID,
                                                     p.climb_tower_floor)
        else:
            p.climb_tower_last_target = 0

        p.save()
        p.sync()
        cache_fight_response(p, req.verify_code, rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CLIMB_TOWER_OPEN_CHEST)
    def climb_tower_open_chest(self, msgtype, body):
        req = poem_pb.ClimbTowerOpenChestRequest()
        req.ParseFromString(body)
        configs = get_config(ClimbTowerChestConfig)
        p = self.player
        if req.floor not in configs:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if req.floor in p.climb_tower_chests:
            return fail_msg(msgtype,
                            code=msgTips.FAIL_MSG_CLIMB_TOWER_CHEST_TAKEN)
        config = configs[req.floor]
        rewards = parse_reward(config.rewards)
        result = apply_reward(p, rewards, {}, RewardType.ClimbTower)
        p.climb_tower_chests.add(config.floor)
        p.save()
        p.sync()
        rsp = poem_pb.UproarOpenChestResponse()
        build_reward_msg(rsp, result)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CLIMB_TOWER_ACCREDIT)
    def climb_tower_accredit(self, msgtype, body):
        """派驻精灵"""
        from lineup.manager import save_lineup
        from lineup.constants import LineupType
        from pvp.climb_tower import g_climbTowerManager
        p = self.player
        if p.climb_tower_floor not in get_config(ClimbTowerAccreditConfig):
            return fail_msg(msgtype, code=msgTips.FAIL_MSG_INVALID_REQUEST)

        req = poem_pb.ClimbTowerAccreditRequest()
        req.ParseFromString(body)
        low_floor = p.climb_tower_floor < p.climb_tower_accredit_floor
        if not req.force and low_floor:
            return fail_msg(msgtype,
                            code=msgTips.FAIL_MSG_CLIMB_TOWER_ACCREDIT_LOW_FLOOR)
        try:
            save_lineup(p, req.lineup.line, LineupType.Accredit)
            g_climbTowerManager.accredit(p, req.lineup.line)
        except AssertionError:
            return fail_msg(msgtype,
                            code=msgTips.FAIL_MSG_CLIMB_TOWER_ACCREDIT_LIMITED_EXCEED)
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.CLIMB_TOWER_ACCREDIT_INFO)
    def climb_tower_accredit_info(self, msgtype, body):
        from pvp.climb_tower import g_climbTowerManager
        p = self.player
        now = int(time.time())
        if p.climb_tower_accredit_floor == 0 or p.climb_tower_accredit_cd < now:
            return fail_msg(msgtype, code=msgTips.FAIL_MSG_INVALID_REQUEST)

        config = get_config(ClimbTowerAccreditConfig)[p.climb_tower_accredit_floor]
        earnings = p.climb_tower_accredit_acc_earnings
        idx = g_climbTowerManager.tip_earnings[config.tip[0]]
        tip = idx.pool.execute('HMGET', idx.key,
                               p.entityID, 't%d' % p.entityID)
        rsp = poem_pb.ClimbTowerAccreditInfoResponse(
            tip_count=int(tip[1] or 0),
            tip_type=config.tip[1],
            tip_earnings=int(tip[0] or 0),
            accredit_type=config.earnings[0],
            accredit_earnings=earnings,
            accredit_earnings_per_minute=config.earnings[2])
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CLIMB_TOWER_HISTORY)
    def climb_tower_history(self, msgtype, body):
        rsp = poem_pb.ClimbTowerHistoryListResponse()
        p = self.player
        for data in p.climb_tower_history:
            item = poem_pb.ClimbTowerHistoryItem(
                id=data['ID'],
                name=data['name'],
                faction=data['faction_name'],
                timestamp=data['time'],
                prototypeID=data['prototypeID'],
                borderID=data['borderID'],
                win=data['isWin'],
            )
            if 'tip_type' in data:
                item.tip_type = data['tip_type']
                item.tip_earnings = data['tip_count']
            rsp.items.append(item)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CLIMB_TOWER_HISTORY_REPLAY)
    def climb_tower_history_replay(self, msgtype, body):
        req = PvpReplayRequest()
        req.ParseFromString(body)
        raw = self.player.climb_tower_fight_history.get(req.ID)
        if not raw:
            return fail_msg(msgtype, msgTips.FAIL_MSG_PVP_FIGHT_HISTORY_MISSED)
        fight = poem_pb.PvpEndFightRequest()
        fight.ParseFromString(raw)
        rsp = poem_pb.ClimbTowerHistoryResponse()
        rsp.fight = fight
        self.player.save()
        self.player.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CLIMB_TOWER_SWIPE)
    def climb_tower_swipe(self, msgtype, body):
        p = self.player
        rsp = poem_pb.ClimbTowerSwipeResponse()
        configs = get_config(ClimbTowerConfig)

        max_floor = int(p.climb_tower_max_floor * 0.7)
        for idx in configs.keys()[p.climb_tower_floor:]:
            # TODO 测试用
            # if idx >= max_floor:
            if idx > p.climb_tower_max_floor:
                rsp.is_accredit = False
                break

            # 派驻层
            if idx in get_config(ClimbTowerAccreditConfig):
                rsp.is_accredit = True
                break

            config = configs[idx]
            f = poem_pb.ClimbTowerSwipeFloor(floor=idx)
            rewards = parse_reward(config.rewards)
            result = apply_reward(p, rewards, {}, RewardType.ClimbTower)
            build_reward_msg(f, result)
            rsp.floors.append(f)
            p.climb_tower_floor += 1

        p.save()
        p.sync()
        return success_msg(msgtype, rsp)
    # }}}
