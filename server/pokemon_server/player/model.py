# coding:utf-8
import time
# import math
from datetime import datetime
import settings

from player.c_player import c_PlayerBase
from player.manager import g_playerManager

from mail.constants import MailType

# from yy.entity.storage.redis import EntityStoreMixinRedis
# from yy.entity.identity import RedisIdentityGenerator
from yy.entity.storage.ssdb import EntityStoreMixinSsdb
from yy.entity.index import UniqueIndexing
from yy.entity.index import SetIndexing
# from yy.ranking import NaturalRanking
from yy.ranking import NaturalRankingWithJoinOrder
from yy.ranking import SwapRanking
from yy.db.redisscripts import load_redis_script

from common.redishelpers import EntityIdentityGenerator
from common import index


class OfflineAttrType:
    Add = 1  # 添加
    Set = 2  # 设置
    Reset = 3  # 重置


class Player(c_PlayerBase, EntityStoreMixinSsdb):
    pool = settings.REDISES['entity']

    def add_pets(self, *infos):
        if not infos:
            return []
        from pet.model import Pet
        from config.configs import get_config
        from config.configs import PetConfig
        playerID = self.entityID
        gettime = int(time.time())
        pets = []
        sames = set()
        for info in infos:
            prototypeID = info['prototypeID']
            config = get_config(PetConfig)[prototypeID]
            pet = Pet.create(
                name=config.name, masterID=playerID,
                gettime=gettime, mtype=config.mtype,
                **info
            )
            pet.save()
            self.pets[pet.entityID] = pet
            self.petset.add(pet.entityID)
            pets.append(pet)
            sames.add(config.same)
        from pet.manager import reload_relations
        changeds = reload_relations(self, sames)
        from entity.sync import multi_sync_property
        if changeds:
            self.clear_base_power()
            # self.update_power()
            self.sync("power")
            # multi_sync_property(changeds)
        multi_sync_property(list(set(pets + changeds)))
        return pets

    def add_equips(self, *infos):
        from equip.model import Equip
        from config.configs import NewEquipConfig, get_config
        playerID = self.entityID
        equips = []
        player_equips = {
            'player_equip1': getattr(self, "player_equip1"),
            'player_equip2': getattr(self, "player_equip2"),
            'player_equip3': getattr(self, "player_equip3"),
            'player_equip4': getattr(self, "player_equip4"),
            'player_equip5': getattr(self, "player_equip5"),
            'player_equip6': getattr(self, "player_equip6"),
        }
        for info in infos:
            prototypeID = info['prototypeID']
            config = get_config(NewEquipConfig)[prototypeID]
            if not config:
                continue
            equip = Equip.create(
                type=config.type,
                masterID=playerID,
                **info
            )
            for k, v in player_equips.items():
                setattr(equip, k, v)
            equip.save()
            self.equips[equip.entityID] = equip
            self.equipset.add(equip.entityID)
            equips.append(equip)
        from entity.sync import multi_sync_property
        if equips:
            multi_sync_property(equips)
        return equips

    def add_pats(self, patchs):
        # TODO 这个接口要优化
        from pet.manager import setdefault
        after_patchs = []
        for id, new in patchs.items():
            id = int(id)
            new = int(new)
            old = setdefault(self.petPatchs, id)
            self.petPatchs[id] = old + new
            after_patchs.append({id: self.petPatchs[id]})
        # self.set_petpatch_dirty(patchs.keys())
        # self.sync_petpatch()
        return after_patchs

    def load_pets(self):
        from pet.model import Pet
        from config.configs import get_config
        from config.configs import PetConfig
        configs = get_config(PetConfig)
        pets = Pet.batch_load(self.petset)
        for pet in pets:
            if not pet:
                continue
            config = configs.get(pet.prototypeID)
            if not config:
                continue
            pet.masterID = self.entityID
            pet.mtype = config.mtype
            # pet.activated_relations = []  # reset
            pet.pop_dirty()
            self.pets[pet.entityID] = pet
            for e in pet.equipeds.values():
                self.equipeds[e] = pet.entityID
        from pet.manager import reload_relations
        reload_relations(self, self.sames.keys())

    def load_equips(self):
        from equip.model import Equip
        from config.configs import NewEquipConfig, get_config
        configs = get_config(NewEquipConfig)
        equips = Equip.batch_load(self.equipset)
        for equip in equips:
            if not equip:
                continue
            config = configs.get(equip.prototypeID)
            if not config:
                continue
            equip.masterID = self.entityID
            equip.type = config.type
            for i in range(1, 7):
                setattr(
                    equip, "player_equip%d" % i,
                    getattr(self, "player_equip%d" % i, 0)
                )
            equip.pop_dirty()
            self.equips[equip.entityID] = equip

    def on_sync(self, *fields, **kwargs):
        from entity.utils import sync_property_msg
        all = kwargs.pop('all', False)
        if not fields:
            fields = self.pop_sync_dirty()
            if not fields and not all:
                return
        if all:
            fields = None
        return self.entityID, sync_property_msg(self, fields=fields, isme=True)

    def do_sync(self, sendto, rsp):
        g_playerManager.sendto(sendto, rsp)

    def sync(self, *fields, **kwargs):
        ret = self.on_sync(*fields, **kwargs)
        if ret:
            sendto, rsp = ret
            if sendto:
                self.do_sync(sendto, rsp)
        from mat.manager import sync_mats
        sync_mats(self, kwargs.get('all', False))
        from gem.manager import sync_gems
        sync_gems(self, kwargs.get('all', False))

    def load_mails(self):
        from mail.model import Mail
        mails = Mail.batch_load(self.mailset)
        for mail in mails:
            if not mail:
                continue
            self.mails[mail.mailID] = mail

    def load_faction(self):
        from faction.model import Faction
        from faction.model import FactionRankRanking
        from faction.manager import update_strengthen_level
        # now = int(time.time())
        if self.factionID:
            faction = Faction.simple_load(
                self.factionID, [
                    'leaderID', 'name',
                    'strengthen_at_level',
                    'strengthen_hp_level',
                    'strengthen_ct_level'
                ])
            if faction:
                if self.entityID == faction.leaderID:
                    applyset = Faction.simple_load(
                        self.factionID, ['applyset']).applyset
                    self.applyMemberSet = applyset
                self.faction_name = faction.name
                level = self.faction_level = FactionRankRanking.get_score(
                    self.factionID) or 1
                from task.manager import on_faction_level
                on_faction_level(self, level)
                update_strengthen_level(self, self.factionID)
        # if self.applyFactionTime and self.applyFactionTime < now:
        #     self.applyFactionTime = 0
        #     self.applyFactionID = 0
        return

    def load_group(self, now=None):
        from group.model import Group
        if self.groupID:
            g = Group.simple_load(
                self.groupID, ["leaderID", "applys", "lastlogin"])
            g.applys.load()
            if not now:
                now = datetime.now()
            if g.lastlogin and (now - g.lastlogin).days >= 5:
                g.leaderID = self.entityID
            if g.leaderID == self.entityID:
                self.group_applys = g.applys
                g.lastlogin = self.lastlogin
            g.save()
        return

    def add_mail(
            self, title, content,
            addition=None, addtime=None,
            type=MailType.System, cd=0):
        from mail.model import Mail
        if not addition:
            addition = {}
        if not addtime:
            addtime = int(time.time())
        mail = Mail.create(
            playerID=self.entityID, title=title,
            content=content, addition=addition,
            addtime=addtime, type=type,
            cd=cd,
        )
        mail.save()
        self.mails[mail.mailID] = mail
        # self.touch_mails()
        self.mailset.add(mail.mailID)
        self.save()
        self.sync()
        return mail

    # def load_offline_mail(self):
    #     # 离线邮件奖励
    #     from mail.model import EmailByTimeIndexing, Mail
    #     from mail.manager import validate_mail_condition
    #     import traceback
    #     if not self.lastlogout:
    #         return
    #     llogout_time  = int(time.mktime(self.lastlogout.timetuple()))
    #     now           = int(time.time())
    #     time_set      = set()
    #     format        = '%Y-%m-%d_%H:%M'
    #     mails = EmailByTimeIndexing.get_by_range(llogout_time, now)
    #     mails = Mail.batch_load(mails)
    #     for offline_mail in mails:
    #         if offline_mail.type == MailType.System:
    #             # 奖励离线邮件
    #             if llogout_time <= offline_mail.addtime and \
    #             validate_mail_condition(self, offline_mail.limitdata) and \
    #             offline_mail.mailID not in self.offlinemail_set:
    #                 #说明添加邮件时，玩家不在线
    #                 #防止重复添加
    #                     self.offlinemail_set.add(offline_mail.mailID)
    #                     self.add_mail(
    #                         offline_mail.title,
    #                         offline_mail.content,
    #                         offline_mail.addition,
    #                         offline_mail.addtime,
    #                         type=offline_mail.type
    #                     )
    #         elif offline_mail.type == MailType.Faction:
    #             # 公会离线邮件
    #             from faction.manager import get_faction_cache
    #             if self.factionID and offline_mail.addtime >= llogout_time:
    #                 atime = datetime.fromtimestamp(offline_mail.addtime).strftime(format)
    #                 cache = get_faction_cache(llogout_time, now)
    #                 try:
    #                     file_cache = cache[atime]
    #                 except KeyError:
    #                     traceback.print_exc()
    #                 if offline_mail.limitdata['csv_id'] == file_cache[self.factionID][0] \
    #                         and offline_mail.addtime not in time_set:
    #                     time_set.add(offline_mail.addtime)
    #                     self.fac_offlinemail_set.add(offline_mail.mailID)
    #                     self.add_mail(
    #                         offline_mail.title,
    #                         offline_mail.content,
    #                         offline_mail.addition,
    #                         offline_mail.addtime,
    #                         type=offline_mail.type
    #                     )

    def load_offline_attrs(self):
        # 从离线属性作用在用户身上
        attrs = getattr(self, 'offline_attrs')
        if attrs:
            for attr in attrs:
                attrid, value, type = attr
                try:
                    name = self.getAttributeByID(attrid).name
                except KeyError:
                    return False
                if type == OfflineAttrType.Add:
                    setattr(self, name, getattr(self, name) + value)
                elif type == OfflineAttrType.Set:
                    setattr(self, name, value)
                elif type == OfflineAttrType.Reset:
                    f = self.getAttributeByID(attrid)
                    if callable(f.default):
                        default = f.default()
                    else:
                        default = f.default
                    setattr(self, name, default)
                else:
                    continue
            self.offline_attrs = []
            self.save()
            return True
        else:
            return False

    @classmethod
    def add_offline_attr(cls, playerID, attrID, value,
                         type=OfflineAttrType.Add):
        # isAdd, 是添加还是覆盖
        try:
            cls.getAttributeByID(attrID)
        except KeyError:
            return False
        else:
            player = cls.simple_load(playerID, ['offline_attrs'])
            player.offline_attrs.append([attrID, value, type])
            player.save()
            return True

    def save_on_quit(self):
        for pet in self.pets.values():
            pet.save()
        self.totalbp_on_logout = self.totalbp
        # session服务器需要玩家vip字段，
        # 但vip字段是个公式属性，
        # 而session服务器没有计算公式属性需要的配置。
        # 所以缓存一个vip字段
        self.vip_offline = self.vip
        self.lastlogout = datetime.now()
        self.save()

    def del_mails(self, *mails):
        for mail in mails:
            try:
                del self.mails[mail.mailID]
                self.mailset.remove(mail.mailID)
            except KeyError:
                pass
        for mail in mails:
            mail.delete()
        # self.touch_mails()
        self.save()
        self.sync()
        return True

    def del_pets(self, *pets):
        from config.configs import PetConfig
        from config.configs import get_config
        sames = set()
        configs = get_config(PetConfig)
        for pet in pets:
            try:
                del self.pets[pet.entityID]
                self.petset.remove(pet.entityID)
                info = configs.get(pet.prototypeID)
                if info:
                    sames.add(info.same)
            except KeyError:
                pass
        for pet in pets:
            pet.delete()
        self.save()
        from pet.manager import reload_relations
        changeds = reload_relations(self, sames)
        from entity.sync import multi_sync_property
        if changeds:
            self.clear_base_power()
            # self.update_power()
            self.sync("power")
            multi_sync_property(changeds)
        return True

    def del_equips(self, *equips):
        for equip in equips:
            try:
                del self.equips[equip.entityID]
                self.equipset.remove(equip.entityID)
            except KeyError:
                pass
        for equip in equips:
            equip.delete()
        self.save()
        return True

    # def get_leader(self):
    #     leaderID = self.lineups[self.on_lineup][0]#队长
    #     return self.pets[leaderID]

    def is_pets_full(self):
        # 去掉限制
        return False
        # return len(self.pets) >= self.petmax

    def add_mats(self, matList):
        from config.configs import get_config, MatConfig
        configs = get_config(MatConfig)
        for matID, count in matList:
            assert matID in configs, 'not valid mat `%d`' % matID
            v = self.mats.get(matID, 0) + count
            if v < 0:
                v = 0
            self.mats[matID] = v
            self.dirty_mats.add(matID)

    def cost_mats(self, matList):
        for matID, count in matList:
            c = self.mats.get(matID, 0) - count
            if c < 0:
                try:
                    del self.mats[matID]
                except KeyError:
                    pass
            self.mats[matID] = c
            self.dirty_mats.add(matID)

    def add_gems(self, gemList):
        from config.configs import get_config, GemConfig
        configs = get_config(GemConfig)
        for gemID, count in gemList:
            assert gemID in configs, 'not valid gem `%d`' % gemID
            v = self.gems.get(gemID, 0) + count
            if v < 0:
                v = 0
            self.gems[gemID] = v
            self.dirty_gems.add(gemID)

    def cost_gems(self, gemList):
        for gemID, count in gemList:
            c = self.gems.get(gemID, 0) - count
            if c < 0:
                try:
                    del self.gems[gemID]
                except KeyError:
                    pass
            self.gems[gemID] = c
            self.dirty_gems.add(gemID)

