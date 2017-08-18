# coding:utf-8
import time
import math
import ujson
import random
import cPickle
import logging
logger = logging.getLogger("pvp")
from datetime import datetime

from state.base import StateObject
from state.base import StartState
from state.base import StopState
# from collections import defaultdict

from yy.utils import guess
from yy.utils import choice_one
from yy.utils import convert_list_to_dict
from yy.entity.storage.redis import make_key
from yy.db.redisscripts import load_redis_script

from entity.manager import g_entityManager

from player.model import Player
from player.model import PlayerRankRanking
from player.model import PlayerMaxPowerRanking
from player.formulas import get_open_level

from config.configs import get_config
from config.configs import PvpRewardConfig
from config.configs import PvpRewardByGroupConfig
from config.configs import PvpActivityConfig
from config.configs import PvpSerialWinBuffConfig
from config.configs import PvpRuleConfig
from config.configs import PvpGradConfig
from config.configs import get_cons_value

from pvp.manager import is_zombie
from pvp.manager import get_opponent_detail
from pvp.manager import get_zombies_by_level
from pvp.manager import get_opponent_detail_all

from reward.manager import combine_reward
from mail.manager import send_mail
from mail.constants import MailType
from lineup.constants import LineupType

from gm.proxy import proxy


import settings
pool = settings.REDISES["index"]
RANK_CLEAR_FLAG = \
    "RANK_CLEAR_FLAG{%d}{%d}" % (
        settings.SESSION["ID"], settings.REGION["ID"])

RANK_BACKUPS = \
    "RANK_BACKUPS{%d}{%d}" % (
        settings.SESSION["ID"], settings.REGION["ID"])

WAIT_INTERVAL = 5 * 60

RANK_COUNT = None


def get_pvprankcount(update=False):
    global RANK_COUNT
    if RANK_COUNT is None or update:
        with PlayerRankRanking.pool.ctx() as conn:
            RANK_COUNT = conn.execute("ZCARD", PlayerRankRanking.key) or 0
    return max(RANK_COUNT, get_cons_value("PvpMinRankerCount"))


def update_pvprankcount():
    if not g_rankManager.is_open():
        return
    get_pvprankcount(update=True)
    from entity.manager import g_entityManager
    for p in g_entityManager.players.values():
        p.clear_pvprankcount()


def get_need_rank_by_ranking(pvprankcount, ranking):
    need_rank = math.ceil(
        pvprankcount * ranking / float(100))
    return need_rank


def get_grad(rank, score, count):
    configs = get_config(PvpGradConfig)
    prev = configs[0].ID if configs else 0
    for v in configs:
        if score >= v.score:
            if count >= v.count:
                need_rank = get_need_rank_by_ranking(
                    get_pvprankcount(), v.ranking)
                if not need_rank or rank < need_rank:
                    prev = v.ID
                    continue
        break
    return prev


@load_redis_script(pool=settings.REDISES['index'])
def incr_score(key, value):
    '''
    local val = tonumber(ARGV[2])
    local meb = ARGV[1]
    local key = KEYS[1]
    local r1 = tonumber(redis.call('ZREVRANK', key, meb))
    local s = tonumber(redis.call('ZSCORE', key, meb))
    if not s then
        s = 1000
    end
    if val > 0 then
        val = s + val
    elseif val < 0 then
        val = s + val
        if val < 0 then
            val = 0
        end
    else
        return val
    end
    redis.call('ZADD', key, val, meb)
    local r2 = tonumber(redis.call('ZREVRANK', key, meb))
    if r1 ~= 0 then
        if r2 == 0 then
            return 1
        end
    end
    return 0
    '''
    # 从不是第一到第一返回1
    keys = (PlayerRankRanking.key,)
    vals = (key, value)
    return keys, vals


