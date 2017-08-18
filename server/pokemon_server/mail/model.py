# coding:utf-8
import time
from mail.c_mail import c_MailBase
from yy.entity.storage.redis import EntityStoreMixinRedis
from yy.entity.identity import RedisIdentityGenerator
from yy.entity.index import SortedIndexing
import settings


class Mail(c_MailBase, EntityStoreMixinRedis):
    pool = settings.REDISES['entity']

    @classmethod
    def add_offline_mail(cls, **kwargs):
        from mail.model import Mail
        mail = Mail.create(
            playerID=kwargs['playerID'], title=kwargs['title'],
            content=kwargs['content'], addition=kwargs['addition'],
            addtime=kwargs['addtime'], limitdata=kwargs['limitdata'],
            type=kwargs['type']
        )
        mail.save()
        EmailByTimeIndexing.register(mail.mailID, kwargs['addtime'])

    @classmethod
    def add_condition_mail(cls, **kwargs):
        kwargs["addtime"] = time.time()
        mail = Mail.create(**kwargs)
        mail.save()
        EmailByTimeIndexing.register(mail.mailID, kwargs['addtime'])
        return mail

Mail.set_identity_generator(
    RedisIdentityGenerator(
        pool=settings.REDISES['identity'],
        key='identity_mail'))
EmailByTimeIndexing = SortedIndexing(
    'email_by_time{%d}' % settings.REGION['ID'],
    settings.REDISES['index'])
