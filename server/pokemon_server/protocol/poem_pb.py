# coding: utf-8
from cprotobuf import ProtoEntity, Field
# file: anim.proto
class Point(ProtoEntity):
    x               = Field('float',	1)
    y               = Field('float',	2)

class Color(ProtoEntity):
    r               = Field('int32',	1)
    g               = Field('int32',	2)
    b               = Field('int32',	3)

class AnimIndexItem(ProtoEntity):
    name            = Field('string',	1)
    symbols         = Field('string',	2, repeated=True)

class AnimIndex(ProtoEntity):
    anims           = Field(AnimIndexItem,	1, repeated=True)

class AnimationKeyframe(ProtoEntity):
    startFrame      = Field('int32',	1)
    isMotion        = Field('bool',	2, required=False, default=False)
    position        = Field(Point,	3)
    duration        = Field('int32',	4, required=False, default=1)
    script          = Field('string',	5, required=False)

class Animation(ProtoEntity):
    keyframes       = Field(AnimationKeyframe,	1, repeated=True)

class Frame(ProtoEntity):
    name            = Field('string',	1)
    x               = Field('int32',	2)
    y               = Field('int32',	3)
    w               = Field('int32',	4)
    h               = Field('int32',	5)
    rotated         = Field('bool',	6)
    filename        = Field('int32',	7)

class FrameList(ProtoEntity):
    frames          = Field(Frame,	1, repeated=True)
    filenames       = Field('string',	2, repeated=True)

class Rect(ProtoEntity):
    x               = Field('float',	1)
    y               = Field('float',	2)
    w               = Field('float',	3)
    h               = Field('float',	4)

class Element(ProtoEntity):
    # enum ElementType
    ND_MOVIECLIP=1
    ND_BITMAP=2
    ND_TTFTEXT=4
    ND_FRAME=7
    ND_RECT=8
    ND_BMTEXT=9
    ND_PARTICLE=11
    type            = Field('enum',	1)
    position        = Field(Point,	2)
    boundingBox     = Field(Rect,	3)
    libName         = Field('string',	4, required=False)
    instanceName    = Field('string',	5, required=False)
    rotation        = Field('float',	6, required=False)
    anchorPoint     = Field(Point,	7, required=False)
    scaleValue      = Field(Point,	8, required=False)
    alpha           = Field('int32',	9, required=False, default=255)
    color           = Field(Color,	10, required=False)
    text            = Field('string',	11, required=False)
    fontSize        = Field('int32',	12, required=False, default=12)
    fnt             = Field('string',	13, required=False)
    alignment       = Field('int32',	14, required=False)
    skew            = Field(Point,	15, required=False)

class Keyframe(ProtoEntity):
    startFrame      = Field('int32',	1)
    isMotion        = Field('bool',	5, required=False, default=False)
    elements        = Field(Element,	3, repeated=True)
    duration        = Field('int32',	4, required=False, default=1)
    script          = Field('string',	6, required=False)

class Layer(ProtoEntity):
    keyframes       = Field(Keyframe,	1, repeated=True)
    name            = Field('string',	2, required=False)

class Symbol(ProtoEntity):
    name            = Field('string',	1)
    boundingBox     = Field(Rect,	2)
    frameCount      = Field('int32',	3)
    layers          = Field(Layer,	5, repeated=True)
    anis            = Field(Animation,	9, repeated=True)
    frameRate       = Field('int32',	10, required=False)
    pauseTime       = Field('float',	11, required=False)

class Anim(ProtoEntity):
    symbols         = Field(Symbol,	1, repeated=True)

# file: attributes.proto
class Property(ProtoEntity):
    step            = Field('int32',	1, required=False, default=1)
    rest_star       = Field('int32',	2, required=False)
    enchant_attrs   = Field('string',	3, required=False)
    entityID        = Field('int32',	4, required=False)
    name            = Field('string',	5, required=False)
    level           = Field('int32',	6, required=False)
    sp              = Field('int32',	7, required=False)
    money           = Field('int32',	8, required=False)
    gold            = Field('int32',	9, required=False)
    vs              = Field('int32',	10, required=False)
    gp              = Field('int32',	11, required=False)
    bp              = Field('int32',	12, required=False)
    slate           = Field('int32',	13, required=False)
    power           = Field('int32',	14, required=False)
    sex             = Field('int32',	16, required=False)
    career          = Field('int32',	17, required=False)
    breaklevel      = Field('int32',	21, required=False)
    soul            = Field('int32',	23, required=False)
    skill           = Field('int32',	24, required=False, default=1)
    lskill          = Field('int32',	25, required=False, default=1)
    newmailcount    = Field('int32',	34, required=False)
    spmax           = Field('int32',	35, required=False)
    petmax          = Field('int32',	36, required=False)
    exp             = Field('int32',	48, required=False)
    expmax          = Field('int32',	49, required=False)
    expnxt          = Field('int32',	50, required=False)
    resume_sp_cd    = Field('int32',	51, required=False)
    spprop          = Field('int32',	52, required=False)
    gettime         = Field('int32',	55, required=False)
    dispatched      = Field('int32',	56, required=False)
    mtype           = Field('int32',	63, required=False)
    relations       = Field('string',	65, required=False)
    explore1        = Field('int32',	71, required=False)
    exploretime1    = Field('int32',	73, required=False)
    explore2        = Field('int32',	81, required=False)
    exploretime2    = Field('int32',	83, required=False)
    explore3        = Field('int32',	85, required=False)
    exploretime3    = Field('int32',	87, required=False)
    uproar_dead     = Field('bool',	97, required=False)
    restHP          = Field('int32',	98, required=False)
    star            = Field('int32',	261, required=False)
    loterry_hero_cd_A = Field('int32',	264, required=False)
    loterry_hero_cd_B = Field('int32',	265, required=False)
    loterry_hero_cd_C = Field('int32',	266, required=False)
    loterry_hero_cost_A = Field('int32',	286, required=False)
    loterry_hero_cost_B = Field('int32',	287, required=False)
    loterry_hero_cost_C = Field('int32',	288, required=False)
    loterry_hero_cd_D = Field('int32',	289, required=False)
    loterry_hero_rest_free_count_A = Field('int32',	294, required=False)
    loterry_hero_rest_free_count_B = Field('int32',	295, required=False)
    loterry_hero_rest_free_count_C = Field('int32',	296, required=False)
    loterry_hero_rest_free_count_D = Field('int32',	297, required=False)
    loterry_hero_tips_A = Field('string',	298, required=False)
    loterry_hero_tips_B = Field('string',	299, required=False)
    loterry_hero_tips_C = Field('string',	300, required=False)
    loterry_hero_tips_D = Field('string',	301, required=False)
    loterry_hero_cost_D = Field('int32',	304, required=False)
    resolvegold_level = Field('int32',	307, required=False)
    pvpgrad         = Field('int32',	312, required=False)
    pvprankcount    = Field('int32',	313, required=False)
    pvpseasonrewardreceived = Field('bool',	320, required=False)
    todaybp         = Field('int32',	336, required=False)
    pvprank         = Field('int32',	337, required=False)
    pvpstarttime    = Field('int32',	338, required=False)
    pvpfinaltime    = Field('int32',	339, required=False)
    pvpopen         = Field('bool',	340, required=False)
    totalbp         = Field('int32',	341, required=False)
    prototypeID     = Field('int32',	342, required=False)
    exploredoubletime1 = Field('int32',	343, required=False)
    exploredoubletime2 = Field('int32',	344, required=False)
    exploredoubletime3 = Field('int32',	345, required=False)
    slatelen        = Field('int32',	357, required=False)
    skill1          = Field('int32',	512, required=False, default=1)
    skill2          = Field('int32',	513, required=False, default=1)
    skill3          = Field('int32',	514, required=False, default=1)
    skill4          = Field('int32',	515, required=False, default=1)
    skill5          = Field('int32',	516, required=False, default=1)
    faction_name    = Field('string',	544, required=False)
    faction_level   = Field('int32',	545, required=False)
    faction_is_leader = Field('bool',	546, required=False)
    faction_level_rewards_count = Field('int32',	549, required=False)
    faction_taskID  = Field('int32',	550, required=False)
    faction_task_done = Field('bool',	552, required=False)
    last_factionID  = Field('int32',	554, required=False)
    factionID       = Field('int32',	592, required=False)
    inviteFactionCount = Field('int32',	596, required=False)
    applyMemberCount = Field('int32',	598, required=False)
    strengthen_df_level = Field('int32',	617, required=False)
    strengthen_hp_level = Field('int32',	624, required=False)
    strengthen_at_level = Field('int32',	625, required=False)
    strengthen_ct_level = Field('int32',	626, required=False)
    buy_sp_rest_count = Field('int32',	641, required=False)
    buy_sp_cost     = Field('int32',	642, required=False)
    equipeds_json   = Field('string',	769, required=False)
    max_level       = Field('int32',	770, required=False)
    next_max_level  = Field('int32',	771, required=False)
    credits         = Field('int32',	1024, required=False)
    vip             = Field('int32',	1025, required=False)
    vip_refresh_fb_max_count = Field('int32',	1107, required=False)
    task_rest_patch_sign_up_count = Field('int32',	1283, required=False)
    task_today_is_sign_up = Field('bool',	1286, required=False)
    taskrewardscount1 = Field('int32',	1287, required=False)
    taskrewardscount2 = Field('int32',	1288, required=False)
    taskrewardscount3 = Field('int32',	1289, required=False)
    taskrewardscount4 = Field('int32',	1290, required=False)
    taskrewardscountnew = Field('int32',	1296, required=False)
    taskrewardscount5 = Field('int32',	1297, required=False)
    task_noob_flag  = Field('bool',	1298, required=False)
    task_noob_undo  = Field('bool',	1299, required=False)
    taskrewardscount6 = Field('int32',	1300, required=False)
    taskrewardscount7 = Field('int32',	1301, required=False)
    taskrewardscountsubtype1 = Field('int32',	1302, required=False)
    taskrewardscountsubtype2 = Field('int32',	1303, required=False)
    taskrewardscountsubtype3 = Field('int32',	1304, required=False)
    taskrewardscountsubtype4 = Field('int32',	1305, required=False)
    taskrewardscount12 = Field('int32',	1312, required=False)
    taskrewardscount13 = Field('int32',	1313, required=False)
    taskrewardscount14 = Field('int32',	1314, required=False)
    taskrewardsdone14 = Field('int32',	1315, required=False)
    limited_packs_flag = Field('bool',	1538, required=False)
    limited_packs_rest_count = Field('int32',	1540, required=False)
    timelimited_packs_rest_time = Field('int32',	1544, required=False)
    timelimited_packs_rest_count = Field('int32',	1545, required=False)
    first_recharge_flag = Field('bool',	1570, required=False, default=True)
    first_recharge_recv = Field('bool',	1571, required=False)
    cleanfb         = Field('int32',	1584, required=False)
    clean_campaign_vip = Field('int32',	1585, required=False)
    on_lineup_defend = Field('int32',	1793, required=False)
    borderID        = Field('int32',	1794, required=False)
    rank_count      = Field('int32',	1796, required=False)
    rank_active_count = Field('int32',	1797, required=False)
    rank_active_win_count = Field('int32',	1798, required=False)
    rank_win_count  = Field('int32',	1799, required=False)
    rank_free_vs    = Field('int32',	1800, required=False, default=10)
    rank_cd         = Field('int32',	1801, required=False)
    rank_passive_offline_count = Field('int32',	1811, required=False)
    totalbp_on_logout = Field('int32',	1812, required=False)
    rank_rest_count = Field('int32',	1815, required=False, default=10)
    rank_resume_rest_count_cd = Field('int32',	1816, required=False)
    rank_reset_rest_count = Field('int32',	1825, required=False)
    rank_reset_cost = Field('int32',	1826, required=False)
    rank_refresh_cd = Field('int32',	1827, required=False)
    rank_refresh_cost = Field('int32',	1829, required=False)
    rank_serial_win_count = Field('int32',	1830, required=False)
    rank_serial_win_count_cd = Field('int32',	1831, required=False)
    fp              = Field('int32',	2304, required=False)
    totalfp         = Field('int32',	2305, required=False)
    todayfp_donate  = Field('int32',	2306, required=False)
    dismissCD       = Field('int32',	2308, required=False)
    todayfp_sp      = Field('int32',	2309, required=False)
    todayfp_sp_max  = Field('int32',	2312, required=False)
    todayfp_donate_max = Field('int32',	2313, required=False)
    todayfp_task    = Field('int32',	2320, required=False)
    todayfp         = Field('int32',	2322, required=False)
    mine_rob_history_flag = Field('bool',	2448, required=False)
    mine_rob_count  = Field('int32',	2454, required=False)
    resume_mine_rob_count_cd = Field('int32',	2455, required=False)
    mine_rob_max_count = Field('int32',	2456, required=False)
    mine_protect_time = Field('int32',	2457, required=False)
    inlay1          = Field('int32',	3088, required=False)
    inlay2          = Field('int32',	3089, required=False)
    inlay3          = Field('int32',	3090, required=False)
    inlay4          = Field('int32',	3091, required=False)
    inlay5          = Field('int32',	3092, required=False)
    inlay6          = Field('int32',	3093, required=False)
    mine_products1  = Field('int32',	4096, required=False)
    mine_productivity1 = Field('int32',	4097, required=False)
    mine_safety1    = Field('int32',	4098, required=False)
    mine_time_past1 = Field('int32',	4100, required=False)
    mine_maximum1   = Field('int32',	4101, required=False)
    mine_free_collect_count1 = Field('int32',	4102, required=False, default=1)
    mine_level1     = Field('int32',	4104, required=False)
    mine_products2  = Field('int32',	4112, required=False)
    mine_productivity2 = Field('int32',	4113, required=False)
    mine_safety2    = Field('int32',	4114, required=False)
    mine_time_past2 = Field('int32',	4116, required=False)
    mine_maximum2   = Field('int32',	4117, required=False)
    mine_free_collect_count2 = Field('int32',	4118, required=False, default=1)
    mine_level2     = Field('int32',	4120, required=False)
    uproar_refresh_rest_count = Field('int32',	4358, required=False)
    jiutian         = Field('int32',	4360, required=False)
    last_target     = Field('int32',	4361, required=False)
    last_chest      = Field('int32',	4368, required=False)
    uproar_enemy_buff = Field('int32',	4372, required=False)
    loot_rest_count = Field('int32',	4866, required=False)
    loot_reset_count = Field('int32',	4883, required=False)
    reward_campaign_opened = Field('bool',	4896, required=False)
    dream           = Field('int32',	4936, required=False)
    pious           = Field('int32',	4937, required=False)
    visit_free_rest_count = Field('int32',	4949, required=False)
    visit_cost      = Field('int32',	4953, required=False)
    beg_flag        = Field('bool',	4960, required=False)
    level_packs_flag = Field('bool',	4994, required=False)
    level_packs_done_count = Field('int32',	4995, required=False)
    power_packs_flag = Field('bool',	5010, required=False)
    power_packs_done_count = Field('int32',	5011, required=False)
    totallogin_flag = Field('bool',	5121, required=False)
    max_power       = Field('int32',	5635, required=False)
    new_role        = Field('bool',	6149, required=False)
    autofight       = Field('bool',	6160, required=False)
    speedUpfight    = Field('bool',	6161, required=False)
    dongtian_cd     = Field('int32',	6400, required=False)
    fudi_cd         = Field('int32',	6401, required=False)
    treasure_type   = Field('int32',	8192, required=False, default=1)
    treasure_count  = Field('int32',	8195, required=False)
    treasure_cd     = Field('int32',	8196, required=False)
    treasure_max_count = Field('int32',	8197, required=False)
    treasure_chest_gold = Field('int32',	8200, required=False)
    friend_messages_count = Field('int32',	8344, required=False)
    friend_count    = Field('int32',	8449, required=False)
    friend_max_count = Field('int32',	8450, required=False)
    friend_applys_count = Field('int32',	8452, required=False)
    friend_gift_used_count = Field('int32',	8453, required=False)
    friend_gift_max_count = Field('int32',	8455, required=False)
    friendfb_remain_count = Field('int32',	8466, required=False)
    friendfb_buff   = Field('int32',	8471, required=False)
    tap_rest_count  = Field('int32',	8708, required=False, default=120)
    tap_rest_count_resume_cd = Field('int32',	8709, required=False)
    tap_max_count   = Field('int32',	8710, required=False, default=120)
    tap_onekey      = Field('int32',	8711, required=False)
    mall_silver_opened = Field('bool',	9040, required=False)
    mall_silver_open_cost = Field('int32',	9041, required=False)
    mall_silver_open_remain = Field('int32',	9042, required=False)
    mall_silver_open_vip = Field('int32',	9043, required=False)
    mall_golden_opened = Field('bool',	9056, required=False)
    mall_golden_open_cost = Field('int32',	9057, required=False)
    mall_golden_open_remain = Field('int32',	9058, required=False)
    mall_golden_open_vip = Field('int32',	9059, required=False)
    shopping        = Field('int32',	9060, required=False)
    mailcount       = Field('int32',	9216, required=False)
    vip_packs_flag  = Field('bool',	9475, required=False)
    wish_rest_count = Field('int32',	9554, required=False)
    wish_remain_time = Field('int32',	9555, required=False)
    wish_experience_time = Field('int32',	9556, required=False)
    weeks_acc_recharge_amount = Field('int32',	9558, required=False)
    weeks_acc_recharge_remain_time = Field('int32',	9559, required=False)
    weeks_acc_recharge_can_receive = Field('bool',	9560, required=False)
    daily_acc_recharge_amount = Field('int32',	9568, required=False)
    daily_acc_recharge_remain_time = Field('int32',	9570, required=False)
    daily_acc_recharge_can_receive = Field('bool',	9571, required=False)
    cycle_acc_recharge_amount = Field('int32',	9573, required=False)
    cycle_acc_recharge_remain_time = Field('int32',	9575, required=False)
    cycle_acc_recharge_can_receive = Field('bool',	9576, required=False)
    month_acc_recharge_amount = Field('int32',	9600, required=False)
    month_acc_recharge_remain_time = Field('int32',	9601, required=False)
    month_acc_recharge_can_receive = Field('bool',	9602, required=False)
    fund_bought_flag = Field('bool',	9728, required=False)
    fund_open_rewards_can_receive = Field('bool',	9730, required=False)
    fund_full_rewards_can_receive = Field('bool',	9731, required=False)
    check_in_over_count = Field('int32',	9983, required=False)
    check_in_used_count = Field('int32',	9984, required=False)
    check_in_rest_count = Field('int32',	9985, required=False)
    check_in_today  = Field('bool',	9986, required=False)
    timed_store_cd  = Field('int32',	10064, required=False)
    monthly_card    = Field('int32',	10313, required=False)
    monthly_card_received = Field('bool',	10320, required=False)
    monthly_card_remain_amount = Field('int32',	10323, required=False)
    skip_guide      = Field('bool',	10324, required=False)
    point_addition  = Field('int32',	10344, required=False)
    point           = Field('int32',	10345, required=False)
    stone           = Field('int32',	10352, required=False)
    enchant_stone_cost = Field('int32',	10353, required=False)
    enchant_ex_stone_cost = Field('int32',	10354, required=False)
    enchant_stone_to_gold = Field('int32',	10355, required=False)
    enchant_free_rest_count = Field('int32',	10358, required=False)
    dlc_opened      = Field('bool',	10391, required=False)
    count_down_flag = Field('bool',	10498, required=False)
    count_down_cd   = Field('int32',	10499, required=False)
    groupID         = Field('int32',	12289, required=False)
    group_applys_count = Field('int32',	12290, required=False)
    group_total_intimate = Field('int32',	12291, required=False)
    gve_damage      = Field('int32',	12306, required=False)
    gve_score       = Field('int32',	12308, required=False)
    gve_state       = Field('int32',	12314, required=False)
    gve_addition    = Field('int32',	12315, required=False)
    gve_groupdamage = Field('int32',	12316, required=False)
    gve_basereward  = Field('string',	12317, required=False)
    gve_reborn_rest_count = Field('int32',	12318, required=False, default=1)
    gve_start_time  = Field('int32',	12321, required=False)
    gve_end_time    = Field('int32',	12322, required=False)
    gve_buff        = Field('int32',	12323, required=False)
    gve_reborn_cost = Field('int32',	12324, required=False)
    gve_buff_addition = Field('int32',	12325, required=False)
    last_region_name = Field('string',	12544, required=False)
    boss_campaign_opened = Field('bool',	12800, required=False)
    skillpoint      = Field('int32',	13056, required=False)
    skillpoint_cd   = Field('int32',	13057, required=False)
    skillpoint_max  = Field('int32',	13058, required=False)
    buy_rest_skillpoint_count = Field('int32',	13060, required=False)
    buy_skillpoint_cost = Field('int32',	13061, required=False)
    buy_skillpoint_gain = Field('int32',	13062, required=False)
    buy_rest_soul_count = Field('int32',	13077, required=False)
    buy_soul_cost   = Field('int32',	13078, required=False)
    buy_soul_gain   = Field('int32',	13079, required=False)
    swap_cd         = Field('int32',	13313, required=False)
    swap_refresh_cd_cost = Field('int32',	13314, required=False)
    swap_rest_count = Field('int32',	13317, required=False)
    swap_most_count = Field('int32',	13318, required=False)
    swap_rest_reset_count = Field('int32',	13321, required=False)
    swap_reset_count_cost = Field('int32',	13329, required=False)
    swaprank        = Field('int32',	13330, required=False)
    swap_win_count  = Field('int32',	13333, required=False)
    ball            = Field('int32',	13568, required=False)
    maze_step_count = Field('int32',	13824, required=False)
    maze_rest_count = Field('int32',	13825, required=False)
    maze_count_cd   = Field('int32',	13826, required=False)
    maze_most_count = Field('int32',	13827, required=False)
    money_rest_pool = Field('int32',	13829, required=False)
    money_most_pool = Field('int32',	13830, required=False)
    online_packs_flag = Field('bool',	20483, required=False)
    maze_time_flag  = Field('int32',	22025, required=False)
    maze_case_cost  = Field('int32',	22032, required=False)
    maze_onekey_vip = Field('int32',	22033, required=False)
    maze_onekey_point = Field('int32',	22034, required=False)
    online_packs_cd = Field('int32',	22528, required=False)
    refinery        = Field('int32',	28673, required=False)
    daily_start_time = Field('int32',	32768, required=False)
    daily_final_time = Field('int32',	32769, required=False)
    daily_reborn_cost = Field('int32',	32774, required=False)
    daily_dead_cd   = Field('int32',	32775, required=False)
    daily_dead      = Field('bool',	32776, required=False)
    daily_kill_count = Field('int32',	32784, required=False)
    daily_registered = Field('bool',	32785, required=False)
    daily_count     = Field('int32',	32786, required=False)
    daily_win_count = Field('int32',	32787, required=False)
    daily_history_flag = Field('bool',	32790, required=False)
    daily_max_win_count = Field('int32',	32791, required=False)
    daily_rank      = Field('int32',	32792, required=False)
    daily_inspire_most_count = Field('int32',	32802, required=False, default=30)
    daily_inspire_rest_count = Field('int32',	32803, required=False)
    daily_inspire_buff = Field('int32',	32805, required=False)
    daily_inspire_cost = Field('int32',	32806, required=False)
    daily_end_panel_flag = Field('bool',	32808, required=False)
    task_seven_cd   = Field('int32',	33024, required=False)
    guide_reward_flag = Field('bool',	33280, required=False)
    guide_defeat_flag = Field('bool',	33281, required=False)
    ambition        = Field('string',	33536, required=False)
    vip_ambition    = Field('string',	33537, required=False)
    ambition_cost   = Field('int32',	33540, required=False)
    ambition_gold_cost = Field('int32',	33541, required=False)
    player_equip1   = Field('int32',	33792, required=False)
    player_equip2   = Field('int32',	33793, required=False)
    player_equip3   = Field('int32',	33794, required=False)
    player_equip4   = Field('int32',	33795, required=False)
    player_equip5   = Field('int32',	33796, required=False)
    player_equip6   = Field('int32',	33797, required=False)
    consume_campaign_rest_time = Field('int32',	34048, required=False)
    consume_campaign_rewards_flag = Field('bool',	34050, required=False)
    consume_campaign_amount = Field('int32',	34052, required=False)
    login_campaign_rest_time = Field('int32',	34128, required=False)
    login_campaign_rewards_flag = Field('bool',	34130, required=False)
    login_campaign_amount = Field('int32',	34132, required=False)
    daily_restHP    = Field('int32',	36983, required=False)
    daily_recharge_remain_time = Field('int32',	37120, required=False)
    daily_recharge_rewards_count = Field('int32',	37125, required=False)
    free_pet_exchange = Field('int32',	37632, required=False, default=3)
    pet_exchange_cd = Field('int32',	37633, required=False)
    lottery_campaign_cd = Field('int32',	37888, required=False)
    lottery_campaign_discount = Field('int32',	37889, required=False)
    lottery_campaign_hot = Field('string',	37890, required=False)
    lottery_campaign_hot_cd = Field('int32',	37891, required=False)
    mat_exchange_campaign_cd = Field('int32',	38144, required=False)
    city_dungeon_start_time = Field('int32',	38658, required=False)
    city_dungeon_final_time = Field('int32',	38659, required=False)
    city_dungeon_rewards_flag = Field('bool',	38662, required=False)
    city_dungeon_kill_count = Field('int32',	38665, required=False)
    city_treasure_recv_flag = Field('bool',	38672, required=False)
    city_contend_rewards_flag = Field('bool',	38914, required=False)
    city_contend_start_time = Field('int32',	38915, required=False)
    city_contend_final_time = Field('int32',	38916, required=False)
    city_contend_treasure = Field('int32',	38919, required=False)
    city_contend_step = Field('int32',	38920, required=False)
    city_contend_total_treasure = Field('int32',	38921, required=False)
    city_contend_count = Field('int32',	38928, required=False)
    monthcard1      = Field('int32',	39168, required=False)
    monthcard2      = Field('int32',	39169, required=False)
    monthcard_recv1 = Field('bool',	39170, required=False)
    monthcard_recv2 = Field('bool',	39172, required=False)
    weekscard1      = Field('int32',	39184, required=False)
    weekscard2      = Field('int32',	39185, required=False)
    weekscard_recv1 = Field('bool',	39186, required=False)
    weekscard_recv2 = Field('bool',	39188, required=False)
    exchange_campaign_remain_time = Field('int32',	39192, required=False)
    refresh_store_campaign_counter = Field('int32',	39193, required=False)
    refresh_store_campaign_remain_time = Field('int32',	39201, required=False)
    refresh_reward_done_count = Field('int32',	39204, required=False)
    arbor_day_campaign_remain_time = Field('int32',	39205, required=False)
    shake_tree_free_count = Field('int32',	39206, required=False)
    shake_tree_max_count = Field('int32',	39208, required=False)
    shake_tree_used_count = Field('int32',	39209, required=False)
    shake_tree_cost = Field('int32',	39218, required=False)
    seed_state      = Field('int32',	39219, required=False)
    seed_id         = Field('int32',	39220, required=False)
    seed_campaign_remain_time = Field('int32',	39221, required=False)
    seed_state_next_change_time = Field('int32',	39223, required=False)
    seed_state_ripening_time = Field('int32',	39232, required=False)
    watering_max_count = Field('int32',	39234, required=False)
    watering_used_count = Field('int32',	39235, required=False)
    watering_time   = Field('int32',	39237, required=False)
    worming_max_count = Field('int32',	39239, required=False)
    worming_used_count = Field('int32',	39240, required=False)
    worming_time    = Field('int32',	39248, required=False)
    seed_reward_index = Field('string',	39251, required=False)
    handsel_campaign_remain_time = Field('int32',	39267, required=False)
    campaign_honor_point = Field('string',	39268, required=False)
    flower_boss_campaign_remain_time = Field('int32',	39269, required=False)
    flower_boss_campaign_total_hurt = Field('int32',	39270, required=False)
    climb_tower_max_floor = Field('int32',	39424, required=False)
    climb_tower_floor = Field('int32',	39425, required=False)
    climb_tower_used_count = Field('int32',	39427, required=False)
    climb_tower_max_count = Field('int32',	39429, required=False)
    climb_tower_accredit_floor = Field('int32',	39433, required=False)
    climb_tower_accredit_lineup = Field('string',	39435, required=False)
    climb_tower_accredit_cd = Field('int32',	39438, required=False)
    phantom         = Field('int32',	39442, required=False)
    climb_tower_total_floor = Field('int32',	39444, required=False)

