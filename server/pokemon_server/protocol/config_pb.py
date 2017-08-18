# coding: utf-8
from cprotobuf import ProtoEntity, Field
# file: config/awardsysinfo.proto
class awardsysinfo(ProtoEntity):
    id              = Field('int32',	1)
    taskType        = Field('int32',	2)
    planValue       = Field('int32',	3)
    rewardID        = Field('int32',	4)
    desc            = Field('string',	5)
    conditionType   = Field('int32',	6)
    icon            = Field('string',	7)
    map             = Field('int32',	8)
    heroType        = Field('int32',	9)
    destination     = Field('int32',	10)

# file: config/building.proto
class buildingLevelData(ProtoEntity):
    level           = Field('int32',	1)
    levelupCost     = Field('int32',	2)
    levelupTime     = Field('int32',	3)
    silverCount     = Field('int32',	4, required=False)
    skillid         = Field('int32',	5, repeated=True)
    stoneCount      = Field('int32',	6, required=False)
    silverCount_yqs = Field('int32',	7, required=False)

class buildingInfo(ProtoEntity):
    # enum conditionType
    PlayerLvl=1
    DabenyingLvl=2
    FinishTask=3
    ThoughFB=4
    ChengMen=5
    id              = Field('int32',	1)
    name            = Field('string',	2)
    icon            = Field('int32',	3, required=False)
    levelData       = Field(buildingLevelData,	4, repeated=True)
    contype         = Field('enum',	5)
    conparam        = Field('int32',	6)

# file: config/challbook.proto
class challbook(ProtoEntity):
    Fbid            = Field('int32',	1)
    heroId          = Field('int32',	2)
    type1           = Field('int32',	3)
    materId1        = Field('int32',	4)
    count1          = Field('int32',	5)
    type2           = Field('int32',	6)
    materId2        = Field('int32',	7)
    count2          = Field('int32',	8)
    type3           = Field('int32',	9)
    materId3        = Field('int32',	10)
    count3          = Field('int32',	11)

# file: config/challenge.proto
class ChallengeTitleConfig(ProtoEntity):
    id              = Field('int32',	1)
    name            = Field('string',	2)
    scoreMin        = Field('int32',	3)
    scoreMax        = Field('int32',	4)
    frame           = Field('int32',	5)

class ChallegeBoxConfig(ProtoEntity):
    id              = Field('int32',	1)
    money           = Field('int32',	2)
    factor          = Field('int32',	3)

# file: config/challengerAwardInfo.proto
class challengerAwardInfo(ProtoEntity):
    id              = Field('int32',	1)
    des             = Field('string',	2)

# file: config/challengerank.proto
class ChallegeRankConfig(ProtoEntity):
    rank            = Field('int32',	1)
    scroe           = Field('int32',	2)
    playerId        = Field('int32',	3)
    icon            = Field('int32',	4)
    name            = Field('string',	5)
    level           = Field('int32',	6)
    spirit          = Field('int32',	7)
    scoreTime       = Field('int32',	8)

class ChallengeRankList(ProtoEntity):
    rankData        = Field(ChallegeRankConfig,	1, repeated=True)
    rankUpdateTime  = Field('int32',	2, required=False)

# file: config/decorateCost.proto
class DecorateCost(ProtoEntity):
    count           = Field('int32',	1)
    normalCost      = Field('int32',	2)
    lockCost        = Field('int32',	3)

# file: config/droppack.proto
class newDroppack(ProtoEntity):
    dropID          = Field('int32',	1)
    packID          = Field('int32',	2)
    type1           = Field('int32',	3)
    item1           = Field('int32',	4)
    amount1         = Field('int32',	5)
    isshow          = Field('int32',	6)

# file: config/fbinfo.proto
class TalkFirstBrushItem(ProtoEntity):
    pos             = Field('int32',	1)
    talk            = Field('string',	2)
    talkTime        = Field('float',	3)

class GroupInfo(ProtoEntity):
    id              = Field('int32',	1)
    modelID         = Field('int32',	2)
    monster1        = Field('int32',	3, required=False)
    monster2        = Field('int32',	4, required=False)
    monster3        = Field('int32',	5, required=False)
    monster4        = Field('int32',	6, required=False)
    monster5        = Field('int32',	7, required=False)
    monster6        = Field('int32',	8, required=False)
    name            = Field('string',	9)
    quality         = Field('int32',	10)
    bossPos         = Field('sint32',	11, required=False)
    level           = Field('sint32',	12, required=False)

