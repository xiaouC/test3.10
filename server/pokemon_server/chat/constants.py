# coding:utf-8
from protocol.poem_pb import ChatType

ChatType  # {System = 1; Tips = 2; World = 3; Faction = 4; Group = 5}


class NewsType:
    PetQualityLottery = 1  # 玩家抽到某品质将
    PetSpecialLottery = 2  # 玩家抽到特定将
    PetQualityCompose = 3  # 玩家合成某品质将
    PetSpecialCompose = 4  # 玩家合成特定将
    PetQualityEvolute = 5  # 玩家进化精灵到某品质
    EquipQualityLottery = 6  # 玩家抽到某品质装备
    EquipQualityCompose = 7  # 玩家合成某品质装备
    EquipStepAdvance = 8  # 玩家进阶装备到满阶
    PetBreaklevelBreak = 9  # 玩家升阶精灵到满星
    PvpFirst = 10  # PVP第一名换人
    FoundFriendfb = 11  # 发现秘境
    Wish = 12  # 许愿
    PetCompose = 13  # 精灵渡魂
    EquipCompose = 14  # 装备炼器
    SparPet = 15  # 占星精灵
    SparEquip = 16  # 占星神器
    Visit = 17  # 转盘
    PetExchange1 = 18  # 精灵置换
    PetExchange2 = 19  # 精灵置换
    PetExchange3 = 20  # 精灵置换
    PetExchange4 = 21  # 精灵置换
