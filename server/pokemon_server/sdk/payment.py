import time
import settings
from yy.utils import convert_list_to_dict
from config.configs import get_config, RechargeConfig, RechargeBySdktypeConfig


def gen_payment(orderid, entityID, sdktype, goodsid, price=None):
    pool = settings.REDISES["payment"]
    key = "payment{%s}" % orderid
    with pool.ctx() as conn:
        rs = conn.execute("HSETNX", key, "orderid", orderid)
        if not rs:
            return rs
        arguments = ["orderid", orderid, "entityID", entityID]
        now = int(time.time())
        arguments.extend(["createtime", now])
        arguments.extend(["modifytime", now])
        # arguments.extend(["status", "SUCCESS"])
        arguments.extend(["sdktype", sdktype])
        arguments.extend(["goodsid", goodsid])
        if price is not None:
            sdkconfigs = get_config(RechargeBySdktypeConfig).get(sdktype, [])
            configs = get_config(RechargeConfig)
            ids = {e.id for e in sdkconfigs}
            good = {configs[e].goodsid: configs[e] for e in ids}.get(goodsid)
            arguments.extend(["price", good.amount])
        conn.execute("HMSET", key, *arguments)
        return rs


def get_payment(orderid):
    pool = settings.REDISES["payment"]
    key = "payment{%s}" % orderid
    with pool.ctx() as conn:
        rs = conn.execute("HGETALL", key)
        if not rs:
            return dict()
        payment = convert_list_to_dict(rs)
        return payment


def end_payment(orderid):
    pool = settings.REDISES["payment"]
    key = "payment{%s}" % orderid
    with pool.ctx() as conn:
        rs = conn.execute("HSETNX", key, "status", "SUCCESS")
        if not rs:
            return rs
        now = int(time.time())
        conn.execute("HSET", key, "modifytime", now)
        return rs
