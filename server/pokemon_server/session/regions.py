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

r_regions = RHash('REGIONS', settings_pool)
r_whitelist_regions = RSet('REGIONS_ENABLE_WHITELIST', settings_pool)
r_whitelist = RSet('WHITELIST', settings_pool)
r_loginlimitmsg = RString("LOGINLIMITMSG", settings_pool)
r_block_devices = RSet("BLOCKDEVICES", settings_pool)
r_versions = RHash('VERSIONS', settings_pool)
r_sdks = RHash('SDKS', settings_pool)
r_version = RString("VERSION", settings_pool)

g_regions = {}
g_whitelist_regions = set()
g_whitelist = set()
g_loginlimitmsg = ''
g_block_devices = set()
g_versions = {}
g_sdks = {}
g_version = 0


def get_loginlimitmsg():
    if not g_loginlimitmsg:
        return settings.LOGINLIMITMSG
    return g_loginlimitmsg


def get_g_version():
    return g_version


def world_key(regionID, worldID):
    return 'REGION{%s}_WORLD{%s}' % (regionID, worldID)


def region_key(regionID):
    return 'REGION{%s}' % regionID


class Region(object):
    def __init__(self, id, name, worlds, total_online):
        self.id = id
        self.name = name
        self.worlds = worlds
        self.total_online = total_online

    def add_world(self, worldID, interval, info):
        assert worldID not in self.worlds, 'world exists'
        if worldID == settings.WORLD["ID"]:
            managehost = os.environ.get(
                "DOCKER_MANAGEHOST")
            if managehost:
                info.update(managehost=managehost)
        self.worlds[worldID] = World.from_info(worldID, info)
        self.update_world(worldID, interval, **info)

    def update_world(self, worldID, interval, **info):
        if worldID not in self.worlds:
            return False

        wkey = world_key(self.id, worldID)
        rkey = region_key(self.id)
        expire = time.time() + interval / float(1000)
        commands = [
            ('hmset', wkey) + tuple(convert_dict_to_list(info)),
            # ('pexpire', wkey, interval),
            ('hset', rkey, worldID, expire),
        ]
        settings_pool.execute_pipeline(*commands)

        # update cache
        for k, v in info.items():
            setattr(self.worlds[worldID], k, v)

        return True

    def del_world(self, worldID):
        del self.worlds[worldID]
        rkey = region_key(self.id)
        settings_pool.execute('hdel', rkey, worldID)


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


def reload_regions(verbose=False):
    global g_regions
    now = time.time()
    regions = {}
    # r_regions.hgetall().items()
    #  for regionID, r in settings.REGIONS.items():
    #      regionName = r["name"]
    for regionID, r in r_regions.hgetall().items():
        regionName = r
        regionID = int(regionID)
        worlds = {}
        rhash = RHash(region_key(regionID), settings_pool)
        for worldID, expire in rhash.hgetall().items():
            worldID = int(worldID)
            expire = float(expire)
            if expire < now:
                continue
            info = RHash(world_key(regionID, worldID), settings_pool).hgetall()
            if not info and not info.get("ID"):
                continue
            assert int(info['ID']) == worldID, 'impossible'
            worlds[worldID] = World.from_info(worldID, info)
        regions[regionID] = Region(
            regionID, regionName, worlds,
            sum(info.online for info in worlds.values())
        )
    g_regions.clear()
    g_regions.update(regions)
    if verbose:
        log_region_summary()


def log_region_summary():
    for region in g_regions.values():
        print region.id, ':', ', '.join(
            map(str, [w.id for w in region.worlds.values()]))


def reload_whitelist():
    global g_whitelist_regions, g_whitelist
    g_whitelist_regions.clear()
    g_whitelist_regions.update(map(int, r_whitelist_regions.smembers()))
    g_whitelist.clear()
    g_whitelist.update(r_whitelist.smembers())


def reload_loginlimitmsg():
    global g_loginlimitmsg
    msg = r_loginlimitmsg.get()
    if msg:
        g_loginlimitmsg = msg.decode('utf-8')


def reload_versions():
    global g_versions
    for regionID, raw in r_versions.hgetall().items():
        g_versions[int(regionID)] = ujson.loads(raw)


def reload_sdks():
    global g_sdks
    for regionID, raw in r_sdks.hgetall().items():
        g_sdks[int(regionID)] = ujson.loads(raw)


def reload_block_devices():
    global g_block_devices
    result = r_block_devices.smembers()
    g_block_devices.clear()
    g_block_devices.update(result)


def reload_version():
    global g_version
    g_version = int(r_version.get() or 0)


def reload_all(verbose=False):
    reload_regions(verbose)
    reload_whitelist()
    reload_loginlimitmsg()
    reload_block_devices()
    reload_versions()
    reload_sdks()
    reload_version()


def run_region_reloader(verbose=False):
    logger.info("Running region reloader")
    from gevent import sleep
    while True:
        try:
            reload_all(verbose)
        except:
            logger.exception('reload regions and whitelist')
        sleep(1)


def reset_regions(regions):
    regions = {k: v["name"] for k, v in regions.items()}
    settings_pool.execute_pipeline(
        ('del', r_regions.key),
        ('hmset', r_regions.key) + tuple(convert_dict_to_list(regions)),
    )


def ping():
    settings_pool.execute("GET", "1")
