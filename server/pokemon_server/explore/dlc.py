# coding:utf-8
import time
import logging
logger = logging.getLogger("dlc")
from datetime import date as datedate

from yy.utils import choice_one

from state.base import StateObject
from state.base import StartState
from protocol import poem_pb
from config.configs import get_cons_value
from config.configs import get_config
from config.configs import DlcConfig
from config.configs import DlcFbInfoConfig
from config.configs import FbInfoConfig
from config.configs import SceneInfoConfig
from config.configs import FbInfoBySceneConfig
from config.configs import PetConfig
from config.configs import TaskConfig
from config.configs import DlcCampaignConfig
from config.configs import DlcCampaignByDlcIDConfig
from config.configs import DlcTaskConfig

from player.model import PlayerMaxPowerRanking

from reward.manager import parse_reward
from reward.manager import build_reward
from reward.manager import combine_reward

from scene.manager import get_fb_score
# from scene.manager import validate_prevs

from pvp.manager import get_opponent_detail
# from pvp.manager import npc2zombie
from pvp.manager import get_zombie
from pvp.manager import get_zombies_by_power
from pvp.manager import get_zombies_by_level

from entity.manager import g_entityManager

from .constants import DlcFbType


def search_target(p, fbID):
    detail = p.dlc_detail_cache.get(fbID, {})
    if detail:
        return detail
    dlc_fb = get_config(DlcFbInfoConfig)[fbID]
    lo, hi = dlc_fb.range
    if lo or hi:
        spower = (1 + lo / float(100)) * p.max_power
        epower = (1 + hi / float(100)) * p.max_power
        if p.max_power > spower and p.max_power < epower:
            count = 11
        else:
            count = 10
        ranks = PlayerMaxPowerRanking.get_range_by_score(
            spower, epower, count=count)
        try:
            ranks.remove(p.entityID)
        except ValueError:
            pass
        if ranks:
            if dlc_fb.rule == 1:
                target = ranks[-1]
            elif dlc_fb.rule == 2:
                target = ranks[0]
            else:
                target = choice_one(ranks)
            detail = get_opponent_detail(target)
    if not detail:  # robot
        lo, hi = dlc_fb.rob_range
        if lo or hi:
            spower = (1 + lo / float(100)) * p.max_power
            epower = (1 + hi / float(100)) * p.max_power
            zombies = get_zombies_by_power(
                spower, epower, count=5, hide=False, group=dlc_fb.robot_group)
            logger.debug("zombies by power: %r", zombies)
        if not zombies:
            zombies = get_zombies_by_level(
                p.level, hide=False, group=dlc_fb.robot_group)
            logger.debug("zombies by level: %r", zombies)
        if dlc_fb.rob_rule == 1:
            target = zombies[-1]
        elif dlc_fb.rob_rule == 2:
            target = zombies[0]
        else:
            target = choice_one(zombies)
        detail = get_zombie(target)
    p.dlc_detail_cache[fbID] = detail
    return detail


def get_helper_cd(p, entityID, now=None):
    if not now:
        now = int(time.time())
    dlc_cd = 0
    last = p.dlc_helpers.get(entityID, 0)
    if last:
        dlc_cd = max(
            get_cons_value("DlcHelperCD") - (now - last), 0)
    return dlc_cd


def apply_dlc_reward(fbID, reward=None, isfirst=False):
    if not reward:
        reward = {}
    config = get_config(DlcFbInfoConfig).get(fbID)
    if not config:
        return reward
    if isfirst:
        reward = combine_reward(reward, config.first_rewards)
    return combine_reward(reward, config.rewards)


def set_dlc_progress(p, fbID):
    config = get_config(DlcFbInfoConfig).get(fbID)
    if not config:
        return
    if config.type == DlcFbType.Dispatch:
        del p.dlc_dispatch[fbID]
    dlcID = config.dlcID
    progress = p.dlc_progress.get(dlcID, [])
    progress.append(fbID)
    try:
        del p.dlc_detail_cache[fbID]
    except KeyError:
        pass
    p.dlc_progress[dlcID] = progress
    p.save()