class FbReward(ProtoEntity):
    # enum Type
    Exp=1
    Money=2
    Gold=3
    Star=4
    Droppack=6
    Metal=7
    Purple=8
    Blue=9
    PARTNER=10
    LIVENESS=11
    TICKET=12
    type            = Field('enum',	1)
    amount          = Field('int32',	2)

class MonsterInfo(ProtoEntity):
    id              = Field('int32',	1)
    modelID         = Field('int32',	2)
    name            = Field('string',	3)
    level           = Field('int32',	4)
    career          = Field('int32',	5)
    skill1          = Field('int32',	6)
    skill2          = Field('int32',	7)
    scalex          = Field('float',	8, required=False)
    scaley          = Field('float',	9, required=False)
    quality         = Field('int32',	10)
    country         = Field('int32',	11)
    first           = Field('int32',	12)

class TalkFirstBrush(ProtoEntity):
    id              = Field('int32',	1)
    value           = Field(TalkFirstBrushItem,	2, repeated=True)

class DroppackItem(ProtoEntity):
    itemId          = Field('int32',	1)
    amount          = Field('int32',	2)

class Droppack(ProtoEntity):
    id              = Field('int32',	1)
    items           = Field(DroppackItem,	2, repeated=True)

class MonsterGroup(ProtoEntity):
    id              = Field('int32',	1)
    posX            = Field('int32',	2)
    posY            = Field('int32',	3)

class FbInfo(ProtoEntity):
    id              = Field('int32',	1)
    mapID           = Field('int32',	2)
    name            = Field('string',	3)
    desc            = Field('string',	4)
    maximum         = Field('int32',	5)
    icon            = Field('int32',	6)
    groups          = Field(MonsterGroup,	7, repeated=True)
    rewards         = Field(FbReward,	8, repeated=True)

# file: config/fightFb.proto
class FightFB(ProtoEntity):
    id              = Field('int32',	1)
    icon            = Field('int32',	2)
    mapID           = Field('int32',	3)
    type            = Field('int32',	4)
    name            = Field('string',	5)
    soldatmoney     = Field('int32',	6)
    dropsoldat      = Field('int32',	7)
    fbtype          = Field('int32',	8)
    Maximum         = Field('int32',	9)
    groupID1        = Field('int32',	10)
    fbReward1       = Field('int32',	11)
    amount1         = Field('int32',	12)
    fbReward2       = Field('int32',	13)
    amount2         = Field('int32',	14)
    fbReward3       = Field('int32',	15)
    amount3         = Field('int32',	16)
    fbReward4       = Field('int32',	17)
    amount4         = Field('int32',	18)
    firstReward1    = Field('int32',	19)
    firstamount1    = Field('int32',	20)
    firstReward2    = Field('int32',	21)
    firstamount2    = Field('int32',	22)
    firstReward3    = Field('int32',	23)
    firstamount3    = Field('int32',	24)
    firstReward4    = Field('int32',	25)
    firstamount4    = Field('int32',	26)
    usesp           = Field('int32',	27)

class SceneBg(ProtoEntity):
    type            = Field('string',	1)
    range           = Field('int32',	2)
    map             = Field('string',	3)
    grass           = Field('string',	4)

class SceneInfo(ProtoEntity):
    sceneID         = Field('int32',	1)
    name            = Field('string',	2)
    fbID            = Field('string',	3)
    bossfbID        = Field('int32',	4)
    mapId           = Field('int32',	5)

# file: config/fightresponseguide.proto
class fightResponseGuide(ProtoEntity):
    id              = Field('int32',	1)
    name            = Field('string',	2)
    tips            = Field('string',	3)
    weight          = Field('int32',	4)
    minlevel        = Field('int32',	5)
    maxlevel        = Field('int32',	6)
    fbID            = Field('string',	7)
    type            = Field('int32',	8)

# file: config/files.proto
# enum FileStorage
PACKAGE=1
INTERNAL=2
EXTERNAL=3
class FileItem(ProtoEntity):
    url             = Field('string',	1)
    md5             = Field('string',	2)
    size            = Field('int32',	3)
    where           = Field('enum',	4)

class FileList(ProtoEntity):
    version         = Field('int32',	1)
    version_name    = Field('string',	2)
    files           = Field(FileItem,	3, repeated=True)
    pkg_version     = Field('int32',	4, required=False)
    platform        = Field('string',	5, required=False)
    config_version  = Field('int32',	6, required=False)

# file: config/taskconfig.proto
class PreCondition(ProtoEntity):
    # enum PreConditionType
    LEVEL=1
    TASK=2
    type            = Field('enum',	1)
    iArg1           = Field('int32',	2, required=False)

