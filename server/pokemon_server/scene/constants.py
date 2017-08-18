# coding:utf-8


class FbType:
    Guide = 0  # 引导
    Normal = 1  # 普通
    Advanced = 2  # 精英
    Campaign = 3  # 活动
    Trigger = 4  # 触发
    Dlc = 5  # Dlc
    Gve = 6
    Maze = 7


class SceneSubType:
    Dongtian = 1  # 洞天
    Fudi = 2  # 福地

TransFbType = {
    FbType.Guide: u"引导副本",
    FbType.Normal: u"普通副本",
    FbType.Advanced: u"精英副本",
    FbType.Campaign: u"活动副本",
    FbType.Trigger: u"触发副本",
    FbType.Dlc: u"Dlc副本",
    FbType.Gve: u"Gve副本"
}


class CycleType:
    Week = 1  # 周
