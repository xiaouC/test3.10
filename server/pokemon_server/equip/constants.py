# coding:utf-8
from protocol.poem_pb import EquipTypeFaBao, EquipTypeTouKui, EquipTypeXueZi
from protocol.poem_pb import EquipTypeFangJu,  EquipTypeWuqi, EquipTypeZuoQi


class EquipType:
    Wuqi = EquipTypeWuqi
    FangJu = EquipTypeFangJu
    TouKui = EquipTypeTouKui
    XueZi = EquipTypeXueZi
    FaBao = EquipTypeFaBao
    ZuoQi = EquipTypeZuoQi


class EquipAttrType:
    Atk = 1  # 攻击
    Def = 2  # 防御
    Hp = 3  # 血量
    Cri = 4  # 暴击%（0.5代表0.5%）
    Dodge = 5  # 闪避%
