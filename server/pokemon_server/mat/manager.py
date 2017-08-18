#coding:utf-8
import logging
logger = logging.getLogger('mat')
import protocol.poem_pb as msgid
from protocol.poem_pb import Mats
from player.manager import g_playerManager

from yy.message.header import success_msg


def set_mats_dirty(role, *mats):
    role.dirty_mats.update(mats)


def pop_mats_dirty(role):
    dirty_mats = role.dirty_mats
    role.dirty_mats = set()
    return dirty_mats


def sync_mats(role, all=False):
    if all:
        mats = role.mats.keys()
    else:
        mats = pop_mats_dirty(role)
    if not mats and not all:
        return
    rsp = Mats()
    for matID in mats:
        count = role.mats.get(matID, 0)
        rsp.mats.add(matID=matID, count=count)
    g_playerManager.sendto(role.entityID, success_msg(msgid.SYNC_MATS, rsp))
