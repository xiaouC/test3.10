# coding:utf-8
import settings
from yy.entity.storage.ssdb import EntityStoreMixinSsdb
# from yy.entity.identity import RedisIdentityGenerator
from yy.entity.index import UniqueIndexing, SetIndexing
from yy.ranking import NaturalRanking
from common.redishelpers import EntityIdentityGenerator
from common import index

from faction.c_faction import c_FactionBase


class Faction(c_FactionBase, EntityStoreMixinSsdb):
    pool = settings.REDISES['entity']

    def incr(self, f, v):
        self.push_command('HINCRBY', self.make_key(), f, v)

FactionRankRanking = NaturalRanking(
    index.RANK_FACTION_LEVEL.render(), settings.REDISES['index'])
FactionSkillRanking = NaturalRanking(
    index.RANK_FACTION_SKILL.render(), settings.REDISES['index'])
FactionnameIndexing = UniqueIndexing(
    index.INDEX_FACTION_NAME.render(), settings.REDISES['index'])
FactionRecommendIndexing = SetIndexing(
    index.SET_FACTION_RECOMMEND.render(), settings.REDISES['index'])  # 非满员公会
Faction.set_identity_generator(
    EntityIdentityGenerator(
        pool=settings.REDISES['identity'],
        key='identity_faction',
        initial=100000))
