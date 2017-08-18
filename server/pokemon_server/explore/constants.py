# coding:utf-8


class TreasureType:
    Gold = 1
    Silver = 2
    Copper = 3


class EventType:
    Fb = 1
    Chest = 2
    Chests = 3
    Task = 4
    Store = 5


class DlcFbType:
    Main = 1  # 主线
    Hero = 2  # 英雄
    Social = 3  # 社交
    Dispatch = 4  # 派遣
    Hidden = 5  # 隐藏


class MazeEventType:
    Noop = 0  # 无
    AddMoney = 1  # 增加金币
    DoubleMoney = 2  # 翻倍金币
    AddCount = 3  # 增加探索次数
    DoubleCount = 4  # 翻倍探索次数
    Drop = 5  # 奖励  直接进背包
    Case = 6  # 宝箱
    Boss = 7  # 副本
    Shop = 8  # 商店