class Option(ProtoEntity):
    # enum OptionStyle
    NEXT=1
    TASK=2
    DOTASK=3
    BUTTON=4
    SHOP=5
    HIRE=6
    type            = Field('enum',	2)
    value           = Field('int32',	3, required=False)
    title           = Field('string',	4)

class Session(ProtoEntity):
    content         = Field('string',	1)
    options         = Field(Option,	2, repeated=True)

class Dialog(ProtoEntity):
    dialogId        = Field('int32',	1)
    sessions        = Field(Session,	2, repeated=True)

class PostCondition(ProtoEntity):
    # enum PostConditionType
    MONSTER=1
    FB=2
    ITEM=3
    TALK=4
    type            = Field('int32',	1)
    iArg1           = Field('int32',	3, required=False)
    iArg2           = Field('int32',	4, required=False)
    iArg3           = Field('int32',	5, required=False)

class Reward(ProtoEntity):
    # enum RewardType
    EXP=1
    MONEY=2
    GOLD=3
    STAR=4
    ITEM=5
    DROPPACK=6
    METAL=7
    PURPLE=8
    BLUE=9
    PARTNER=10
    LIVENESS=11
    TICKET=12
    type            = Field('enum',	1)
    item            = Field('int32',	2, required=False)
    count           = Field('int32',	3)

class Task(ProtoEntity):
    # enum TaskStatus
    UNKNOWN=-1
    UNACCEPT=0
    ONGOING=1
    TOFINISH=2
    FAILED=3
    # enum TaskType
    INVALID=0
    MAIN=1
    BRANCH=2
    DAILY=3
    id              = Field('int32',	1)
    type            = Field('enum',	2)
    name            = Field('string',	3)
    startNPC        = Field('int32',	4, required=False)
    endNPC          = Field('int32',	5, required=False)
    rewards         = Field(Reward,	6, repeated=True)
    dialogs         = Field(Dialog,	7, repeated=True)
    preConditions   = Field(PreCondition,	8, repeated=True)
    postConditions  = Field(PostCondition,	9, repeated=True)
    quality         = Field('int32',	10, required=False)

class TaskFile(ProtoEntity):
    all_task        = Field(Task,	1, repeated=True)

# file: config/npc.proto
class NPCRes(ProtoEntity):
    # enum NPCType
    Transfer=1
    Task=2
    Shop=4
    Hire=8
    id              = Field('int32',	1)
    name            = Field('string',	2)
    type            = Field('int32',	3)
    resId           = Field('int32',	4)
    iconId          = Field('int32',	5, required=False)
    shopId          = Field('int32',	6, required=False)
    defaultDialog   = Field(Dialog,	7)
    x               = Field('int32',	8)
    y               = Field('int32',	9)
    offset_y        = Field('int32',	10)

# file: config/scene.proto
class Scene(ProtoEntity):
    # enum SceneType
    Main=0
    Fb=1
    PVP=2
    Boss=3
    id              = Field('int32',	1)
    width           = Field('int32',	2)
    height          = Field('int32',	3)
    farlayer        = Field('string',	4, required=False)
    nearlayer       = Field('string',	5, required=False)
    frontlayer      = Field('string',	6, required=False)
    all_npc_res     = Field(NPCRes,	7, repeated=True)
    fblist          = Field('int32',	8, repeated=True)
    defaultX        = Field('int32',	9)
    defaultY        = Field('int32',	10)
    type            = Field('enum',	11)
    name            = Field('string',	12)
    textures        = Field('string',	13, repeated=True)
    miny            = Field('int32',	14)
    maxy            = Field('int32',	15)
    music           = Field('string',	16, required=False)
    mirror          = Field('bool',	17, required=False)
    minx            = Field('int32',	18, required=False)
    maxx            = Field('int32',	19, required=False)
    fbname          = Field('string',	20, required=False)
    number          = Field('int32',	21, required=False)
    res_id          = Field('int32',	22)

# file: config/materialItems.proto
# enum ItemType
Equipment=1
Expendable=2
Material=3
class MatItems(ProtoEntity):
    type            = Field('enum',	1)
    id              = Field('int32',	2)
    name            = Field('string',	3)
    part            = Field('int32',	4)
    description     = Field('string',	5)
    mediaID         = Field('int32',	6)
    quality         = Field('int32',	7)
    needSex         = Field('int32',	8, required=False)
    needWork        = Field('int32',	9)
    isDelAfterUse   = Field('int32',	10)
    stackUpNum      = Field('int32',	11)
    attrID          = Field('int32',	12, required=False)
    buyPrice        = Field('int32',	13, required=False)
    sellPrice       = Field('int32',	14, required=False)
    levelLimitMin   = Field('int32',	15, required=False)
    triggerSkills   = Field('int32',	16, required=False)
    rankUpFormula   = Field('int32',	17, required=False)
    clothesID       = Field('int32',	18, required=False)
    weight          = Field('int32',	19, required=False)
    itemLink        = Field('string',	20, required=False)

