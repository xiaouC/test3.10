#!/usr/bin/env python
# coding=utf-8

import copy, json
import random
import time
from common import msgTips
from common.game_config import all_game_config
from player.manager import g_playerManager

from common.game_config import all_game_config

class GameManager(object):
    def __init__(self):
        self.min_id = 100000
        self.max_id = 999999
        self.all_rooms = {}

    def gen_new_room_id(self):
        while True:
            new_room_id = random.randint(self.min_id, self.max_id)
    
            if not self.all_rooms.has_key(new_room_id):
                break
    
        return new_room_id
        
    def create_room(self, player, game_id, game_settings):
        room_id = self.gen_new_room_id()
        eval('from game import %s as game_proxy'%all_game_config[self.game_id]['game_proxy'])
        new_game_proxy = game_proxy(room_id, player.entityID, game_id, game_settings)
        self.all_rooms[room_id] = new_game_proxy
        new_game_proxy.all_role_infos.append({
            'entityID': player.entityID,
            'username': player.username,
            'sex': player.sex,
            'offline': False,
            'is_ready': False,
            'server_index': 0,
            })
        return new_game_proxy

    def dismiss_room(self, player):
        room_obj = self.all_rooms[player.room_id]
        if not room_obj:
            return
        
        for role in room_obj.roles:
            if role.entityID == 0:
                continue

            p = g_entityManager.get_player(role.entityID)
            if not p:
                continue

            p.room_id = 0
            p.save()
            p.sync()

        del self.all_rooms[player.room_id]

    def get_room(self, room_id):
        return self.all_rooms[room_id]

g_gameManager = GameManager()
