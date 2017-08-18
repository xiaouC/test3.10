# coding:utf-8
import settings
from yy.entity.storage.ssdb import EntityStoreMixinSsdb
from common.redishelpers import EntityIdentityGenerator
from yy.entity.index import SetIndexing
from yy.entity.index import UniqueIndexing
from common import index

from group.c_group import c_GroupBase


class Group(c_GroupBase, EntityStoreMixinSsdb):
    pool = settings.REDISES['entity']

    def incr(self, f, v):
        self.push_command('HINCRBY', self.make_key(), f, v)

Group.set_identity_generator(
    EntityIdentityGenerator(
        pool=settings.REDISES['identity'],
        key='identity_group', initial=100000))
GroupRecommendIndexing = SetIndexing(
    index.SET_GROUP_RECOMMEND.render(), settings.REDISES['index'])  # 非满员同门
GroupnameIndexing = UniqueIndexing(
    index.INDEX_GROUP_NAME.render(), settings.REDISES['index'])
