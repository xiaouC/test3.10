# coding:utf-8
import time
import json
import random
import msgpack
import logging
logger = logging.getLogger("city")
import settings
# from credis import RedisReplyError
from yy.utils import convert_list_to_dict
from yy.ranking.manager import NaturalRankingWithJoinOrder
from yy.message.header import success_msg
from config.configs import CityDungeonMonsterGroupConfig
from config.configs import CityDungeonRewardConfig
from config.configs import get_config
from config.configs import get_cons_value
from config.configs import CityEventConfig
from config.configs import CityTreasureConfig
from config.configs import CityDungeonMessageConfig
from config.configs import CityContendDefendMessageConfig
from config.configs import CityContendAttackMessageConfig
from itertools import count as icount

from reward.manager import parse_reward
from reward.manager import apply_reward
from reward.manager import build_reward
from reward.manager import combine_reward
from reward.manager import build_reward_msg
from reward.manager import open_reward
from reward.constants import RewardType
from faction.model import Faction
from player.model import Player
from player.manager import g_playerManager
from entity.manager import g_entityManager
from mail.manager import get_mail
from mail.manager import send_mail
from gm.proxy import proxy
from pvp.manager import get_opponent_detail
from lineup.manager import LineupType
from chat.red import g_redManager
from chat.red import RedModuleType
from chat.red import RedType
from protocol import poem_pb
from protocol import poem_pb as msgid
from faction.model import FactionRankRanking
from player.model import PlayerLevelRanking
from collections import OrderedDict


class CityContendEventType:
    Drop = 1
    Enemy = 2
    End = 3

entity_pool = settings.REDISES["entity"]
index_pool = settings.REDISES["index"]

# 推图重置时间记录
CityDungeonReset = "CITY_DUNGEON_RESET{%d}{%d}" % (
    settings.SESSION["ID"], settings.REGION["ID"])

# 争夺重置时间记录
CityContendReset = "CITY_CONTEND_RESET{%d}{%d}" % (
    settings.SESSION["ID"], settings.REGION["ID"])

# 推图击杀排行榜（公会）
CityDungeonKillRanking = NaturalRankingWithJoinOrder(
    "CITY_DUNGEON_KILL_RANK{%d}{%d}" % (
        settings.SESSION["ID"], settings.REGION["ID"]), index_pool)

# 推图攻破排行榜（公会）
CityDungeonSumsRanking = NaturalRankingWithJoinOrder(
    "CITY_DUNGEON_SUMS_RANK{%d}{%d}" % (
        settings.SESSION["ID"], settings.REGION["ID"]), index_pool)

# 推图击杀排行榜（公会）备份
CityDungeonKillBackupRanking = NaturalRankingWithJoinOrder(
    "CITY_DUNGEON_KILL_RANK{%d}{%d}{BACKUP}" % (
        settings.SESSION["ID"], settings.REGION["ID"]), index_pool)

# 推图击杀排行榜（个人）
CityDungeonSelfRanking = NaturalRankingWithJoinOrder(
    "CITY_DUNGEON_SELF_RANK{%d}{%d}" % (
        settings.SESSION["ID"], settings.REGION["ID"]), index_pool)

# 推图击杀排行榜（个人）备份
CityDungeonSelfBackupRanking = NaturalRankingWithJoinOrder(
    "CITY_DUNGEON_SELF_RANK{%d}{%d}{BACKUP}" % (
        settings.SESSION["ID"], settings.REGION["ID"]), index_pool)

# 推图第一公会数据
CityDungeonTop = "CITY_DUNGEON_TOP{%d}{%d}" % (
    settings.SESSION["ID"], settings.REGION["ID"])

# 争夺攻击方排名（公会）
CityContendFactionRanking = NaturalRankingWithJoinOrder(
    "CITY_DUNGEON_FACTION_ATTACK_RANK{%d}{%d}" % (
        settings.SESSION["ID"], settings.REGION["ID"]), index_pool)

# 争夺攻击方排名（个人）
CityContendAttackRanking = NaturalRankingWithJoinOrder(
    "CITY_DUNGEON_ATTACK_RANK{%d}{%d}" % (
        settings.SESSION["ID"], settings.REGION["ID"]), index_pool)

# 争夺防守方排名（个人）
CityContendDefendRanking = NaturalRankingWithJoinOrder(
    "CITY_DUNGEON_DEFEND_RANK{%d}{%d}" % (
        settings.SESSION["ID"], settings.REGION["ID"]), index_pool)


