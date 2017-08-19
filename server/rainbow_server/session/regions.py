# coding: utf-8
import os
import time
import ujson
import logging
logger = logging.getLogger('session')

# from yy.db.redisscripts import load_redis_script
from yy.utils import convert_dict_to_list
from common.redishelpers import RHash, RSet
from common.redishelpers import RString
import settings

settings_pool = settings.REDISES['settings']

r_worlds = RHash('ALL_WORLDS', settings_pool)
r_whitelist = RSet('WHITELIST', settings_pool)
r_block_devices = RSet("BLOCKDEVICES", settings_pool)
r_version = RString("VERSION", settings_pool)

g_worlds = {}
g_whitelist = set()
g_loginlimitmsg = ''
g_block_devices = set()
g_version = 0


def get_loginlimitmsg():
    return settings.LOGINLIMITMSG


def get_g_version():
    return g_version


def world_key(worldID):
    return 'WORLD{%s}' % worldID


def add_world(worldID, interval, info):
    assert worldID not in g_worlds, 'world exists'
    if worldID == settings.WORLD["ID"]:
        managehost = os.environ.get("DOCKER_MANAGEHOST")
        if managehost:
            info.update(managehost=managehost)
    g_worlds[worldID] = World.from_info(worldID, info)
    update_world(worldID, interval, **info)


def update_world(worldID, interval, **info):
    if worldID not in g_worlds:
        return False

    wkey = world_key(worldID)
    expire = time.time() + interval / float(1000)
    commands = [
        ('hmset', wkey) + tuple(convert_dict_to_list(info)),
        ('hset', 'ALL_WORLDS', worldID, expire),
    ]
    settings_pool.execute_pipeline(*commands)

    # update cache
    for k, v in info.items():
        setattr(g_worlds[worldID], k, v)

    return True


def del_world(self, worldID):
    del g_worlds[worldID]
    settings_pool.execute('hdel', 'ALL_WORLDS', worldID)


class World(object):
    def __init__(self, ID, online, ip, port, managehost, manageport, mode, backdoorport):
        self.id = ID
        self.online = online
        self.ip = ip
        self.port = port
        self.managehost = managehost
        self.manageport = manageport
        self.mode = mode
        self.backdoorport = backdoorport

    @classmethod
    def from_info(cls, worldID, info):
        return cls(
            worldID,
            int(info.get('online', 0)),
            info['ip'],
            int(info['port']),
            info['managehost'],
            int(info['manageport']),
            info['mode'],
            int(info['backdoorport']),
        )


def reload_worlds(verbose=False):
    now = time.time()
    worlds = {}
    for worldID, expire in r_worlds.hgetall().items():
        worldID = int(worldID)
        expire = float(expire)
        if expire < now:
            continue
        info = RHash(world_key(worldID), settings_pool).hgetall()
        if not info and not info.get("ID"):
            continue
        assert int(info['ID']) == worldID, 'impossible'
        worlds[worldID] = World.from_info(worldID, info)

    g_worlds.clear()
    g_worlds.update(worlds)
    if verbose:
        log_worlds_summary()


def log_worlds_summary():
    for world in g_worlds.values():
        print 'world.id :', world.id


def reload_whitelist():
    global g_whitelist
    g_whitelist.clear()
    g_whitelist.update(r_whitelist.smembers())


def reload_block_devices():
    global g_block_devices
    result = r_block_devices.smembers()
    g_block_devices.clear()
    g_block_devices.update(result)


def reload_version():
    global g_version
    g_version = int(r_version.get() or 0)


def reload_all(verbose=False):
    reload_worlds(verbose)
    reload_whitelist()
    reload_block_devices()
    reload_version()


def run_world_reloader(verbose=False):
    logger.info("Running region reloader")
    from gevent import sleep
    while True:
        try:
            reload_all(verbose)
        except:
            logger.exception('reload regions and whitelist')
        sleep(1)


