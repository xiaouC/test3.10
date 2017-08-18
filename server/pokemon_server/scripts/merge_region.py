# coding: utf-8
import settings
from common import index
from common.index import IndexString
from yy.entity.index import UniqueIndexing
from yy.entity.index import DuplicateIndexException
from yy.ranking import NaturalRanking
from yy.entity.index import SetIndexing
from yy.utils import group_list_by_two
from user.model import User
from session.regions import reload_regions, g_regions

"""
合服
可以重复执行
"""

reload_regions()
assert g_regions


def merge_index(key_name, regionID):
    key = getattr(index, key_name)
    merge_from = key.render(sessionID=SID, regionID=regionID)
    merge_to = key.render(sessionID=SID, regionID=RID)
    pool = settings.REDISES['index']
    type, _ = key_name.split("_", 1)
    print "Merge index %s to %s" % (merge_from, merge_to)
    if type == "INDEX":
        entity_pool = settings.REDISES["entity"]
        register_dup_names = False
        tag = ''
        if key_name == "INDEX_NAME":
            tag = 'p'
            register_dup_names = True
        elif key_name == "INDEX_FACTION_NAME":
            tag = 'f'
        elif key_name == "INDEX_GROUP_NAME":
            tag = 'g'
        if tag:
            index_to = UniqueIndexing(merge_to, pool)
            index_from = UniqueIndexing(merge_from, pool)
            #  { 仅作用玩家名称
            dup_names_key = index.SET_DUPLICATE_NAMES.render(
                sessionID=SID, regionID=RID)  # 存储需要修改名称的玩家集合
            dup_names = SetIndexing(dup_names_key, pool)
            #  }
            cur = 0
            while True:
                #  2.6 不支持HSCAN
                #  cur, vs = index_from.pool.execute("HSCAN", merge_from, cur)
                #  cur = int(cur)
                vs = index_from.pool.execute("HGETALL", merge_from)
                for name, entityID in group_list_by_two(vs):
                    name = name.decode("utf-8")
                    entityID = int(entityID)
                    exist_entityID = index_to.get_pk(name)
                    print "name:", name, "exist_entityID:",
                    print exist_entityID, "entityID:", entityID
                    if exist_entityID:
                        print "exist_entityID"
                        if exist_entityID != entityID:
                            print "exist_entityID != entityID"
                            name = name + " S%d" % regionID
                            entity_pool.execute(
                                "HSET", "%s{%d}" % (tag, entityID),
                                "name", name)
                            try:
                                index_to.register(entityID, name)
                            except DuplicateIndexException:
                                pass
                            if register_dup_names:
                                print "register_dup_names"
                                # 如果已存在的玩家ID不是自己，说明自己需要修改名称
                                dup_names.register(entityID)
                    else:
                        print "not exist_entityID"
                        index_to.pool.execute(
                            "HSET", index_to.key, name, entityID)
                    entity_pool.execute(
                        "HSETNX", "%s{%d}" % (tag, entityID),
                        "last_region_name", g_regions[regionID].name)
                # 修改当前区玩家的上次区服名
                vs2 = index_to.pool.execute("HGETALL", merge_to)
                for name, entityID in group_list_by_two(vs2):
                    entityID = int(entityID)
                    entity_pool.execute(
                        "HSETNX", "%s{%d}" % (tag, entityID),
                        "last_region_name", g_regions[RID].name)
                if cur == 0:
                    break
        else:
            print "Unknown index %s" % key_name
    else:
        cmds = []
        if type == "RANK":
            cmds = [
                ("ZUNIONSTORE", merge_to + "_tmp", 2,
                    merge_from, merge_to, "AGGREGATE", "MAX"),
                ('RENAME', merge_to + '_tmp', merge_to),
            ]
        elif type == "SET":
            cmds = [
                ("SUNIONSTORE", merge_to + "_tmp",
                    merge_from, merge_to),
                ('RENAME', merge_to + '_tmp', merge_to),
            ]
        elif type == "INT":
            val = pool.execute("GET", merge_from) or 0
            if val:
                cmds = [
                    ("INCRBY", merge_to, val),
                    ("DEL", merge_from),
                ]
        else:
            print "Unknown index type %r" % type
        if cmds:
            print pool.execute_pipeline(*cmds)


def merge_roles(regionID):
    merge_from = index.RANK_LEVEL.render(sessionID=SID, regionID=regionID)
    cur = 0
    pool = settings.REDISES["index"]
    entity_pool = settings.REDISES["entity"]
    user_pool = settings.REDISES["user"]
    index_from = NaturalRanking(merge_from, pool)
    print "Merge roles"
    while True:
        #  2.6 不支持ZSCAN
        #  cur, vs = index_from.pool.execute("HSCAN", merge_from, cur)
        #  cur = int(cur)
        vs = index_from.pool.execute("ZRANGE", merge_from, 0, -1)
        for entityID in vs:
            entityID = int(entityID)
            userID = int(entity_pool.execute(
                "HGET", "p{%d}" % entityID, "userID") or 0)
            print entityID
            if not userID:
                print "Not found userID for entityID %r" % userID
            else:
                rs = user_pool.execute("HGETALL", "roles_u{%d}" % userID)
                decoder = User.fields['roles'].decoder
                encoder = User.fields['roles'].encoder
                roles = {int(k): decoder(v) for k, v in group_list_by_two(rs)}
                print "before", roles
                exist_roles = roles.get(RID, [])
                if entityID not in exist_roles:
                    exist_roles.append(entityID)
                    roles.setdefault(RID, exist_roles)
                if regionID in roles:
                    del roles[regionID]
                print "after", roles
                user_pool.execute("HDEL", "roles_u{%d}" % userID, regionID)
                user_pool.execute(
                    "HMSET", "roles_u{%d}" % userID, *reduce(
                        lambda x, y: x + y,
                        [(k, encoder(v)) for k, v in roles.items()]))
        if cur == 0:
            break


def merge_region(regionID):
    for key_name in dir(index):
        key_value = getattr(index, key_name)
        if isinstance(key_value, IndexString):
            merge_index(key_name, regionID)
    merge_roles(regionID)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sessionID',     type=int, default=None)
    parser.add_argument('-t', '--t',   type=int, default=None, help="合并到的目标区")
    parser.add_argument('-f', '--f', type=int, help="需要合并的区")
    args = parser.parse_args()
    SID = args.sessionID or settings.SESSION["ID"]
    RID = args.t or settings.REGION["ID"]
    merge_region(args.f)