PlayerOnlineIndexing = UniqueIndexing(
    "index_p_online{%d}{%d}" % (
        settings.REGION["ID"], settings.SESSION["ID"]),
    settings.REDISES['index'])
# 竞技场排名
PlayerRankRanking = NaturalRankingWithJoinOrder.init_entity(
    Player, 'totalbp', pool=settings.REDISES['index'],
    key=index.RANK_TOTALBP.render())
# 等级排名
PlayerLevelRanking = NaturalRankingWithJoinOrder(
    index.RANK_LEVEL.render(), settings.REDISES['index'])
# 当前战力排名
PlayerPowerRanking = NaturalRankingWithJoinOrder(
    index.RANK_POWER.render(), settings.REDISES['index'])
# 最高战力排名
PlayerMaxPowerRanking = NaturalRankingWithJoinOrder(
    index.RANK_MAXPOWER.render(), settings.REDISES['index'])
# 玩家名称集合
PlayernameIndexing = UniqueIndexing(
    index.INDEX_NAME.render(), settings.REDISES['index'])
# 玩家推荐集合
PlayerFriendRecommendIndexing = SetIndexing(
    index.SET_FRIEND_RECOMMEND.render(),
    settings.REDISES['index'])
PlayerFriendRecommendOnlineIndexing = SetIndexing(
    index.SET_FRIEND_RECOMMEND_ONLINE.render(), settings.REDISES['index'])