class CityDungeon(object):

    def get_mg_pool_key(self, factionID):
        assert factionID
        return "CITY_DUNGEON_MG_POOL{%d}" % factionID

    def get_mg_kill_key(self, factionID):
        assert factionID
        return "CITY_DUNGEON_MG_KILL{%d}" % factionID

    def get_mg_sums_key(self, factionID):
        assert factionID
        return "CITY_DUNGEON_MG_SUMS{%d}" % factionID

    def incr_mg_sums(self, p, incr=1):
        key = self.get_mg_sums_key(p.factionID)
        return int(entity_pool.execute("INCRBY", key, incr) or 0)

    def get_mg_sums(self, p):
        key = self.get_mg_sums_key(p.factionID)
        return int(entity_pool.execute("GET", key) or 0)

    def incr_mg_kill(self, p, mg_id, incr=1):
        p.city_dungeon_kill_count += incr
        CityDungeonKillRanking.incr_score(p.factionID, incr)
        kill_key = self.get_mg_kill_key(p.factionID)
        entity_pool.execute("HINCRBY", kill_key, mg_id, incr)
        f = Faction.simple_load(p.factionID, ['city_top_member_kills'])
        if p.city_dungeon_kill_count > f.city_top_member_kills:
            dd = {
                "name": p.name,
                "prototypeID": p.prototypeID,
                "borderID": p.borderID,
            }
            lineup = p.lineups.get(LineupType.City, [])
            if not lineup:
                lineup = p.lineups.get(LineupType.ATK, [])
            if lineup:
                petID = filter(lambda s: s, lineup)[0]
                pet = p.pets.get(petID)
                if pet:
                    dd.update({
                        "petID": pet.prototypeID,
                        "pet_step": pet.breaklevel,
                    })
            f.city_top_member = dd
            f.city_top_member_kills = p.city_dungeon_kill_count
            f.save()
        p.save()
        p.sync()

    def get_mg(self, p):
        if p.city_dungeon_mg_cache:
            mg = p.city_dungeon_mg_cache
        else:
            mg = self.get_mg_from_pool(p)
            if not mg:
                mg = self.gen_mg(p)
            p.city_dungeon_mg_cache = mg
            p.save()
        return dict(mg)

    def gen_mg(self, p):
        incr = 1
        sums = self.incr_mg_sums(p, incr)
        origin = self.get_mg_by_count(sums - incr)
        current = self.get_mg_by_count(sums)
        horn = False
        if current["id"] != origin["id"]:
            # 进入下一层
            message_configs = get_config(CityDungeonMessageConfig)
            message_config = message_configs.get(origin["id"])
            if not message_config:
                message_config = message_configs[max(message_configs)]
            full_message = ""
            red_message = ""
            red_count = 0
            if message_config.multiple1 or message_config.multiple2:
                rs = CityDungeonSumsRanking.pool.execute_pipeline(
                    [
                        "ZADD",
                        CityDungeonSumsRanking.key,
                        current["id"],
                        p.factionID,
                    ],
                    [
                        "ZCOUNT",
                        CityDungeonSumsRanking.key,
                        current["id"],
                        "+inf",
                    ]
                )
                count = rs[1]
                if (not message_config.multiple1) or \
                        message_config.multiple1 and count == 1:
                    full_message = message_config.unions_win_desc.format(
                        p.faction_name, current["id"])
                if (not message_config.multiple2) or \
                        message_config.multiple2 and count == 1:
                    red_count = message_config.red_paper_count
                    red_message = message_config.red_paper_desc.format(
                        p.faction_name, current["id"], red_count)
                    red_drop = message_config.red_paper
            else:
                CityDungeonSumsRanking.update_score(p.factionID, current["id"])
                full_message = message_config.unions_win_desc
                red_count = message_config.red_paper_count
                red_message = message_config.red_paper_desc
            if full_message:
                _type = RedType.Horn if horn else RedType.Normal
                g_redManager.send_red_message(
                    p, full_message, type=_type,
                    module=RedModuleType.CityDungeon)
            if red_message and red_count:
                g_redManager.send_red_message(
                    p, red_message, red_count=red_count,
                    type=RedType.Red, red_drop=red_drop,
                    module=RedModuleType.CityDungeon, name=p.faction_name)
            self.sync_city_dungeon_current_info(p)
        return current

    def sync_city_dungeon_current_info(self, p):
        current_info = self.get_current_info(p)
        f = Faction.simple_load(p.factionID, ["memberset"])
        for entityID in f.memberset:
            proxy.sync_city_dungeon_current_info(entityID, current_info)

    def get_mg_from_pool(self, p):
        key = self.get_mg_pool_key(p.factionID)
        mg = entity_pool.execute("LPOP", key)
        if mg:
            mg = json.loads(mg)
        return mg

    def add_mg_into_pool(self, p, mg):
        key = self.get_mg_pool_key(p.factionID)
        mg = json.dumps(mg)
        return entity_pool.execute("RPUSH", key, mg)

    def get_mg_by_count(self, count):
        configs = get_config(
            CityDungeonMonsterGroupConfig)
        current = None
        sums = 0
        for _, config in configs.items():
            sums += config.monster_group_count
            if count <= sums:
                current = config
                break
        if not current:  # 数量很大，已经超出表了
            rest = count - sums
            last = configs[max(configs)]
            over = rest // last.monster_group_count
            current = last
        else:
            over = 0
        mg = dict(current._asdict())
        mg.update({
            "id": current.id + over,
            "monsters": [{
                "pos": k, "prototypeID": v
            } for k, v in enumerate(
                current.monster_id) if v]
        })
        return mg

    def get_mg_config_by_id(self, id):
        configs = get_config(CityDungeonMonsterGroupConfig)
        config = configs.get(id)
        if not config:
            max_id = max(configs)
            if id > max_id:
                return configs[max_id]
        return config

    def battle(self, p, fight, rsp):
        mg = p.city_dungeon_mg_cache
        message_configs = get_config(CityDungeonMessageConfig)
        self_message = ""
        message_config = message_configs.get(mg["id"])
        if not message_config:
            message_config = message_configs[max(message_configs)]
        if fight.fightResult:
            kills = len(mg.get("monsters", []))
            config = self.get_mg_config_by_id(mg["id"])
            rewards = parse_reward(config.rewards)
            self_message = message_config.single_win_desc.format(mg["id"])
            # 玩家损血
            # {{ 使用每日PVP
            for each in fight.player_team:
                pet = p.pets[each.entityID]
                if each.restHP == 0:
                    pet.daily_dead = True
                else:
                    pet.daily_restHP = each.restHP
                pet.save()
                pet.sync()
            # }}
        else:
            kills = 0
            pending = []
            for enemy in fight.enemy_team:
                for m in mg["monsters"]:
                    if m["pos"] == enemy.posIndex:
                        if not enemy.restHP:
                            pending.append(m)
                            kills += 1
                        else:
                            m["restHP"] = enemy.restHP
            for m in pending:
                mg["monsters"].remove(m)
            self.add_mg_into_pool(p, mg)
            now = int(time.time())
            # {{ 使用每日PVP
            p.daily_dead_cd = now + get_cons_value("DailyDeadCD")
            # }}
            rewards = {}
            self_message = message_config.single_lose_desc.format(mg["id"])
        if fight.total_damage:
            CityDungeonSelfRanking.incr_score(
                p.entityID, fight.total_damage)
        if kills:
            self.incr_mg_kill(p, mg["id"], kills)
            if fight.fightResult:
                self.sync_city_dungeon_current_info(p)
        if rewards:
            rewards = combine_reward(
                rewards, config.must_rewards)
            rewards = apply_reward(
                p, rewards, type=RewardType.CityDungeon)
            build_reward_msg(rsp, rewards)
            combine_reward(rewards, {}, p.city_dungeon_rewards)
        if self_message:
            g_redManager.send_red_message(
                p, self_message, to_self=True,
                module=RedModuleType.CityDungeon)
        p.city_dungeon_mg_cache.clear()
        p.save()
        p.sync()

    def give_reward(self):
        ranking = CityDungeonSelfRanking.get_range_by_score(
            "-inf", "+inf", withscores=True)
        configs = get_config(CityDungeonRewardConfig)
        from campaign.manager import g_campaignManager
        start_time = g_campaignManager.city_dungeon_campaign.get_start_time()
        final_time = g_campaignManager.city_dungeon_campaign.get_final_time()
        for rank, (entityID, score) in enumerate(
                convert_list_to_dict(ranking, dictcls=OrderedDict).items(), 1):
            if not rank:
                continue
            for c in configs.values():
                start, end = c.range
                if start:
                    if start > rank:
                        continue
                if end:
                    if end < rank:
                        continue
                config = c
            if not config:
                continue
            title, content, ID = get_mail("CityDungeon")
            content = content.format(rank)
            rewards = parse_reward(config.rewards)
            key = "CityDungeon{%d}{%d}" % (start_time, final_time)
            try:
                proxy.city_send_mail(
                    entityID, title, content, rewards, key, ID)
            except AttributeError:
                pass

    def reset(self):
        from campaign.manager import g_campaignManager
        start_time = g_campaignManager.city_dungeon_campaign.get_start_time()
        final_time = g_campaignManager.city_dungeon_campaign.get_final_time()
        reset = int(float(index_pool.execute(
            "GETSET", CityDungeonReset, start_time) or 0))
        if reset >= start_time and reset <= final_time:
            index_pool.execute(
                "SET", CityDungeonReset, reset)
            logger.info("Not need reset city dungeon")
            return
        logger.info("Reset city dungeon")
        # 发送奖励
        self.give_reward()
        cmds = []
        # 备份
        self.set_top_info()
        CityDungeonKillRanking.pool.execute(
            'ZUNIONSTORE', CityDungeonKillBackupRanking.key,
            1, CityDungeonKillRanking.key)

        CityDungeonSelfRanking.pool.execute(
            'ZUNIONSTORE', CityDungeonSelfBackupRanking.key,
            1, CityDungeonSelfRanking.key)
        # 清除数据
        ranking = CityDungeonKillRanking.get_range_by_score("-inf", "+inf")
        for k in ranking:
            k = int(k)
            f = Faction.simple_load(k, [
                "entityID", "faction_treasure",
                "city_top_member_kills"])
            f.city_top_member_kills = 0
            f.faction_treasure = 0
            f.save()
            cmds.append([
                "DEL",
                self.get_mg_pool_key(k),
                self.get_mg_sums_key(k),
            ])
            cmds.append([
                "HCLEAR", self.get_mg_kill_key(k)
            ])
        entity_pool.execute_pipeline(*cmds)
        index_pool.execute_pipeline(
            ("DEL", CityDungeonKillRanking.key),
            ("DEL", CityDungeonSelfRanking.key),
            ("DEL", CityDungeonSumsRanking.key),
        )
        g_redManager.clean_red(module=RedModuleType.CityDungeon)
        top_faction = self.get_top_faction()
        if top_faction:
            g_cityContend.set_top_faction(top_faction)
        self.reset_players()

    def reset_players(self):
        for p in g_entityManager.players.values():
            self.reset_player(p)

    def reset_player(self, p, all=False):
        from campaign.manager import g_campaignManager
        start_time = g_campaignManager.city_dungeon_campaign.get_start_time()
        final_time = g_campaignManager.city_dungeon_campaign.get_final_time()
        reset = p.city_dungeon_last_reset
        if reset >= start_time and reset <= final_time:
            return
        logger.info("Player reset city dungeon")
        p.city_dungeon_mg_cache.clear()
        p.city_dungeon_dead_cd = 0
        p.city_dungeon_last_reset = start_time
        p.city_dungeon_kill_count = 0
        if all:
            p.city_dungeon_rewards.clear()
        # {{ 鼓舞及复活
        p.daily_dead_cd = 0
        Player.pool.execute("del", "daily_dead_p{%d}" % p.entityID)
        p.clear_daily_dead()
        p.daily_inspire_used_count = 0
        # }}
        p.save()
        p.sync()

    def get_top_info(self):
        rs = index_pool.execute(
            "GET", CityDungeonTop)
        if rs:
            info = msgpack.loads(rs)
            return info

    def get_top_faction(self):
        info = self.get_top_info()
        if info:
            return int(info.get("top_factionID", 0)) or None

    def set_top_info(self):
        ranking = CityDungeonKillRanking .get_range_by_score(
            "-inf", "+inf", count=1)
        if ranking:
            faction = Faction.simple_load(
                ranking[0],
                ["entityID", "name", "leaderID"])
            if faction:
                info = {
                    "top_factionID": faction.entityID,
                    "top_faction_name": faction.name,
                }
                player = Player.simple_load(
                    faction.leaderID, ["name"])
                if player:
                    info.update({
                        "top_faction_leader_name": player.name
                    })
                index_pool.execute(
                    "SET", CityDungeonTop, msgpack.dumps(info))

    def get_panel(self, p, rsp):
        rsp.faction_rank = CityDungeonKillRanking.get_rank(p.factionID)
        rsp.self_rank = CityDungeonSelfRanking.get_rank(p.entityID)
        faction_rankers = convert_list_to_dict(
            CityDungeonKillRanking.get_range_by_score(
                "-inf", "+inf", count=10, withscores=True),
            dictcls=OrderedDict)
        factions = Faction.batch_load(
            faction_rankers.keys(),
            ["entityID", "name", "level"])
        for faction in factions:
            if not faction:
                continue
            score = faction_rankers[faction.entityID]
            faction_rankers[faction.entityID] = {
                "name": faction.name,
                "score": score,
                "level": FactionRankRanking.get_score(faction.factionID) or 1,
            }
        player_rankers = convert_list_to_dict(
            CityDungeonSelfRanking.get_range_by_score(
                "-inf", "+inf", count=10, withscores=True),
            dictcls=OrderedDict)
        players = Player.batch_load(
            player_rankers.keys(),
            ["entityID", "name", "faction_name", "level"])
        for player in players:
            score = player_rankers[player.entityID]
            player_rankers[player.entityID] = {
                "name": player.name,
                "score": score,
                "level": player.level,
                "name2": player.faction_name,
            }
        rsp.faction_ranking = sorted(
            faction_rankers.values(), key=lambda s: s["score"], reverse=True)
        rsp.self_ranking = sorted(
            player_rankers.values(), key=lambda s: s["score"], reverse=True)
        rsp.top_prototypeID = p.prototypeID
        rsp.current_info = self.get_current_info(p)
        rsp.top_member_info = self.get_top_member_info(p)
        rsp.reds = g_redManager.get_red_messages(
            module=RedModuleType.CityDungeon)

    def get_cleaned_dungeons(self, p, top):
        start = max(top - 4, 1)
        final = max(start + 1, top + 1)
        r = range(start, final)
        info = dict(zip(r, entity_pool.execute(
                    "HMGET", self.get_mg_kill_key(p.factionID),
                    *r)))
        cleaned_dungeons = []
        for k, v in info.items():
            v = int(v or 0)
            k = int(k)
            config = self.get_mg_config_by_id(k)
            if v >= config.monster_group_count * len(config.monster_id):
                cleaned_dungeons.append(k)
        return cleaned_dungeons

    def get_current_info(self, p):
        dd = {}
        dd["top"] = int(
            CityDungeonSumsRanking.get_score(p.factionID) or 1)
        dd["cleaned_dungeons"] = self.get_cleaned_dungeons(p, dd["top"])
        dd["top"] = max(dd["cleaned_dungeons"] or [0]) + 1
        config = self.get_mg_config_by_id(dd["top"])
        kill_count = int(entity_pool.execute(
            "HGET", self.get_mg_kill_key(p.factionID), dd["top"]) or 0)
        dd["top_count"] = max(
            config.monster_group_count * len(config.monster_id) - kill_count,
            0) / len(config.monster_id)
        return dd

    def get_top_member_info(self, p):
        f = Faction.simple_load(p.factionID, [
            "city_top_member", "city_top_member_kills"])
        dd = dict(f.city_top_member)
        dd["kill_count"] = f.city_top_member_kills
        return dd


