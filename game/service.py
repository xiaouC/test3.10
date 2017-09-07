#!/usr/bin/env python
# coding=utf-8

import protocol.rainbow_pb as msgid
from protocol import rainbow_pb

from yy.rpc import RpcService, rpcmethod
from yy.message.header import success_msg, fail_msg

from game.manager import RoleIterator
from game.manager import g_gameManager
from entity.manager import g_entityManager
from player.manager import g_playerManager


# 
def room_required():
    def dec_func(func):
        def inner(self, msgtype, body):
            room_obj = g_gameManager.get_room(self.player.room_id)
            if not room_obj or not room_obj.has_player(self.player.entityID):
                self.player.room_id = 0
                self.player.save()
                self.player.sync()
                return fail_msg(msgtype, msgTips.FAIL_MSG_ROOM_NOT_EXIST)
            return func(self, msgtype, body)
        return inner
    return dec_func


# # 
# def room_sit_down_required():
#     def dec_func(func):
#         def inner(self, msgtype, body):
#             room_obj = g_gameManager.get_room(self.player.room_id)
#             is_valid = False
#             if room_obj:
#                 role_info = room_obj.get_role_info(self.player.entityID)
#                 if role_info and role_info['server_index'] != -1:
#                     is_valid = True
#             if not is_valid:
#                 self.player.room_id = 0
#                 self.player.save()
#                 self.player.sync()
#                 return fail_msg(msgtype, msgTips.FAIL_MSG_ROOM_NOT_EXIST)
#             return func(self, msgtype, body)
#         return inner
#     return dec_func
# 

#
def no_room_required():
    def dec_func(func):
        def inner(self, msgtype, body):
            if self.player.room_id != 0:
                room_obj = g_gameManager.get_room(self.player.room_id)
                if room_obj and room_obj.has_player(self.player.entityID):
                    return fail_msg(msgtype, msgTips.FAIL_MSG_ROOM_CREATE_HAS_ROOM)
            return func(self, msgtype, body)
        return inner
    return dec_func