# file: sdk.proto
# enum SDKType
SDK_YY=0
SDK_IAPPPAY=1
SDK_JODO=2
SDK_ITOOLS_IOS=3
SDK_PP_IOS=4
SDK_LJ=5
SDK_YY_IOS=6
SDK_UC=7
SDK_YYZC=8
SDK_YYZCLH=9
SDK_TB_IOS=10
SDK_KY_IOS=11
SDK_XY_IOS=12
SDK_AS_IOS=13
SDK_APP_IOS=14
SDK_IIAPPLE_IOS=15
SDK_YYLH=16
SDK_BAIDU=17
SDK_XIAOMI=18
SDK_C360=19
SDK_OPPO=20
SDK_ANZHI=21
SDK_WDJ=22
SDK_WANKA=23
SDK_YYB=24
SDK_HM_IOS=25
SDK_ZC_IOS=26
SDK_HWD=27
SDK_GFAN=28
SDK_MM=29
SDK_M4399=30
SDK_PAOJIAO=31
SDK_PIPAW=32
SDK_YOUKU=33
SDK_YYH=34
SDK_ZY=35
SDK_KUGOU=36
SDK_EGAME=37
SDK_DOWNJOY=38
SDK_PPS=39
SDK_PPTV=40
SDK_MZW=41
SDK_VIVO=42
SDK_DUODUO_IOS=43
SDK_HAIMA=44
SDK_XYANDROID=45
SDK_WO17=46
SDK_MOLI=47
SDK_HUAWEI=48
SDK_WL=49
SDK_LX=50
SDK_GIONEE=51
SDK_COOLPAD=52
SDK_YIWAN=53
SDK_XX_IOS=54
SDK_XX=55
SDK_KAOPU=56
SDK_MEIZU=57
SDK_BAIDU2=58
SDK_WL2=59
SDK_HAOMENG=60
SDK_CC=61
SDK_YIJIE=62
SDK_TIANTIAN=63
SDK_HTC=64
SDK_LE8_IOS=65
SDK_MMY=66
SDK_H07073=67
SDK_PYW=68
SDK_LIULIAN=69
SDK_MOGE=70
# enum PlatformType
Platform_UNKNOWN=0
Platform_QQ=1
Platform_WEIXIN=2
class SDKStartPayResponse(ProtoEntity):
    serialNo        = Field('string',	1)

class iTunesStoreReceiptResponse(ProtoEntity):
    transaction_id  = Field('string',	1)
    successed       = Field('bool',	2)

class AndroidEditTextMessage(ProtoEntity):
    content         = Field('string',	1)

class DeviceInfo(ProtoEntity):
    os              = Field('string',	1, required=False)
    osVersion       = Field('string',	2, required=False)
    resolution      = Field('string',	3, required=False)
    IMEI            = Field('string',	4, required=False)
    UDID            = Field('string',	5, required=False)
    MAC             = Field('string',	6, required=False)
    UA              = Field('string',	7, required=False)
    clientVersion   = Field('string',	8, required=False)
    idfa            = Field('string',	9, required=False)
    deviceUniqueID  = Field('string',	10, required=False)
    appid           = Field('string',	11, required=False)

class iTunesStoreReceiptRequest(ProtoEntity):
    receipt         = Field('string',	1)

class PayResult(ProtoEntity):
    success         = Field('bool',	1)
    roleID          = Field('int32',	2)
    goods           = Field('int32',	3)
    count           = Field('int32',	4)
    userID          = Field('int32',	5)
    payID           = Field('string',	6)
    clientVersion   = Field('string',	7, required=False)
    data            = Field('string',	8, required=False)

class LJSDKInfo(ProtoEntity):
    userId          = Field('string',	1)
    channelUserID   = Field('string',	2)
    channelID       = Field('string',	3)
    channelLabel    = Field('string',	4)
    userName        = Field('string',	5)
    token           = Field('string',	6)
    productCode     = Field('string',	7)

class SDKLoginRequest(ProtoEntity):
    sdkType         = Field('enum',	1)
    sessionId       = Field('string',	2)
    uin             = Field('string',	3)
    deviceId        = Field('string',	4)
    regionID        = Field('int32',	5)
    featureCode     = Field('string',	6, required=False)
    deviceInfo      = Field(DeviceInfo,	7, required=False)
    platformType    = Field('enum',	8, required=False)
    ljsdkInfo       = Field(LJSDKInfo,	9, required=False)
    channel         = Field('string',	10, required=False)

class SDKStartPayRequest(ProtoEntity):
    sdkType         = Field('enum',	1)
    goodsid         = Field('string',	2, required=False)

class SDKPayEnable(ProtoEntity):
    pay             = Field('bool',	1)

# file: world.proto
class RechargeListRequest(ProtoEntity):
    type            = Field('int32',	1, required=False)

class ReconnectResponse(ProtoEntity):
    result          = Field('bool',	1)

class EnterRequest(ProtoEntity):
    entityID        = Field('int32',	1)
    featureCode     = Field('string',	2, required=False)
    clientVersion   = Field('string',	3, required=False)
    deviceInfo      = Field(DeviceInfo,	4, required=False)

class RechargeItem(ProtoEntity):
    id              = Field('int32',	1)
    name            = Field('string',	2)
    cmd1            = Field('string',	3)
    golden          = Field('int32',	4)
    amount          = Field('string',	5)
    currency        = Field('string',	6)
    goodsid         = Field('string',	7)
    gift_png        = Field('string',	8)
    first_tag       = Field('string',	9)
    general_tag     = Field('string',	10)
    first_drop      = Field('int32',	11)
    general_drop    = Field('int32',	12)
    general_cmd     = Field('string',	13)
    is_first        = Field('bool',	14, default=False)
    bright_point    = Field('bool',	15)
    lj_callback     = Field('string',	16, required=False)

class StarPack(ProtoEntity):
    # enum StarPacksState
    Unavailable=1
    Available=2
    Taken=3
    id              = Field('int32',	1)
    star            = Field('int32',	2)
    rewards         = Field('string',	3)
    state           = Field('enum',	4, default=Unavailable)
    sceneID         = Field('int32',	5)

class SyncProperty(ProtoEntity):
    # enum EntityType
    Me=-1
    Player=0
    Pet=1
    Npc=2
    Monster=3
    Equip=4
    entityID        = Field('int32',	1)
    type            = Field('enum',	2)
    properties      = Field(Property,	3, required=False)

class StarPacksRecv(ProtoEntity):
    id              = Field('int32',	1)
    guide_type      = Field('string',	2, required=False)

class HeartBeat(ProtoEntity):
    timestamp       = Field('int32',	1)

class ChangeAvatarOrBorderRequest(ProtoEntity):
    id              = Field('int32',	1)

class ResponseSlateInit(ProtoEntity):
    ID              = Field('int32',	1, repeated=True)

class NoticeStruct(ProtoEntity):
    ID              = Field('int32',	1)
    title           = Field('string',	2)
    content         = Field('string',	3)

class Notice(ProtoEntity):
    notices         = Field(NoticeStruct,	1, repeated=True)
    lottery         = Field('string',	2)

class MultiSyncProperty(ProtoEntity):
    entities        = Field(SyncProperty,	1, repeated=True)

class RequestSlateReward(ProtoEntity):
    ID              = Field('int32',	1)

class Reconnect(ProtoEntity):
    verify_code     = Field('string',	1)
    entityID        = Field('int32',	2)

class ComposeRequest(ProtoEntity):
    # enum ComposeType
    ComposePet=1
    ComposeEquip=2
    ComposeMat=3
    type            = Field('enum',	1)
    id              = Field('int32',	2)
    stuffs          = Field('int32',	3, repeated=True)

class QuitResponse(ProtoEntity):
    entityID        = Field('int32',	1)

class TestPay(ProtoEntity):
    count           = Field('int32',	1)

class StarPacksInfo(ProtoEntity):
    packs           = Field(StarPack,	1, repeated=True)

class RechargeListResponse(ProtoEntity):
    items           = Field(RechargeItem,	1, repeated=True)
    start           = Field('int32',	2, required=False)
    end             = Field('int32',	3, required=False)

class EnterResponse(ProtoEntity):
    ENABLE_GIFTKEY  = Field('bool',	1, required=False)
    ENABLE_RANKING_CAMPAIGN = Field('bool',	2, required=False)
    time            = Field('int32',	3, required=False)
    REV             = Field('string',	4, required=False)
    campaign_sequence = Field('string',	5, required=False)

# file: reward.proto
class Giftkey(ProtoEntity):
    key             = Field('string',	1)

class GuideRewardRecvRequest(ProtoEntity):
    guide_type      = Field('string',	1, required=False)

class VipDescRequest(ProtoEntity):
    vip             = Field('int32',	1)

class SceneRewardsRecvReqeust(ProtoEntity):
    id              = Field('int32',	1)
    guide_type      = Field('string',	2, required=False)

class VipPacksBuyRequest(ProtoEntity):
    ID              = Field('int32',	1)
    guide_type      = Field('string',	2, required=False)

class VipPacksInfoRequest(ProtoEntity):
    type            = Field('int32',	1)
    vip             = Field('int32',	2, required=False)

class RewardData(ProtoEntity):
    type            = Field('int32',	1)
    arg             = Field('int32',	2)
    count           = Field('int32',	3)
    property        = Field(SyncProperty,	4, required=False)

class SceneRewardsRecvResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class VipPack(ProtoEntity):
    ID              = Field('int32',	1)
    gift_name       = Field('string',	2)
    gift_sort       = Field('int32',	3)
    fixed_price_type = Field('int32',	4)
    fixed_price     = Field('int32',	5)
    discount_price_type = Field('int32',	6)
    discount_price  = Field('int32',	7)
    gifts_des       = Field('string',	8)
    vip_level       = Field('int32',	9)
    gift_name_png   = Field('string',	10)
    gift_label      = Field('string',	11)
    rewards         = Field(RewardData,	12, repeated=True)
    count           = Field('int32',	13)

class VipPacksInfo(ProtoEntity):
    packs           = Field(VipPack,	1, repeated=True)

class VipDescResponse(ProtoEntity):
    desc            = Field('string',	1)
    pack            = Field(VipPack,	2)

class MonthcardItem(ProtoEntity):
    id              = Field('int32',	1)
    gain            = Field('int32',	2)
    daily_gain      = Field(RewardData,	3, repeated=True)

class LoginReward(ProtoEntity):
    ID              = Field('int32',	1)
    reward          = Field(RewardData,	2)
    received        = Field('bool',	3)

class LoginRewardResponse(ProtoEntity):
    rewards         = Field(LoginReward,	1, repeated=True)
    curr            = Field('int32',	2)
    pop             = Field('bool',	3)

class GuideDefeatRecvResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class GiftkeyResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class MonthcardRecvResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class SceneRewardsInfoResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class FirstRechargeInfo(ProtoEntity):
    worth_gold      = Field('int32',	1)
    gift_gold       = Field('int32',	2)
    rewards         = Field(RewardData,	3, repeated=True)

class MonthcardInfoRequest(ProtoEntity):
    type            = Field('int32',	1)

class MonthcardRecv(ProtoEntity):
    id              = Field('int32',	1)

class SceneRewardsInfoReqeust(ProtoEntity):
    id              = Field('int32',	1)

class MonthcardInfo(ProtoEntity):
    items           = Field(MonthcardItem,	1, repeated=True)

class GuideRewardRecvResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

# file: equip.proto
# enum EquipType
EquipTypeWuqi=1
EquipTypeFangJu=2
EquipTypeTouKui=3
EquipTypeXueZi=4
EquipTypeFaBao=5
EquipTypeZuoQi=6
class EnchantEquip(ProtoEntity):
    equipID         = Field('int32',	1)
    locks           = Field('int32',	2, repeated=True)
    ex              = Field('bool',	3, required=False)

class StrengthenPlayerEquipResponse(ProtoEntity):
    count           = Field('int32',	1)

class StrengthenEquip(ProtoEntity):
    equipID         = Field('int32',	1)
    onekey          = Field('bool',	2)
    guide_type      = Field('string',	3, required=False)
    petID           = Field('int32',	4)

class StrengthenEquipsOnekeyResponse(ProtoEntity):
    incrs           = Field('int32',	1, repeated=True)

class AdvanceEquip(ProtoEntity):
    equipID         = Field('int32',	1)
    equips          = Field('int32',	3, repeated=True)
    mats            = Field('int32',	4, repeated=True)
    mats_count      = Field('int32',	5, repeated=True)
    petID           = Field('int32',	6)
    guide_type      = Field('string',	7, required=False)

class Equiped(ProtoEntity):
    equipID         = Field('int32',	1)
    index           = Field('int32',	3)
    prototypeID     = Field('int32',	4, required=False)
    level           = Field('int32',	5, required=False)
    step            = Field('int32',	6, required=False)
    enchant_attrs   = Field('string',	7, required=False)

class StrengthenEquipsOnekey(ProtoEntity):
    equips          = Field('int32',	1, repeated=True)

class SwapEquipsResponse(ProtoEntity):
    equipeds        = Field(Equiped,	1, repeated=True)

class StrengthenPlayerEquip(ProtoEntity):
    type            = Field('enum',	1)
    onekey          = Field('bool',	2)

class UninstallEquip(ProtoEntity):
    index           = Field('int32',	1)
    type            = Field('enum',	2)

class InstallEquip(ProtoEntity):
    petID           = Field('int32',	1)
    equipID         = Field('int32',	2)

class StrengthenEquipResponse(ProtoEntity):
    success         = Field('bool',	1)

class SwapEquip(ProtoEntity):
    index           = Field('int32',	1, repeated=True)

class SwapEquips(ProtoEntity):
    swaps           = Field(SwapEquip,	1, repeated=True)

# file: lineup.proto
# enum LineupType
LineupTypeATK=1
LineupTypeDEF=2
LineupTypeMine1=3
LineupTypeMine2=4
LineupTypeDaily=5
LineupTypeCity=6
LineupTypeAccredit=7
class ChangeLineupResponse(ProtoEntity):
    isSuccess       = Field('bool',	1)

class Lineup(ProtoEntity):
    line            = Field('sint32',	1, repeated=True)
    type            = Field('enum',	2)
    equipeds        = Field(Equiped,	3, repeated=True)

class Lineups(ProtoEntity):
    lineups         = Field(Lineup,	1, repeated=True)

class PetInfo(ProtoEntity):
    prototypeID     = Field('int32',	1, required=False)
    level           = Field('int32',	2, required=False)
    skill           = Field('int32',	3, required=False)
    subattr1        = Field('int32',	4, required=False)
    subattr2        = Field('int32',	5, required=False)
    posIndex        = Field('int32',	6, required=False)
    isTeamLeader    = Field('bool',	7, required=False)
    breaklevel      = Field('int32',	8, required=False, default=1)
    entityID        = Field('int32',	9, required=False)
    restHP          = Field('int32',	10, required=False)
    relations       = Field('string',	11, required=False)
    skill1          = Field('int32',	12, required=False)
    skill2          = Field('int32',	13, required=False)
    skill3          = Field('int32',	14, required=False)
    skill4          = Field('int32',	15, required=False)
    skill5          = Field('int32',	16, required=False)

class ChangeLineup(ProtoEntity):
    lineup          = Field(Lineup,	1, required=False)
    guide_type      = Field('string',	2, required=False)

# file: fightReplay.proto
# enum ActionType
attack=1
move=2
relive=3
class LargeConfig(ProtoEntity):
    cmd1            = Field('string',	1)
    cmd2            = Field('string',	2)
    flgPrm1         = Field('int32',	3)
    skill1          = Field('int32',	4)
    skill2          = Field('int32',	5)
    prob1           = Field('int32',	6)
    prob2           = Field('int32',	7)
    mvRge1TL        = Field('int32',	8)
    mvRge1T         = Field('int32',	9)
    mvRge1TR        = Field('int32',	10)
    mvRge1L         = Field('int32',	11)
    mvRge1R         = Field('int32',	12)
    mvRge1BL        = Field('int32',	13)
    mvRge1B         = Field('int32',	14)
    mvRge1BR        = Field('int32',	15)
    mvRge2TL        = Field('int32',	16)
    mvRge2T         = Field('int32',	17)
    mvRge2TR        = Field('int32',	18)
    mvRge2L         = Field('int32',	19)
    mvRge2R         = Field('int32',	20)
    mvRge2BL        = Field('int32',	21)
    mvRge2B         = Field('int32',	22)
    mvRge2BR        = Field('int32',	23)
    flg             = Field('int32',	24)

class Attr(ProtoEntity):
    _atk            = Field('int32',	1)
    _hp             = Field('int32',	2)
    _def            = Field('int32',	3)
    _crit           = Field('int32',	4)
    _dodge          = Field('int32',	5)

class skill_info(ProtoEntity):
    id              = Field('int32',	1)
    name            = Field('string',	2)
    desc            = Field('string',	3)
    effects         = Field('string',	4)
    probability     = Field('int32',	5)
    is_aura         = Field('int32',	6)
    is_additional   = Field('int32',	7)
    in_cd           = Field('int32',	8)
    round           = Field('int32',	9)
    action          = Field('int32',	10)
    active          = Field('int32',	11)
    rge             = Field('int32',	12)
    attr            = Field('int32',	13)
    state           = Field('int32',	14)
    attr_type       = Field('int32',	15)
    relative        = Field('int32',	16)
    param           = Field('int32',	17)
    compare_type    = Field('int32',	18)
    src_relationship = Field('int32',	19)
    src_attr        = Field('int32',	20)
    src_state       = Field('int32',	21)
    src_attr_type   = Field('int32',	22)
    src_relative    = Field('int32',	23)
    src_param       = Field('int32',	24)
    src_compare_type = Field('int32',	25)
    target_relationship = Field('int32',	26)
    target_attr     = Field('int32',	27)
    target_state    = Field('int32',	28)
    target_attr_type = Field('int32',	29)
    target_relative = Field('int32',	30)
    target_param    = Field('int32',	31)
    target_compare_type = Field('int32',	32)
    icon            = Field('string',	33)
    special_effect_name = Field('string',	34)
    special_effect_name_2 = Field('string',	35)
    play_effect_delay = Field('float',	36)

class fightAction(ProtoEntity):
    action_type     = Field('enum',	1)
    entity_id       = Field('int32',	2, required=False)
    mv_index        = Field('int32',	3, required=False)

class se_info(ProtoEntity):
    id              = Field('int32',	1)
    name            = Field('string',	2)
    target_type     = Field('int32',	3)
    targets         = Field('string',	4)
    rge             = Field('int32',	5)
    attr            = Field('int32',	6)
    state_param     = Field('string',	7)
    kind            = Field('int32',	8)
    relative        = Field('int32',	9)
    param           = Field('int32',	10)
    abs_param       = Field('int32',	11)
    round           = Field('int32',	12)
    additional      = Field('int32',	13)
    tri_param       = Field('string',	14)
    additional_beak_back = Field('int32',	15)
    display_type    = Field('int32',	16)
    lv_param        = Field('int32',	17)
    lv_abs_param    = Field('int32',	18)
    lv_probability  = Field('int32',	19)

class FighterSkillInfo(ProtoEntity):
    id              = Field('int32',	1)
    level           = Field('int32',	2)

class fighterInfo(ProtoEntity):
    type            = Field('string',	1)
    config_id       = Field('int32',	2)
    random_index    = Field('int32',	3)
    level           = Field('int32',	4)
    attr            = Field('int32',	5)
    model           = Field('int32',	6)
    size            = Field('int32',	7)
    rarity          = Field('int32',	8)
    ability         = Field('int32',	9)
    mvRgeTL         = Field('int32',	10)
    mvRgeT          = Field('int32',	11)
    mvRgeTR         = Field('int32',	12)
    mvRgeR          = Field('int32',	13)
    mvRgeBR         = Field('int32',	14)
    mvRgeB          = Field('int32',	15)
    mvRgeBL         = Field('int32',	16)
    mvRgeL          = Field('int32',	17)
    same            = Field('int32',	18)
    mtype           = Field('int32',	19)
    entity_id       = Field('int32',	20)
    real_entity_id  = Field('int32',	21, required=False)
    pos_index       = Field('int32',	22, required=False)
    team_pos_index  = Field('int32',	23)
    base_attr       = Field(Attr,	24)
    faction_attr    = Field(Attr,	25)
    equip_attr      = Field(Attr,	26)
    buff_attr       = Field(Attr,	27)
    origin_hp       = Field('int32',	28, required=False)
    skill_ids       = Field(FighterSkillInfo,	29, repeated=True)
    origin_scale    = Field('float',	30)
    drop1           = Field(RewardData,	31, repeated=True)
    drop2           = Field(RewardData,	32, repeated=True)
    equipeds        = Field('int32',	33, repeated=True)
    all_large_config = Field(LargeConfig,	34, repeated=True)
    relations       = Field('string',	35, required=False)
    restrain_2      = Field('float',	36)
    restrain_0      = Field('float',	37)

class areaInfo(ProtoEntity):
    enemy_fighters  = Field(fighterInfo,	1, repeated=True)
    replace_list    = Field(fighterInfo,	2, repeated=True)

class buff_info(ProtoEntity):
    type            = Field('string',	1)
    last_round      = Field('int32',	2)
    kind            = Field('int32',	3)
    val             = Field('int32',	4)

class fightReplay(ProtoEntity):
    is_win          = Field('bool',	1)
    bg_id           = Field('int32',	2)
    fight_type      = Field('string',	3)
    is_new          = Field('bool',	4)
    stone_num       = Field('int32',	5)
    random_index    = Field('int32',	6)
    max_last_round  = Field('int32',	7)
    round_fight_state = Field('string',	8)
    player_fighters = Field(fighterInfo,	9, repeated=True)
    areas           = Field(areaInfo,	10, repeated=True)
    actions         = Field(fightAction,	11, repeated=True)
    skill_list      = Field(skill_info,	12, repeated=True)
    se_info_list    = Field(se_info,	13, repeated=True)
    buff_group_index = Field('int32',	14)
    buff_info_list  = Field(buff_info,	15, repeated=True)
    is_player_turn  = Field('bool',	16, required=False)

class Fight(ProtoEntity):
    fightResult     = Field('bool',	1, required=False)
    round           = Field('int32',	2, required=False)
    replay          = Field(fightReplay,	3)
    player_members_count = Field('int32',	4, required=False)
    enemy_members_count = Field('int32',	5, required=False)
    player_death_count = Field('int32',	6, required=False)
    enemy_death_count = Field('int32',	7, required=False)
    player_team     = Field(PetInfo,	8, repeated=True)
    enemy_team      = Field(PetInfo,	9, repeated=True)
    total_damage    = Field('int32',	10, required=False)

# file: friend.proto
class InviteFriend(ProtoEntity):
    friendfbID      = Field('string',	1)
    ids             = Field('int32',	2, repeated=True)

class EndFriendfbResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    error_code      = Field('int32',	2, required=False)

class GiftFriend(ProtoEntity):
    ids             = Field('int32',	1, repeated=True)

class ApplyFriend(ProtoEntity):
    id              = Field('int32',	1)

