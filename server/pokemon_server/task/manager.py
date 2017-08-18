# coding:utf-8
'''
taskInfo {
    taskID:{
        plan:进度
        when:修改时间
    }
}
'''

import time
import logging
logger = logging.getLogger('task')
import calendar
from datetime import datetime
from datetime import date as datedate
from datetime import timedelta
from config.configs import get_config
from config.configs import TaskConfig
from config.configs import TaskByTypeConfig
from config.configs import TaskByCondConfig
from config.configs import TaskByGroupConfig
from config.configs import DlcTaskConfig
from config.configs import PetConfig
from config.configs import NewEquipConfig
from config.configs import SevenConfig
from protocol.poem_pb import Task
# from reward.manager import RewardItemType

from explore.dlc import g_dlcCampaignManager

from .constants import TaskCond, TaskType, DailySPState

from gm.proxy import proxy
from entity.manager import g_entityManager


def clock(now, hour, minute):
    return datetime(now.year, now.month, now.day, hour, minute)

SEC = 86400
DAILY_SP_INDEX = 0
DAILY_SP_STATE = DailySPState.Close


def check_daily_sp_state():
    global DAILY_SP_INDEX
    global DAILY_SP_STATE
    now = datetime.now()
    if now >= clock(now, 0, 0) and now < clock(now, 12, 0):
        DAILY_SP_INDEX = 0
        DAILY_SP_STATE = DailySPState.Close
    elif now >= clock(now, 12, 0) and now < clock(now, 14, 0):
        DAILY_SP_INDEX = 0
        DAILY_SP_STATE = DailySPState.Open
        broadcast_tasks_changed()
    elif now >= clock(now, 14, 0) and now < clock(now, 18, 0):
        DAILY_SP_INDEX = 1
        DAILY_SP_STATE = DailySPState.Close
    elif now >= clock(now, 18, 0) and now < clock(now, 20, 0):
        DAILY_SP_INDEX = 1
        DAILY_SP_STATE = DailySPState.Open
        broadcast_tasks_changed()
    elif now >= clock(now, 20, 0) and now < clock(now, 21, 0):
        DAILY_SP_INDEX = 2
        DAILY_SP_STATE = DailySPState.Close
    elif now >= clock(now, 21, 0) and now < clock(now, 23, 59):
        DAILY_SP_INDEX = 2
        DAILY_SP_STATE = DailySPState.Open
        broadcast_tasks_changed()
    else:
        DAILY_SP_INDEX = 0
        # DAILY_SP_STATE = DailySPState.Hide
        DAILY_SP_STATE = DailySPState.Close


def broadcast_tasks_changed():
    # 广播可领取任务数量
    from entity.manager import g_entityManager
    for p in g_entityManager.players.values():
        p.clear_taskrewardscount1()
        p.clear_beg_flag()
        p.sync()


def get_daily_sp_info():
    return DAILY_SP_INDEX, DAILY_SP_STATE


def _get_daily_sp_tasks(task_sp_daily_receiveds):
    configs = get_config(TaskByTypeConfig).get(TaskType.DailySP, [])
    index, state = get_daily_sp_info()
    if not configs:
        return []
    config = configs[index]
    info = get_config(TaskConfig)[config.ID]
    task = dict(info._asdict())
    if state == DailySPState.Close:
        task['state'] = Task.Track
        task['plan'] = 0
    elif state == DailySPState.Open:
        if config.ID in task_sp_daily_receiveds:
            task['state'] = Task.End
        else:
            task['state'] = Task.Done
        task['plan'] = task['goal']
    else:
        raise AssertionError
    return [task]


def get_daily_sp_tasks(player):
    return _get_daily_sp_tasks(player.task_sp_daily_receiveds)


