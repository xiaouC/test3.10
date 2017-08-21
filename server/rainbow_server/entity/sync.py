#coding:utf-8
import logging
logger = logging.getLogger('property')

from utils import sync_property_msg
from player.manager import g_playerManager

def sync_player_property(player, all=False,syncSence=False,syncfields = set()):
    'sync player dirty fields'
    if all:
        fields = None
        player.pop_sync_dirty()
    elif syncfields:
        fields = player.remove_sync_dirty(syncfields)
    else:
        fields = player.pop_sync_dirty(syncSence)
        if not fields:
            #logger.error("Called sync_property, but nothing to sync!")
            return
    msg = sync_property_msg(player, fields, isme=True)
    g_playerManager.sendto(player.entityID, msg)

def broadcast_player_property(player):
    scene = player.scene or player.boss_scene
    if scene:
        scene.broadcast(player.entityID, sync_property_msg(player, ['modelID', 'name', 'quality']))
