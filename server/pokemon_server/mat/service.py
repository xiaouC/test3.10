# coding:utf-8
import logging

logger = logging.getLogger("mat")
from yy.rpc import RpcService
from yy.rpc import rpcmethod

from yy.message.header import success_msg
from yy.message.header import fail_msg

from config.configs import get_config
from config.configs import MatConfig

import protocol.poem_pb as msgid
from protocol import poem_pb
from common import msgTips

from mat.constants import USEINGS
from mat.constants import MatType

from reward.constants import RewardType
from reward.manager import open_reward
from reward.manager import build_reward_msg


class MatService(RpcService):

    @rpcmethod(msgid.USE_MAT)
    def use_mat(self, msgtype, body):
        p = self.player
        req = poem_pb.UseMatRequest()
        req.ParseFromString(body)
        config = get_config(MatConfig).get(req.matID)
        if not config:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        rsp = poem_pb.UseMatResponse()
        if config.type == MatType.Drop:
            drop = config.arg
            attr = ""
        elif config.type in USEINGS:
            drop = 0
            attr = USEINGS.get(config.type)
        elif config.type == MatType.RipeningAgent:
            if p.seed_state == poem_pb.SeedStateNormal or\
                    p.seed_state == poem_pb.SeedStateRipening or\
                    p.seed_state == poem_pb.SeedStateRoot:
                return fail_msg(msgtype, reason="无法使用!")
            p.seed_state = poem_pb.SeedStateRipening
            p.seed_state_last_change_time = 0
            p.seed_state_next_change_time = 0
            p.seed_state_ripening_time = 0
            drop = 0
            attr = ''
        else:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        reward = open_reward(RewardType.UseMat, drop)
        reward.cost_after(p, matList=[[req.matID, 1]])
        result = reward.apply(p)
        if attr:
            value = getattr(p, attr, 0) + config.arg
            setattr(p, attr, value)
        rsp.tips = config.tips
        build_reward_msg(rsp, result)
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)
