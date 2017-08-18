# coding:utf-8
import time
import logging
logger = logging.getLogger("explore")
from datetime import date as datedate
from yy.rpc import RpcService, rpcmethod
from yy.message.header import success_msg, fail_msg
from yy.utils import choice_one
# from yy.utils import guess
from yy.utils import weighted_random2

import protocol.poem_pb as msgid
from protocol import poem_pb
from protocol.poem_pb import TreasureGrid

from common import msgTips
from config.configs import get_config
from config.configs import VisitConfig
from config.configs import get_cons_value
from config.configs import TapMonsterConfig
from config.configs import TreasureChestConfig
from config.configs import TriggerEventConfig
from config.configs import TriggerChestConfig
from config.configs import TriggerChestsConfig
from config.configs import TriggerStoreConfig
from config.configs import TaskConfig
from config.configs import DlcConfig
from config.configs import FbInfoBySceneConfig
from config.configs import DlcFbInfoConfig
from config.configs import DlcTaskConfig
from config.configs import SceneInfoConfig
from config.configs import FbInfoConfig
from config.configs import DlcStarPacksByDlcConfig
from config.configs import DlcStarPacksConfig
from config.configs import AmbitionConfig
from config.configs import VipAmbitionConfig
from config.configs import VisitRewardByGroupConfig
from config.configs import RandomAmbitionConfig

from task.manager import get_daily_sp_tasks
from task.manager import on_tap_count
from task.manager import on_treasure_count
from task.manager import done_task
from task.manager import is_done
from task.manager import on_maze_count

from entity.manager import level_required
from player.model import PlayerTreasureLock

from reward.manager import open_reward
from reward.manager import RewardType
from reward.manager import parse_reward
from reward.manager import compare_reward
from reward.manager import build_reward_msg
from reward.manager import apply_reward
from reward.manager import AttrNotEnoughError
from reward.manager import combine_reward
from reward.manager import build_reward

from pvp.manager import update_onlines
from pvp.manager import get_opponent_detail

from faction.model import Faction

from .treasure import enter_treasure
from .treasure import refresh_treasure
# from .constants import TreasureType

from .tap import end_tap
from .tap import save_tap
from .tap import start_tap
from .tap import onekey_tap

from .trigger import check_trigger_event_type

from .constants import EventType
from .constants import DlcFbType
from .constants import MazeEventType

from .dlc import get_helper_cd
from .dlc import apply_dlc_reward
from .dlc import set_dlc_progress
from .dlc import reset_dlc_progress
from .dlc import validate_start
from .dlc import validate_dlc_fb
from .dlc import get_dlc_score
from .dlc import g_dlcCampaignManager
from .dlc import get_campaign_info
from .dlc import search_target

from .maze import step_mazes

from scene.manager import set_fb_score
from scene.manager import validate_prevs
from scene.manager import is_first
from mall.constants import MallType

from .visit import visit
from .visit import incr_visit_flag

# from ranking.manager import get_current_rank
from campaign.manager import g_campaignManager
from lineup.constants import LineupType