def get_task_info(player, taskID, today):
    configs = get_config(TaskConfig)
    info = configs[taskID]
    task = dict(info._asdict())
    task["state"] = Task.Track
    # FIXME
    plan = get_plan(player, taskID, today)
    if taskID in player.taskrewards:
        task['state'] = Task.Done
    elif plan < task['goal']:
        task['state'] = Task.Track
    else:
        task['state'] = Task.End

    if task['state'] == Task.Done:
        task['plan'] = task['goal']
    else:
        task['plan'] = plan
    #  else:
    #      # FIXME
    #      task['plan'] = get_plan(player, taskID, today)
    #      if info.prev:  # 显示的时候要把上索引的进度减去
    #          prev = configs.get(info.prev)
    #          if prev:
    #              task['plan'] = max(task['plan'] - prev.goal, 0)
    if info.cond == TaskCond.Levelup:  # FIXME
        task['plan'] = player.level
    if info.cond == TaskCond.MonthlyCard30:
        if not player.monthly_card_30:
            task['desc'] = '购买月卡领取奖励'
        else:
            task['desc'] = task['desc'] % player.monthly_card_30
    seven = get_config(SevenConfig).get(taskID)
    if seven:
        task["day"] = seven.day
        task["tab_desc"] = seven.tab_desc
    return task


def get_plan(player, taskID, today):
    task = player.tasks.get(taskID)
    if task:
        if task.get('when'):
            when = datedate.fromtimestamp(task['when'])
            info = get_config(TaskConfig).get(taskID)
            if not info:
                return 0
            if info.type in (
                    TaskType.Daily, TaskType.Faction, TaskType.Trigger):
                if when != today:
                    return 0
            elif info.type == TaskType.Sign:
                if (when.year, when.month) != (today.year, today.month):
                    return 0
            elif info.type == TaskType.Dlc:
                dlc_task = get_config(DlcTaskConfig)[taskID]
                campaign = g_dlcCampaignManager.campaigns.get(dlc_task.dlcID)
                start, end = campaign.get_current_time()
                if task["when"] < start and task["when"] > end:
                    return 0
        return task.get('plan', 0)
    return 0


def done_task(p, taskID, today=None):
    if not today:
        today = datedate.today()
    if is_end(p, taskID, today):
        return
    plan = get_plan(p, taskID, today)
    info = get_config(TaskConfig).get(taskID)
    if not info:
        return
    value = max(info.goal - plan, 0)
    return _set_plan(p, info, today, value=value)


def _set_plan(player, task, today, value=1, replace=False):
    realID = task.ID
    configs = get_config(TaskConfig)
    info = task
    taskID = info.sameID
    task = player.tasks.get(taskID, {})
    if not info:
        return
    logger.debug('set taskID {} value {}'.format(taskID, value))
    if not replace:
        if task.get('when'):
            when = datedate.fromtimestamp(task['when'])
            plan = task.get('plan', 0)
            prev = configs.get(info.prev)
            if prev:
                init = prev.goal
            else:
                init = 0
            if info.type in (
                    TaskType.Daily, TaskType.Faction, TaskType.Trigger):
                if when != today:
                    task['plan'] = init + value
                else:
                    if not plan:
                        task['plan'] = init + value
                    else:
                        task['plan'] += value
            elif info.type == TaskType.Sign:
                if (when.year, when.month) != (today.year, today.month):
                    task['plan'] = init + value
                else:
                    if not plan:
                        task['plan'] = init + value
                    else:
                        task['plan'] += value
            else:
                if not plan:
                    task['plan'] = init + value
                else:
                    task['plan'] += value
        else:
            task['plan'] = value
    else:
        task['plan'] = value
    task['when'] = int(time.time())
    logger.debug("{} {}".format(taskID, task))
    isdone = task['plan'] >= info.goal
    if isdone:
        info = configs[realID]
        player.taskrewards.add(realID)
        if info.type == TaskType.Faction:
            player.faction_taskID = 0
            player.faction_task_done = True
        elif info.type == TaskType.Trigger:
            pass
        from common.log import gm_logger
        t = {TaskType.Normal: "主线"}
        info = configs[realID]
        gm_logger.info({'task': {
            'entityID': player.entityID,
            'userID': player.userID,
            'username': player.username,
            'data': {'taskID': realID},
            'type': t.get(info.type, "支线"),
        }})
    player.tasks[taskID] = task
    return isdone


_cached_sorted_noob_group = None


def get_sorted_noob_group():
    global _cached_sorted_noob_group
    if _cached_sorted_noob_group is not None:
        return _cached_sorted_noob_group
    group = set()
    configs = get_config(TaskConfig)
    noobs = get_config(TaskByTypeConfig).get(TaskType.Noob, [])
    for each in noobs:
        group.add(configs[each.ID].groupID)
    _cached_sorted_noob_group = sorted(group)
    return _cached_sorted_noob_group


