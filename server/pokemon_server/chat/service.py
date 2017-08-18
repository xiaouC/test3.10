# coding:utf-8
from yy.utils import trie
from yy.rpc import RpcService, rpcmethod
from yy.message.header import fail_msg, success_msg
import protocol.poem_pb as msgid
from protocol import poem_pb
from .manager import g_chatManager
from .constants import ChatType
from config.configs import dirty_words_trie
from entity.manager import level_required
from common import msgTips
from protocol.poem_pb import Message


class ChatService(RpcService):

    @rpcmethod(msgid.GET_CACHE_MESSAGES)
    def get_cache_messages(self, msgtype, body):
        req = poem_pb.GetCacheMessagesRequest()
        req.ParseFromString(body)
        rsp = poem_pb.GetCacheMessagesResponse(type=req.type)
        ms = g_chatManager.get_cache_messages(
            req.type, factionID=self.player.factionID,
            groupID=self.player.groupID)
        for m in ms:
            rsp.messages.append(m)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.SEND_MESSAGE)
    @level_required(tag="chatroom")
    def send_message(self, msgtype, body):
        req = poem_pb.SendMessageRequest()
        req.ParseFromString(body)
        p = self.player
        if not g_chatManager.check_limited((p.entityID, req.type)):
            return fail_msg(
                msgtype,  msgTips.FAIL_MSG_CHAT_SPEAK_TOO_FREQUENTLY)
        if req.type == ChatType.Faction:
            if not p.factionID:
                return fail_msg(msgtype, reason="未加入公会")
        if req.type == ChatType.Group:
            if not p.groupID:
                return fail_msg(msgtype, reason="未加入同门")
        content = trie.trie_replace(dirty_words_trie, req.content, u'*')
        assert req.type in (ChatType.World, ChatType.Faction, ChatType.Group)

        if p.chat_blocked:
            m = Message(type=req.type,
                        content=content,
                        name=p.name,
                        entityID=p.entityID,
                        prototypeID=p.prototypeID,
                        is_faction_leader=p.faction_is_leader)
            return success_msg(msgid.RECV_MESSAGE, m)

        g_chatManager.send(
            req.type, content, p.name, p.entityID,
            prototypeID=p.prototypeID,
            is_faction_leader=p.faction_is_leader, borderID=p.borderID)
        return success_msg(msgtype, '')

    @rpcmethod(msgid.GET_TIPS_MESSAGES)
    def get_tips_messages(self, msgtype, body):
        rsp = poem_pb.GetTipsMessagesResponse()
        ms = g_chatManager.get_tips_messages()
        for m in ms:
            rsp.messages.append(m)
        return success_msg(msgtype, rsp)
