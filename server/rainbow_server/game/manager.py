#!/usr/bin/env python
# coding=utf-8

import copy, json
from common import msgTips
from common.game_config import all_game_config

class Room(object):
    def __init__(self, room_id, entity_id, game_id, game_settings):
        self.id = room_id
        self.master_entity_id = entity_id
        self.create_time = time.time()
        self.roles = []
        self.game_config = copy.deepcopy(all_game_config[game_id])
        self.game_config.update(json.loads(game_settings))
        self.apply_entityID = 0     # 申请解散的是谁

    def has_player(self, entityID):
        for role in self.roles:
            if entityID == role.entityID:
                return True

        return False

    def get_role(self, entityID):
        for role in self.roles:
            if entityID == role.entityID:
                return role

        return None

    def get_roles_count(self):
        count = 0
        for role in self.roles:
            if role.entityID != 0:
                count = count + 1
        return count

    @classmethod
    def from_info(cls, room_id, entity_id, game_id, game_settings):
        return cls(room_id, entity_id, game_id, game_settings)


class RoomManager(Object):
    def __init__(self):
        self.min_id = 100000
        self.max_id = 999999
        self.all_rooms = {}

    def gen_new_room_id(self):
        pass

    def create_room(self, player, game_id, game_settings):
        room_id = self.gen_new_room_id()
        room_obj = Room.from_info(room_id, player.entityID, game_id, game_settings)
        self.all_rooms[room_id] = room_obj
        room_obj.roles.append({
            'entityID': player.entityID,
            'username': player.username,
            'sex': player.sex,
            'offline': False,
            })
        return room_obj

    def dismiss_room(self, player):
        del self.all_rooms[player.room_id]

    def update_room(self, room_id, **info):
        pass

    def get_room(self, room_id):
        return self.all_rooms[room_id]

g_roomManager = RoomManager()
