# coding:utf-8
import settings
from credis import RedisReplyError
from yy.db.redisscripts import load_redis_script


@load_redis_script(pool=settings.REDISES["index"])
def _copy(key1, key2):
    """
    local serialized = redis.call("DUMP", KEYS[1])
    if serialized then
        local ok = redis.call("RESTORE", KEYS[2], 0, serialized)
        return ok
    else
        return "OK"
    end
    """
    return (key1, key2), tuple()


@load_redis_script(pool=settings.REDISES["index"])
def _copy_and_del(key1, key2):
    """
    local serialized = redis.call("DUMP", KEYS[1])
    if serialized then
        local ok = redis.call("RESTORE", KEYS[2], 0, serialized)
        redis.call("DEL", KEYS[1])
        return ok
    else
        return "OK"
    end
    """
    return (key1, key2), tuple()


@load_redis_script(pool=settings.REDISES["index"])
def __copy(key1, key2, delete, replace):
    """
    local delete = KEYS[3]
    local replace = KEYS[4]
    local serialized = redis.call("DUMP", KEYS[1])
    if serialized then
        if replace ~= "0" then
            redis.call("DEL", KEYS[2])
        end
        local ok = redis.call("RESTORE", KEYS[2], 0, serialized)
        if delete ~= "0" then
            redis.call("DEL", KEYS[1])
        end
        return ok
    else
        if replace ~= "0" then
            redis.call("DEL", KEYS[2])
            return "OK"
        else
            return nil
        end
    end
    """
    return (key1, key2, delete, replace), tuple()


def copy(key1, key2, delete=False, replace=False):
    try:
        rs = __copy(key1, key2, delete, replace)
        return rs == "OK"
    except RedisReplyError:
        return False