def get_current_day(p, now=None):
    now = datetime.now()
    today = now.date()
    configs = get_config(TaskConfig)
    totals = (now - p.createtime).total_seconds()
    # 如果不是今天创建的角色
    if today != p.createtime.date():
        # 判断第一天的任务是否超过24小时了
        if totals <= SEC:
            gg = get_sorted_noob_group()
            if not gg:
                return 8, 0
            groupID = gg[0]
            finish = lambda i: get_plan(p, i.ID, today) >= configs[i.ID].goal
            group = get_config(TaskByGroupConfig).get(groupID, [])
            if not all([finish(i) for i in group]):
                return 1, SEC - totals
        # 超时，或者已经完成则显示第二天的
        tomo = today + timedelta(days=1)
        tomo = datetime.combine(tomo, datetime.min.time())
        remain = int((tomo - now).total_seconds())
        return (today - p.createtime.date()).days + 1, remain
    return 1, SEC - totals


def is_done(player, taskID, today):
    """任务超时，或已经完成"""
    if taskID in player.taskrewards:
        return True
    configs = get_config(TaskConfig)
    info = configs[taskID]
    if info.type == TaskType.Noob:
        # 根据任务配置，取任务是第几天的任务
        # 如果是第一天，超过24小时则算超时，返回True
        # 第n天(n > 1)，超过一天算超时，返回True
        # 未到指定日期，返回True
        group = get_sorted_noob_group()
        cur = group.index(info.groupID) + 1
        if cur == 1:
            # if (datetime.now() - player.createtime).total_seconds() > SEC:
            #     return True
            pass
        else:
            days = (today - player.createtime.date()).days
            if days + 1 < cur:
                return True
    elif info.type == TaskType.Faction:
        # 过滤公会任务
        if taskID == player.faction_taskID and \
                not player.faction_task_done:
            return False
        return True
    elif info.type == TaskType.Trigger:
        if taskID not in player.trigger_tasks:
            return True  # 不让set_plan
    elif info.type == TaskType.Dlc:
        dlc_task = get_config(DlcTaskConfig).get(taskID)
        if not dlc_task:
            return True
        for i in player.dlc_tasks.get(dlc_task.dlcID, []):
            curr = configs[i]
            if get_plan(player, i, today) < curr.goal:
                if taskID == i:
                    cd = player.dlc_tasks_cd.get(dlc_task.dlcID, 0)
                    now = int(time.time())
                    if max(cd - now, 0):
                        return True
                else:
                    return True
                break
    return get_plan(player, info.sameID, today) >= info.goal


def is_end(player, taskID, today):
    info = get_config(TaskConfig)[taskID]
    if info.cond == TaskCond.DailySP:
        if taskID in player.task_sp_daily_receiveds:
            return True
    return is_done(player, taskID, today) and taskID not in player.taskrewards


def is_open(player, taskID):
    configs = get_config(TaskConfig)
    config = configs.get(taskID)
    if config and player.level >= config.openlevel:
        if config.openfb:
            cls = set(player.fbscores).intersection(set(config.openfb))
            if len(cls) != len(config.openfb):
                return False
        return True
    return False


def get_tasks_by(player, func, config_class, type_or_cond, today):
    tasks = get_config(config_class).get(type_or_cond, [])
    result = []
    for task in tasks:
        if not func(player, task.ID, today):
            if is_open(player, task.ID):
                result.append(task.ID)
    return result


def get_end_tasks_by(player, config_class, type_or_cond, today):
    return get_tasks_by(player, lambda p, i, t: not is_end(p, i, t), config_class, type_or_cond, today)


def get_end_tasks_by_type(player, type, today):
    return get_end_tasks_by(player, TaskByTypeConfig, type, today)


def get_end_tasks_by_cond(player, cond, today):
    return get_end_tasks_by(player, TaskByCondConfig, cond, today)


def get_unend_tasks_by(player, config_class, type_or_cond, today):
    return get_tasks_by(player, is_end, config_class, type_or_cond, today)


def get_unend_tasks_by_type(player, type, today):
    return get_unend_tasks_by(player, TaskByTypeConfig, type, today)


