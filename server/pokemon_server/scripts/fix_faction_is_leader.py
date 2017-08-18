# coding:utf-8

from yy.utils import load_settings
load_settings()
import settings

pool = settings.REDISES['entity']
keys = pool.execute('keys', 'f{*}')
cmds = []
for key in keys:
    leaderID, dflag = pool.execute('hmget', key, 'leaderID', 'dflag')
    if not leaderID or dflag:
        continue
    factionID = key.replace("f{", '').replace("}", "")
    cmds.append(["hset", "p{%s}" % leaderID, "faction_is_leader", 1])
pool.execute_pipeline(*cmds)