class FriendfbRewardRankingItem(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    start           = Field('int32',	2)
    final           = Field('int32',	3)

class EndFriendfb(ProtoEntity):
    fight           = Field(Fight,	1)
    verify_code     = Field('string',	2, required=False)

class ChatFriend(ProtoEntity):
    friendID        = Field('int32',	1)
    content         = Field('string',	2)

class FriendfbDetailRequest(ProtoEntity):
    friendfbID      = Field('string',	1)

class FriendfbRank(ProtoEntity):
    name            = Field('string',	1)
    prototypeID     = Field('int32',	2)
    damage          = Field('int32',	3)
    entityID        = Field('int32',	4)
    rank            = Field('int32',	5, required=False)
    level           = Field('int32',	6, required=False)
    faction_name    = Field('string',	7, required=False)
    borderID        = Field('int32',	8, required=False)

class FriendfbRewardRanking(ProtoEntity):
    items           = Field(FriendfbRewardRankingItem,	1, repeated=True)
    ranks           = Field(FriendfbRank,	2, repeated=True)
    maxdamage       = Field('int32',	3)
    self            = Field(FriendfbRank,	4, required=False)

class FriendInfo(ProtoEntity):
    id              = Field('int32',	1)
    name            = Field('string',	2)
    prototypeID     = Field('int32',	3)
    level           = Field('int32',	4)
    time            = Field('int32',	5, required=False)
    vip             = Field('int32',	6, required=False)
    gifted          = Field('bool',	7, required=False)
    dlc_cd          = Field('int32',	8, required=False)
    groupID         = Field('int32',	9, required=False)
    borderID        = Field('int32',	10, required=False)
    messages_count  = Field('int32',	11, required=False)

class InviteFriendListResponse(ProtoEntity):
    friends         = Field(FriendInfo,	1, repeated=True)

class FriendList(ProtoEntity):
    friends         = Field(FriendInfo,	1, repeated=True)

class ApplysList(ProtoEntity):
    applys          = Field(FriendInfo,	1, repeated=True)

class InviteFriendList(ProtoEntity):
    friendfbID      = Field('string',	1)

class AllowFriend(ProtoEntity):
    id              = Field('int32',	1)

class GiftFriendResponse(ProtoEntity):
    ids             = Field('int32',	1, repeated=True)
    rewards         = Field(RewardData,	2, repeated=True)

class Friendfb(ProtoEntity):
    friendfbID      = Field('string',	1)
    name            = Field('string',	2)
    bossID          = Field('int32',	3)
    remain          = Field('int32',	4)
    maxhp           = Field('int32',	5)
    hp              = Field('int32',	6)
    done            = Field('bool',	7)
    pname           = Field('string',	8)
    ownerID         = Field('int32',	9)
    owner           = Field('string',	10, required=False)
    open_cd         = Field('int32',	11, required=False)
    desc            = Field('string',	12, required=False)

class DenyFriend(ProtoEntity):
    id              = Field('int32',	1)

class RebornFriendfb(ProtoEntity):
    friendfbID      = Field('string',	1)

class RemoveFriend(ProtoEntity):
    id              = Field('int32',	1)

class EnterFriendfb(ProtoEntity):
    friendfbID      = Field('string',	1)

class RankingFriendfb(ProtoEntity):
    friendfbID      = Field('string',	1)

class FriendMessage(ProtoEntity):
    time            = Field('int32',	1)
    content         = Field('string',	2)

class FriendMessages(ProtoEntity):
    messages        = Field(FriendMessage,	1, repeated=True)
    senderID        = Field('int32',	2)

class ListenFriend(ProtoEntity):
    friendID        = Field('int32',	1)

class EnterFriendfbResponse(ProtoEntity):
    bossID          = Field('int32',	1)
    maxhp           = Field('int32',	2)
    hp              = Field('int32',	3)
    verify_code     = Field('string',	4, required=False)

class FriendfbList(ProtoEntity):
    friendfbs       = Field(Friendfb,	1, repeated=True)

class FriendfbDetail(ProtoEntity):
    friendfb        = Field(Friendfb,	1)
    rewards         = Field('string',	3)
    reborn_cost     = Field('int32',	4)
    is_dead         = Field('bool',	5)

class RecommendsList(ProtoEntity):
    recommends      = Field(FriendInfo,	1, repeated=True)

# file: campaign.proto
# enum SeedState
SeedStateNormal=0
SeedStateSeed=1
SeedStateSapling=2
SeedStateTree=3
SeedStateRipening=4
SeedStateRoot=5
class ExchangeCampaignInfo(ProtoEntity):
    sourcePrototypeID = Field('int32',	1)
    targetPrototypeID = Field('int32',	2)
    mats            = Field(RewardData,	3, repeated=True)
    desc            = Field('string',	4)
    bg              = Field('string',	5)

class PetExchangeRequest(ProtoEntity):
    pets            = Field('int32',	1, repeated=True)
    exchange_type   = Field('int32',	2)

class PowerPacksRecv(ProtoEntity):
    id              = Field('int32',	1)

class RecvMonthlyCard(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class LoginCampaignItem(ProtoEntity):
    ID              = Field('int32',	1)
    rewards         = Field(RewardData,	2, repeated=True)
    day             = Field('int32',	3)
    state           = Field('int32',	4)

class OnlinePacksRecv(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    is_last         = Field('bool',	2, required=False)

class PetExchangeInfoResponse(ProtoEntity):
    open_type       = Field('int32',	1)

class DailyRechargeItem(ProtoEntity):
    id              = Field('int32',	1)
    rewards         = Field(RewardData,	2, repeated=True)
    gold            = Field('int32',	3)
    count           = Field('int32',	4)
    used            = Field('int32',	5)
    can_receive     = Field('bool',	6)

class OnlinePacksInfo(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class SeedWateringWormingResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class RecvAccRechargeRewardResponse(ProtoEntity):
    more            = Field('bool',	1)

class RecvAccRechargeRewardRequest(ProtoEntity):
    ID              = Field('int32',	1)

class FlowerBossCampaignInfo(ProtoEntity):
    total_hurt      = Field('int32',	1)
    total_count     = Field('int32',	2)
    reward_multiple = Field('int32',	3)
    fbDetail        = Field(FriendfbDetail,	4)

class SeedCleanResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class SeedCropRequest(ProtoEntity):
    seedID          = Field('int32',	1)

class RecvFundRewardRequest(ProtoEntity):
    ID              = Field('int32',	1)

class FundRewardItem(ProtoEntity):
    # enum FundRewardItemState
    FundRewardItemStateNormal=1
    FundRewardItemStateFinish=2
    FundRewardItemStateEnding=3
    ID              = Field('int32',	1)
    rewards         = Field(RewardData,	2, repeated=True)
    desc            = Field('string',	3)
    state           = Field('enum',	4)

class RewardCampaignItem(ProtoEntity):
    desc            = Field('string',	1)
    opened          = Field('bool',	2)

class RewardCampaignInfo(ProtoEntity):
    items           = Field(RewardCampaignItem,	1, repeated=True)

class ExchangeCampaignItemResponse(ProtoEntity):
    items           = Field(RewardData,	1, repeated=True)

class CheckInfoItem(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    vip             = Field('int32',	2)
    cost            = Field('int32',	3)

class LevelPacksRecv(ProtoEntity):
    id              = Field('int32',	1)

class HandselItem(ProtoEntity):
    item_id         = Field('int32',	1)
    cost_type       = Field(RewardData,	2)
    camp_count      = Field('int32',	4)

class RefreshRewardItem(ProtoEntity):
    # enum RefreshRewardItemState
    RefreshRewardItemStateNormal=1
    RefreshRewardItemStateFinish=2
    RefreshRewardItemStateEnding=3
    ID              = Field('int32',	1)
    rewards         = Field(RewardData,	2, repeated=True)
    count           = Field('int32',	3)
    state           = Field('enum',	4)

class FundInfo(ProtoEntity):
    items           = Field(FundRewardItem,	1, repeated=True)
    count           = Field('int32',	2)
    vip             = Field('int32',	3)
    gold            = Field('int32',	4)

class AccRechargeItem(ProtoEntity):
    # enum AccRechargeItemState
    AccRechargeItemStateNormal=1
    AccRechargeItemStateFinish=2
    AccRechargeItemStateEnding=3
    ID              = Field('int32',	1)
    rewards         = Field(RewardData,	2, repeated=True)
    gold            = Field('int32',	3)
    state           = Field('enum',	4)

class AccRechargeInfo(ProtoEntity):
    items           = Field(AccRechargeItem,	1, repeated=True)

class DailyRechargeInfo(ProtoEntity):
    items           = Field(DailyRechargeItem,	1, repeated=True)

class ArborDayYYYResponse(ProtoEntity):
    index           = Field('int32',	1)
    rewards         = Field(RewardData,	2, repeated=True)

class PowerPacksItem(ProtoEntity):
    # enum PowerPacksItemState
    PowerPacksItemStateNormal=1
    PowerPacksItemStateFinish=2
    PowerPacksItemStateEnding=3
    id              = Field('int32',	1)
    rewards         = Field(RewardData,	3, repeated=True)
    state           = Field('enum',	4)

class PowerPacksInfo(ProtoEntity):
    items           = Field(PowerPacksItem,	2, repeated=True)

class RecvDailyRechargeRequest(ProtoEntity):
    id              = Field('int32',	1)

class FundInfoRequest(ProtoEntity):
    type            = Field('int32',	1)

class RefreshStoreRecv(ProtoEntity):
    ID              = Field('int32',	1)

class SeedReapRequest(ProtoEntity):
    index           = Field('int32',	1)

class CountDownInfo(ProtoEntity):
    gift_png        = Field('string',	1)
    rewards         = Field(RewardData,	2, repeated=True)
    particle_effect = Field('string',	3)

class HandselOpResponse(ProtoEntity):
    personal_count  = Field('int32',	1)
    total_count     = Field('int32',	2)
    next_lv_count   = Field('int32',	3)
    reward_multiple = Field('int32',	4)
    next_reward_multiple = Field('int32',	5)

class TimedStoreInfo(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    cost            = Field('int32',	2)
    store_png       = Field('string',	3)
    fixed_price     = Field('int32',	4)

class ConsumeCampaignRecv(ProtoEntity):
    ID              = Field('int32',	1)

class RecvDailyRechargeResponse(ProtoEntity):
    more            = Field('bool',	1)

class AccRechargeInfoRequest(ProtoEntity):
    type            = Field('int32',	1)

class LoginCampaignRecv(ProtoEntity):
    ID              = Field('int32',	1)

class MonthlyCardInfo(ProtoEntity):
    need            = Field('int32',	1)
    gold            = Field('int32',	2)

class HandselCampaignInfo(ProtoEntity):
    personal_count  = Field('int32',	1)
    total_count     = Field('int32',	2)
    next_lv_count   = Field('int32',	3)
    reward_multiple = Field('int32',	4)
    next_reward_multiple = Field('int32',	5)
    items           = Field(HandselItem,	6, repeated=True)

class ExchageCampaignRequest(ProtoEntity):
    hero_id         = Field('int32',	1)

class MatExchangeItem(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    count           = Field('int32',	2)
    rest            = Field('int32',	3)
    id              = Field('int32',	4)

class MatExchangeInfo(ProtoEntity):
    items           = Field(MatExchangeItem,	1, repeated=True)
    bg              = Field('string',	2)

class LoginCampaignInfo(ProtoEntity):
    items           = Field(LoginCampaignItem,	1, repeated=True)
    tip             = Field('string',	2)

class HandselOperation(ProtoEntity):
    item_id         = Field('int32',	1)
    count           = Field('int32',	2)

class MatExchangeRequest(ProtoEntity):
    id              = Field('int32',	1)

class LevelPacksItem(ProtoEntity):
    # enum LevelPacksItemState
    LevelPacksItemStateNormal=1
    LevelPacksItemStateFinish=2
    LevelPacksItemStateEnding=3
    id              = Field('int32',	1)
    level           = Field('int32',	2)
    rewards         = Field('string',	3)
    state           = Field('enum',	4)

class LevelPacksInfo(ProtoEntity):
    items           = Field(LevelPacksItem,	2, repeated=True)

class RefreshStoreInfo(ProtoEntity):
    items           = Field(RefreshRewardItem,	1, repeated=True)
    desc            = Field('string',	2)

class WishInfo(ProtoEntity):
    start           = Field('int32',	1)
    ending          = Field('int32',	2)
    cost            = Field('int32',	3)
    cost_type       = Field('int32',	4)
    result          = Field('int32',	5, required=False)

class CheckInInfo(ProtoEntity):
    items           = Field(CheckInfoItem,	1, repeated=True)

class ConsumeCampaignItem(ProtoEntity):
    ID              = Field('int32',	1)
    rewards         = Field(RewardData,	2, repeated=True)
    consume         = Field('int32',	3)
    state           = Field('int32',	4)

class ConsumeCampaignInfo(ProtoEntity):
    consume_type    = Field('int32',	1)
    tip             = Field('string',	2)
    items           = Field(ConsumeCampaignItem,	3, repeated=True)

class PetExchange(ProtoEntity):
    pet_id          = Field('int32',	1)
    config_id       = Field('int32',	2)

class PetExchangeResponse(ProtoEntity):
    pets            = Field(PetExchange,	1, repeated=True)

# file: chat.proto
class GetCacheMessagesRequest(ProtoEntity):
    type            = Field('int32',	1)

class ChatType(ProtoEntity):
    # enum types
    System=1
    Tips=2
    World=3
    Faction=4
    Group=5
    pass

class Message(ProtoEntity):
    type            = Field('int32',	1)
    content         = Field('string',	2)
    name            = Field('string',	3, required=False)
    entityID        = Field('int32',	4, required=False)
    rewards         = Field(RewardData,	5, repeated=True)
    duration        = Field('int32',	6, required=False)
    prototypeID     = Field('int32',	7, required=False)
    is_faction_leader = Field('bool',	8, required=False)
    borderID        = Field('int32',	9, required=False)

class GetTipsMessagesResponse(ProtoEntity):
    messages        = Field(Message,	1, repeated=True)

class GetCacheMessagesResponse(ProtoEntity):
    type            = Field('int32',	1)
    messages        = Field(Message,	2, repeated=True)

class SendMessageRequest(ProtoEntity):
    content         = Field('string',	1)
    type            = Field('int32',	2)

# file: pvp.proto
# enum MineType
MineType1=1
MineType2=2
class UproarOpenChestResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class ClimbTowerInfoRequest(ProtoEntity):
    floor           = Field('int32',	1, required=False)

class RobTarget(ProtoEntity):
    ID              = Field('int32',	1)
    entityID        = Field('int32',	2)
    booty           = Field('int32',	3)
    fought          = Field('bool',	4)
    name            = Field('string',	5)
    prototypeID     = Field('int32',	6)
    level           = Field('int32',	7)
    type            = Field('int32',	8)

class LootTarget(ProtoEntity):
    type            = Field('int32',	1)
    power           = Field('int32',	2, required=False, default=0)

class ClimbTowerSwipeFloor(ProtoEntity):
    floor           = Field('int32',	1)
    rewards         = Field(RewardData,	2, repeated=True)

class NpcTarget(ProtoEntity):
    name            = Field('string',	1)
    prototypeID     = Field('int32',	2)
    power           = Field('int32',	3)
    breaklevel      = Field('int32',	4)
    cd              = Field('int32',	5)
    openlevel       = Field('int32',	6)
    rewards         = Field(RewardData,	7, repeated=True)

class TargetDetailResponse(ProtoEntity):
    pets            = Field(PetInfo,	1, repeated=True)
    name            = Field('string',	2, required=False)
    prototypeID     = Field('int32',	3, required=False)
    verify_code     = Field('string',	4, required=False)
    equipeds        = Field(Equiped,	5, repeated=True)
    level           = Field('int32',	6, required=False)
    entityID        = Field('int32',	7, required=False)
    pvprank         = Field('int32',	8, required=False)
    totalbp         = Field('int32',	9, required=False)
    rank_win_count  = Field('int32',	10, required=False)
    faction_name    = Field('string',	11, required=False)
    pets2           = Field(PetInfo,	12, repeated=True)
    totalfp         = Field('int32',	13, required=False)
    todayfp         = Field('int32',	14, required=False)
    time            = Field('int32',	15, required=False)
    jointime        = Field('int32',	16, required=False)
    strengthen_hp_level = Field('int32',	17, required=False)
    strengthen_at_level = Field('int32',	18, required=False)
    strengthen_ct_level = Field('int32',	19, required=False)
    defeated        = Field('bool',	20, required=False)
    vip             = Field('int32',	21, required=False)
    beMyFriend      = Field('bool',	22, required=False)
    applied         = Field('bool',	23, required=False)
    dlc_cd          = Field('int32',	24, required=False)
    online          = Field('bool',	25, required=False)
    pvpgrad         = Field('int32',	26, required=False)
    intimate        = Field('int32',	27, required=False)
    swaprank        = Field('int32',	28, required=False)
    borderID        = Field('int32',	29, required=False)
    strengthen_df_level = Field('int32',	30, required=False)
    point           = Field('int32',	31, required=False)
    swap_win_count  = Field('int32',	32, required=False)
    daily_kill_count = Field('int32',	33, required=False)
    red_count       = Field('int32',	34, required=False)
    daily_max_win_count = Field('int32',	35, required=False)
    power           = Field('int32',	36, required=False)
    daily_inspire_buff = Field('int32',	37, required=False)
    ambition        = Field('string',	38, required=False)
    vip_ambition    = Field('string',	39, required=False)
    player_equip1   = Field('int32',	40, required=False)
    player_equip2   = Field('int32',	41, required=False)
    player_equip3   = Field('int32',	42, required=False)
    player_equip4   = Field('int32',	43, required=False)
    player_equip5   = Field('int32',	44, required=False)
    player_equip6   = Field('int32',	45, required=False)
    fbprocess       = Field('int32',	46, required=False)
    fbadvance       = Field('int32',	47, required=False)
    cd              = Field('int32',	48, required=False)
    inlay1          = Field('int32',	49, required=False)
    inlay2          = Field('int32',	50, required=False)
    inlay3          = Field('int32',	51, required=False)
    inlay4          = Field('int32',	52, required=False)
    inlay5          = Field('int32',	53, required=False)
    inlay6          = Field('int32',	54, required=False)
    handsel_counter = Field('int32',	55, required=False)
    campaign_honor_point = Field('string',	56, required=False)

class RedInfoRequest(ProtoEntity):
    red             = Field('string',	1)

class ResponsePvpRank(ProtoEntity):
    opponents       = Field(TargetDetailResponse,	1, repeated=True)
    hasnext         = Field('bool',	2, default=False)

class DailyFinalFightResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    before_daily_win_count = Field('int32',	2)
    daily_win_count = Field('int32',	3)
    daily_max_win_count = Field('int32',	4, required=False)
    max_win_count   = Field('int32',	5, required=False)

class UproarTargetDetailRequest(ProtoEntity):
    index           = Field('int32',	1)

class ClimbTowerChest(ProtoEntity):
    # enum ClimbTowerChestState
    Unavailable=1
    Available=2
    Taken=3
    floor           = Field('int32',	1)
    rewards         = Field(RewardData,	2, repeated=True)
    state           = Field('enum',	3, default=Unavailable)

class LootListRequest(ProtoEntity):
    refresh         = Field('bool',	1, required=False)

class RobReplayRequest(ProtoEntity):
    ID              = Field('int32',	1)

class PvpHistory(ProtoEntity):
    score           = Field('sint32',	1)
    isActive        = Field('bool',	2)
    isWin           = Field('bool',	3)
    name            = Field('string',	4)
    level           = Field('int32',	5)
    time            = Field('int32',	6)
    ID              = Field('string',	7)
    prototypeID     = Field('int32',	8)
    can_revenge     = Field('bool',	9)
    faction_name    = Field('string',	10)
    before_rank     = Field('int32',	11)
    after_rank      = Field('int32',	12)

class PvpHistoryList(ProtoEntity):
    items           = Field(PvpHistory,	1, repeated=True)

class TargetDetailRequest(ProtoEntity):
    entityID        = Field('int32',	1)

class DailyFinalFightRequest(ProtoEntity):
    verify_code     = Field('string',	1)
    fight           = Field(Fight,	2, required=False)

class ClimbTowerOpenChestResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class ClimbTowerOpenChestRequest(ProtoEntity):
    floor           = Field('int32',	1)

class ClimbTowerSwipeResponse(ProtoEntity):
    floors          = Field(ClimbTowerSwipeFloor,	1, repeated=True)
    is_accredit     = Field('bool',	2, default=False)

class SwapInfoRequest(ProtoEntity):
    refresh         = Field('bool',	1, required=False)

class ClimbTowerEndFightResponse(ProtoEntity):
    limit           = Field('int32',	1)
    rewards         = Field(RewardData,	2, repeated=True)

class PvpReward(ProtoEntity):
    title           = Field('string',	1)
    rewards         = Field(RewardData,	2, repeated=True)
    start           = Field('int32',	3, required=False)
    final           = Field('int32',	4, required=False)
    grad_png        = Field('string',	5, required=False)
    grad            = Field('int32',	6, required=False)

class MineCollectResponse(ProtoEntity):
    booty           = Field('int32',	1)

class MineRobListResponse(ProtoEntity):
    targets         = Field(RobTarget,	1, repeated=True)

class DailyReplayRequest(ProtoEntity):
    index           = Field('int32',	1)

class SwapFinalChallengeRequest(ProtoEntity):
    targetID        = Field('int32',	1)
    verify_code     = Field('string',	2)
    fight           = Field(Fight,	3, required=False)

class LootComposeRequest(ProtoEntity):
    cub             = Field('int32',	1)

class RedRecvResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class PvpEndFightResponse(ProtoEntity):
    getBP           = Field('sint32',	1, required=False)
    errorcode       = Field('int32',	2, required=False)
    booty           = Field('int32',	3, required=False)
    loot_count      = Field('int32',	4, required=False)
    gp              = Field('int32',	5, required=False)
    rewards         = Field(RewardData,	6, repeated=True)
    cd              = Field('int32',	7, required=False)

class RobHistory(ProtoEntity):
    ID              = Field('int32',	1)
    entityID        = Field('int32',	2)
    level           = Field('int32',	3)
    name            = Field('string',	4)
    prototypeID     = Field('int32',	5)
    booty           = Field('int32',	6)
    revenge         = Field('bool',	7)
    type            = Field('int32',	8)
    win             = Field('bool',	9)
    time            = Field('int32',	10)
    fought          = Field('bool',	11)

class RobHistoryList(ProtoEntity):
    items           = Field(RobHistory,	1, repeated=True)

class ClimbTowerHistoryItem(ProtoEntity):
    id              = Field('string',	1)
    name            = Field('string',	2)
    faction         = Field('string',	3)
    timestamp       = Field('int32',	4)
    prototypeID     = Field('int32',	5)
    borderID        = Field('int32',	6)
    win             = Field('bool',	7, default=False)
    tip_type        = Field('int32',	8, required=False)
    tip_earnings    = Field('int32',	9, required=False)

class PvpTargetsRequest(ProtoEntity):
    refresh         = Field('bool',	1)
    usegold         = Field('bool',	2)

class RedInfo(ProtoEntity):
    name            = Field('string',	1)
    message         = Field('string',	2)
    prototypeID     = Field('int32',	3)
    borderID        = Field('int32',	4)
    type            = Field('int32',	5)
    cd              = Field('int32',	6, required=False)
    count           = Field('int32',	7, required=False)
    red             = Field('string',	8, required=False)
    order           = Field('string',	9)
    to_self         = Field('bool',	10)
    module          = Field('int32',	11)

class DailyStartFightResponse(ProtoEntity):
    cd              = Field('int32',	1)
    verify_code     = Field('string',	2)

class RankPanelItem(ProtoEntity):
    name            = Field('string',	1)
    level           = Field('int32',	2)
    daily_max_win_count = Field('int32',	3)
    daily_kill_count = Field('int32',	4)

class NpcTargetDetailRequest(ProtoEntity):
    index           = Field('int32',	1)

class MineRobListRequest(ProtoEntity):
    refresh         = Field('bool',	1)

class SwapmaxrankInfo(ProtoEntity):
    swapmaxrank     = Field('int32',	1)
    rewards         = Field(RewardData,	2, repeated=True)

class DailyHistory(ProtoEntity):
    name            = Field('string',	1)
    faction_name    = Field('string',	2)
    daily_win_count = Field('int32',	3)
    win             = Field('bool',	4)
    active          = Field('bool',	5)
    shutdown        = Field('bool',	6)
    prototypeID     = Field('int32',	7)
    borderID        = Field('int32',	9)
    point           = Field('int32',	10)

class DailyHistoryList(ProtoEntity):
    histories       = Field(DailyHistory,	1, repeated=True)

class PvpTargets(ProtoEntity):
    targets         = Field(TargetDetailResponse,	1, repeated=True)

class ClimbTowerChestsResponse(ProtoEntity):
    chests          = Field(ClimbTowerChest,	1, repeated=True)

class DailyEndPanel(ProtoEntity):
    daily_rank      = Field('int32',	1)
    daily_max_win_count = Field('int32',	2)
    daily_kill_count = Field('int32',	3)
    rewards         = Field(RewardData,	4, repeated=True)

class NpcTargets(ProtoEntity):
    targets         = Field(NpcTarget,	1, repeated=True)

class LootHistory(ProtoEntity):
    entityID        = Field('int32',	1)
    name            = Field('string',	2)
    level           = Field('int32',	3)
    prototypeID     = Field('int32',	4)
    loot            = Field('int32',	5, required=False)
    count           = Field('int32',	6, required=False)

class LootHistoryList(ProtoEntity):
    items           = Field(LootHistory,	1, repeated=True)

class LivePanelItem(ProtoEntity):
    self_name       = Field('string',	1)
    self_prototypeID = Field('int32',	2)
    self_borderID   = Field('int32',	3)
    peer_name       = Field('string',	4)
    peer_prototypeID = Field('int32',	5)
    peer_borderID   = Field('int32',	6)
    is_win          = Field('bool',	7)

class ClimbTowerHistoryListResponse(ProtoEntity):
    items           = Field(ClimbTowerHistoryItem,	1, repeated=True)

class ClimbTowerAccreditInfoResponse(ProtoEntity):
    tip_count       = Field('int32',	1)
    tip_type        = Field('int32',	2)
    tip_earnings    = Field('int32',	3)
    accredit_type   = Field('int32',	4)
    accredit_earnings = Field('int32',	5)
    accredit_earnings_per_minute = Field('int32',	6)

class ClimbTowerHistoryRequest(ProtoEntity):
    id              = Field('string',	1)

class DailyPanelResponse(ProtoEntity):
    lives           = Field(LivePanelItem,	1, repeated=True)
    ranks           = Field(RankPanelItem,	2, repeated=True)
    rewards         = Field(RewardData,	3, repeated=True)
    reds            = Field(RedInfo,	4, repeated=True)
    registers       = Field('int32',	5)
    target          = Field(TargetDetailResponse,	6, required=False)

class SwapStartChallengeResponse(ProtoEntity):
    cd              = Field('int32',	1)
    verify_code     = Field('string',	2)

class PvpStartFightRequest(ProtoEntity):
    id              = Field('int32',	1)
    lineup          = Field(Lineup,	2, required=False)
    cub             = Field('int32',	3, required=False)
    revenge         = Field('bool',	4, required=False)
    timestamp       = Field('int32',	5, required=False)

class PvpReplayRequest(ProtoEntity):
    ID              = Field('string',	1)

class UproarOpenChestRequest(ProtoEntity):
    index           = Field('int32',	1)

class SwapFinalChallengeResponse(ProtoEntity):
    before          = Field('int32',	1)
    after           = Field('int32',	2)
    rewards         = Field(RewardData,	3, repeated=True)
    swapmaxrank_info = Field(SwapmaxrankInfo,	4, required=False)

class RedRecvRequest(ProtoEntity):
    red             = Field('string',	1)

class ClimbTowerFloor(ProtoEntity):
    floor           = Field('int32',	1)
    target          = Field(TargetDetailResponse,	2)
    is_accredit     = Field('bool',	3, default=False)
    limit           = Field('int32',	4)
    description     = Field('string',	5)
    tip_type        = Field('int32',	6, required=False)
    tip_cost        = Field('int32',	7, required=False)
    accredit_max_count = Field('int32',	8, required=False)
    accredit_count  = Field('int32',	9, required=False)

class ClimbTowerInfoResponse(ProtoEntity):
    floors          = Field(ClimbTowerFloor,	1, repeated=True)

class MineCollectRequest(ProtoEntity):
    type            = Field('int32',	1)

class RequestPvpRewards(ProtoEntity):
    # enum PvpRewardPanelType
    Rank=1
    BP=2
    type            = Field('enum',	1)

class LootListResponse(ProtoEntity):
    targets         = Field(LootTarget,	1, repeated=True)

class ResponsePvpRewards(ProtoEntity):
    items           = Field(PvpReward,	1, repeated=True)

class PvpEndFightRequest(ProtoEntity):
    fight           = Field(Fight,	1, required=False)
    verify_code     = Field('string',	2, required=False)
    targetID        = Field('int32',	3, required=False)
    revenge         = Field('bool',	4, required=False)

class ClimbTowerHistoryResponse(ProtoEntity):
    fight           = Field(PvpEndFightRequest,	1)

class DailyInfoResponse(ProtoEntity):
    targets         = Field(TargetDetailResponse,	1, repeated=True)
    registers       = Field('int32',	2)

class SwapTargetRequest(ProtoEntity):
    targetID        = Field('int32',	1)

class RequestPvpRank(ProtoEntity):
    # enum PvpRankPanelType
    All=1
    Self=2
    Last=3
    Top=4
    type            = Field('enum',	1)
    index           = Field('sint32',	2, required=False, default=0)

class SwapStartChallengeRequest(ProtoEntity):
    targetID        = Field('int32',	1)
    swaprank        = Field('int32',	2)

class RobGetCurrProducts(ProtoEntity):
    curr            = Field('int32',	1)

class UproarTargetsThumbItem(ProtoEntity):
    prototypeID     = Field('int32',	1)
    chest           = Field(UproarOpenChestResponse,	2)
    floor           = Field('int64',	3)
    name            = Field('string',	4, required=False)
    pet             = Field(PetInfo,	5, required=False)

class UproarTargetsThumb(ProtoEntity):
    items           = Field(UproarTargetsThumbItem,	1, repeated=True)

class ClimbTowerAccreditRequest(ProtoEntity):
    lineup          = Field(Lineup,	1)
    force           = Field('bool',	2, required=False, default=False)

# file: task.proto
class NodeReward(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    index           = Field('int32',	4)

class TaskListRequest(ProtoEntity):
    type            = Field('int32',	1)
    subtype         = Field('int32',	2, default=0)

class TaskRecvRewardRequest(ProtoEntity):
    ID              = Field('int32',	1)
    guide_type      = Field('string',	2, required=False)

class Task(ProtoEntity):
    # enum TaskState
    Track=1
    Done=2
    End=3
    ID              = Field('int32',	1)
    title           = Field('string',	2)
    desc            = Field('string',	3)
    goal            = Field('int32',	4)
    plan            = Field('int32',	5)
    state           = Field('enum',	6)
    arg             = Field('int32',	7)
    rewards         = Field('string',	8)
    order           = Field('int32',	9)
    transmit        = Field('string',	10)
    groupID         = Field('int32',	11)
    day             = Field('int32',	12, required=False)
    tab_desc        = Field('string',	13, required=False)

class TaskList(ProtoEntity):
    tasks           = Field(Task,	1, repeated=True)
    current         = Field('int32',	2, required=False)
    remain          = Field('int32',	3, required=False)
    faction_task    = Field(Task,	4, required=False)
    trigger_tasks   = Field(Task,	5, repeated=True)

class DlcCampaignInfo(ProtoEntity):
    count           = Field('int32',	1)
    total           = Field('int32',	2)
    task            = Field(Task,	3)
    nodes           = Field(NodeReward,	4, repeated=True)
    cd              = Field('int32',	5)
    campaign_cd     = Field('int32',	6)
    cost            = Field('int32',	7)

class TaskRecvRewardResponse(ProtoEntity):
    next            = Field(Task,	2, required=False)
    campaign        = Field(DlcCampaignInfo,	3, required=False)

class TaskSignUpRequest(ProtoEntity):
    patch           = Field('bool',	1)

# file: explore.proto
class EndTreasure(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    gain_chest      = Field('bool',	2, required=False)
    verify_code     = Field('string',	3, required=False)
    fight           = Field(Fight,	4, required=False)
    kill_monster    = Field('bool',	5, required=False)

class DlcTargetDetailRequest(ProtoEntity):
    fbID            = Field('int32',	1)

class TreasureGrid(ProtoEntity):
    # enum TreasureGridType
    TreasureGridTypeEmpty=0
    TreasureGridTypeChest=1
    TreasureGridTypeMonster=2
    TreasureGridTypeBuff=3
    TreasureGridTypeReward=4
    TreasureGridTypeStone=5
    TreasureGridTypePlayer=6
    type            = Field('enum',	1)
    chest           = Field('int32',	2, required=False)
    monster         = Field('int32',	3, required=False)
    buff            = Field('int32',	4, required=False)
    reward          = Field(RewardData,	5, required=False)

class DlcStarPacksInfoRequest(ProtoEntity):
    dlcID           = Field('int32',	1)

class EndTap(ProtoEntity):
    count           = Field('int32',	1)

class TriggerChestRecvRequest(ProtoEntity):
    is_double       = Field('bool',	1)

class TriggerChestsRecv(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    is_best         = Field('bool',	2)

class SaveTap(ProtoEntity):
    count           = Field('int32',	1)

class DlcDispatchInfoRequest(ProtoEntity):
    fbID            = Field('int32',	1)

class TriggerChestsInfo(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    more_cost       = Field('int32',	2)

class DlcDispatchEnd(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class VisitRewardItem(ProtoEntity):
    pious           = Field('int32',	1)
    rewards         = Field(RewardData,	2, repeated=True)

class VisitRewardResponse(ProtoEntity):
    items           = Field(VisitRewardItem,	1, repeated=True)

class DlcHelperListRequest(ProtoEntity):
    social          = Field('int32',	1)

class TriggerTaskInfo(ProtoEntity):
    task_name       = Field('string',	1)

class MazeCaseResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class DlcTaskDoneRequest(ProtoEntity):
    taskID          = Field('int32',	1)

class MazePoolResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class DlcSceneListRequest(ProtoEntity):
    dlcID           = Field('int32',	1)

class DlcDispatchInfo(ProtoEntity):
    pets            = Field('int32',	1, repeated=True)
    cd              = Field('int32',	2)

class Light(ProtoEntity):
    type            = Field('int32',	1)
    scores          = Field('int32',	2)
    max_scores      = Field('int32',	3)

class MazeStepRequest(ProtoEntity):
    onekey          = Field('bool',	1, required=False)

class TriggerChestInfo(ProtoEntity):
    double_cost     = Field('int32',	1)

class DlcDispatchRequest(ProtoEntity):
    fbID            = Field('int32',	1)
    pets            = Field('int32',	2, repeated=True)

class DlcFb(ProtoEntity):
    fbID            = Field('int32',	1)
    cleared         = Field('bool',	2)
    subs            = Field('DlcFb',	3, repeated=True)
    dispatch_cd     = Field('int32',	4, required=False)
    dispatching     = Field('bool',	5, required=False)
    isNew           = Field('bool',	6, required=False)

class DlcFbList(ProtoEntity):
    fb              = Field(DlcFb,	1)
    boss            = Field(DlcFb,	2)

class MazeEvent(ProtoEntity):
    type            = Field('int32',	1)
    argv            = Field('float',	2)
    cd              = Field('int32',	3, required=False)

class MazeEvents(ProtoEntity):
    events          = Field(MazeEvent,	1, repeated=True)

class MazeStepResponse(ProtoEntity):
    events          = Field(MazeEvent,	1, repeated=True)
    rewards         = Field(RewardData,	2, repeated=True)

class TriggerFbInfo(ProtoEntity):
    fbID            = Field('int32',	1)

class DlcResetRequest(ProtoEntity):
    sceneID         = Field('int32',	1)

class MazeEventRequest(ProtoEntity):
    index           = Field('int32',	1)
    treble          = Field('bool',	2, required=False)

class EndTapResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class VisitItem(ProtoEntity):
    id              = Field('int32',	1)
    rewards         = Field(RewardData,	2, repeated=True)

class VisitList(ProtoEntity):
    items           = Field(VisitItem,	1, repeated=True)
    bg              = Field('string',	2, required=False)
    start           = Field('int32',	3, required=False)
    final           = Field('int32',	4, required=False)
    now             = Field('int32',	5, required=False)

class TriggerStoreInfo(ProtoEntity):
    show_id         = Field('int32',	1)
    fixed_price_type = Field('int32',	2)
    fixed_price     = Field('int32',	3)
    discount_price_type = Field('int32',	4)
    discount_price  = Field('int32',	5)
    rewards         = Field(RewardData,	6, repeated=True)

class EndTreasureResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    rewardsex       = Field(RewardData,	2, repeated=True)
    stars           = Field('int32',	3, required=False, default=1)
    finisheds       = Field('bool',	4, repeated=True)

class DlcStarPacksRecv(ProtoEntity):
    id              = Field('int32',	1)

class EnterTreasure(ProtoEntity):
    grids           = Field(TreasureGrid,	1, repeated=True)
    need_count      = Field('int32',	2)
    round_count     = Field('int32',	3)
    verify_code     = Field('string',	4, required=False)

class DlcHelperList(ProtoEntity):
    helpers         = Field(TargetDetailResponse,	1, repeated=True)

class TriggerChestRecv(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class VisitRequest(ProtoEntity):
    onekey          = Field('bool',	1)

class DlcDispatchEndRequest(ProtoEntity):
    fbID            = Field('int32',	1)

class DlcFbListRequest(ProtoEntity):
    sceneID         = Field('int32',	2)

class DlcInfo(ProtoEntity):
    dlcID           = Field('int32',	1)
    cd              = Field('int32',	2, required=False)
    desc            = Field('string',	3)
    name            = Field('string',	4)
    background      = Field('string',	5)
    pname           = Field('string',	6)
    open_cd         = Field('int32',	7, required=False)

class DlcList(ProtoEntity):
    infos           = Field(DlcInfo,	1, repeated=True)

class DlcSceneInfo(ProtoEntity):
    sceneID         = Field('int32',	1)
    enable          = Field('bool',	2)
    lights          = Field(Light,	3, repeated=True)

class DlcSceneList(ProtoEntity):
    infos           = Field(DlcSceneInfo,	1, repeated=True)
    campaign        = Field(DlcCampaignInfo,	5, required=False)

class StartTapResponse(ProtoEntity):
    monster         = Field('int32',	1)
    hp              = Field('int32',	2)
    size            = Field('int32',	3)
    index           = Field('int32',	4)
    hurts           = Field('int32',	5, repeated=True)
    repeats         = Field('int32',	6, repeated=True)

class OnekeyTapResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    next            = Field(StartTapResponse,	2)

class AmbitionUpRequest(ProtoEntity):
    type            = Field('int32',	1, required=False)
    index           = Field('int32',	2)
    use_gold        = Field('bool',	3, required=False)

class DlcStarPack(ProtoEntity):
    id              = Field('int32',	1)
    star            = Field('int32',	2)
    rewards         = Field(RewardData,	3, repeated=True)

class DlcStarPacksInfo(ProtoEntity):
    packs           = Field(DlcStarPack,	1, repeated=True)
    rank            = Field('int32',	2)

class VisitResponse(ProtoEntity):
    ids             = Field('int32',	1, repeated=True)
    rewards         = Field(RewardData,	2, repeated=True)

# file: faction.proto
# enum FactionApplyMode
Check=1
Free=2
Deny=3
# enum FactionStrengthenType
hp=1
at=2
ct=3
df=4
class CityEvent(ProtoEntity):
    type            = Field('int32',	1)
    argv            = Field('int32',	2)

class CancelApplyFaction(ProtoEntity):
    factionID       = Field('int32',	1)

class CityContendFinalFightRequest(ProtoEntity):
    verify_code     = Field('string',	1)
    fight           = Field(Fight,	2, required=False)

class UnlockMallProduct(ProtoEntity):
    pos             = Field('int32',	1)

class InviteMember(ProtoEntity):
    name            = Field('string',	1)

class AlterNoticeFaction(ProtoEntity):
    notice          = Field('string',	1)

class ThroneMember(ProtoEntity):
    entityID        = Field('int32',	1)

class FactionDonateResponse(ProtoEntity):
    totalfp         = Field('int32',	1)

class CityContendStartFightResponse(ProtoEntity):
    verify_code     = Field('string',	1)
    target          = Field(TargetDetailResponse,	2)

class AlterNameFaction(ProtoEntity):
    name            = Field('string',	1)

class CityDungeonCurrentInfo(ProtoEntity):
    cleaned_dungeons = Field('int32',	1, repeated=True)
    top             = Field('int32',	2)
    top_count       = Field('int32',	3)

class RecvLevelReward(ProtoEntity):
    level           = Field('int32',	1)

class CityDungeonEndPanel(ProtoEntity):
    top_faction_name = Field('string',	1)
    faction_rank    = Field('int32',	2)
    faction_rewards = Field(RewardData,	3, repeated=True)
    self_rewards    = Field(RewardData,	4, repeated=True)

class RequestMemberDetail(ProtoEntity):
    entityID        = Field('int32',	1)

class FactionInfo(ProtoEntity):
    factionID       = Field('int32',	1)
    name            = Field('string',	2)
    level           = Field('int32',	3)
    totalfp         = Field('int32',	4)
    rank            = Field('int32',	5)
    mcount          = Field('int32',	6, required=False)
    acount          = Field('int32',	7, required=False)
    todayfp         = Field('int32',	8, required=False)
    mode            = Field('enum',	9, required=False)
    prototypeID     = Field('int32',	10, required=False)
    leader          = Field('string',	11, required=False)
    createtime      = Field('int32',	12, required=False)
    notice          = Field('string',	13, required=False)
    strengthen_hp_level = Field('int32',	14, required=False)
    strengthen_at_level = Field('int32',	15, required=False)
    strengthen_ct_level = Field('int32',	16, required=False)
    strengthen_df_level = Field('int32',	17, required=False)
    can_strengthen  = Field('bool',	18, required=False)
    leaderID        = Field('int32',	19, required=False)
    applied         = Field('bool',	20, required=False)

class FactionInfos(ProtoEntity):
    infos           = Field(FactionInfo,	1, repeated=True)
    hasnext         = Field('bool',	2, required=False, default=False)

class FactionReward(ProtoEntity):
    title           = Field('string',	1)
    rewards         = Field(RewardData,	2, repeated=True)

class FactionRewards(ProtoEntity):
    items           = Field(FactionReward,	1, repeated=True)

class SearchFaction(ProtoEntity):
    factionID       = Field('int32',	1, required=False)
    name            = Field('string',	2, required=False)

class KickMember(ProtoEntity):
    entityID        = Field('int32',	1)

class ApplyFaction(ProtoEntity):
    factionID       = Field('int32',	1)

class AcceptInvite(ProtoEntity):
    factionID       = Field('int32',	1)
    isaccept        = Field('bool',	2)

class FactionResearchOrLearn(ProtoEntity):
    type            = Field('enum',	1)

class CityDungeonInfo(ProtoEntity):
    top_factionID   = Field('int32',	1, required=False)
    top_faction_name = Field('string',	2, required=False)
    top_faction_leader_name = Field('string',	3, required=False)

class CityTreasureRecv(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class RequestFactionRankList(ProtoEntity):
    # enum FactionRankType
    All=1
    Self=2
    index           = Field('sint32',	1)
    type            = Field('enum',	2)

class LevelReward(ProtoEntity):
    level           = Field('int32',	1)

class CityDungeonFinalFightRequest(ProtoEntity):
    verify_code     = Field('string',	1)
    fight           = Field(Fight,	2, required=False)

class DonateInfo(ProtoEntity):
    gold            = Field('int32',	1)
    gold2point      = Field('int32',	2)
    money           = Field('int32',	3)
    money2point     = Field('int32',	4)
    point           = Field('int32',	5)
    point2fp        = Field('int32',	6)

class CityDungeonFinalFightResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class CityContendDropEventResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class MemberInfos(ProtoEntity):
    members         = Field(TargetDetailResponse,	1, repeated=True)

class FactionStrengthen(ProtoEntity):
    # enum FactionStrengthenType
    hp=1
    at=2
    ct=3
    df=4
    type            = Field('enum',	1)
    cost            = Field('int32',	2)

class CityContendEndPanel(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    count           = Field('int32',	2)
    self_treasure   = Field('int32',	3)
    faction_treasure = Field('int32',	4, required=False)

class CityDungeonMonster(ProtoEntity):
    pos             = Field('int32',	1)
    prototypeID     = Field('int32',	2)
    restHP          = Field('int32',	3, required=False)

class CityDungeonMonsterGroup(ProtoEntity):
    id              = Field('int32',	1)
    monster_lv      = Field('int32',	2)
    monster_skill_lv = Field('int32',	3)
    monster_star    = Field('int32',	4)
    monsters        = Field(CityDungeonMonster,	5, repeated=True)

class CityDungeonStartFightResponse(ProtoEntity):
    mg              = Field(CityDungeonMonsterGroup,	1)
    verify_code     = Field('string',	2)

class AlterModeFactionRequest(ProtoEntity):
    mode            = Field('enum',	1)

class CityRanking(ProtoEntity):
    name            = Field('string',	1)
    name2           = Field('string',	2)
    score           = Field('int32',	3)
    level           = Field('int32',	4)
    score2          = Field('int32',	5, required=False)

class CityContendPanel(ProtoEntity):
    faction_rank    = Field('int32',	1, required=False)
    self_rank       = Field('int32',	2, required=False)
    faction_ranking = Field(CityRanking,	3, repeated=True)
    self_ranking    = Field(CityRanking,	4, repeated=True)
    reds            = Field(RedInfo,	5, repeated=True)
    rewards         = Field(RewardData,	6, repeated=True)
    events          = Field(CityEvent,	7, repeated=True)
    faction_treasure = Field('int32',	8, required=False)

class CityChest(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class ReviewMember(ProtoEntity):
    entityID        = Field('int32',	1)
    isallow         = Field('bool',	2)

class CityDungeonProgress(ProtoEntity):
    level           = Field('int32',	1)

class FactionDonate(ProtoEntity):
    gold            = Field('int32',	1)

class LevelRewardResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    level           = Field('int32',	2)
    can_recv        = Field('bool',	3)

class CityContendFinalFightResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    treasure_rewards = Field(RewardData,	2, repeated=True)
    treasure_count  = Field('int32',	3)

class CityDungeonTopMemberInfo(ProtoEntity):
    name            = Field('string',	1)
    prototypeID     = Field('int32',	2)
    borderID        = Field('int32',	3)
    kill_count      = Field('int32',	4)
    petID           = Field('int32',	5)
    pet_step        = Field('int32',	6)

class CityDungeonPanel(ProtoEntity):
    faction_rank    = Field('int32',	1)
    self_rank       = Field('int32',	2)
    faction_ranking = Field(CityRanking,	3, repeated=True)
    self_ranking    = Field(CityRanking,	4, repeated=True)
    reds            = Field(RedInfo,	5, repeated=True)
    current_info    = Field(CityDungeonCurrentInfo,	6)
    top_member_info = Field(CityDungeonTopMemberInfo,	7)

class AlterModeFaction(ProtoEntity):
    mode            = Field('enum',	1)

# file: mall.proto
class PetPaltSuccessResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

class MallInfoRequest(ProtoEntity):
    type            = Field('int32',	1)
    refresh         = Field('bool',	2, required=False)

class Product(ProtoEntity):
    ID              = Field('int32',	1)
    product_type    = Field('int32',	2)
    productID       = Field('int32',	3)
    product_amount  = Field('int32',	4)
    item_type       = Field('int32',	5)
    itemID          = Field('int32',	6)
    price           = Field('int32',	7)
    limit           = Field('int32',	8)
    remain          = Field('int32',	9)
    count           = Field('int32',	10)
    unlock_cost     = Field('int32',	11, required=False)
    locked          = Field('bool',	12, required=False)
    cd              = Field('int32',	13, required=False)
    pos             = Field('int32',	14, required=False)

class LotteryRequest(ProtoEntity):
    type            = Field('int32',	1)
    count           = Field('int32',	2, required=False)
    guide_type      = Field('string',	3, required=False)

class SparRequest(ProtoEntity):
    ID              = Field('int32',	1)
    onekey          = Field('bool',	2)

class MallOpen(ProtoEntity):
    type            = Field('int32',	1)

class SparItem(ProtoEntity):
    ID              = Field('int32',	1)
    itemID          = Field('int32',	2)
    money           = Field('int32',	3)
    show            = Field('int32',	4)
    onekeycount     = Field('int32',	5)
    tips            = Field('string',	6)

class LotteryResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    type            = Field('int32',	2)
    hot_rewards     = Field(RewardData,	3, repeated=True)

class LotteryItem(ProtoEntity):
    type            = Field('int32',	1)
    cost            = Field('int32',	2)

class LotteryInfo(ProtoEntity):
    items           = Field(LotteryItem,	1, repeated=True)
    notice          = Field('string',	2)

class SparInfo(ProtoEntity):
    items           = Field(SparItem,	1, repeated=True)

class BuySPRequest(ProtoEntity):
    usegold         = Field('bool',	1)

class MallBuyProduct(ProtoEntity):
    ID              = Field('int32',	1)

class MatInfo(ProtoEntity):
    id              = Field('int32',	1)
    count           = Field('int32',	2)

class RefiningRequest(ProtoEntity):
    pet_ids         = Field('int32',	1, repeated=True)
    equip_ids       = Field('int32',	2, repeated=True)
    guide_type      = Field('string',	3, required=False)
    materials       = Field(MatInfo,	4, repeated=True)

class HotPets(ProtoEntity):
    pet             = Field(RewardData,	1)
    superpet        = Field('bool',	2, required=False)

class PetPaltListResponse(ProtoEntity):
    hotpets         = Field(HotPets,	1, repeated=True)
    gold            = Field('int32',	2)
    cdtime          = Field('int32',	3, required=False)

class ResolveGoldMsgResponse(ProtoEntity):
    time            = Field('int32',	1)
    golden          = Field('int32',	2, required=False)
    silver          = Field('int32',	3, required=False)
    maxtime         = Field('int32',	4)

class MallInfoResponse(ProtoEntity):
    products        = Field(Product,	1, repeated=True)
    time            = Field('int32',	2, required=False)
    cost            = Field('int32',	3, required=False)
    cost_type       = Field('int32',	4, required=False)
    can_refresh_times = Field('int32',	5, required=False)
    used_refresh_times = Field('int32',	6, required=False)
    cd              = Field('int32',	7, required=False)

class SparResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    item            = Field(SparItem,	2)

class RefiningResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)

# file: scene.proto
class RetryFbResponse(ProtoEntity):
    success         = Field('bool',	1)

class RefreshFbRequest(ProtoEntity):
    fbID            = Field('int32',	1)

class MonsterDrop(ProtoEntity):
    index           = Field('int32',	1)
    layer           = Field('int32',	2)
    must            = Field(RewardData,	3, repeated=True)
    maybe           = Field(RewardData,	4, repeated=True)

class EnterFbRequest(ProtoEntity):
    fbID            = Field('int32',	1)
    usegold         = Field('bool',	2, required=False)
    dlc_helperID    = Field('int32',	3, required=False)
    pets            = Field('int32',	4, repeated=True)
    maze_event_index = Field('int32',	5, required=False)

class BestClearanceRequest(ProtoEntity):
    fbID            = Field('int32',	1)

class BestClearance(ProtoEntity):
    entityID        = Field('int32',	1)
    level           = Field('int32',	2)
    name            = Field('string',	3)
    time            = Field('int32',	4)
    fight           = Field(Fight,	5)
    score           = Field('int32',	6)

class Actor(ProtoEntity):
    entityID        = Field('int32',	1, required=False)
    prototypeID     = Field('int32',	2)
    level           = Field('int32',	3)
    pos             = Field('int32',	4)

class Rusher(ProtoEntity):
    prototypeID     = Field('int32',	1)
    layer           = Field('int32',	2)
    index           = Field('int32',	3)
    camp            = Field('int32',	4)

class FbInfo(ProtoEntity):
    fbID            = Field('int32',	1)
    isNew           = Field('bool',	2, default=False)
    count           = Field('int32',	3)
    need_clear      = Field('int32',	4, required=False)
    cost_count      = Field('int32',	5, required=False)
    cost            = Field('int32',	6, required=False)
    refresh_count   = Field('int32',	7, required=False)
    refresh_cost    = Field('int32',	8, required=False)
    scores          = Field('int32',	9, required=False)
    openlv          = Field('int32',	10, required=False, default=0)

class SceneInfo(ProtoEntity):
    sceneID         = Field('int32',	1)
    desc            = Field('string',	2, required=False)
    cycle           = Field('int32',	3, required=False)
    opendays        = Field('string',	4, required=False)
    count           = Field('sint32',	5, required=False)
    mark            = Field('string',	6, required=False)
    openlv          = Field('int32',	7, required=False, default=0)

class SceneInfos(ProtoEntity):
    fbs             = Field(FbInfo,	1, repeated=True)
    scenes          = Field(SceneInfo,	2, repeated=True)
    type            = Field('int32',	3)

class EndFbResponse(ProtoEntity):
    curFbInfo       = Field(FbInfo,	1)
    newFbInfos      = Field(FbInfo,	2, repeated=True)
    isFirst         = Field('bool',	3, required=False, default=False)
    time            = Field('int32',	5, required=False)
    nextID          = Field('int32',	6, required=False)
    curSceneInfo    = Field(SceneInfo,	7, required=False)
    newSceneInfo    = Field(SceneInfo,	8, required=False)
    openedFriendfb  = Field('bool',	9, required=False)
    stars           = Field('int32',	10, required=False, default=1)
    goldenMall      = Field('bool',	11, required=False)
    silverMall      = Field('bool',	12, required=False)
    event_type      = Field('int32',	13, required=False)

class BestClearanceResponse(ProtoEntity):
    info            = Field(BestClearance,	1, required=False)

class CleanFbRspStruct(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    curFbInfo       = Field(FbInfo,	2)
    add_pets        = Field('int32',	3, repeated=True)

class CleanFbRequest(ProtoEntity):
    fbID            = Field('int32',	1)
    cleantime       = Field('int32',	2)
    usegold         = Field('bool',	3, required=False)
    guide_type      = Field('string',	4, required=False)

class EnterFbResponse(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    drops           = Field(MonsterDrop,	2, repeated=True)
    replaces        = Field('int32',	3, repeated=True)
    rushers         = Field(Rusher,	4, repeated=True)
    first           = Field(RewardData,	5, repeated=True)
    buffid          = Field('int32',	6, required=False)
    buffpose        = Field('int32',	7, required=False)
    verify_code     = Field('string',	8, required=False)
    is_first        = Field('bool',	9, required=False)

class CleanFbResponse(ProtoEntity):
    cleanfbresult   = Field(CleanFbRspStruct,	1, repeated=True)
    time            = Field('int32',	5, required=False)
    openedFriendfb  = Field('bool',	6, required=False)
    goldenMall      = Field('bool',	7, required=False)
    silverMall      = Field('bool',	8, required=False)
    event_type      = Field('int32',	9, required=False)

class EndFbRequest(ProtoEntity):
    fbID            = Field('int32',	1)
    rewards         = Field(RewardData,	2, repeated=True)
    guide_type      = Field('string',	5, required=False)
    fight           = Field(Fight,	6)
    verify_code     = Field('string',	7, required=False)

class RefreshFbResponse(ProtoEntity):
    fbInfo          = Field(FbInfo,	1)

# file: group.proto
class GroupInvite(ProtoEntity):
    entityID        = Field('int32',	1)

class GroupDamageRewardRequest(ProtoEntity):
    sceneID         = Field('int32',	1, required=False)

class GroupMemberRankingRequest(ProtoEntity):
    sceneID         = Field('int32',	1, required=False)

class GroupInfoRequest(ProtoEntity):
    groupID         = Field('int32',	1, required=False)

class GroupDeny(ProtoEntity):
    entityID        = Field('int32',	1)

class GveFightResponse(ProtoEntity):
    hp              = Field('int32',	1)
    maxhp           = Field('int32',	2)
    verify_code     = Field('string',	3, required=False)

class GveScene(ProtoEntity):
    sceneID         = Field('int32',	1)
    desc            = Field('string',	2)
    rewards         = Field('string',	3)
    name            = Field('string',	4)
    banner          = Field('string',	5)
    background      = Field('string',	6)
    unitsid         = Field('int32',	7)

class GveFightEndResponse(ProtoEntity):
    error_code      = Field('int32',	1, required=False)

class GveSceneList(ProtoEntity):
    scenes          = Field(GveScene,	1, repeated=True)

class GroupRankingRewardItem(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    start           = Field('int32',	2)
    final           = Field('int32',	3)

class GroupRankingRequest(ProtoEntity):
    sceneID         = Field('int32',	1, required=False)

class GroupRankingRewardRequest(ProtoEntity):
    sceneID         = Field('int32',	1, required=False)

class GroupKick(ProtoEntity):
    entityID        = Field('int32',	1)

class GroupRankingMember(ProtoEntity):
    entityID        = Field('int32',	1)
    prototypeID     = Field('int32',	2)

class GveEntity(ProtoEntity):
    # enum GveEntityState
    GveEntityStateLeave=0
    GveEntityStateNormal=1
    GveEntityStateFight=2
    GveEntityStateDead=3
    GveEntityStateReborn=4
    GveEntityStateQuit=5
    GveEntityStateJoin=6
    id              = Field('int32',	1)
    index           = Field('int32',	2)
    state           = Field('enum',	3, required=False)
    prototypeID     = Field('int32',	4, required=False)
    target          = Field('int32',	5, required=False)
    name            = Field('string',	6, required=False)
    hp              = Field('int32',	7, required=False)
    maxhp           = Field('int32',	8, required=False)

class GveJoinResponse(ProtoEntity):
    sceneID         = Field('int32',	1)
    entities        = Field(GveEntity,	2, repeated=True)
    activateds      = Field('int32',	3, repeated=True)
    is_end          = Field('bool',	4, required=False)

class GroupRankingReward(ProtoEntity):
    damage          = Field('int32',	1)
    rank            = Field('int32',	2, required=False)
    maxdamage       = Field('int32',	3)
    items           = Field(GroupRankingRewardItem,	4, repeated=True)

class GroupRankingItem(ProtoEntity):
    groupID         = Field('int32',	1)
    regionID        = Field('int32',	2)
    region          = Field('string',	3)
    score           = Field('int32',	4)
    name            = Field('string',	5)
    members         = Field(GroupRankingMember,	6, repeated=True)
    rank            = Field('int32',	7, required=False)

class GroupRanking(ProtoEntity):
    items           = Field(GroupRankingItem,	1, repeated=True)
    self            = Field(GroupRankingItem,	2, required=False)

class GroupInfo(ProtoEntity):
    groupID         = Field('int32',	1)
    name            = Field('string',	2)
    intimate        = Field('int32',	3)
    membercount     = Field('int32',	4)
    members         = Field(TargetDetailResponse,	5, repeated=True)
    leaderID        = Field('int32',	6)

class GroupInfos(ProtoEntity):
    infos           = Field(GroupInfo,	1, repeated=True)

class GveStartResponse(ProtoEntity):
    entities        = Field(GveEntity,	1, repeated=True)
    sceneID         = Field('int32',	2)
    rest            = Field('int32',	3)

class GveFight(ProtoEntity):
    fbID            = Field('int32',	1)

class GroupMemberRankingItem(ProtoEntity):
    entityID        = Field('int32',	1)
    regionID        = Field('int32',	2)
    region          = Field('string',	3)
    score           = Field('int32',	4)
    name            = Field('string',	5)
    prototypeID     = Field('int32',	6)
    rank            = Field('int32',	7, required=False)

class GroupMemberRanking(ProtoEntity):
    items           = Field(GroupMemberRankingItem,	1, repeated=True)
    self            = Field(GroupMemberRankingItem,	2, required=False)

class GveFightEnd(ProtoEntity):
    fight           = Field(Fight,	1)
    verify_code     = Field('string',	2, required=False)

class GroupApplyList(ProtoEntity):
    members         = Field(TargetDetailResponse,	1, repeated=True)

class GroupAllow(ProtoEntity):
    entityID        = Field('int32',	1)

class GroupAlterName(ProtoEntity):
    name            = Field('string',	1)

class GroupCreate(ProtoEntity):
    name            = Field('string',	1)

class GveEndPanelMember(ProtoEntity):
    entityID        = Field('int32',	1)
    name            = Field('string',	2)
    prototypeID     = Field('int32',	3)
    damage          = Field('int32',	4)
    addition        = Field('int32',	5)
    score           = Field('int32',	6)

class GveEndPanel(ProtoEntity):
    damage          = Field('int32',	1)
    rank            = Field('int32',	2)
    percent         = Field('int32',	3)
    maxdamage       = Field('int32',	4)
    rewards         = Field('string',	5)
    members         = Field(GveEndPanelMember,	6, repeated=True)

class GroupApply(ProtoEntity):
    groupID         = Field('int32',	1)

class GroupMemberDetailAcrossRegion(ProtoEntity):
    regionID        = Field('int32',	1)
    entityID        = Field('int32',	2)

class GroupDamageRewardItem(ProtoEntity):
    damage          = Field('int32',	1)
    rewards         = Field(RewardData,	2, repeated=True)

class GroupDamageReward(ProtoEntity):
    items           = Field(GroupDamageRewardItem,	1, repeated=True)

# file: fightArchive.proto
class requestResponseData(ProtoEntity):
    request_rsp1    = Field(EnterFriendfbResponse,	1, required=False)
    request_rsp2    = Field(EnterFbResponse,	2, required=False)
    request_rsp3    = Field(TargetDetailResponse,	3, required=False)
    request_rsp4    = Field(GveFightResponse,	4, required=False)
    request_rsp5    = Field(SwapStartChallengeResponse,	5, required=False)
    request_rsp6    = Field(DailyStartFightResponse,	6, required=False)
    request_rsp7    = Field(CityDungeonStartFightResponse,	7, required=False)
    request_rsp8    = Field(CityContendStartFightResponse,	8, required=False)

class itemBuffInfo(ProtoEntity):
    last_round      = Field('int32',	1)
    kind            = Field('int32',	2)
    val             = Field('int32',	3)
    type            = Field('string',	4)

class itemBuffState(ProtoEntity):
    obj_info        = Field(itemBuffInfo,	1)
    remain_round    = Field('int32',	2)
    param           = Field('float',	3)
    fight_state     = Field('string',	4)

class sceneItemBuffState(ProtoEntity):
    pos_index       = Field('int32',	1)
    obj_info        = Field(itemBuffInfo,	2)

class buffState(ProtoEntity):
    buff_debuff_id  = Field('int32',	1, required=False)
    src_entity_id   = Field('int32',	2)
    remain_round    = Field('int32',	3)
    start_round     = Field('int32',	4)
    effect_attr     = Field('int32',	5)
    effect_param    = Field('float',	6)
    extend_param    = Field('float',	7)
    fight_state     = Field('string',	8)
    first_check     = Field('bool',	9)
    temp_se_info    = Field(se_info,	10)
    skill_level     = Field('int32',	11)

class fighterState(ProtoEntity):
    entity_id       = Field('int32',	1)
    random_index    = Field('int32',	2)
    cur_pos_index   = Field('int32',	3)
    cur_hp          = Field('int32',	4)
    total_damage    = Field('int32',	5)
    total_round     = Field('int32',	6)
    used_skill_ids  = Field('int32',	7, repeated=True)
    buff_debuff_state = Field(buffState,	8, repeated=True)
    item_buff_state = Field(itemBuffState,	10, repeated=True)
    next_buff_debuff_id = Field('int32',	11)
    origin_pos_index = Field('int32',	12)

class fightArchive(ProtoEntity):
    is_valid        = Field('bool',	1)
    random_index    = Field('int32',	2)
    replay          = Field(fightReplay,	3)
    fighter_state   = Field(fighterState,	4, repeated=True)
    area_index      = Field('int32',	5)
    next_fight_state = Field('string',	6)
    cur_round       = Field('int32',	7)
    player_total_round = Field('int32',	8)
    enemy_total_round = Field('int32',	9)
    player_total_damage = Field('int32',	10)
    enemy_total_damage = Field('int32',	11)
    gain_count      = Field('int32',	12)
    item_buff_state = Field(sceneItemBuffState,	13, repeated=True)
    request_rsp     = Field(requestResponseData,	14)
    extern_data     = Field('string',	15)
    init_rsp        = Field('bool',	16)
    all_stone_index = Field('int32',	17, repeated=True)
    start_time      = Field('int32',	18, required=False)
    plot_play       = Field('bool',	19)

# file: gem.proto
class GemRefineRequest(ProtoEntity):
    index           = Field('int32',	1)

class GemComposeRequest(ProtoEntity):
    gemID           = Field('int32',	1)
    all             = Field('bool',	2, default=False)

class Gem(ProtoEntity):
    gemID           = Field('int32',	1)
    count           = Field('int32',	2)

class Gems(ProtoEntity):
    gems            = Field(Gem,	1, repeated=True)

# file: guide.proto
class guideResponse(ProtoEntity):
    guide_types     = Field('string',	1, repeated=True)

class guideEnd(ProtoEntity):
    guide_type      = Field('string',	1)

# file: incrementalConfig.proto
class field_info(ProtoEntity):
    key_name        = Field('string',	1)
    value_type      = Field('int32',	2)
    value           = Field('string',	3)

class config_item_info(ProtoEntity):
    id              = Field('int32',	1)
    diff_fields     = Field(field_info,	2, repeated=True)
    rm_fields       = Field('string',	3, repeated=True)

class config_file_info(ProtoEntity):
    config_name     = Field('string',	1)
    items           = Field(config_item_info,	2, repeated=True)
    rm_items        = Field('int32',	3, repeated=True)

class incrementResponse(ProtoEntity):
    config_version  = Field('int32',	1)
    config_diff     = Field(config_file_info,	2, repeated=True)

class incrementConfigs(ProtoEntity):
    configs         = Field(incrementResponse,	1, repeated=True)

class incrementRequest(ProtoEntity):
    config_version  = Field('int32',	1)

# file: mail.proto
class ReceiveMailReward(ProtoEntity):
    mailID          = Field('int32',	1)

class MailInfo(ProtoEntity):
    mailID          = Field('int32',	1)
    title           = Field('string',	2)
    type            = Field('int32',	3)
    isread          = Field('bool',	4)
    isreceived      = Field('bool',	5, required=False)
    content         = Field('string',	6, required=False)
    addtime         = Field('int32',	7, required=False)
    rewards         = Field(RewardData,	8, repeated=True)
    cd              = Field('int32',	9, required=False)
    icon_not_read   = Field('int32',	10, required=False)
    icon_read       = Field('int32',	11, required=False)

class MailList(ProtoEntity):
    mails           = Field(MailInfo,	1, repeated=True)

class ReceiveMailRewardResponse(ProtoEntity):
    mailID          = Field('int32',	1)
    delete          = Field('bool',	2)

class ReadMailConetentResponse(ProtoEntity):
    mailID          = Field('int32',	1)
    delete          = Field('bool',	2)

class MailListRequest(ProtoEntity):
    # enum GetMailListType
    GetMailListTypeNew=1
    GetMailListTypeOld=2
    type            = Field('enum',	1)
    arg             = Field('int32',	2, default=0)

class ReadMailConetent(ProtoEntity):
    mailID          = Field('int32',	1)

# file: mat.proto
class UseMatRequest(ProtoEntity):
    matID           = Field('int32',	1)

class UseMatResponse(ProtoEntity):
    tips            = Field('string',	1, required=False)
    rewards         = Field(RewardData,	2, repeated=True)

class Mat(ProtoEntity):
    matID           = Field('int32',	1)
    count           = Field('int32',	2)

class Mats(ProtoEntity):
    mats            = Field(Mat,	1, repeated=True)

# file: netmessageid.proto
# enum NetMsgID
SEVER_NOTICE=1
TV_NOTICE=2
ERROR_REPORT=3
ILLEGAL_OPERATION=11
ENTER_SCENE=30
NET_USER_QUIT=31
CHANGE_SCENE=32
SYNC_PROPERTY=72
MULTI_SYNC_PROPERTY=73
NET_USER_MOVE_TO=79
GUIDE_OPEN=80
GUIDE_CLOSE=81
BUG_REPORT=82
CHECK_UPGRADE=83
DOWNLOAD_FILE=84
HEART_BEAT=85
CHECK_LAUCH=86
CHECK_CONFIG=88
REGION_LIST=89
SDK_CHECK_LOGIN=90
SDK_PAY_ENABLE=91
SDK_PAY_RESULT=92
SDK_PAY_START=93
SDK_MM_QUERY_PAY=94
TEST_PAY=95
CLEAN_USER_LASTSERVER=99
LOGIN=100
LOGIN_KEY=104
LOGIN_WORLD=101
VERIFY_LOGIN=102
SELECT_ACTOR=103
PLAYER_MOVE_TO=105
CREATE_USER=106
LOGIN_REFRESH=107
NEW_ACTOR=108
AUTO_REGISTER=109
CHANGE_PASSWORD=110
LOGIN_EXTRA=111
DELETE_ACTOR=112
CHECKREG_PLAYERNAME=113
CHOOSE_ROLE=114
ALTER_ACTOR_NAME=115
RANDOM_ACTOR_NAME=126
LJSDK_LOGIN_SUCCESS=201
LJSDK_LOGIN_FAILED=202
LJSDK_LOGOUT=203
LJSDK_EXIT_ON_GAMEEXIT=204
LJSDK_EXIT_ON_NO3RD=205
LJSDK_PAY_SUCCESS=206
LJSDK_PAY_FAIL=207
ANDROID_EDIT_TEXT=208
RECONNECT=250
SESSION_RECONNECT=251
TOAST=288
GUIDE_TYPE_SAVED=300
GUIDE_TYPE_END=301
GUIDE_FINAL_SIGNAL=302
LINEUP_LINEUPS=3000
SAVE_LINEUPS=3001
SCENE_INFOS=3010
ENTER_FB=3011
END_FB=3012
ADVANCED_FB=3013
CAMPAIGN_FB=3014
RETRY_FB=3015
REFRESH_FB=3016
BEST_CLEARANCE=3017
RESUME_SP=3020
HERO_BREED=3100
HERO_EVOLUTION=3105
HERO_SALE=3110
HERO_EXPLORE=3115
GET_PET_BOOK=3116
SAVE_PET_BOOK=3117
EXPLORE_REWARD=3118
GET_EXPLORE_INFOS=3119
START_EXPLORE=3120
FINAL_EXPLORE=3121
CHECK_EXPLORE=3122
LOTTERY_INFO=3200
LOTTERY=3201
BUY_SP=3202
EXPAND_PET_BOX=3203
RESOLVE_GOLD_MSG=3204
RESOLVE_GOLD=3205
MALL_LIST=3206
TEMP_MALL_LIST=3207
MALL_FLUSH=3208
MALL_BUY=3209
MALL_STATUS=3210
MALL_OPEN_FOREVER=3211
REFINING=3212
BUY_SKILLPOINT=3213
SPAR_INFO=3222
SPAR_REQUEST=3223
GET_LOGIN_REWARD=3300
CHECK_LOGIN_REWARD=3301
NOTICE=3320
MAIL_LIST=3400
MAIL_READ=3401
MAIL_RECV=3402
MAIL_ONEKEY_RECV=3403
SLATE_INIT=3410
SLATE_REWARD=3411
FAKE_FIGHT_LIST=3499
FAKE_START_FIGHT=3500
PVP_OPPONENT_LIST=3501
PVP_START_FIGHT=3502
PVP_FINAL_FIGHT=3503
PVP_REWARD_LIST=3504
PVP_RANK_LIST=3505
PVP_CLEAN_CD=3506
PVP_HISTORY=3507
PVP_REPLAY=3508
PVP_PLAYER_LINEUPS=3509
PVP_CLEAN_SEASON_REWARD=3510
PVP_TARGETS=3511
PVP_RESET=3512
NPC_TARGETS=3520
NPC_TARGET_DETAIL=3521
NPC_START_FIGHT=3522
NPC_END_FIGHT=3523
FACTION_INFO=3700
FACTION_CREATE=3701
FACTION_SEARCH=3702
FACTION_INVITED=3703
FACTION_RANK=3704
FACTION_REWARD=3705
FACTION_MEMBER_INFOS=3706
FACTION_APPLY_INFOS=3707
FACTION_INVITE_INFOS=3708
FACTION_APPLY=3709
FACTION_INVITE=3710
FACTION_KICK=3711
FACTION_ALTER_NAME=3712
FACTION_ALTER_MODE=3713
FACTION_ALTER_NOTICE=3714
FACTION_DISMISS=3715
FACTION_THRONE=3716
FACTION_QUIT=3717
FACTION_MEMBER_DETAIL=3718
FACTION_REVIEW=3719
FACTION_STRENGTHEN=3720
FACTION_CANCEL_APPLY=3721
FACTION_ACCEPT_INVITE=3722
FACTION_DONATE=3723
FACTION_LEVELUP=3724
FACTION_RESEARCH=3725
FACTION_LEARN=3726
FACTION_CANCEL_DISMISS=3727
FACTION_DONATE_INFO=3728
FACTION_LEVEL_REWARD=3729
FACTION_RECV_LEVEL_REWARD=3730
FACTION_ACCEPT_TASK=3731
FACTION_UNLOCK_MALL_PRODUCT=3732
PET_PATCH_SYNC=3800
PET_PATCH_CHANGE=3801
VIP_DESCRIPTION=3900
RECHARGE_LIST=3910
TASK_LIST=4000
TASK_SIGN_UP=4001
TASK_RECV_REWARD=4003
CLEANFB=4030
PET_PALTFORM_LIST=4040
PET_PALTFORM_REQ=4041
SYNC_MATS=4100
SYNC_GEMS=4101
BREAK=4110
PET_FUSION=4111
PET_SKILL_UP=4112
GIFTKEY=4200
EQUIP_INSTALL=4300
EQUIP_UNINSTALL=4301
EQUIP_STRENGTHEN=4302
EQUIP_SWAP_EQUIPS=4303
EQUIP_ADVANCE=4304
EQUIP_STRENGTHEN_ONEKEY=4305
EQUIP_ENCHANT=4306
MINE_COLLECT=4400
MINE_ROB_LIST=4401
MINE_ROB_START_FIGHT=4402
MINE_ROB_END_FIGHT=4403
MINE_ROBBED_HISTORY=4404
MINE_ROBBED_REPLAY=4405
MINE_ROB_GET_CURR_PRODUCTS=4406
MINE_ROB_DETAIL=4407
UPROAR_REFRESH_TARGETS=4500
UPROAR_OPEN_CHEST=4501
UPROAR_START_FIGHT=4502
UPROAR_END_FIGHT=4503
UPROAR_TARGET_DETAIL=4504
UPROAR_TARGETS_THUMB=4505
LOOT_TARGETS_LIST=4600
LOOT_START_FIGHT=4601
LOOT_END_FIGHT=4602
LOOT_COMPOSE=4603
LOOT_RESET_COUNT=4604
LOOT_HISTORY_LIST=4605
REWARD_CAMPAIGN_INFO=4650
GET_CACHE_MESSAGES=4700
SEND_MESSAGE=4701
RECV_MESSAGE=4702
GET_TIPS_MESSAGES=4703
VISIT_LIST=4800
VISIT_VISIT=4801
VISIT_REWARD=4802
BEG_INFO=4900
REFRESH_TREASURE=4901
ENTER_TREASURE=4902
END_TREASURE=4903
CLEAN_TREASURE_CD=4904
START_TAP=4920
END_TAP=4921
SAVE_TAP=4922
ONEKEY_TAP=4923
LEVEL_PACKS_INFO=5001
LEVEL_PACKS_RECV=5002
POWER_PACKS_INFO=5011
POWER_PACKS_RECV=5012
TOTAL_LOGIN_REWARD=5100
STAR_PACKS_INFO=5200
STAR_PACKS_RECV=5201
COMPOSE=5300
PET_PATCH_EXCHANGE=5301
FIRST_RECHARGE_INFO=5400
FIRST_RECHARGE_RECV=5401
LIST_FRIEND=5500
APPLY_FRIEND=5501
ALLOW_FRIEND=5502
DENY_FRIEND=5503
REMOVE_FRIEND=5504
LIST_APPLYS=5505
LIST_RECOMMEND=5506
GIFT_FRIEND=5507
INVITE_FRIEND_LIST=5508
INVITE_FRIEND=5509
FRIENDFB_LIST=5510
FRIENDFB_DETAIL=5511
ENTER_FRIENDFB=5512
END_FRIENDFB=5513
REBORN_FRIENDFB=5514
FRIENDFB_RANKING_REWARD=5515
LISTEN_FRIEND=5516
UNLISTEN_FRIEND=5517
CHAT_FRIEND=5518
MALL_INFO=5600
MALL_BUY_PRODUCT=5601
MALL_OPEN=5602
VIP_PACKS_INFO=5650
VIP_PACKS_BUY=5651
ITUNES_IAP_VALIDATION=5700
WISH_INFO=6000
WISH=6001
ACC_RECHARGE_INFO=6010
RECV_ACC_RECHARGE_REWARD=6011
DAILY_RECHARGE_INFO=6012
DAILY_RECHARGE_RECV=6013
FUND_INFO=6100
RECV_FUND_REWARD=6101
BUY_FUND=6102
CHECK_IN_INFO=6200
CHECK_IN=6201
RECV_MONTHLY_CARD=6205
MONTHLY_CARD_INFO=6206
TIMED_STORE_INFO=6300
TIMED_STORE_BUY=6301
TRIGGER_FB_INFO=6400
TRIGGER_CHEST_INFO=6401
TRIGGER_CHEST_RECV=6402
TRIGGER_CHESTS_INFO=6403
TRIGGER_CHESTS_RECV=6404
TRIGGER_TASK_INFO=6405
TRIGGER_STORE_INFO=6406
TRIGGER_STORE_BUY=6407
RANKING_LIST=6500
RANKING_EXTRA_INFO=6501
RANKING_CAMPAIGN_INFO=6502
RANKING_CAMPAIGN_REWARD=6503
DLC_LIST=6600
DLC_SCENE_LIST=6601
DLC_FB_LIST=6602
DLC_TARGET_DETAIL=6603
DLC_HELPER_LIST=6604
DLC_DISPATCH_INFO=6605
DLC_DISPATCH=6606
DLC_DISPATCH_END=6607
DLC_RESET=6608
DLC_STAR_PACKS_INFO=6609
DLC_STAR_PACKS_RECV=6610
DLC_TASK_DONE=6611
COUNT_DOWN_INFO=6800
COUNT_DOWN_RECV=6801
GROUP_INFO=7000
GROUP_CREATE=7001
GROUP_SEARCH=7002
GROUP_QUIT=7003
GROUP_KICK=7004
GROUP_ALLOW=7005
GROUP_INVITE=7006
GROUP_APPLY=7007
GROUP_APPLY_LIST=7008
GROUP_ALTER_NAME=7009
GROUP_DENY=7017
SYNC_GVE_ENTITY=7100
GVE_JOIN=7101
GVE_QUIT=7102
GVE_START=7103
GVE_FIGHT=7104
GVE_FIGHT_END=7105
GVE_REBORN=7106
GVE_END_PANEL=7107
GVE_GROUP_RANKING=7108
GVE_GROUP_MEMBER_DETAIL=7109
GVE_GROUP_MEMBER_RANKING=7110
GVE_GROUP_RANKING_REWARD=7111
GVE_GROUP_DAMAGE_REWARD=7112
GVE_SCENE_LIST=7113
GVE_LEAVE=7114
SWAP_INFO=8000
SWAP_TARGET_DETAIL=8001
SWAP_REFRESH_CD=8003
SWAP_REFRESH_COUNT=8004
SWAP_RANK_LIST=8005
SWAP_HISTORY=8006
SWAP_REPLAY=8007
SWAP_REWARD=8008
SWAP_START_CHALLENGE=8009
SWAP_FINAL_CHALLENGE=8010
MAZE_STEP=8100
MAZE_EVENTS=8101
MAZE_CASE_RECV=8102
MAZE_POOL_RECV=8103
CHANGE_AVATAR_OR_BORDER=8200
USE_MAT=8300
ONLINE_PACKS_INFO=8400
ONLINE_PACKS_RECV=8401
BROADCAST_HORN=8500
DAILY_INFO=9000
DAILY_TARGET_DETAIL=9001
DAILY_START_FIGHT=9002
DAILY_FINAL_FIGHT=9003
DAILY_BUY_COUNT=9004
DAILY_REWARD_LIST=9005
DAILY_RANK_LIST=9006
DAILY_HISTORY_LIST=9007
DAILY_REPLAY=9008
DAILY_RED_INFO=9009
DAILY_RED_RECV=9010
DAILY_RED_LIST=9011
DAILY_INSPIRE=9012
DAILY_PANEL=9013
DAILY_REGISTER=9014
DAILY_REBORN=9015
DAILY_END_PANEL=9016
GUIDE_REWARD_RECV=9100
GUIDE_DEFEAT_RECV=9101
AMBITION_UP=9200
SCENE_REWARD_INFO=9300
SCENE_REWARD_RECV=9301
BUY_SOUL=9400
PET_EXCHANGE_INFO=9500
PET_EXCHANGE=9501
MAT_EXCHANGE_INFO=9600
MAT_EXCHANGE=9601
CITY_DUNGEON_CURRENT_INFO=9699
CITY_DUNGEON_INFO=9700
CITY_DUNGEON_PANEL=9701
CITY_DUNGEON_START_FIGHT=9702
CITY_DUNGEON_FINAL_FIGHT=9703
CITY_DUNGEON_END_PANEL=9704
CITY_CONTEND_PANEL=9705
CITY_CONTEND_DROP_EVENT=9706
CITY_CONTEND_END_EVENT=9707
CITY_CONTEND_START_FIGHT=9708
CITY_CONTEND_FINAL_FIGHT=9709
CITY_CHEST_RECV=9710
CITY_CONTEND_END_PANEL=9711
MONTHCARD_INFO=9800
MONTHCARD_RECV=9801
PLAYER_EQUIP_STRENGTHEN=9900
CONSUME_CAMPAIGN_INFO=10000
CONSUME_CAMPAIGN_RECV=10001
LOGIN_CAMPAIGN_INFO=10100
LOGIN_CAMPAIGN_RECV=10101
EXCHANGE_CAMPAIGN_INFO=10102
EXCHANGE_CAMPAIGN_REQUEST=10103
EXCHANGE_CAMPAIGN_ITEM_RESULT=10104
REFRESH_STORE_CAMPAIGN_INFO=10105
REFRESH_STORE_CAMPAIGN_RECV=10106
ARBOR_DAY_CAMPAIGN_YYY=10107
SEED_CROP=10108
SEED_WATERING=10109
SEED_WORMING=10110
SEED_REAP=10111
SEED_CLEAN=10112
CHECK_SEED_STATE=10113
HANDSEL_CAMPAIGN_INFO=10120
HANDSEL_CAMPAIGN_SEND=10121
HANDSEL_CAMPAIGN_RANK_S=10122
HANDSEL_CAMPAIGN_RANK_F=10123
CLIMB_TOWER_INFO=10200
CLIMB_TOWER_CHESTS=10201
CLIMB_TOWER_RESET=10202
CLIMB_TOWER_START_FIGHT=10203
CLIMB_TOWER_END_FIGHT=10204
CLIMB_TOWER_HISTORY=10205
CLIMB_TOWER_HISTORY_REPLAY=10206
CLIMB_TOWER_TIP=10207
CLIMB_TOWER_ACCREDIT=10208
CLIMB_TOWER_ACCREDIT_INFO=10209
CLIMB_TOWER_OPEN_CHEST=10210
CLIMB_TOWER_SWIPE=10211
FLOWER_BOSS_CAMPAIGN_INFO=10130
FLOWER_BOSS_ENTER_FB=10131
FLOWER_BOSS_END_FB=10132
FLOWER_BOSS_REBORN=10133
GEM_COMPOSE=10300
GEM_REFINE=10301
# file: pet.proto
class ResponseHeroBreed(ProtoEntity):
    # enum BreedType
    normal=1
    super=2
    ultra=3
    targetHeroID    = Field('int32',	1)
    breedType       = Field('enum',	2)
    targetHeroLv    = Field('int32',	3)
    targetHeroExp   = Field('int32',	4)

class RequestHeroEvolution(ProtoEntity):
    targetHeroID    = Field('int32',	1)
    guide_type      = Field('string',	2, required=False)

class SkillUpRequest(ProtoEntity):
    petID           = Field('int32',	1)
    skill           = Field('int32',	2)
    count           = Field('int32',	3, default=1)

class PetBook(ProtoEntity):
    book            = Field('sint32',	1, repeated=True)

class ResponseStartExplore(ProtoEntity):
    cdTime          = Field('int32',	1)

class RequestHeroSale(ProtoEntity):
    heroIDs         = Field('int32',	1, repeated=True)

class ResponseHeroEvolution(ProtoEntity):
    costHeroIDs     = Field('int32',	1, repeated=True)

class requestHeroEvolution(ProtoEntity):
    targetHeroID    = Field('int32',	1)
    materialHeroIDs = Field('int32',	2, repeated=True)

class RequestFinalExplore(ProtoEntity):
    teamID          = Field('int32',	1)

class RequestHeroBreed(ProtoEntity):
    targetHeroID    = Field('int32',	1)
    materialHeroIDs = Field('int32',	2, repeated=True)
    guide_type      = Field('string',	3, required=False)

class Patch(ProtoEntity):
    id              = Field('int32',	1)
    need            = Field('int32',	2, required=False)
    have            = Field('int32',	3)

class ResponseFinalExplore(ProtoEntity):
    rewards         = Field(RewardData,	1, repeated=True)
    exp             = Field('int32',	2)

class RequestStartExplore(ProtoEntity):
    heroID          = Field('int32',	1)
    teamID          = Field('int32',	2)
    timeType        = Field('int32',	3)

class FusionRequest(ProtoEntity):
    pets            = Field('int32',	1, repeated=True)
    guide_type      = Field('string',	2, required=False)

class BreakRequest(ProtoEntity):
    petID           = Field('int32',	1)
    pets            = Field('int32',	2, repeated=True)
    mats            = Field('int32',	3, repeated=True)
    mats_count      = Field('int32',	4, repeated=True)
    guide_type      = Field('string',	5, required=False)

class ResponseExploreInfo(ProtoEntity):
    cdTime1         = Field('int32',	1, required=False)
    cdType1         = Field('int32',	2, required=False)
    cdTime2         = Field('int32',	3, required=False)
    cdType2         = Field('int32',	4, required=False)
    cdTime3         = Field('int32',	5, required=False)
    cdType3         = Field('int32',	6, required=False)

class BreedRequest(ProtoEntity):
    petID           = Field('int32',	1)
    count           = Field('int32',	2, required=False, default=1)
    guide_type      = Field('string',	3, required=False)

class FustionResponse(ProtoEntity):
    pet_entity_id   = Field('int32',	1)

class requestHeroBreed(ProtoEntity):
    targetHeroID    = Field('int32',	1)
    materialHeroIDs = Field('int32',	2, repeated=True)

class ResponseHeroSale(ProtoEntity):
    totalPrice      = Field('int32',	1, required=False)

class RequestChange(ProtoEntity):
    id              = Field('int32',	1)
    guide_type      = Field('string',	2, required=False)
    patchs          = Field('int32',	3, repeated=True)
    counts          = Field('int32',	4, repeated=True)

class ResponsePatchsync(ProtoEntity):
    patchs          = Field(Patch,	1, repeated=True)

# file: ranking.proto
class RankingExtraInfoRequest(ProtoEntity):
    type            = Field('string',	1)
    extra           = Field('string',	2)

class RankingListRequest(ProtoEntity):
    type            = Field('string',	1)
    from_campaign   = Field('bool',	2, required=False)
    use_backup      = Field('bool',	3, required=False)

class RankingCampaignRewardListRequest(ProtoEntity):
    day             = Field('int32',	1)

class RankingExtraInfoResponse(ProtoEntity):
    pet             = Field(PetInfo,	1, required=False)
    equip           = Field(Equiped,	2, required=False)

class RankingReward(ProtoEntity):
    title           = Field('string',	1)
    start           = Field('int32',	2, required=False)
    final           = Field('int32',	3, required=False)
    comment         = Field('string',	4, required=False)
    rewards         = Field(RewardData,	5, repeated=True)

class RankingCampaignRewardListResponse(ProtoEntity):
    items           = Field(RankingReward,	1, repeated=True)

class RankingItem(ProtoEntity):
    entityID        = Field('int32',	1, required=False)
    rank            = Field('int32',	2, required=False)
    name            = Field('string',	3, required=False)
    prototypeID     = Field('int32',	4, required=False)
    score           = Field('int32',	5, required=False)
    trend           = Field('sint32',	6, required=False)
    detail          = Field(TargetDetailResponse,	7, required=False)
    faction_count   = Field('int32',	10, required=False)
    extra           = Field('string',	11, required=False)
    faction_level   = Field('int32',	12, required=False)

class RankingList(ProtoEntity):
    self            = Field(RankingItem,	1, required=False)
    items           = Field(RankingItem,	2, repeated=True)

class RankingCampaign(ProtoEntity):
    day             = Field('int32',	1, required=False)
    start           = Field('int32',	2, required=False)
    final           = Field('int32',	3, required=False)
    ranking         = Field('string',	4, required=False)
    desc            = Field('string',	5, required=False)
    title           = Field('string',	6, required=False)
    rank            = Field('int32',	7, required=False)

class RankingCampaignList(ProtoEntity):
    now             = Field('int32',	1)
    campaigns       = Field(RankingCampaign,	2, repeated=True)

# file: role.proto
class DeleteRoleResponse(ProtoEntity):
    pass

class ChooseRoleRequest(ProtoEntity):
    roleId          = Field('int32',	1)

class LoginWorldRequest(ProtoEntity):
    userID          = Field('int32',	1)
    verify_code     = Field('string',	2)
    entityID        = Field('int32',	3, required=False)

class RandomNameRequest(ProtoEntity):
    sex             = Field('int32',	1)

class CreateRoleNameCheckRequest(ProtoEntity):
    name            = Field('string',	1)

class DeleteRoleRequest(ProtoEntity):
    password        = Field('string',	1)
    roleId          = Field('int32',	2)

class RandomNameResponse(ProtoEntity):
    names           = Field('string',	1, repeated=True)
    namefemales     = Field('string',	2, repeated=True)

class Role(ProtoEntity):
    id              = Field('int32',	1)
    name            = Field('string',	2)
    level           = Field('int32',	3)
    sex             = Field('int32',	4)
    school          = Field('int32',	5)
    resourceId      = Field('int32',	6)

class LoginWorldResponse(ProtoEntity):
    roles           = Field(Role,	1, repeated=True)
    need_rename     = Field('bool',	2, required=False)

class CreateRoleResponse(ProtoEntity):
    roleId          = Field('int32',	1)
    roles           = Field(Role,	2, repeated=True)

class CreateRoleRequest(ProtoEntity):
    name            = Field('string',	1)
    sex             = Field('int32',	2)
    school          = Field('int32',	3)
    iconID          = Field('int32',	4)

class ChooseRoleResponse(ProtoEntity):
    ip              = Field('string',	1)
    port            = Field('int32',	2)
    verify_code     = Field('string',	3)

class AlterNameRequest(ProtoEntity):
    userID          = Field('int32',	1)
    verify_code     = Field('string',	2)
    entityID        = Field('int32',	3)
    name            = Field('string',	4)

class CreateRoleNameCheckResponse(ProtoEntity):
    pass

# file: serverlist.proto
class serverinfo(ProtoEntity):
    ip              = Field('string',	1)
    port            = Field('int32',	2)
    name            = Field('string',	3)
    isnew           = Field('int32',	4)

class serverlist(ProtoEntity):
    list            = Field(serverinfo,	1, repeated=True)

# file: session.proto
class RegisterRequest(ProtoEntity):
    username        = Field('string',	1)
    password        = Field('string',	2)
    imsi            = Field('string',	3)
    tid             = Field('string',	4)
    sdkType         = Field('enum',	5, required=False)
    featureCode     = Field('string',	6, required=False)
    deviceInfo      = Field(DeviceInfo,	7, required=False)
    origin_username = Field('string',	8, required=False)
    origin_password = Field('string',	9, required=False)
    channel         = Field('string',	10, required=False)

class DownloadFileRequest(ProtoEntity):
    tag             = Field('int32',	1)
    path            = Field('string',	2)

class ErrorReport(ProtoEntity):
    traceback       = Field('string',	1)

class RoleInfo(ProtoEntity):
    entityID        = Field('int32',	1)
    name            = Field('string',	2)
    iconID          = Field('int32',	3)
    vip             = Field('int32',	4, required=False)
    level           = Field('int32',	5, required=False)
    last_region_name = Field('string',	6, required=False)
    borderID        = Field('int32',	7, required=False)

class HTTPChooseRoleRequest(ProtoEntity):
    regionID        = Field('int32',	1)
    roleID          = Field('int32',	2)

class ChangePasswordRequest(ProtoEntity):
    new_password    = Field('string',	2)
    verify_code     = Field('string',	3, required=False)

class VerifyLoginResponse(ProtoEntity):
    userID          = Field('int32',	1)

class RequestRegionList(ProtoEntity):
    sdkType         = Field('enum',	1)
    username        = Field('string',	2, required=False)
    deviceInfo      = Field(DeviceInfo,	7, required=False)

class World(ProtoEntity):
    ID              = Field('int32',	1)
    ip              = Field('string',	2)
    port            = Field('int32',	3)
    online          = Field('int32',	4)
    mode            = Field('string',	5, required=False)

class HTTPLoginResponse(ProtoEntity):
    userID          = Field('int32',	1)
    world           = Field(World,	2, required=False)
    verify_code     = Field('string',	3, required=False)
    sdk_username    = Field('string',	4, required=False)
    roles           = Field(RoleInfo,	5, repeated=True)
    extra           = Field('string',	6, required=False)

class HTTPChooseRoleResponse(ProtoEntity):
    roleID          = Field('int32',	1)
    world           = Field(World,	2)
    verify_code     = Field('string',	3)

class AutoRegisterRequest(ProtoEntity):
    sdkType         = Field('enum',	1)
    version         = Field('int32',	2, required=False)
    featureCode     = Field('string',	3, required=False)
    deviceInfo      = Field(DeviceInfo,	4, required=False)
    channel         = Field('string',	5, required=False)

class SessionReconnectResponse(ProtoEntity):
    world           = Field(World,	1)

class Region(ProtoEntity):
    # enum State
    NEW=0
    GOOD=1
    BEST=2
    BUSY=3
    FULL=4
    HALT=5
    id              = Field('int32',	1)
    name            = Field('string',	2)
    state           = Field('enum',	3, required=False)

class RegionList(ProtoEntity):
    regions         = Field(Region,	1, repeated=True)

class SessionReconnect(ProtoEntity):
    verify_code     = Field('string',	1)
    userID          = Field('int32',	2)
    roleID          = Field('int32',	3)
    regionID        = Field('int32',	4)

class Server(ProtoEntity):
    # enum State
    NEW=0
    GOOD=1
    BEST=2
    BUSY=3
    FULL=4
    HALT=5
    id              = Field('int32',	1)
    ip              = Field('string',	2)
    port            = Field('int32',	3)
    name            = Field('string',	4)
    roleCount       = Field('int32',	5)
    state           = Field('enum',	6)
    online          = Field('int32',	7)
    msg             = Field('string',	8, required=False)
    mode            = Field('string',	9, required=False)
    manahost        = Field('string',	10, required=False)
    manaport        = Field('int32',	11, required=False)

class LoginResponse(ProtoEntity):
    userID          = Field('int32',	1)
    lastServer      = Field('int32',	2, required=False)
    servers         = Field(Server,	3, repeated=True)
    verify_code     = Field('string',	4)
    new             = Field('bool',	5, required=False)

class WorldServerJoin(ProtoEntity):
    info            = Field(Server,	1)

class LoginResponseExtra(ProtoEntity):
    init_password   = Field('bool',	1)
    platform_uin    = Field('string',	2, required=False)

class FileInfo(ProtoEntity):
    url             = Field('string',	1)
    md5             = Field('string',	2)
    size            = Field('int32',	3)
    new             = Field('bool',	4, default=False)

class CleanUserLastserver(ProtoEntity):
    userID          = Field('int32',	1)

class CheckUpgrade(ProtoEntity):
    version         = Field('int32',	1)
    featureCode     = Field('string',	2, required=False)
    deviceInfo      = Field(DeviceInfo,	3, required=False)

class LoginRequest(ProtoEntity):
    username        = Field('string',	1)
    password        = Field('string',	2)
    serverId        = Field('int32',	3, required=False)
    version         = Field('int32',	4, required=False)
    sdkType         = Field('enum',	5, required=False)
    featureCode     = Field('string',	6, required=False)
    deviceInfo      = Field(DeviceInfo,	7, required=False)

class ChangePasswordResponse(ProtoEntity):
    new_password    = Field('string',	1)

class AutoRegisterResponse(ProtoEntity):
    username        = Field('string',	1)
    sdk_username    = Field('string',	2)
    password        = Field('string',	3)
    regionID        = Field('int32',	4, required=False)

class CheckUpgradeResponse(ProtoEntity):
    isbigupgrade    = Field('bool',	1)
    versionId       = Field('int32',	2, required=False)
    versionName     = Field('string',	3, required=False)
    files           = Field(FileInfo,	4, repeated=True)
    config_version  = Field('int32',	5, required=False)

class RegisterResponse(ProtoEntity):
    sdk_username    = Field('string',	1, required=False)

class DownloadFileResponse(ProtoEntity):
    tag             = Field('int32',	1)
    content         = Field('bytes',	2, required=False)

class HTTPLoginRequest(ProtoEntity):
    username        = Field('string',	1)
    password        = Field('string',	2)
    regionID        = Field('int32',	3, required=False)
    version         = Field('int32',	4, required=False)
    sdkType         = Field('enum',	5, required=False)
    featureCode     = Field('string',	6, required=False)
    deviceInfo      = Field(DeviceInfo,	7, required=False)

class VerifyLoginRequest(ProtoEntity):
    worldID         = Field('int32',	2)
    verify_code     = Field('string',	3)

