# coding:utf-8
import ujson
import cPickle
import traceback
from bottle import request
from urllib3 import PoolManager
from inspect import getcallargs, getmodule
from urllib import urlencode
from urlparse import urlsplit, parse_qs, urlunsplit

from yy.utils import choice_one

import settings
WORLD = settings.WORLD
PROXY = settings.PROXY
REGION = settings.REGION
main_package = settings.main_package
index_pool = settings.REDISES["index"]

from session.regions import g_regions

poolmanager = None


class DuplicateError(Exception):
    pass


def get_poolmanager():
    global poolmanager
    if not poolmanager:
        poolmanager = PoolManager()
    return poolmanager


SUCCESS = ujson.dumps("success")
FAILURE = ujson.dumps("failure")


def urljoin(host, port, path=""):
    # FIXME
    return '/'.join(filter(
        lambda s: s, ['http://{}:{}'.format(host, port), path])
    )


def set_query_string(url, **kwargs):
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    for k, v in kwargs.items():
        query_params[k] = [v]
    new_query_string = urlencode(query_params, doseq=True)
    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


def combine_int(x, y):
    return x + y


def combine_sequence(x, y):
    cast = type(x)
    if cast != list:
        x = list(x)
    x.extend(y)
    if cast != list:
        x = cast(x)
    return x


def combine_dict(x, y):
    for k, v in x.items():
        if isinstance(v, (int, float)):
            x[k] = combine_int(v, y[k])
        elif isinstance(v, (list, set, tuple)):
            x[k] = combine_sequence(v, y[k])
        elif isinstance(v, dict):
            x[k] = combine_dict(v, y[k])
    return x


def combine_result(x, y):
    assert isinstance(x, type(y)), 'Assert x, y are same type'
    if isinstance(x, (int, float)):
        return combine_int(x, y)
    elif isinstance(x, (list, set, tuple)):
        return combine_sequence(x, y)
    elif isinstance(x, dict):
        return combine_dict(x, y)
    elif isinstance(x, basestring):
        return x


def proxy_request(url, *args, **kwargs):
    body = cPickle.dumps((args, kwargs))
    rsp = get_poolmanager().urlopen("POST", url, body=body)
    try:
        data = ujson.loads(rsp.data)
    except ValueError:
        traceback.print_exc()
        data = None
    return data


def proxy_batch_call(f, regionID, *args, **kwargs):
    proxy_url = urljoin(PROXY["host"], PROXY["port"])
    if callable(f):
        m = getmodule(f)
        fullname = '.'.join([m.__name__, f.__name__])
    else:
        fullname = f
    url = "/".join([proxy_url, "RPC_BATCH", fullname])
    url = set_query_string(url, regionID=regionID)
    return proxy_request(url, *args, **kwargs)


class ServerProxy(object):

    def __init__(self, type):
        self.type = type

    def rpc(self, f=None, **kwargs):
        return f

    def batch(self, f=None, **kwargs):
        return f

    def every(self, f=None, **kwargs):
        return f

    def specific(self, f=None, **kwargs):
        return f

    def random(self, f=None, **kwargs):
        return f

    def __call__(self, key=None, **kwargs):
        def deco(f):
            return f
        return deco


