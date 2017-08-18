import os
import md5
import copy
import time
import fnmatch
from yy.utils import convert_list_to_dict
from yy.db.redisscripts import load_redis_script
from yy.config.cache import load
from proxy_objects import AbstractWrapper
from functools import reduce
from common.redishelpers import RHash


def get_session_pool():
    import settings
    return settings.REDISES["session"]


def get_index_pool():
    import settings
    return settings.REDISES["index"]


def get_settings_pool():
    import settings
    return settings.REDISES['settings']


def make_settings_key(regionID, worldID):
    return 'REGION{%s}_WORLD{%s}' % (str(regionID), str(worldID))


def make_region_settings_key(regionID):
    return "REGION{%s}" % str(regionID)


def parse_world(world):
    if world:
        world['ID'] = int(world['ID'])
        world['port'] = int(world['port'])
        world['online'] = int(world.get('online', 0))
    return world


def make_hash(o):
    if isinstance(o, (set, tuple, list)):
        return tuple([make_hash(e) for e in o])
    elif not isinstance(o, dict):
        return hash(o)
    new_o = copy.deepcopy(o)
    for k, v in new_o.items():
        new_o[k] = make_hash(v)
    return hash(tuple(frozenset(sorted(new_o.items()))))


class Singleton(object):
    objs = {}

    def __new__(cls, *args, **kwargs):
        if args or kwargs:
            hashed = make_hash((cls, args, kwargs))
        else:
            hashed = cls
        if hashed in cls.objs:
            return cls.objs[hashed]['obj']
        obj = object.__new__(cls, *args, **kwargs)
        cls.objs[hashed] = {'obj': obj, 'init': False}
        setattr(cls, '__init__', cls.decorate_init(cls.__init__))
        return obj

    @classmethod
    def decorate_init(cls, fn):
        def init_wrap(*args, **kwargs):
            if args[1:] or kwargs:
                hashed = make_hash((cls, args[1:], kwargs))
            else:
                hashed = cls
            if not cls.objs[hashed]['init']:
                fn(*args, **kwargs)
                cls.objs[hashed]['init'] = True
            return
        return init_wrap


class Fetcher(AbstractWrapper):
    extra = None

    def __init__(self, *arg_for_handle, **kwargs):
        super(Fetcher, self).__init__()
        self.extra = kwargs
        self.extra.setdefault('args_for_handle', arg_for_handle)

    def __getattr__(self, attr):
        if attr == '__subject__':
            try:
                super(Fetcher, self).__getattr__(attr)
            except AttributeError:
                self.fetch()
            return self.__subject__
        return super(Fetcher, self).__getattr__(attr)

    def fetch(self):
        r = self.handle(*self.extra['args_for_handle'], **self.extra)
        f = self.extra.get('formatter')
        if f:
            self.__subject__ = f(r)
        else:
            self.__subject__ = r
        return self.__subject__

    def clear(self):
        if hasattr(self, '__subject__'):
            del self.__subject__

    def handle(self, *args):
        raise NotImplementedError


class RedisFetcher(Fetcher):

    def handle(self, *args, **kwargs):
        pool = kwargs.get("pool", None)
        if not pool:
            pool = get_settings_pool()
        with pool.ctx() as conn:
            return conn.execute(*args)


class ClientConfig(Singleton):

    def __init__(self):
        self.key = 'client_config'
        self.pool = get_index_pool()

    def set(self, version, data):
        with self.pool.ctx() as conn:
            return conn.execute("HSET", self.key, version, data)

    def get(self, version):
        with self.pool.ctx() as conn:
            return conn.execute("HGET", self.key, version)


class ConfigFiles(Singleton):

    def __init__(self, id):
        self.id = id
        self.key = "config_files.{}".format(id)
        self.pool = get_index_pool()
        self.md5_prefix = '_md5'
        self.files = RedisFetcher(
            "HGETALL",
            self.key,
            formatter=lambda s: {
                k: v for k,
                v in convert_list_to_dict(s).items() if not k.endswith("_md5")
            }, pool=self.pool)

    def get_file(self, name):
        with self.pool.ctx() as conn:
            return conn.execute("HGET", self.key, name)

    def get_file_md5(self, name):
        name_md5 = name + self.md5_prefix
        with self.pool.ctx() as conn:
            return conn.execute("HGET", self.key, name_md5)

    def set_file(self, name, source):
        m = md5.new(source)
        name_md5 = name + self.md5_prefix
        hexdigest = m.hexdigest()
        with self.pool.ctx() as conn:
            check_sum = self.get_file_md5(name)
            if check_sum == hexdigest:
                return
            conn.execute(
                "HMSET", self.key,
                name, source,
                name_md5, hexdigest)
            # FIXME
            path = "data/region{}".format(self.id)
            if not os.path.exists(path):
                os.mkdir(path)
            with open("data/region{}/{}.csv".format(self.id, name), "w") as f:
                f.write(source)

    def del_file(self, name):
        name_md5 = name + self.md5_prefix
        with self.pool.ctx() as conn:
            conn.execute("HDEL", self.key, name, name_md5)

    def get_names(self):
        with self.pool.ctx() as conn:
            return [e for e in conn.execute(
                "HKEYS", self.key
            ) if not e.endswith(self.md5_prefix)]

    def check_files(self, path):
        files = set()
        for filename in os.listdir(path):
            if not fnmatch.fnmatch(filename, "*.csv"):
                continue
            fullname = os.path.join(path, filename)
            name, _ = os.path.splitext(filename)
            with open(fullname) as f:
                self.set_file(name, f.read())
            files.add(name)
        for filename in self.get_names():
            name, _ = os.path.splitext(filename)
            if name not in files:
                self.del_file(name)

    def load_configs(self, configs, path, **sources):
        if not sources:
            sources = self.files.fetch()
        load(configs, path, **sources)
