# coding:utf-8
import time
import cPickle
import operator

from collections import deque
from state.base import StateObject

from reward.constants import RewardType
from reward.manager import apply_reward
from yy.utils import choice_one

import settings
# from datetime import date as datedate
# from datetime import timedelta
# from yy.utils import choice_one
from yy.utils import convert_list_to_dict
from pvp.manager import get_opponent_detail
# from pvp.manager import get_zombie
from player.model import PlayerDailyRankRanking
from player.model import Player

from config.configs import get_cons_value
from config.configs import DailyWinConfig
from config.configs import DailyLoseConfig
from config.configs import get_config
# from config.configs import get_config
# from config.configs import DailyRuleConfig
# from config.configs import DailyRewardConfig

# from reward.manager import parse_reward
# from mail.manager import get_mail, send_mail
from reward.manager import build_reward
from reward.manager import combine_reward
from reward.manager import open_reward

from gm.proxy import proxy
from entity.manager import g_entityManager
from lineup.constants import LineupType
# from common.utils import copy
from yy.db.redisscripts import load_redis_script
from chat.red import g_redManager
from chat.red import RedType


MAX_HIST_LEN = 10


@load_redis_script(pool=settings.REDISES["index"])
def update_daily_rank(ranking, entityID, score):
    """
    local key = KEYS[1]
    local member = ARGV[1]
    local score = ARGV[2]
    redis.call("ZADD", key, score, member)
    local count = redis.call("ZCOUNT", key, score, "+inf")
    return count
    """
    return (ranking.key,), (entityID, score)


index_pool = settings.REDISES["index"]

DailyResetFlag = "DAILY_RESET_FLAG{%d}{%d}" % (
    settings.SESSION["ID"], settings.REGION["ID"])

DailyTopThreeBackup = "DAILY_TOP_THREE_BACKUP{%d}{%d}" % (
    settings.SESSION["ID"], settings.REGION["ID"])