class UpdateMatResponse(ProtoEntity):
    materials       = Field(MatItems,	1, repeated=True)

class EquipSellQualityFactor(ProtoEntity):
    id              = Field('int32',	1)
    factor          = Field('int32',	2)

class EquipSellPartFactorInfo(ProtoEntity):
    id              = Field('int32',	1)
    factor          = Field('int32',	2)

class EquipAttrs(ProtoEntity):
    id              = Field('int32',	1)
    costSilver      = Field('int32',	2)
    costGold        = Field('int32',	3)
    costItem        = Field('int32',	4)
    itemAmount      = Field('int32',	5)
    sellPrice       = Field('int32',	7)
    phyAtk          = Field('int32',	8)
    magAtk          = Field('int32',	9)
    stuntAtk        = Field('int32',	10)
    phyDef          = Field('int32',	11)
    magDef          = Field('int32',	12)
    stuntDef        = Field('int32',	13)
    HP              = Field('int32',	14)

class clothes(ProtoEntity):
    ID              = Field('int32',	1)
    petList         = Field('string',	2)
    proType         = Field('int32',	3)
    proValue        = Field('int32',	4)
    proPercentType  = Field('int32',	5)
    proPercentValue = Field('int32',	6)
    desc            = Field('string',	7)

# file: config/skillinfo.proto
# enum SkillType
HURT=0
CURE=1
PROT=3
VMPI=13
class EffectInfo(ProtoEntity):
    resourceId      = Field('int32',	1)
    offsetX         = Field('float',	2)
    offsetY         = Field('float',	3)
    scaleX          = Field('float',	4)
    scaleY          = Field('float',	5)
    loop            = Field('int32',	6)

class NormalAttack(ProtoEntity):
    id              = Field('int32',	1)
    effect_attack   = Field(EffectInfo,	2)
    effect_attacked = Field(EffectInfo,	3)

class SkillInfo(ProtoEntity):
    id              = Field('int32',	1)
    iconID          = Field('int32',	2, required=False)
    name            = Field('string',	3)
    type            = Field('enum',	4)
    effect_attack   = Field(EffectInfo,	5, repeated=True)
    effect_attacked = Field(EffectInfo,	6, repeated=True)
    rangeDesc       = Field('string',	7, required=False)
    effectDesc      = Field('string',	8, required=False)
    action          = Field('string',	9, required=False)
    attackStyle     = Field('int32',	10, required=False)
    attackTime      = Field('float',	11, required=False)
    attackAction    = Field('int32',	12, required=False)
    attackEffect    = Field('string',	13, required=False)
    hurtAction      = Field('int32',	14, required=False)
    hurtEffect      = Field('string',	15, required=False)
    hurtCount       = Field('int32',	16, required=False)
    hurtInterval    = Field('float',	17, required=False)
    flyEffect       = Field('string',	18, required=False)
    flyTime         = Field('float',	19, required=False)
    attackAutoFlip  = Field('int32',	20, required=False)
    hurtAutoFlip    = Field('int32',	21, required=False)
    endTime         = Field('float',	22, required=False)
    attackSound     = Field('string',	23, required=False)
    hurtSound       = Field('string',	24, required=False)
    flySound        = Field('string',	25, required=False)

class BuffInfo(ProtoEntity):
    id              = Field('int32',	1)
    name            = Field('string',	2)
    inEffect        = Field('string',	3, required=False)
    outEffect       = Field('string',	4, required=False)
    runEffect       = Field('string',	5, required=False)
    inText          = Field('string',	6, required=False)
    inSound         = Field('string',	7, required=False)
    outSound        = Field('string',	8, required=False)
    pro             = Field('string',	9, required=False)
    provalue        = Field('float',	10, required=False)
    inAutoFlip      = Field('sint32',	11, required=False)
    outAutoFlip     = Field('sint32',	12, required=False)
    runAutoFlip     = Field('sint32',	13, required=False)
    addTime         = Field('sint32',	14, required=False)

class TechnologyLevel(ProtoEntity):
    value           = Field('int32',	1)
    stone           = Field('int32',	2)
    time            = Field('int32',	3)
    level           = Field('int32',	4)

