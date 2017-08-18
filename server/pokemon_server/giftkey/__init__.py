# coding:utf-8
import time
import string
from yy.utils import load_settings
load_settings()
import settings
from config.configs import get_config, GiftkeyConfig
from yy.utils import get_rand_string
from yy.utils import convert_list_to_dict
from session.utils import username2sdk


class InvalidGiftkeyError(Exception):
    pass


class ExceedUseCountError(Exception):
    pass


class ExceedDeallineError(Exception):
    pass


sample = string.translate(
    string.ascii_lowercase + string.digits,
    # string.ascii_letters + string.digits,
    None, "6bIl1Oo0")  # Filtering the similar characters
_pool = settings.REDISES['giftkey']


def get_key(count=12):
    return get_rand_string(count, allowed_chars=sample)


def gen_key(giftID, giftkey="", count=1, channels=None, servers=None):
    keys = []
    if giftkey and count != 1:  # 指定了giftkey，那么count只能指定1
        raise AssertionError
    key = giftkey.lower()
    with _pool.ctx() as conn:
        for i in range(count):
            if key:
                # 若指定了giftkey，如果该giftkey已经存在，那么生成失败
                giftkey = key
                if conn.execute("EXISTS", "giftkey{%s}" % giftkey):
                    return keys
            else:
                giftkey = get_key()
                while conn.execute("EXISTS", giftkey):
                    giftkey = get_key()
            arguments = ["giftID", giftID]
            if channels:
                arguments.extend(["channels", channels])
            if servers:
                arguments.extend(["servers", servers])
            conn.execute("HMSET", "giftkey{%s}" % giftkey, *arguments)
            keys.append(giftkey)
    return keys


def use_key(player, key):
    sdk = username2sdk(player.username)
    key = key.lower()
    with _pool.ctx() as conn:
        info = convert_list_to_dict(
            conn.execute("HGETALL", "giftkey{%s}" % key))
        if not info:
            raise InvalidGiftkeyError
        giftID_key = info["giftID"]  # player.giftkeys 的 key需要是字符串
        info["giftID"] = giftID = int(info["giftID"])
        info["used"] = int(info.get("used") or 0)
        info["channels"] = filter(
            lambda s: s, info.get("channels", "").split(","))
        info["servers"] = map(
            int, filter(lambda s: s, info.get("servers", "").split(",")))
        configs = get_config(GiftkeyConfig)
        config = configs.get(giftID)
        if not config:
            raise InvalidGiftkeyError
        # 区服限制
        if info["servers"] and settings.REGION["ID"] not in info["servers"]:
            raise InvalidGiftkeyError
        # 渠道限制
        if info["channels"] and sdk not in info["channels"]:
            raise InvalidGiftkeyError
        # 同组的只能领取一次
        groups = set()
        for i in player.giftkeys.keys():
            c = configs.get(int(i))
            if c:
                groups.add(c.group)
        if config.group in groups:
            if giftID_key not in player.giftkeys:
                raise ExceedUseCountError
        # 单个玩家次数限制
        each_used = player.giftkeys.get(giftID_key, 0)
        if config.each_use_count != -1:  # -1表示不限制
            if each_used >= config.each_use_count:
                raise ExceedUseCountError
        now = int(time.time())
        # 时间限制
        if config.start_time and now < config.start_time:
            raise ExceedDeallineError
        if config.end_time and now >= config.end_time:
            raise ExceedDeallineError
        used = conn.execute("HINCRBY", "giftkey{%s}" % key, "used", 1)
        # 使用总次数限制
        if config.use_count != -1:  # -1表示不限制
            if used > config.use_count:
                conn.execute("HINCRBY", "giftkey{%s}" % key, "used", -1)
                raise ExceedUseCountError
        player.giftkeys[giftID_key] = player.giftkeys.get(giftID_key, 0) + 1
        player.save()
        return giftID
