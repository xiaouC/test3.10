from equip.c_equip import c_EquipBase
from yy.entity.storage.ssdb import EntityStoreMixinSsdb
from yy.entity.identity import RedisIdentityGenerator
import settings
from player.manager import g_playerManager


class Equip(c_EquipBase, EntityStoreMixinSsdb):
    pool = settings.REDISES['entity']

    def on_sync(self, *fields, **kwargs):
        from entity.utils import sync_property_msg
        all = kwargs.pop('all', False)
        if not fields:
            fields = self.pop_sync_dirty()
            if not fields:
                return
        if all:
            fields = None
        return self.masterID, sync_property_msg(self, fields=fields)

    def do_sync(self, sendto, rsp):
        g_playerManager.sendto(sendto, rsp)

    def sync(self, *fields, **kwargs):
        ret = self.on_sync(*fields, **kwargs)
        if ret:
            sendto, rsp = ret
            if sendto:
                self.do_sync(sendto, rsp)

Equip.set_identity_generator(
    RedisIdentityGenerator(
        pool=settings.REDISES['identity'],
        key='identity_equip'))
