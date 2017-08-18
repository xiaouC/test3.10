#coding:utf-8

from yy.utils import load_settings
load_settings()
import settings

pool = settings.REDISES['entity']
keys = pool.execute('keys', 'p{*}')
cmds = []
for key in keys:
    cmds.append(['hdel', key, 'pvprankreceiveds'])
pool.execute_pipeline(*cmds)    