class ExploreService(RpcService):

    @rpcmethod(msgid.VISIT_LIST)
    def visit_list(self, msgtype, body):
        configs = get_config(VisitConfig)
        rsp = poem_pb.VisitList()
        for k, v in configs.items():
            info = v._asdict()
            rsp.items.add(**info)
        campaign = g_campaignManager.visit_campaign
        if campaign.is_open():
            rsp.now = int(time.time())
            rsp.start, rsp.final = campaign.get_current_time()
            config = campaign.get_current()
            rsp.bg = config.bg
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.VISIT_VISIT)
    @level_required(tag="visit")
    def visit_visit(self, msgtype, body):
        p = self.player
        req = poem_pb.VisitRequest()
        req.ParseFromString(body)
        cost = {}
        count = 1
        if req.onekey:
            count = 10
        gain, cost, ids, luck = visit(p, count)
        try:
            apply_reward(p, gain, cost=cost, type=RewardType.Visit)
        except AttrNotEnoughError:
            incr_visit_flag(count=-count)
            return fail_msg(msgtype, reason="钻石不足")
        if p.visit_free_rest_count < count:
            p.visit_free_used_count += p.visit_free_rest_count
            count -= p.visit_free_rest_count
        else:
            p.visit_free_used_count += count
            count = 0
        p.visit_today_used_count += count
        rsp = poem_pb.VisitResponse(ids=ids)
        if luck:
            rsp.rewards = build_reward(luck)
        campaign = g_campaignManager.visit_campaign
        if campaign.is_open():
            config = campaign.get_current()
            p.visit_group = config.reward_group
        p.visit_time = int(time.time())
        p.save()
        p.sync()
        from chat.manager import on_visit
        on_visit(p, rsp.rewards)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.VISIT_REWARD)
    @level_required(tag="visit")
    def visit_reward(self, msgtype, body):
        campaign = g_campaignManager.visit_campaign
        if campaign.is_open():
            group = campaign.get_current().reward_group
        else:
            group = 1
        configs = get_config(VisitRewardByGroupConfig).get(group)
        rsp = poem_pb.VisitRewardResponse()
        for config in sorted(configs, key=lambda s: s.pious, reverse=True):
            info = config._asdict()
            info["rewards"] = build_reward(parse_reward(config.rewards))
            rsp.items.add(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.BEG_INFO)
    def beg_info(self, msgtype, body):
        p = self.player
        tasks = get_daily_sp_tasks(p)
        rsp = poem_pb.TaskList()
        rsp.tasks = tasks
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.REFRESH_TREASURE)
    def treasure_refresh(self, msgtype, body):
        p = self.player
        try:
            apply_reward(
                p, {},
                cost={'gold': get_cons_value("TreasureRefreshGold")},
                type=RewardType.TreasureRefresh)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="钻石不足")
        refresh_treasure(p)
        return success_msg(msgtype, "")

    @rpcmethod(msgid.CLEAN_TREASURE_CD)
    def treasure_clean_cd(self, msgtype, body):
        p = self.player
        try:
            apply_reward(
                p, {},
                cost={'gold': get_cons_value("TreasureCleanCDGold")},
                type=RewardType.TreasureCleanCD)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="钻石不足")
        p.treasure_cd = 0
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.ENTER_TREASURE)
    def treasure_enter(self, msgtype, body):
        p = self.player
        if not p.treasure_count:
            return fail_msg(msgtype, reason="not enough challenge times")
        now = int(time.time())
        if p.treasure_cd > now:
            return fail_msg(msgtype, reason="CD冷却中")
        rsp = enter_treasure(p)
        rsp.verify_code = PlayerTreasureLock.lock(p.entityID, force=True)
        rsp.need_count = get_cons_value("TreasureNeedBuffCount")
        rsp.round_count = get_cons_value("TreasureRoundCount")
        logger.debug(rsp)
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.END_TREASURE)
    def treasure_end(self, msgtype, body):
        p = self.player
        req = poem_pb.EndTreasure()
        req.ParseFromString(body)
        if not PlayerTreasureLock.unlock(p.entityID, req.verify_code):
            logger.debug("verify_code %s", req.verify_code)
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if not p.treasure_cache:
            logger.debug("not treasure_cache")
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        rewards = []
        for type, subtype, count in p.treasure_cache:
            if type == TreasureGrid.TreasureGridTypeReward:
                rewards.append(poem_pb.RewardData(
                    type=subtype, count=count))
        r1 = parse_reward(req.rewards)
        r2 = parse_reward(rewards)
        logger.debug("reward %r %r", r1, r2)
        if not compare_reward(r1, r2):
            logger.debug("compare reward fail")
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        config = get_config(TreasureChestConfig)[p.treasure_type]
        gain_chest = bool(req.gain_chest)
        if gain_chest:
            reward = open_reward(RewardType.Treasure, config.drop)
            result = reward.apply_after()
        else:
            result = {}
        result = combine_reward(r1, result)
        rsp = poem_pb.EndTreasureResponse()
        finisheds = []
        finisheds.append(gain_chest)
        finisheds.append(bool(req.kill_monster))
        need = get_cons_value("TreasureNeedBuffCount")
        finisheds.append(len(req.rewards) >= need)
        rsp.stars = len(filter(lambda s: s, finisheds))
        if rsp.stars == len(finisheds):
            rewardex = open_reward(RewardType.Treasure, config.dropex)
            rsp.rewardsex = build_reward(rewardex.apply(p))
        rsp.finisheds = finisheds
        apply_reward(p, result, type=RewardType.Treasure)
        build_reward_msg(rsp, result)
        now = int(time.time())
        p.treasure_used_count += 1
        p.treasure_cd = now + 10 * 60
        p.treasure_cache = []
        refresh_treasure(p)
        on_treasure_count(p)
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    # {{{ tap
    @rpcmethod(msgid.START_TAP)
    def tap_start(self, msgtype, body):
        p = self.player
        start_tap(p)
        m = get_config(TapMonsterConfig)[p.tap_monster]
        rsp = poem_pb.StartTapResponse(**m._asdict())
        rsp.index = p.tap_hurts_index
        # from: [1, 1, 1, 10, 10, 1, 1, 10, 1]
        # to  : [[1, 3], [10, 2], [1, 2], [10, 1], [1, 1]]
        prev = None
        result = []
        for i in p.tap_hurts:
            if prev is not None:
                if i == prev:
                    result[-1][1] += 1
                else:
                    result.append([i, 1])
            else:
                result.append([i, 1])
            prev = i
        for hurt, repeat in result:
            rsp.hurts.append(hurt)
            rsp.repeats.append(repeat)
        logger.debug("tap start")
        logger.debug(rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.END_TAP)
    def tap_end(self, msgtype, body):
        p = self.player
        req = poem_pb.EndTap()
        req.ParseFromString(body)
        logger.debug("tap end")
        logger.debug(req)
        reward = end_tap(p, req.count)
        if not reward:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        rsp = poem_pb.EndTapResponse()
        build_reward_msg(rsp, reward)
        logger.debug(rsp)
        on_tap_count(p, req.count)
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SAVE_TAP)
    def tap_save(self, msgtype, body):
        p = self.player
        req = poem_pb.SaveTap()
        req.ParseFromString(body)
        logger.debug("tap save")
        logger.debug(req)
        if not save_tap(p, req.count):
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        on_tap_count(p, req.count)
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.ONEKEY_TAP)
    def tap_onekey(self, msgtype, body):
        p = self.player
        if not p.tap_onekey:
            return fail_msg(msgtype, msgTips.FAIL_MSG_CANT_TAP_ONEKEY)
        rsp = poem_pb.OnekeyTapResponse()
        reward, count = onekey_tap(p)
        m = get_config(TapMonsterConfig)[p.tap_monster]
        rsp.next = poem_pb.StartTapResponse(**m._asdict())
        rsp.next.hurts = p.tap_hurts
        rsp.next.index = p.tap_hurts_index
        build_reward_msg(rsp, reward)
        on_tap_count(p, count)
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)
    # }}}

    # {{{ 触发事件
    @rpcmethod(msgid.TRIGGER_FB_INFO)
    def trigger_fb_info(self, msgtype, body):
        p = self.player
        if not check_trigger_event_type(p, EventType.Fb):
            return fail_msg(msgtype, reason="无触发事件或错误的事件类型")
        config = get_config(TriggerEventConfig)[p.trigger_event]
        rsp = poem_pb.TriggerFbInfo(fbID=config.event_param)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.TRIGGER_CHEST_INFO)
    def trigger_chest_info(self, msgtype, body):
        p = self.player
        if not check_trigger_event_type(p, EventType.Chest):
            return fail_msg(msgtype, reason="无触发事件或错误的事件类型")
        # config = get_config(TriggerEventConfig)[p.trigger_event]
        rsp = poem_pb.TriggerChestInfo(
            double_cost=get_cons_value("TriggerChestDoubleCost"))
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.TRIGGER_CHEST_RECV)
    def trigger_chest_recv(self, msgtype, body):
        p = self.player
        if not check_trigger_event_type(p, EventType.Chest):
            return fail_msg(msgtype, reason="无触发事件或错误的事件类型")
        req = poem_pb.TriggerChestRecvRequest()
        req.ParseFromString(body)
        config = get_config(TriggerEventConfig)[p.trigger_event]
        chest = get_config(TriggerChestConfig).get(config.event_param)
        if not chest:
            return fail_msg(msgtype, reason="不存在的宝箱")
        if req.is_double:
            cost = {"gold": get_cons_value("TriggerChestDoubleCost")}
            gain = {}
            for i in range(get_cons_value("TriggerChestMultiple")):
                gain = combine_reward([chest.reward], [], data=gain)
        else:
            cost = {}
            gain = parse_reward([chest.reward])
        try:
            apply_reward(p, gain, cost=cost, type=RewardType.TriggerChest)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="钻石不足")
        p.trigger_event = 0
        p.save()
        p.sync()
        rsp = poem_pb.TriggerChestRecv()
        build_reward_msg(rsp, gain)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.TRIGGER_CHESTS_INFO)
    def trigger_chests_info(self, msgtype, body):
        p = self.player
        if not check_trigger_event_type(p, EventType.Chests):
            return fail_msg(msgtype, reason="无触发事件或错误的事件类型")
        config = get_config(TriggerEventConfig)[p.trigger_event]
        chest = get_config(TriggerChestsConfig).get(config.event_param)
        reward = chest.rewards[0]  # 默认第一个是最好的
        rsp = poem_pb.TriggerChestsInfo(
            more_cost=get_cons_value("TriggerChestsMoreCost"))
        build_reward_msg(rsp, parse_reward([reward]))
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.TRIGGER_CHESTS_RECV)
    def trigger_chests_recv(self, msgtype, body):
        p = self.player
        if not check_trigger_event_type(p, EventType.Chests):
            return fail_msg(msgtype, reason="无触发事件或错误的事件类型")
        config = get_config(TriggerEventConfig)[p.trigger_event]
        chest = get_config(TriggerChestsConfig).get(config.event_param)
        if len(p.trigger_chests) > 0:
            cost = {"gold": get_cons_value("TriggerChestsMoreCost")}
        else:
            cost = {}
        rests = set(range(len(chest.rewards))) - p.trigger_chests
        if not rests:
            return fail_msg(msgtype, reason="已经没有宝箱了")
        index = choice_one(list(rests))
        is_best = False
        if index == 0:
            p.trigger_event = 0
            is_best = True
        gain = parse_reward([chest.rewards[index]])
        try:
            apply_reward(p, gain, cost=cost, type=RewardType.TriggerChests)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="钻石不足")
        p.trigger_chests.add(index)
        p.save()
        p.sync()
        rsp = poem_pb.TriggerChestsRecv(is_best=is_best)
        build_reward_msg(rsp, gain)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.TRIGGER_TASK_INFO)
    def trigger_task_info(self, msgtype, body):
        p = self.player
        if not check_trigger_event_type(p, EventType.Task):
            return fail_msg(msgtype, reason="无触发事件或错误的事件类型")
        config = get_config(TriggerEventConfig)[p.trigger_event]
        task = get_config(TaskConfig).get(config.event_param)
        if not task:
            return fail_msg(msgtype, reason="不存在的任务")
        rsp = poem_pb.TriggerTaskInfo(task_name=task.title)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.TRIGGER_STORE_INFO)
    def trigger_store_info(self, msgtype, body):
        p = self.player
        if not check_trigger_event_type(p, EventType.Store):
            return fail_msg(msgtype, reason="无触发事件或错误的事件类型")
        config = get_config(TriggerEventConfig)[p.trigger_event]
        goods = get_config(TriggerStoreConfig).get(config.event_param)
        if not goods:
            return fail_msg(msgtype, reason="没有这个商品")
        info = goods._asdict()
        info["rewards"] = build_reward(parse_reward([goods.reward]))
        rsp = poem_pb.TriggerStoreInfo(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.TRIGGER_STORE_BUY)
    def trigger_store_buy(self, msgtype, body):
        p = self.player
        if not check_trigger_event_type(p, EventType.Store):
            return fail_msg(msgtype, reason="无触发事件或错误的事件类型")
        config = get_config(TriggerEventConfig)[p.trigger_event]
        goods = get_config(TriggerStoreConfig).get(config.event_param)
        if not goods:
            return fail_msg(msgtype, reason="没有这个商品")
        cost = parse_reward([{
            'count': goods.discount_price,
            'type': goods.discount_price_type}])
        gain = parse_reward([goods.reward])
        try:
            apply_reward(p, gain, cost=cost, type=RewardType.TriggerStore)
        except AttrNotEnoughError as e:
            if e.attr == "gold":
                return fail_msg(msgtype, reason="钻石不足")
            elif e.attr == "money":
                return fail_msg(msgtype, reason="金币不足")
            else:
                return fail_msg(msgtype, reason="消耗不足")
        p.trigger_event = 0
        p.save()
        p.sync()
        return success_msg(msgtype, "")
    # }}}

    @rpcmethod(msgid.DLC_LIST)
    def dlc_list(self, msgtype, body):
        rsp = poem_pb.DlcList()
        configs = get_config(DlcConfig)
        now = int(time.time())
        for k, v in configs.items():  # TODO cd
            camp = g_dlcCampaignManager.campaigns.get(k)
            cd = 0
            desc = v.end_desc
            open_cd = max((v.open_time or 0) - now, 0)
            if v.open_time and open_cd > 0:
                desc = v.open_desc
            else:
                if camp.is_open():
                    cd = camp.get_end_time() - now
                    desc = v.start_desc
            info = v._asdict()
            rsp.infos.add(
                dlcID=k, cd=cd,
                desc=desc, open_cd=open_cd,
                **info
            )
        logger.debug(rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DLC_SCENE_LIST)
    def dlc_scene_list(self, msgtype, body):
        p = self.player
        req = poem_pb.DlcSceneListRequest()
        req.ParseFromString(body)
        dlc = get_config(DlcConfig).get(req.dlcID)
        if not dlc:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        now = int(time.time())
        if dlc.open_time and dlc.open_time - now > 0:
            return fail_msg(msgtype, reason="活动尚未开始")
        scenes = get_config(FbInfoBySceneConfig)
        configs = get_config(DlcFbInfoConfig)
        fbinfos = get_config(FbInfoConfig)
        rsp = poem_pb.DlcSceneList()
        for each in dlc.scenes:
            info = rsp.infos.add(sceneID=each)
            group_by_dlc_type = {}
            fbs = [i.ID for i in scenes.get(each, [])]
            if fbs:
                info.enable = bool(validate_prevs(p, fbs[0]))
                for fbID in fbs:
                    config = configs.get(fbID)
                    if not config:
                        continue
                    group_by_dlc_type.setdefault(
                        config.type, []).append(fbID)
            # NOTE 最高星数为1，与副本不一致
            for t, fs in group_by_dlc_type.items():
                scores = 0
                for fbID in fs:
                    fbinfo = fbinfos.get(fbID)
                    if not fbinfo or fbinfo.sceneID != each:
                        continue
                    dlcfbinfo = configs.get(fbID)
                    if not dlcfbinfo or dlcfbinfo.type != t:
                        continue
                    scores += p.fbscores.get(fbID, {}).get("score", 0)
                info.lights.add(
                    type=t, scores=scores, max_scores=len(fs))
        rsp.campaign = get_campaign_info(p, req.dlcID)
        # logger.debug(rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DLC_FB_LIST)
    def dlc_fb_list(self, msgtype, body):
        p = self.player
        req = poem_pb.DlcFbListRequest()
        req.ParseFromString(body)
        scene = get_config(SceneInfoConfig).get(req.sceneID)
        if not scene:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        configs = get_config(FbInfoConfig)
        # dlcfbs = get_config(DlcFbInfoConfig)
        rsp = poem_pb.DlcFbList()
        if scene.fbs:
            now = int(time.time())

            def fb_info(fb, progress):
                info = configs[fb.fbID]
                # dlc_fb = dlcfbs[fb.fbID]
                fb.cleared = (fb.fbID in progress)
                fb.isNew = (fb.fbID not in p.fbscores)
                dispatch = p.dlc_dispatch.get(fb.fbID, {})
                fb.dispatching = bool(dispatch)
                if fb.dispatching:
                    fb.dispatch_cd = max(dispatch.get("time", 0) - now, 0)
                if not info:
                    return
                for i in info.post:
                    if configs[i].sceneID == info.sceneID:
                        fb_info(fb.subs.add(fbID=i), progress)
            fbID = scene.fbs[0]
            config = get_config(DlcFbInfoConfig)[fbID]
            dlcID = config.dlcID
            progress = p.dlc_progress.get(dlcID, [])
            rsp.fb.fbID = fbID
            fb_info(rsp.fb, progress)
        rsp.boss.fbID = scene.subtype
        rsp.boss.cleared = bool(scene.subtype in progress)
        # logger.debug(rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DLC_TARGET_DETAIL)
    def dlc_target_detail(self, msgtype, body):
        p = self.player
        req = poem_pb.DlcTargetDetailRequest()
        req.ParseFromString(body)
        configs = get_config(DlcFbInfoConfig)
        config = configs.get(req.fbID)
        # logger.debug(req)
        if not config:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if not validate_prevs(p, req.fbID):
            return fail_msg(msgtype, reason="前置未通")
        if not validate_dlc_fb(p, req.fbID):
            return fail_msg(msgtype, reason="此关已通")
        #  validate fb type
        #  zombineID = npc2zombie(config.robot, max(p.level, 30))
        #  zombine = get_zombie(zombineID)
        # 匹配规则
        detail = search_target(p, req.fbID)
        rsp = poem_pb.TargetDetailResponse(**detail)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DLC_HELPER_LIST)
    def dlc_helper_list(self, msgtype, body):
        p = self.player
        req = poem_pb.DlcHelperListRequest()
        req.ParseFromString(body)
        now = int(time.time())
        if req.social == 1:  # friend
            helpers = list(p.friendset)
        else:
            if not p.factionID:
                helpers = []
            else:
                f = Faction.simple_load(p.factionID, ["memberset"])
                helpers = list(f.memberset)
                try:
                    helpers.remove(p.entityID)
                except ValueError:
                    pass
            if req.social == 3:  # both
                helpers += list(p.friendset)
                helpers = list(set(helpers))
        rsp = poem_pb.DlcHelperList()
        details = []
        for helper in helpers:
            detail = get_opponent_detail(helper)
            last = int(time.mktime(
                detail['lastlogin'].timetuple()
            ))
            detail['time'] = now - last
            detail["dlc_cd"] = get_helper_cd(p, helper, now=now)
            details.append(detail)
        update_onlines(details)
        rsp.helpers = details
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DLC_DISPATCH_INFO)
    def dlc_dispatch_info(self, msgtype, body):
        p = self.player
        req = poem_pb.DlcDispatchInfoRequest()
        req.ParseFromString(body)
        config = get_config(DlcFbInfoConfig).get(req.fbID)
        assert config.type == DlcFbType.Dispatch
        # 检查关卡开启
        if not validate_prevs(p, req.fbID):
            return fail_msg(msgtype, reason="前置未通")
        if not validate_dlc_fb(p, req.fbID):
            return fail_msg(msgtype, reason="此关已通")
        #  # 是否进行中
        dispatch = p.dlc_dispatch.get(req.fbID)
        if not dispatch:
            dd = {"cd": config.cd}
        else:
            now = int(time.time())
            dd = dispatch
            dd["cd"] = max(dd["time"] - now, 0)
        rsp = poem_pb.DlcDispatchInfo(**dd)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DLC_DISPATCH)
    def dlc_dispatch(self, msgtype, body):
        p = self.player
        req = poem_pb.DlcDispatchRequest()
        req.ParseFromString(body)
        # 检查关卡开启
        if not validate_prevs(p, req.fbID):
            return fail_msg(msgtype, reason="前置未通")
        if not validate_dlc_fb(p, req.fbID):
            return fail_msg(msgtype, reason="此关已通")
        # 校验精灵
        if not validate_start(p, req.fbID, req.pets):
            return fail_msg(msgtype, reason="精灵校验失败")
        pets = []
        now = int(time.time())
        for pp in req.pets:
            if pp:
                pet = p.pets.get(pp)
                if not pet or max(pet.dispatched - now, 0):
                    return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
                pets.append(pet)
        config = get_config(DlcFbInfoConfig)[req.fbID]
        for pet in pets:
            pet.dispatched = now + config.cd
            pet.save()
            pet.sync()
        p.dlc_dispatch[req.fbID] = {"pets": req.pets, "time": now + config.cd}
        dd = dict(p.dlc_dispatch[req.fbID])
        dd["cd"] = max(dd["time"] - now, 0)
        rsp = poem_pb.DlcDispatchInfo(**dd)
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DLC_DISPATCH_END)
    def dlc_dispatch_end(self, msgtype, body):
        p = self.player
        req = poem_pb.DlcDispatchEndRequest()
        req.ParseFromString(body)
        # 检查关卡开启
        if not validate_prevs(p, req.fbID):
            return fail_msg(msgtype, reason="前置未通")
        if not validate_dlc_fb(p, req.fbID):
            return fail_msg(msgtype, reason="此关已通")
        dispatch = p.dlc_dispatch.get(req.fbID)
        if not dispatch:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        now = int(time.time())
        if now < dispatch["time"]:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        reward = apply_dlc_reward(req.fbID, isfirst=is_first(p, req.fbID))
        apply_reward(p, reward, type=RewardType.DlcDispatch)
        set_dlc_progress(p, req.fbID)
        set_fb_score(p, req.fbID, 1)   # FIXME
        from task.manager import on_end_dlc_fb
        from task.manager import on_dlc_score
        from task.manager import on_end_spec_fb_count
        from task.manager import on_end_fb_count
        on_end_spec_fb_count(p, req.fbID)
        on_end_fb_count(p, req.fbID)
        on_end_dlc_fb(p, req.fbID)
        on_dlc_score(p)
        p.save()
        p.sync()
        rsp = poem_pb.DlcDispatchEnd()
        build_reward_msg(rsp, reward)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DLC_RESET)
    def dlc_reset(self, msgtype, body):
        req = poem_pb.DlcResetRequest()
        req.ParseFromString(body)
        p = self.player
        reset_dlc_progress(p, req.sceneID)
        p.save()
        p.sync()
        req = poem_pb.DlcFbListRequest(sceneID=req.sceneID)
        return self.dlc_fb_list(msgtype, str(req.SerializeToString()))

    @rpcmethod(msgid.DLC_STAR_PACKS_INFO)
    def dlc_star_packs_info(self, msgtype, body):
        p = self.player
        req = poem_pb.DlcStarPacksInfoRequest()
        req.ParseFromString(body)
        group = get_config(DlcStarPacksByDlcConfig).get(req.dlcID, [])
        configs = get_config(DlcStarPacksConfig)
        rsp = poem_pb.DlcStarPacksInfo()
        for each in group:
            config = configs[each.ID]
            if each.ID in p.dlc_star_packs_end:
                continue
            rsp.packs.add(
                id=config.ID, star=config.score,
                rewards=build_reward(
                    parse_reward(config.rewards)))
        # rsp.rank = get_current_rank("DLC%d" % req.dlcID, p.entityID)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.DLC_STAR_PACKS_RECV)
    def dlc_star_packs_recv(self, msgtype, body):
        req = poem_pb.DlcStarPacksRecv()
        req.ParseFromString(body)
        p = self.player
        if req.id in p.dlc_star_packs_end:
            return fail_msg(msgtype, reason="领过了")
        config = get_config(DlcStarPacksConfig).get(req.id)
        if not config:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        score = get_dlc_score(p, config.dlcID)
        if score < config.score:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        apply_reward(
            p, parse_reward(config.rewards),
            type=RewardType.DlcStarPacks)
        p.dlc_star_packs_end.add(req.id)
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.DLC_TASK_DONE)
    def dlc_done_task(self, msgtype, body):
        p = self.player
        today = datedate.today()
        req = poem_pb.DlcTaskDoneRequest()
        req.ParseFromString(body)
        # logger.debug(req)
        dlc_task = get_config(DlcTaskConfig).get(req.taskID)
        if not dlc_task:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        campaign = g_dlcCampaignManager.campaigns.get(dlc_task.dlcID)
        if not campaign or not campaign.is_open() or\
                is_done(p, req.taskID, today):
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        now = int(time.time())
        cd = p.dlc_tasks_cd.get(dlc_task.dlcID, 0)
        if max(cd - now, 0):
            return fail_msg(msgtype, reason="cd中")
        try:
            apply_reward(
                p, {}, cost={"gold": dlc_task.gold},
                type=RewardType.DlcDoneTask)
        except AttrNotEnoughError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        done_task(p, req.taskID, today)
        from task.manager import on_dlc_score
        on_dlc_score(p)
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.MAZE_POOL_RECV)
    def maze_pool_recv(self, msgtype, body):
        p = self.player
        if not p.money_rest_pool:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        result = apply_reward(
            p, {"money": p.money_rest_pool},
            type=RewardType.MazePool)
        p.money_rest_pool = 0
        p.save()
        p.sync()
        rsp = poem_pb.MazePoolResponse()
        build_reward_msg(rsp, result)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.MAZE_CASE_RECV)
    def maze_case_recv(self, msgtype, body):
        p = self.player
        req = poem_pb.MazeEventRequest()
        req.ParseFromString(body)
        index = req.index or 0
        try:
            event = p.mazes[index]
        except IndexError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        count = 1
        cost = {}
        if req.treble:
            count = 3
            cost = {"gold": p.maze_case_cost}
        if event.get("type") != MazeEventType.Case:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        drop = event.get("argv", 0)
        drops = [drop] * count
        if drop:
            reward = open_reward(RewardType.MazeDrop, *drops)
        if cost:
            reward.cost_after(p, **cost)
        result = reward.apply(p)
        p.mazes.remove(event)
        p.touch_mazes()
        p.save()
        p.sync()
        rsp = poem_pb.MazeCaseResponse()
        build_reward_msg(rsp, result)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.MAZE_EVENTS)
    def maze_events(self, msgtype, body):
        p = self.player
        rsp = poem_pb.MazeEvents()
        now = int(time.time())
        pending = []
        event_exists = set()
        events = []
        flag = False
        for maze in p.mazes[::-1]:
            cd = max(maze["time"] - now, 0)
            if cd == 0:
                flag = True
                pending.append(maze)
                continue
            if maze["type"] == MazeEventType.Shop:
                if (maze["type"], maze["argv"]) in event_exists:
                    flag = True
                    pending.append(maze)
                    continue
                else:
                    event_exists.add((maze["type"], maze["argv"]))
            events.insert(0, dict(cd=cd, **maze))
        rsp.events = events
        for each in pending:
            p.mazes.remove(each)
        if flag:
            p.touch_mazes()
            p.save()
            p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.MAZE_STEP)
    def maze_step(self, msgtype, body):
        p = self.player
        req = poem_pb.MazeStepRequest()
        req.ParseFromString(body)
        count = p.maze_rest_count if req.onekey else 1
        # check count
        if count > p.maze_rest_count:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        gains = {}
        attr = {}
        mazes = []
        incr = {}
        results = step_mazes(p, attr, incr, count)
        count = len(results)
        rsp = poem_pb.MazeStepResponse()
        for each in results:
            drop = each.get("drop", 0)
            if drop:
                maze_drop = open_reward(RewardType.MazeDrop, drop)
                rewards = maze_drop.apply_after()
                gains = combine_reward(rewards, {}, data=gains)
            if each.get("append", False):
                mazes.append(each)
            drop = get_cons_value("MazeMustDropID")
            must_drop = open_reward(RewardType.MazeDrop, drop)
            rewards = must_drop.apply_after()
            gains = combine_reward(rewards, {}, data=gains)
            rsp.events.add(**each)
        rsp.rewards = build_reward(gains)
        for each in mazes:
            p.mazes.append(each)
        apply_reward(p, gains, type=RewardType.MazeDrop)
        for each, value in attr.items():
            setattr(p, each, value)
        for each, value in incr.items():
            setattr(p, each, getattr(p, each) + value)
        if "mall_silver_open_remain" in attr:
            try:
                del p.malls[MallType.Silver]
            except KeyError:
                pass
        if "mall_golden_open_remain" in attr:
            try:
                del p.malls[MallType.Golden]
            except KeyError:
                pass
        p.touch_mazes()
        p.maze_step_count += count
        on_maze_count(p, count)
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.AMBITION_UP)
    def ambition_up(self, msgtype, body):
        p = self.player
        req = poem_pb.AmbitionUpRequest()
        req.ParseFromString(body)
        if not req.type:
            configs = get_config(AmbitionConfig)
            level = p.level
            ambition = str(p.ambition) or ''
            attr = "ambition"
        else:
            configs = get_config(VipAmbitionConfig)
            level = p.vip
            ambition = str(p.vip_ambition) or ''
            attr = "vip_ambition"
        index = req.index or 0
        config = configs.get(index + 1)
        if not config:
            return fail_msg(msgtype, reason="没有下一个了")
        if level < config.level:
            return fail_msg(msgtype, reason="等级不足")
        random_configs = get_config(RandomAmbitionConfig)
        if req.use_gold:
            c = weighted_random2([[
                i.step, i.golden_pro] for i in random_configs.values()])
            cost = {"gold": get_cons_value("AmbitionGoldUpCost")}
        else:
            c = weighted_random2([[
                i.step, i.pro] for i in random_configs.values()])
            cost = {"soul": get_cons_value("AmbitionUpCost")}
        if c not in random_configs:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        try:
            ll = list(ambition)
            ll[index] = str(c)
            ambition = ''.join(ll)
        except IndexError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        apply_reward(p, {}, cost, type=RewardType.AmbitionUp)
        setattr(p, attr, ambition)
        if c >= 5:
            p.ambition_count += 1
        from task.manager import on_ambition
        on_ambition(p)
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.DAILY_REBORN)
    def reborn(self, msgtype, body):
        p = self.player
        cost = get_cons_value("DailyRebornCost")
        # if not g_campaignManager.dailypvp_campaign.is_open():
        #     return fail_msg(msgtype, msgTips.FAIL_MSG_DAILY_CAMPAIGN_CLOSED)
        try:
            apply_reward(
                p, {}, cost={"gold": cost}, type=RewardType.DailyPVPReborn)
        except AttrNotEnoughError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        changeds = set()
        lineups = [
            p.lineups.get(LineupType.Daily, []),
            p.lineups.get(LineupType.City, []),
        ]
        for lineup in lineups:
            for each in lineup:
                pet = p.pets.get(each)
                if pet:
                    pet.daily_dead = False
                    pet.daily_restHP = 0
                    changeds.add(pet)
        for pet in changeds:
            pet.save()
            pet.sync()
        p.daily_dead_cd = 0
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.DAILY_INSPIRE)
    def inspire(self, msgtype, body):
        p = self.player
        # if not g_campaignManager.dailypvp_campaign.is_open():
        #     return fail_msg(msgtype, msgTips.FAIL_MSG_DAILY_CAMPAIGN_CLOSED)
        if not p.daily_inspire_rest_count:
            return fail_msg(msgtype, reason="次数不足")
        try:
            apply_reward(
                p, {}, cost={"gold": p.daily_inspire_cost},
                type=RewardType.DailyInspire)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="钻石不足")
        p.daily_inspire_used_count += 1
        p.save()
        p.sync()
        return success_msg(msgtype, "")
