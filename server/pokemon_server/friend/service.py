# coding:utf-8
import time
import logging
logger = logging.getLogger("friend")
from protocol import poem_pb
import protocol.poem_pb as msgid

from yy.message.header import fail_msg
from yy.message.header import success_msg
from yy.rpc import RpcService, rpcmethod
from yy.utils import trie

from common import msgTips

from gm.proxy import proxy

from player.model import Player
from player.formulas import get_vip

from reward.manager import RewardType
from reward.manager import apply_reward
from reward.manager import build_reward_msg
from reward.manager import open_reward

from config.configs import get_config
from config.configs import FriendfbConfig
from config.configs import get_cons_value
from config.configs import FriendfbRewardByFbIDConfig
from config.configs import FriendfbRewardConfig
from config.configs import dirty_words_trie

from friend.manager import *  # NOQA

from player.model import PlayerFightLock
from faction.model import Faction

from entity.manager import level_required

from explore.boss import g_bossCampaignManager
from task.constants import TaskCond
from task.manager import on_friendfb_count
from chat.manager import g_chatManager
from chat.manager import ChatType


class FriendService(RpcService):

    @rpcmethod(msgid.LIST_FRIEND)
    @level_required(tag="friend")
    def friend_list(self, msgtype, body):
        p = self.player
        # 推荐好友
        if p.friend_count < p.friend_max_count:
            recommend(p.entityID)
        rsp = poem_pb.FriendList()
        fields = [
            'entityID', 'name',
            'prototypeID', 'level',
            'credits', 'lastlogin', "groupID", "borderID"]
        rs = Player.batch_load(list(p.friendset), fields)
        for each in rs:
            info = {}
            for f in fields:
                info[f] = getattr(each, f)
            info['id'] = info['entityID']
            if info['lastlogin']:
                info['time'] = time.mktime(
                    info['lastlogin'].timetuple())
            else:
                info['time'] = 0
            info['gifted'] = info['id'] in p.friendgiftedset
            info['vip'] = get_vip(info['credits'] or 0)
            info["messages_count"] = len(
                p.friend_messages.get(info['entityID'], []))
            rsp.friends.add(**info)
        logger.debug(rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.LIST_APPLYS)
    @level_required(tag="friend")
    def friend_applys(self, msgtype, body):
        p = self.player
        rsp = poem_pb.ApplysList()
        applys = p.friend_applys or {}
        fields = [
            'entityID', 'name',
            'prototypeID', 'level', 'credits', "borderID"]
        now = int(time.time())
        pending = []
        rs = Player.batch_load(applys.keys(), fields)
        for each in rs:
            info = {}
            applytime = applys.get(
                each.entityID, {}).get('applytime', 0)
            if applytime and now > applytime + FRIEND_APPLY_CD:
                pending.append(each.entityID)
                continue
            for f in fields:
                info[f] = getattr(each, f)
            info['id'] = info['entityID']
            info['time'] = applytime
            info['vip'] = get_vip(info['credits'] or 0)
            rsp.applys.add(**info)
        if pending:
            for i in pending:
                del p.friend_applys[i]
            p.save()
            p.sync()
        logger.debug(rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.LIST_RECOMMEND)
    @level_required(tag="friend")
    def friend_recommends(self, msgtype, body):
        p = self.player
        rsp = poem_pb.RecommendsList()
        recommends = getrecommends(p, count=10)
        fields = [
            'entityID', 'name',
            'prototypeID', 'level', 'credits',
            'friend_applys', 'lastlogin', "borderID"]
        rs = Player.batch_load(recommends, fields)
        for each in rs:
            if not each:
                continue
            each.friend_applys.load()
            if p.entityID in each.friend_applys:
                continue
            info = {}
            for f in fields:
                info[f] = getattr(each, f)
            info['id'] = info['entityID']
            info['vip'] = get_vip(info['credits'] or 0)
            if info['lastlogin']:
                info['time'] = int(time.mktime(info['lastlogin'].timetuple()))
            rsp.recommends.add(**info)
        logger.debug(rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.REMOVE_FRIEND)
    @level_required(tag="friend")
    def friend_remove(self, msgtype, body):
        p = self.player
        req = poem_pb.RemoveFriend()
        req.ParseFromString(body)
        # FIXME
        proxy.remove_friend(req.id, p.entityID)
        remove_friend(p.entityID, req.id)
        return success_msg(msgtype, "")

    @rpcmethod(msgid.APPLY_FRIEND)
    @level_required(tag="friend")
    def friend_apply(self, msgtype, body):
        p = self.player
        if p.friend_count >= p.friend_max_count:
            return fail_msg(msgtype, reason="好友已达上限")
        req = poem_pb.ApplyFriend()
        req.ParseFromString(body)
        logger.debug(req)
        if req.id == p.entityID:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FRIEND_CAN_NOT_APPLY_SELF)
        if req.id in p.friendset:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FRIEND_ALREADY_FIREND)
        if req.id in p.friend_applys:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FRIEND_ALREADY_APPLYED_YOU)
        error_code = proxy.apply_friend(req.id, p.entityID)
        if error_code:
            return fail_msg(msgtype, error_code)
        return success_msg(msgtype, "")

    @rpcmethod(msgid.ALLOW_FRIEND)
    @level_required(tag="friend")
    def friend_allow(self, msgtype, body):
        p = self.player
        if p.friend_count >= p.friend_max_count:
            return fail_msg(msgtype, reason="好友已达上限")
        req = poem_pb.AllowFriend()
        req.ParseFromString(body)
        # FIXME
        if not proxy.allow_friend(req.id, p.entityID):
            return fail_msg(msgtype, msgTips.FAIL_MSG_FRIEND_LIMITED_EXCEED)
        add_friend(p.entityID, req.id)
        from task.manager import on_friends_count
        on_friends_count(p)
        remove_apply_friend(p.entityID, req.id)
        return success_msg(msgtype, "")

    @rpcmethod(msgid.DENY_FRIEND)
    @level_required(tag="friend")
    def friend_deny(self, msgtype, body):
        p = self.player
        req = poem_pb.DenyFriend()
        req.ParseFromString(body)
        if deny_friend(req.id, p.entityID):
            remove_apply_friend(p.entityID, req.id)
        return success_msg(msgtype, "")

    @rpcmethod(msgid.GIFT_FRIEND)
    @level_required(tag="friend")
    def friend_gift(self, msgtype, body):
        p = self.player
        req = poem_pb.GiftFriend()
        req.ParseFromString(body)
        logger.debug(req)
        count = len(req.ids)
        if p.friend_gift_used_count + count > p.friend_gift_max_count:
            return fail_msg(msgtype, reason="次数不足，无法赠送能量")
        for i in req.ids:
            if i not in p.friendset:
                return fail_msg(msgtype, reason="该玩家还不是你的好友")
            if i in p.friendgiftedset:
                return fail_msg(msgtype, reason="已经给该玩家赠送过能量")
        sp = 1
        money = 1000
        rewards = {"sp": sp, "money": money}
        for i in req.ids:
            proxy.gift_friend(i, p.name, rewards)
            p.friend_gift_used_count += 1
            p.friendgiftedset.add(i)
        self_rewards = {
            "sp": sp * count,
            "money": money * count
        }
        apply_reward(
            p, self_rewards,
            type=RewardType.GiftFriend)
        p.save()
        p.sync()
        rsp = poem_pb.GiftFriendResponse(ids=req.ids)
        build_reward_msg(rsp, self_rewards)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.INVITE_FRIEND_LIST)
    @level_required(tag="friend")
    def friend_invite_list(self, msgtype, body):
        p = self.player
        if not p.factionID:
            return success_msg(msgtype, "")
        req = poem_pb.InviteFriendList()
        req.ParseFromString(body)
        logger.debug(req)
        try:
            ownerID, fbID = simple_load_friendfb(
                req.friendfbID, 'ownerID', 'fbID')
        except DoesNotExistsException:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FRIENDFB_ALREADY_DISAPPEARED)
        if p.entityID != ownerID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        invitees = load_friendfb_invitees(req.friendfbID)
        # invitees 起码会有发现者
        assert invitees, "impossible"
        fields = ['entityID', 'name', 'prototypeID', 'level', "borderID"]
        #  过滤已经邀请的好友(2016-02-18 改会公会成员)
        f = Faction.simple_load(p.factionID, ["memberset"])
        rs = Player.batch_load(list(set(f.memberset) - invitees), fields)
        rsp = poem_pb.InviteFriendListResponse()
        config = get_config(FriendfbConfig)[fbID]
        for each in rs:
            info = {}
            if each.level < config.openlv:
                continue
            for f in fields:
                info[f] = getattr(each, f)
            info['id'] = info['entityID']
            rsp.friends.add(**info)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.INVITE_FRIEND)
    @level_required(tag="friend")
    def friend_invite(self, msgtype, body):
        p = self.player
        req = poem_pb.InviteFriend()
        req.ParseFromString(body)
        try:
            ownerID, fbID, hp = simple_load_friendfb(
                req.friendfbID, 'ownerID', 'fbID', "hp")
            if hp <= 0:
                return fail_msg(
                    msgtype, msgTips.FAIL_MSG_FRIENDFB_ALREADY_DEAD)
        except DoesNotExistsException:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FRIENDFB_ALREADY_DISAPPEARED)
        config = get_config(FriendfbConfig)[fbID]
        # check friendfb
        if p.entityID != ownerID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        for id in req.ids:
            proxy.invite_friend(id, req.friendfbID, p.name, config.name)
        # if proxy.invite_friend(req.id, req.friendfbID, p.name, config.name):
        #     return fail_msg(msgtype, reason="已经邀请过该好友了")
        return success_msg(msgtype, '')

    @rpcmethod(msgid.FRIENDFB_LIST)
    @level_required(tag="friend")
    def friend_friendfb_list(self, msgtype, body):
        p = self.player
        rsp = poem_pb.FriendfbList()
        now = int(time.time())
        configs = get_config(FriendfbConfig)
        # {{ explore boss
        for campaign in g_bossCampaignManager.campaigns.values():
            from campaign.manager import g_campaignManager
            if campaign.config.ID == g_campaignManager.flower_boss_campaign.flower_boss_config_id:
                continue

            friendfbID = "bosscampaign:%d" % campaign.config.ID
            friendfb = load_friendfb(friendfbID)
            config = configs[campaign.config.fbID]
            friendfb.update(**config._asdict())
            if not campaign.is_open():  # 还未开启
                open_cd = campaign.config.start - now
                if open_cd < 0 or open_cd > 86400:
                    continue
                friendfb["open_cd"] = open_cd
            rsp.friendfbs.add(**friendfb)
        # }}
        pending = []
        for friendfbID in p.friendfb_list:
            if now > friendfbID2time(friendfbID) + FRIENDFB_INTERVAL:
                pending.append(friendfbID)
                continue
            friendfb = load_friendfb(friendfbID)
            if not friendfb:
                continue
            config = configs[friendfb['fbID']]
            friendfb.update(**config._asdict())
            if p.entityID in friendfb['activists']:
                friendfb['done'] = True
            rsp.friendfbs.add(**friendfb)
        if pending:
            for i in pending:
                p.friendfb_list.remove(i)
            p.save()
            p.sync()
        logger.debug(rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FRIENDFB_DETAIL)
    @level_required(tag="friend")
    def friend_friendfb_detail(self, msgtype, body):
        p = self.player
        req = poem_pb.FriendfbDetailRequest()
        req.ParseFromString(body)
        rsp = poem_pb.FriendfbDetail()
        friendfb = load_friendfb(req.friendfbID)
        logger.debug("detail %r", friendfb)
        if not friendfb:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FRIENDFB_ALREADY_DISAPPEARED)
        config = get_config(FriendfbConfig)[friendfb['fbID']]
        friendfb.update(**config._asdict())
        if p.entityID in friendfb['activists']:
            friendfb['done'] = True
        rsp.friendfb = poem_pb.Friendfb(**friendfb)
        rsp.rewards = config.rewards
        #  # 排行榜
        #  ranks = load_ranks(req.friendfbID)
        #  for rank in ranks:
        #      rsp.ranks.add(**rank)
        rsp.is_dead = player_is_dead(p, req.friendfbID)
        rsp.reborn_cost = (p.friendfb_reborn_counts.get(
            req.friendfbID, 0) + 1) * get_cons_value("FriendfbRebornCost")
        logger.debug(rsp)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.ENTER_FRIENDFB)
    @level_required(tag="friend")
    def friend_friendfb_enter(self, msgtype, body):
        p = self.player
        req = poem_pb.EnterFriendfb()
        req.ParseFromString(body)
        if not p.friendfb_remain_count:
            return fail_msg(msgtype, reason="挑战次数不足")
        if player_is_dead(p, req.friendfbID):
            return fail_msg(msgtype, reason="已经死亡")
        if not if_boss(req.friendfbID) and \
                req.friendfbID not in p.friendfb_list:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        try:
            createtime, maxhp, hp, fbID = simple_load_friendfb(
                req.friendfbID, 'createtime', 'maxhp', 'hp', 'fbID')
        except DoesNotExistsException:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FRIENDFB_ALREADY_DISAPPEARED)
        if hp <= 0:
            return fail_msg(msgtype, reason='BOSS已经被击杀了')
        now = int(time.time())
        if if_boss(req.friendfbID):
            if not if_boss_campaign_opened(req.friendfbID):
                return fail_msg(msgtype, reason='秘境已经消失')
            elif now > createtime + FRIENDFB_INTERVAL:
                return fail_msg(msgtype, reason='秘境已经消失')
        # activists = load_friendfb_activists(req.friendfbID)
        #  if p.entityID in activists:
        #      return fail_msg(msgtype, reason='已经挑战过了')
        if req.friendfbID not in p.friendfb_reborn_counts:
            p.friendfb_used_count += 1
        done_friendfb(req.friendfbID, p.entityID)
        info = get_config(FriendfbConfig)[fbID]
        rsp = poem_pb.EnterFriendfbResponse(
            maxhp=maxhp, hp=hp, bossID=info.bossID)
        rsp.verify_code = PlayerFightLock.lock(p.entityID, force=True)
        p.cache_friendfbID = req.friendfbID
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.END_FRIENDFB)
    @level_required(tag="friend")
    def friend_friendfb_end(self, msgtype, body):
        p = self.player
        req = poem_pb.EndFriendfb()
        req.ParseFromString(body)
        if not PlayerFightLock.unlock(p.entityID, req.verify_code):
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        assert p.cache_friendfbID, "impossible"
        rsp = poem_pb.EndFriendfbResponse()
        try:
            createtime, hp, fbID = simple_load_friendfb(
                p.cache_friendfbID, 'createtime', 'hp', 'fbID')
        except DoesNotExistsException:
            error_code = msgTips.FAIL_MSG_FRIENDFB_ALREADY_DISAPPEARED
        else:
            if hp <= 0:
                error_code = msgTips.FAIL_MSG_FRIENDFB_ALREADY_DEAD
                # return fail_msg(msgtype, reason='BOSS已经被击杀了')
            else:
                from pvp.manager import send_fight_verify
                from fightverifier.direct_verifier import verify
                send_fight_verify(p, req.fight)
                if not verify(p, req.fight):
                    return fail_msg(
                        msgtype, msgTips.FAIL_MSG_FIGHT_VERIFY_FAILED)
                error_code = 0
                now = int(time.time())
                if if_boss(p.cache_friendfbID) and\
                        not if_boss_campaign_opened(p.cache_friendfbID) or \
                        not if_boss(p.cache_friendfbID) and \
                        now > createtime + FRIENDFB_INTERVAL:
                    error_code = msgTips.FAIL_MSG_FRIENDFB_ALREADY_DISAPPEARED  # NOQA
                else:
                    info = get_config(FriendfbConfig)[fbID]
                    if info.drop:
                        r = open_reward(RewardType.Friendfb, info.drop)
                        result = r.apply(p)
                        build_reward_msg(rsp, result)
                    damage = max(req.fight.total_damage or 0, 0)
                    hp = hurt_boss(p, fbID, p.cache_friendfbID, damage)
                    if hp <= 0:
                        if if_boss(p.cache_friendfbID):
                            # 提前发奖
                            bc = get_boss_campaign(p.cache_friendfbID)
                            proxy.notify_boss_campaign_end(bc.config.ID)
                            entityID = bc.get_by_rank(1)
                            proxy.sync_on_task_change(
                                entityID,
                                TaskCond.FriendfbFirst,
                                p.cache_friendfbID)
                        else:
                            give_reward(p.cache_friendfbID)
                        on_friendfb_count(p, fbID)
                    else:
                        p.friendfb_deads.add(p.cache_friendfbID)
                        p.friendfb_deadtimes[fbID] = now
        p.friendfb_buff = 0
        p.save()
        p.sync()
        rsp.error_code = error_code
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.REBORN_FRIENDFB)
    def friend_friendfb_reborn(self, msgtype, body):
        req = poem_pb.RebornFriendfb()
        req.ParseFromString(body)
        p = self.player
        try:
            hp, fbID = simple_load_friendfb(
                req.friendfbID, 'hp', 'fbID')
        except DoesNotExistsException:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FRIENDFB_ALREADY_DISAPPEARED)
        if hp <= 0:
            return fail_msg(msgtype, reason='BOSS已经被击杀了')
        if not player_is_dead(p, req.friendfbID):
            return fail_msg(msgtype, reason="无须复活")
        count = p.friendfb_reborn_counts[req.friendfbID] =\
            p.friendfb_reborn_counts.get(req.friendfbID, 0) + 1
        cost = get_cons_value("FriendfbRebornCost") * count
        try:
            apply_reward(
                p, {}, cost={"gold": cost},
                type=RewardType.FriendfbReborn)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="钻石不足")
        p.friendfb_deads.remove(req.friendfbID)
        if fbID in p.friendfb_deadtimes:
            del p.friendfb_deadtimes[fbID]
        p.friendfb_buff = get_cons_value("GveBuffAddition")
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.FRIENDFB_RANKING_REWARD)
    def friendfb_ranking_reward(self, msgtype, body):
        p = self.player
        req = poem_pb.RankingFriendfb()
        req.ParseFromString(body)
        ownerID, fbID = simple_load_friendfb(
            req.friendfbID, 'ownerID', 'fbID')
        group = get_config(FriendfbRewardByFbIDConfig).get(fbID, [])
        configs = get_config(FriendfbRewardConfig)
        rsp = poem_pb.FriendfbRewardRanking()
        # 排行榜
        ranks = load_ranks(req.friendfbID)
        for index, rank in enumerate(ranks, 1):
            rank["rank"] = index
            if p.entityID == rank["entityID"]:
                rsp.self = rank
            rsp.ranks.add(**rank)
        if not rsp.self or (hasattr(
                rsp.self, "todict") and not rsp.self.todict()):
            rsp.self = load_rank(req.friendfbID, p.entityID)
        for config in group:
            config = configs[config.ID]
            start, final = config.range
            rsp.items.add(
                rewards=config.rewards,
                start=start, final=final)
        rsp.maxdamage = p.friendfb_damages.get(fbID, 0)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.LISTEN_FRIEND)
    def listen_friend(self, msgtype, body):
        p = self.player
        req = poem_pb.ListenFriend()
        req.ParseFromString(body)
        if req.friendID not in p.friendset:
            return fail_msg(msgtype, msgid.FAIL_MSG_INVALID_REQUEST)
        listen(p.entityID, req.friendID)
        messages = p.friend_messages.get(req.friendID, [])
        try:
            del p.friend_messages[req.friendID]
        except KeyError:
            pass
        rsp = poem_pb.FriendMessages()
        for message in messages:
            rsp.messages.add(**message)
            rsp.senderID = req.friendID
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.UNLISTEN_FRIEND)
    def unlisten_friend(self, msgtype, body):
        p = self.player
        unlisten(p.entityID)
        return success_msg(msgtype, '')

    @rpcmethod(msgid.CHAT_FRIEND)
    def chat_friend(self, msgtype, body):
        p = self.player
        req = poem_pb.ChatFriend()
        req.ParseFromString(body)
        if not g_chatManager.check_limited((p.entityID, ChatType.World)):
            return fail_msg(
                msgtype,  msgTips.FAIL_MSG_FRIEND_CHAT_SPEAK_TOO_FREQUENTLY)
        content = trie.trie_replace(dirty_words_trie, req.content, u'*')
        proxy.send_friend_message(
            req.friendID, content, p.entityID)
        rsp = poem_pb.FriendMessage(
            time=time.time(),
            content=content,
        )
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FLOWER_BOSS_ENTER_FB)
    def flowerboss_friendfb_enter(self, msgtype, body):
        p = self.player
        req = poem_pb.EnterFriendfb()
        req.ParseFromString(body)

        from campaign.manager import g_campaignManager
        flower_boss_friendfbID = "bosscampaign:%d" % g_campaignManager.flower_boss_campaign.flower_boss_config_id
        if req.friendfbID != flower_boss_friendfbID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)

        if player_is_dead(p, req.friendfbID):
            return fail_msg(msgtype, reason="已经死亡")
        if not if_boss(req.friendfbID) and \
                req.friendfbID not in p.friendfb_list:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        try:
            createtime, maxhp, hp, fbID = simple_load_friendfb(
                req.friendfbID, 'createtime', 'maxhp', 'hp', 'fbID')
        except DoesNotExistsException:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FRIENDFB_ALREADY_DISAPPEARED)
        if hp <= 0:
            return fail_msg(msgtype, reason='BOSS已经被击杀了')
        now = int(time.time())
        if if_boss(req.friendfbID):
            if not if_boss_campaign_opened(req.friendfbID):
                return fail_msg(msgtype, reason='秘境已经消失')
            elif now > createtime + FRIENDFB_INTERVAL:
                return fail_msg(msgtype, reason='秘境已经消失')
        # activists = load_friendfb_activists(req.friendfbID)
        #  if p.entityID in activists:
        #      return fail_msg(msgtype, reason='已经挑战过了')
        if req.friendfbID not in p.friendfb_reborn_counts:
            p.friendfb_used_count += 1
        done_friendfb(req.friendfbID, p.entityID)
        info = get_config(FriendfbConfig)[fbID]
        rsp = poem_pb.EnterFriendfbResponse(
            maxhp=maxhp, hp=hp, bossID=info.bossID)
        rsp.verify_code = PlayerFightLock.lock(p.entityID, force=True)
        p.cache_friendfbID = req.friendfbID
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FLOWER_BOSS_END_FB)
    def flowerboss_friendfb_end(self, msgtype, body):
        p = self.player
        req = poem_pb.EndFriendfb()
        req.ParseFromString(body)
        if not PlayerFightLock.unlock(p.entityID, req.verify_code):
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        assert p.cache_friendfbID, "impossible"

        from campaign.manager import g_campaignManager
        flower_boss_friendfbID = "bosscampaign:%d" % g_campaignManager.flower_boss_campaign.flower_boss_config_id
        if p.cache_friendfbID != flower_boss_friendfbID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)

        rsp = poem_pb.EndFriendfbResponse()
        try:
            createtime, hp, fbID = simple_load_friendfb(
                p.cache_friendfbID, 'createtime', 'hp', 'fbID')
        except DoesNotExistsException:
            error_code = msgTips.FAIL_MSG_FRIENDFB_ALREADY_DISAPPEARED
        else:
            if hp <= 0:
                error_code = msgTips.FAIL_MSG_FRIENDFB_ALREADY_DEAD
                # return fail_msg(msgtype, reason='BOSS已经被击杀了')
            else:
                from pvp.manager import send_fight_verify
                from fightverifier.direct_verifier import verify
                send_fight_verify(p, req.fight)
                if not verify(p, req.fight):
                    return fail_msg(
                        msgtype, msgTips.FAIL_MSG_FIGHT_VERIFY_FAILED)
                error_code = 0
                now = int(time.time())
                if if_boss(p.cache_friendfbID) and\
                        not if_boss_campaign_opened(p.cache_friendfbID) or \
                        not if_boss(p.cache_friendfbID) and \
                        now > createtime + FRIENDFB_INTERVAL:
                    error_code = msgTips.FAIL_MSG_FRIENDFB_ALREADY_DISAPPEARED  # NOQA
                else:
                    damage = max(req.fight.total_damage or 0, 0)

                    info = get_config(FriendfbConfig)[fbID]
                    if info.drop:
                        from config.configs import HandselMulRewardConfig
                        mr_configs = get_config(HandselMulRewardConfig)
                        mr_id = g_campaignManager.flower_boss_campaign.get_mulreward_id()
                        mr_config = mr_configs[mr_id]
                        mr = mr_config.mulreward

                        import math
                        r = open_reward(RewardType.Flower315Campaign, info.drop, int(math.ceil(mr * damage)))
                        result = r.apply(p)
                        build_reward_msg(rsp, result)

                        start_time, end_time = g_campaignManager.flower_boss_campaign.get_current_time()
                        if p.flower_boss_campaign_last_time < start_time or p.flower_boss_campaign_last_time > end_time:
                            p.flower_boss_campaign_total_hurt = 0
                        p.flower_boss_campaign_total_hurt += damage
                        p.flower_boss_campaign_last_time = now

                    hp = hurt_boss(p, fbID, p.cache_friendfbID, damage)
                    if hp <= 0:
                        if if_boss(p.cache_friendfbID):
                            # 提前发奖
                            bc = get_boss_campaign(p.cache_friendfbID)
                            proxy.notify_boss_campaign_end(bc.config.ID)
                            entityID = bc.get_by_rank(1)
                            proxy.sync_on_task_change(
                                entityID,
                                TaskCond.FriendfbFirst,
                                p.cache_friendfbID)
                        else:
                            give_reward(p.cache_friendfbID)
                        on_friendfb_count(p, fbID)
                    else:
                        p.friendfb_deads.add(p.cache_friendfbID)
                        p.friendfb_deadtimes[fbID] = now
        p.friendfb_buff = 0
        p.save()
        p.sync()
        rsp.error_code = error_code
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.FLOWER_BOSS_REBORN)
    def flowerboss_friendfb_reborn(self, msgtype, body):
        req = poem_pb.RebornFriendfb()
        req.ParseFromString(body)
        p = self.player
        try:
            hp, fbID = simple_load_friendfb(
                req.friendfbID, 'hp', 'fbID')
        except DoesNotExistsException:
            return fail_msg(
                msgtype, msgTips.FAIL_MSG_FRIENDFB_ALREADY_DISAPPEARED)
        if hp <= 0:
            return fail_msg(msgtype, reason='BOSS已经被击杀了')
        if not player_is_dead(p, req.friendfbID):
            return fail_msg(msgtype, reason="无须复活")
        count = p.friendfb_reborn_counts[req.friendfbID] =\
            p.friendfb_reborn_counts.get(req.friendfbID, 0) + 1
        cost = get_cons_value("FlowerBossRebornCost") * count
        try:
            apply_reward(
                p, {}, cost={"gold": cost},
                type=RewardType.FriendfbReborn)
        except AttrNotEnoughError:
            return fail_msg(msgtype, reason="钻石不足")
        p.friendfb_deads.remove(req.friendfbID)
        if fbID in p.friendfb_deadtimes:
            del p.friendfb_deadtimes[fbID]
        p.friendfb_buff = get_cons_value("GveBuffAddition")
        p.save()
        p.sync()
        return success_msg(msgtype, "")
