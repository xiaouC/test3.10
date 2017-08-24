#!/usr/bin/env python
# coding=utf-8

import protocol.rainbow_pb as msgid
from protocol import rainbow_pb

from yy.rpc import RpcService, rpcmethod
from yy.message.header import success_msg, fail_msg

from game.manager import g_roomManager
from entity.manager import g_entityManager
from player.manager import g_playerManager

class RoomService(RpcService):
    @rpcmethod(msgid.ROOM_CREATE)
    def create_room(self, msgtype, body):
        req = rainbow_pb.CreateRoomRequest()
        req.ParseFromString(body)

        if self.player.room_id != 0:
            room_obj = g_roomManager.get_room(self.player.room_id):
            if room_obj and room_obj.has_player(self.player.entityID):
                return fail_msg(msgtype, msgTips.FAIL_MSG_ROOM_CREATE_HAS_ROOM)

        room_obj = g_roomManager.create_room(self.player, req.game_id, req.game_settings)

        self.player.room_id = room_obj.room_id
        self.player.pos_index = 0
        self.player.save()
        self.player.sync()

        rsp = rainbow_pb.JoinRoomResponse()
        rsp.room_id = room_obj.id
        rsp.master_id = room_obj.master_entity_id
        rsp.server_index = 0
        for role in room_obj.roles:
            rsp.users.add(**role)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.ROOM_USER_JOIN)
    def join_room(self, msgtype, body):
        req = rainbow_pb.JoinRoomRequest()
        req.ParseFromString(body)

        room_obj = g_roomManager.get_room(req.room_id)
        if not room_obj:
            return fail_msg(msgtype, msgTips.FAIL_MSG_ROOM_NOT_EXIST)

        if room_obj.max_count <= len(room_obj.roles):
            return fail_msg(msgtype, msgTips.FAIL_MSG_ROOM_LIMIT_EXCEED)

        # 
        rsp_user_info = rainbow_pb.UserInfo()
        rsp_user_info.entityID = self.player.entityID
        rsp_user_info.username = self.player.username
        rsp_user_info.sex = self.player.sex
        rsp_user_info.offline = False
        g_playerManager.broadcast(room_obj.roles, success_msg(msgid.ROOM_USER_IN, rsp_user_info))

        # 
        pos_index = -1
        for index, role in enumerate(room_obj.roles):
            if role.entityID == 0:
                role.entityID = self.player.entityID
                role.username = self.player.username
                role.sex = self.player.sex
                role.offline = False

                pos_index = index

        if pos_index == -1:
            pos_index = len(room_obj.roles)

            room_obj.roles.append({
                'entityID': self.player.entityID,
                'username': self.player.username,
                'sex': self.player.sex,
                'offline': False,
                })

        self.player.room_id = req.room_id
        self.player.pos_index = pos_index
        self.player.save()
        self.player.sync()

        rsp = rainbow_pb.JoinRoomResponse()
        rsp.room_id = room_obj.id
        rsp.master_id = room_obj.master_entity_id
        rsp.server_index = self.player.pos_index
        for role in room_obj.roles:
            rsp.users.add(**role)
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.ROOM_USER_KICK_OUT)
    def user_out(self, msgtype, body):
        req = rainbow_pb.KickOutRequest()
        req.ParseFromString(body)

        room_obj = g_roomManager.get_room(self.player.room_id)
        if not room_obj:
            return fail_msg(msgtype, msgTips.FAIL_MSG_ROOM_NOT_EXIST)

        if room_obj.master_entity_id != self.player.entityID:
            return fail_msg(msgtype, msgTips.FAIL_MSG_ROOM_KICK_OUT_PERMISSION_DENY)

        rsp_user_kick_out = rainbow_pb.UserKickOut()
        rsp_user_kick_out.kick_out_id = req.kick_out_id
        msg = success_msg(msgid.ROOM_USER_BEEN_KICK_OUT, rsp_user_kick_out)
        for role in room_obj.roles:
            if role.entityID == 0:
                continue

            p = g_entityManager.get_player(role.entityID)
            if p:
                if p.entityID == req.kick_out_id:
                    p.room_id = 0
                    p.pos_index = 0
                    p.save()
                g_playerManager.sendto(role.entityID, msg)

            if role.entityID == req.kick_out_id:
                role.entityID = 0
                role.username = ''

        return success_msg(msgtype, '')

    @rpcmethod(msgid.ROOM_USER_BACK)
    def user_back(self, msgtype, body):
        room_obj = g_roomManager.get_room(self.player.room_id)
        if not room_obj or not room_obj:has_player(self.player.entityID):
            self.player.room_id = 0
            self.player.pos_index = 0
            self.player.save()
            return fail_msg(msgtype, msgTips.FAIL_MSG_ROOM_NOT_EXIST)

        rsp_user_offline = rainbow_pb.UserOffline()
        rsp_user_offline.entityID = self.player.entityID
        rsp_user_offline.offline = False
        msg = success_msg(msgid.ROOM_USER_BACK, rsp_user_offline)
        for role in room_obj.roles:
            if not role.offline:
                g_playerManager.sendto(role.entityID, msg)

        role = room_obj.get_role(self.player.entityID)
        role.offline = False

        rsp = rainbow_pb.JoinRoomResponse()
        rsp.room_id = room_obj.id
        rsp.master_id = room_obj.master_entity_id
        rsp.server_index = self.player.pos_index
        for role in room_obj.roles:
            rsp.users.add(**role)
        return success_msg(msgtype, '')

    @rpcmethod(msgid.ROOM_USER_LEAVE)
    def user_leave(self, msgtype, body):
        room_obj = g_roomManager.get_room(self.player.room_id)
        if not room_obj or not room_obj:has_player(self.player.entityID):
            self.player.room_id = 0
            self.player.pos_index = 0
            self.player.save()
            return fail_msg(msgtype, msgTips.FAIL_MSG_ROOM_NOT_EXIST)

        role = room_obj.get_role(self.player.entityID)
        role.offline = True

        rsp_user_offline = rainbow_pb.UserOffline()
        rsp_user_offline.entityID = self.player.entityID
        rsp_user_offline.offline = True
        msg = success_msg(msgid.ROOM_USER_LEAVE, rsp_user_offline)
        for role in room_obj.roles:
            if not role.offline:
                g_playerManager.sendto(role.entityID, msg)

        return success_msg(msgtype, '')

    @rpcmethod(msgid.ROOM_APPLY_FOR_DISMISS)
    def apply_for_dismiss(self, msgtype, body):
        room_obj = g_roomManager.get_room(self.player.room_id)
        if not room_obj or not room_obj:has_player(self.player.entityID):
            self.player.room_id = 0
            self.player.pos_index = 0
            self.player.save()
            return fail_msg(msgtype, msgTips.FAIL_MSG_ROOM_NOT_EXIST)

        if room_obj.get_roles_count() == 1:
            rsp_result = rainbow_pb.DissmissRoomResult()
            rsp_result.dismiss = True
            return success_msg(msgid.ROOM_DISMISS_RESULT, rsp_result)

        # 如果已经有人申请了，你再申请的话，就默认同意了
        if room_obj.apply_entityID != 0:
            role = room_obj.get_role(self.player.entityID)
            role.dismiss_agree = True
        else:
            room_obj.apply_entityID = self.player.entityID

            for role in room_obj.roles:
                if role.entityID == self.player.entityID:
                    role.dismiss_agree = True
                else
                    role.dismiss_agree = False

        rsp_dismiss = rainbow_pb.DissmissRoomResponse()
        rsp_dismiss.apply_id = room_obj.apply_entityID
        for role in room_obj.roles:
            if role.entityID != 0:
                rsp.users.add(entityID=role.entityID, agree=role.dismiss_agree)
        msg = success_msg(msgid.ROOM_DISMISS_RESPONSE, rsp_dismiss)
        for role in room_obj.roles:
            if not role.offline:
                g_playerManager.sendto(role.entityID, msg)

        return success_msg(msgtype, '')

    @rpcmethod(msgid.ROOM_DISMISS_RESPONSE)
    def apply_for_dismiss(self, msgtype, body):
        room_obj = g_roomManager.get_room(self.player.room_id)
        if not room_obj or not room_obj:has_player(self.player.entityID):
            self.player.room_id = 0
            self.player.pos_index = 0
            self.player.save()
            return fail_msg(msgtype, msgTips.FAIL_MSG_ROOM_NOT_EXIST)

        # 啥也不干吧
        if room_obj.apply_entityID == 0:
            return success_msg(msgtype, '')

        req = rainbow_pb.AgreeDismiss()
        req.ParseFromString(body)

        if not req.agree:
            rsp_result = rainbow_pb.DissmissRoomResult()
            rsp_result.dismiss = False
            msg = success_msg(msgid.ROOM_DISMISS_RESULT, rsp_result)

            room_obj.apply_entityID = 0
            for role in room_obj.roles:
                if role.entityID != 0:
                    role.dismiss_agree = False
                    if not role.offline:
                        g_playerManager.sendto(role.entityID, msg)

            return success_msg(msgtype, '')

        is_all_agree = True
        for role in room_obj.roles:
            if role.entityID == self.player.entityID:
                role.dismiss_agree = True

            if role.entityID != 0 and not role.dismiss_agree:
                is_all_agree = False

        if is_all_agree:
            rsp_result = rainbow_pb.DissmissRoomResult()
            rsp_result.dismiss = True
            msg = success_msg(msgid.ROOM_DISMISS_RESULT, rsp_result)
        else:
            rsp_dismiss = rainbow_pb.DissmissRoomResponse()
            rsp_dismiss.apply_id = room_obj.apply_entityID
            for role in room_obj.roles:
                if role.entityID != 0:
                    rsp.users.add(entityID=role.entityID, agree=role.dismiss_agree)
            msg = success_msg(msgid.ROOM_DISMISS_RESPONSE, rsp_dismiss)

        for role in room_obj.roles:
            if not role.offline:
                g_playerManager.sendto(role.entityID, msg)

        return success_msg(msgtype, '')