def sync_rank_offline(entityID, history, fight=None):
    from player.model import Player
    FIGHT_HISTORY_LIMIT = 5
    pkey = make_key(Player.store_tag, entityID)
    history['ID'] = '%d:%d' % (history['time'], history['oppID'])
    if incr_score(entityID, history['score']):
        from chat.manager import on_news_pvp_first
        on_news_pvp_first(Player.simple_load(entityID, ["entityID", "name"]))
    Player.pool.execute('HINCRBY', pkey, 'rank_count', 1)
    Player.pool.execute(
        "LPUSH",
        "rank_history_p{%d}" %
        entityID,
        Player.fields['rank_history'].encoder(history))
    Player.pool.execute("LTRIM", "rank_history_p{%d}" % entityID, 0, 30)
    if fight:
        Player.pool.execute(
            "HSET",
            "rank_fight_history_p{%d}" %
            entityID,
            history['ID'],
            fight)
        keys = Player.pool.execute(
            'HKEYS',
            "rank_fight_history_p{%d}" %
            entityID)
        if len(keys) > FIGHT_HISTORY_LIMIT:
            for key in sorted(keys)[:-FIGHT_HISTORY_LIMIT]:
                Player.pool.execute(
                    "HDEL",
                    "rank_fight_history_p{%d}" %
                    entityID,
                    key)
    if history['isWin']:
        Player.pool.execute('HINCRBY', pkey, 'rank_win_count', 1)
    else:
        Player.pool.execute('HINCRBY', pkey, 'rank_passive_offline_count', 1)
    return 'FAILURE'


@proxy.rpc(failure=sync_rank_offline)
def sync_rank(entityID, history, fight=None):
    from entity.manager import g_entityManager
    from player.model import Player
    FIGHT_HISTORY_LIMIT = 5
    p = g_entityManager.get_player(entityID)
    pkey = make_key(Player.store_tag, entityID)
    history['ID'] = '%d:%d' % (history['time'], history['oppID'])

    if incr_score(entityID, history['score']):
        from chat.manager import on_news_pvp_first
        on_news_pvp_first(p)
    logger.debug('player is online %d' % entityID)
    PlayerRankRanking.sync_player(p)
    p.pvprank = PlayerRankRanking.get_rank(entityID)
    p.rank_history.appendleft(history)
    p.rank_history.ltrim(0, 30)
    p.rank_count = Player.pool.execute('HINCRBY', pkey, 'rank_count', 1)
    p.remove_dirty('rank_count')
    if fight:  # clean fight history
        p.rank_fight_history[history['ID']] = fight
        if len(p.rank_fight_history) > FIGHT_HISTORY_LIMIT:
            for key in sorted(p.rank_fight_history)[:-FIGHT_HISTORY_LIMIT]:
                del p.rank_fight_history[key]
    if history['isWin']:
        logger.debug('player is win %d' % entityID)
        p.rank_win_count = Player.pool.execute(
            'HINCRBY',
            pkey,
            'rank_win_count',
            1)
        p.remove_dirty('rank_win_count')
    if history['isActive']:
        logger.debug("{}".format(history))
        logger.debug('player is active %d' % entityID)
        from task.manager import on_rank_count
        from task.manager import on_rank_season_count, on_rank_win_count
        on_rank_count(p)
        p.pvpseasoncount += 1
        on_rank_season_count(p)
        p.rank_detail_cache = {}
        p.rank_active_count += 1
        p.rank_active_win_count += 1
        if history['isWin']:
            now = int(time.time())
            MAX_SERIAL_WIN_COUNT_CD = 3600
            if not history.get('isRevenge', False):
                if p.rank_serial_win_count_cd and \
                        p.rank_serial_win_count_cd > now:
                    p.rank_serial_win_count += 1
                else:
                    p.rank_serial_win_count = 1
                configs = get_config(PvpSerialWinBuffConfig)
                config = configs.get(p.rank_serial_win_count)
                if not config:
                    config = configs[max(configs)]
                if config.cd:
                    p.rank_serial_win_count_cd = now + min(
                        MAX_SERIAL_WIN_COUNT_CD,
                        max(p.rank_serial_win_count_cd - now, 0) + config.cd)
                p.rank_defeated_targets.add(history['oppID'])
                on_rank_win_count(p)
        else:
            if not history.get('isRevenge', False):
                p.rank_serial_win_count = 0
                p.rank_serial_win_count_cd = 0
    p.save()
    p.sync()
    return 'SUCCESS'