def get_unend_tasks_by_cond(player, cond, today):
    return get_unend_tasks_by(player, TaskByCondConfig, cond, today)


def get_undone_tasks_by(player, config_class, type_or_cond, today):
    return get_tasks_by(player, is_done, config_class, type_or_cond, today)


def get_undone_tasks_by_type(player, type, today):
    return get_undone_tasks_by(player, TaskByTypeConfig, type, today)


def get_undone_tasks_by_cond(player, cond, today):
    return get_undone_tasks_by(player, TaskByCondConfig, cond, today)


def filter_unstart_tasks(unend_tasks):
    started_tasks = set()
    configs = get_config(TaskConfig)
    for t in unend_tasks:
        info = configs[t]
        if not info.prev or info.prev not in unend_tasks:
            started_tasks.add(t)
    return started_tasks


def filter_same_tasks(tasks):
    '''同same组的合并为same组内第一个'''
    filtered_same = set()
    for t in tasks:
        info = get_config(TaskConfig)[t]
        filtered_same.add(info.sameID)
    filtered_group = {}
    for t in filtered_same:
        info = get_config(TaskConfig)[t]
        filtered_group.setdefault(info.groupID, set()).add(t)
    return_tasks = set(map(min, filtered_group.values()))
    return return_tasks


def filter_done_same_tasks(tasks):
    '''当有可领取时，防止same组内第一个和可领取的重复出现'''
    return_tasks = set()
    for t in sorted(tasks):
        info = get_config(TaskConfig)[t]
        if info.sameID != t:
            try:
                return_tasks.remove(info.sameID)
            except KeyError:
                pass
            return_tasks.add(t)
        else:
            return_tasks.add(info.sameID)
    return return_tasks


def check_sign_up(player, today=None):
    if player.task_last_sign_up_time:
        if not today:
            today = datedate.today()
        # 同步补签数
        if not player.task_is_calc_sign_up:
            last = datedate.fromtimestamp(player.task_last_sign_up_time)
            if last.year == today.year and\
               last.month == today.month:
                player.task_max_patch_sign_up_count += max(
                    (today.day - last.day) - 1,
                    0)
            else:  # 隔月登录
                player.task_max_patch_sign_up_count = max(today.day - 1, 0)
            player.task_is_calc_sign_up = True
        player.clear_task_today_is_sign_up()
        player.save()
        player.sync()


def get_task_list_by_type(player, type, subtype, today, rsp=None):
    tasks = []
    configs = get_config(TaskConfig)
    # sevens = get_config(SevenConfig)
    if type == TaskType.Sign:
        # 签到只显示当月天数数量的item数量
        # 因为超过当月天数的任务是无法完成的
        _, mr = calendar.monthrange(today.year, today.month)
        ll = [i.ID for i in get_config(TaskByTypeConfig).get(type, [])][:mr]
    elif type == TaskType.Noob:
        ll = [i.ID for i in get_config(TaskByTypeConfig).get(type, [])]
        rsp.current, rsp.remain = get_current_day(player)
    elif type == TaskType.Daily:
        ll = filter_same_tasks(filter_unstart_tasks(
            get_unend_tasks_by_type(player, type, today)
        ))
        rewards = []
        trigger_rewards = []
        faction_taskID = player.faction_taskID
        for r in player.taskrewards:
            config = configs.get(r)
            if not config:
                continue
            if config.type == type:
                rewards.append(r)
            elif config.type == TaskType.Faction:
                faction_taskID = r
            elif config.type == TaskType.Trigger:
                trigger_rewards.append(r)
        ll.update(filter_unstart_tasks(rewards))
        ll = filter_done_same_tasks(ll)
        if faction_taskID:
            rsp.faction_task = Task(
                **get_task_info(player, faction_taskID, today))
        for taskID in list(player.trigger_tasks) + trigger_rewards:
            if is_end(player, taskID, today):
                continue
            rsp.trigger_tasks.add(**get_task_info(player, taskID, today))
    elif type == TaskType.Seven:
        ll = [i.ID for i in get_config(TaskByTypeConfig).get(type, [])]
    else:
        ll = filter_same_tasks(filter_unstart_tasks(
            get_unend_tasks_by_type(player, type, today)
        ))
        ll.update(filter_unstart_tasks([
            r for r in player.taskrewards
            if configs.get(r) and configs.get(r).type == type
        ]))
        ll = filter_done_same_tasks(ll)
        ll = filter_same_tasks(ll)
    if type == TaskType.Normal:
        ll.update(get_end_tasks_by_type(player, type, today))
    for ID in ll:
        info = configs.get(ID)
        if not subtype or info.subtype == subtype:
            task = get_task_info(player, ID, today)
            tasks.append(task)
    if type == TaskType.Daily:
        # 领能量改为化缘
        # tasks.extend(get_daily_sp_tasks(player))
        pass
    check_sign_up(player, today=today)
    if rsp:
        rsp.tasks.extend(tasks)
        logger.debug(rsp)
    return tasks