class RoomService(RpcService):
    @rpcmethod(msgid.ROOM_CREATE)
    @no_room_required()
    def create_room(self, msgtype, body):
        req = rainbow_pb.CreateRoomRequest()
        req.ParseFromString(body)

        room_obj = g_gameManager.create_room(self.player, req.game_id, req.game_settings)

        self.player.room_id = room_obj.room_id
        self.player.save()
        self.player.sync()

        rsp = rainbow_pb.JoinRoomResponse()
        rsp.room_id = room_obj.room_id
        rsp.master_id = room_obj.master_entity_id
        rsp.master_server_index = room_obj.master_server_index
        rsp.server_index = 0
        rsp.game_id = room_obj.game_id
        rsp.game_settings = room_obj.game_settings
        rsp.play_count = room_obj.play_count
        rsp.min_player_count = room_obj.game_config['min_player_count']
        rsp.max_player_count = room_obj.game_config['max_player_count']
        for index, role in enumerate(room_obj.roles):
            if role['entityID'] != 0:
                rsp.users.add(**role)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.ROOM_USER_JOIN)
    @no_room_required()
    def join_room(self, msgtype, body):
        req = rainbow_pb.JoinRoomRequest()
        req.ParseFromString(body)

        room_obj = g_gameManager.get_room(req.room_id)
        if not room_obj:
            return fail_msg(msgtype, msgTips.FAIL_MSG_ROOM_NOT_EXIST)

        if room_obj.max_count <= len(room_obj.roles):
            return fail_msg(msgtype, msgTips.FAIL_MSG_ROOM_LIMIT_EXCEED)

        # 自动找个位置坐下
        pos_index = -1
        for index, role in enumerate(room_obj.roles):
            if role['entityID'] == 0:
                role['entityID'] = self.player.entityID
                role['username'] = self.player.username
                role['sex'] = self.player.sex
                role['offline'] = False
                role['is_ready'] = False
                role['pos_index'] = index

                pos_index = index

        if pos_index == -1:
            pos_index = len(room_obj.roles)

            room_obj.roles.append({
                'entityID': self.player.entityID,
                'username': self.player.username,
                'sex': self.player.sex,
                'offline': False,
                'is_ready': False,
                'pos_index': pos_index,
                })

        # 通知房间中的其他玩家，有人进来了
        rsp_user_info = rainbow_pb.RoomUserInfo()
        rsp_user_info.entityID = self.player.entityID
        rsp_user_info.username = self.player.username
        rsp_user_info.sex = self.player.sex
        rsp_user_info.offline = False
        rsp_user_info.pos_index = pos_index
        msg = success_msg(msgid.ROOM_USER_IN, rsp_user_info)
        for role in room_obj.roles:
            if role['entityID'] != 0 and not role['offline'] and role['entityID'] != self.player.entityID:
                g_playerManager.sendto(role['entityID'], msg)

        # 
        self.player.room_id = req.room_id
        self.player.save()
        self.player.sync()

        rsp = rainbow_pb.JoinRoomResponse()
        rsp.room_id = room_obj.room_id
        rsp.master_id = room_obj.master_entity_id
        rsp.master_server_index = room_obj.master_server_index
        rsp.game_id = room_obj.game_id
        rsp.game_settings = room_obj.game_settings
        rsp.play_count = room_obj.play_count
        rsp.min_player_count = room_obj.game_config['min_player_count']
        rsp.max_player_count = room_obj.game_config['max_player_count']
        for index, role in enumerate(room_obj.roles):
            if role['entityID'] != 0:
                rsp.users.add(**role)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.ROOM_USER_KICK_OUT)
    @room_required()
    def user_out(self, msgtype, body):
        req = rainbow_pb.KickOutRequest()
        req.ParseFromString(body)

        room_obj = g_gameManager.get_room(self.player.room_id)
        if room_obj.master_entity_id != self.player.entityID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_ROOM_KICK_OUT_PERMISSION_DENY)

        rsp = rainbow_pb.KickOutResponse()
        rsp.kick_out_id = req.kick_out_id
        msg = success_msg(msgtype, rsp)
        for role in room_obj.roles:
            if role['entityID'] == 0:
                continue

            p = g_entityManager.get_player(role['entityID'])
            if p:
                # 如果就是这个玩家被踢的话，清空一下数据
                if p.entityID == req.kick_out_id:
                    p.room_id = 0
                    p.save()
                    p.sync()

                # 发送踢人的消息
                if role['entityID'] != self.player.entityID:
                    g_playerManager.sendto(role['entityID'], msg)

            # 把这个位置空出来
            if role['entityID'] == req.kick_out_id:
                role['entityID'] = 0
                role['username'] = ''

        return msg

    @rpcmethod(msgid.ROOM_USER_BACK)
    @room_required()
    def user_back(self, msgtype, body):
        room_obj = g_gameManager.get_room(self.player.room_id)

        rsp_user_offline = rainbow_pb.UserOffline()
        rsp_user_offline.entityID = self.player.entityID
        rsp_user_offline.offline = False
        msg = success_msg(msgid.ROOM_USER_OFFLINE, rsp_user_offline)
        for role in room_obj.roles:
            if not role['offline']:
                g_playerManager.sendto(role['entityID'], msg)

        role = room_obj.get_role(self.player.entityID)
        role.offline = False

        rsp = rainbow_pb.JoinRoomResponse()
        rsp.room_id = room_obj.room_id
        rsp.master_id = room_obj.master_entity_id
        rsp.master_server_index = room_obj.master_server_index
        rsp.game_id = room_obj.game_id
        rsp.game_settings = room_obj.game_settings
        rsp.play_count = room_obj.play_count
        rsp.min_player_count = room_obj.game_config['min_player_count']
        rsp.max_player_count = room_obj.game_config['max_player_count']
        for role in room_obj.roles:
            rsp.users.add(**role)
        return success_msg(msgtype, '')

    @rpcmethod(msgid.ROOM_USER_LEAVE)
    @room_required()
    def user_leave(self, msgtype, body):
        room_obj = g_gameManager.get_room(self.player.room_id)
        role = room_obj.get_role(self.player.entityID)
        role['offline'] = True

        rsp_user_offline = rainbow_pb.UserOffline()
        rsp_user_offline.entityID = self.player.entityID
        rsp_user_offline.offline = True
        msg = success_msg(msgid.ROOM_USER_OFFLINE, rsp_user_offline)
        for role in room_obj.roles:
            if not role['offline']:
                g_playerManager.sendto(role['entityID'], msg)

        return success_msg(msgtype, '')

    @rpcmethod(msgid.ROOM_APPLY_FOR_DISMISS)
    @room_required()
    def apply_for_dismiss(self, msgtype, body):
        room_obj = g_gameManager.get_room(self.player.room_id)

        rsp = rainbow_pb.DismissRoomResult()

        # 如果只有自己一个人的话，那就直接解散吧
        if room_obj.get_roles_count() == 1:
            g_gameManager.dismiss_room(self.player)
            rsp.result = 2
            return success_msg(msgtype, rsp)

        # 如果已经有人申请了，你再申请的话，就默认同意了
        if room_obj.apply_entityID != 0:
            role = room_obj.get_role(self.player.entityID)
            role['dismiss_agree'] = True
        else:
            room_obj.apply_entityID = self.player.entityID
            rsp.apply_id = self.player.entityID

            for role in room_obj.roles:
                if role['entityID'] == self.player.entityID:
                    role['dismiss_agree'] = True
                else:
                    role['dismiss_agree'] = False

        # 统计一下同意的玩家数量和等待的玩家数量
        rsp.agree_num = 0
        rsp.waiting_num = 0
        rsp.result = 1

        for role in room_obj.roles:
            if role['entityID'] != 0:
                if role['dismiss_agree']:
                    rsp.agree_num += 1
                else:
                    rsp.waiting_num += 1

        msg = success_msg(msgtype, rsp_dismiss)
        for role in room_obj.roles:
            if role['entityID'] != 0 and not role['offline'] and role['entityID'] != self.player.entityID:
                g_playerManager.sendto(role['entityID'], msg)

        return msg

    @rpcmethod(msgid.ROOM_DISMISS_RESPONSE)
    @room_required()
    def user_dismiss_response(self, msgtype, body):
        room_obj = g_gameManager.get_room(self.player.room_id)

        rsp = rainbow_pb.DismissRoomResult()

        # 没有人申请解散房间，这个可能是玩家长时间没有回应导致的
        # 这个时候，房间可能已经因为超时之类的，已经自动解散了
        if room_obj.apply_entityID == 0:
            rsp.result = 0
            return success_msg(msgtype, rsp)

        req = rainbow_pb.AgreeDismiss()
        req.ParseFromString(body)

        # 不同意的话，就解散失败
        if not req.is_agree:
            rsp.result = 3
            msg = success_msg(msgtype, rsp)

            room_obj.apply_entityID = 0
            for role in room_obj.roles:
                if role['entityID'] != 0:
                    # 清理掉玩家对解散包间的回应标识
                    role['dismiss_agree'] = False

                    # 通知玩家，解散房间失败
                    if not role['offline'] and role['entityID'] != self.player.entityID:
                        g_playerManager.sendto(role['entityID'], msg)

            return msg

        # 同意的话，就检查是否所有玩家都做出了回应
        is_all_agree = True
        for role in room_obj.roles:
            # 先把自己的回应标记一下
            if role['entityID'] == self.player.entityID:
                role['dismiss_agree'] = True

            # 如果有玩家还没有回应，就需要继续等待
            if role['entityID'] != 0 and not role['dismiss_agree']:
                is_all_agree = False

        # 如果所有玩家都同意了，就解散吧
        if is_all_agree:
            rsp.result = 2
            msg = success_msg(msgtype, rsp)

            for role in room_obj.roles:
                if role['entityID'] != 0 and not role['offline'] and role['entityID'] != self.player.entityID:
                    g_playerManager.sendto(role['entityID'], msg)

            g_gameManager.dismiss_room(self.player)

            return msg

        # 统计一下同意的玩家数量和等待的玩家数量
        rsp.agree_num = 0
        rsp.waiting_num = 0
        rsp.result = 1

        for role in room_obj.roles:
            if role['entityID'] != 0:
                if role['dismiss_agree']:
                    rsp.agree_num += 1
                else:
                    rsp.waiting_num += 1

        msg = success_msg(msgtype, rsp)
        for role in room_obj.roles:
            if role['entityID'] != 0 and not role['offline'] and role['entityID'] != self.player.entityID:
                g_playerManager.sendto(role['entityID'], msg)

        return msg

    @rpcmethod(msgid.ROOM_USER_READY)
    @room_required()
    def user_ready(self, msgtype, body):
        room_obj = g_gameManager.get_room(self.player.room_id)

        req = rainbow_pb.UserReadyRequest()
        req.ParseFromString(body)

        role = room_obj.get_role(self.player.entityID)
        role['is_ready'] = req.is_ready

        # 判断是否所有玩家都准备就绪了，如果是的话，就开始游戏吧
        is_all_ready = True
        for role in RoleIterator(room_obj):
            if not role['is_ready']:
                is_all_ready = False

        if is_all_ready:
            room_obj.game_start()

        rsp = rainbow_pb.UserReadyResponse()
        rsp.pos_index = role['pos_index']
        rsp.is_ready = req.is_ready
        msg = success_msg(msgtype, rsp)

        room_obj.broadcast(self.player.entityID, msg)
        return msg

    @rpcmethod(msgid.MAHJONG_OUT_CARD)
    @room_required()
    def mahjong_out_card(self, msgtype, body):
        req = rainbow_pb.UserOutCardRequest()
        req.ParseFromString(body)

        # 不是处于游戏中，不可能出牌
        room_obj = g_gameManager.get_room(self.player.room_id)
        if room_obj.game_status != 'playing':
            return fail_msg(msgtype, msgTips.GAME_STATUS_NOT_PLAYING)

        # 还没轮到出牌
        role_info = room_obj.get_role_info(self.player.entityID)
        if role_info['server_index'] != room_obj.user_turn_index:
            return fail_msg(msgtype, msgTips.OUT_CARD_NOT_YOUR_TURN)

        # 手牌中没有这张牌，这就尴尬了
        if req.card_id not in role_info['hand_cards']:
            return fail_msg(msgtype, msgTips.OUT_CARD_CARD_ID_NOT_FOUND)

        return success_msg(msgtype, room_obj.player_out_card(self.player, req.card_id))

    @rpcmethod(msgid.MAHJONG_BLOCK_CARD)
    @room_required()
    def mahjong_block_card(self, msgtype, body):
        req = rainbow_pb.BlockRequest()
        req.ParseFromString(body)

        # 不是处于游戏中，不可能拦牌
        room_obj = g_gameManager.get_room(self.player.room_id)
        if room_obj.game_status != 'playing':
            return fail_msg(msgtype, msgTips.GAME_STATUS_NOT_PLAYING)

        # 没有找到对应的拦牌数据，-1 代表取消
        role_info = room_obj.get_role_info(self.player.entityID)
        if req.block_index != -1 and not role_info['block_op'][req.block_index]:
            return fail_msg(msgtype, msgTips.BLOCK_INDEX_ERROR)

        return success_msg(msgtype, room_obj.player_do_block(self.player, req.block_index))

    @rpcmethod(msgid.GAME_RECONN)
    @room_required()
    def game_reconn(self, msgtype, body):
        room_obj = g_gameManager.get_room(self.player.room_id)
        room_obj.player_reconn(self.player)

        offline_rsp = rainbow_pb.UserOffline()
        offline_rsp.entityID = self.player.entityID
        offline_rsp.offline = False
        for role_info in RoomRoleIterator(room_obj):
            if role_info['entityID'] == self.player.entityID:
                continue
            g_playerManager.sendto(role_info['entityID'], success_msg(msgid.ROOM_USER_OFFLINE, offline_rsp))

        return success_msg(msgtype, room_obj.pack_game_data(rainbow_pb.GameDataMahjong.Reconn, self.player.entityID))