class CityContend(object):
    top_factionID = None

    def set_top_faction(self, factionID):
        self.top_factionID = factionID

    def is_top_faction(self, factionID):
        return self.top_factionID == factionID

    def get_target(self, p):
        if not p.city_contend_cache_target:
            if self.is_top_faction(p.factionID):
                targets_pool = CityContendAttackRanking
            else:
                targets_pool = CityContendDefendRanking
            size = targets_pool.count()
            if not size:
                targets_pool = CityDungeonSelfBackupRanking
                size = targets_pool.count()
            if not size:
                targets_pool = PlayerLevelRanking
                size = targets_pool.count()
            rank = int(random.randint(1, size) or 0)
            if not rank:
                return None
            targetID = targets_pool.get_by_rank(rank)
            detail = get_opponent_detail(
                targetID, type=LineupType.City)
            if not detail.get("pets"):
                detail = get_opponent_detail(targetID)
            result = detail
            try:
                del result["lastlogin"]
            except KeyError:
                pass
            p.city_contend_cache_target = result
        return dict(p.city_contend_cache_target)

    def get_events(self, p):
        if not p.city_contend_events:
            configs = get_config(CityEventConfig)
            start = p.city_contend_total_step + 1
            events = []
            c = 0
            for i in icount(start):
                i = i % len(configs) or len(configs)
                config = configs.get(i)
                if not config:
                    continue
                if self.is_top_faction(p.factionID):
                    events.append({
                        "type": config.defend_event_type,
                        "argv": config.defend_event_argv
                    })
                else:
                    events.append({
                        "type": config.attack_event_type,
                        "argv": config.attack_event_argv
                    })
                if self.is_top_faction(p):
                    if config.defend_event_type == CityContendEventType.End:
                        break
                else:
                    if config.attack_event_type == CityContendEventType.End:
                        break
                c += 1
                if c > len(configs):
                    break
            p.city_contend_events = events
            p.save()
        return list(p.city_contend_events)

    def get_current_step(self, p):
        event = p.city_contend_events[p.city_contend_step]
        return event

    def check_event(self, p, type):
        try:
            event = p.city_contend_events[p.city_contend_step]
        except IndexError:
            return False
        return event.get("type") == type

    def battle(self, p, fight, rsp):
        treasures = get_config(CityTreasureConfig)
        self_message = ""
        full_message = ""
        red_message = ""
        red_count = 0
        horn = False
        target = p.city_contend_cache_target
        if self.is_top_faction(p.factionID):
            message_configs = get_config(CityContendDefendMessageConfig)
            message_config = message_configs.get(p.city_contend_count)
            if not message_config:
                message_config = message_configs[max(message_configs)]
            if fight.fightResult:
                event = self.get_current_step(p)
                drop = event["argv"]
                reward = open_reward(RewardType.CityContendDefend, drop)
                rewards = reward.apply(p)
                combine_reward(rewards, {}, p.city_contend_rewards)
                try:
                    target_name = target.get("name", u"").decode("utf-8")
                    target_faction_name = (target.get(
                        "faction_name", u"") or u"").decode("utf-8")
                except UnicodeEncodeError:
                    target_name = target.get("name", u"")
                    target_faction_name = target.get("faction_name", u"")
                self_message = message_config.single_defend_win_desc.format(
                    target_faction_name, target_name
                )
                # {{ 使用每日PVP
                for each in fight.player_team:
                    pet = p.pets[each.entityID]
                    if each.restHP == 0:
                        pet.daily_dead = True
                    else:
                        pet.daily_restHP = each.restHP
                    pet.save()
                    pet.sync()
                # }}
                rsp.rewards = build_reward(rewards)
            else:
                sub = p.city_contend_treasure * get_cons_value(
                    "CityContendFailPunish") / float(100)
                p.city_contend_treasure = max(
                    p.city_contend_treasure - sub, 1)
                # {{ 每日PVP
                now = int(time.time())
                p.daily_dead_cd = now + get_cons_value("DailyDeadCD")
                # }}
                try:
                    target_name = target.get("name", u"").decode("utf-8")
                    target_faction_name = (target.get(
                        "faction_name", u"") or u"").decode("utf-8")
                except UnicodeEncodeError:
                    target_name = target.get("name", u"")
                    target_faction_name = target.get("faction_name", u"")
                self_message = message_config.single_defend_lose_desc.format(
                    target_faction_name, target_name
                )
            module = RedModuleType.CityContendDefend
        else:
            message_configs = get_config(CityContendAttackMessageConfig)
            message_config = message_configs.get(p.city_contend_count + 1)
            if not message_config:
                message_config = message_configs[max(message_configs)]
            if fight.fightResult:
                p.city_contend_count += 1
                self_count = CityContendAttackRanking.update_score(
                    p.entityID, p.city_contend_count)
                count = CityContendAttackRanking.pool.execute(
                    "ZCOUNT", CityContendAttackRanking.key, self_count, "+inf")
                CityContendFactionRanking.incr_score(
                    p.factionID, 1)
                treasure = treasures.get(
                    p.city_contend_cache_target.get("level", 1))
                if not treasure:
                    treasure = treasures[max(treasures)]
                money = treasure.attack_treasure * get_cons_value(
                    "CityContendAttackMoney")
                soul = treasure.attack_treasure * get_cons_value(
                    "CityContendAttackSoul")
                event = self.get_current_step(p)
                drop = event["argv"]
                gain = {"money": money, "soul": soul}
                reward = open_reward(
                    RewardType.CityContendAttack, drop
                )
                drop_reward = reward.apply_after()
                total_reward = apply_reward(
                    p, combine_reward(gain, drop_reward),
                    type=RewardType.CityContendAttack)
                combine_reward(total_reward, {}, p.city_contend_rewards)
                p.city_contend_total_treasure += treasure.attack_treasure
                rsp.rewards = build_reward(drop_reward)
                rsp.treasure_rewards = build_reward(gain)
                rsp.treasure_count = treasure.attack_treasure
                if not message_config.multiple1 or message_config.multiple1 \
                        and count == 1:
                    full_message = message_config.attack_count_desc.format(
                        p.faction_name, p.name, p.city_contend_count
                    )
                    horn = message_config.horn1
                try:
                    target_name = target.get("name", u"").decode("utf-8")
                except UnicodeEncodeError:
                    target_name = target.get("name", u"")
                self_message = message_config.single_attack_win_desc.format(
                    target_name
                )
                if not message_config.multiple2 or message_config.multiple2 \
                        and count == 1:
                    red_count = message_config.red_paper_count
                    red_drop = message_config.red_paper
                    red_message = message_config.red_paper_desc.format(
                        p.faction_name, p.name,
                        p.city_contend_count, red_count
                    )
                # {{ 使用每日PVP
                for each in fight.player_team:
                    pet = p.pets[each.entityID]
                    if each.restHP == 0:
                        pet.daily_dead = True
                    else:
                        pet.daily_restHP = each.restHP
                    pet.save()
                    pet.sync()
                # }}
            else:
                # {{ 每日PVP
                now = int(time.time())
                p.daily_dead_cd = now + get_cons_value("DailyDeadCD")
                # }}
                # FIXME
                try:
                    target_name = target.get("name", u"").decode("utf-8")
                except UnicodeEncodeError:
                    target_name = target.get("name", u"")
                self_message = message_config.single_attack_lose_desc.format(
                    target_name
                )
            module = RedModuleType.CityContendAttack
        if self_message:
            g_redManager.send_red_message(
                p, self_message,
                to_self=True,
                module=module)
        if full_message:
            _type = RedType.Horn if horn else RedType.Normal
            g_redManager.send_red_message(
                p, full_message, type=_type,
                module=module)
        if red_message and red_count:
            g_redManager.send_red_message(
                p, red_message, red_drop=red_drop,
                red_count=red_count, type=RedType.Red,
                module=module)
        p.save()
        p.sync()

    def get_player_ranking(self, ranking):
        player_rankers = convert_list_to_dict(
            ranking.get_range_by_score(
                "-inf", "+inf", count=10, withscores=True),
            dictcls=OrderedDict)
        players = Player.batch_load(
            player_rankers.keys(),
            ["entityID", "name", "faction_name",
             "level", "city_contend_total_treasure"])
        for player in players:
            score = player_rankers[player.entityID]
            player_rankers[player.entityID] = {
                "name": player.name,
                "score": score,
                "level": player.level,
                "name2": player.faction_name,
                "score2": player.city_contend_total_treasure,
            }
        player_rankers = sorted(
            player_rankers.values(), key=lambda s: (
                s["score"], s["score2"]), reverse=True)
        return player_rankers

    def get_faction_ranking(self, ranking):
        faction_rankers = convert_list_to_dict(
            ranking.get_range_by_score(
                "-inf", "+inf", count=10, withscores=True),
            dictcls=OrderedDict)
        factions = Faction.batch_load(
            faction_rankers.keys(),
            ["entityID", "name", "level"])
        for faction in factions:
            score = faction_rankers[faction.entityID]
            faction_rankers[faction.entityID] = {
                "name": faction.name,
                "score": score,
                "level": FactionRankRanking.get_score(faction.factionID) or 1,
            }
        faction_rankers = sorted(
            faction_rankers.values(), key=lambda s: s["score"], reverse=True)
        return faction_rankers

    def get_panel(self, p, rsp):
        if self.is_top_faction(p.factionID):  # 防守方
            rsp.self_rank = CityContendDefendRanking.get_rank(p.entityID)
            if not rsp.self_rank:
                CityContendDefendRanking.update_score(p.entityID, 0)
            rsp.self_ranking = self.get_player_ranking(
                CityContendDefendRanking)
            if not p.city_contend_treasure:
                configs = get_config(CityTreasureConfig)
                config = configs.get(p.level)
                if not config:
                    config = configs[max(configs)]
                p.city_contend_treasure = config.defend_treasure
                p.save()
                p.sync()
        else:  # 攻击方
            rsp.self_rank = CityContendAttackRanking.get_rank(p.entityID)
            if not rsp.self_rank:
                CityContendAttackRanking.update_score(p.entityID, 0)
            rsp.faction_rank = CityContendFactionRanking.get_rank(p.factionID)
            if not rsp.faction_rank:
                CityContendFactionRanking.update_score(p.factionID, 0)
            rsp.self_ranking = self.get_player_ranking(
                CityContendAttackRanking)
            rsp.faction_ranking = self.get_faction_ranking(
                CityContendFactionRanking)
        rsp.reds = list(g_redManager.get_red_messages(
            module=RedModuleType.CityContendDefend)) + list(
                g_redManager.get_red_messages(
                    module=RedModuleType.CityContendAttack))
        rsp.events = self.get_events(p)
        rsp.rewards = build_reward(parse_reward(p.city_contend_rewards))
        f = Faction.simple_load(p.factionID, ["faction_treasure"])
        rsp.faction_treasure = f.faction_treasure

    def end_defend_event(self, p):
        Faction.incr_attribute(
            p.factionID, "faction_treasure", p.city_contend_treasure)
        p.city_contend_total_treasure += p.city_contend_treasure
        p.city_contend_treasure = 0
        p.city_contend_step = 0
        p.city_contend_events = []
        p.city_contend_count += 1
        p.save()
        p.sync()
        # self_count = CityContendDefendRanking.incr_score(
        #     p.entityID, p.city_contend_treasure)
        self_count = CityContendDefendRanking.update_score(
            p.entityID, p.city_contend_count)
        message_configs = get_config(CityContendDefendMessageConfig)
        message_config = message_configs.get(p.city_contend_count)
        if not message_config:
            message_config = message_configs[max(message_configs)]
        count = CityContendDefendRanking.pool.execute(
            "ZCOUNT", CityContendDefendRanking.key, self_count, "+inf")
        full_message = ""
        red_message = ""
        red_count = 0
        if message_config.multiple1 or message_config.multiple1 \
                and count == 1:
            full_message = message_config.defend_count_desc.format(
                p.name, p.city_contend_count
            )
            horn = message_config.horn1
        if message_config.multiple2 or message_config.multiple2 \
                and count == 1:
            red_count = message_config.red_paper_count
            red_message = message_config.red_paper_desc.format(
                p.faction_name, p.name, p.city_contend_count, red_count
            )
            red_drop = message_config.red_paper
        if full_message:
            g_redManager.send_red_message
            _type = RedType.Horn if horn else RedType.Normal
            g_redManager.send_red_message(
                p, full_message, type=_type)
        if red_message and red_count:
            g_redManager.send_red_message(
                p, red_message, red_drop=red_drop,
                red_count=red_count, type=RedType.Red,
                module=RedModuleType.CityContendDefend)

    def reset(self):
        from campaign.manager import g_campaignManager
        start_time = g_campaignManager.city_contend_campaign.get_start_time()
        final_time = g_campaignManager.city_contend_campaign.get_final_time()
        reset = int(float(index_pool.execute(
            "GETSET", CityContendReset, start_time) or 0))
        if reset >= start_time and reset <= final_time:
            index_pool.execute(
                "SET", CityContendReset, reset)
            logger.info("Not need reset city contend")
            return
        logger.info("Reset city contend")
        # 清除数据
        index_pool.execute_pipeline(
            ("DEL", CityContendFactionRanking.key),
            ("DEL", CityContendAttackRanking.key),
            ("DEL", CityContendDefendRanking.key),
        )
        g_redManager.clean_red(module=RedModuleType.CityContendAttack)
        g_redManager.clean_red(module=RedModuleType.CityContendDefend)
        self.reset_players()

    def reset_players(self):
        for p in g_entityManager.players.values():
            self.reset_player(p)

    def reset_player(self, p, all=False):
        from campaign.manager import g_campaignManager
        start_time = g_campaignManager.city_contend_campaign.get_start_time()
        final_time = g_campaignManager.city_contend_campaign.get_final_time()
        reset = p.city_contend_last_reset
        if reset >= start_time and reset <= final_time:
            return
        logger.info("Player reset city contend")
        p.city_contend_cache_target.clear()
        if all:
            p.city_contend_rewards.clear()
        p.city_contend_total_treasure_backup = p.city_contend_total_treasure
        p.city_contend_count_backup = p.city_contend_count
        p.city_contend_last_reset = start_time
        p.city_contend_treasure = 0
        p.city_contend_step = 0
        p.city_contend_total_treasure = 0
        p.city_contend_events = []
        p.city_contend_count = 0
        p.city_contend_total_step = 0
        # {{ 鼓舞及复活
        p.daily_dead_cd = 0
        Player.pool.execute("del", "daily_dead_p{%d}" % p.entityID)
        p.clear_daily_dead()
        p.daily_inspire_used_count = 0
        # }}
        p.save()
        p.sync()

    def get_end_panel(self, p, rsp):
        build_reward_msg(rsp, p.city_contend_rewards)


