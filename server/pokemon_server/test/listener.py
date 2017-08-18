#coding:utf-8
from gevent import getcurrent

from test.mockup import PlayerBase
from protocol import poem_pb
import protocol.poem_pb as msgid

listeners = {}

def listen(msgtype, klass=None):
    def _decorator(func):
        def _inner(self, body, *args):
            if klass:
                msg = klass()
                msg.ParseFromString(body)
            else:
                msg = body
            return func(self, msg, *args)
        listeners[msgtype] = _inner
        return _inner
    return _decorator

class Listener(object):

    def __init__(self):
        pass

    @listen(msgid.SYNC_PROPERTY, poem_pb.SyncProperty)
    def sync_property(self, rsp, player):
        if rsp.type == poem_pb.SyncProperty.Me:
            player.sync_property(rsp)
        elif rsp.type == poem_pb.SyncProperty.Pet:
            player.sync_pet_property(rsp)

    @listen(msgid.MULTI_SYNC_PROPERTY, poem_pb.MultiSyncProperty)
    def multi_sync_property(self, rsp, player):
        for each in rsp.entities:
            if each.type == poem_pb.SyncProperty.Pet:
                player.sync_pet_property(each)

    @listen(msgid.SCENE_INFOS, poem_pb.SceneInfos)
    def scene_infos(self, rsp, player):
        player.sync_scene_infos(rsp)

    @listen(msgid.LINEUP_LINEUPS, poem_pb.Lineups)
    def sync_lineups(self, rsp, player):
        player.sync_lineups(rsp)

    def listen(self, msgtype, msg):
        func = listeners.get(msgtype)
        if func:
            from test.utils import get_player, set_player
            player = get_player(getcurrent())
            if not player:
                player = PlayerBase()
                set_player(getcurrent(), player)
            return func(self, msg, player)

g_listener = Listener()