from functools import update_wrapper


__tasks = {}


def register_task(type):
    def _register_task(f):
        def inner(*args, **kwargs):
            p = args[0]
            today = datedate.today()
            tasks = get_undone_tasks_by_cond(p, type, today)
            tasks = filter_unstart_tasks(tasks)
            configs = get_config(TaskConfig)
            dlc_tasks = set()
            for each in p.dlc_tasks.values():
                dlc_tasks.update(each)

            def recursion(f, task, today, *args, **kwargs):
                if f(task, today, *args, **kwargs):
                    if task.post:
                        post = configs.get(task.post)
                        if post:
                            logger.debug("检查下一个任务")
                            if task.type != TaskType.Dlc:
                                return recursion(
                                    f, post, today, *args, **kwargs)
            servens = get_config(SevenConfig)
            now = int(time.time())
            for t in tasks:
                task = configs.get(t)
                if not task:
                    continue
                if task.type == TaskType.Dlc:
                    if t not in dlc_tasks:
                        continue
                elif task.type == TaskType.Seven:
                    if not p.task_seven_cd:
                        continue
                    cd = p.task_seven_cd - now
                    if cd > 0:
                        day = (7 * 86400 - cd) / 86400 + 1
                        seven = servens.get(t)
                        if not seven:
                            continue
                        if day < seven.day:
                            continue
                        if seven.today and day != seven.day:
                            continue
                    else:
                        continue
                recursion(f, task, today, *args, **kwargs)
        update_wrapper(inner, f)
        __tasks[type] = inner
        return inner
    return _register_task


@register_task(TaskCond.Levelup)
def on_levelup(task, today, player):
    return _set_plan(player, task, today, value=player.level, replace=True)


@register_task(TaskCond.BuySPCount)
def on_buy_sp(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.FBCount)
def on_end_fb_count(task, today, player, fbID, count=1):
    from config.configs import get_config, FbInfoConfig
    fb = get_config(FbInfoConfig).get(fbID)
    if fb and fb.type in task.arg2:
        return _set_plan(player, task, today, value=count)


@register_task(TaskCond.SpecFBCount)
def on_end_spec_fb_count(task, today, player, fbID, count=1):
    from config.configs import get_config, FbInfoConfig
    fb = get_config(FbInfoConfig).get(fbID)
    if fb and fbID in task.arg2:
        return _set_plan(player, task, today, value=count)


@register_task(TaskCond.BreedCount)
def on_breed(task, today, player, pet):
    pet = get_config(PetConfig).get(pet.prototypeID)
    if not pet:
        return
    if pet.cls in task.arg2 or not task.arg2:
        return _set_plan(player, task, today)


@register_task(TaskCond.EvolutionCount)
def on_evolution(task, today, player, pet):
    #  from entity.manager import save_guide
    #  pet = get_config(PetConfig).get(pet.prototypeID)
    #  if not pet:
    #      return
    #  flag = False
    #  if task.arg2:
    #      # 40 表示4星0阶，41 表示4星1阶
    #      for arg in task.arg2:
    #          rarity = arg // 10
    #          step = arg % 10
    #          if pet.rarity == rarity and pet.step == step:
    #              if rarity == 3 and step == 1:  # 第1次 进化到蓝+1任务
    #                  save_guide(player, "FAKE_FIRST_EVO_BLUE1")
    #              elif rarity == 4 and step == 0:  # 第1次 进化到紫任务
    #                  save_guide(player, "FAKE_FIRST_EVO_PURPLE0")
    #              flag = True
    #  else:
    #      flag = True
    #  if flag:
    #      _set_plan(player, task, today)
    #  return False
    pet = get_config(PetConfig).get(pet.prototypeID)
    if pet.cls in task.arg2 or not task.arg2:
        return _set_plan(player, task, today)