class ServerProxyMaster(ServerProxy):

    def __init__(self, *args, **kwargs):
        super(ServerProxyMaster, self).__init__("Master")

    def prepare_query(self, worlds):
        if not worlds:
            return [], None, None, None
        method = request.method
        body = request.body.read()
        headers = request.headers
        path = request.path.strip('/')
        urls = []
        for world in worlds:
            url = urljoin(world.managehost, world.manageport, path)
            if method == "GET":
                if request.query_string:
                    url = "?".join([url, request.query_string])
            urls.append(url)
        return urls, method, body, headers

    def query(self, url, method="GET", body=None, headers=None):
        rsp = get_poolmanager().urlopen(
            method,
            url,
            body=body,
            headers=dict(headers))
        if not rsp.data:
            return FAILURE
        try:
            return ujson.loads(rsp.data)
        except ValueError:
            return cPickle.loads(rsp.data)

    def batch_query(self, urls, method="GET", body=None, headers=None):
        rsps = []
        for url in urls:
            rsp = self.query(url, method, body, headers)
            rsps.append(rsp)
        if not rsps:
            return FAILURE
        result = reduce(combine_result, rsps)
        return ujson.dumps(result)

    def batch(self, f=None):
        def deco(f):
            def _proxy(*args, **kwargs):

                regionID = int(request.GET["regionID"])
                fromWorldID = request.GET.get("fromWorldID")
                region = g_regions.get(regionID)
                if not region:
                    return FAILURE
                ws = region.worlds
                if fromWorldID is not None:
                    fromWorldID = int(fromWorldID)
                    ws.pop(fromWorldID, None)
                worlds = ws.values()

                rs = self.batch_query(*self.prepare_query(worlds))
                return rs
            return _proxy
        if f:
            return deco(f)
        return deco

    def every(self, f=None):
        def deco(f):
            def _proxy(*args, **kwargs):

                worlds = []
                for r in g_regions.values():
                    worlds.extend(r.worlds.values())

                return self.batch_query(*self.prepare_query(worlds))
            return _proxy
        if f:
            return deco(f)
        return deco

    def specific(self, f=None):
        '''向指定world服务器发送请求'''
        def deco(f):
            def _proxy(*arggs, **kwargs):

                regionID = int(request.GET["regionID"])
                worldID = int(request.GET["worldID"])
                region = g_regions.get(regionID)
                if not region:
                    return FAILURE
                world = region.worlds[worldID]
                worlds = [world]

                return self.batch_query(*self.prepare_query(worlds))
            return _proxy
        if f:
            return deco(f)
        return deco

    def random(self, f=None):
        '''随机挑选一个world服务器'''
        def deco(f):
            def _proxy(*args, **kwargs):

                regionID = int(request.GET["regionID"])
                region = g_regions.get(regionID)
                if not region:
                    return FAILURE
                worldIDs = region.worlds.keys()
                w = choice_one(worldIDs)
                worlds = []
                if w:
                    worlds.append(region.worlds[w])

                return self.batch_query(*self.prepare_query(worlds))
            return _proxy
        if f:
            return deco(f)
        return deco

    def __call__(self, key=None):
        def deco(f):
            def _proxy(*args, **kwargs):

                # from player.model import Player
                val = int(getcallargs(f, *args, **kwargs)[key])
                regionID = int(request.GET["regionID"])
                # w = Player.simple_load(val, ["worldID"]).worldID
                w = int(index_pool.execute(
                    "HGET",
                    "index_p_online{%d}{%d}" % (
                        regionID, settings.SESSION["ID"]),
                    val) or 0)
                region = g_regions.get(regionID)
                if not region:
                    return FAILURE
                if not w:
                    worldIDs = region.worlds.keys()
                    w = choice_one(worldIDs)
                    if w:
                        worlds = [region.worlds[w]]
                    else:
                        worlds = []
                else:
                    worlds = [region.worlds[w]]

                return self.batch_query(*self.prepare_query(worlds))
            return _proxy
        return deco


class LocateError(Exception):
    pass


