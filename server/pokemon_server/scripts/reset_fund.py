# coding:utf-8
"""
重置开服基金活动
"""
import time
import settings
from common.index import INT_FUND_BOUGHT_COUNT

pool = settings.REDISES["index"]


def reset_fund(sessionID, regionID):
    now = int(time.time())
    print "SET", "FUND_RESET_TIME{%d}{%d}" % (sessionID, regionID), now
    print pool.execute(
        "SET", "FUND_RESET_TIME{%d}{%d}" % (sessionID, regionID), now)
    print "DEL", INT_FUND_BOUGHT_COUNT.render(
        sessionID=sessionID, regionID=regionID)
    print pool.execute("DEL", INT_FUND_BOUGHT_COUNT.render(
        sessionID=sessionID, regionID=regionID))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sessionID', type=int)
    parser.add_argument('-r', '--regionID', type=int)
    args = parser.parse_args()
    reset_fund(args.sessionID, args.regionID)