@register_task(TaskCond.PatchExchange)
def on_patch_exchange(task, today, player, pet):
    pet = get_config(PetConfig).get(pet.prototypeID)
    if not pet:
        return
    if pet.cls in task.arg2 or not task.arg2:
        return _set_plan(player, task, today)


@register_task(TaskCond.Money)
def on_money(task, today, player, value):
    return _set_plan(player, task, today, value=value)


@register_task(TaskCond.RebornCount)
def on_retry_fb(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.LotteryCount)
def on_lottery(task, today, player, value, is_gold):
    if task.arg2 and task.arg2[0] is not 0:
        type = task.arg2[0]
        if type == 1:
            if is_gold:
                return
        elif type == 2:
            if not is_gold:
                return
    return _set_plan(player, task, today, value=value)


@register_task(TaskCond.RankCount)
def on_rank_count(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.BestPetCount)
def on_best_pet(task, today, player, pets):
    petInfos = get_config(PetConfig)
    count = 0
    for pet in pets:
        petInfo = petInfos.get(pet.prototypeID)
        # if petInfo and petInfo.dtype == 0 and pet.rarity in task.arg2:
        if petInfo.rarity in task.arg2 or not task.arg2:
            count += 1
    if count:
        return _set_plan(player, task, today, value=count)


@register_task(TaskCond.RankSeasonCount)
def on_rank_season_count(task, today, player):
    return _set_plan(
        player, task, today, value=player.pvpseasoncount, replace=True)


@register_task(TaskCond.RefreshShopCount)
def on_refresh_shop(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.Signup)
def on_sign_up(task, today, player):
    result = _set_plan(player, task, today)
    if result:
        from reward.manager import open_reward, RewardType
        reward = open_reward(RewardType.Task, task.drop)
        reward.apply(player)
        player.taskrewards.remove(task.ID)
    return False  # 防止递归检查下一个任务


@register_task(TaskCond.GoldenFinger)
def on_golden_finger(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.MonthlyCard30)
def on_monthly_card(task, today, player):
    if player.monthly_card_30:
        player.monthly_card_30 -= 1
        return _set_plan(player, task, today)


@register_task(TaskCond.ShoppingCount)
def on_shopping(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.RankWinCount)
def on_rank_win_count(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.VipLevel)
def on_vip_level(task, today, player):
    if player.vip in task.arg2:
        return _set_plan(player, task, today)


@register_task(TaskCond.LotteryCount10)
def on_lottery10(task, today, player):
    return _set_plan(player, task, today)


#  def on_login(player):
#      today = datedate.today()
#      tasks = get_undone_tasks_by_cond(player, TaskCond.Login, today)
#      for taskID in sorted(filter_unstart_tasks(tasks))[::-1]:
#          set_plan(player, taskID, today)
#          break  # 只完成最后一个
#      player.save()
#      player.sync()


@register_task(TaskCond.Login)
def on_login(task, today, player):
    _set_plan(player, task, today)


@register_task(TaskCond.RobCount)
def on_rob_count(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.Rob)
def on_rob(task, today, player, value, type):
    if type in task.arg2:
        return _set_plan(player, task, today, value=value)


@register_task(TaskCond.Collect)
def on_collect(task, today, player, value, type):
    if type in task.arg2:
        return _set_plan(player, task, today, value=value)


@register_task(TaskCond.UproarCount)
def on_uproar_count(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.UproarReset)
def on_uproar_reset(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.LootComposeZuoqi)
def on_loot_compose_zuoqi(task, today, player, quality):
    if quality in task.arg2:
        return _set_plan(player, task, today)


@register_task(TaskCond.LootComposeFabao)
def on_loot_compose_fabao(task, today, player, quality):
    if quality in task.arg2:
        return _set_plan(player, task, today)


@register_task(TaskCond.LootCount)
def on_loot_count(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.UproarSerialCount)
def on_uproar_serial_count(task, today, player):
    count = len(player. uproar_targets_done)
    if count in task.arg2:
        return _set_plan(player, task, today)