class ServerProxyNode(ServerProxy):

    def __init__(self, host=None, port=None):
        super(ServerProxyNode, self).__init__("Node")
        if not host:
            host = PROXY["host"]
        self.proxy_host = host
        if not port:
            port = PROXY["port"]
        self.proxy_port = port
        self.proxy_url = urljoin(self.proxy_host, self.proxy_port)
        self.rpc_methods = {}

    def locate(self, key):
        path, err = self.route(key)
        if err:
            raise LocateError
        return path

    def route(self, key):
        # from player.model import Player
        from player.model import PlayerOnlineIndexing
        # w = Player.simple_load(key, ["worldID"]).worldID
        w = PlayerOnlineIndexing.get_pk(key)
        return (REGION["ID"], w), not bool(w)

    def can_do_local(self, key):
        from entity.manager import g_entityManager
        return bool(g_entityManager.get_player(key))

    def ping(self):
        url = urljoin(self.proxy_host, self.proxy_port, "ping")
        get_poolmanager().urlopen("GET", url)

    def get(self, uri, *args, **kwargs):
        url = urljoin(self.proxy_host, self.proxy_port, uri)
        return get_poolmanager().request("GET", url, *args, **kwargs)

    def post(self, uri, *args, **kwargs):
        url = urljoin(self.proxy_host, self.proxy_port, uri)
        return get_poolmanager().request("POST", url, *args, **kwargs)

    def request(self, url, *args, **kwargs):
        return proxy_request(url, *args, **kwargs)

    def rpc_across(
            self, f=None, failure=None, across="regionID"):
        def deco(f):
            def _proxy(*args, **kwargs):
                regionID = int(getcallargs(f, *args, **kwargs).get(across))
                if regionID and regionID == REGION["ID"]:
                    return f(*args, **kwargs)
                else:
                    m = getmodule(f)
                    fullname = '.'.join([m.__name__, f.__name__])
                    url = "/".join([self.proxy_url, "RPC_RANDOM", fullname])
                    url = set_query_string(
                        url, regionID=regionID)
                    return self.request(url, *args, **kwargs)
            _proxy.__name__ = f.__name__
            if f.__name__ in self.rpc_methods:
                raise DuplicateError("Duplicate method: %s" % f.__name__)
            self.rpc_methods[f.__name__] = (_proxy, failure)
            return f  # Return the pure function
        if f:
            return deco(f)
        return deco

    def rpc(self, f=None, failure=None, key="entityID"):
        def deco(f):
            def _proxy(*args, **kwargs):

                val = int(getcallargs(f, *args, **kwargs)[key])
                if self.can_do_local(val):
                    return f(*args, **kwargs)
                try:
                    regionID, worldID = self.locate(val)
                    if worldID == WORLD["ID"]:  # No more redirect
                        if failure:
                            return failure(*args, **kwargs)
                        return
                except LocateError:
                    if failure:
                        return failure(*args, **kwargs)
                else:
                    m = getmodule(f)
                    fullname = '.'.join([m.__name__, f.__name__])
                    url = "/".join([self.proxy_url, "RPC", fullname])
                    url = set_query_string(
                        url, regionID=regionID, worldID=worldID)
                    return self.request(url, *args, **kwargs)

            _proxy.__name__ = f.__name__
            if f.__name__ in self.rpc_methods:
                raise DuplicateError("Duplicate method: %s" % f.__name__)
            self.rpc_methods[f.__name__] = (_proxy, failure)
            return f  # Return the pure function
        if f:
            return deco(f)
        return deco

    def rpc_batch(self, f=None):
        def deco(f):
            # FIXME return value NOTE
            def _proxy(*args, **kwargs):
                local = f(*args, **kwargs)  # Do local first
                m = getmodule(f)
                fullname = '.'.join([m.__name__, f.__name__])
                url = "/".join([self.proxy_url, "RPC_BATCH", fullname])
                url = set_query_string(
                    url, regionID=REGION["ID"], fromWorldID=WORLD["ID"])
                rs = self.request(url, *args, **kwargs)
                if rs == 'failure':  # 临时
                    return local
                else:
                    if hasattr(rs, "extend"):
                        rs.extend(local)
                    return rs

            _proxy.__name__ = f.__name__
            if f.__name__ in self.rpc_methods:
                raise DuplicateError("Duplicate method: %s" % f.__name__)
            self.rpc_methods[f.__name__] = (_proxy, None)
            # FIXME fix the "pure_" prefix
            if 'pure_' + f.__name__ in self.rpc_methods:
                raise DuplicateError("Duplicate method: %s" % f.__name__)
            self.rpc_methods["pure_"+f.__name__] = (f, None)
            return f  # Return the pure function
        if f:
            return deco(f)
        return deco

    def __getattr__(self, name):
        try:
            method, _ = self.rpc_methods[name]
        except KeyError:
            raise AttributeError(name)
        return method

if main_package in ("world", "region", "sdk", "bench"):
    proxy = ServerProxyNode()
else:
    proxy = ServerProxyMaster()
