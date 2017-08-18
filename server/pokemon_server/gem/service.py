#!/usr/bin/env python
# -*- coding: utf-8 -*-

from yy.rpc import RpcService, rpcmethod
from yy.message.header import fail_msg, success_msg

from protocol import poem_pb
import protocol.poem_pb as msgid
from common import msgTips
from reward.constants import RewardType, RewardItemType
from reward.manager import parse_reward, apply_reward
from reward.manager import AttrNotEnoughError, GemNotEnoughError
from config.configs import get_config, GemConfig, GemRefineConfig
from config.configs import PlayerRefineConfig
from gem.manager import match_gems


class GemService(RpcService):
    @rpcmethod(msgid.GEM_COMPOSE)
    def gem_compose(self, msgtype, body):
        req = poem_pb.GemComposeRequest()
        req.ParseFromString(body)
        p = self.player
        config = get_config(GemConfig).get(req.gemID, None)
        if not config:
            return fail_msg(msgtype, code=msgTips.FAIL_MSG_INVALID_REQUEST)

        if config.gupr <= 0:
            return fail_msg(msgtype, code=msgTips.FAIL_MSG_INVALID_REQUEST)

        have = p.gems.get(config.ID, 0)
        if have >= config.compose_consume:
            count = have / config.compose_consume if req.all else 1
            cost = config.compose_consume * count
            cost = parse_reward([dict(type=RewardItemType.Gem, arg=config.ID,
                                      count=cost)])
            reward = parse_reward([dict(type=RewardItemType.Gem, arg=config.gupr,
                                        count=count)])
            result = apply_reward(p, reward, cost=cost, type=RewardType.GemCompose)
        else:
            return fail_msg(msgtype, reason='宝石不足')

        p.save()
        p.sync()
        return success_msg(msgtype, '')

    @rpcmethod(msgid.GEM_REFINE)
    def gem_refine(self, msgtype, body):
        req = poem_pb.GemRefineRequest()
        req.ParseFromString(body)
        p = self.player
        if not hasattr(p, 'inlay%d' % req.index):
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)

        inlay = getattr(p, 'inlay%d' % req.index)
        config = get_config(GemRefineConfig).get(inlay + 1)
        if not config:
            return fail_msg(msgtype, reason='满级了')

        kind = {1: 11, 2: 12, 3: 13, 4: 14, 5: 15}[req.index]
        refine_cfg = get_config(PlayerRefineConfig)[kind]
        cost = [dict(type=config.cost_type, arg=config.cost_type,
                     count=config.cost)]
        gems = match_gems(req.index, inlay + 1)
        cost.extend([dict(type=RewardItemType.Gem, arg=g.ID, count=1) for g in gems])
        try:
            result = apply_reward(p, {}, cost=parse_reward(cost),
                                  type=RewardType.GemRefine)
        except AttrNotEnoughError as e:
            return fail_msg(msgtype, reason='消耗不足')
        except GemNotEnoughError:
            return fail_msg(msgtype, reason='宝石不足')

        count = 1
        setattr(p, "inlay%d" % req.index, inlay + count)
        p.clear_equip_power()
        p.clear_power()
        p.save()
        p.sync()
        return success_msg(msgtype, '')
