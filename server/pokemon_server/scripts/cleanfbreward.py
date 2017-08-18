# coding:utf-8

from yy.utils import load_settings
load_settings()
import settings

pool = settings.REDISES['entity']
keys = pool.execute('keys', 'p{*}')
cmds = []
for key in keys:
    ck = key.replace("p{", "").replace("}", "")
    cmds.append(['del', 'fbreward_p{%s}' % ck])
pool.execute_pipeline(*cmds)
