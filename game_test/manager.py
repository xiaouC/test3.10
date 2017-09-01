#!/usr/bin/env python
# coding=utf-8

import copy, json
import random
import time
from common import msgTips
from common.game_config import all_game_config
from player.manager import g_playerManager

class Room(object):
    def __init__(self, room_id, entity_id, game_id, game_settings):
        self.room_id = room_id
        self.master_entity_id = entity_id
        self.master_server_index = 0
        self.game_id = game_id
        self.game_settings = game_settings
        self.create_time = time.time()
        self.roles = []
        self.game_config = copy.deepcopy(all_game_config[str(game_id)])
        self.game_config.update(json.loads(game_settings))
        self.apply_entityID = 0     # 申请解散的是谁
        self.play_count = 0         # 当前小局局数

    def __del__(self):
        self._game_proxy = None

    def has_player(self, entityID):
        for role in self.roles:
            if entityID == role['entityID']:
                return True

        return False

    def get_role(self, entityID):
        for role in self.roles:
            if entityID == role['entityID']:
                return role

        return None

    def get_roles_count(self):
        count = 0
        for role in self.roles:
            if role['entityID'] != 0:
                count = count + 1
        return count

    def broadcast(self, ignore_entity_id, msg):
        for role in self.roles:
            if role['entityID'] != 0 and not role['offline'] and role['entityID'] != ignore_entity_id:
                g_playerManager.sendto(role['entityID'], msg)

    def get_game_proxy(self):
        if not self._game_proxy:
            eval('from game import game_proxy_%d as game_proxy'%self.game_id)
            self._game_proxy = game_proxy(self)

    def game_start(self):
        self.get_game_proxy().start()

    @classmethod
    def from_info(cls, room_id, entity_id, game_id, game_settings):
        return cls(room_id, entity_id, game_id, game_settings)


class RoleIterator(object):
    def __init__(self, room_obj):
        self.room_obj = room_obj
        self.index = 0

    def __iter__(self):
        return self

    def next(self):
        role = self.get_next_valid_role()
        if not role:
            raise StopIteration()
        return role

    def get_next_valid_role(self):
        while self.index < len(self.room_obj.roles):
            role = self.room_obj.roles[self.index]
            self.index += 1

            if not role:
                continue

            if role['entityID'] == 0:
                continue

            return role
        return None


class RoomManager(object):
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
        room_obj = Room.from_info(room_id, player.entityID, game_id, game_settings)
        self.all_rooms[room_id] = room_obj
        room_obj.roles.append({
            'entityID': player.entityID,
            'username': player.username,
            'sex': player.sex,
            'offline': False,
            'is_ready': False,
            'pos_index': 0,
            })
        return room_obj

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

    def update_room(self, room_id, **info):
        pass

    def get_room(self, room_id):
        return self.all_rooms[room_id]

g_roomManager = RoomManager()
