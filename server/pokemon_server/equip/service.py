# coding:utf-8
from yy.rpc import RpcService, rpcmethod
from yy.message.header import fail_msg, success_msg

from protocol import poem_pb
import protocol.poem_pb as msgid
from protocol.poem_pb import AdvanceEquip
# from protocol.poem_pb import SwapEquips
# from protocol.poem_pb import SwapEquipsResponse
from protocol.poem_pb import InstallEquip
# from protocol.poem_pb import UninstallEquip
# from protocol.poem_pb import StrengthenEquip
# from protocol.poem_pb import StrengthenEquipResponse
from protocol.poem_pb import EnchantEquip
#  from equip.manager import install_equip
#  from equip.manager import uninstall_equip
#  from equip.manager import strengthen_equip
#  from equip.manager import get_equipeds_infos
#  from equip.manager import swap_equips
#  # , advance_equip
#  from equip.manager import is_equiped
#  from equip.manager import strengthen_equips_onekey

# from config.configs import get_config
# from config.configs import EquipConfig
# from config.configs import EquipAdvanceLimitConfig
from config.configs import get_cons_value
from reward.manager import MatNotEnoughError
from reward.manager import AttrNotEnoughError
from reward.manager import apply_reward
from reward.manager import RewardType
# from reward.manager import check_cost_mats
# from .manager import advance_cost
from .manager import enchant_equip
from .manager import advance_equip
from .manager import install_equip
from .manager import strengthen_equip
from common import msgTips
from config.configs import get_config, EquipStrengthenConfig


class EquipService(RpcService):

    @rpcmethod(msgid.EQUIP_INSTALL)
    def install(self, msgtype, body):
        req = InstallEquip()
        req.ParseFromString(body)
        p = self.player
        err = install_equip(p, req.petID, req.equipID)
        if err:
            return fail_msg(msgtype, err)
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.EQUIP_ADVANCE)
    def advance(self, msgtype, body):
        req = AdvanceEquip()
        req.ParseFromString(body)
        p = self.player
        from entity.manager import save_guide
        save_guide(p, req.guide_type)  # 保存新手引导进度
        err = advance_equip(p, req.petID, req.equipID, req.equips)
        if err:
            return fail_msg(msgtype, err)
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.EQUIP_ENCHANT)
    def enchant(self, msgtype, body):
        p = self.player
        req = EnchantEquip()
        req.ParseFromString(body)
        need = pow(2, len(req.locks))
        enchant_free_used_count = 0
        if req.ex:
            need *= get_cons_value("EnchantExCostBase")
        else:
            if p.enchant_free_rest_count:
                need = 0
                enchant_free_used_count = 1

            else:
                need *= get_cons_value("EnchantCostBase")
        if need:
            if p.stone < need:
                gold = (need - p.stone) * get_cons_value("EnchantStoneToGold")
                cost = {"stone": p.stone, "gold": gold}
            else:
                cost = {"stone": need}
            try:
                apply_reward(p, {}, cost=cost, type=RewardType.EnchantEquip)
            except (AttrNotEnoughError, MatNotEnoughError):
                return fail_msg(msgtype, reason="消耗不足")
        enchant_equip(p, req.equipID, locks=req.locks, ex=req.ex)
        p.enchant_free_used_count += enchant_free_used_count
        p.save()
        p.sync()
        return success_msg(msgtype, "")

    @rpcmethod(msgid.EQUIP_STRENGTHEN)
    def strengthen(self, msgtype, body):
        p = self.player
        req = poem_pb.StrengthenEquip()
        req.ParseFromString(body)
        p = self.player
        from entity.manager import save_guide
        save_guide(p, req.guide_type)  # 保存新手引导进度
        err, rollback = strengthen_equip(p, req.petID, req.equipID)
        if err:
            return fail_msg(msgtype, err)
        rsp = poem_pb.StrengthenEquipResponse(success=not rollback)
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)

    @rpcmethod(msgid.PLAYER_EQUIP_STRENGTHEN)
    def player_strengthen(self, msgtype, body):
        req = poem_pb.StrengthenPlayerEquip()
        req.ParseFromString(body)
        p = self.player
        if not hasattr(p, "player_equip%d" % req.type):
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        player_equip = getattr(p, "player_equip%d" % req.type)
        if req.onekey:
            count = p.level + 5 - player_equip
        else:
            count = 1
        if player_equip + count > p.level + 5:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        configs = get_config(EquipStrengthenConfig)
        cost = 0
        for c, i in enumerate(
                range(player_equip + 1, player_equip + count + 1), 1):
            config = configs.get(i)
            if not config:
                return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
            if cost + config.cost > p.money:
                count = c - 1
                break
            cost += config.cost
        if not count:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        try:
            apply_reward(
                p, {}, {"money": cost},
                type=RewardType.PlayerEquipStrengthen)
        except AttrNotEnoughError:
            return fail_msg(msgtype, msgTips.FAIL_MSG_INVALID_REQUEST)
        setattr(p, "player_equip%d" % req.type, player_equip + count)
        for equip in p.equips.values():
            setattr(equip, "player_equip%d" % req.type, player_equip + count)
            equip.clear_base_power()
        p.clear_equip_power()
        p.clear_power()
        rsp = poem_pb.StrengthenPlayerEquipResponse()
        rsp.count = count
        from task.manager import on_strengthen_player_equip
        on_strengthen_player_equip(p, count)
        p.save()
        p.sync()
        return success_msg(msgtype, rsp)