def get_season_key(start, end):
    assert isinstance(start, int)
    assert isinstance(end, int)
    return ujson.dumps((start, end))


def get_season_time(season_key):
    return tuple(ujson.loads(season_key))


class RankManager(StateObject):

    def __init__(self):
        super(RankManager, self).__init__(wait_interval=WAIT_INTERVAL)
        self.size = 2  # max seasons cache size
        self.load_hists()

    #  {{{ implement stateobject
    def get_loops(self):
        configs = get_config(PvpActivityConfig)
        return [[v.start, v.end, k] for k, v in configs.items()]

    def enter_stop(self):
        self.backup()

    def execute_stop(self):
        st, ed, _ = self.get_current()
        self.give_reward(get_season_key(st, ed))

    def enter_wait(self):
        self.sync()

    def enter_start(self):
        self.sync()
        self.reset()
    #  }}}

    def get_current(self):
        if self.current_loop is None:
            return 0, 0, 1
        v = get_config(PvpActivityConfig).get(self.current_loop)
        return v.start, v.end, v.group

    def get_hist(self, season_key):
        try:
            hist = self.hists[get_season_time(season_key)]
        except KeyError:
            logger.error("Not found season key %s, load again" % season_key)
            hist = self.load_hist(season_key)
            if not hist:
                logger.error("Loaded fail season key %s" % season_key)
            else:
                self.set_hist(season_key, hist)
        return hist

    def set_hist(self, season_key, hist):
        if not hist:
            return
        self.hists[get_season_time(season_key)] = hist
        if len(self.hists) >= self.size:
            seasons = sorted(map(
                lambda s: s, self.hists.keys()))[:len(self.hists) - self.size]
            for season in seasons:
                del self.hists[season]

    def load_hist(self, season_key):
        with pool.ctx() as conn:
            data = conn.execute("HGET", RANK_BACKUPS, season_key)
        return cPickle.loads(data)

    def load_hists(self):
        self.hists = {}
        with pool.ctx() as conn:
            keys = conn.execute("HKEYS", RANK_BACKUPS)
        seasons = sorted(map(
            lambda s: get_season_time(s), keys))[-self.size:]
        for season in seasons:
            key = get_season_key(*season)
            self.set_hist(key, self.load_hist(key))

    def is_open(self):
        if self.state:
            return isinstance(self.state, StartState)
        return False

    def is_close(self):
        if self.state:
            return isinstance(self.state, StopState)
        return True

    def sync(self):
        # 同步在线玩家关闭/开启消息
        for p in g_entityManager.players.values():
            p.clear_pvpopen()
            p.clear_pvpstarttime()
            p.clear_pvpfinaltime()
            p.sync(
                'pvpopen',
                'pvpstarttime',
                'pvpfinaltime'
            )

    def reset(self):
        # 清除在线玩家rank数据
        for p in g_entityManager.players.values():
            self.reset_rank(p)
        # 清除排行榜数据
        # 防止重复clear
        st, ed, group = self.get_current()
        season_key = get_season_key(st, ed)
        with pool.ctx() as conn:
            old_key = conn.execute("GETSET", RANK_CLEAR_FLAG, season_key)
            if season_key == old_key:
                return
        PlayerRankRanking.clear_raw()

    def reset_rank(self, p):
        # 清除玩家上次PVP数据
        # 进世界调用， 开启PVP瞬间调用
        if not self.need_reset(p):
            return
        # 清除上次PVP数据
        p.pvprewards = set()
        p.rank_detail_cache = {}
        p.rank_count = 0
        p.rank_active_count = 0
        p.rank_active_win_count = 0
        p.rank_win_count = 0
        p.rank_targets = []
        p.rank_defeated_targets.clear()
        p.rank_revenged_targets.clear()

        p.rank_rest_count = p.fields['rank_rest_count'].default
        p.rank_resume_rest_count_cd = 0
        p.rank_reset_used_count = 0
        p.rank_refresh_cd = 0
        p.rank_refresh_used_count = 0

        p.rank_serial_win_count = 0
        p.rank_serial_win_count_cd = 0
        p.npc_targets_cd.clear()
        p.npc_target_cache = 0

        p.rank_free_vs = 10  # 策划要求
        p.rank_cd = 0

        p.rank_history.clear()
        p.rank_fight_history.clear()

        p.todaybp = 0
        p.pvprank = 0
        p.totalbp = 0
        p.pvpgrad = 0
        p.pvpseasoncount = 0
        p.pvplastcleantime = int(time.time())
        p.rank_passive_offline_count = 0
        logger.debug('reset last rank data')
        p.save()
        p.sync()

    def need_reset(self, p):
        last = p.pvplastcleantime
        logger.debug('Rank pvplastcleantime %d' % last)
        if not last:
            p.pvplastcleantime = int(time.time())
            p.save()
            return False
        if not self.is_open():  # 不在开启期间
            if not self.hists:  # 没有历史，说明不需要处理旧数据
                logger.debug("Rank not historys")
                return False
            # 玩家上次参与了PVP，此类玩家的属性不应该清除
            # 玩家上次之前参与了PVP， 此类玩家的数据需要清除
            if last < sorted(self.hists.keys())[-1][0]:
                # 如果玩家清除数据的时间比上次PVP开启的时间还早，
                # 说明玩家上次的PVP并没有参加，
                # PVP数据是上次PVP之前的旧数据，需要被清除
                logger.warn(
                    'Rank too old data for player:`%d`, %d'
                    % (p.entityID, p.pvplastcleantime))
                return True
            return False
        st, ed, group = self.get_current()
        need = last < st or last > ed
        logger.debug('Rank need clean {}'.format(need))
        return need

    def get_last_rank_list(self, count=50):
        if not self.hists:
            return []
        try:
            if not self.is_open():
                st, ed = key = sorted(self.hists.keys())[-2]
            else:
                st, ed = key = sorted(self.hists.keys())[-1]
        except IndexError:
            st, ed = key = sorted(self.hists.keys())[-1]
        hist = self.hists[key]
        logger.debug(
            "Rank list %s - %s",
            datetime.fromtimestamp(st),
            datetime.fromtimestamp(ed))
        rankers = [k for k, v in sorted(
            hist['ranks'].items(), key=lambda s: s[1]['rank'])][:count]
        needs = [
            'entityID', 'name', 'level',
            'career', 'prototypeID', 'totalbp',
            'rank_win_count', "factionID"]
        thumbs = g_entityManager.get_players_info(rankers, needs)
        for thumb in thumbs:
            thumb['pvprank'] = rankers.index(thumb['entityID']) + 1
            thumb['totalbp'] = hist['ranks'].get(
                thumb['entityID'], {}).get("score", 0)
            detail = get_opponent_detail_all(thumb["entityID"])
            thumb.update(detail)
            thumb["pvpgrad"] = hist["ranks"].get(
                thumb['entityID'], {}).get("grad", 0)
            thumb["rank_win_count"] = hist["ranks"].get(
                thumb['entityID'], {}).get("win_count", 0)
        thumbs.sort(key=lambda s: s['pvprank'])
        return thumbs

    def get_rank_list(self, rank, page=0, count=50):
        if rank <= count:
            start = '-inf'
            end = '+inf'
            offset = count * page
            rankscores = PlayerRankRanking.get_range_by_score(
                start, end,
                count=count + 1,  # 多取一条，用于判断是否有下一页
                offset=offset,
                withscores=True,
            )
            infos = convert_list_to_dict(rankscores)
            rankers = [c for i, c in enumerate(rankscores) if i % 2 == 0]
            offset += 1
        else:
            start = max(rank + count * page, 0)
            end = start + count
            rankers = PlayerRankRanking.get_by_range(
                start, end + 1,  # 多取一条，用于判断是否有下一页
            )
            offset = start
            scores = PlayerRankRanking.get_scores(rankers)
            infos = dict(zip(rankers, scores))
        needs = [
            'entityID', 'name', 'level',
            'career', 'prototypeID', 'totalbp',
            'rank_win_count', "factionID"]
        thumbs = g_entityManager.get_players_info(rankers, needs)
        for thumb in thumbs:
            thumb['pvprank'] = rankers.index(thumb['entityID']) + offset
            thumb['totalbp'] = infos.get(thumb['entityID'], 0)
            detail = get_opponent_detail_all(thumb["entityID"])
            thumb.update(detail)
        thumbs.sort(key=lambda s: s['pvprank'])
        return thumbs

    def backup(self):
        st, ed, group = self.get_current()
        assert st
        assert ed
        score = 0
        group = get_config(PvpRewardByGroupConfig).get(group, [])
        configs = get_config(PvpRewardConfig)
        for each in group:
            config = configs[each.ID]
            scond, econd = config.condition
            score = scond
        # 分数高于配置表最低分数段
        scores = PlayerRankRanking.get_range_by_score(
            score, '+inf', withscores=True)
        rank = 0
        index = 0
        old_c = 0
        # ranks = defaultdict(dict)
        ranks = {}
        for c in scores:
            c = int(c)
            index += 1
            if index % 2 == 0:
                ranks.setdefault(old_c, {}).setdefault("score", c)
                # ranks[old_c]['score'] = c
            else:
                rank += 1
                ranks.setdefault(c, {}).setdefault('rank', rank)
                # ranks[c]['rank'] = rank
            old_c = c
        pvprankcount = get_pvprankcount(update=True)
        # 将玩家数据, 和将要获得的奖励，都计算好
        for k, v in ranks.items():
            rank = v['rank']
            score = v['score']
            obj = Player.simple_load(k, [
                "rank_active_count", "rank_win_count"])
            count = getattr(obj, "rank_active_count",  0)
            grad = get_grad(rank, score, count)
            ranks[k]["grad"] = grad
            win_count = getattr(obj, "rank_win_count",  0)
            ranks[k]["win_count"] = win_count
            for each in sorted(group, key=lambda s: s.ID):
                config = configs[each.ID]
                s, c = config.condition
                if score < s:
                    continue
                if count < c:
                    continue
                need_rank = get_need_rank_by_ranking(
                    pvprankcount, config.ranking)
                logger.debug("rank:%d, need_rank:%d", rank, need_rank)
                if need_rank and rank > need_rank:
                    continue
                ranks[k].setdefault("rewards", []).append(config.ID)
        _configs = {}
        for k, v in configs.items():
            _configs[k] = v._asdict()
        data = {"ranks": ranks, "configs": _configs}
        st, ed, group = self.get_current()
        season_key = get_season_key(st, ed)
        self.set_hist(season_key, data)
        with pool.ctx() as conn:
            conn.execute(
                "HSETNX", RANK_BACKUPS, season_key, cPickle.dumps(data))
        return season_key

    def give_reward(self, season_key, player=None):
        logger.info('Give reward {}'.format(season_key))
        hist = self.get_hist(season_key)
        if not hist:
            return
        ranks, configs = hist["ranks"], hist["configs"]
        if player:
            players = [player]
        else:
            players = g_entityManager.players.values()
        for p in players:
            rank = ranks.get(p.entityID)
            if not rank:
                continue
            title = ""
            content = ""
            rewards = {}
            for i in sorted(rank.get("rewards", []), reverse=True):
                title = configs[i]["title"]
                content = configs[i]["content"]
                rewards = combine_reward(rewards, configs[i]["rewards"])
            if rewards:
                grad = rank.get("grad", 0)
                self.send_mail(
                    p, title, content, rewards, grad, season_key)

    def send_mail(self, player, title, content, rewards, grad, key):
        if key in player.pvprankreceiveds:
            return
        send_mail(
            player.entityID,
            title,
            content,
            addition=rewards,
            type=MailType.Pvp)
        player.pvpseasonreward = {
            "title": title, "reward": rewards, "grad": grad}
        player.pvprankreceiveds.add(key)  # 防止重复添加
        player.save()
        player.sync()

    def check_mail(self, p):
        for season, hists in self.hists.items():
            ranks = hists.get("ranks")
            if p.entityID in ranks:
                self.give_reward(get_season_key(*season), player=p)

    def get_opponents_by_strategy(
            self,
            level,
            score,
            count=10,
            ldiff=1,
            sdiff=20):
        logger.debug("level: %d, score: %d", level, score)
        opps = set()
        opps.update(
            self.get_opponents_by_score(
                score,
                count -
                len(opps),
                sdiff))
        logger.debug("opps: %r", opps)
        while len(opps) < count:
            opps.update(
                self.get_opponents_by_score(
                    score,
                    count -
                    len(opps),
                    sdiff))
            score -= sdiff
            if score < 0:
                break
        if len(opps) >= 2:
            return list(opps)
        while len(opps) < count:
            o_len = len(opps)
            opps.update(get_zombies_by_level(level))
            if o_len == len(opps):
                break
            level = level - ldiff
            if level < 0:
                break
        logger.debug("last opps: %r", opps)
        return list(opps)

    def get_opponents_by_score(self, score, count, diff):
        rstart, rend = score - (diff - 1), score + (diff + 1)
        opps = map(
            lambda s: int(s),
            PlayerRankRanking.get_range_by_score(
                rstart,
                rend,
                count=count))
        opps = list(set(opps[:count]))
        return opps

    def get_opponents_by_level(self, level, count, diff):
        rstart, rend = max(1, level - (diff - 1)), level + (diff + 1)
        opps = []
        zombine_opps = []
        if len(opps) < count:
            ranges = range(rstart, rend)
            random.shuffle(ranges)
            while ranges:
                sample = ranges.pop()
                zombies = get_zombies_by_level(sample)
                if zombies:
                    c = random.randint(1, min(5, len(zombies)))
                    zombine_opps += zombies[:c]
                if len(opps + zombine_opps) >= count:
                    break
        opps = list(set((opps + zombine_opps)[:count]))
        return opps

    def get_opponent_detail_by_strategy(self, player):
        from config.configs import get_config, PvpDegreeConfig
        configs = get_config(PvpDegreeConfig)
        opps = []
        score = player.totalbp
        logger.debug("score: %d", score)
        for config in configs:
            logger.debug("start:%d, end:%d", config.start, config.end)
            if score >= config.start and score < config.end:
                logger.debug("prob:%f", config.prob)
                if guess(config.prob):
                    logger.debug("guess:true")
                    opps = get_zombies_by_level(player.level)
                break
        if not opps:
            opps = self.get_opponents_by_strategy(player.level, player.totalbp)
            opps = filter(lambda s: s != player.entityID, opps)
            logger.debug('random opps {}'.format(opps))
        oppID = choice_one(opps)
        assert oppID, 'not opp'
        logger.debug("choose opp:%d", oppID)
        return get_opponent_detail(oppID, type=LineupType.DEF)

    def get_rank_targets(self, p, count=10):
        if p.rank_targets:
            return p.rank_targets
        power = p.max_power
        score = p.totalbp or 1000
        configs = get_config(PvpRuleConfig)
        high_scores = []
        low_scores = []
        targets = set()
        for ID, config in configs.items():
            if config.score > score:
                high_scores.append((config.score, ID))
            else:
                low_scores.append((config.score, ID))
        if low_scores:
            floor = max(low_scores)
            high_scores.insert(0, floor)
        current = configs[min(high_scores)[1]]
        logger.debug("current config: %r", current)
        high_score_rest = current.high_score_count
        high_scores = sorted([i for i, j in high_scores])
        logger.debug("high_scores %r", high_scores)
        for index, s in enumerate(high_scores):
            if index > 1:
                break
            if not high_score_rest:
                logger.debug("high_score_rest:%r", high_score_rest)
                continue
            spower = int(power * (1 + current.power_down / float(100)))
            epower = int(power * (1 + current.power_up / float(100)))
            sscore = max(s, score)
            escore = high_scores[index + 1]\
                if index + 1 < len(high_scores) else "+inf"
            scores = set(PlayerRankRanking.get_range_by_score(
                sscore, '%s' % escore
                if isinstance(escore, basestring) else "(%d" % escore))
            logger.debug("sscore:%r", sscore)
            logger.debug("escore:%r", escore)
            logger.debug("scores:%r", scores)
            logger.debug("spower:%r", spower)
            logger.debug("epower:%r", epower)
            scores = scores - {p.entityID}
            ranks = scores
            if s != 1500:
                ranks = PlayerMaxPowerRanking.get_range_by_score(
                    spower, epower, count=100)
                logger.debug("ranks :%r", ranks)
                ranks = list((set(ranks) & scores))
            ranks = random.sample(ranks, min(len(ranks), high_score_rest))
            logger.debug("high_score_rest:%r", high_score_rest)
            logger.debug("rranks :%r", ranks)
            high_score_rest -= len(ranks)
            targets.update(ranks)
        low_score_rest = 0
        low_scores = sorted([i for i, j in low_scores], reverse=True)
        logger.debug("low_scores %r", low_scores)
        low_score_rest = high_score_rest + current.low_score_count
        for index, s in enumerate(low_scores):
            if index > 0:
                break
            if not low_score_rest:
                logger.debug("low_score_rest:%r", low_score_rest)
                continue
            spower = power * (1 + current.power_down / float(100))
            epower = power * (1 + current.power_up / float(100))
            sscore = low_scores[index + 1]\
                if index + 1 < len(low_scores) else "-inf"
            escore = max(s, score)
            scores = set(PlayerRankRanking.get_range_by_score(
                sscore, "(%d" % escore))
            ranks = PlayerMaxPowerRanking.get_range_by_score(
                spower, epower, count=100)
            logger.debug("sscore:%r", sscore)
            logger.debug("escore:%r", escore)
            logger.debug("scores:%r", scores)
            logger.debug("spower:%r", spower)
            logger.debug("epower:%r", epower)
            logger.debug("ranks :%r", ranks)
            ranks = list((set(ranks) & scores) - {p.entityID})
            ranks = random.sample(ranks, min(len(ranks), low_score_rest))
            logger.debug("rranks :%r", ranks)
            logger.debug("low_score_rest:%r", low_score_rest)
            low_score_rest -= len(ranks)
            targets.update(ranks)

        def choice_one():
            level = max(p.level - current.robot_level, 15)
            while level >= get_open_level("pvp"):
                logger.debug("level match %d", level)
                samples = get_zombies_by_level(level)
                while samples:
                    try:
                        one = random.choice(samples)
                        samples.remove(one)
                        yield one
                    except IndexError:
                        pass
                level -= 1
        for each in choice_one():
            if len(targets) >= count:
                break
            else:
                logger.debug("only level match %r", each)
                targets.add(each)
        logger.debug("final %r", targets)
        p.rank_targets = list(targets)
        p.save()
        return p.rank_targets

    def fix_rank(self, player):
        '''对非正常结束战斗的玩家进行处罚'''
        if self.is_open():
            now = int(time.time())
            if player.rank_detail_cache:
                detail = dict(player.rank_detail_cache)
                sync_rank(player.entityID, {
                    'oppID': detail['entityID'],
                    'name': detail['name'],
                    'prototypeID': detail.get('prototypeID') or
                    detail.get('prototypeID'),
                    'level': detail['level'],
                    'score': -15, 'isActive': True,
                    'isWin': False, 'time': now,
                })
                if not is_zombie(detail['entityID']):
                    proxy.sync_rank(detail['entityID'], {
                        'oppID': player.entityID,
                        'name': player.name,
                        'level': player.level,
                        'prototypeID': player.prototypeID,
                        'score': 5,
                        'isActive': False, 'isWin': True, 'time': now,
                    })

g_rankManager = RankManager()

if __name__ == '__main__':
    from yy.utils import load_settings
    load_settings()
    from yy.config.cache import load_config
    from config.configs import get_registereds
    from gevent import sleep
    load_config(get_registereds())
    g_rankManager.start()
    g_rankManager.backup()
    while True:
        sleep(1)