PlayerDuplicateNamesIndexing = SetIndexing(
    index.SET_DUPLICATE_NAMES.render(),
    settings.REDISES['index'])
Player.set_identity_generator(
    EntityIdentityGenerator(
        pool=settings.REDISES['identity'],
        key='identity_player',
        initial=100000))
PlayerSwapRankRanking = SwapRanking(
    Player, 'swaprank',
    pool=settings.REDISES['index'],
    register_on_create=True,
    key=index.RANK_SWAPRANK.render())

PlayerDailyRankRanking = NaturalRankingWithJoinOrder(
    index.RANK_DAILYRANK.render(), settings.REDISES['index'])
PlayerAmbitionCountRanking = NaturalRankingWithJoinOrder.init_entity_reverse(
    Player, 'ambition_count', pool=settings.REDISES['index'],
    key=index.RANK_AMBITION.render())
PlayerPetCountRanking = NaturalRankingWithJoinOrder.init_entity_reverse(
    Player, 'ranking_pet_count', pool=settings.REDISES['index'],
    key=index.RANK_PETCOUNT.render())
PlayerBestPetRanking = NaturalRankingWithJoinOrder.init_entity_reverse(
    Player, 'ranking_pet_power', pool=settings.REDISES['index'],
    key=index.RANK_PETMAXPOWER.render())