class Technology(ProtoEntity):
    id              = Field('int32',	1)
    name            = Field('string',	2)
    type            = Field('int32',	3)
    icon            = Field('int32',	4)
    scope           = Field('int32',	5)
    levels          = Field(TechnologyLevel,	6, repeated=True)

# file: config/shop.proto
# enum GoodsType
Reel=1
Stage=2
Fashion=3
Hide=4
Guide=5
# enum GoodsState
NotSell=0
NormalSell=1
Discount=2
HotSell=3
TimeLimit=4
NewSell=5
class GoodsItem(ProtoEntity):
    id              = Field('int32',	1)
    resourceId      = Field('int32',	2, required=False)
    count           = Field('int32',	3, required=False)
    price           = Field('int32',	4, required=False)
    discountPrice   = Field('int32',	5, required=False)
    type            = Field('enum',	6, required=False)
    state           = Field('enum',	7, required=False)
    buyLimits       = Field('int32',	8, required=False)
    buyCounts       = Field('int32',	9, required=False)
    vip             = Field('int32',	10, required=False)
    sellStar        = Field('string',	11, required=False)
    sellEnd         = Field('string',	12, required=False)
    sellLimit       = Field('int32',	13, required=False)
    priceType       = Field('int32',	14, required=False)

# file: config/guideconfig.proto
# enum triggerType
enterWorld=1
openWindow=2
levelUp=3
receiveTask=4
endTask=5
enterScene=6
enterFB=7
endFB=8
newMenuItem=9
exitGuide=10
enterHomeland=11
lessLevel=12
partner=13
levelDaBenYing=14
levelYunTieKuang=15
levelYaoQianShu=16
obtainEquip=17
obtainPartner=18
# enum contentType
cutsscenes=1
focus=2
menuItem=3
mainCity=4
fight=5
wearEqu=6
building=7
closeWindow=8
saveGuide=9
sprite=10
text=11
mingjiang=12
winEqu=13
winPartner=14
specialOption=15
class triggerCondition(ProtoEntity):
    t_type          = Field('enum',	1)
    arg             = Field('string',	2, required=False)

class guideContent(ProtoEntity):
    c_type          = Field('enum',	1)
    arg             = Field('string',	2, required=False)

class guideconfig(ProtoEntity):
    id              = Field('int32',	1)
    groupid         = Field('int32',	2)
    save            = Field('bool',	3)
    tc              = Field(triggerCondition,	4)
    gc              = Field(guideContent,	5, repeated=True)

# file: config/reward.proto
class RewardInfo(ProtoEntity):
    id              = Field('int32',	1)
    requireValue    = Field('int32',	2)
    rewardModelID   = Field('int32',	3, required=False)
    rewardType      = Field('int32',	4)
    rewardID        = Field('int32',	5, required=False)
    rewardValue     = Field('int32',	6, required=False)
    name            = Field('string',	7, required=False)

class Rewards(ProtoEntity):
    type            = Field('int32',	1)
    rewardInfos     = Field(RewardInfo,	2, repeated=True)

# file: config/petinfo.proto
class PetLockInfo(ProtoEntity):
    id              = Field('int32',	1)
    isLocked        = Field('bool',	2)

class heroPosEnhanceInfo(ProtoEntity):
    pos             = Field('int32',	1)
    effType         = Field('int32',	2)
    effValue        = Field('int32',	3)

class PetInfo(ProtoEntity):
    id              = Field('int32',	1)
    evolve          = Field('int32',	2)
    country         = Field('int32',	3)
    name            = Field('string',	4)
    career          = Field('int32',	5)
    modelID         = Field('int32',	6)
    quality         = Field('int32',	7)
    cost            = Field('int32',	8)
    proway          = Field('int32',	9)
    skillID1        = Field('int32',	10)
    skillID2        = Field('int32',	11)
    skillID3        = Field('int32',	12)
    skillID4        = Field('int32',	13)
    condition       = Field('int32',	14)
    lifeMin         = Field('int32',	15)
    lifeMax         = Field('int32',	16)
    patkMin         = Field('int32',	17)
    patkMax         = Field('int32',	18)
    matkMin         = Field('int32',	19)
    matkMax         = Field('int32',	20)
    pdefMin         = Field('int32',	21)
    pdefMax         = Field('int32',	22)
    mdefMin         = Field('int32',	23)
    mdefMax         = Field('int32',	24)
    speedMin        = Field('int32',	25)
    speedMax        = Field('int32',	26)
    jungle          = Field('int32',	27)
    intro           = Field('string',	28)
    equip           = Field('string',	29)
    group           = Field('int32',	30)
    twoid           = Field('int32',	31)
    advanceStuff    = Field('string',	32)
    advanceMoney    = Field('int32',	33)
    sort            = Field('int32',	34)
    maxLevel        = Field('int32',	35)
    position        = Field('int32',	36)
    worthExp        = Field('int32',	37)
    step            = Field('int32',	38)
    prototypeID     = Field('int32',	39)
    maxExp          = Field('int32',	40)
    prev            = Field('int32',	41)
    maxAdvance      = Field('int32',	42)
    SumInherit      = Field('int32',	43)
    rarity          = Field('int32',	44)

