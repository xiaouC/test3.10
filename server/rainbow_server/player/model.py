# coding:utf-8
import time
# import math
from datetime import datetime
import settings

from player.c_player import c_PlayerBase
from player.manager import g_playerManager

from mail.constants import MailType

# from yy.entity.storage.redis import EntityStoreMixinRedis
# from yy.entity.identity import RedisIdentityGenerator
from yy.entity.storage.ssdb import EntityStoreMixinSsdb
from yy.entity.index import UniqueIndexing
from yy.entity.index import SetIndexing
# from yy.ranking import NaturalRanking
from yy.ranking import NaturalRankingWithJoinOrder
from yy.ranking import SwapRanking
from yy.db.redisscripts import load_redis_script

from common.redishelpers import EntityIdentityGenerator
from common import index


class Player(c_PlayerBase, EntityStoreMixinSsdb):
    pool = settings.REDISES['entity']

    def on_sync(self, *fields, **kwargs):
        from entity.utils import sync_property_msg
        all = kwargs.pop('all', False)
        if not fields:
            fields = self.pop_sync_dirty()
            if not fields and not all:
                return
        if all:
            fields = None
        return self.entityID, sync_property_msg(self, fields=fields, isme=True)

    def do_sync(self, sendto, rsp):
        g_playerManager.sendto(sendto, rsp)

    def sync(self, *fields, **kwargs):
        ret = self.on_sync(*fields, **kwargs)
        if ret:
            sendto, rsp = ret
            if sendto:
                self.do_sync(sendto, rsp)

    def load_mails(self):
        from mail.model import Mail
        mails = Mail.batch_load(self.mailset)
        for mail in mails:
            if not mail:
                continue
            self.mails[mail.mailID] = mail

    def add_mail(self, title, content, addition=None, addtime=None, type=MailType.System, cd=0):
        from mail.model import Mail
        if not addition:
            addition = {}
        if not addtime:
            addtime = int(time.time())
        mail = Mail.create(playerID=self.entityID, title=title, content=content, addition=addition, addtime=addtime, type=type, cd=cd)
        mail.save()
        self.mails[mail.mailID] = mail
        # self.touch_mails()
        self.mailset.add(mail.mailID)
        self.save()
        self.sync()
        return mail

    def save_on_quit(self):
        self.totalbp_on_logout = self.totalbp
        self.lastlogout = datetime.now()
        self.save()

    def del_mails(self, *mails):
        for mail in mails:
            try:
                del self.mails[mail.mailID]
                self.mailset.remove(mail.mailID)
            except KeyError:
                pass
        for mail in mails:
            mail.delete()
        # self.touch_mails()
        self.save()
        self.sync()
        return True


Player.set_identity_generator(EntityIdentityGenerator(pool=settings.REDISES['identity'], key='identity_player', initial=100000))

PlayerOnlineIndexing = UniqueIndexing("index_p_online{%d}" % (settings.SESSION["ID"]), settings.REDISES['index'])

