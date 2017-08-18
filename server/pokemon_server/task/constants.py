# coding:utf-8


class TaskType:
    Daily = 1  # 日常奖励
    Normal = 2  # 任务奖励
    Achieve = 3  # 成就奖励
    Sign = 4  # 签到奖励
    DailySP = 5  # 每日能量
    Noob = 8  # 新手好礼
    Faction = 9  # 公会
    Trigger = 10  # 触发
    Dlc = 11  # DLC任务
    DailyPVP = 12  # 每日PVP
    Seven = 13  # 七天
    Progress = 14  # 历程


class TaskSubType:
    Default = 0
    Growth = 1
    Resource = 2
    Team = 3
    Battle = 4


class TaskCond:
    FBCount = 1  # 完成关卡次数  {1 普通,2 精英,3 活动}
    Levelup = 2  # 达到等级
    BuySPCount = 3  # 购买能量
    BreedCount = 4  # 完成升级次数
    EvolutionCount = 5  # 完成进化次数
    Money = 6  # 累计获得金币
    RebornCount = 7  # 复活
    LotteryCount = 8  # 完成抽卡次数
    RankCount = 9  # 完成pvp次数
    BestPetCount = 10  # 收集精灵      {1， 2， 3， 4， 5} 星级
    RankSeasonCount = 11  # 赛季完成pvp次数
    RefreshShopCount = 12  # 刷新商店
    Signup = 13  # 签到
    SpecFBCount = 14  # 完成特定关卡  {fbID}
    PatchExchange = 15  # 碎片兑换精灵
    DailySP = 16  # 每日能量
    GoldenFinger = 17  # 炼银
    MonthlyCard30 = 18  # 月卡
    ShoppingCount = 19  # 商店购买
    VipLevel = 20  # VIP等级
    RankWinCount = 21  # PvP主动战斗胜利次数
    LotteryCount10 = 22  # 钻石十连抽次数
    Login = 23  # 登录
    RobCount = 24  # 抢天庭——今日抢夺XX次
    Rob = 25  # 抢天庭——累计抢夺XXX {1金币 2水晶}
    Collect = 26  # 抢天庭——累计采集XXX {1金币 水晶}
    UproarCount = 27  # 大闹天宫—通关XX关
    UproarReset = 28  # 大闹天宫—重置一次大闹天宫
    LootComposeZuoqi = 29  # 蓬莱夺宝——合成出了品质X的坐骑1个{1.....}
    LootComposeFabao = 30  # 蓬莱夺宝——合成出了品质X的法宝1个{1.....}
    LootCount = 31   # 蓬莱夺宝——进行一次蓬莱夺宝
    UproarSerialCount = 32  # 大闹天宫—连续通关xx关
    TapCount = 33  # 群魔乱舞参与次数
    TreasureCount = 34  # 金银山参与次数
    DlcFbCount = 35  # 指定数量Dlc英雄关等等
    DlcScoreCount = 36  # Dlc星数
    CollectPet1 = 37  # 收集精灵（包括进化和抽卡）
    CollectPet2 = 38  # 收集精灵（包括合成和抽卡）
    CollectEquip = 39  # 收集专属装备
    AdvanceEquip = 40  # 进阶装备
    PetFusionCount = 41  # 精灵合成次数
    SparCount = 42  # 占星台次数
    Jiutian = 43  # 大闹天宫累计获得九天币
    DongtianFudiMoney = 44  # 洞天福地获取总量 （金币）
    DongtianFudiSoul = 45  # 洞天福地获取总量 （水晶）
    Skillup = 46  # 技能升级次数
    Gold = 47  # 累计获得钻石
    Soul = 48  # 累计获得水晶
    Point = 49  # 累计获得成就
    MazeCount = 50  # 迷宫探索次数（包含扫荡）
    SwapRank = 51  # PVP最高排名
    FriendsCount = 52  # 好友个数
    FriendfbFirst = 53  # 秘境第一
    FriendfbCount = 54  # 秘境次数
    SwapRankCount = 55  # 交换排名竞技场次数
    SwapRankWinCount = 56  # 交换排名竞技场胜利场次
    DailyPVPCount = 57  # 每日PVP胜利次数
    BreakPet = 58  # 升星到对应星级
    StrengthenEquipCount = 59  # 装备强化次数
    EnhantEquipCount = 60  # 装备洗炼次数
    AmbitionCount = 61  # 集训次数
    Maxpower = 62  # 巅峰站力达到
    FactionLevel = 63  # 公会等级
    PlayerEquipStrengthenCount = 64  # 玩家装备强化次数


class DailySPState:
    Close = 1  # 未开启
    Open = 2  # 开启中
    Hide = 3  # 隐藏
