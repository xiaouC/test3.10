#!/usr/bin/env python
# coding=utf-8

import time
from common.game_config import all_game_config
from game.new_manager import g_gameManager

# game_config
# '100001': {
#     'game_proxy': '',
#     'expire': 3 * 60 * 60,
#     'min_player_count': 2,
#     'max_player_count': 4,
#     'ghost_card_num': 1,
#     'has_wan': False,
#     'has_tiao': True,
#     'has_tong': True,
#     'has_wind': True,
#     'has_arrow': True,
#     'has_flower': False,
#     'allow_sequence': False,
#     'allow_triplet': True,
#     'allow_kong': True,
# }

# role = {
#     'entityID': player.entityID,
#     'username': player.username,
#     'sex': player.sex,
#     'offline': False,
#     'is_ready': False,
#     'server_index': -1,
# }

# game status : 'waiting', 'playing'

class RoomRoleSitDownIterator(object):
    def __init__(self, room_obj):
        self.room_obj = room_obj
        self.index = 0

    def __iter__(self):
        return self

    def next(self):
        role_info = self.get_next_valid_role()
        if not role_info:
            raise StopIteration()
        return role_info

    def get_next_valid_role(self):
        while self.index < len(self.room_obj.all_role_infos):
            role_info = self.room_obj.all_role_infos[self.index]
            self.index += 1
            if not role_info or role_info['entityID'] == 0 or role_info['server_index'] == -1:
                continue
            return role_info
        return None


class RoomRoleAllIterator(object):
    def __init__(self, room_obj):
        self.room_obj = room_obj
        self.index = 0

    def __iter__(self):
        return self

    def next(self):
        role_info = self.get_next_valid_role()
        if not role_info:
            raise StopIteration()
        return role_info

    def get_next_valid_role(self):
        while self.index < len(self.room_obj.all_role_infos):
            role_info = self.room_obj.all_role_infos[self.index]
            self.index += 1
            if not role_info or role_info['entityID'] == 0:
                continue
            return role_info
        return None


class RoomBase(object):
    def __init__(self, room_id, entity_id, game_id, game_settings):
        self.room_id = room_id
        self.master_entity_id = entity_id
        self.game_id = game_id
        self.game_settings = game_settings
        self.create_time = time.time()
        self.all_role_infos = []
        self.game_config = copy.deepcopy(all_game_config[str(game_id)])
        self.game_config.update(json.loads(game_settings))
        self.apply_entityID = 0
        self.play_count = 0
        self.total_play_count = self.game_config['total_play_count']
        self.game_status = 'waiting'
        self.user_turn_index = 0

    def __del__(self):
        pass

    def has_player(self, entity_id):
        for role_info in self.all_role_infos:
            if entity_id == role_info['entityID']:
                return True
        return False

    def get_role_info(self, entity_id):
        for role_info in self.all_role_infos:
            if entity_id == role_info['entityID']:
                return role_info
        return None

    def get_role_info_by_server_index(self, server_index):
        for role_info in self.all_role_infos:
            if server_index == role_info['server_index']:
                return role_info
        return None

    def player_in(self, player):
        if self.has_player(self, player.entityID):
            return msgTips.PLAYER_ALREADY_IN

        if self.play_count > 0:
            return msgTips.GMAE_IS_STARTED

        for index, role_info in enumerate(self.all_role_infos):
            if role_info['entityID'] == 0:
                role_info'entityID'] = player.entityID
                role_info'username'] = player.username
                role_info'sex'] = player.sex
                role_info'offline'] = False
                role_info'is_ready'] = False
                role_info'server_index'] = -1

                return msgTips.SUCCESS

        self.all_role_infos.append({
            'entityID': player.entityID,
            'username': player.username,
            'sex': player.sex,
            'offline': False,
            'is_ready': False,
            'server_index': -1,
            })

        return msgTips.SUCCESS

    def player_out(self, player):
        role_info = self.get_role_info(player.entityID)
        if not role_info:
            return msgTips.PLAYER_NOT_FOUND

        role_info['entityID'] = 0
        role_info['server_index'] = -1
        return msgTips.SUCCESS

    def player_leave(self, player):
        role_info = self.get_role_info(player.entityID)
        if not role_info:
            return msgTips.PLAYER_NOT_FOUND

        role_info['offline'] = True
        if self.play_count == 0:
            role_info['server_index'] = -1

        return msgTips.SUCCESS

    def player_back(self, player):
        role_info = self.get_role_info(player.entityID)
        if not role_info:
            return msgTips.PLAYER_NOT_FOUND

        role_info['offline'] = False
        return msgTips.SUCCESS

    def player_kick_out(self, player, entity_id):
        if player.entityID != self.master_entity_id:
            return msgTips.KICK_OUT_NOT_MASTER

        role_info = self.get_role_info(entity_id)
        if not role_info:
            return msgTips.PLAYER_NOT_FOUND

        role_info['entityID'] = 0
        role_info['server_index'] = -1
        return msgTips.SUCCESS

    def player_sit_down(self, player, server_index):
        role_info = self.get_role_info(player.entityID)
        if not role_info:
            return msgTips.PLAYER_NOT_FOUND

        if self.get_role_info_by_server_index(server_index):
            return msgTips.SIT_DOWN_HAS_PLAYER

        if server_index < 0 or server_index >= self.game_config['max_player_count']:
            return msgTips.SIT_DOWN_POSITION_NOT_EXIST

        role_info['server_index'] = server_index
        return msgTips.SUCCESS

    def player_apply_dismiss(self, player):
        role_info = self.get_role_info(player.entityID)
        if not role_info:
            return msgTips.PLAYER_NOT_FOUND

        self.apply_entityID = player.entityID
        return msgTips.SUCCESS

    def player_dismiss_response(self, player, is_agree):
        pass

    def player_ready(self, player, is_ready):
        role_info = self.get_role_info(player.entityID)
        if not role_info:
            return msgTips.PLAYER_NOT_FOUND

        if role_info['server_index'] == -1:
            return msgTips.PLAYER_NOT_SIT_DOWN

        role_info['is_ready'] = is_ready

        if self.check_game_start():
            self.game_start()

        return msgTips.SUCCESS

    def check_game_start(self):
        counter = 0
        for role_info in RoomRoleSitDownIterator(self):
            if not role_info['is_ready']:
                return False
            ++counter
        return counter >= self.game_config['min_player_count']

    def player_reconn(self, player):
        role_info = self.get_role_info(player.entityID)
        if not role_info:
            role_info['offline'] = False

    def game_start(self):
        pass

    def get_next_user_turn(self, index):
        ++index
        if index >= self.game_config['max_player_count']:
            index = 0
        role_info = self.get_role_info_by_server_index(index)
        if not role_info:
            return self.get_next_user_turn(index)
        return index