def reset_dlc_progress(p, sceneID):
    scene = get_config(SceneInfoConfig)[sceneID]
    dlcID = get_config(DlcFbInfoConfig)[scene.fbs[0]].dlcID
    progress = p.dlc_progress.get(dlcID, [])
    configs = get_config(FbInfoConfig)
    if progress:
        reseted = []
        for i in progress:
            c = configs.get(i)
            if not c:
                continue
            if c.sceneID != sceneID:
                reseted.append(i)
        p.dlc_progress[dlcID] = reseted
    for i in get_config(FbInfoBySceneConfig).get(sceneID, []):
        if i.ID in p.dlc_dispatch:
            for petID in p.dlc_dispatch[i.ID].get("pets", []):
                pp = p.pets.get(petID)
                if pp:
                    pp.dispatched = 0
                    pp.save()
                    pp.sync()
            del p.dlc_dispatch[i.ID]
    p.dlc_detail_cache.clear()
    p.save()


def __satisfy(cond, value):
    return cond is None or cond <= value


def __equals(cond, value):
    return cond is None or cond == value


def __check_condition(p, cond, pets):
    if not cond:
        return True
    dispatchs = []
    for pos, petID in enumerate(pets):
        if petID <= 0:
            continue
        pet = p.pets.get(petID)
        if not pet:
            return False
        info = get_config(PetConfig).get(pet.prototypeID)
        if not info:
            return False
        dispatchs.append((pos, pet, info))
    #  if cond.get("lock_pose"):
    #      return True
    if cond.get("id"):
        for pos, pet, info in dispatchs:
            if __equals(cond.get("id"), pet.prototypeID) and\
               (cond.get("pose") == 0 or __equals(cond.get("pose"), pos + 1)):
                return True
        return False
    if cond.get("same_id"):
        for pos, pet, info in dispatchs:
            if __equals(cond.get("same_id"), info.same) and\
               __satisfy(cond.get("quality"), info.rarity) and\
               __satisfy(cond.get("stage"), info.step) and\
               __satisfy(cond.get("class"), info.cls) and\
               (cond.get("pose") == 0 or __equals(cond.get("pose"), pos + 1)):
                return True
        return False
    for pos, pet, info in dispatchs:
        if __satisfy(cond.get("quality"), info.rarity) and\
           __satisfy(cond.get("stage"), info.step) and\
           __satisfy(cond.get("class"), info.cls) and\
           (cond.get("attr") is None or (cond.get("attr") & pow(2, info.attr - 1))) and\
           (cond.get("pose") == 0 or __equals(cond.get("pose"), pos + 1)):
            return True
    return False


def validate_start(p, fbID, pets, helperID=None):
    config = get_config(DlcFbInfoConfig).get(fbID)
    if config.type == DlcFbType.Social:
        if helperID and not get_helper_cd(p, helperID):
            return True
        else:
            return False
    else:
        for cond in config.condition:
            if not __check_condition(p, cond, pets):
                return False
    return True


def validate_dlc_fb(p, fbID):
    configs = get_config(DlcFbInfoConfig)
    config = configs.get(fbID)
    dlcID = config.dlcID
    return fbID not in p.dlc_progress.get(dlcID, [])  # 已通


def get_dlc_score(p, dlcID):
    dlc = get_config(DlcConfig)[dlcID]
    scores = 0
    for i in dlc.scenes:
        fbs = get_config(FbInfoBySceneConfig).get(i, [])
        for f in fbs:
            scores += get_fb_score(p, f.ID)
    return scores