@register_task(TaskCond.TapCount)
def on_tap_count(task, today, player, count):
    return _set_plan(player, task, today, value=count)


@register_task(TaskCond.TreasureCount)
def on_treasure_count(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.DlcFbCount)
def on_end_dlc_fb(task, today, player, fbID, count=1):
    from config.configs import get_config, DlcFbInfoConfig
    dlc_fb = get_config(DlcFbInfoConfig).get(fbID)
    dlc_task = get_config(DlcTaskConfig).get(task.ID)
    if dlc_fb.dlcID != dlc_task.dlcID:
        return
    if dlc_fb and (not task.arg2 or dlc_fb.type in task.arg2):
        return _set_plan(player, task, today, value=count)


@register_task(TaskCond.DlcScoreCount)
def on_dlc_score(task, today, player):
    from config.configs import get_config
    from config.configs import DlcConfig
    from config.configs import DlcTaskConfig
    from config.configs import DlcFbInfoConfig
    from config.configs import FbInfoBySceneConfig
    from scene.manager import get_fb_score
    dlc_task = get_config(DlcTaskConfig).get(task.ID)
    if not dlc_task:
        return
    dlc = get_config(DlcConfig).get(dlc_task.dlcID)
    if not dlc:
        return
    score = 0
    scene_group = get_config(FbInfoBySceneConfig)
    configs = get_config(DlcFbInfoConfig)
    for sceneID in dlc.scenes:
        fbs = scene_group.get(sceneID, [])
        for fb in fbs:
            dlc_fb = configs.get(fb.ID)
            if not dlc_fb or (task.arg2 and dlc_fb.type not in task.arg2):
                continue
            score += get_fb_score(player, fb.ID)
    return _set_plan(player, task, today, value=score, replace=True)


@register_task(TaskCond.CollectPet1)
def on_collect_pet1(task, today, player, *pets):
    pet_configs = get_config(PetConfig)
    score = 0
    if task.arg2:
        for pet in pets:
            # 40 表示4星0阶，41 表示4星1阶
            info = pet_configs.get(pet.prototypeID)
            if not info:
                continue
            for arg in task.arg2:
                rarity = arg // 10
                step = arg % 10
                if info.rarity >= rarity and info.step >= step:
                    score += 1
    else:
        score += 1
    return _set_plan(player, task, today, value=score, replace=True)


@register_task(TaskCond.CollectPet2)
def on_collect_pet2(task, today, player, *pets):
    pet_configs = get_config(PetConfig)
    score = 0
    for pet in pets:
        info = pet_configs.get(pet.prototypeID)
        if not info:
            continue
        if task.arg2:
            if not info.cls >= task.arg2:
                score += 1
        else:
            score += 1
    if score:
        return _set_plan(player, task, today, value=score)


@register_task(TaskCond.CollectEquip)
def on_collect_equip(task, today, player, equips):
    equip_configs = get_config(NewEquipConfig)
    score = 0
    for equip in equips:
        info = equip_configs.get(equip.prototypeID)
        if info.units_same:
            score += 1
    if score:
        return _set_plan(player, task, today, value=score)


@register_task(TaskCond.AdvanceEquip)
def on_advance_equip(task, today, player, equip):
    if equip.step >= task.arg2 or not task.arg2:
        return _set_plan(player, task, today, value=1)


@register_task(TaskCond.PetFusionCount)
def on_pet_fusion_count(task, today, player, pet):
    pet = get_config(PetConfig).get(pet.prototypeID)
    if pet.cls in task.arg2 or not task.arg2:
        return _set_plan(player, task, today, value=1)


@register_task(TaskCond.SparCount)
def on_spar_count(task, today, player, count):
    return _set_plan(player, task, today, value=count)


@register_task(TaskCond.Jiutian)
def on_jiutian(task, today, player, score):
    if score:
        return _set_plan(player, task, today, value=score)


@register_task(TaskCond.DongtianFudiMoney)
def on_dongtian_fudi_money(task, today, player, score):
    if score:
        return _set_plan(player, task, today, value=score)


@register_task(TaskCond.DongtianFudiSoul)
def on_dongtian_fudi_soul(task, today, player, score):
    if score:
        return _set_plan(player, task, today, value=score)