class PetLockList(ProtoEntity):
    petLockInfo     = Field(PetLockInfo,	1, repeated=True)

class HeroFatalInfo(ProtoEntity):
    ID              = Field('int32',	1)
    name            = Field('string',	2)
    groups          = Field('string',	3)
    effect2         = Field('string',	4)
    effect3         = Field('string',	5)
    effect4         = Field('string',	6)
    effect5         = Field('string',	7)

class PatchInfo(ProtoEntity):
    quality         = Field('int32',	1)
    cost            = Field('int32',	2)

class heroRiseExpInfo(ProtoEntity):
    id              = Field('int32',	1)
    exp             = Field('int32',	2)
    patchExp        = Field('int32',	3)

class heroTwoIdInfo(ProtoEntity):
    id              = Field('int32',	1)
    heroname        = Field('string',	2)

# file: config/runeinfo.proto
class RuneInfo(ProtoEntity):
    id              = Field('int32',	1)
    backID          = Field('int32',	2)
    name            = Field('string',	3)
    condition       = Field('int32',	4)
    level           = Field('int32',	5)
    exp             = Field('int32',	6)
    protype         = Field('string',	7)
    provalue        = Field('int32',	8)
    resource        = Field('int32',	9)
    desc            = Field('string',	10)

# file: config/physicalPower.proto
class physicalPower(ProtoEntity):
    id              = Field('int32',	1)
    starttime       = Field('int32',	2)
    endtime         = Field('int32',	3)

# file: config/signin.proto
class signin(ProtoEntity):
    day             = Field('int32',	1)
    money           = Field('int32',	2)
    gold            = Field('int32',	3)
    reward          = Field('int32',	4)
    count           = Field('int32',	5)

# file: config/luckydrawinfo.proto
class herolistmoneyinfo(ProtoEntity):
    ID              = Field('int32',	1)
    price           = Field('int32',	2)

class luckydrawinfo(ProtoEntity):
    id              = Field('int32',	1)
    name            = Field('string',	2)
    desc            = Field('string',	3)
    herolist        = Field('int32',	4)
    firstdesc       = Field('string',	5)
    gold            = Field('int32',	6)
    money           = Field('int32',	7)
    output          = Field('int32',	8)
    maxoutput       = Field('int32',	9)
    level           = Field('int32',	10)
    luckydesc       = Field('string',	11)
    freeMaxCount    = Field('int32',	12)
    goldMaxCount    = Field('int32',	13)
    showIcon        = Field('int32',	14)
    desc2           = Field('string',	15)
    point           = Field('int32',	16)

# file: config/secretcom.proto
class secretcominfo(ProtoEntity):
    ID              = Field('int32',	1)
    idx             = Field('int32',	2)
    heroid          = Field('int32',	3)
    type            = Field('int32',	4)
    path1           = Field('int32',	5)
    count1          = Field('int32',	6)
    path2           = Field('int32',	7)
    count2          = Field('int32',	8)
    path3           = Field('int32',	9)
    count3          = Field('int32',	10)
    cost            = Field('int32',	11)
    maplevel        = Field('int32',	12)

# file: config/hotspringmissioninfo.proto
class HotSpringMissionInfo(ProtoEntity):
    id              = Field('int32',	1)
    group           = Field('int32',	2)
    heroID          = Field('int32',	3)
    chance          = Field('int32',	4)
    dropID          = Field('int32',	5)
    taskContent     = Field('string',	6)

# file: config/hotspringequiptinfo.proto
class HotSpringeQuiptInfo(ProtoEntity):
    id              = Field('int32',	1)
    dtime           = Field('int32',	2)
    magnification   = Field('int32',	3)
    raidcount       = Field('int32',	4)
    raidloss        = Field('int32',	5)
    freechance      = Field('int32',	6)
    paychance       = Field('int32',	7)
    moudelid        = Field('int32',	8)
    moudelname      = Field('string',	9)

