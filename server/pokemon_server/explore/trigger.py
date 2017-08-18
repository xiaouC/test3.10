# coding:utf-8
import logging
logger = logging.getLogger("trigger")

from yy.utils import guess
from yy.utils import weighted_random2

from config.configs import get_config
from config.configs import TriggerEventConfig
from config.configs import TriggerAfterFbConfig

from .constants import EventType


def check_trigger_event_type(p, event_type):
    if not p.trigger_event:
        return False
    configs = get_config(TriggerEventConfig)
    config = configs[p.trigger_event]
    return event_type == config.event_type


def check_trigger_event_param(p, event_param):
    if not p.trigger_event:
        return False
    configs = get_config(TriggerEventConfig)
    config = configs[p.trigger_event]
    return event_param == config.event_param


def trigger_event(p):
    if p.trigger_packs_flag:
        return 0
    prob = 0
    triggers = get_config(TriggerAfterFbConfig)
    for tg in triggers:
        if p.trigger_event_sp >= tg.sp:
            prob = tg.trigger_event_prob
        else:
            break
    if not guess(prob):
        return 0
    configs = {
        k: v for k, v in get_config(TriggerEventConfig).items()
        if p.level >= v.open_level}
    if not configs:
        return 0
    logger.debug("trigger_event_sp: %r", p.trigger_event_sp)
    logger.debug("trigger event prob: %r", prob)
    ID = weighted_random2([[k, v.prob] for k, v in configs.items()])
    config = configs[ID]
    logger.debug("%r", config)
    if config.event_type == EventType.Fb:
        logger.debug("EventType.Fb")
        if p.is_pets_full():
            logger.debug("pet full")
            return 0
    elif config.event_type == EventType.Chest:
        logger.debug("EventType.Chest")
    elif config.event_type == EventType.Chests:
        logger.debug("EventType.Chests")
        p.trigger_chests.clear()
    elif config.event_type == EventType.Store:
        logger.debug("EventType.Store")
    elif config.event_type == EventType.Task:
        logger.debug("EventType.Task")
        taskID = config.event_param
        if taskID in p.trigger_tasks:
            tasks = {}
            for k, v in configs.items():
                if v.event_type == EventType.Task:
                    tasks[k, v.event_param] = v.prob
            while tasks:
                ID, taskID = weighted_random2(tasks.items())
                if taskID not in p.trigger_tasks:
                    break
                del tasks[ID, taskID]
        if taskID in p.trigger_tasks:  # 已经存在的任务，那么就不触发了
            return 0
        p.trigger_tasks.add(taskID)
    p.trigger_event_sp = 0
    p.trigger_event = ID
    p.save()
    p.sync()
    return config.event_type
