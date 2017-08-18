# coding: utf-8
import os, glob
from credis.base import RedisReplyError, Connection
from yy.utils import parse_redis_url

g_scripts = {}

def load_script(pool, source):
    'nutcracker 暂不支持 script load，特殊处理一下'
    sha = None
    if pool.name == 'nutcracker':
        import settings
        assert settings.NUTCRACKER_REDISES
        for url in settings.NUTCRACKER_REDISES:
            info = parse_redis_url(url)
            info.pop('name', None)
            info.pop('poolmax', None)
            sha = Connection(**info).execute('SCRIPT', 'LOAD', source)
    else:
        sha = pool.execute('SCRIPT', 'LOAD', source)
    return sha

class RedisScript(object):
    def __init__(self, name, source):
        self.shas = {}
        self.name = name
        self.source = source

    def __call__(self, keys, args, pool=None):
        if pool is None:
            from yy.db.redismanager import g_redismanager
            pool = g_redismanager
        with pool.ctx() as conn:
            if pool not in self.shas:
                self.shas[pool] = load_script(pool, self.source)
            try:
                return conn.execute('EVALSHA', self.shas[pool], len(keys), *(keys+args))
            except RedisReplyError as e:
                if e.message.startswith('NOSCRIPT'):
                    self.shas[pool] = load_script(pool, self.source)
                    return conn.execute('EVALSHA', self.shas[pool], len(keys), *(keys+args))
                else:
                    raise

def execute_script(name, keys, argv, pool=None):
    return g_scripts[name](keys, argv, pool=pool)

def init_scripts(files):
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0]
        content = open(f).read()
        g_scripts[name] = RedisScript(name, content)

def load_redis_script(func=None, script_file_name=None, pool=None, arg_name_for_pool="pool"):
    def wrapper(func):
        def get_source():
            if script_file_name:
                with open(script_file_name, 'r') as f:
                    return f.read()
            else:
                return func.__doc__.strip(' ')

        def inner(*args, **kwargs):
            _pool = pool
            if not _pool and args:
                _pool = getattr(args[0], arg_name_for_pool, None)
            assert _pool, "Not specific pool"
            keys, vals = func(*args, **kwargs)
            with _pool.ctx() as conn:
                if not hasattr(func, "__redis_eval_sha") or not func.__redis_eval_sha:
                    func.__redis_eval_sha = load_script(_pool, get_source())
                try:
                    cmds = ("EVALSHA", func.__redis_eval_sha, len(keys)) + keys + vals
                    return conn.execute(*cmds)
                except RedisReplyError as e:
                    if e.message.startswith('NOSCRIPT'):
                        func.__redis_eval_sha = load_script(_pool, get_source())
                        cmds = ("EVALSHA", func.__redis_eval_sha, len(keys)) + keys + vals
                        return conn.execute(*cmds)
                    else:
                        raise
        inner.__name__ = func.__name__
        inner.__doc__ = func.__doc__
        return inner
    if func:
        return wrapper(func)
    return wrapper

d = os.path.join(os.path.dirname(__file__), 'redis_scripts', '*.lua')
init_scripts(glob.glob(d))