# file: config/savestepup.proto
class savestepupdata(ProtoEntity):
    heroID          = Field('string',	1)
    stepup          = Field('int32',	2)
    tab1            = Field('int32',	3)
    tab2            = Field('int32',	4)
    tab3            = Field('int32',	5)
    tab4            = Field('int32',	6)
    tab5            = Field('int32',	7)
    tab6            = Field('int32',	8)
    tab7            = Field('int32',	9)
    tab8            = Field('int32',	10)
    tab9            = Field('int32',	11)
    tab10           = Field('int32',	12)
    tab11           = Field('int32',	13)

# file: config/guiddata.proto
class winstepdata(ProtoEntity):
    id              = Field('int32',	1)
    isshow          = Field('int32',	2)
    txt             = Field('string',	3)
    next            = Field('int32',	4)
    issave          = Field('int32',	5)
    guiId           = Field('int32',	6)
    guicom          = Field('int32',	7)
    aligment        = Field('int32',	8)
    trigger         = Field('string',	9)
    saveId          = Field('int32',	10)
    islink          = Field('int32',	11)
    plan            = Field('int32',	12)
    isnobalck       = Field('int32',	13)

# file: config/publicdefine.proto
class publicdefine(ProtoEntity):
    ID              = Field('int32',	1)
    value           = Field('string',	2)

# file: config/levelopengui.proto
class levelopenguidata(ProtoEntity):
    id              = Field('int32',	1)
    guiId           = Field('int32',	2)
    saveId          = Field('int32',	3)
    level           = Field('int32',	4)
    txt             = Field('string',	5)
    plan            = Field('int32',	6)

# file: config/heroblessinfo.proto
class heroblessinfo(ProtoEntity):
    vipLevel        = Field('int32',	1)
    maxCount        = Field('int32',	2)

# file: config/vip.proto
class VIPChallengeBossConsume(ProtoEntity):
    id              = Field('int32',	1)
    gold            = Field('int32',	2)

# file: config/gameconfig.proto
class GiftRewardInfo(ProtoEntity):
    id              = Field('int32',	1)
    amount1         = Field('int32',	2)

class Career(ProtoEntity):
    id              = Field('int32',	1)
    name            = Field('string',	2)
    skill1          = Field('string',	3)
    skill2          = Field('string',	4)
    skill3          = Field('string',	5)

class FBTalk(ProtoEntity):
    id              = Field('int32',	1)
    content         = Field('string',	2)
    nextStep        = Field('int32',	3)
    monsterId       = Field('int32',	4)

class EquipForge(ProtoEntity):
    id              = Field('int32',	1)
    consume_count   = Field('int32',	2)
    consume_money   = Field('int32',	3)

class EquipPatch(ProtoEntity):
    id              = Field('int32',	1)
    level           = Field('int32',	2)
    count           = Field('int32',	3)
    money           = Field('int32',	4)
    randID          = Field('int32',	5)
    icon            = Field('int32',	6)

class RefineEquip(ProtoEntity):
    quality         = Field('int32',	1)
    part            = Field('int32',	2)
    refineLevel     = Field('int32',	3)
    refineVal       = Field('int32',	4)
    condLevel       = Field('int32',	5)
    attrVal         = Field('int32',	6)

class AdventrueOne(ProtoEntity):
    id              = Field('int32',	1)
    name            = Field('string',	2)
    enterlevelcondition = Field('int32',	3)

class HomeExchange(ProtoEntity):
    id              = Field('int32',	1)
    metalcost       = Field('int32',	2)
    treecost        = Field('int32',	3)

class RefineItem(ProtoEntity):
    itemId          = Field('int32',	1)
    part            = Field('int32',	2)
    refineVal       = Field('int32',	3)

class RankLevelInfo(ProtoEntity):
    id              = Field('int32',	1)
    name            = Field('string',	2)
    quality         = Field('int32',	3)