def get_campaign_info(p, dlcID):
    from task.manager import get_task_info
    from task.manager import get_plan
    campaign = g_dlcCampaignManager.campaigns.get(dlcID)
    if not campaign or not campaign.is_open():
        return
    rsp = poem_pb.DlcCampaignInfo()
    today = datedate.today()
    dlc_tasks = p.dlc_tasks.get(dlcID, [])
    task = None
    count = 0
    total = len(dlc_tasks)
    configs = get_config(DlcTaskConfig)
    infos = get_config(TaskConfig)
    cost = 0
    for i in sorted(dlc_tasks):
        dlc_task = configs[i]
        info = infos[i]
        is_done = get_plan(p, i, today) >= info.goal
        if dlc_task.rewards:
            rsp.nodes.add(
                rewards=build_reward(
                    parse_reward(dlc_task.rewards)),
                can_receive=(i in p.taskrewards),
                is_done=is_done,
                index=dlc_task.index)
        if is_done:
            count += 1
            if task is None:
                if i in p.taskrewards:
                    task = get_task_info(p, i, today)
                    cost = dlc_task.gold
        elif task is None:
            task = get_task_info(p, i, today)
            cost = dlc_task.gold
    if task:
        now = int(time.time())
        rsp.campaign_cd = max(campaign.get_end_time() - now, 0)
        rsp.task = task
        rsp.count = count
        rsp.total = total
        rsp.cost = cost
        cd = p.dlc_tasks_cd.get(dlcID, 0)
        if cd:
            rsp.cd = max(cd - now, 0)
        return rsp
    return None


class DlcCampaign(StateObject):
    def __init__(self, dlcID):
        super(DlcCampaign, self).__init__()
        self.dlcID = dlcID

    def get_loops(self):
        camp = get_config(DlcCampaignByDlcIDConfig).get(self.dlcID, [])
        cons = get_config(DlcCampaignConfig)
        return [
            [i.start, i.end, (i.ID, i.task)]
            for i in [cons[i.ID] for i in camp]]

    def is_open(self):
        return isinstance(self.state, StartState)

    def get_start_task(self):
        return self.current_loop[1]

    def get_current(self):
        if not self.is_open():
            return None
        configs = get_config(DlcCampaignConfig)
        return configs.get(self.current_loop[0])

    def get_current_time(self):
        config = self.get_current()
        if not config:
            return 0, 0
        return config.start, config.end

    def get_end_time(self):
        _, end = self.get_current_time()
        return end

    def enter_start(self):
        self.reset_task()
        self.reset()
        self.sync()

    def enter_stop(self):
        self.reset()
        self.reset_task()

    def reset(self, p=None):
        if p:
            ps = [p]
        else:
            ps = g_entityManager.players.values()
        for p in ps:
            p.clear_dlc_tasks()
            p.clear_dlc_opened()
            p.sync()

    def sync(self):
        for p in g_entityManager.players.values():
            from task.manager import on_dlc_score
            on_dlc_score(p)

    def reset_task(self, p=None):
        if p:
            ps = [p]
        else:
            ps = g_entityManager.players.values()
        opened = self.is_open()
        start, end = self.get_current_time()
        configs = get_config(DlcTaskConfig)
        for p in ps:
            pending = []
            for each in p.taskrewards:
                task = configs.get(each)
                if task:
                    if task.dlcID != self.dlcID:
                        continue
                    when = p.tasks.get(each, {}).get("when", 0)
                    if opened:
                        if when >= start and when <= end:
                            continue
                    pending.append(each)
            for task in pending:
                try:
                    p.taskrewards.remove(task)
                except KeyError:
                    pass
            p.save()
            p.sync()


class DlcCampaignManager(object):
    def __init__(self):
        self.campaigns = {}

    def reset_task(self, p):
        for campaign in self.campaigns.values():
            campaign.reset_task(p)

    def start(self):
        for dlcID, campaign in self.campaigns.items():
            campaign.stop()
            del self.campaigns[dlcID]
        configs = get_config(DlcConfig)
        for dlcID in configs.keys():
            self.campaigns[dlcID] = DlcCampaign(dlcID)
        for campaign in self.campaigns.values():
            campaign.start()
            campaign.reset()

g_dlcCampaignManager = DlcCampaignManager()
