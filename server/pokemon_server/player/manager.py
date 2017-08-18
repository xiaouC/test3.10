# coding: utf-8
import logging
logger = logging.getLogger('player')

import gevent


class QuitPlayer(Exception):
    def __init__(self, entityID):
        self.entityID = entityID

    def __str__(self):
        return 'player quit %d' % self.entityID


class Peer(object):
    def __init__(self, sock):
        self.key = sock
        self._sock = sock

    def sender(self, msg):
        self._sock.async_send(msg)

    def close(self):
        self._sock.async_close()


class PlayerManager(object):
    def __init__(self):
        self.peers = {}
        self.recv_threads = {}

    def has_player(self, entityID):
        return entityID in self.peers

    def register(self, playerId, peer):
        self.peers[playerId] = peer
        self.recv_threads[playerId] = gevent.getcurrent()

    def close_player(self, playerId):
        self.peers.pop(playerId, None)
        self.recv_threads.pop(playerId, None)

    def kick_player(self, playerId):
        self.peers.pop(playerId)
        thread = self.recv_threads.pop(playerId)
        thread.kill(QuitPlayer(playerId), block=True, timeout=30)

    def broadcast(self, playerIds, msg):
        for playerId in playerIds:
            try:
                self.peers[playerId].sender(msg)
            except KeyError:
                # logger.error('not found player %d', playerId)
                pass

    def sendto(self, playerId, msg):
        try:
            self.peers[int(playerId)].sender(msg)
        except KeyError:
            # logger.error('not found player %s', playerId)
            pass

    def count(self):
        '''当前在线'''
        return len(self.peers)

g_playerManager = PlayerManager()
