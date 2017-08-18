#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('gem')
import protocol.poem_pb as msgid
from protocol import poem_pb
from player.manager import g_playerManager
from yy.message.header import success_msg


def set_gems_dirty(role, *gems):
    role.dirty_gems.update(gems)


def pop_gems_dirty(role):
    dirty_gems = role.dirty_gems
    role.dirty_gems = set()
    return dirty_gems


def sync_gems(role, all=False):
    if all:
        gems = role.gems.keys()
    else:
        gems = pop_gems_dirty(role)
    if not gems and not all:
        return
    rsp = poem_pb.Gems()
    for gemID in gems:
        count = role.gems.get(gemID, 0)
        rsp.gems.add(gemID=gemID, count=count)
    g_playerManager.sendto(role.entityID, success_msg(msgid.SYNC_GEMS, rsp))


def match_gems(index, level):
    if index not in range(1, 6):
        return []
    from config.configs import get_config, GemConfig, PlayerRefineConfig
    kind = {1: 11, 2: 12, 3: 13, 4: 14, 5: 15}[index]
    refine_cfg = get_config(PlayerRefineConfig)[kind]
    gems = filter(lambda x: x.phase == level and x.kind in (refine_cfg.gem_group),
                  get_config(GemConfig).values())
    gem_group = dict([(gem.kind, gem) for gem in gems])
    return [gem_group[k] for k in refine_cfg.gem_group if k in gem_group]


def get_gems_addition(*args, **kwargs):
    gems = []
    for i, inlay in enumerate(args, 1):
        _gems = match_gems(i, inlay)
        gems.extend(_gems)
    additions = [getattr(g, kwargs['tag'], 0) for g in gems]
    return sum(additions)