@register_task(TaskCond.Skillup)
def on_skillup(task, today, player, score):
    if score:
        return _set_plan(player, task, today, value=score)


@register_task(TaskCond.Gold)
def on_gold(task, today, player, score):
    if score:
        return _set_plan(player, task, today, value=score)


@register_task(TaskCond.Soul)
def on_soul(task, today, player, score):
    if score:
        return _set_plan(player, task, today, value=score)


@register_task(TaskCond.Point)
def on_point(task, today, player, score):
    if score:
        return _set_plan(player, task, today, value=score)


@register_task(TaskCond.MazeCount)
def on_maze_count(task, today, player, count):
    if count:
        return _set_plan(player, task, today, value=count)
    get_plan(task.ID, today, player)


@register_task(TaskCond.SwapRank)
def on_swap_rank(task, today, player, swaprank):
    lo, hi = task.arg2
    if lo > hi:
        lo, hi = hi, lo
    if swaprank >= lo and swaprank <= hi:
        return _set_plan(player, task, today, value=1, replace=True)


@register_task(TaskCond.FriendsCount)
def on_friends_count(task, today, player):
    count = len(player.friendset)
    return _set_plan(player, task, today, value=count, replace=True)


@register_task(TaskCond.FriendfbFirst)
def on_friendfb_first(task, today, player, fbID):
    if fbID in task.arg2 or not task.arg2:
        return _set_plan(player, task, today, value=1, replace=True)


@register_task(TaskCond.FriendfbCount)
def on_friendfb_count(task, today, player, fbID):
    if fbID in task.arg2 or not task.arg2:
        return _set_plan(player, task, today, value=1)


@register_task(TaskCond.SwapRankCount)
def on_swap_rank_count(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.SwapRankWinCount)
def on_swap_rank_win_count(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.DailyPVPCount)
def on_dailypvp_count(task, today, player, value):
    return _set_plan(player, task, today, value=value, replace=True)


@register_task(TaskCond.BreakPet)
def on_break_pet(task, today, player, pet):
    if task.arg2 and pet.breaklevel not in task.args2:
        return
    return _set_plan(player, task, today)


@register_task(TaskCond.StrengthenEquipCount)
def on_strengthen_equip(task, today, player, equip):
    if task.arg2 and equip.level not in task.args2:
        return
    return _set_plan(player, task, today)


@register_task(TaskCond.PlayerEquipStrengthenCount)
def on_strengthen_player_equip(task, today, player, value):
    return _set_plan(player, task, today, value=value)


@register_task(TaskCond.EnhantEquipCount)
def on_enhant_equip(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.AmbitionCount)
def on_ambition(task, today, player):
    return _set_plan(player, task, today)


@register_task(TaskCond.Maxpower)
def on_maxpower(task, today, player, maxpower):
    return _set_plan(player, task, today, value=maxpower, replace=True)


@register_task(TaskCond.FactionLevel)
def on_faction_level(task, today, player, level):
    return _set_plan(player, task, today, value=level, replace=True)


def patch_noob_tasks(p):
    groups = get_config(TaskByGroupConfig)
    configs = get_config(TaskConfig)
    for group in get_sorted_noob_group():
        tasks = groups.get(group)
        flag = False
        rest = []
        for task in tasks:
            task = configs.get(task.ID)
            if task.ID in p.taskrewards:
                flag = True
            elif p.tasks.get(task.ID, {}).get("plan", 0) < task.goal:
                flag = True
            else:
                rest.append(task)
        if flag and rest:
            for each in rest:
                if each.cond == TaskCond.Levelup:
                    if p.tasks.get(each.ID, {}).get("plan", 0) >= each.goal:
                        p.taskrewards.add(each.ID)
                else:
                    for task in tasks:
                        try:
                            p.taskrewards.remove(task.ID)
                        except KeyError:
                            pass
    p.save()


@proxy.rpc
def sync_on_task_change(entityID, type, *args, **kwargs):
    func = __tasks[type]
    p = g_entityManager.get_player(entityID)
    return func(p, *args, **kwargs)


def trigger_seven_task(p):
    if not p.task_seven_cd:
        p.task_seven_cd = time.mktime(
            (datetime.now() + timedelta(days=7)).date().timetuple())