g_cityDungeon = CityDungeon()
g_cityContend = CityContend()


def city_send_mail_offline(entityID, title, content, rewards, key, ID):
    if not int(Player.pool.execute(
            "HSET", "city_rewards_recv_p{%d}" % entityID, key, "") or 0):
        return
    p = Player.simple_load(entityID, ['factionID'])
    rank = CityDungeonKillRanking.get_rank(p.factionID)
    content = content.format(rank)
    send_mail(entityID, title, content, addition=rewards, configID=ID)


@proxy.rpc(failure=city_send_mail_offline)
def city_send_mail(entityID, title, content, rewards, key, ID):
    if not int(Player.pool.execute(
            "HSET", "city_rewards_recv_p{%d}" % entityID, key, "") or 0):
        return
    p = g_entityManager.get_player(entityID)
    if not p:
        p = Player.simple_load(entityID, ['factionID'])
    rank = CityDungeonKillRanking.get_rank(p.factionID)
    content = content.format(rank)
    send_mail(entityID, title, content, addition=rewards, configID=ID)


@proxy.rpc
def sync_city_dungeon_current_info(entityID, current_info):
    p = g_entityManager.get_player(entityID)
    if p:
        rsp = poem_pb.CityDungeonCurrentInfo(**current_info)
        msg = success_msg(msgid.CITY_DUNGEON_CURRENT_INFO, rsp)
        g_playerManager.sendto(entityID, msg)
