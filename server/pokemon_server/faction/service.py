# coding:utf-8
import time

import protocol.poem_pb as msgid
from protocol import poem_pb

from yy.rpc import RpcService
from yy.rpc import rpcmethod

from yy.utils import trie
from yy.utils import convert_list_to_dict

from yy.message.header import fail_msg
from yy.message.header import success_msg

from yy.entity.index import DuplicateIndexException

from yy.entity.base import EntityNotFoundError
from yy.entity.base import EntityExistsException

from common import msgTips
from common.log import gm_logger
# from faction.manager import *  # NOQA
from entity.manager import level_required
from entity.manager import g_entityManager
from player.model import PlayernameIndexing
from player.model import PlayerFightLock

from reward.manager import RewardType
from reward.manager import apply_reward
from reward.manager import AttrNotEnoughError
from reward.manager import parse_reward
from reward.manager import build_reward
from reward.manager import open_reward
from reward.manager import build_reward_msg
from reward.manager import combine_reward

from faction.model import Faction
from faction.model import FactionRankRanking
from faction.model import FactionnameIndexing
from faction.model import FactionSkillRanking

from config.configs import get_config
from config.configs import get_cons_value
from config.configs import FactionLimitConfig
from config.configs import dirty_words_trie
from config.configs import FactionDonateConfig
from config.configs import FactionStrengthenConfig
from config.configs import FactionLevelRewardConfig
from config.configs import FactionMallUnlockConfig
from config.configs import CityDungeonRewardConfig
from config.configs import CityTreasureRecvConfig

from pvp.manager import get_opponent_detail
from pvp.manager import update_onlines
from gm.proxy import proxy

# from explore.dlc import get_helper_cd

from .manager import is_applied
from .manager import is_apply
from .manager import get_faction_info
from .manager import validate_name
from .manager import join_faction
from .manager import recommend
from .manager import scan_recommned
from .manager import get_faction_thumb
from .manager import isrecommend
# from .manager import APPLYFACTIONCD
from .manager import safe_remove
from .manager import notify_change
from .manager import unrecommend
from .manager import DISMISSFACTIONCD
from .manager import QUITFACTIONCD
from .manager import clean_faction
from .manager import refresh_faction_task
from .manager import notify_strengthen_change

from .city import g_cityDungeon
from .city import g_cityContend
from .city import CityDungeonSelfBackupRanking
from .city import CityContendEventType
from .city import CityDungeonKillBackupRanking
from campaign.manager import g_campaignManager
from fight.cache import get_cached_fight_response
from fight.cache import cache_fight_response
from lineup.constants import LineupType