class GameConfig(ProtoEntity):
    all_scenes      = Field(Scene,	1, repeated=True)
    all_task        = Field(Task,	2, repeated=True)
    all_decorateCost = Field(DecorateCost,	3, repeated=True)
    all_material    = Field(MatItems,	4, repeated=True)
    all_fbs         = Field(FbInfo,	6, repeated=True)
    all_groups      = Field(GroupInfo,	7, repeated=True)
    all_monsters    = Field(MonsterInfo,	8, repeated=True)
    all_careers     = Field(Career,	9, repeated=True)
    all_droppacks   = Field(Droppack,	10, repeated=True)
    all_skills      = Field(SkillInfo,	12, repeated=True)
    all_levelExp    = Field('int32',	13, repeated=True)
    all_shopGoods   = Field(GoodsItem,	14, repeated=True)
    all_buildings   = Field(buildingInfo,	15, repeated=True)
    all_technologys = Field(Technology,	16, repeated=True)
    all_guides      = Field(guideconfig,	17, repeated=True)
    all_rankLevelInfos = Field(RankLevelInfo,	18, repeated=True)
    all_rewards     = Field(Rewards,	19, repeated=True)
    all_exchanges   = Field(HomeExchange,	20, repeated=True)
    all_normalAttack = Field(NormalAttack,	21, repeated=True)
    all_clothes     = Field(clothes,	22, repeated=True)
    all_pets        = Field(PetInfo,	23, repeated=True)
    all_runeinfo    = Field(RuneInfo,	24, repeated=True)
    all_physicalPower = Field(physicalPower,	25, repeated=True)
    all_signin      = Field(signin,	26, repeated=True)
    all_patchs      = Field(PatchInfo,	27, repeated=True)
    all_levelExppet = Field('int32',	28, repeated=True)
    all_challbook   = Field(challbook,	29, repeated=True)
    all_luckydrawinfo = Field(luckydrawinfo,	30, repeated=True)
    all_secretcominfo = Field(secretcominfo,	31, repeated=True)
    all_hotspringmissioninfo = Field(HotSpringMissionInfo,	32, repeated=True)
    all_hotspringequiptinfo = Field(HotSpringeQuiptInfo,	33, repeated=True)
    all_fatals      = Field(HeroFatalInfo,	34, repeated=True)
    all_herolistmoneyinfo = Field(herolistmoneyinfo,	35, repeated=True)
    all_fightFb     = Field(FightFB,	36, repeated=True)
    all_droppack    = Field(newDroppack,	37, repeated=True)
    all_giftRewardInfo = Field(GiftRewardInfo,	38, repeated=True)
    all_winstepdata = Field(winstepdata,	39, repeated=True)
    all_twoidPets   = Field(heroTwoIdInfo,	40, repeated=True)
    all_publicdefine = Field(publicdefine,	41, repeated=True)
    all_fbtalk      = Field(FBTalk,	42, repeated=True)
    all_buffs       = Field(BuffInfo,	43, repeated=True)
    all_levelopenguidata = Field(levelopenguidata,	44, repeated=True)
    all_sellPartFactorInfo = Field(EquipSellPartFactorInfo,	45, repeated=True)
    all_sellQualityFactor = Field(EquipSellQualityFactor,	46, repeated=True)
    all_talkFirstBrush = Field(TalkFirstBrush,	47, repeated=True)
    all_challengeboxs = Field(ChallegeBoxConfig,	48, repeated=True)
    all_heroblessinfo = Field(heroblessinfo,	50, repeated=True)
    all_equippatch  = Field(EquipPatch,	49, repeated=True)
    all_awardsysinfo = Field(awardsysinfo,	51, repeated=True)
    all_equForge    = Field(EquipForge,	52, repeated=True)
    all_heroriseexp = Field(heroRiseExpInfo,	53, repeated=True)
    all_vipChallengeBoss = Field(VIPChallengeBossConsume,	54, repeated=True)
    all_fightresponseguide = Field(fightResponseGuide,	55, repeated=True)
    all_challengerAwardInfo = Field(challengerAwardInfo,	56, repeated=True)
    all_adventrueone = Field(AdventrueOne,	57, repeated=True)
    all_challengeTitle = Field(ChallengeTitleConfig,	58, repeated=True)
    all_sceneBg     = Field(SceneBg,	59, repeated=True)
    all_heroposbuff = Field(heroPosEnhanceInfo,	60, repeated=True)
    all_refineequip = Field(RefineEquip,	61, repeated=True)
    all_refineitem  = Field(RefineItem,	62, repeated=True)

# file: config/homebase.proto
class homebaseLevelData(ProtoEntity):
    level           = Field('int32',	1)
    revenue         = Field('int32',	2)
    levelupCost     = Field('int32',	3)

# file: config/mailAdditionData.proto
class MailAdditionData(ProtoEntity):
    value1          = Field('string',	1, required=False)
    value2          = Field('int32',	2, required=False)

# file: config/mailData.proto
class MailData(ProtoEntity):
    mailID          = Field('int32',	1)
    mailType        = Field('int32',	2)
    mailState       = Field('int32',	3)
    mailWord        = Field('string',	4)
    additionType    = Field('int32',	5, required=False)
    additionData    = Field(MailAdditionData,	6, repeated=True)

# file: config/textPack.proto
class textInfo(ProtoEntity):
    originText      = Field('string',	1)
    transformText   = Field('string',	2)

class allTexts(ProtoEntity):
    all_text        = Field(textInfo,	1, repeated=True)

