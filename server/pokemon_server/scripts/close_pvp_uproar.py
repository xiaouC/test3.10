#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pvp.service import *  # NOQA
from world.service import *  # NOQA


@rpcmethod(msgid.UPROAR_START_FIGHT)
@level_required(tag="ticket")
def uproar_start_fight(self, msgtype, body):
    req = poem_pb.PvpStartFightRequest()
    req.ParseFromString(body)
    p = self.player
    if req.id in p.uproar_targets_done:
        return fail_msg(msgtype, reason="打过了")
    from pvp.uproar import validate_prev
    if not validate_prev(p, req.id):
        return fail_msg(msgtype, reason="未通关前置关卡")
    if req.id > 10:
        return fail_msg(msgtype,
                        reason="由于系统存在严重bug，训练家之丘无尽模式暂时关闭，敬请期待")
    # 校验阵型
    for i in req.lineup.line:
        if i:
            pet = p.pets[i]
            if pet.uproar_dead:
                return fail_msg(msgtype, reason="已阵亡的精灵不可参战")
    t = p.uproar_targets[req.id]
    if p.uproar_targets_team.get(t):  # 使用替换缓存
        rsp = poem_pb.TargetDetailResponse()
        rsp.ParseFromString(p.uproar_targets_team[t])
    else:
        if t in p.uproar_details_cache:
            detail = p.uproar_details_cache[t]
        else:
            detail = get_opponent_detail(t)
        rsp = poem_pb.TargetDetailResponse(**detail)
    p.uproar_target_cache = t
    p.save()
    rsp.verify_code = PlayerFightLock.lock(p.entityID, force=True)
    logger.debug(rsp)
    return success_msg(msgtype, rsp)

WorldService._method_map[msgid.UPROAR_START_FIGHT] = uproar_start_fight
