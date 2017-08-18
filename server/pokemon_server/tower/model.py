#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
from tower.c_floor import c_FloorBase
from yy.entity.storage.ssdb import EntityStoreMixinSsdb
import settings
from common.index import IndexString
from yy.entity.index import SortedIndexing, UniqueIndexing, SetIndexing
from config.configs import get_config, ClimbTowerAccreditConfig


class Floor(c_FloorBase, EntityStoreMixinSsdb):
    pool = settings.REDISES['entity']

    def is_closed(self):
        config = get_config(ClimbTowerAccreditConfig).get(self.floor, None)
        return any([not config, config and not config.unlock])

    def count(self):
        return self.idx.count() + self.idx_p.count()

    def is_full(self):
        if self.limit == -1:
            return False
        return self.count() >= self.limit

    def cleanup(self):
        end = int(time.time())
        self.idx.pool.execute('ZREMRANGEBYSCORE', self.idx.key, '-inf', end)
        self.idx_p.pool.execute('ZREMRANGEBYSCORE', self.idx_p.key, '-inf', end)
        self.lock.pool.execute('ZREMRANGEBYSCORE', self.lock.key, '-inf', end)
