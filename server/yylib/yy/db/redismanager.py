#coding:utf-8
import credis
from credis.geventpool import ResourcePool
from credis.base import Connection
from yy.utils import parse_redis_url
from .redisscripts import init_scripts

def create_pool(url):
    info = parse_redis_url(url)
    poolmax = int(info.pop('poolmax', 32))
    return ResourcePool(poolmax, Connection, **info)

def generate_uniqueID(pool, prefix):
    assert prefix and isinstance(prefix, basestring), 'Not prefix specify or is not str'
    return pool.execute('INCR', prefix)

def check_duplicate_name(pool, name):
    return bool(pool.execute('HEXISTS', 'PlayerName:UNIQ', name))

def update_duplicate_name(pool, name):
    return pool.execute('HSET', 'PlayerName:UNIQ', name, 1)
