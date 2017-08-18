#coding:utf-8
import logging
logger = logging.getLogger('property')

from utils import sync_property_msg, multi_sync_property_msg
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

def sync_pet_property(pet, all=False):
    'sync pet dirty fields'

    from entity.manager import g_entityManager
    master = g_entityManager.get_player(pet.masterID)
    if pet.entityID not in master.pets:
        logger.debug('pet not in master')
        return

    if all:
        fields = None
        pet.pop_sync_dirty()
    else:
        fields = pet.pop_sync_dirty()
        if not fields:
            logger.error("Called sync_property, but nothing to sync!")
            return

    msg = sync_property_msg(pet, fields)
    g_playerManager.sendto(master.entityID, msg)

# def sync_pets_property(pets):
#     #全量同步
#     assert pets, 'not pets'
#     masterID = None
#     for pet in pets:
#         pet.pop_sync_dirty()
#         if masterID:
#             assert pet.masterID == masterID, 'pet not in master'
#         else:
#             masterID = pet.masterID
#     msg = multi_sync_property_msg(pets, None)
#     g_playerManager.sendto(masterID, msg)


def multi_sync_property(entities, masterID=None):
    for entity in entities:
        entity.pop_sync_dirty()
        if masterID:
            assert entity.masterID == masterID, 'entity not in master'
        else:
            masterID = entity.masterID
    if masterID:
        msg = multi_sync_property_msg(entities, None)
        g_playerManager.sendto(masterID, msg)