class FactionService(RpcService):
    @rpcmethod(msgid.FACTION_INFO)
    @level_required(tag="union")
    def faction_info(self, msgtype, body):
        p = self.player
        factionID = p.factionID
        if not factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        info = get_faction_info(p.factionID)
        if not info:
            p.factionID = 0
            p.save()
            p.sync()
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        if info['dflag']:
            if info['leaderID'] == p.entityID:
                # 检查解散公会
                if p.dismissCD:
                    if p.dismissCD < int(time.time()):
                        faction = Faction.simple_load(factionID, ['name'])
                        faction.delete()
                        FactionnameIndexing.unregister(faction.name)
                        FactionRankRanking.del_key(factionID)
                        clean_faction(p.entityID)
                        p.dismissCD = 0
                        p.save()
                        p.sync()
                        return fail_msg(
                            msgtype,
                            msgTips.FAIL_MSG_FACTION_ALREADY_DISMISSED)
        if not info:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_NOT_THIS_FACTION)
        rsp = poem_pb.FactionInfo(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FACTION_CREATE)
    @level_required(tag="union")
    def faction_create(self, msgtype, body):
        p = self.player
        # 判断是否可以创建公会
        if p.factionID:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FACTION_ALREADY_HAD_FACTION)
        # if is_applied(p):
        #     return fail_msg(
        #         msgtype, msgTips.FAIL_MSG_FACTION_ALREADY_APPLYED)
        req = poem_pb.AlterNameFaction()
        req.ParseFromString(body)
        name, err = validate_name(req.name)
        if err:
            return fail_msg(msgtype, err)
        try:
            FactionnameIndexing.register(0, name)  # 占位
        except DuplicateIndexException:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FACTION_DUPLICATE_FACTION_NAME)
        try:
            now = int(time.time())
            faction = Faction.create(
                name=name,
                createtime=now,
                leaderID=p.entityID
            )
        except EntityExistsException:
            FactionnameIndexing.unregister(name)
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_CREATE_FAIL)
        try:
            apply_reward(
                p, {}, cost={'gold': 500}, type=RewardType.CreateFaction)
        except AttrNotEnoughError:
            FactionnameIndexing.unregister(name)
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_NOT_ENOUGH_GOLD)
        FactionnameIndexing.pool.execute(
            'HSET', FactionnameIndexing.key, name, faction.entityID)  # 更新
        faction.save()
        gm_logger.info({'faction': {
            'entityID': p.entityID, 'type': 'create_faction',
            'factionName': faction.name, 'factionLevel': 1,
            'factionID': faction.factionID,
        }})
        join_faction(p.entityID, faction.factionID)
        p.faction_is_leader = True
        p.save()
        p.sync()
        recommend(faction.factionID)  # 加入推荐列表
        FactionRankRanking.update_score(faction.factionID, 1)
        rsp = poem_pb.FactionInfo(**get_faction_info(faction.factionID))
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FACTION_SEARCH)
    @level_required(tag="union")
    def faction_search(self, msgtype, body):
        req = poem_pb.SearchFaction()
        req.ParseFromString(body)
        rsp = poem_pb.FactionInfos()
        if req.factionID:
            rs = [req.factionID]
        elif req.name:
            rs = FactionnameIndexing.get_pk(req.name)
            if rs:
                rs = [rs]
            else:
                rs = []
        else:
            count = 25
            rs = list(scan_recommned(count))
        for factionID in rs:
            faction_info = get_faction_info(factionID)
            if not faction_info:
                continue
            applied = (factionID in self.player.applyFactions)
            faction_info.update(applied=applied)
            rsp.infos.add(**faction_info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FACTION_RANK)
    @level_required(tag="union")
    def faction_rank(self, msgtype, body):
        req = poem_pb.RequestFactionRankList()
        req.ParseFromString(body)
        rsp = poem_pb.FactionInfos()
        rank = 0
        if req.type == poem_pb.RequestFactionRankList.Self:
            if self.player.factionID:
                rank = FactionRankRanking.get_rank(self.player.factionID)
        count = 50
        page = req.index
        if rank <= count:
            start = '-inf'
            end = '+inf'
            offset = count * page
            rankscores = FactionRankRanking.get_range_by_score(
                start, end,
                count=count + 1,  # 多取一条，用于判断是否有下一页
                offset=offset,
                withscores=True,
            )
            infos = convert_list_to_dict(rankscores)
            rankers = [c for i, c in enumerate(rankscores) if i % 2 == 0]
            offset += 1
        else:
            start = max(rank - 1 + count * page, 0)
            end = start + count
            rankers = FactionRankRanking.get_by_range(
                start, end + 1,  # 多取一条，用于判断是否有下一页
            )
            offset = start - 1
            scores = FactionRankRanking.get_scores(rankers)
            infos = dict(zip(rankers, scores))
        thumbs = []
        for i in rankers:
            thumb = get_faction_thumb(i)
            if not thumb:
                continue
            thumbs.append(thumb)
        for thumb in thumbs[:count]:
            thumb['rank'] = rankers.index(thumb['factionID']) + offset
            thumb['level'] = infos.get(thumb['factionID'], 1)
            rsp.infos.add(**thumb)
        thumbs.sort(key=lambda s: s['rank'])
        if len(thumbs) > count:
            rsp.hasnext = True
        else:
            rsp.hasnext = False
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FACTION_MEMBER_INFOS)
    @level_required(tag="union")
    def faction_member_infos(self, msgtype, body):
        factionID = self.player.factionID
        if not factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        faction = Faction.simple_load(factionID, ['memberset'])
        thumbs = g_entityManager.get_players_info(
            list(faction.memberset), [
                'entityID', 'name', 'career',
                'prototypeID', 'totalfp', 'level',
                'todayfp', 'lastlogin', 'joinFactionTime',
            ]
        )
        rsp = poem_pb.MemberInfos()
        now = int(time.time())
        DAY = 86400
        for thumb in thumbs:
            last = int(time.mktime(
                thumb['lastlogin'].timetuple()
            ))
            thumb['time'] = now - last
            if thumb['time'] >= DAY:
                thumb['todayfp'] = 0
            thumb['jointime'] = now - thumb['joinFactionTime']
            detail = get_opponent_detail(thumb["entityID"])
            detail['beMyFriend'] = thumb["entityID"] in self.player.friendset
            detail['applied'] = thumb["entityID"] in self.player.friend_applys
            thumb.update(detail)
        update_onlines(thumbs)
        rsp.members = thumbs
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FACTION_APPLY_INFOS)
    @level_required(tag="union")
    def faction_apply_infos(self, msgtype, body):
        factionID = self.player.factionID
        if not factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        faction = Faction.simple_load(factionID, ['applyset', 'leaderID'])
        if self.player.entityID != faction.leaderID:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_PERMISSION_DENIED)
        applyIDs = faction.applyset
        thumbs = g_entityManager.get_players_info(
            applyIDs, [
                'entityID', 'name', 'career',
                'prototypeID', 'totalfp', 'level',
                'todayfp', 'lastlogin',
            ]
        )
        rsp = poem_pb.MemberInfos()
        now = int(time.time())
        for thumb in thumbs:
            last = int(time.mktime(
                thumb['lastlogin'].timetuple()
            ))
            thumb['time'] = now - last
            detail = get_opponent_detail(thumb["entityID"])
            thumb.update(detail)
            rsp.members.add(**thumb)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FACTION_INVITE_INFOS)
    @level_required(tag="union")
    def faction_invite_infos(self, msgtype, body):
        factionID = self.player.factionID
        if not factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        faction = Faction.simple_load(factionID, ['leaderID', 'inviteset'])
        if self.player.entityID != faction.leaderID:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_PERMISSION_DENIED)
        memberIDs = faction.inviteset
        thumbs = g_entityManager.get_players_info(
            memberIDs, [
                'entityID', 'name', 'career',
                'prototypeID', 'totalfp', 'level',
                'todayfp', 'lastlogin',
            ]
        )
        rsp = poem_pb.MemberInfos()
        now = int(time.time())
        for thumb in thumbs:
            last = int(time.mktime(
                thumb['lastlogin'].timetuple()
            ))
            thumb['time'] = now - last
            # rs = get_lineup_details_atk(thumb['entityID'])
            detail = get_opponent_detail(thumb["entityID"])
            thumb.update(detail)
            rsp.members.add(**thumb)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FACTION_APPLY)
    @level_required(tag="union")
    def faction_apply(self, msgtype, body):
        p = self.player
        if p.factionID:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FACTION_ALREADY_HAD_FACTION)
        req = poem_pb.ApplyFaction()
        req.ParseFromString(body)
        if is_apply(p, req.factionID):
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_ALREADY_APPLYED)
        try:
            faction = Faction.get(req.factionID)
        except EntityNotFoundError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_NOT_THIS_FACTION)
        if faction.dflag:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_CAN_NOT_JOIN_WILL_DISMISS_FACTION)
        if p.entityID in faction.inviteset:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_ALREADY_INVITED)
        if faction.mode == poem_pb.Free:
            if not isrecommend(req.factionID):
                return fail_msg(
                    msgtype, msgTips.FAIL_MSG_FACTION_MEMBERS_LIMIT_EXCEED)
            join_faction(p.entityID, faction.factionID)
        elif faction.mode == poem_pb.Deny:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_DENY_APPLY)
        else:
            # now = int(time.time())
            faction.applyset.add(self.player.entityID)
            faction.save()
            proxy.sync_apply(faction.leaderID)
            self.player.applyFactions.add(faction.factionID)
            # self.player.applyFactionID = faction.factionID
            # self.player.applyFactionTime = now + APPLYFACTIONCD
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FACTION_CANCEL_APPLY)
    @level_required(tag="union")
    def faction_cancel_apply(self, msgtype, body):
        req = poem_pb.CancelApplyFaction()
        req.ParseFromString(body)
        if not is_applied(self.player):
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_NOT_APPLYED)
        try:
            faction = Faction.load(req.factionID)
        except EntityNotFoundError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_NOT_THIS_FACTION)
        safe_remove(faction.applyset, self.player.entityID)
        safe_remove(self.player.applyFactions, req.factionID)
        # self.player.applyFactionID = 0
        # self.player.applyFactionTime = 0
        faction.save()
        proxy.sync_apply(faction.leaderID)
        self.player.save()
        self.player.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FACTION_INVITE)
    @level_required(tag="union")
    def faction_invite(self, msgtype, body):
        factionID = self.player.factionID
        faction = Faction.simple_load(factionID, ['leaderID', 'dflag'])
        if faction.dflag:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_CAN_NOT_INVITE_TO_WILL_DISMISS_FACTION)  # NOQA
        if self.player.entityID != faction.leaderID:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_PERMISSION_DENIED)
        req = poem_pb.InviteMember()
        req.ParseFromString(body)
        entityID = PlayernameIndexing.get_pk(req.name)
        if not entityID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_PLAYER_NOT_FOUND)
        err = proxy.invite_member(factionID, entityID)
        if err:
            return fail_msg(msgtype, err)
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FACTION_ACCEPT_INVITE)
    @level_required(tag="union")
    def faction_accept_invite(self, msgtype, body):
        p = self.player
        if p.factionID:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FACTION_ALREADY_HAD_FACTION)
        if is_applied(p):
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_ALREADY_APPLYED)
        req = poem_pb.AcceptInvite()
        req.ParseFromString(body)
        try:
            faction = Faction.load(req.factionID)
        except EntityNotFoundError:
            safe_remove(self.player.inviteFactionSet, req.factionID)
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_NOT_THIS_FACTION)
        if req.isaccept:
            if not isrecommend(req.factionID):
                return fail_msg(
                    msgtype, msgTips.FAIL_MSG_FACTION_MEMBERS_LIMIT_EXCEED)
            join_faction(p.entityID, faction.factionID)
        else:
            safe_remove(self.player.inviteFactionSet, req.factionID)
            safe_remove(faction.inviteset, self.player.entityID)
        faction.save()
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FACTION_INVITED)
    @level_required(tag="union")
    def faction_invited(self, msgtype, body):
        rsp = poem_pb.FactionInfos()
        missing = set()
        for factionID in self.player.inviteFactionSet:
            faction_info = get_faction_info(factionID)
            if not faction_info:  # 帮派已经解散
                missing.add(factionID)
                continue
            rsp.infos.add(**faction_info)
        for each in missing:
            safe_remove(self.player.inviteFactionSet, each)
        self.player.save()
        self.player.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FACTION_KICK)
    @level_required(tag="union")
    def faction_kick(self, msgtype, body):
        factionID = self.player.factionID
        faction = Faction.simple_load(factionID, ['leaderID'])
        if self.player.entityID != faction.leaderID:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FACTION_PERMISSION_DENIED)
        req = poem_pb.KickMember()
        req.ParseFromString(body)
        err = proxy.kick_member(factionID, req.entityID)
        if err:
            return fail_msg(msgtype, err)
        else:  # 加入推荐列表
            recommend(factionID)
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FACTION_ALTER_NAME)
    @level_required(tag="union")
    def faction_alter_name(self, msgtype, body):
        p = self.player
        factionID = self.player.factionID
        if not factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        faction = Faction.simple_load(factionID, ['leaderID', 'name'])
        if self.player.entityID != faction.leaderID:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_PERMISSION_DENIED)
        req = poem_pb.AlterNameFaction()
        req.ParseFromString(body)
        cost = get_cons_value("FactionAlterNameGold")
        if p.gold < cost:
            return fail_msg(msgtype, reason="钻石不足")
        name, err = validate_name(req.name)
        if err:
            return fail_msg(msgtype, err)
        try:
            FactionnameIndexing.register(factionID, req.name)
        except DuplicateIndexException:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_DUPLICATE_FACTION_NAME)
        FactionnameIndexing.unregister(faction.name)
        apply_reward(
            p, {}, cost={"gold": cost},
            type=RewardType.FactionAlterName)
        faction.name = req.name
        p.save()
        p.sync()
        faction.save()
        notify_change(factionID)
        gm_logger.info({'faction': {
            'entityID': p.entityID, 'type': 'altername_faction',
            'factionName': faction.name, 'factionID': faction.factionID,
        }})
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FACTION_ALTER_MODE)
    @level_required(tag="union")
    def faction_alter_mode(self, msgtype, body):
        req = poem_pb.AlterModeFactionRequest()
        req.ParseFromString(body)
        factionID = self.player.factionID
        if not factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        faction = Faction.simple_load(factionID, ['leaderID', 'mode'])
        if self.player.entityID != faction.leaderID:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_PERMISSION_DENIED)
        if req.mode not in (poem_pb.Check, poem_pb.Free, poem_pb.Deny):
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        faction.mode = req.mode
        faction.save()
        rsp = poem_pb.AlterModeFaction(mode=faction.mode)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FACTION_ALTER_NOTICE)
    @level_required(tag="union")
    def faction_alter_notice(self, msgtype, body):
        factionID = self.player.factionID
        if not factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        faction = Faction.simple_load(factionID, ['notice', 'leaderID'])
        if self.player.entityID != faction.leaderID:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FACTION_PERMISSION_DENIED)
        req = poem_pb.AlterNoticeFaction()
        req.ParseFromString(body)
        notice = trie.trie_replace(dirty_words_trie, req.notice, u'*')
        faction.notice = notice
        faction.save()
        rsp = poem_pb.AlterNoticeFaction(notice=notice)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FACTION_DISMISS)
    @level_required(tag="union")
    def faction_dismiss(self, msgtype, body):
        player = self.player
        factionID = player.factionID
        faction = Faction.simple_load(
            factionID, [
                'leaderID', 'name', 'memberset', 'dflag'])
        if player.entityID != faction.leaderID:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_PERMISSION_DENIED)
        if len(faction.memberset) > 1:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_CAN_NOT_DISMISS)
        faction.dflag = True
        faction.save()
        unrecommend(factionID)
        player.dismissCD = int(time.time()) + DISMISSFACTIONCD
        player.save()
        player.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FACTION_CANCEL_DISMISS)
    @level_required(tag="union")
    def faction_cancel_dismiss(self, msgtype, body):
        player = self.player
        factionID = player.factionID
        faction = Faction.simple_load(factionID, ['leaderID', 'dflag'])
        if player.entityID != faction.leaderID:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_PERMISSION_DENIED)
        faction.dflag = False
        faction.save()
        recommend(factionID)
        player.dismissCD = 0
        player.save()
        player.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FACTION_THRONE)
    @level_required(tag="union")
    def faction_throne(self, msgtype, body):
        p = self.player
        factionID = self.player.factionID
        faction = Faction.simple_load(factionID, ['leaderID'])
        if self.player.entityID != faction.leaderID:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_PERMISSION_DENIED)
        req = poem_pb.ThroneMember()
        req.ParseFromString(body)
        if req.entityID == faction.leaderID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_ALREADY_LEADER)
        err = proxy.throne_member(factionID, req.entityID)
        if err:
            return fail_msg(msgtype, err)
        p.faction_is_leader = False
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FACTION_QUIT)
    @level_required(tag="union")
    def faction_quit(self, msgtype, body):
        p = self.player
        factionID = p.factionID
        if not factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        now = int(time.time())
        if p.joinFactionTime and (
                now - p.joinFactionTime) < QUITFACTIONCD:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_CAN_NOT_LEAVE)
        faction = Faction.simple_load(factionID, ['memberset', 'leaderID'])
        if faction.leaderID == p.entityID:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FACTION_LEADER_CAN_NOT_QUIT)
        if p.entityID not in faction.memberset:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FACTION_IS_NOT_IN_FACTION)
        clean_faction(p.entityID)
        recommend(factionID)
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FACTION_MEMBER_DETAIL)
    @level_required(tag="union")
    def faction_member_detail(self, msgtype, body):
        req = poem_pb.RequestMemberDetail()
        req.ParseFromString(body)
        from pvp.manager import get_opponent_detail
        d = get_opponent_detail(req.entityID)
        rsp = poem_pb.TargetDetailResponse(**d)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FACTION_REVIEW)
    @level_required(tag="union")
    def faction_review(self, msgtype, body):
        factionID = self.player.factionID
        fs = Faction.expend_fields(['level', 'memberset', 'leaderID', 'dflag'])
        faction = Faction.simple_load(factionID, fs)
        if self.player.entityID != faction.leaderID:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_PERMISSION_DENIED)
        req = poem_pb.ReviewMember()
        req.ParseFromString(body)
        if req.isallow:
            if faction.dflag:
                return fail_msg(
                    msgtype,
                    msgTips.FAIL_MSG_FACTION_CAN_NOT_ALLOW_JOIN_WILL_DISMISS_FACTION)  # NOQA
            err = proxy.allow_apply(factionID, req.entityID)
            if err == msgTips.FAIL_MSG_FACTION_ALREADY_CANCEL_APPLY:
                recommend(factionID)
        else:
            err = proxy.deny_apply(factionID, req.entityID)
        if not err:
            return success_msg(msgtype, '')
        return fail_msg(msgtype, err)

    @rpcmethod(msgid.FACTION_DONATE)
    @level_required(tag="union")
    def faction_donate(self, msgtype, body):
        p = self.player
        if not p.factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        if p.todayfp_donate >= p.todayfp_donate_max:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FACTION_EXCEED_DAILY_DONATE_LIMIT)
        req = poem_pb.FactionDonate()
        req.ParseFromString(body)
        config = get_config(FactionDonateConfig)[1]
        fp = req.gold / config.arg1 * config.arg2
        if req.gold < config.arg1 or \
                req.gold % 10 != 0 or \
                (p.todayfp_donate + fp) > p.todayfp_donate_max:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FACTION_DONATE_AMOUNT_INVALID)
        try:
            cc = get_config(FactionDonateConfig)[3]
            apply_reward(
                p, {'fp': fp / cc.arg1 * cc.arg2},
                cost={'gold': req.gold},
                type=RewardType.DonateFaction)
        except AttrNotEnoughError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_NOT_ENOUGH_GOLD)
        totalfp = Faction.incr_attribute(p.factionID, 'totalfp', fp)
        p.totalfp += fp
        p.todayfp_donate += fp
        p.save()
        p.sync()
        rsp = poem_pb.FactionDonateResponse()
        rsp.totalfp = totalfp
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FACTION_LEVEL_REWARD)
    @level_required(tag="union")
    def faction_level_reward(self, msgtype, body):
        p = self.player
        req = poem_pb.LevelReward()
        req.ParseFromString(body)
        config = get_config(FactionLevelRewardConfig).get(req.level)
        if not config:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        rsp = poem_pb.LevelRewardResponse()
        for i, _ in enumerate(config.types):
            rsp.rewards.add(
                type=config.types[i],
                arg=config.itemIDs[i],
                count=config.amounts[i])
        level = rsp.level = req.level
        if level == p.faction_level:
            rsp.can_recv = not p.faction_level_rewards_received
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FACTION_RECV_LEVEL_REWARD)
    @level_required(tag="union")
    def faction_recv_level_reward(self, msgtype, body):
        p = self.player
        req = poem_pb.RecvLevelReward()
        req.ParseFromString(body)
        config = get_config(FactionLevelRewardConfig).get(req.level)
        if not config:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if req.level != p.faction_level:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if p.faction_level_rewards_received:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        rewards = []
        for i, _ in enumerate(config.types):
            rewards.append(poem_pb.RewardData(
                type=config.types[i],
                arg=config.itemIDs[i],
                count=config.amounts[i]))
        rewards = parse_reward(rewards)
        apply_reward(p, rewards, type=RewardType.FactionLevelReward)
        p.faction_level_rewards_received.add(req.level)
        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FACTION_LEVELUP)
    @level_required(tag="union")
    def faction_levelup(self, msgtype, body):
        '''只有会长能操作'''
        player = self.player
        factionID = player.factionID
        if not factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        faction = Faction.simple_load(factionID, ['leaderID'])
        if player.entityID != faction.leaderID:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_PERMISSION_DENIED)
        level = FactionRankRanking.get_score(factionID) or 0
        configs = get_config(FactionLimitConfig)
        config = configs.get((level or 1) + 1)
        if not config:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_MAX_LEVEL)
        faction = Faction.load(factionID)
        if faction.totalfp < config.exp:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_NOT_ENOUGH_TOTALFP)
        faction.incr('totalfp', -config.exp)
        faction.save()
        if not level:
            incr = 2
        else:
            incr = 1
        rs = FactionRankRanking.incr_score(factionID, incr)
        limit1 = get_config(FactionLimitConfig)[level or 1]
        limit2 = get_config(FactionLimitConfig).get((level or 1) + 1)
        if limit2 and limit2.limit > limit1.limit:
            recommend(factionID)
        player.save()
        player.sync()
        notify_change(factionID)
        gm_logger.info({'faction': {
            'entityID': player.entityID, 'type': 'levelup_faction',
            'factionLevel': rs, 'factionID': faction.factionID,
        }})
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FACTION_RESEARCH)
    @level_required(tag="union")
    def faction_research(self, msgtype, body):
        '''只有会长能操作'''
        player = self.player
        factionID = player.factionID
        if not factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        faction = Faction.simple_load(factionID, ['leaderID'])
        if player.entityID != faction.leaderID:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_PERMISSION_DENIED)
        level = FactionRankRanking.get_score(factionID) or 1
        faction = Faction.load(factionID)
        req = poem_pb.FactionResearchOrLearn()
        req.ParseFromString(body)
        prefix = {
            poem_pb.FactionStrengthen.hp: 'strengthen_hp',
            poem_pb.FactionStrengthen.at: 'strengthen_at',
            poem_pb.FactionStrengthen.ct: 'strengthen_ct',
            poem_pb.FactionStrengthen.df: 'strengthen_df',
        }[req.type]
        k = prefix + '_level'
        slevel = getattr(faction, k, 0)
        if slevel >= level:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_MAX_LEVEL)
        configs = get_config(FactionStrengthenConfig)
        config = configs.get(slevel + 1)
        if not config:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_MAX_LEVEL)
        if faction.totalfp < config.cost:
            return fail_msg(
                msgtype,
                msgTips.FAIL_MSG_FACTION_NOT_ENOUGH_TOTALFP)
        faction.totalfp -= config.cost
        setattr(faction, k, slevel + 1)
        faction.save()
        FactionSkillRanking.incr_score(faction.factionID, 1)
        notify_strengthen_change(factionID)
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FACTION_LEARN)
    @level_required(tag="union")
    def faction_learn(self, msgtype, body):
        player = self.player
        factionID = player.factionID
        if not factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        req = poem_pb.FactionResearchOrLearn()
        req.ParseFromString(body)
        prefix = {
            poem_pb.FactionStrengthen.hp: 'strengthen_hp',
            poem_pb.FactionStrengthen.at: 'strengthen_at',
            poem_pb.FactionStrengthen.ct: 'strengthen_ct',
            poem_pb.FactionStrengthen.df: 'strengthen_df',
        }[req.type]
        k = prefix + '_level'
        level = getattr(player, k, 0)
        configs = get_config(FactionStrengthenConfig)
        config = configs.get(level + 1)
        if not config:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_MAX_LEVEL)
        slevel = getattr(Faction.simple_load(factionID, [k]), k, 0)
        if level >= slevel:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_MAX_LEVEL)
        try:
            apply_reward(
                player,
                {},
                cost={
                    'fp': config.learn_cost},
                type=RewardType.LearnFaction)
        except AttrNotEnoughError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_NOT_ENOUGH_FP)
        max_k = prefix + '_max_level'
        to_level = level + 1
        if to_level > getattr(player, max_k, 0):
            setattr(player, max_k, to_level)
        setattr(player, k, to_level)
        player.save()
        player.sync()
        player.clear_faction_power()
        # player.update_power()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FACTION_DONATE_INFO)
    @level_required(tag="union")
    def faction_donate_info(self, msgtype, body):
        player = self.player
        factionID = player.factionID
        if not factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        configs = get_config(FactionDonateConfig)
        return success_msg(msgtype, poem_pb.DonateInfo(
            gold=configs[1].arg1, gold2point=configs[1].arg2,
            money=configs[2].arg1, money2point=configs[2].arg2,
            point=configs[3].arg1, point2fp=configs[3].arg2,
        ))

    @rpcmethod(msgid.FACTION_ACCEPT_TASK)
    @level_required(tag="union")
    def faction_accept_task(self, msgtype, body):
        p = self.player
        if not p.factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        if p.faction_task_done:
            return fail_msg(msgtype, reason="今日公会任务已完成")
        if p.faction_taskID:
            return fail_msg(msgtype, reason="今日公会任务已领取")
        refresh_faction_task(p)
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FACTION_UNLOCK_MALL_PRODUCT)
    @level_required(tag="union")
    def faction_unlock_mall_product(self, msgtype, body):
        p = self.player
        if not p.factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        faction = Faction.simple_load(
            p.factionID, ['mall_products', 'leaderID', 'totalfp'])
        if p.entityID != faction.leaderID:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FACTION_PERMISSION_DENIED)
        req = poem_pb.UnlockMallProduct()
        req.ParseFromString(body)
        if req.pos in faction.mall_products:
            return fail_msg(msgtype, reason="已经解锁了")
        config = get_config(FactionMallUnlockConfig).get(req.pos)
        if not config:
            return fail_msg(msgtype, reason="无效的位置")
        if faction.totalfp < config.cost:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FACTION_NOT_ENOUGH_TOTALFP)
        faction.totalfp -= config.cost
        faction.mall_products.add(req.pos)
        faction.save()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.CITY_DUNGEON_INFO)
    def city_dungeon_info(self, msgtype, body):
        info = g_cityDungeon.get_top_info() or {}
        rsp = poem_pb.CityDungeonInfo(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CITY_DUNGEON_PANEL)
    @level_required(tag="union")
    def city_dungeon_panel(self, msgtype, body):
        p = self.player
        if not p.factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        if not g_campaignManager.city_dungeon_campaign.is_open():
            return fail_msg(msgtype, msgTips.FAIL_MSG_CITY_CAMPAIGN_CLOSED)
        rsp = poem_pb.CityDungeonPanel()
        g_cityDungeon.get_panel(p, rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CITY_DUNGEON_START_FIGHT)
    @level_required(tag="union")
    def city_dungeon_start_fight(self, msgtype, body):
        p = self.player
        if not p.factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        if not g_campaignManager.city_dungeon_campaign.is_open():
            return fail_msg(msgtype, msgTips.FAIL_MSG_CITY_CAMPAIGN_CLOSED)
        # {{ 自动复活， 使用每日PVP的
        now = int(time.time())
        if (now > p.daily_dead_cd and p.daily_dead_resume < p.daily_dead_cd)\
                or not p.daily_dead_cd:
            lineup = p.lineups.get(LineupType.City, [])
            for each in lineup:
                pet = p.pets.get(each)
                if pet:
                    pet.daily_dead = False
                    pet.daily_restHP = 0
                    pet.save()
                    pet.sync()
            p.daily_dead_resume = now
            p.daily_dead_cd = now
        # }}
        p.save()
        p.sync()
        if now < p.daily_dead_cd:
            return fail_msg(msgtype, reason="你已经死亡")
        rsp = poem_pb.CityDungeonStartFightResponse()
        rsp.mg = g_cityDungeon.get_mg(p)
        rsp.verify_code = PlayerFightLock.lock(p.entityID, force=True)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CITY_DUNGEON_FINAL_FIGHT)
    @level_required(tag="union")
    def city_dungeon_final_fight(self, msgtype, body):
        p = self.player
        if not p.factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        if not g_campaignManager.city_dungeon_campaign.is_open():
            return fail_msg(msgtype, msgTips.FAIL_MSG_CITY_CAMPAIGN_CLOSED)
        req = poem_pb.CityDungeonFinalFightRequest()
        req.ParseFromString(body)
        rsp = poem_pb.CityDungeonFinalFightResponse()
        if not PlayerFightLock.unlock(p.entityID, req.verify_code):
            cached = get_cached_fight_response(p, req.verify_code)
            if cached is not None:
                rsp.ParseFromString(cached)
                return success_msg(msgtype, rsp)
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        g_cityDungeon.battle(p, req.fight, rsp)
        cache_fight_response(p, req.verify_code, rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CITY_DUNGEON_END_PANEL)
    @level_required(tag="union")
    def city_dungeon_end_panel(self, msgtype, body):
        p = self.player
        info = g_cityDungeon.get_top_info() or {}
        rsp = poem_pb.CityDungeonEndPanel(**info)
        rsp.self_rewards = build_reward(p.city_dungeon_rewards)
        rank = CityDungeonSelfBackupRanking.get_rank(p.entityID)
        rsp.faction_rank = CityDungeonKillBackupRanking.get_rank(p.factionID)
        configs = get_config(CityDungeonRewardConfig)
        config = None
        for c in configs.values():
            start, end = c.range
            if start:
                if start > rank:
                    continue
            if end:
                if end < rank:
                    continue
            config = c
        if config:
            rsp.faction_rewards = build_reward(parse_reward(config.rewards))
        p.city_dungeon_rewards.clear()
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CITY_CHEST_RECV)
    @level_required(tag="union")
    def city_treasure_recv(self, msgtype, body):
        if g_campaignManager.city_dungeon_campaign.is_open():
            return fail_msg(msgtype, reason="活动开启中")
        if g_campaignManager.city_contend_campaign.is_open():
            return fail_msg(msgtype, reason="活动开启中")
        p = self.player
        info = g_cityDungeon.get_top_info()
        top_factionID = info.get("top_factionID", 0)
        if not top_factionID:
            return fail_msg(msgtype, reason="还没有公会获得宝藏")
        if p.factionID != top_factionID:
            return fail_msg(msgtype, reason="您不属于这个公会")
        if p.city_treasure_recv_flag:
            return fail_msg(msgtype, reason="今天已经领取过了")
        f = Faction.simple_load(p.factionID, ["faction_treasure"])
        if not f.faction_treasure:
            return fail_msg(msgtype, reason="还没有公会获得宝藏")
        current = None
        configs = get_config(CityTreasureRecvConfig)
        for config in configs.values():
            if f.faction_treasure >= config.treasure_count:
                current = config
            else:
                break
        if not current:
            return fail_msg(msgtype, reason="没有奖励可以领取")
        result = apply_reward(
            p, parse_reward(current.rewards),
            type=RewardType.CityTreasure)
        rsp = poem_pb.CityTreasureRecv()
        build_reward_msg(rsp, result)
        p.city_treasure_recv_flag = True
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CITY_CONTEND_PANEL)
    @level_required(tag="union")
    def city_contend_panel(self, msgtype, body):
        p = self.player
        if not p.factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        if not g_campaignManager.city_contend_campaign.is_open():
            return fail_msg(msgtype, msgTips.FAIL_MSG_CITY_CAMPAIGN_CLOSED)
        rsp = poem_pb.CityContendPanel()
        g_cityContend.get_panel(p, rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CITY_CONTEND_DROP_EVENT)
    @level_required(tag="union")
    def city_contend_drop_event(self, msgtype, body):
        p = self.player
        if not p.factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        if not g_campaignManager.city_contend_campaign.is_open():
            return fail_msg(msgtype, msgTips.FAIL_MSG_CITY_CAMPAIGN_CLOSED)
        if not g_cityContend.check_event(p, CityContendEventType.Drop):
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        event = g_cityContend.get_current_step(p)
        if g_cityContend.is_top_faction(p.factionID):
            result = open_reward(
                RewardType.CityContend, event["argv"])
        else:
            result = open_reward(
                RewardType.CityContend, event["argv"])
        rewards = result.apply(p)
        rsp = poem_pb.CityContendDropEventResponse()
        combine_reward(rewards, {}, p.city_contend_rewards)
        rsp.rewards = build_reward(p.city_contend_rewards)
        p.city_contend_step += 1
        p.city_contend_total_step += 1
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CITY_CONTEND_END_EVENT)
    @level_required(tag="union")
    def city_contend_end_event(self, msgtype, body):
        p = self.player
        if not p.factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        if not g_campaignManager.city_contend_campaign.is_open():
            return fail_msg(msgtype, msgTips.FAIL_MSG_CITY_CAMPAIGN_CLOSED)
        if not g_cityContend.check_event(p, CityContendEventType.End):
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        if g_cityContend.is_top_faction(p.factionID):
            g_cityContend.end_defend_event(p)
        else:
            pass
        p.city_contend_step = 0
        p.city_contend_total_step += 1
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.CITY_CONTEND_START_FIGHT)
    @level_required(tag="union")
    def city_contend_start_fight(self, msgtype, body):
        p = self.player
        if not p.factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        if not g_campaignManager.city_contend_campaign.is_open():
            return fail_msg(msgtype, msgTips.FAIL_MSG_CITY_CAMPAIGN_CLOSED)
        # {{ 自动复活， 使用每日PVP的
        now = int(time.time())
        if (now > p.daily_dead_cd and p.daily_dead_resume < p.daily_dead_cd)\
                or not p.daily_dead_cd:
            lineup = p.lineups.get(LineupType.City, [])
            for each in lineup:
                pet = p.pets.get(each)
                if pet:
                    pet.daily_dead = False
                    pet.daily_restHP = 0
                    pet.save()
                    pet.sync()
            p.daily_dead_resume = now
            p.daily_dead_cd = now
        # }}
        p.save()
        p.sync()
        if now < p.daily_dead_cd:
            return fail_msg(msgtype, reason="你已经死亡")
        rsp = poem_pb.CityContendStartFightResponse()
        rsp.verify_code = PlayerFightLock.lock(p.entityID, force=True)
        rsp.target = g_cityContend.get_target(p)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CITY_CONTEND_FINAL_FIGHT)
    @level_required(tag="union")
    def city_contend_final_fight(self, msgtype, body):
        p = self.player
        if not p.factionID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_FACTION_HAS_NOT_FACTION)
        if not g_campaignManager.city_contend_campaign.is_open():
            return fail_msg(msgtype, msgTips.FAIL_MSG_CITY_CAMPAIGN_CLOSED)
        p = self.player
        req = poem_pb.CityContendFinalFightRequest()
        req.ParseFromString(body)
        rsp = poem_pb.CityContendFinalFightResponse()
        if not PlayerFightLock.unlock(p.entityID, req.verify_code):
            cached = get_cached_fight_response(p, req.verify_code)
            if cached is not None:
                rsp.ParseFromString(cached)
                return success_msg(msgtype, rsp)
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        g_cityContend.battle(p, req.fight, rsp)
        cache_fight_response(p, req.verify_code, rsp)
        p.city_contend_step += 1
        p.city_contend_total_step += 1
        p.city_contend_cache_target.clear()
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.CITY_CONTEND_END_PANEL)
    @level_required(tag="union")
    def city_contend_end_panel(self, msgtype, body):
        p = self.player
        rsp = poem_pb.CityContendEndPanel()
        g_cityContend.get_end_panel(p, rsp)
        rsp.self_treasure = p.city_contend_total_treasure_backup or\
            p.city_contend_total_treasure
        rsp.count = p.city_contend_count_backup or \
            p.city_contend_count
        f = Faction.simple_load(p.factionID, ["faction_treasure"])
        rsp.faction_treasure = f.faction_treasure
        p.city_contend_rewards.clear()
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)