class DailyManager(StateObject):
    loop = None
    lives = deque([], 50)
    top_lives = deque([], 10)
    pool = settings.REDISES["entity"]
    top_three = []

    def __init__(self):
        self.reload_top_three()

    def reload_top_three(self):
        self.top_three = []
        rankers = convert_list_to_dict(index_pool.execute(
            "HGETALL", DailyTopThreeBackup))
        result = []
        for k, v in sorted(rankers.items()):
            result.append(cPickle.loads(v))
        self.top_three = result
        return self.top_three

    def get_backup_top_three(self):
        return self.top_three

    def get_lives(self, count=10):
        result = []
        index = 0
        break_flag1 = False
        break_flag2 = False
        while True:
            if len(self.top_lives) > index:
                result.append(self.top_lives[index])
            else:
                break_flag1 = True
            if len(self.lives) > index:
                result.append(self.lives[index])
            else:
                break_flag2 = True
            if len(result) >= count:
                break
            if break_flag1 and break_flag2:
                break
            index += 2
        return result

    def get_panel(self, p, rsp):
        lives = self.get_lives(count=10)
        rsp.lives = lives
        rankers = self.get_rankers(count=10)
        rsp.ranks = rankers
        rsp.rewards = build_reward(p.daily_rewards)
        rsp.reds = g_redManager.get_red_messages()
        # 检查战斗期间内是否被已死亡
        rsp.registers = PlayerDailyRankRanking.count()
        p.clear_daily_dead()
        if p.daily_dead and p.daily_count:
            now = int(time.time())
            p.daily_dead_cd = now + get_cons_value("DailyDeadCD")
            self.pool.execute("DEL", "daily_dead_p{%d}" % p.entityID)
            p.clear_daily_dead()
            p.save()
            p.sync()
        return rsp

    def get_rankers(self, count=50):
        from campaign.manager import g_campaignManager
        opened = g_campaignManager.dailypvp_campaign.is_open()
        if opened:
            rankers = convert_list_to_dict(
                PlayerDailyRankRanking.get_range_by_score(
                    "-inf", "+inf", count=count, withscores=True))
            result = []
            sorted_rankers = sorted(
                rankers.items(),
                key=operator.itemgetter(1),
                reverse=True)
            for i, daily_max_win_count in sorted_rankers:
                detail = get_opponent_detail(i)
                detail["daily_max_win_count"] = daily_max_win_count
                result.append(detail)
        else:
            result = self.get_backup_top_three()
        return result

    def register(self, p):
        PlayerDailyRankRanking.update_score(
            p.entityID, p.daily_max_win_count)

    def get_target(self, p):
        if p.daily_cache_targetID:
            targetID = p.daily_cache_targetID
        else:
            # 下区间 = int(500/(2*最高连胜数+10))
            # 上区间 = int(最高连胜数/2)
            top = int(p.daily_max_win_count / 2) + 2
            bot = int(500/(2 * p.daily_max_win_count + 10))
            need = bot + top
            targets = map(
                int, PlayerDailyRankRanking.get_range_by_score(
                    p.daily_rank, "+inf", count=top))
            need = need - len(targets)
            targets.extend(map(
                int, PlayerDailyRankRanking.get_range_by_score(
                    "-inf", max(p.daily_rank - 1, 0), count=need)))
            try:
                targets = list(set(targets))
                targets.remove(p.entityID)
            except ValueError:
                pass
            if not targets:
                return None
            targetID = choice_one(targets)
            p.daily_cache_targetID = targetID
            p.save()
        detail = get_opponent_detail(targetID, type=LineupType.Daily)
        if not detail.get("pets"):
            detail = get_opponent_detail(targetID)
        return detail

    def battle(self, p, targetID, fight, raw, rsp):
        target_win_count = 0  # 对手连胜次数
        max_win_count = 0
        history = None  # 战斗记录
        shutdown = False
        self_message = ""
        full_message = ""
        horn = False
        red_message = ""
        red_count = 0
        self_shutdown_message = ""
        full_shutdown_message = ""
        peer_shutdown_message = ""
        count = 0
        rsp.before_daily_win_count = p.daily_win_count
        if fight.fightResult:  # 胜利
            # 终结对手连胜
            target_win_count = int(self.pool.execute(
                "GETSET", "daily_win_count_p{%d}" % targetID, 0) or 0)
            self.pool.execute("SET", "daily_dead_p{%d}" % targetID, 1)
            # 添加自己连胜
            daily_win_count = int(self.pool.execute(
                "INCRBY", "daily_win_count_p{%d}" % p.entityID, 1) or 0)
            p.clear_daily_win_count()
            # 更新最大连胜次数
            if p.daily_win_count > p.daily_max_win_count:
                p.daily_max_win_count = p.daily_win_count
                count = update_daily_rank(
                    PlayerDailyRankRanking, p.entityID, p.daily_max_win_count)
                # PlayerDailyRankRanking.update_score(
                #     p.entityID, p.daily_max_win_count)
                # 连胜任务
                from task.manager import on_dailypvp_count
                on_dailypvp_count(p, p.daily_max_win_count)
                # 取全服最大次数
                top = PlayerDailyRankRanking.get_range_by_score(
                    "-inf", "+inf", withscores=True, count=1)
                if top:
                    max_win_count = top[1]
                rsp.max_win_count = max_win_count
            daily_win_config = get_config(DailyWinConfig).get(
                p.daily_win_count)
            if not daily_win_config and \
                    p.daily_win_count > max(get_config(DailyWinConfig)):
                daily_win_config = get_config(
                    DailyWinConfig)[max(get_config(DailyWinConfig))]
            if daily_win_config:
                if not daily_win_config.multiple or (
                        daily_win_config.multiple and count == 1):
                    self_message = daily_win_config.single_desc
                    full_message = daily_win_config.all_desc
                    horn = daily_win_config.horn
                    if daily_win_config.red_paper:
                        red_message = daily_win_config.red_paper_desc
                        red_count = daily_win_config.red_paper_count
                        red_drop = daily_win_config.red_paper
            daily_lose_config = get_config(DailyLoseConfig).get(
                target_win_count)
            if not daily_lose_config and \
                    target_win_count > max(get_config(DailyLoseConfig)):
                daily_lose_config = get_config(
                    DailyLoseConfig)[max(get_config(DailyLoseConfig))]
            if daily_lose_config:
                self_shutdown_message = daily_lose_config.single_win_desc
                peer_shutdown_message = daily_lose_config.single_lose_desc
                full_shutdown_message = daily_lose_config.all_desc
            # 增加胜利次数
            p.daily_kill_count += 1
            # 奖励加成系数
            multi = min(40, 2 * daily_win_count) + min(
                80, target_win_count * 4)
            shutdown = target_win_count > 2
            history = {
                "active": False, "name": p.name,
                "win": not fight.fightResult,
                "faction_name": p.faction_name,
                "daily_win_count": p.daily_win_count,
                "fight": raw.encode("base64"),
                "prototypeID": p.prototypeID,
                "borderID": p.borderID,
                "shutdown": shutdown}
            for each in fight.player_team:
                pet = p.pets[each.entityID]
                if each.restHP == 0:
                    pet.daily_dead = True
                else:
                    pet.daily_restHP = each.restHP
                pet.save()
                pet.sync()
        else:
            if not p.daily_rank:
                PlayerDailyRankRanking.update_score(
                    p.entityID, p.daily_max_win_count)
            # 自己连胜被终结
            daily_win_count = int(self.pool.execute(
                "GETSET", "daily_win_count_p{%d}" % p.entityID, 0) or 0)
            # 死亡
            self.pool.execute("SET", "daily_dead_p{%d}" % p.entityID, 1)
            p.clear_daily_win_count()
            # 奖励加成系数
            multi = 0
            daily_lose_config = get_config(DailyLoseConfig).get(
                daily_win_count)
            if not daily_lose_config and \
                    daily_win_count > max(get_config(DailyLoseConfig)):
                daily_lose_config = get_config(
                    DailyLoseConfig)[max(get_config(DailyLoseConfig))]
            if daily_lose_config:
                self_shutdown_message = daily_lose_config.single_lose_desc
                peer_shutdown_message = daily_lose_config.single_win_desc
                full_shutdown_message = daily_lose_config.all_desc
        # 取对手数据
        data = g_entityManager.get_players_info(
            [targetID], [
                "entityID", "name", "daily_win_count",
                "faction_name", "prototypeID", "borderID"])[0]
        # 终结连胜
        shutdown = target_win_count > 2
        data.update({
            "active": True, "shutdown": shutdown,
            "win": fight.fightResult,
            "fight": raw.encode("base64")
        })
        # 自己的战斗记录
        p.daily_histories.appendleft(data)
        p.daily_histories.ltrim(0, MAX_HIST_LEN - 1)
        # 更新排名
        p.daily_rank = PlayerDailyRankRanking.get_rank(p.entityID)
        rewards = {}
        reward = open_reward(
            RewardType.DailyPVP, get_cons_value("DailyPVPDrop"))
        rewards = reward.apply_after()
        # 奖励加成
        if multi:
            for k, v in rewards.items():
                if isinstance(v, int) and k != 'exp':
                    rewards[k] = int(v * (100 + multi) / float(100))
        # 记录累计奖励
        apply_reward(p, rewards, type=RewardType.DailyPVP)
        combine_reward(rewards, [], data=p.daily_rewards)
        p.daily_rewards = dict(p.daily_rewards)
        p.daily_count += 1
        p.daily_cache_targetID = 0
        p.save()
        p.sync()
        # 添加直播
        self.add_live({
            "self_name": p.name,
            "self_prototypeID": p.prototypeID,
            "self_borderID": p.borderID,
            "peer_name": data["name"],
            "peer_prototypeID": data["prototypeID"],
            "peer_borderID": data["borderID"],
            "is_win": fight.fightResult,
        }, top=p.daily_rank and p.daily_rank <= 5)
        rsp.daily_win_count = p.daily_win_count
        rsp.rewards = build_reward(rewards)
        if self_message:
            self_message = self_message.format(data["name"], p.daily_win_count)
            g_redManager.send_red_message(
                p, self_message, to_self=True, type=RedType.Normal)
        if full_message:
            full_message = full_message.format(
                p.name, data["name"], p.daily_win_count)
            _type = RedType.Horn if horn else RedType.Normal
            g_redManager.send_red_message(
                p, full_message, type=_type)
        if red_count and red_message:
            if daily_win_count == 1:
                red_message = red_message.format(
                    p.name, red_count)
            else:
                red_message = red_message.format(
                    p.name, daily_win_count, red_count)
            g_redManager.send_red_message(
                p, red_message, red_drop=red_drop,
                red_count=red_count, type=RedType.Red)
        if full_shutdown_message:
            if fight.fightResult:
                full_shutdown_message = full_shutdown_message.format(
                    p.name, data["name"], target_win_count)
            else:
                full_shutdown_message = full_shutdown_message.format(
                    data["name"], p.name, daily_win_count)
            _type = RedType.Horn if horn else RedType.Normal
            g_redManager.send_red_message(
                p, full_shutdown_message, type=_type)
        if fight.fightResult:
            if self_shutdown_message:
                self_shutdown_message = self_shutdown_message.format(
                    data["name"], target_win_count)
                g_redManager.send_red_message(
                    p.entityID, self_shutdown_message,
                    to_self=True, type=RedType.Normal)
            if peer_shutdown_message:
                peer_shutdown_message = peer_shutdown_message.format(
                    p.name, target_win_count)
                g_redManager.send_red_message(
                    data["entityID"], peer_shutdown_message,
                    to_self=True, type=RedType.Normal)
        else:
            if self_shutdown_message:
                self_shutdown_message = self_shutdown_message.format(
                    data["name"], daily_win_count)
                g_redManager.send_red_message(
                    p.entityID, self_shutdown_message,
                    to_self=True, type=RedType.Normal)
            if peer_shutdown_message:
                peer_shutdown_message = peer_shutdown_message.format(
                    p.name, daily_win_count)
                g_redManager.send_red_message(
                    data["entityID"], peer_shutdown_message,
                    to_self=True, type=RedType.Normal)
        proxy.sync_daily_rank(targetID, history)
        return rewards

    def add_live(self, lives, top=False):
        if top:
            self.top_lives.appendleft(lives)
        else:
            self.lives.appendleft(lives)

    def reborn(self, p):
        lineup = p.lineups.get(LineupType.Daily, [])
        for each in lineup:
            pet = p.pets.get(each)
            if pet:
                pet.daily_dead = False
                pet.daily_restHP = 0
                pet.save()
                pet.sync()

    def backup(self):
        rankers = convert_list_to_dict(
            PlayerDailyRankRanking.get_range_by_score(
                "-inf", "+inf", count=3, withscores=True))
        result = []
        sorted_rankers = sorted(
            rankers.items(),
            key=operator.itemgetter(1),
            reverse=True)
        index_pool.execute("DEL", DailyTopThreeBackup)
        for rank, (i, daily_max_win_count) in enumerate(sorted_rankers, 1):
            detail = get_opponent_detail(i)
            detail["daily_max_win_count"] = daily_max_win_count
            result.append(detail)
            index_pool.execute(
                "HSET", DailyTopThreeBackup, rank, cPickle.dumps(detail))
        self.reload_top_three()
        return result

    def cleanup(self):
        from campaign.manager import g_campaignManager
        now = int(time.time())
        start = g_campaignManager.dailypvp_campaign.get_start_time()
        final = g_campaignManager.dailypvp_campaign.get_final_time()
        reset = int(float(index_pool.execute(
            "GETSET", DailyResetFlag, now) or 0))
        if reset < start or reset > final:
            self.backup()
            PlayerDailyRankRanking.clear_raw()  # make sure reset  # NOTE
            g_redManager.clean_red()
            self.reset()
            self.lives.clear()
            self.top_lives.clear()
        else:
            index_pool.execute("SET", DailyResetFlag, reset)

    def reset(self, p=None):
        from campaign.manager import g_campaignManager
        if p:
            ps = [p]
        else:
            ps = g_entityManager.players.values()
        # now = int(time.time())
        for p in ps:
            start = g_campaignManager.dailypvp_campaign.get_start_time()
            final = g_campaignManager.dailypvp_campaign.get_final_time()
            if p.daily_reset_time < start or p.daily_reset_time > final:
                p.daily_end_panel = {
                    "daily_rank": p.daily_rank,
                    "daily_kill_count": p.daily_kill_count,
                    "daily_max_win_count": p.daily_max_win_count,
                    "rewards":  build_reward(p.daily_rewards, cls=dict),
                }
                p.daily_cache_targetID = 0
                self.pool.execute("del", "daily_win_count_p{%d}" % p.entityID)
                p.clear_daily_win_count()
                # {{ 鼓舞及复活
                p.daily_dead_cd = 0
                self.pool.execute("del", "daily_dead_p{%d}" % p.entityID)
                p.clear_daily_dead()
                p.daily_inspire_used_count = 0
                # }}
                p.daily_histories.clear()
                p.daily_rewards.clear()
                p.daily_history_flag = False
                p.daily_max_win_count = 0
                p.daily_kill_count = 0
                p.daily_count = 0
                p.daily_rank = 0
                p.daily_registered = False
                p.daily_reset_time = start
                p.save()
                p.sync()


@proxy.rpc
def sync_daily_rank_offline(entityID, history=None):
    p = Player.simple_load(entityID, [
        "daily_histories", "daily_history_flag"])
    p.daily_histories.load()
    if p:
        if history:
            p.daily_histories.appendleft(history)
            p.daily_histories.ltrim(0, MAX_HIST_LEN - 1)
            p.daily_history_flag = True
        p.save()


@proxy.rpc(failure=sync_daily_rank_offline)
def sync_daily_rank(entityID, history=None):
    p = g_entityManager.get_player(entityID)
    if p:
        if history:
            p.daily_histories.appendleft(history)
            p.daily_histories.ltrim(0, MAX_HIST_LEN - 1)
            p.daily_history_flag = True
        p.clear_daily_win_count()
        p.save()
        p.sync()


g_dailyManager = DailyManager()