PlayerBestEquipRanking = NaturalRankingWithJoinOrder.init_entity_reverse(
    Player, 'ranking_equip_power', pool=settings.REDISES['index'],
    key=index.RANK_EQUIPMAXPOWER.render())
PlayerStarRanking = NaturalRankingWithJoinOrder(
    index.RANK_STAR.render(), settings.REDISES['index'])
PlayerAdvancedRanking = NaturalRankingWithJoinOrder(
    index.RANK_ADVANCED.render(), settings.REDISES['index'])
PlayerProgressRanking = NaturalRankingWithJoinOrder.init_entity_reverse(
    Player, 'fbprocess', pool=settings.REDISES['index'],
    key=index.RANK_PROGRESS .render())
PlayerBossKillRanking = NaturalRankingWithJoinOrder.init_entity_reverse(
    Player, 'friendfb_kill_count', pool=settings.REDISES['index'],
    key=index.RANK_BOSSKILL.render())
PlayerRobmine1Ranking = NaturalRankingWithJoinOrder(
    index.RANK_ROBMINE1.render(), settings.REDISES['index'])
PlayerRobmine2Ranking = NaturalRankingWithJoinOrder(
    index.RANK_ROBMINE2.render(), settings.REDISES['index'])
PlayerClimbTowerRanking = NaturalRankingWithJoinOrder(
    index.RANK_CLIMB_TOWER.render(), settings.REDISES['index'])


