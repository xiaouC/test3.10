# coding:utf-8
import settings
from yy.utils import weighted_random2
from reward.manager import combine_reward
from config.configs import get_config
from config.configs import VisitIncrByGroupConfig
from config.configs import VisitConfig
from config.configs import VisitRewardByGroupConfig
from campaign.manager import g_campaignManager
from reward.manager import parse_reward
from mail.manager import get_mail
from mail.manager import send_mail
from entity.manager import g_entityManager
from reward.constants import RewardType
from reward.manager import open_reward


VISIT_INCR_FLAG = "VISIT_INCR_FLAG{%d}{%d}" % (
    settings.SESSION["ID"], settings.REGION["ID"])

pool = settings.REDISES["index"]


def incr_visit_flag(count=1):
    return (pool.execute("INCRBY", VISIT_INCR_FLAG, count) or 0)


def visit(p, count):
    gain = {}
    cost = {}
    configs = get_config(VisitConfig)
    incr_groups = get_config(VisitIncrByGroupConfig)
    choices = []
    campaign = g_campaignManager.visit_campaign
    campaign_opened = campaign.is_open()
    luck = {}
    for i in range(count):
        weighted_samples = []
        rewards = None
        for k, config in configs.items():
            if config.flag and campaign_opened:
                current = campaign.get_current()
                incr_configs = incr_groups.get(current.reward_group)
                VISIT_COUNT = incr_visit_flag()
                for incr_config in incr_configs:
                    if VISIT_COUNT % incr_config.count == 0:
                        choice = incr_config
                        reward = open_reward(RewardType.Visit, choice.drop)
                        rewards = reward.apply_after()
                        combine_reward(rewards, {}, data=luck)
                        break
                if rewards:
                    break
            else:
                weighted_samples.append([config, config.prob])
        if not rewards:
            choice = weighted_random2(weighted_samples)
            rewards = choice.rewards
            choices.append(choice.id)
        gain_pious = {"pious": 1}
        gain = combine_reward(rewards, gain_pious, data=gain)
    if p.visit_free_rest_count < count:
        count = count - p.visit_free_rest_count
        if p.dream:
            cost["dream"] = min(p.dream, count)
            count -= cost["dream"]
        if count:
            cost["gold"] = p.visit_cost * count
    return gain, cost, choices, luck


def give_visit_reward(p=None):
    if p:
        ps = [p]
    else:
        ps = g_entityManager.players.values()
    # 有积分，发奖励
    campaign = g_campaignManager.visit_campaign
    campaign_opened = campaign.is_open()
    start, final = campaign.get_current_time()
    for p in ps:
        if not p.pious or not p.visit_group:
            continue
        configs = get_config(VisitRewardByGroupConfig).get(p.visit_group, [])
        if campaign_opened:
            if p.visit_time >= start and p.visit_time < final:
                continue
        for config in configs:
            if p.pious >= config.pious:
                rewards = parse_reward(config.rewards)
                title, content, ID = get_mail("Visit")
                content = content.format(p.pious)
                send_mail(
                    p.entityID, title, content,
                    addition=rewards, configID=ID)
                p.pious_backup = p.pious
                p.pious = 0
                p.save()
                p.sync()
                break
