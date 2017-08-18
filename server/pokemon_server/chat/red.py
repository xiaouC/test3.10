# coding:utf-8
import time
import settings
from gevent import kill
from gevent import sleep
from gevent import Greenlet
from yy.utils import convert_list_to_dict
from yy.message.header import success_msg
import protocol.poem_pb as msgid
from protocol import poem_pb
from player.manager import g_playerManager
from entity.manager import g_entityManager
from gm.proxy import proxy
from collections import deque
from collections import defaultdict
from config.configs import get_cons_value


class RedType:
    Normal = 1
    Horn = 2
    Red = 3


class RedModuleType:
    Daily = 1
    CityDungeon = 2
    CityContendAttack = 3
    CityContendDefend = 4
    System = 5


class ListIndexing(object):
    def __init__(self, key, pool):
        self.key = key
        self.pool = pool

    def lpush(self, *args):
        return self.execute("LPUSH", self.key, *args)

    def lpop(self):
        return self.execute("LPOP", self.key)

    def rpush(self, *args):
        return self.execute("RPUSH", self.key, *args)

    def execute(self, *args):
        return self.pool.execute(*args)

    def lrange(self, start, end):
        return self.pool.execute("LRANGE", self.key, start, end)

    def lrem(self, *args):
        return self.execute("LREM", self.key, 0, *args)

    def empty(self):
        return self.execute("DEL", self.key)

index_pool = settings.REDISES["index"]

RedQueue = ListIndexing("DAILY_RED_QUEUE{%d}{%d}" % (
    settings.SESSION["ID"], settings.REGION["ID"]), index_pool)

EndQueue = ListIndexing("DAILY_END_QUEUE{%d}{%d}" % (
    settings.SESSION["ID"], settings.REGION["ID"]), index_pool)


class RedManager(object):
    loop = None
    RED_TIMEOUT = 3
    reds = defaultdict(lambda: deque([], 10))
    MAX_IDLE_TIME = 10

    def run_red_loop(self):
        idle_times = 0
        while True:
            red = RedQueue.lpop()
            if red:
                info = self.get_red(red)
                if not info:
                    continue
                if not info.get("count", 0):
                    continue
                self.count_down_red(red)
                proxy.broadcast_red(red)
                EndQueue.rpush(red)
                sleep(self.RED_TIMEOUT)
            else:
                idle_times += 1
            if idle_times >= self.MAX_IDLE_TIME:
                break
            sleep(1)

    def send_red(self, p, count, info):
        red = "red{%d:%d}" % (p.entityID, int(time.time()))
        info.update(red=red, count=count)
        args = []
        for item in info.items():
            args.extend(item)
        index_pool.execute("HMSET", red, *args)
        RedQueue.rpush(red)
        self.start()

    def clean_red(self, module=RedModuleType.Daily):
        while True:
            red = EndQueue.lpop()
            if not red:
                break
            index_pool.execute("DEL", red)
        self.reds[module].clear()

    def start(self):
        if not self.loop or not self.loop.started:
            self.loop = Greenlet.spawn(self.run_red_loop)

    def stop(self):
        kill(self.loop)
        self.loop = None

    def get_red(self, red):
        info = convert_list_to_dict(index_pool.execute("HGETALL", red))
        if not info:
            return
        info["count"] = int(info["count"])
        info["prototypeID"] = int(info["prototypeID"])
        info["borderID"] = int(info["borderID"])
        info["type"] = int(info["type"])
        info["module"] = int(info["module"])
        info["drop"] = int(info["drop"])
        if info.get("time"):
            info["time"] = int(info["time"])
            info["cd"] = max(int(info["time"] - time.time()), 0)
        return info

    def recv_red(self, red):
        # -1 被领取完了， 0 超时， 1成功
        rest = index_pool.execute("HINCRBY", red, "count", -1)
        if rest < 0:
            index_pool.execute("HINCRBY", red, "count", 1)
            return -1
        t = index_pool.execute("HGET", red, "time")
        if time.time() > int(t):
            index_pool.execute("HINCRBY", red, "count", 1)
            return 0
        return int(index_pool.execute(
            "HGET", red, "drop") or get_cons_value("DailyRed"))

    def count_down_red(self, red):
        index_pool.execute(
            "HSET", red, "time",
            int(time.time()) + self.RED_TIMEOUT + 1)

    def send_red_message(
            self, p, message,
            red_count=0, cd=10, red_drop=0,
            to_self=False, type=RedType.Normal,
            module=RedModuleType.Daily, **kwargs):
        if not message.strip(" "):
            return
        t = str(float(time.time()))
        data = {
            "message": message,
            "type": type,
            "order": t,
            "to_self": to_self,
            "module": module,
            "drop": red_drop,
        }
        if isinstance(p, int):
            entityID = p
        else:
            entityID = p.entityID
            data.update({
                "name": p.name,
                "prototypeID": p.prototypeID,
                "borderID": p.borderID,
            })
        data.update(**kwargs)
        pb = poem_pb.RedInfo(**data)
        if type == RedType.Red:
            del data["to_self"]
            self.send_red(p, red_count, data)
        else:
            if to_self:
                msg = success_msg(msgid.DAILY_RED_INFO, pb)
                if g_playerManager.has_player(entityID):
                    g_playerManager.sendto(entityID, msg)
                else:
                    proxy.send_self_red_message(entityID, data)
            else:
                data["cd"] = cd
                proxy.broadcast_red_message(data)

    def get_red_messages(self, module=RedModuleType.Daily):
        return self.reds[module]

    def cache_red_message(self, info):
        module = info.get("module", RedModuleType.Daily)
        self.reds[module].append(info)


@proxy.rpc_batch
def broadcast_red(red):
    info = g_redManager.get_red(red)
    if not info:
        return
    g_redManager.cache_red_message(info)
    rsp = poem_pb.RedInfo(**info)
    msg = success_msg(msgid.DAILY_RED_INFO, rsp)
    for k, p in g_entityManager.players.items():
        g_playerManager.sendto(k, msg)


@proxy.rpc_batch
def broadcast_red_message(info):
    rsp = poem_pb.RedInfo(**info)
    if not info:
        return
    g_redManager.cache_red_message(info)
    msg = success_msg(msgid.DAILY_RED_INFO, rsp)
    for k, p in g_entityManager.players.items():
        g_playerManager.sendto(k, msg)


@proxy.rpc
def send_self_red_message(entityID, info):
    rsp = poem_pb.RedInfo(**info)
    if not info:
        return
    msg = success_msg(msgid.DAILY_RED_INFO, rsp)
    g_playerManager.sendto(entityID, msg)


def send_horn(message, cd=10, **kwargs):
    t = str(float(time.time()))
    data = {
        "message": message,
        "type": RedType.Horn,
        "order": t,
        "to_self": False,
        "module": RedModuleType.System,
        "cd": cd,
    }
    data.update(**kwargs)
    data["cd"] = cd
    g_redManager.cache_red_message(data)
    rsp = poem_pb.RedInfo(**data)
    print rsp
    msg = success_msg(msgid.BROADCAST_HORN, rsp)
    for k, p in g_entityManager.players.items():
        g_playerManager.sendto(k, msg)


@proxy.rpc_batch
def broadcast_horn(message, cd=10, **kwargs):
    send_horn(message, cd=10, **kwargs)


g_redManager = RedManager()
