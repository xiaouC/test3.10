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
        ms = g_chatManager.get_cache_messages(req.type, factionID=self.player.factionID, groupID=self.player.groupID)
        for m in ms:
            rsp.messages.append(m)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.GET_TIPS_MESSAGES)
    def get_tips_messages(self, msgtype, body):
        rsp = poem_pb.GetTipsMessagesResponse()
        ms = g_chatManager.get_tips_messages()
        for m in ms:
            rsp.messages.append(m)
        return success_msg(msgtype, rsp)
