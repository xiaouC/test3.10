# coding:utf-8
import json
from yy.utils import convert_list_to_dict
import settings

pool = settings.REDISES['user']
keys = pool.execute('keys', 'u{*}')
for key in keys:
    key = "roles_%s" % key
    cmds = ["HMSET", key]
    roles = convert_list_to_dict(pool.execute("HGETALL", key))
    for regionID, roleID in roles.items():
        roleID = json.loads(roleID)
        if not isinstance(roleID, list):
            cmds.extend([regionID, json.dumps([int(roleID)])])
    if len(cmds) == 2:
        continue
    print cmds
    pool.execute(*cmds)
