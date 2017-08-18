# coding:utf-8
import re
import sys
import settings
regionID = sys.argv[1]
try:
    do = sys.argv[2] == "do"
except IndexError:
    do = False
print "regionID", regionID
index_pool = settings.REDISES["index"]
keys = index_pool.execute("KEYS", "*{%s}*" % regionID)
index_commands = []
for key in keys:
    if not re.findall(".*\{%s\}[^{].*" % regionID, key):
        continue
    print "DEL", key
    index_commands.append(["DEL", key])

user_pool = settings.REDISES["user"]
keys = user_pool.execute("KEYS", "roles_u{*}")
user_commands = []
for key in keys:
    print "HDEL", key, regionID
    user_commands.append(["HDEL", key, regionID])
if do:
    index_pool.execute_pipeline(*index_commands)
    user_pool.execute_pipeline(*user_commands)
