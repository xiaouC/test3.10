# coding:utf-8

from yy.utils import load_settings
load_settings()
import settings

pool = settings.REDISES['entity']
keys = pool.execute('keys', 'p{*}')
cmds = []
MAX_LEVEL = 50
for key in keys:
    level = int(pool.execute("hget", key, "level") or 1)
    print level
    if level > MAX_LEVEL:
        print pool.execute("hset", key, "level", MAX_LEVEL)
