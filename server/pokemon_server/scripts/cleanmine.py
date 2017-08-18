# coding:utf-8

from yy.utils import load_settings
load_settings()
import settings

pool = settings.REDISES['entity']
keys = pool.execute('keys', 'p{*}')
cmds = []
for key in keys:
    cmds.append(['hdel', key, 'mine_safety1'])
    cmds.append(['hdel', key, 'mine_safety2'])
    cmds.append(['hdel', key, 'mine_maximum1'])
    cmds.append(['hdel', key, 'mine_maximum2'])
pool.execute_pipeline(*cmds)
