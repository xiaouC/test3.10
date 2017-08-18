# coding:utf-8
import logging
logger = logging.getLogger('user')
from user.c_user import c_UserBase
from yy.entity.storage.ssdb import EntityStoreMixinSsdb
from yy.entity.identity import RedisIdentityGenerator
from yy.entity.index import UniqueIndexing

import settings


class User(c_UserBase, EntityStoreMixinSsdb):
    pool = settings.REDISES['user']

UsernameIndexing = UniqueIndexing(
    'index_u_username', settings.REDISES['index'])
User.set_identity_generator(RedisIdentityGenerator(
    pool=settings.REDISES['identity'], key='identity_user'))