from yy.utils import get_random_string


class LockedError(Exception):
    pass


class Lock(object):
    LockedError = LockedError

    def __init__(self, name, pool, timeout=None):
        self.name = name
        self.pool = pool
        self.timeout = timeout

    def make_key(self, entityID):
        return self.name % entityID

    def lock(self, entityID, force=False):
        unlocking_key = get_random_string()
        key = self.make_key(entityID)
        cmd = ["SET", key, unlocking_key]
        if self.timeout is not None:
            cmd.extend(["EX", self.timeout])
        if not force:
            cmd.append("NX")
        with self.pool.ctx() as conn:
            success = bool(conn.execute(*cmd))
        if not success:
            raise LockedError
        return unlocking_key

    @load_redis_script
    def can_unlock(self, entityID, unlocking_key):
        '''\
        local key = KEYS[1]
        local unlocking_key = ARGV[1]
        local value = redis.call('GET', key)
        if value == unlocking_key then
          return 1
        end
        return 0\
        '''
        key = self.make_key(entityID)
        return (key, ), (unlocking_key, )

    @load_redis_script
    def unlock(self, entityID, unlocking_key):
        """\
        local key = KEYS[1]
        local unlocking_key = ARGV[1]
        local value = redis.call('GET', key)
        if value == unlocking_key then
          return redis.call('DEL', key);
        end
        return 0\
        """
        key = self.make_key(entityID)
        return (key, ), (unlocking_key, )

    def locked(self, entityID):
        key = self.make_key(entityID)
        with self.pool.ctx() as conn:
            return bool(conn.execute("EXISTS", key))

SWAP_LOCK_CD = 5*60 + 5
PlayerMineLock = Lock(
    "lock_p_%d_mine",
    settings.REDISES['index'], timeout=10*60)
PlayerLootLock = Lock(
    "lock_p_%d_loot",
    settings.REDISES['index'], timeout=60*60)
PlayerFightLock = Lock(
    "lock_p_%d_fight",
    settings.REDISES['index'])
PlayerNpcFightLock = Lock(
    "lock_p_%d_npcfight",
    settings.REDISES['index'])
PlayerTreasureLock = Lock(
    "lock_p_%d_treasurefight",
    settings.REDISES['index'])
PlayerSwapLock = Lock(
    "lock_p_%d_swapRank",
    settings.REDISES['index'], timeout=SWAP_LOCK_CD)  # 5秒用于延时
PlayerDailyLock = Lock(
    "lock_p_%d_dailyRank",
    settings.REDISES['index'], timeout=SWAP_LOCK_CD)  # 5秒用于延时
PlayerAccreditLock = Lock(
    "lock_p_%d_accredit",
    settings.REDISES['index'], timeout=SWAP_LOCK_CD)  # 5秒用于延时
