cimport cython
from yy.entity.formulas import g_formulas as fn
from yy.entity.base import cycle
from time import time
from datetime import timedelta, date as datedate
from yy.entity.containers import ListContainer, SetContainer, DictContainer, StoredListContainer, StoredSetContainer, StoredDictContainer

from collections import defaultdict, deque

from player.define import PlayerBase as PureEntity

cdef convert_bool(b):
    return bool(int(b))



@cython.freelist(1000)
cdef class c_PlayerBase(object):
    fields_list = PureEntity.fields_list
    fields = PureEntity.fields
    fields_ids_map = PureEntity.fields_ids_map
    store_tag = 'p'

    def cycle(self, *args, **kwargs):
        return cycle(self, *args, **kwargs)

    cdef bint _initialized
    cdef public set dirty_fields
    cdef public set sync_dirty_fields
    cdef public list dirty_commands

    _listeners_on_load = []
    _listeners_on_create = []

    @classmethod
    def listen_on_load(cls, cb):
        cls._listeners_on_load.append(cb)

    @classmethod
    def listen_on_create(cls, cb):
        cls._listeners_on_create.append(cb)

    def __cinit__(self):
        self._initialized = True
        self.dirty_fields = set()
        self.sync_dirty_fields = set()
        self.dirty_commands = []
        # set default value
        self.rank_rest_max_count = 10
        self.maze_boss_cache = -1

        self.__userID = 0

        self.__username = None

        self.__IMEI = None

        self.__entityID = 0

        self.__name = None

        self.__level = 0

        self.__sp = 0

        self.__money = 0

        self.__gold = 0

        self.__vs = 0

        self.__gp = 0

        self.__bp = 0

        self.__slate = 0

        self.__modelID = 0

        self.__sex = 0

        self.__career = 0

        self.__lastlogin = None

        self.__totallogin = 0

        self.__seriallogin = 0

        self.__createtime = None

        self.__fbset = SetContainer()

        self.__fbset.init_entity(self, 'fbset', self.touch_fbset)
        self.__soul = 0

        self.__mailset = SetContainer()

        self.__mailset.init_entity(self, 'mailset', self.touch_mailset)
        self.__petset = SetContainer()

        self.__petset.init_entity(self, 'petset', self.touch_petset)
        self.__pets = DictContainer()

        self.__pets.init_entity(self, 'pets', self.touch_pets)
        self.__mails = DictContainer()

        self.__mails.init_entity(self, 'mails', self.touch_mails)
        self.__spmax = 0

        self.__petmax = 0

        self.__lineups = StoredDictContainer(int_value=False, int_key=True)

        self.__lineups.init_entity(self, 'lineups', self.touch_lineups)
        self.__fbscores = StoredDictContainer(int_value=False, int_key=True)

        self.__fbscores.init_entity(self, 'fbscores', self.touch_fbscores)
        self.__currentfbID = 0

        self.__fbreward = StoredDictContainer(int_value=False, int_key=True)

        self.__fbreward.init_entity(self, 'fbreward', self.touch_fbreward)
        self.__exp = 0

        self.__resume_sp_cd = 0

        self.__spprop = 0

        self.__dbtag = None

        self.__book = StoredSetContainer(int_value=True)

        self.__book.init_entity(self, 'book', self.touch_book)
        self.__fbprocess = 0

        self.__fbadvance = 0

        self.__explore1 = 0

        self.__exploretime1 = 0

        self.__exploretimetype1 = 0

        self.__explore2 = 0

        self.__exploretime2 = 0

        self.__exploretimetype2 = 0

        self.__explore3 = 0

        self.__exploretime3 = 0

        self.__exploretimetype3 = 0

        self.__guide_types = SetContainer()

        self.__guide_types.init_entity(self, 'guide_types', self.touch_guide_types)
        self.__guide_end_signal = 0

        self.__lotteryflag = False

        self.__slatereward_getedset = SetContainer()

        self.__slatereward_getedset.init_entity(self, 'slatereward_getedset', self.touch_slatereward_getedset)
        self.__credits = 0

        self.__loterry_hero_cd_A = 0

        self.__loterry_hero_cd_B = 0

        self.__loterry_hero_cd_C = 0

        self.__loterry_hero_count_A = 0

        self.__loterry_hero_count_B = 0

        self.__loterry_hero_count_C = 0

        self.__loterry_hero_gold_first_A = True

        self.__loterry_hero_gold_first_B = True

        self.__loterry_hero_gold_first_C = True

        self.__loterry_hero_used_free_count_A_ts = 0

        self.__loterry_hero_used_free_count_A = 0

        self.__loterry_hero_used_free_count_B_ts = 0

        self.__loterry_hero_used_free_count_B = 0

        self.__loterry_hero_used_free_count_C_ts = 0

        self.__loterry_hero_used_free_count_C = 0

        self.__loterry_hero_count_2 = 0

        self.__loterry_hero_history_3 = SetContainer()

        self.__loterry_hero_history_3.init_entity(self, 'loterry_hero_history_3', self.touch_loterry_hero_history_3)
        self.__loterry_hero_gold_first_4 = True

        self.__loterry_hero_gold_first_5 = True

        self.__loterry_hero_gold_first_6 = True

        self.__loterry_hero_gold_first_7 = True

        self.__loterry_hero_gold_first_8 = True

        self.__loterry_hero_cd_D = 0

        self.__loterry_hero_count_D = 0

        self.__loterry_hero_gold_first_D = True

        self.__loterry_hero_used_free_count_D_ts = 0

        self.__loterry_hero_used_free_count_D = 0

        self.__resolvegold_time_ts = 0

        self.__resolvegold_time = 0

        self.__pvpgrad = 0

        self.__pvpseasonreward = DictContainer()

        self.__pvpseasonreward.init_entity(self, 'pvpseasonreward', self.touch_pvpseasonreward)
        self.__pvpseasoncount = 0

        self.__pvprankreceiveds = SetContainer()

        self.__pvprankreceiveds.init_entity(self, 'pvprankreceiveds', self.touch_pvprankreceiveds)
        self.__vsCount = 0

        self.__pvplastcleantime = 0

        self.__pvpopenflag = False

        self.__pvprewards = SetContainer()

        self.__pvprewards.init_entity(self, 'pvprewards', self.touch_pvprewards)
        self.__todaybp_ts = 0

        self.__todaybp = 0

        self.__pvprank = 0

        self.__totalbp = 0

        self.__prototypeID = 0

        self.__exploredoubletime1 = 0

        self.__exploredoubletime2 = 0

        self.__exploredoubletime3 = 0

        self.__get_serialloginreward = 0

        self.__offline_attrs = ListContainer()

        self.__offline_attrs.init_entity(self, 'offline_attrs', self.touch_offline_attrs)
        self.__lastlogout = None

        self.__offlinemail_set = SetContainer()

        self.__offlinemail_set.init_entity(self, 'offlinemail_set', self.touch_offlinemail_set)
        self.__fac_offlinemail_set = SetContainer()

        self.__fac_offlinemail_set.init_entity(self, 'fac_offlinemail_set', self.touch_fac_offlinemail_set)
        self.__worldID = 0

        self.__faction_name = None

        self.__faction_level = 0

        self.__faction_is_leader = False

        self.__faction_level_rewards_received_ts = 0

        self.__faction_level_rewards_received = SetContainer()

        self.__faction_level_rewards_received.init_entity(self, 'faction_level_rewards_received', self.touch_faction_level_rewards_received)
        self.__faction_taskID_ts = 0

        self.__faction_taskID = 0

        self.__faction_task_done_ts = 0

        self.__faction_task_done = False

        self.__last_factionID = 0

        self.__applyFactions = SetContainer()

        self.__applyFactions.init_entity(self, 'applyFactions', self.touch_applyFactions)
        self.__joinFactionTime = 0

        self.__factionID = 0

        self.__inviteFactionSet = SetContainer()

        self.__inviteFactionSet.init_entity(self, 'inviteFactionSet', self.touch_inviteFactionSet)
        self.__applyMemberSet = SetContainer()

        self.__applyMemberSet.init_entity(self, 'applyMemberSet', self.touch_applyMemberSet)
        self.__strengthen_df_level = 0

        self.__strengthen_hp_level = 0

        self.__strengthen_at_level = 0

        self.__strengthen_ct_level = 0

        self.__strengthen_hp_max_level = 0

        self.__strengthen_at_max_level = 0

        self.__strengthen_ct_max_level = 0

        self.__strengthen_df_max_level = 0

        self.__buy_sp_used_count_ts = 0

        self.__buy_sp_used_count = 0

        self.__featureCode = None

        self.__clientIP = None

        self.__clientVersion = None

        self.__petPatchs = StoredDictContainer(int_value=True, int_key=True)

        self.__petPatchs.init_entity(self, 'petPatchs', self.touch_petPatchs)
        self.__petpatchdirty = SetContainer()

        self.__petpatchdirty.init_entity(self, 'petpatchdirty', self.touch_petpatchdirty)
        self.__golden_sp = 0

        self.__silver_sp = 0

        self.__retry_fb_count = 0

        self.__consume_count = 0

        self.__lottery_count = 0

        self.__lottery_gold_accumulating = 0

        self.__lottery_money_accumulating = 0

        self.__lottery_gold_accumulating10 = 0

        self.__lottery_money_accumulating10 = 0

        self.__vip_offline = 0

        self.__tasks = StoredDictContainer(int_value=False, int_key=True)

        self.__tasks.init_entity(self, 'tasks', self.touch_tasks)
        self.__taskrewards = SetContainer()

        self.__taskrewards.init_entity(self, 'taskrewards', self.touch_taskrewards)
        self.__task_max_patch_sign_up_count = 0

        self.__task_used_patch_sign_up_count = 0

        self.__task_last_sign_up_time = 0

        self.__task_is_calc_sign_up_ts = 0

        self.__task_is_calc_sign_up = False

        self.__task_sp_daily_receiveds_ts = 0

        self.__task_sp_daily_receiveds = SetContainer()

        self.__task_sp_daily_receiveds.init_entity(self, 'task_sp_daily_receiveds', self.touch_task_sp_daily_receiveds)
        self.__monthly_card_30 = 0

        self.__reset_recharges_seq = 0

        self.__bought_recharges = SetContainer()

        self.__bought_recharges.init_entity(self, 'bought_recharges', self.touch_bought_recharges)
        self.__offline_recharges = ListContainer()

        self.__offline_recharges.init_entity(self, 'offline_recharges', self.touch_offline_recharges)
        self.__limited_packs_used_count = 0

        self.__limited_packs_last_time = 0

        self.__timelimited_packs_last_time = 0

        self.__trigger_packs_buy_count_ts = 0

        self.__trigger_packs_buy_count = 0

        self.__trigger_packs_flag_ts = 0

        self.__trigger_packs_flag = True

        self.__totallogin_after_guide = 0

        self.__seriallogin_after_guide = 0

        self.__first_recharge_flag = True

        self.__first_recharge_numb = 0

        self.__first_recharge_patch = False

        self.__cleanfb = 0

        self.__lineups_defend = ListContainer()

        self.__lineups_defend.init_entity(self, 'lineups_defend', self.touch_lineups_defend)
        self.__on_lineup_defend = 0

        self.__borderID = 0

        self.__rank_detail_cache = DictContainer()

        self.__rank_detail_cache.init_entity(self, 'rank_detail_cache', self.touch_rank_detail_cache)
        self.__rank_count = 0

        self.__rank_active_count = 0

        self.__rank_active_win_count = 0

        self.__rank_win_count = 0

        self.__rank_free_vs_ts = 0

        self.__rank_free_vs = 10

        self.__rank_cd = 0

        self.__rank_history = StoredListContainer(int_value=False)

        self.__rank_history.init_entity(self, 'rank_history', self.touch_rank_history)
        self.__rank_fight_history = StoredDictContainer(int_value=False)

        self.__rank_fight_history.init_entity(self, 'rank_fight_history', self.touch_rank_fight_history)
        self.__rank_passive_offline_count = 0

        self.__totalbp_on_logout = 0

        self.__rank_targets = ListContainer()

        self.__rank_targets.init_entity(self, 'rank_targets', self.touch_rank_targets)
        self.__rank_defeated_targets = SetContainer()

        self.__rank_defeated_targets.init_entity(self, 'rank_defeated_targets', self.touch_rank_defeated_targets)
        self.__rank_rest_count = 10

        self.__rank_resume_rest_count_cd = 0

        self.__rank_reset_used_count_ts = 0

        self.__rank_reset_used_count = 0

        self.__rank_refresh_cd = 0

        self.__rank_refresh_used_count_ts = 0

        self.__rank_refresh_used_count = 0

        self.__rank_serial_win_count = 0

        self.__rank_serial_win_count_cd = 0

        self.__npc_targets_cd = DictContainer()

        self.__npc_targets_cd.init_entity(self, 'npc_targets_cd', self.touch_npc_targets_cd)
        self.__npc_target_cache = 0

        self.__rank_revenged_targets = SetContainer()

        self.__rank_revenged_targets.init_entity(self, 'rank_revenged_targets', self.touch_rank_revenged_targets)
        self.__hotpet_set = SetContainer()

        self.__hotpet_set.init_entity(self, 'hotpet_set', self.touch_hotpet_set)
        self.__today_hotpet = 0

        self.__superhotpet = 0

        self.__petpalt_time = None

        self.__mats = StoredDictContainer(int_value=True, int_key=True)

        self.__mats.init_entity(self, 'mats', self.touch_mats)
        self.__dirty_mats = SetContainer()

        self.__dirty_mats.init_entity(self, 'dirty_mats', self.touch_dirty_mats)
        self.__fp = 0

        self.__totalfp = 0

        self.__todayfp_donate_ts = 0

        self.__todayfp_donate = 0

        self.__dismissCD = 0

        self.__todayfp_sp_ts = 0

        self.__todayfp_sp = 0

        self.__faction_sp = 0

        self.__todayfp_task_ts = 0

        self.__todayfp_task = 0

        self.__giftkeys = StoredDictContainer(int_value=True)

        self.__giftkeys.init_entity(self, 'giftkeys', self.touch_giftkeys)
        self.__equipset = SetContainer()

        self.__equipset.init_entity(self, 'equipset', self.touch_equipset)
        self.__equips = DictContainer()

        self.__equips.init_entity(self, 'equips', self.touch_equips)
        self.__equipeds = DictContainer()

        self.__equipeds.init_entity(self, 'equipeds', self.touch_equipeds)
        self.__mine_rob_history_flag = False

        self.__mine_curr_target_cache = 0

        self.__mine_revenge_booty_cache = -1

        self.__mine_targets_detail_cache = None

        self.__mine_rob_history = StoredListContainer(int_value=False)

        self.__mine_rob_history.init_entity(self, 'mine_rob_history', self.touch_mine_rob_history)
        self.__mine_rob_count = 0

        self.__resume_mine_rob_count_cd = 0

        self.__mine_protect_time = 0

        self.__mine_products1 = 0

        self.__mine_productivity1 = 0

        self.__mine_time1 = 0

        self.__mine_free_collect_count1_ts = 0

        self.__mine_free_collect_count1 = 1

        self.__mine_rob_by_date1 = StoredDictContainer(int_value=True)

        self.__mine_rob_by_date1.init_entity(self, 'mine_rob_by_date1', self.touch_mine_rob_by_date1)
        self.__mine_products2 = 0

        self.__mine_productivity2 = 0

        self.__mine_time2 = 0

        self.__mine_free_collect_count2_ts = 0

        self.__mine_free_collect_count2 = 1

        self.__mine_rob_by_date2 = StoredDictContainer(int_value=True)

        self.__mine_rob_by_date2.init_entity(self, 'mine_rob_by_date2', self.touch_mine_rob_by_date2)
        self.__uproar_targets_cache = None

        self.__uproar_targets_done = SetContainer()

        self.__uproar_targets_done.init_entity(self, 'uproar_targets_done', self.touch_uproar_targets_done)
        self.__uproar_chests_done = SetContainer()

        self.__uproar_chests_done.init_entity(self, 'uproar_chests_done', self.touch_uproar_chests_done)
        self.__uproar_target_cache = 0

        self.__uproar_refresh_used_count_ts = 0

        self.__uproar_refresh_used_count = 0

        self.__jiutian = 0

        self.__uproar_targets_team = StoredDictContainer(int_value=False, int_key=True)

        self.__uproar_targets_team.init_entity(self, 'uproar_targets_team', self.touch_uproar_targets_team)
        self.__uproar_chests_cache = None

        self.__uproar_details_cache = StoredDictContainer(int_value=False, int_key=True)

        self.__uproar_details_cache.init_entity(self, 'uproar_details_cache', self.touch_uproar_details_cache)
        self.__uproar_enemy_buff = 0

        self.__uproar_enemy_min_power = 0

        self.__uproar_targets = StoredDictContainer(int_value=False, int_key=True)

        self.__uproar_targets.init_entity(self, 'uproar_targets', self.touch_uproar_targets)
        self.__uproar_chests = StoredDictContainer(int_value=False, int_key=True)

        self.__uproar_chests.init_entity(self, 'uproar_chests', self.touch_uproar_chests)
        self.__loot_used_count_ts = 0

        self.__loot_used_count = 0

        self.__loot_max_count = 5

        self.__loot_last_resume_time = 0

        self.__loot_temp_mats = StoredDictContainer(int_value=True, int_key=True)

        self.__loot_temp_mats.init_entity(self, 'loot_temp_mats', self.touch_loot_temp_mats)
        self.__loot_targets_cache = None

        self.__loot_current_target = 0

        self.__loot_history = StoredListContainer(int_value=False)

        self.__loot_history.init_entity(self, 'loot_history', self.touch_loot_history)
        self.__loot_reset_count_ts = 0

        self.__loot_reset_count = 0

        self.__loot_reset_crit_count_ts = 0

        self.__loot_reset_crit_count = 0

        self.__loot_protect_time = 0

        self.__pious_backup = 0

        self.__visit_group = 0

        self.__visit_time = 0

        self.__dream = 0

        self.__pious = 0

        self.__visit_free_used_count_ts = 0

        self.__visit_free_used_count = 0

        self.__visit_today_used_count_ts = 0

        self.__visit_today_used_count = 0

        self.__level_packs_done = SetContainer()

        self.__level_packs_done.init_entity(self, 'level_packs_done', self.touch_level_packs_done)
        self.__level_packs_end = SetContainer()

        self.__level_packs_end.init_entity(self, 'level_packs_end', self.touch_level_packs_end)
        self.__power_packs_done = SetContainer()

        self.__power_packs_done.init_entity(self, 'power_packs_done', self.touch_power_packs_done)
        self.__power_packs_end = SetContainer()

        self.__power_packs_end.init_entity(self, 'power_packs_end', self.touch_power_packs_end)
        self.__totallogin_end = SetContainer()

        self.__totallogin_end.init_entity(self, 'totallogin_end', self.touch_totallogin_end)
        self.__factionEVA = 0.0

        self.__max_power = 0

        self.__power_cache = 0

        self.__star_packs_end = SetContainer()

        self.__star_packs_end.init_entity(self, 'star_packs_end', self.touch_star_packs_end)
        self.__star_packs_version = 0

        self.__appid = None

        self.__UDID = None

        self.__idfa = None

        self.__MAC = None

        self.__new_role = False

        self.__autofight = False

        self.__speedUpfight = False

        self.__dongtian_cd = 0

        self.__fudi_cd = 0

        self.__treasure_type = 1

        self.__treasure_refresh_count = 0

        self.__treasure_cache = ListContainer()

        self.__treasure_cache.init_entity(self, 'treasure_cache', self.touch_treasure_cache)
        self.__treasure_cd = 0

        self.__treasure_used_count_ts = 0

        self.__treasure_used_count = 0

        self.__friend_messages = StoredDictContainer(int_value=False, int_key=True)

        self.__friend_messages.init_entity(self, 'friend_messages', self.touch_friend_messages)
        self.__friendset = SetContainer()

        self.__friendset.init_entity(self, 'friendset', self.touch_friendset)
        self.__friend_applys = StoredDictContainer(int_value=False, int_key=True)

        self.__friend_applys.init_entity(self, 'friend_applys', self.touch_friend_applys)
        self.__friend_gift_used_count_ts = 0

        self.__friend_gift_used_count = 0

        self.__friendgiftedset_ts = 0

        self.__friendgiftedset = SetContainer()

        self.__friendgiftedset.init_entity(self, 'friendgiftedset', self.touch_friendgiftedset)
        self.__tap_hurts = ListContainer()

        self.__tap_hurts.init_entity(self, 'tap_hurts', self.touch_tap_hurts)
        self.__tap_hurts_index = 0

        self.__tap_monster = 0

        self.__tap_loop_count = 0

        self.__tap_rest_count = 120

        self.__tap_rest_count_resume_cd = 0

        self.__tap_max_count = 120

        self.__friendfb_list = StoredSetContainer(int_value=False)

        self.__friendfb_list.init_entity(self, 'friendfb_list', self.touch_friendfb_list)
        self.__friend_total_sp = 0

        self.__cache_friendfbID = None

        self.__friendfb_triggered_count = 0

        self.__friendfb_last_trigger_time = 0

        self.__friendfb_last_trigger_fbID = 0

        self.__friendfb_used_count_ts = 0

        self.__friendfb_used_count = 0

        self.__friendfb_kill_count = 0

        self.__friendfb_deads = StoredSetContainer(int_value=False)

        self.__friendfb_deads.init_entity(self, 'friendfb_deads', self.touch_friendfb_deads)
        self.__friendfb_reborn_counts = StoredDictContainer(int_value=True)

        self.__friendfb_reborn_counts.init_entity(self, 'friendfb_reborn_counts', self.touch_friendfb_reborn_counts)
        self.__friendfb_damages = StoredDictContainer(int_value=True, int_key=True)

        self.__friendfb_damages.init_entity(self, 'friendfb_damages', self.touch_friendfb_damages)
        self.__friendfb_buff = 0

        self.__friendfb_deadtimes = StoredDictContainer(int_value=False)

        self.__friendfb_deadtimes.init_entity(self, 'friendfb_deadtimes', self.touch_friendfb_deadtimes)
        self.__malls = StoredDictContainer(int_value=False, int_key=True)

        self.__malls.init_entity(self, 'malls', self.touch_malls)
        self.__mall_times = StoredDictContainer(int_value=True, int_key=True)

        self.__mall_times.init_entity(self, 'mall_times', self.touch_mall_times)
        self.__mall_limits = DictContainer()

        self.__mall_limits.init_entity(self, 'mall_limits', self.touch_mall_limits)
        self.__mall_refresh_times_ts = 0

        self.__mall_refresh_times = DictContainer()

        self.__mall_refresh_times.init_entity(self, 'mall_refresh_times', self.touch_mall_refresh_times)
        self.__mall_last_refresh = DictContainer()

        self.__mall_last_refresh.init_entity(self, 'mall_last_refresh', self.touch_mall_last_refresh)
        self.__mall_silver_opened = False

        self.__mall_silver_open_remain = 0

        self.__mall_golden_opened = False

        self.__mall_golden_open_remain = 0

        self.__shopping = 0

        self.__vip_packs_limits = DictContainer()

        self.__vip_packs_limits.init_entity(self, 'vip_packs_limits', self.touch_vip_packs_limits)
        self.__vip_packs_today_bought_count_ts = 0

        self.__vip_packs_today_bought_count = 0

        self.__vip_packs_limits_reset_flag = False

        self.__wish_used_count = 0

        self.__wish_experience_time = 0

        self.__wish_last_reset_time = 0

        self.__weeks_acc_recharge_amount = 0

        self.__weeks_acc_recharge_last_clean_time = 0

        self.__daily_acc_recharge_amount_ts = 0

        self.__daily_acc_recharge_amount = 0

        self.__cycle_acc_recharge_amount = 0

        self.__cycle_acc_recharge_last_clean_time = 0

        self.__daily_acc_recharge_rewards_ts = 0

        self.__daily_acc_recharge_rewards = SetContainer()

        self.__daily_acc_recharge_rewards.init_entity(self, 'daily_acc_recharge_rewards', self.touch_daily_acc_recharge_rewards)
        self.__cycle_acc_recharge_rewards = SetContainer()

        self.__cycle_acc_recharge_rewards.init_entity(self, 'cycle_acc_recharge_rewards', self.touch_cycle_acc_recharge_rewards)
        self.__weeks_acc_recharge_rewards = SetContainer()

        self.__weeks_acc_recharge_rewards.init_entity(self, 'weeks_acc_recharge_rewards', self.touch_weeks_acc_recharge_rewards)
        self.__month_acc_recharge_rewards = SetContainer()

        self.__month_acc_recharge_rewards.init_entity(self, 'month_acc_recharge_rewards', self.touch_month_acc_recharge_rewards)
        self.__month_acc_recharge_amount = 0

        self.__month_acc_recharge_last_clean_time = 0

        self.__fund_bought_flag = False

        self.__fund_rewards_received = SetContainer()

        self.__fund_rewards_received.init_entity(self, 'fund_rewards_received', self.touch_fund_rewards_received)
        self.__fund_reset_time = 0

        self.__check_in_over_count = 0

        self.__check_in_used_count = 0

        self.__check_in_today_ts = 0

        self.__check_in_today = False

        self.__check_in_last_time = None

        self.__timed_store_cd = 0

        self.__timed_store_id = 0

        self.__trigger_event = 0

        self.__trigger_event_sp = 0

        self.__trigger_chests = SetContainer()

        self.__trigger_chests.init_entity(self, 'trigger_chests', self.touch_trigger_chests)
        self.__trigger_tasks_ts = 0

        self.__trigger_tasks = SetContainer()

        self.__trigger_tasks.init_entity(self, 'trigger_tasks', self.touch_trigger_tasks)
        self.__monthly_card_time = None

        self.__monthly_card_received_ts = 0

        self.__monthly_card_received = False

        self.__monthly_card_acc_amount = 0

        self.__skip_guide = fn.get_skip_guide()

        self.__spar_counts = DictContainer()

        self.__spar_counts.init_entity(self, 'spar_counts', self.touch_spar_counts)
        self.__username_alias = None

        self.__chat_blocked = False

        self.__lock_level = 0

        self.__channel = None

        self.__point = 0

        self.__stone = 0

        self.__enchant_free_used_count_ts = 0

        self.__enchant_free_used_count = 0

        self.__dlc_progress = StoredDictContainer(int_value=False, int_key=True)

        self.__dlc_progress.init_entity(self, 'dlc_progress', self.touch_dlc_progress)
        self.__dlc_helpers = StoredDictContainer(int_value=True, int_key=True)

        self.__dlc_helpers.init_entity(self, 'dlc_helpers', self.touch_dlc_helpers)
        self.__dlc_dispatch = StoredDictContainer(int_value=False, int_key=True)

        self.__dlc_dispatch.init_entity(self, 'dlc_dispatch', self.touch_dlc_dispatch)
        self.__dlc_star_packs_end = SetContainer()

        self.__dlc_star_packs_end.init_entity(self, 'dlc_star_packs_end', self.touch_dlc_star_packs_end)
        self.__dlc_tasks_cd = DictContainer()

        self.__dlc_tasks_cd.init_entity(self, 'dlc_tasks_cd', self.touch_dlc_tasks_cd)
        self.__dlc_detail_cache = StoredDictContainer(int_value=False, int_key=True)

        self.__dlc_detail_cache.init_entity(self, 'dlc_detail_cache', self.touch_dlc_detail_cache)
        self.__count_down_time = 0

        self.__count_down_index = 0

        self.__count_down_cd = 0

        self.__group_applys = None

        self.__groupID = 0

        self.__group_total_intimate = 0

        self.__group_last_kicked_time = 0

        self.__gve_damage = 0

        self.__gve_score = 0

        self.__gve_index = 0

        self.__gve_target = 0

        self.__gve_state = 0

        self.__gve_addition = 0

        self.__gve_groupdamage = 0

        self.__gve_reborn_rest_count_ts = 0

        self.__gve_reborn_rest_count = 1

        self.__gve_last_reset_time = 0

        self.__gve_buff = 0

        self.__gve_ranking_rewards = StoredSetContainer(int_value=False)

        self.__gve_ranking_rewards.init_entity(self, 'gve_ranking_rewards', self.touch_gve_ranking_rewards)
        self.__last_region_name = None

        self.__cache_fight_verify_code = None

        self.__cache_fight_response = None

        self.__boss_campaign_rewards = StoredSetContainer(int_value=False)

        self.__boss_campaign_rewards.init_entity(self, 'boss_campaign_rewards', self.touch_boss_campaign_rewards)
        self.__skillpoint = 0

        self.__skillpoint_cd = 0

        self.__buy_used_skillpoint_count_ts = 0

        self.__buy_used_skillpoint_count = 0

        self.__buy_used_soul_count_ts = 0

        self.__buy_used_soul_count = 0

        self.__swap_targets = SetContainer()

        self.__swap_targets.init_entity(self, 'swap_targets', self.touch_swap_targets)
        self.__swap_cd = 0

        self.__swap_used_count_ts = 0

        self.__swap_used_count = 0

        self.__swap_used_reset_count_ts = 0

        self.__swap_used_reset_count = 0

        self.__swaprank = 0

        self.__swap_history = StoredListContainer(int_value=False)

        self.__swap_history.init_entity(self, 'swap_history', self.touch_swap_history)
        self.__swap_fight_history = StoredDictContainer(int_value=False)

        self.__swap_fight_history.init_entity(self, 'swap_fight_history', self.touch_swap_fight_history)
        self.__swap_win_count = 0

        self.__swapmaxrank = 0

        self.__swap_lock_cd = 0

        self.__swap_register_time = 0

        self.__ball = 0

        self.__maze_step_count = 0

        self.__maze_rest_count = 0

        self.__maze_count_cd = 0

        self.__money_rest_pool = 0

        self.__mazes = list()

        self.__online_packs_cd = 0

        self.__online_packs_index = 0

        self.__online_packs_last_recv = 0

        self.__online_packs_reset = 0

        self.__online_packs_done = False

        self.__mail_reward_receiveds = StoredSetContainer(int_value=False)

        self.__mail_reward_receiveds.init_entity(self, 'mail_reward_receiveds', self.touch_mail_reward_receiveds)
        self.__refinery = 0

        self.__daily_cache_targetID = 0

        self.__daily_dead_resume = 0

        self.__daily_dead_cd = 0

        self.__daily_rewards = DictContainer()

        self.__daily_rewards.init_entity(self, 'daily_rewards', self.touch_daily_rewards)
        self.__daily_kill_count = 0

        self.__daily_registered = 0

        self.__daily_count = 0

        self.__daily_histories = StoredListContainer(int_value=False)

        self.__daily_histories.init_entity(self, 'daily_histories', self.touch_daily_histories)
        self.__daily_history_flag = False

        self.__daily_max_win_count = 0

        self.__daily_rank = 0

        self.__daily_reset_time = 0

        self.__daily_inspire_used_count = 0

        self.__daily_inspire_most_count = 30

        self.__daily_end_panel = DictContainer()

        self.__daily_end_panel.init_entity(self, 'daily_end_panel', self.touch_daily_end_panel)
        self.__task_seven_cd = 0

        self.__guide_reward_flag = False

        self.__guide_defeat_flag = False

        self.__ambition = None

        self.__vip_ambition = None

        self.__ambition_count = 0

        self.__player_equip1 = 0

        self.__player_equip2 = 0

        self.__player_equip3 = 0

        self.__player_equip4 = 0

        self.__player_equip5 = 0

        self.__player_equip6 = 0

        self.__consume_campaign_rewards = SetContainer()

        self.__consume_campaign_rewards.init_entity(self, 'consume_campaign_rewards', self.touch_consume_campaign_rewards)
        self.__consume_campaign_reset_time = 0

        self.__consume_campaign_amount = 0

        self.__login_campaign_rewards = SetContainer()

        self.__login_campaign_rewards.init_entity(self, 'login_campaign_rewards', self.touch_login_campaign_rewards)
        self.__login_campaign_reset_time = 0

        self.__login_campaign_amount = 0

        self.__ranking_pet_count = 0

        self.__ranking_pet_power = 0

        self.__ranking_pet_power_entityID = 0

        self.__ranking_pet_power_prototypeID = 0

        self.__ranking_pet_power_breaklevel = 0

        self.__rankingreceiveds = SetContainer()

        self.__rankingreceiveds.init_entity(self, 'rankingreceiveds', self.touch_rankingreceiveds)
        self.__ranking_receiveds = StoredSetContainer(int_value=False)

        self.__ranking_receiveds.init_entity(self, 'ranking_receiveds', self.touch_ranking_receiveds)
        self.__ranking_equip_power = 0

        self.__ranking_equip_power_entityID = 0

        self.__ranking_equip_power_prototypeID = 0

        self.__ranking_equip_power_step = 0

        self.__ranking_equip_power_level = 0

        self.__daily_recharge_rewards_ts = 0

        self.__daily_recharge_rewards = list()

        self.__daily_recharge_useds_ts = 0

        self.__daily_recharge_useds = DictContainer()

        self.__daily_recharge_useds.init_entity(self, 'daily_recharge_useds', self.touch_daily_recharge_useds)
        self.__scene_rewards = StoredSetContainer(int_value=True)

        self.__scene_rewards.init_entity(self, 'scene_rewards', self.touch_scene_rewards)
        self.__free_pet_exchange_ts = 0

        self.__free_pet_exchange = 3

        self.__mat_exchange_limits_ts = 0

        self.__mat_exchange_limits = DictContainer()

        self.__mat_exchange_limits.init_entity(self, 'mat_exchange_limits', self.touch_mat_exchange_limits)
        self.__last_check_mail_time = 0

        self.__city_dungeon_mg_cache = DictContainer()

        self.__city_dungeon_mg_cache.init_entity(self, 'city_dungeon_mg_cache', self.touch_city_dungeon_mg_cache)
        self.__city_dungeon_last_reset = 0

        self.__city_dungeon_rewards = DictContainer()

        self.__city_dungeon_rewards.init_entity(self, 'city_dungeon_rewards', self.touch_city_dungeon_rewards)
        self.__city_rewards_recv = StoredSetContainer(int_value=False)

        self.__city_rewards_recv.init_entity(self, 'city_rewards_recv', self.touch_city_rewards_recv)
        self.__city_dungeon_kill_count = 0

        self.__city_treasure_recv_flag_ts = 0

        self.__city_treasure_recv_flag = False

        self.__city_contend_cache_target = DictContainer()

        self.__city_contend_cache_target.init_entity(self, 'city_contend_cache_target', self.touch_city_contend_cache_target)
        self.__city_contend_rewards = DictContainer()

        self.__city_contend_rewards.init_entity(self, 'city_contend_rewards', self.touch_city_contend_rewards)
        self.__city_contend_last_reset = 0

        self.__city_contend_treasure = 0

        self.__city_contend_step = 0

        self.__city_contend_total_treasure = 0

        self.__city_contend_count = 0

        self.__city_contend_events = ListContainer()

        self.__city_contend_events.init_entity(self, 'city_contend_events', self.touch_city_contend_events)
        self.__city_contend_total_step = 0

        self.__city_contend_total_treasure_backup = 0

        self.__city_contend_count_backup = 0

        self.__monthcard1 = 0

        self.__monthcard2 = 0

        self.__monthcard_recv1_ts = 0

        self.__monthcard_recv1 = False

        self.__monthcard_recv2_ts = 0

        self.__monthcard_recv2 = False

        self.__weekscard1 = 0

        self.__weekscard2 = 0

        self.__weekscard_recv1_ts = 0

        self.__weekscard_recv1 = False

        self.__weekscard_recv2_ts = 0

        self.__weekscard_recv2 = False

        self.__exchange_campaign_counter = 0

        self.__exchange_campaign_last_time = 0

        self.__refresh_store_campaign_counter = 0

        self.__refresh_store_campaign_last_time = 0

        self.__refresh_reward_done = SetContainer()

        self.__refresh_reward_done.init_entity(self, 'refresh_reward_done', self.touch_refresh_reward_done)
        self.__refresh_reward_end = SetContainer()

        self.__refresh_reward_end.init_entity(self, 'refresh_reward_end', self.touch_refresh_reward_end)
        self.__shake_tree_used_count_ts = 0

        self.__shake_tree_used_count = 0

        self.__seed_state = 0

        self.__seed_id = 0

        self.__seed_state_last_change_time = 0

        self.__seed_state_next_change_time = 0

        self.__seed_state_plant_time = 0

        self.__seed_state_ripening_time = 0

        self.__watering_used_count_ts = 0

        self.__watering_used_count = 0

        self.__watering_time = 0

        self.__worming_used_count_ts = 0

        self.__worming_used_count = 0

        self.__worming_time = 0

        self.__clean_reward_index = 0

        self.__seed_reward_index = None

        self.__seal_seed_prob_id = 0

        self.__seal_seed_prob_campaign_last_time = 0

        self.__seal_seed_reward_next_index = 0

        self.__shake_tree_prob_id = 0

        self.__shake_tree_reward_free_next_index = 0

        self.__shake_tree_prob_campaign_last_time = 0

        self.__shake_tree_reward_pay_next_index = 0

        self.__handsel_campaign_counter = 0

        self.__handsel_campaign_last_time = 0

        self.__campaign_honor_point = None

        self.__flower_boss_campaign_total_hurt = 0

        self.__flower_boss_campaign_last_time = 0

        self.__climb_tower_max_floor = 0

        self.__climb_tower_floor = 0

        self.__climb_tower_tip_floors = SetContainer()

        self.__climb_tower_tip_floors.init_entity(self, 'climb_tower_tip_floors', self.touch_climb_tower_tip_floors)
        self.__climb_tower_used_count_ts = 0

        self.__climb_tower_used_count = 0

        self.__climb_tower_chests = SetContainer()

        self.__climb_tower_chests.init_entity(self, 'climb_tower_chests', self.touch_climb_tower_chests)
        self.__climb_tower_history = StoredListContainer(int_value=False)

        self.__climb_tower_history.init_entity(self, 'climb_tower_history', self.touch_climb_tower_history)
        self.__climb_tower_fight_history = StoredDictContainer(int_value=False)

        self.__climb_tower_fight_history.init_entity(self, 'climb_tower_fight_history', self.touch_climb_tower_fight_history)
        self.__climb_tower_accredit_floor = 0

        self.__climb_tower_accredit_protect_time = 0

        self.__climb_tower_accredit_stash_time = 0

        self.__climb_tower_accredit_cd = 0

        self.__climb_tower_accredit_stash_earnings = 0

        self.__phantom = 0

        self.__climb_tower_last_target = 0

        self.__climb_tower_verify_code = None

        self.__gems = StoredDictContainer(int_value=True, int_key=True)

        self.__gems.init_entity(self, 'gems', self.touch_gems)
        self.__dirty_gems = SetContainer()

        self.__dirty_gems.init_entity(self, 'dirty_gems', self.touch_dirty_gems)
        self.__inlay1 = 0

        self.__inlay2 = 0

        self.__inlay3 = 0

        self.__inlay4 = 0

        self.__inlay5 = 0

        self.__inlay6 = 0


    def begin_initialize(self):
        self._initialized = False

    def end_initialize(self):
        self._initialized = True

    def load_containers(self):
        self.lineups.load()
        self.fbscores.load()
        self.fbreward.load()
        self.book.load()
        self.petPatchs.load()
        self.tasks.load()
        self.rank_history.load()
        self.rank_fight_history.load()
        self.mats.load()
        self.giftkeys.load()
        self.mine_rob_history.load()
        self.mine_rob_by_date1.load()
        self.mine_rob_by_date2.load()
        self.uproar_targets_team.load()
        self.uproar_details_cache.load()
        self.uproar_targets.load()
        self.uproar_chests.load()
        self.loot_temp_mats.load()
        self.loot_history.load()
        self.friend_messages.load()
        self.friend_applys.load()
        self.friendfb_list.load()
        self.friendfb_deads.load()
        self.friendfb_reborn_counts.load()
        self.friendfb_damages.load()
        self.friendfb_deadtimes.load()
        self.malls.load()
        self.mall_times.load()
        self.dlc_progress.load()
        self.dlc_helpers.load()
        self.dlc_dispatch.load()
        self.dlc_detail_cache.load()
        self.gve_ranking_rewards.load()
        self.boss_campaign_rewards.load()
        self.swap_history.load()
        self.swap_fight_history.load()
        self.mail_reward_receiveds.load()
        self.daily_histories.load()
        self.ranking_receiveds.load()
        self.scene_rewards.load()
        self.city_rewards_recv.load()
        self.climb_tower_history.load()
        self.climb_tower_fight_history.load()
        self.gems.load()
        pass

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if v is not None:
                setattr(self, k, v)

    def push_command(self, *cmd):
        self.dirty_commands.append(cmd)

    # event fields
    _listeners_fbprocess = []
    @classmethod
    def listen_fbprocess(cls, callback):
        cls._listeners_fbprocess.append(callback)
    _listeners_friendfb_kill_count = []
    @classmethod
    def listen_friendfb_kill_count(cls, callback):
        cls._listeners_friendfb_kill_count.append(callback)
    _listeners_ambition_count = []
    @classmethod
    def listen_ambition_count(cls, callback):
        cls._listeners_ambition_count.append(callback)
    _listeners_ranking_pet_count = []
    @classmethod
    def listen_ranking_pet_count(cls, callback):
        cls._listeners_ranking_pet_count.append(callback)
    _listeners_ranking_pet_power = []
    @classmethod
    def listen_ranking_pet_power(cls, callback):
        cls._listeners_ranking_pet_power.append(callback)
    _listeners_ranking_equip_power = []
    @classmethod
    def listen_ranking_equip_power(cls, callback):
        cls._listeners_ranking_equip_power.append(callback)

    # simple fields
    cdef public int rank_rest_max_count
    cdef public int maze_boss_cache

    # normal fields
    cdef public int __userID
    property userID:
        def __get__(self):
            return self.__userID
        def __set__(self, value):
                value = int(value)
                if value != self.__userID:
                    self.__userID = value
                    if self._initialized:
                        self.touch_userID()

    cpdef touch_userID(self):
        self.dirty_fields.add('userID')
        pass
    cdef public unicode __username
    property username:
        def __get__(self):
            return self.__username
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__username:
                    self.__username = value
                    if self._initialized:
                        self.touch_username()

    cpdef touch_username(self):
        self.dirty_fields.add('username')
        pass
    cdef public unicode __IMEI
    property IMEI:
        def __get__(self):
            return self.__IMEI
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__IMEI:
                    self.__IMEI = value
                    if self._initialized:
                        self.touch_IMEI()

    cpdef touch_IMEI(self):
        self.dirty_fields.add('IMEI')
        pass
    cdef public int __entityID
    property entityID:
        def __get__(self):
            return self.__entityID
        def __set__(self, value):
                value = int(value)
                if value != self.__entityID:
                    self.__entityID = value
                    if self._initialized:
                        self.touch_entityID()

    cpdef touch_entityID(self):
        self.dirty_fields.add('entityID')
        self.sync_dirty_fields.add('entityID')
        self.__power = None
        self.__task_noob_flag = None
        self.__task_noob_undo = None
        self.__taskrewardsdone14 = None
        self.__base_power = None
        self.__equip_power = None
        self.__point_power = None
        self.__count_down_flag = None
        self.__daily_dead = None
        self.__daily_win_count = None
        self.__honor_power = None
        self.__climb_tower_accredit_lineup = None
        self.__gems_power = None
        self.clear_power()
        self.clear_task_noob_flag()
        self.clear_task_noob_undo()
        self.clear_taskrewardsdone14()
        self.clear_base_power()
        self.clear_equip_power()
        self.clear_point_power()
        self.clear_count_down_flag()
        self.clear_daily_dead()
        self.clear_daily_win_count()
        self.clear_honor_power()
        self.clear_climb_tower_accredit_lineup()
        self.clear_gems_power()
        pass
    cdef public unicode __name
    property name:
        def __get__(self):
            return self.__name
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__name:
                    self.__name = value
                    if self._initialized:
                        self.touch_name()

    cpdef touch_name(self):
        self.dirty_fields.add('name')
        self.sync_dirty_fields.add('name')
        pass
    cdef public int __level
    property level:
        def __get__(self):
            return self.__level
        def __set__(self, value):
                value = int(value)
                if value != self.__level:
                    self.__level = value
                    if self._initialized:
                        self.touch_level()

    cpdef touch_level(self):
        self.dirty_fields.add('level')
        self.sync_dirty_fields.add('level')
        self.__expmax = None
        self.__expnxt = None
        self.__mine_safety1 = None
        self.__mine_maximum1 = None
        self.__mine_level1 = None
        self.__mine_safety2 = None
        self.__mine_maximum2 = None
        self.__mine_level2 = None
        self.__friend_max_count = None
        self.__friend_gift_max_count = None
        self.__mall_silver_open_cost = None
        self.__mall_golden_open_cost = None
        self.__fund_open_rewards_can_receive = None
        self.__count_down_flag = None
        self.__money_most_pool = None
        self.__online_packs_flag = None
        self.clear_expmax()
        self.clear_expnxt()
        self.clear_mine_safety1()
        self.clear_mine_maximum1()
        self.clear_mine_level1()
        self.clear_mine_safety2()
        self.clear_mine_maximum2()
        self.clear_mine_level2()
        self.clear_friend_max_count()
        self.clear_friend_gift_max_count()
        self.clear_mall_silver_open_cost()
        self.clear_mall_golden_open_cost()
        self.clear_fund_open_rewards_can_receive()
        self.clear_count_down_flag()
        self.clear_money_most_pool()
        self.clear_online_packs_flag()
        pass
    cdef public int __sp
    property sp:
        def __get__(self):
            return self.__sp
        def __set__(self, value):
                value = int(value)
                if value != self.__sp:
                    self.__sp = value
                    if self._initialized:
                        self.touch_sp()

    cpdef touch_sp(self):
        self.dirty_fields.add('sp')
        self.sync_dirty_fields.add('sp')
        #self.sync_dirty_fields.add('resume_sp_cd')
        pass
    cdef public int __money
    property money:
        def __get__(self):
            return self.__money
        def __set__(self, value):
                value = int(value)
                if value != self.__money:
                    self.__money = value
                    if self._initialized:
                        self.touch_money()

    cpdef touch_money(self):
        self.dirty_fields.add('money')
        self.sync_dirty_fields.add('money')
        pass
    cdef public int __gold
    property gold:
        def __get__(self):
            return self.__gold
        def __set__(self, value):
                value = int(value)
                if value != self.__gold:
                    self.__gold = value
                    if self._initialized:
                        self.touch_gold()

    cpdef touch_gold(self):
        self.dirty_fields.add('gold')
        self.sync_dirty_fields.add('gold')
        pass
    cdef public int __vs
    property vs:
        def __get__(self):
            return self.__vs
        def __set__(self, value):
                value = int(value)
                if value != self.__vs:
                    self.__vs = value
                    if self._initialized:
                        self.touch_vs()

    cpdef touch_vs(self):
        self.dirty_fields.add('vs')
        self.sync_dirty_fields.add('vs')
        pass
    cdef public int __gp
    property gp:
        def __get__(self):
            return self.__gp
        def __set__(self, value):
                value = int(value)
                if value != self.__gp:
                    self.__gp = value
                    if self._initialized:
                        self.touch_gp()

    cpdef touch_gp(self):
        self.dirty_fields.add('gp')
        self.sync_dirty_fields.add('gp')
        pass
    cdef public int __bp
    property bp:
        def __get__(self):
            return self.__bp
        def __set__(self, value):
                value = int(value)
                if value != self.__bp:
                    self.__bp = value
                    if self._initialized:
                        self.touch_bp()

    cpdef touch_bp(self):
        self.dirty_fields.add('bp')
        self.sync_dirty_fields.add('bp')
        pass
    cdef public int __slate
    property slate:
        def __get__(self):
            return self.__slate
        def __set__(self, value):
                value = int(value)
                if value != self.__slate:
                    self.__slate = value
                    if self._initialized:
                        self.touch_slate()

    cpdef touch_slate(self):
        self.dirty_fields.add('slate')
        self.sync_dirty_fields.add('slate')
        pass
    cdef public int __modelID
    property modelID:
        def __get__(self):
            return self.__modelID
        def __set__(self, value):
                value = int(value)
                if value != self.__modelID:
                    self.__modelID = value
                    if self._initialized:
                        self.touch_modelID()

    cpdef touch_modelID(self):
        self.dirty_fields.add('modelID')
        pass
    cdef public int __sex
    property sex:
        def __get__(self):
            return self.__sex
        def __set__(self, value):
                value = int(value)
                if value != self.__sex:
                    self.__sex = value
                    if self._initialized:
                        self.touch_sex()

    cpdef touch_sex(self):
        self.dirty_fields.add('sex')
        self.sync_dirty_fields.add('sex')
        pass
    cdef public int __career
    property career:
        def __get__(self):
            return self.__career
        def __set__(self, value):
                value = int(value)
                if value != self.__career:
                    self.__career = value
                    if self._initialized:
                        self.touch_career()

    cpdef touch_career(self):
        self.dirty_fields.add('career')
        self.sync_dirty_fields.add('career')
        pass
    cdef public object __lastlogin
    property lastlogin:
        def __get__(self):
            return self.__lastlogin
        def __set__(self, value):
                value = value
                if value != self.__lastlogin:
                    self.__lastlogin = value
                    if self._initialized:
                        self.touch_lastlogin()

    cpdef touch_lastlogin(self):
        self.dirty_fields.add('lastlogin')
        pass
    cdef public int __totallogin
    property totallogin:
        def __get__(self):
            return self.__totallogin
        def __set__(self, value):
                value = int(value)
                if value != self.__totallogin:
                    self.__totallogin = value
                    if self._initialized:
                        self.touch_totallogin()

    cpdef touch_totallogin(self):
        self.dirty_fields.add('totallogin')
        pass
    cdef public int __seriallogin
    property seriallogin:
        def __get__(self):
            return self.__seriallogin
        def __set__(self, value):
                value = int(value)
                if value != self.__seriallogin:
                    self.__seriallogin = value
                    if self._initialized:
                        self.touch_seriallogin()

    cpdef touch_seriallogin(self):
        self.dirty_fields.add('seriallogin')
        pass
    cdef public object __createtime
    property createtime:
        def __get__(self):
            return self.__createtime
        def __set__(self, value):
                value = value
                if value != self.__createtime:
                    self.__createtime = value
                    if self._initialized:
                        self.touch_createtime()

    cpdef touch_createtime(self):
        self.dirty_fields.add('createtime')
        self.__check_in_rest_count = None
        self.clear_check_in_rest_count()
        pass
    cdef public object __fbset
    property fbset:
        def __get__(self):
            return self.__fbset
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'fbset', self.touch_fbset)
                if value != self.__fbset:
                    self.__fbset = value
                    if self._initialized:
                        self.touch_fbset()

    cpdef touch_fbset(self):
        self.dirty_fields.add('fbset')
        pass
    cdef public int __soul
    property soul:
        def __get__(self):
            return self.__soul
        def __set__(self, value):
                value = int(value)
                if value != self.__soul:
                    self.__soul = value
                    if self._initialized:
                        self.touch_soul()

    cpdef touch_soul(self):
        self.dirty_fields.add('soul')
        self.sync_dirty_fields.add('soul')
        pass
    cdef public object __mailset
    property mailset:
        def __get__(self):
            return self.__mailset
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'mailset', self.touch_mailset)
                if value != self.__mailset:
                    self.__mailset = value
                    if self._initialized:
                        self.touch_mailset()

    cpdef touch_mailset(self):
        self.dirty_fields.add('mailset')
        pass
    cdef public object __petset
    property petset:
        def __get__(self):
            return self.__petset
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'petset', self.touch_petset)
                if value != self.__petset:
                    self.__petset = value
                    if self._initialized:
                        self.touch_petset()

    cpdef touch_petset(self):
        self.dirty_fields.add('petset')
        pass
    cdef public object __pets
    property pets:
        def __get__(self):
            return self.__pets
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'pets', self.touch_pets)
                if value != self.__pets:
                    self.__pets = value
                    if self._initialized:
                        self.touch_pets()

    cpdef touch_pets(self):
        self.__sames = None
        self.clear_sames()
        pass
    cdef public object __mails
    property mails:
        def __get__(self):
            return self.__mails
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'mails', self.touch_mails)
                if value != self.__mails:
                    self.__mails = value
                    if self._initialized:
                        self.touch_mails()

    cpdef touch_mails(self):
        self.__newmailcount = None
        self.__mailcount = None
        self.clear_newmailcount()
        self.clear_mailcount()
        pass
    cdef public int __spmax
    property spmax:
        def __get__(self):
            return self.__spmax
        def __set__(self, value):
                value = int(value)
                if value != self.__spmax:
                    self.__spmax = value
                    if self._initialized:
                        self.touch_spmax()

    cpdef touch_spmax(self):
        self.dirty_fields.add('spmax')
        self.sync_dirty_fields.add('spmax')
        pass
    cdef public int __petmax
    property petmax:
        def __get__(self):
            return self.__petmax
        def __set__(self, value):
                value = int(value)
                if value != self.__petmax:
                    self.__petmax = value
                    if self._initialized:
                        self.touch_petmax()

    cpdef touch_petmax(self):
        self.dirty_fields.add('petmax')
        self.sync_dirty_fields.add('petmax')
        pass
    cdef public object __lineups
    property lineups:
        def __get__(self):
            return self.__lineups
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_lineups(self):
        self.__power = None
        self.__base_power = None
        self.__equip_power = None
        self.__point_power = None
        self.__climb_tower_accredit_lineup = None
        self.__gems_power = None
        self.clear_power()
        self.clear_base_power()
        self.clear_equip_power()
        self.clear_point_power()
        self.clear_climb_tower_accredit_lineup()
        self.clear_gems_power()
        pass
    cdef public object __fbscores
    property fbscores:
        def __get__(self):
            return self.__fbscores
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_fbscores(self):
        pass
    cdef public int __currentfbID
    property currentfbID:
        def __get__(self):
            return self.__currentfbID
        def __set__(self, value):
                value = int(value)
                if value != self.__currentfbID:
                    self.__currentfbID = value
                    if self._initialized:
                        self.touch_currentfbID()

    cpdef touch_currentfbID(self):
        self.dirty_fields.add('currentfbID')
        pass
    cdef public object __fbreward
    property fbreward:
        def __get__(self):
            return self.__fbreward
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_fbreward(self):
        pass
    cdef public int __exp
    property exp:
        def __get__(self):
            return self.__exp
        def __set__(self, value):
                value = int(value)
                if value != self.__exp:
                    self.__exp = value
                    if self._initialized:
                        self.touch_exp()

    cpdef touch_exp(self):
        self.dirty_fields.add('exp')
        self.sync_dirty_fields.add('exp')
        pass
    cdef public int __resume_sp_cd
    property resume_sp_cd:
        def __get__(self):
            return self.__resume_sp_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__resume_sp_cd:
                    self.__resume_sp_cd = value
                    if self._initialized:
                        self.touch_resume_sp_cd()

    cpdef touch_resume_sp_cd(self):
        self.dirty_fields.add('resume_sp_cd')
        self.sync_dirty_fields.add('resume_sp_cd')
        pass
    cdef public int __spprop
    property spprop:
        def __get__(self):
            return self.__spprop
        def __set__(self, value):
                value = int(value)
                if value != self.__spprop:
                    self.__spprop = value
                    if self._initialized:
                        self.touch_spprop()

    cpdef touch_spprop(self):
        self.dirty_fields.add('spprop')
        self.sync_dirty_fields.add('spprop')
        pass
    cdef public unicode __dbtag
    property dbtag:
        def __get__(self):
            return self.__dbtag
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__dbtag:
                    self.__dbtag = value
                    if self._initialized:
                        self.touch_dbtag()

    cpdef touch_dbtag(self):
        pass
    cdef public object __book
    property book:
        def __get__(self):
            return self.__book
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_book(self):
        pass
    cdef public int __fbprocess
    property fbprocess:
        def __get__(self):
            return self.__fbprocess
        def __set__(self, value):
                value = int(value)
                if value != self.__fbprocess:
                    if self._initialized:
                        for callback in type(self)._listeners_fbprocess:
                            callback(self, value)
                    self.__fbprocess = value
                    if self._initialized:
                        self.touch_fbprocess()

    cpdef touch_fbprocess(self):
        self.dirty_fields.add('fbprocess')
        if self._initialized:
            value = self.fbprocess
            for callback in type(self)._listeners_fbprocess:
                callback(self, value)
        pass
    cdef public int __fbadvance
    property fbadvance:
        def __get__(self):
            return self.__fbadvance
        def __set__(self, value):
                value = int(value)
                if value != self.__fbadvance:
                    self.__fbadvance = value
                    if self._initialized:
                        self.touch_fbadvance()

    cpdef touch_fbadvance(self):
        self.dirty_fields.add('fbadvance')
        pass
    cdef public int __explore1
    property explore1:
        def __get__(self):
            return self.__explore1
        def __set__(self, value):
                value = int(value)
                if value != self.__explore1:
                    self.__explore1 = value
                    if self._initialized:
                        self.touch_explore1()

    cpdef touch_explore1(self):
        self.dirty_fields.add('explore1')
        self.sync_dirty_fields.add('explore1')
        pass
    cdef public int __exploretime1
    property exploretime1:
        def __get__(self):
            return self.__exploretime1
        def __set__(self, value):
                value = int(value)
                if value != self.__exploretime1:
                    self.__exploretime1 = value
                    if self._initialized:
                        self.touch_exploretime1()

    cpdef touch_exploretime1(self):
        self.dirty_fields.add('exploretime1')
        self.sync_dirty_fields.add('exploretime1')
        pass
    cdef public int __exploretimetype1
    property exploretimetype1:
        def __get__(self):
            return self.__exploretimetype1
        def __set__(self, value):
                value = int(value)
                if value != self.__exploretimetype1:
                    self.__exploretimetype1 = value
                    if self._initialized:
                        self.touch_exploretimetype1()

    cpdef touch_exploretimetype1(self):
        self.dirty_fields.add('exploretimetype1')
        pass
    cdef public int __explore2
    property explore2:
        def __get__(self):
            return self.__explore2
        def __set__(self, value):
                value = int(value)
                if value != self.__explore2:
                    self.__explore2 = value
                    if self._initialized:
                        self.touch_explore2()

    cpdef touch_explore2(self):
        self.dirty_fields.add('explore2')
        self.sync_dirty_fields.add('explore2')
        pass
    cdef public int __exploretime2
    property exploretime2:
        def __get__(self):
            return self.__exploretime2
        def __set__(self, value):
                value = int(value)
                if value != self.__exploretime2:
                    self.__exploretime2 = value
                    if self._initialized:
                        self.touch_exploretime2()

    cpdef touch_exploretime2(self):
        self.dirty_fields.add('exploretime2')
        self.sync_dirty_fields.add('exploretime2')
        pass
    cdef public int __exploretimetype2
    property exploretimetype2:
        def __get__(self):
            return self.__exploretimetype2
        def __set__(self, value):
                value = int(value)
                if value != self.__exploretimetype2:
                    self.__exploretimetype2 = value
                    if self._initialized:
                        self.touch_exploretimetype2()

    cpdef touch_exploretimetype2(self):
        self.dirty_fields.add('exploretimetype2')
        pass
    cdef public int __explore3
    property explore3:
        def __get__(self):
            return self.__explore3
        def __set__(self, value):
                value = int(value)
                if value != self.__explore3:
                    self.__explore3 = value
                    if self._initialized:
                        self.touch_explore3()

    cpdef touch_explore3(self):
        self.dirty_fields.add('explore3')
        self.sync_dirty_fields.add('explore3')
        pass
    cdef public int __exploretime3
    property exploretime3:
        def __get__(self):
            return self.__exploretime3
        def __set__(self, value):
                value = int(value)
                if value != self.__exploretime3:
                    self.__exploretime3 = value
                    if self._initialized:
                        self.touch_exploretime3()

    cpdef touch_exploretime3(self):
        self.dirty_fields.add('exploretime3')
        self.sync_dirty_fields.add('exploretime3')
        pass
    cdef public int __exploretimetype3
    property exploretimetype3:
        def __get__(self):
            return self.__exploretimetype3
        def __set__(self, value):
                value = int(value)
                if value != self.__exploretimetype3:
                    self.__exploretimetype3 = value
                    if self._initialized:
                        self.touch_exploretimetype3()

    cpdef touch_exploretimetype3(self):
        self.dirty_fields.add('exploretimetype3')
        pass
    cdef public object __guide_types
    property guide_types:
        def __get__(self):
            return self.__guide_types
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'guide_types', self.touch_guide_types)
                if value != self.__guide_types:
                    self.__guide_types = value
                    if self._initialized:
                        self.touch_guide_types()

    cpdef touch_guide_types(self):
        self.dirty_fields.add('guide_types')
        pass
    cdef public int __guide_end_signal
    property guide_end_signal:
        def __get__(self):
            return self.__guide_end_signal
        def __set__(self, value):
                value = int(value)
                if value != self.__guide_end_signal:
                    self.__guide_end_signal = value
                    if self._initialized:
                        self.touch_guide_end_signal()

    cpdef touch_guide_end_signal(self):
        self.dirty_fields.add('guide_end_signal')
        pass
    cdef public object __lotteryflag
    property lotteryflag:
        def __get__(self):
            return self.__lotteryflag
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__lotteryflag:
                    self.__lotteryflag = value
                    if self._initialized:
                        self.touch_lotteryflag()

    cpdef touch_lotteryflag(self):
        self.dirty_fields.add('lotteryflag')
        pass
    cdef public object __slatereward_getedset
    property slatereward_getedset:
        def __get__(self):
            return self.__slatereward_getedset
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'slatereward_getedset', self.touch_slatereward_getedset)
                if value != self.__slatereward_getedset:
                    self.__slatereward_getedset = value
                    if self._initialized:
                        self.touch_slatereward_getedset()

    cpdef touch_slatereward_getedset(self):
        self.dirty_fields.add('slatereward_getedset')
        self.__slatelen = None
        self.clear_slatelen()
        pass
    cdef public int __credits
    property credits:
        def __get__(self):
            return self.__credits
        def __set__(self, value):
                value = int(value)
                if value != self.__credits:
                    self.__credits = value
                    if self._initialized:
                        self.touch_credits()

    cpdef touch_credits(self):
        self.dirty_fields.add('credits')
        self.sync_dirty_fields.add('credits')
        self.__buy_sp_rest_count = None
        self.__vip = None
        self.__vip_refresh_fb_max_count = None
        self.__clean_campaign_vip = None
        self.__rank_reset_rest_count = None
        self.__mine_rob_max_count = None
        self.__uproar_refresh_rest_count = None
        self.__uproar_refresh_max_count = None
        self.__treasure_count = None
        self.__treasure_max_count = None
        self.__tap_onekey = None
        self.__mall_silver_open_cost = None
        self.__mall_golden_open_cost = None
        self.__vip_packs_flag = None
        self.__skillpoint_max = None
        self.__buy_rest_skillpoint_count = None
        self.__buy_rest_soul_count = None
        self.__swap_rest_reset_count = None
        self.__swap_most_reset_count = None
        self.__climb_tower_max_count = None
        self.clear_buy_sp_rest_count()
        self.clear_vip()
        self.clear_vip_refresh_fb_max_count()
        self.clear_clean_campaign_vip()
        self.clear_rank_reset_rest_count()
        self.clear_mine_rob_max_count()
        self.clear_uproar_refresh_rest_count()
        self.clear_uproar_refresh_max_count()
        self.clear_treasure_count()
        self.clear_treasure_max_count()
        self.clear_tap_onekey()
        self.clear_mall_silver_open_cost()
        self.clear_mall_golden_open_cost()
        self.clear_vip_packs_flag()
        self.clear_skillpoint_max()
        self.clear_buy_rest_skillpoint_count()
        self.clear_buy_rest_soul_count()
        self.clear_swap_rest_reset_count()
        self.clear_swap_most_reset_count()
        self.clear_climb_tower_max_count()
        pass
    cdef public int __loterry_hero_cd_A
    property loterry_hero_cd_A:
        def __get__(self):
            return self.__loterry_hero_cd_A
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_cd_A:
                    self.__loterry_hero_cd_A = value
                    if self._initialized:
                        self.touch_loterry_hero_cd_A()

    cpdef touch_loterry_hero_cd_A(self):
        self.dirty_fields.add('loterry_hero_cd_A')
        self.sync_dirty_fields.add('loterry_hero_cd_A')
        pass
    cdef public int __loterry_hero_cd_B
    property loterry_hero_cd_B:
        def __get__(self):
            return self.__loterry_hero_cd_B
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_cd_B:
                    self.__loterry_hero_cd_B = value
                    if self._initialized:
                        self.touch_loterry_hero_cd_B()

    cpdef touch_loterry_hero_cd_B(self):
        self.dirty_fields.add('loterry_hero_cd_B')
        self.sync_dirty_fields.add('loterry_hero_cd_B')
        pass
    cdef public int __loterry_hero_cd_C
    property loterry_hero_cd_C:
        def __get__(self):
            return self.__loterry_hero_cd_C
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_cd_C:
                    self.__loterry_hero_cd_C = value
                    if self._initialized:
                        self.touch_loterry_hero_cd_C()

    cpdef touch_loterry_hero_cd_C(self):
        self.dirty_fields.add('loterry_hero_cd_C')
        self.sync_dirty_fields.add('loterry_hero_cd_C')
        pass
    cdef public int __loterry_hero_count_A
    property loterry_hero_count_A:
        def __get__(self):
            return self.__loterry_hero_count_A
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_count_A:
                    self.__loterry_hero_count_A = value
                    if self._initialized:
                        self.touch_loterry_hero_count_A()

    cpdef touch_loterry_hero_count_A(self):
        self.dirty_fields.add('loterry_hero_count_A')
        self.__loterry_hero_tips_A = None
        self.clear_loterry_hero_tips_A()
        pass
    cdef public int __loterry_hero_count_B
    property loterry_hero_count_B:
        def __get__(self):
            return self.__loterry_hero_count_B
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_count_B:
                    self.__loterry_hero_count_B = value
                    if self._initialized:
                        self.touch_loterry_hero_count_B()

    cpdef touch_loterry_hero_count_B(self):
        self.dirty_fields.add('loterry_hero_count_B')
        self.__loterry_hero_tips_B = None
        self.clear_loterry_hero_tips_B()
        pass
    cdef public int __loterry_hero_count_C
    property loterry_hero_count_C:
        def __get__(self):
            return self.__loterry_hero_count_C
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_count_C:
                    self.__loterry_hero_count_C = value
                    if self._initialized:
                        self.touch_loterry_hero_count_C()

    cpdef touch_loterry_hero_count_C(self):
        self.dirty_fields.add('loterry_hero_count_C')
        self.__loterry_hero_tips_C = None
        self.clear_loterry_hero_tips_C()
        pass
    cdef public object __loterry_hero_gold_first_A
    property loterry_hero_gold_first_A:
        def __get__(self):
            return self.__loterry_hero_gold_first_A
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__loterry_hero_gold_first_A:
                    self.__loterry_hero_gold_first_A = value
                    if self._initialized:
                        self.touch_loterry_hero_gold_first_A()

    cpdef touch_loterry_hero_gold_first_A(self):
        self.dirty_fields.add('loterry_hero_gold_first_A')
        pass
    cdef public object __loterry_hero_gold_first_B
    property loterry_hero_gold_first_B:
        def __get__(self):
            return self.__loterry_hero_gold_first_B
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__loterry_hero_gold_first_B:
                    self.__loterry_hero_gold_first_B = value
                    if self._initialized:
                        self.touch_loterry_hero_gold_first_B()

    cpdef touch_loterry_hero_gold_first_B(self):
        self.dirty_fields.add('loterry_hero_gold_first_B')
        pass
    cdef public object __loterry_hero_gold_first_C
    property loterry_hero_gold_first_C:
        def __get__(self):
            return self.__loterry_hero_gold_first_C
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__loterry_hero_gold_first_C:
                    self.__loterry_hero_gold_first_C = value
                    if self._initialized:
                        self.touch_loterry_hero_gold_first_C()

    cpdef touch_loterry_hero_gold_first_C(self):
        self.dirty_fields.add('loterry_hero_gold_first_C')
        pass
    cdef public int __loterry_hero_used_free_count_A_ts
    property loterry_hero_used_free_count_A_ts:
        def __get__(self):
            return self.__loterry_hero_used_free_count_A_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_used_free_count_A_ts:
                    self.__loterry_hero_used_free_count_A_ts = value
                    if self._initialized:
                        self.touch_loterry_hero_used_free_count_A_ts()

    cpdef touch_loterry_hero_used_free_count_A_ts(self):
        self.dirty_fields.add('loterry_hero_used_free_count_A_ts')
        pass
    cdef public int __loterry_hero_used_free_count_A
    property loterry_hero_used_free_count_A:
        def __get__(self):
            return self.__loterry_hero_used_free_count_A
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_used_free_count_A:
                    self.__loterry_hero_used_free_count_A = value
                    if self._initialized:
                        self.touch_loterry_hero_used_free_count_A()

    cpdef touch_loterry_hero_used_free_count_A(self):
        self.dirty_fields.add('loterry_hero_used_free_count_A')
        self.__loterry_hero_rest_free_count_A = None
        self.clear_loterry_hero_rest_free_count_A()
        pass
    cdef public int __loterry_hero_used_free_count_B_ts
    property loterry_hero_used_free_count_B_ts:
        def __get__(self):
            return self.__loterry_hero_used_free_count_B_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_used_free_count_B_ts:
                    self.__loterry_hero_used_free_count_B_ts = value
                    if self._initialized:
                        self.touch_loterry_hero_used_free_count_B_ts()

    cpdef touch_loterry_hero_used_free_count_B_ts(self):
        self.dirty_fields.add('loterry_hero_used_free_count_B_ts')
        pass
    cdef public int __loterry_hero_used_free_count_B
    property loterry_hero_used_free_count_B:
        def __get__(self):
            return self.__loterry_hero_used_free_count_B
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_used_free_count_B:
                    self.__loterry_hero_used_free_count_B = value
                    if self._initialized:
                        self.touch_loterry_hero_used_free_count_B()

    cpdef touch_loterry_hero_used_free_count_B(self):
        self.dirty_fields.add('loterry_hero_used_free_count_B')
        self.__loterry_hero_rest_free_count_B = None
        self.clear_loterry_hero_rest_free_count_B()
        pass
    cdef public int __loterry_hero_used_free_count_C_ts
    property loterry_hero_used_free_count_C_ts:
        def __get__(self):
            return self.__loterry_hero_used_free_count_C_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_used_free_count_C_ts:
                    self.__loterry_hero_used_free_count_C_ts = value
                    if self._initialized:
                        self.touch_loterry_hero_used_free_count_C_ts()

    cpdef touch_loterry_hero_used_free_count_C_ts(self):
        self.dirty_fields.add('loterry_hero_used_free_count_C_ts')
        pass
    cdef public int __loterry_hero_used_free_count_C
    property loterry_hero_used_free_count_C:
        def __get__(self):
            return self.__loterry_hero_used_free_count_C
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_used_free_count_C:
                    self.__loterry_hero_used_free_count_C = value
                    if self._initialized:
                        self.touch_loterry_hero_used_free_count_C()

    cpdef touch_loterry_hero_used_free_count_C(self):
        self.dirty_fields.add('loterry_hero_used_free_count_C')
        self.__loterry_hero_rest_free_count_C = None
        self.clear_loterry_hero_rest_free_count_C()
        pass
    cdef public int __loterry_hero_count_2
    property loterry_hero_count_2:
        def __get__(self):
            return self.__loterry_hero_count_2
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_count_2:
                    self.__loterry_hero_count_2 = value
                    if self._initialized:
                        self.touch_loterry_hero_count_2()

    cpdef touch_loterry_hero_count_2(self):
        self.dirty_fields.add('loterry_hero_count_2')
        pass
    cdef public object __loterry_hero_history_3
    property loterry_hero_history_3:
        def __get__(self):
            return self.__loterry_hero_history_3
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'loterry_hero_history_3', self.touch_loterry_hero_history_3)
                if value != self.__loterry_hero_history_3:
                    self.__loterry_hero_history_3 = value
                    if self._initialized:
                        self.touch_loterry_hero_history_3()

    cpdef touch_loterry_hero_history_3(self):
        self.dirty_fields.add('loterry_hero_history_3')
        pass
    cdef public object __loterry_hero_gold_first_4
    property loterry_hero_gold_first_4:
        def __get__(self):
            return self.__loterry_hero_gold_first_4
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__loterry_hero_gold_first_4:
                    self.__loterry_hero_gold_first_4 = value
                    if self._initialized:
                        self.touch_loterry_hero_gold_first_4()

    cpdef touch_loterry_hero_gold_first_4(self):
        self.dirty_fields.add('loterry_hero_gold_first_4')
        pass
    cdef public object __loterry_hero_gold_first_5
    property loterry_hero_gold_first_5:
        def __get__(self):
            return self.__loterry_hero_gold_first_5
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__loterry_hero_gold_first_5:
                    self.__loterry_hero_gold_first_5 = value
                    if self._initialized:
                        self.touch_loterry_hero_gold_first_5()

    cpdef touch_loterry_hero_gold_first_5(self):
        self.dirty_fields.add('loterry_hero_gold_first_5')
        pass
    cdef public object __loterry_hero_gold_first_6
    property loterry_hero_gold_first_6:
        def __get__(self):
            return self.__loterry_hero_gold_first_6
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__loterry_hero_gold_first_6:
                    self.__loterry_hero_gold_first_6 = value
                    if self._initialized:
                        self.touch_loterry_hero_gold_first_6()

    cpdef touch_loterry_hero_gold_first_6(self):
        self.dirty_fields.add('loterry_hero_gold_first_6')
        pass
    cdef public object __loterry_hero_gold_first_7
    property loterry_hero_gold_first_7:
        def __get__(self):
            return self.__loterry_hero_gold_first_7
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__loterry_hero_gold_first_7:
                    self.__loterry_hero_gold_first_7 = value
                    if self._initialized:
                        self.touch_loterry_hero_gold_first_7()

    cpdef touch_loterry_hero_gold_first_7(self):
        self.dirty_fields.add('loterry_hero_gold_first_7')
        pass
    cdef public object __loterry_hero_gold_first_8
    property loterry_hero_gold_first_8:
        def __get__(self):
            return self.__loterry_hero_gold_first_8
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__loterry_hero_gold_first_8:
                    self.__loterry_hero_gold_first_8 = value
                    if self._initialized:
                        self.touch_loterry_hero_gold_first_8()

    cpdef touch_loterry_hero_gold_first_8(self):
        self.dirty_fields.add('loterry_hero_gold_first_8')
        pass
    cdef public int __loterry_hero_cd_D
    property loterry_hero_cd_D:
        def __get__(self):
            return self.__loterry_hero_cd_D
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_cd_D:
                    self.__loterry_hero_cd_D = value
                    if self._initialized:
                        self.touch_loterry_hero_cd_D()

    cpdef touch_loterry_hero_cd_D(self):
        self.dirty_fields.add('loterry_hero_cd_D')
        self.sync_dirty_fields.add('loterry_hero_cd_D')
        pass
    cdef public int __loterry_hero_count_D
    property loterry_hero_count_D:
        def __get__(self):
            return self.__loterry_hero_count_D
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_count_D:
                    self.__loterry_hero_count_D = value
                    if self._initialized:
                        self.touch_loterry_hero_count_D()

    cpdef touch_loterry_hero_count_D(self):
        self.dirty_fields.add('loterry_hero_count_D')
        self.__loterry_hero_tips_D = None
        self.clear_loterry_hero_tips_D()
        pass
    cdef public object __loterry_hero_gold_first_D
    property loterry_hero_gold_first_D:
        def __get__(self):
            return self.__loterry_hero_gold_first_D
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__loterry_hero_gold_first_D:
                    self.__loterry_hero_gold_first_D = value
                    if self._initialized:
                        self.touch_loterry_hero_gold_first_D()

    cpdef touch_loterry_hero_gold_first_D(self):
        self.dirty_fields.add('loterry_hero_gold_first_D')
        pass
    cdef public int __loterry_hero_used_free_count_D_ts
    property loterry_hero_used_free_count_D_ts:
        def __get__(self):
            return self.__loterry_hero_used_free_count_D_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_used_free_count_D_ts:
                    self.__loterry_hero_used_free_count_D_ts = value
                    if self._initialized:
                        self.touch_loterry_hero_used_free_count_D_ts()

    cpdef touch_loterry_hero_used_free_count_D_ts(self):
        self.dirty_fields.add('loterry_hero_used_free_count_D_ts')
        pass
    cdef public int __loterry_hero_used_free_count_D
    property loterry_hero_used_free_count_D:
        def __get__(self):
            return self.__loterry_hero_used_free_count_D
        def __set__(self, value):
                value = int(value)
                if value != self.__loterry_hero_used_free_count_D:
                    self.__loterry_hero_used_free_count_D = value
                    if self._initialized:
                        self.touch_loterry_hero_used_free_count_D()

    cpdef touch_loterry_hero_used_free_count_D(self):
        self.dirty_fields.add('loterry_hero_used_free_count_D')
        self.__loterry_hero_rest_free_count_D = None
        self.clear_loterry_hero_rest_free_count_D()
        pass
    cdef public int __resolvegold_time_ts
    property resolvegold_time_ts:
        def __get__(self):
            return self.__resolvegold_time_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__resolvegold_time_ts:
                    self.__resolvegold_time_ts = value
                    if self._initialized:
                        self.touch_resolvegold_time_ts()

    cpdef touch_resolvegold_time_ts(self):
        self.dirty_fields.add('resolvegold_time_ts')
        pass
    cdef public int __resolvegold_time
    property resolvegold_time:
        def __get__(self):
            return self.__resolvegold_time
        def __set__(self, value):
                value = int(value)
                if value != self.__resolvegold_time:
                    self.__resolvegold_time = value
                    if self._initialized:
                        self.touch_resolvegold_time()

    cpdef touch_resolvegold_time(self):
        self.dirty_fields.add('resolvegold_time')
        pass
    cdef public int __pvpgrad
    property pvpgrad:
        def __get__(self):
            return self.__pvpgrad
        def __set__(self, value):
                value = int(value)
                if value != self.__pvpgrad:
                    self.__pvpgrad = value
                    if self._initialized:
                        self.touch_pvpgrad()

    cpdef touch_pvpgrad(self):
        self.dirty_fields.add('pvpgrad')
        self.sync_dirty_fields.add('pvpgrad')
        pass
    cdef public object __pvpseasonreward
    property pvpseasonreward:
        def __get__(self):
            return self.__pvpseasonreward
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'pvpseasonreward', self.touch_pvpseasonreward)
                if value != self.__pvpseasonreward:
                    self.__pvpseasonreward = value
                    if self._initialized:
                        self.touch_pvpseasonreward()

    cpdef touch_pvpseasonreward(self):
        self.dirty_fields.add('pvpseasonreward')
        self.__pvpseasonrewardreceived = None
        self.clear_pvpseasonrewardreceived()
        pass
    cdef public int __pvpseasoncount
    property pvpseasoncount:
        def __get__(self):
            return self.__pvpseasoncount
        def __set__(self, value):
                value = int(value)
                if value != self.__pvpseasoncount:
                    self.__pvpseasoncount = value
                    if self._initialized:
                        self.touch_pvpseasoncount()

    cpdef touch_pvpseasoncount(self):
        self.dirty_fields.add('pvpseasoncount')
        pass
    cdef public object __pvprankreceiveds
    property pvprankreceiveds:
        def __get__(self):
            return self.__pvprankreceiveds
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'pvprankreceiveds', self.touch_pvprankreceiveds)
                if value != self.__pvprankreceiveds:
                    self.__pvprankreceiveds = value
                    if self._initialized:
                        self.touch_pvprankreceiveds()

    cpdef touch_pvprankreceiveds(self):
        self.dirty_fields.add('pvprankreceiveds')
        pass
    cdef public int __vsCount
    property vsCount:
        def __get__(self):
            return self.__vsCount
        def __set__(self, value):
                value = int(value)
                if value != self.__vsCount:
                    self.__vsCount = value
                    if self._initialized:
                        self.touch_vsCount()

    cpdef touch_vsCount(self):
        self.dirty_fields.add('vsCount')
        pass
    cdef public int __pvplastcleantime
    property pvplastcleantime:
        def __get__(self):
            return self.__pvplastcleantime
        def __set__(self, value):
                value = int(value)
                if value != self.__pvplastcleantime:
                    self.__pvplastcleantime = value
                    if self._initialized:
                        self.touch_pvplastcleantime()

    cpdef touch_pvplastcleantime(self):
        self.dirty_fields.add('pvplastcleantime')
        pass
    cdef public object __pvpopenflag
    property pvpopenflag:
        def __get__(self):
            return self.__pvpopenflag
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__pvpopenflag:
                    self.__pvpopenflag = value
                    if self._initialized:
                        self.touch_pvpopenflag()

    cpdef touch_pvpopenflag(self):
        self.__pvpstarttime = None
        self.__pvpfinaltime = None
        self.__pvpopen = None
        self.clear_pvpstarttime()
        self.clear_pvpfinaltime()
        self.clear_pvpopen()
        pass
    cdef public object __pvprewards
    property pvprewards:
        def __get__(self):
            return self.__pvprewards
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'pvprewards', self.touch_pvprewards)
                if value != self.__pvprewards:
                    self.__pvprewards = value
                    if self._initialized:
                        self.touch_pvprewards()

    cpdef touch_pvprewards(self):
        self.dirty_fields.add('pvprewards')
        pass
    cdef public int __todaybp_ts
    property todaybp_ts:
        def __get__(self):
            return self.__todaybp_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__todaybp_ts:
                    self.__todaybp_ts = value
                    if self._initialized:
                        self.touch_todaybp_ts()

    cpdef touch_todaybp_ts(self):
        self.dirty_fields.add('todaybp_ts')
        pass
    cdef public int __todaybp
    property todaybp:
        def __get__(self):
            return self.__todaybp
        def __set__(self, value):
                value = int(value)
                if value != self.__todaybp:
                    self.__todaybp = value
                    if self._initialized:
                        self.touch_todaybp()

    cpdef touch_todaybp(self):
        self.dirty_fields.add('todaybp')
        self.sync_dirty_fields.add('todaybp')
        pass
    cdef public int __pvprank
    property pvprank:
        def __get__(self):
            return self.__pvprank
        def __set__(self, value):
                value = int(value)
                if value != self.__pvprank:
                    self.__pvprank = value
                    if self._initialized:
                        self.touch_pvprank()

    cpdef touch_pvprank(self):
        self.dirty_fields.add('pvprank')
        self.sync_dirty_fields.add('pvprank')
        pass
    cdef public int __totalbp
    property totalbp:
        def __get__(self):
            return self.__totalbp
        def __set__(self, value):
                value = int(value)
                if value != self.__totalbp:
                    self.__totalbp = value
                    if self._initialized:
                        self.touch_totalbp()

    cpdef touch_totalbp(self):
        self.sync_dirty_fields.add('totalbp')
        pass
    cdef public int __prototypeID
    property prototypeID:
        def __get__(self):
            return self.__prototypeID
        def __set__(self, value):
                value = int(value)
                if value != self.__prototypeID:
                    self.__prototypeID = value
                    if self._initialized:
                        self.touch_prototypeID()

    cpdef touch_prototypeID(self):
        self.dirty_fields.add('prototypeID')
        self.sync_dirty_fields.add('prototypeID')
        pass
    cdef public int __exploredoubletime1
    property exploredoubletime1:
        def __get__(self):
            return self.__exploredoubletime1
        def __set__(self, value):
                value = int(value)
                if value != self.__exploredoubletime1:
                    self.__exploredoubletime1 = value
                    if self._initialized:
                        self.touch_exploredoubletime1()

    cpdef touch_exploredoubletime1(self):
        self.dirty_fields.add('exploredoubletime1')
        self.sync_dirty_fields.add('exploredoubletime1')
        pass
    cdef public int __exploredoubletime2
    property exploredoubletime2:
        def __get__(self):
            return self.__exploredoubletime2
        def __set__(self, value):
                value = int(value)
                if value != self.__exploredoubletime2:
                    self.__exploredoubletime2 = value
                    if self._initialized:
                        self.touch_exploredoubletime2()

    cpdef touch_exploredoubletime2(self):
        self.dirty_fields.add('exploredoubletime2')
        self.sync_dirty_fields.add('exploredoubletime2')
        pass
    cdef public int __exploredoubletime3
    property exploredoubletime3:
        def __get__(self):
            return self.__exploredoubletime3
        def __set__(self, value):
                value = int(value)
                if value != self.__exploredoubletime3:
                    self.__exploredoubletime3 = value
                    if self._initialized:
                        self.touch_exploredoubletime3()

    cpdef touch_exploredoubletime3(self):
        self.dirty_fields.add('exploredoubletime3')
        self.sync_dirty_fields.add('exploredoubletime3')
        pass
    cdef public int __get_serialloginreward
    property get_serialloginreward:
        def __get__(self):
            return self.__get_serialloginreward
        def __set__(self, value):
                value = int(value)
                if value != self.__get_serialloginreward:
                    self.__get_serialloginreward = value
                    if self._initialized:
                        self.touch_get_serialloginreward()

    cpdef touch_get_serialloginreward(self):
        self.dirty_fields.add('get_serialloginreward')
        pass
    cdef public object __offline_attrs
    property offline_attrs:
        def __get__(self):
            return self.__offline_attrs
        def __set__(self, value):
                value = ListContainer(value)
                value.init_entity(self, 'offline_attrs', self.touch_offline_attrs)
                if value != self.__offline_attrs:
                    self.__offline_attrs = value
                    if self._initialized:
                        self.touch_offline_attrs()

    cpdef touch_offline_attrs(self):
        self.dirty_fields.add('offline_attrs')
        pass
    cdef public object __lastlogout
    property lastlogout:
        def __get__(self):
            return self.__lastlogout
        def __set__(self, value):
                value = value
                if value != self.__lastlogout:
                    self.__lastlogout = value
                    if self._initialized:
                        self.touch_lastlogout()

    cpdef touch_lastlogout(self):
        self.dirty_fields.add('lastlogout')
        pass
    cdef public object __offlinemail_set
    property offlinemail_set:
        def __get__(self):
            return self.__offlinemail_set
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'offlinemail_set', self.touch_offlinemail_set)
                if value != self.__offlinemail_set:
                    self.__offlinemail_set = value
                    if self._initialized:
                        self.touch_offlinemail_set()

    cpdef touch_offlinemail_set(self):
        self.dirty_fields.add('offlinemail_set')
        pass
    cdef public object __fac_offlinemail_set
    property fac_offlinemail_set:
        def __get__(self):
            return self.__fac_offlinemail_set
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'fac_offlinemail_set', self.touch_fac_offlinemail_set)
                if value != self.__fac_offlinemail_set:
                    self.__fac_offlinemail_set = value
                    if self._initialized:
                        self.touch_fac_offlinemail_set()

    cpdef touch_fac_offlinemail_set(self):
        self.dirty_fields.add('fac_offlinemail_set')
        pass
    cdef public int __worldID
    property worldID:
        def __get__(self):
            return self.__worldID
        def __set__(self, value):
                value = int(value)
                if value != self.__worldID:
                    self.__worldID = value
                    if self._initialized:
                        self.touch_worldID()

    cpdef touch_worldID(self):
        self.dirty_fields.add('worldID')
        pass
    cdef public unicode __faction_name
    property faction_name:
        def __get__(self):
            return self.__faction_name
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__faction_name:
                    self.__faction_name = value
                    if self._initialized:
                        self.touch_faction_name()

    cpdef touch_faction_name(self):
        self.dirty_fields.add('faction_name')
        self.sync_dirty_fields.add('faction_name')
        pass
    cdef public int __faction_level
    property faction_level:
        def __get__(self):
            return self.__faction_level
        def __set__(self, value):
                value = int(value)
                if value != self.__faction_level:
                    self.__faction_level = value
                    if self._initialized:
                        self.touch_faction_level()

    cpdef touch_faction_level(self):
        self.dirty_fields.add('faction_level')
        self.sync_dirty_fields.add('faction_level')
        self.__faction_level_rewards_count = None
        self.clear_faction_level_rewards_count()
        pass
    cdef public object __faction_is_leader
    property faction_is_leader:
        def __get__(self):
            return self.__faction_is_leader
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__faction_is_leader:
                    self.__faction_is_leader = value
                    if self._initialized:
                        self.touch_faction_is_leader()

    cpdef touch_faction_is_leader(self):
        self.dirty_fields.add('faction_is_leader')
        self.sync_dirty_fields.add('faction_is_leader')
        pass
    cdef public int __faction_level_rewards_received_ts
    property faction_level_rewards_received_ts:
        def __get__(self):
            return self.__faction_level_rewards_received_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__faction_level_rewards_received_ts:
                    self.__faction_level_rewards_received_ts = value
                    if self._initialized:
                        self.touch_faction_level_rewards_received_ts()

    cpdef touch_faction_level_rewards_received_ts(self):
        self.dirty_fields.add('faction_level_rewards_received_ts')
        pass
    cdef public object __faction_level_rewards_received
    property faction_level_rewards_received:
        def __get__(self):
            return self.__faction_level_rewards_received
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'faction_level_rewards_received', self.touch_faction_level_rewards_received)
                if value != self.__faction_level_rewards_received:
                    self.__faction_level_rewards_received = value
                    if self._initialized:
                        self.touch_faction_level_rewards_received()

    cpdef touch_faction_level_rewards_received(self):
        self.dirty_fields.add('faction_level_rewards_received')
        self.__faction_level_rewards_count = None
        self.clear_faction_level_rewards_count()
        pass
    cdef public int __faction_taskID_ts
    property faction_taskID_ts:
        def __get__(self):
            return self.__faction_taskID_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__faction_taskID_ts:
                    self.__faction_taskID_ts = value
                    if self._initialized:
                        self.touch_faction_taskID_ts()

    cpdef touch_faction_taskID_ts(self):
        self.dirty_fields.add('faction_taskID_ts')
        pass
    cdef public int __faction_taskID
    property faction_taskID:
        def __get__(self):
            return self.__faction_taskID
        def __set__(self, value):
                value = int(value)
                if value != self.__faction_taskID:
                    self.__faction_taskID = value
                    if self._initialized:
                        self.touch_faction_taskID()

    cpdef touch_faction_taskID(self):
        self.dirty_fields.add('faction_taskID')
        self.sync_dirty_fields.add('faction_taskID')
        pass
    cdef public int __faction_task_done_ts
    property faction_task_done_ts:
        def __get__(self):
            return self.__faction_task_done_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__faction_task_done_ts:
                    self.__faction_task_done_ts = value
                    if self._initialized:
                        self.touch_faction_task_done_ts()

    cpdef touch_faction_task_done_ts(self):
        self.dirty_fields.add('faction_task_done_ts')
        pass
    cdef public object __faction_task_done
    property faction_task_done:
        def __get__(self):
            return self.__faction_task_done
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__faction_task_done:
                    self.__faction_task_done = value
                    if self._initialized:
                        self.touch_faction_task_done()

    cpdef touch_faction_task_done(self):
        self.dirty_fields.add('faction_task_done')
        self.sync_dirty_fields.add('faction_task_done')
        pass
    cdef public int __last_factionID
    property last_factionID:
        def __get__(self):
            return self.__last_factionID
        def __set__(self, value):
                value = int(value)
                if value != self.__last_factionID:
                    self.__last_factionID = value
                    if self._initialized:
                        self.touch_last_factionID()

    cpdef touch_last_factionID(self):
        self.dirty_fields.add('last_factionID')
        self.sync_dirty_fields.add('last_factionID')
        pass
    cdef public object __applyFactions
    property applyFactions:
        def __get__(self):
            return self.__applyFactions
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'applyFactions', self.touch_applyFactions)
                if value != self.__applyFactions:
                    self.__applyFactions = value
                    if self._initialized:
                        self.touch_applyFactions()

    cpdef touch_applyFactions(self):
        self.dirty_fields.add('applyFactions')
        pass
    cdef public int __joinFactionTime
    property joinFactionTime:
        def __get__(self):
            return self.__joinFactionTime
        def __set__(self, value):
                value = int(value)
                if value != self.__joinFactionTime:
                    self.__joinFactionTime = value
                    if self._initialized:
                        self.touch_joinFactionTime()

    cpdef touch_joinFactionTime(self):
        self.dirty_fields.add('joinFactionTime')
        pass
    cdef public int __factionID
    property factionID:
        def __get__(self):
            return self.__factionID
        def __set__(self, value):
                value = int(value)
                if value != self.__factionID:
                    self.__factionID = value
                    if self._initialized:
                        self.touch_factionID()

    cpdef touch_factionID(self):
        self.dirty_fields.add('factionID')
        self.sync_dirty_fields.add('factionID')
        pass
    cdef public object __inviteFactionSet
    property inviteFactionSet:
        def __get__(self):
            return self.__inviteFactionSet
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'inviteFactionSet', self.touch_inviteFactionSet)
                if value != self.__inviteFactionSet:
                    self.__inviteFactionSet = value
                    if self._initialized:
                        self.touch_inviteFactionSet()

    cpdef touch_inviteFactionSet(self):
        self.dirty_fields.add('inviteFactionSet')
        self.__inviteFactionCount = None
        self.clear_inviteFactionCount()
        pass
    cdef public object __applyMemberSet
    property applyMemberSet:
        def __get__(self):
            return self.__applyMemberSet
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'applyMemberSet', self.touch_applyMemberSet)
                if value != self.__applyMemberSet:
                    self.__applyMemberSet = value
                    if self._initialized:
                        self.touch_applyMemberSet()

    cpdef touch_applyMemberSet(self):
        self.__applyMemberCount = None
        self.clear_applyMemberCount()
        pass
    cdef public int __strengthen_df_level
    property strengthen_df_level:
        def __get__(self):
            return self.__strengthen_df_level
        def __set__(self, value):
                value = int(value)
                if value != self.__strengthen_df_level:
                    self.__strengthen_df_level = value
                    if self._initialized:
                        self.touch_strengthen_df_level()

    cpdef touch_strengthen_df_level(self):
        self.dirty_fields.add('strengthen_df_level')
        self.sync_dirty_fields.add('strengthen_df_level')
        self.__power = None
        self.__factionDEF = None
        self.__faction_power = None
        self.clear_power()
        self.clear_factionDEF()
        self.clear_faction_power()
        pass
    cdef public int __strengthen_hp_level
    property strengthen_hp_level:
        def __get__(self):
            return self.__strengthen_hp_level
        def __set__(self, value):
                value = int(value)
                if value != self.__strengthen_hp_level:
                    self.__strengthen_hp_level = value
                    if self._initialized:
                        self.touch_strengthen_hp_level()

    cpdef touch_strengthen_hp_level(self):
        self.dirty_fields.add('strengthen_hp_level')
        self.sync_dirty_fields.add('strengthen_hp_level')
        self.__power = None
        self.__factionHP = None
        self.__faction_power = None
        self.clear_power()
        self.clear_factionHP()
        self.clear_faction_power()
        pass
    cdef public int __strengthen_at_level
    property strengthen_at_level:
        def __get__(self):
            return self.__strengthen_at_level
        def __set__(self, value):
                value = int(value)
                if value != self.__strengthen_at_level:
                    self.__strengthen_at_level = value
                    if self._initialized:
                        self.touch_strengthen_at_level()

    cpdef touch_strengthen_at_level(self):
        self.dirty_fields.add('strengthen_at_level')
        self.sync_dirty_fields.add('strengthen_at_level')
        self.__power = None
        self.__factionATK = None
        self.__faction_power = None
        self.clear_power()
        self.clear_factionATK()
        self.clear_faction_power()
        pass
    cdef public int __strengthen_ct_level
    property strengthen_ct_level:
        def __get__(self):
            return self.__strengthen_ct_level
        def __set__(self, value):
                value = int(value)
                if value != self.__strengthen_ct_level:
                    self.__strengthen_ct_level = value
                    if self._initialized:
                        self.touch_strengthen_ct_level()

    cpdef touch_strengthen_ct_level(self):
        self.dirty_fields.add('strengthen_ct_level')
        self.sync_dirty_fields.add('strengthen_ct_level')
        self.__power = None
        self.__factionCRI = None
        self.__faction_power = None
        self.clear_power()
        self.clear_factionCRI()
        self.clear_faction_power()
        pass
    cdef public int __strengthen_hp_max_level
    property strengthen_hp_max_level:
        def __get__(self):
            return self.__strengthen_hp_max_level
        def __set__(self, value):
                value = int(value)
                if value != self.__strengthen_hp_max_level:
                    self.__strengthen_hp_max_level = value
                    if self._initialized:
                        self.touch_strengthen_hp_max_level()

    cpdef touch_strengthen_hp_max_level(self):
        self.dirty_fields.add('strengthen_hp_max_level')
        pass
    cdef public int __strengthen_at_max_level
    property strengthen_at_max_level:
        def __get__(self):
            return self.__strengthen_at_max_level
        def __set__(self, value):
                value = int(value)
                if value != self.__strengthen_at_max_level:
                    self.__strengthen_at_max_level = value
                    if self._initialized:
                        self.touch_strengthen_at_max_level()

    cpdef touch_strengthen_at_max_level(self):
        self.dirty_fields.add('strengthen_at_max_level')
        pass
    cdef public int __strengthen_ct_max_level
    property strengthen_ct_max_level:
        def __get__(self):
            return self.__strengthen_ct_max_level
        def __set__(self, value):
                value = int(value)
                if value != self.__strengthen_ct_max_level:
                    self.__strengthen_ct_max_level = value
                    if self._initialized:
                        self.touch_strengthen_ct_max_level()

    cpdef touch_strengthen_ct_max_level(self):
        self.dirty_fields.add('strengthen_ct_max_level')
        pass
    cdef public int __strengthen_df_max_level
    property strengthen_df_max_level:
        def __get__(self):
            return self.__strengthen_df_max_level
        def __set__(self, value):
                value = int(value)
                if value != self.__strengthen_df_max_level:
                    self.__strengthen_df_max_level = value
                    if self._initialized:
                        self.touch_strengthen_df_max_level()

    cpdef touch_strengthen_df_max_level(self):
        self.dirty_fields.add('strengthen_df_max_level')
        pass
    cdef public int __buy_sp_used_count_ts
    property buy_sp_used_count_ts:
        def __get__(self):
            return self.__buy_sp_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__buy_sp_used_count_ts:
                    self.__buy_sp_used_count_ts = value
                    if self._initialized:
                        self.touch_buy_sp_used_count_ts()

    cpdef touch_buy_sp_used_count_ts(self):
        self.dirty_fields.add('buy_sp_used_count_ts')
        pass
    cdef public int __buy_sp_used_count
    property buy_sp_used_count:
        def __get__(self):
            return self.__buy_sp_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__buy_sp_used_count:
                    self.__buy_sp_used_count = value
                    if self._initialized:
                        self.touch_buy_sp_used_count()

    cpdef touch_buy_sp_used_count(self):
        self.dirty_fields.add('buy_sp_used_count')
        self.__buy_sp_rest_count = None
        self.__buy_sp_cost = None
        self.clear_buy_sp_rest_count()
        self.clear_buy_sp_cost()
        pass
    cdef public unicode __featureCode
    property featureCode:
        def __get__(self):
            return self.__featureCode
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__featureCode:
                    self.__featureCode = value
                    if self._initialized:
                        self.touch_featureCode()

    cpdef touch_featureCode(self):
        self.dirty_fields.add('featureCode')
        pass
    cdef public unicode __clientIP
    property clientIP:
        def __get__(self):
            return self.__clientIP
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__clientIP:
                    self.__clientIP = value
                    if self._initialized:
                        self.touch_clientIP()

    cpdef touch_clientIP(self):
        self.dirty_fields.add('clientIP')
        pass
    cdef public unicode __clientVersion
    property clientVersion:
        def __get__(self):
            return self.__clientVersion
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__clientVersion:
                    self.__clientVersion = value
                    if self._initialized:
                        self.touch_clientVersion()

    cpdef touch_clientVersion(self):
        self.dirty_fields.add('clientVersion')
        pass
    cdef public object __petPatchs
    property petPatchs:
        def __get__(self):
            return self.__petPatchs
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_petPatchs(self):
        pass
    cdef public object __petpatchdirty
    property petpatchdirty:
        def __get__(self):
            return self.__petpatchdirty
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'petpatchdirty', self.touch_petpatchdirty)
                if value != self.__petpatchdirty:
                    self.__petpatchdirty = value
                    if self._initialized:
                        self.touch_petpatchdirty()

    cpdef touch_petpatchdirty(self):
        self.dirty_fields.add('petpatchdirty')
        pass
    cdef public int __golden_sp
    property golden_sp:
        def __get__(self):
            return self.__golden_sp
        def __set__(self, value):
                value = int(value)
                if value != self.__golden_sp:
                    self.__golden_sp = value
                    if self._initialized:
                        self.touch_golden_sp()

    cpdef touch_golden_sp(self):
        self.dirty_fields.add('golden_sp')
        pass
    cdef public int __silver_sp
    property silver_sp:
        def __get__(self):
            return self.__silver_sp
        def __set__(self, value):
                value = int(value)
                if value != self.__silver_sp:
                    self.__silver_sp = value
                    if self._initialized:
                        self.touch_silver_sp()

    cpdef touch_silver_sp(self):
        self.dirty_fields.add('silver_sp')
        pass
    cdef public int __retry_fb_count
    property retry_fb_count:
        def __get__(self):
            return self.__retry_fb_count
        def __set__(self, value):
                value = int(value)
                if value != self.__retry_fb_count:
                    self.__retry_fb_count = value
                    if self._initialized:
                        self.touch_retry_fb_count()

    cpdef touch_retry_fb_count(self):
        self.dirty_fields.add('retry_fb_count')
        pass
    cdef public int __consume_count
    property consume_count:
        def __get__(self):
            return self.__consume_count
        def __set__(self, value):
                value = int(value)
                if value != self.__consume_count:
                    self.__consume_count = value
                    if self._initialized:
                        self.touch_consume_count()

    cpdef touch_consume_count(self):
        self.dirty_fields.add('consume_count')
        pass
    cdef public int __lottery_count
    property lottery_count:
        def __get__(self):
            return self.__lottery_count
        def __set__(self, value):
                value = int(value)
                if value != self.__lottery_count:
                    self.__lottery_count = value
                    if self._initialized:
                        self.touch_lottery_count()

    cpdef touch_lottery_count(self):
        self.dirty_fields.add('lottery_count')
        pass
    cdef public int __lottery_gold_accumulating
    property lottery_gold_accumulating:
        def __get__(self):
            return self.__lottery_gold_accumulating
        def __set__(self, value):
                value = int(value)
                if value != self.__lottery_gold_accumulating:
                    self.__lottery_gold_accumulating = value
                    if self._initialized:
                        self.touch_lottery_gold_accumulating()

    cpdef touch_lottery_gold_accumulating(self):
        self.dirty_fields.add('lottery_gold_accumulating')
        self.__loterry_hero_tips_C = None
        self.clear_loterry_hero_tips_C()
        pass
    cdef public int __lottery_money_accumulating
    property lottery_money_accumulating:
        def __get__(self):
            return self.__lottery_money_accumulating
        def __set__(self, value):
                value = int(value)
                if value != self.__lottery_money_accumulating:
                    self.__lottery_money_accumulating = value
                    if self._initialized:
                        self.touch_lottery_money_accumulating()

    cpdef touch_lottery_money_accumulating(self):
        self.dirty_fields.add('lottery_money_accumulating')
        self.__loterry_hero_tips_A = None
        self.clear_loterry_hero_tips_A()
        pass
    cdef public int __lottery_gold_accumulating10
    property lottery_gold_accumulating10:
        def __get__(self):
            return self.__lottery_gold_accumulating10
        def __set__(self, value):
                value = int(value)
                if value != self.__lottery_gold_accumulating10:
                    self.__lottery_gold_accumulating10 = value
                    if self._initialized:
                        self.touch_lottery_gold_accumulating10()

    cpdef touch_lottery_gold_accumulating10(self):
        self.dirty_fields.add('lottery_gold_accumulating10')
        self.__loterry_hero_tips_D = None
        self.clear_loterry_hero_tips_D()
        pass
    cdef public int __lottery_money_accumulating10
    property lottery_money_accumulating10:
        def __get__(self):
            return self.__lottery_money_accumulating10
        def __set__(self, value):
                value = int(value)
                if value != self.__lottery_money_accumulating10:
                    self.__lottery_money_accumulating10 = value
                    if self._initialized:
                        self.touch_lottery_money_accumulating10()

    cpdef touch_lottery_money_accumulating10(self):
        self.dirty_fields.add('lottery_money_accumulating10')
        self.__loterry_hero_tips_B = None
        self.clear_loterry_hero_tips_B()
        pass
    cdef public int __vip_offline
    property vip_offline:
        def __get__(self):
            return self.__vip_offline
        def __set__(self, value):
                value = int(value)
                if value != self.__vip_offline:
                    self.__vip_offline = value
                    if self._initialized:
                        self.touch_vip_offline()

    cpdef touch_vip_offline(self):
        self.dirty_fields.add('vip_offline')
        pass
    cdef public object __tasks
    property tasks:
        def __get__(self):
            return self.__tasks
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_tasks(self):
        self.__taskrewardsdone14 = None
        self.clear_taskrewardsdone14()
        pass
    cdef public object __taskrewards
    property taskrewards:
        def __get__(self):
            return self.__taskrewards
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'taskrewards', self.touch_taskrewards)
                if value != self.__taskrewards:
                    self.__taskrewards = value
                    if self._initialized:
                        self.touch_taskrewards()

    cpdef touch_taskrewards(self):
        self.dirty_fields.add('taskrewards')
        self.__taskrewardscount1 = None
        self.__taskrewardscount2 = None
        self.__taskrewardscount3 = None
        self.__taskrewardscount4 = None
        self.__taskrewardscountnew = None
        self.__taskrewardscount5 = None
        self.__task_noob_flag = None
        self.__task_noob_undo = None
        self.__taskrewardscount6 = None
        self.__taskrewardscount7 = None
        self.__taskrewardscountsubtype1 = None
        self.__taskrewardscountsubtype2 = None
        self.__taskrewardscountsubtype3 = None
        self.__taskrewardscountsubtype4 = None
        self.__taskrewardscount12 = None
        self.__taskrewardscount13 = None
        self.__taskrewardscount14 = None
        self.__taskrewardsdone14 = None
        self.__beg_flag = None
        self.clear_taskrewardscount1()
        self.clear_taskrewardscount2()
        self.clear_taskrewardscount3()
        self.clear_taskrewardscount4()
        self.clear_taskrewardscountnew()
        self.clear_taskrewardscount5()
        self.clear_task_noob_flag()
        self.clear_task_noob_undo()
        self.clear_taskrewardscount6()
        self.clear_taskrewardscount7()
        self.clear_taskrewardscountsubtype1()
        self.clear_taskrewardscountsubtype2()
        self.clear_taskrewardscountsubtype3()
        self.clear_taskrewardscountsubtype4()
        self.clear_taskrewardscount12()
        self.clear_taskrewardscount13()
        self.clear_taskrewardscount14()
        self.clear_taskrewardsdone14()
        self.clear_beg_flag()
        pass
    cdef public int __task_max_patch_sign_up_count
    property task_max_patch_sign_up_count:
        def __get__(self):
            return self.__task_max_patch_sign_up_count
        def __set__(self, value):
                value = int(value)
                if value != self.__task_max_patch_sign_up_count:
                    self.__task_max_patch_sign_up_count = value
                    if self._initialized:
                        self.touch_task_max_patch_sign_up_count()

    cpdef touch_task_max_patch_sign_up_count(self):
        self.dirty_fields.add('task_max_patch_sign_up_count')
        self.__task_rest_patch_sign_up_count = None
        self.clear_task_rest_patch_sign_up_count()
        pass
    cdef public int __task_used_patch_sign_up_count
    property task_used_patch_sign_up_count:
        def __get__(self):
            return self.__task_used_patch_sign_up_count
        def __set__(self, value):
                value = int(value)
                if value != self.__task_used_patch_sign_up_count:
                    self.__task_used_patch_sign_up_count = value
                    if self._initialized:
                        self.touch_task_used_patch_sign_up_count()

    cpdef touch_task_used_patch_sign_up_count(self):
        self.dirty_fields.add('task_used_patch_sign_up_count')
        self.__task_rest_patch_sign_up_count = None
        self.clear_task_rest_patch_sign_up_count()
        pass
    cdef public int __task_last_sign_up_time
    property task_last_sign_up_time:
        def __get__(self):
            return self.__task_last_sign_up_time
        def __set__(self, value):
                value = int(value)
                if value != self.__task_last_sign_up_time:
                    self.__task_last_sign_up_time = value
                    if self._initialized:
                        self.touch_task_last_sign_up_time()

    cpdef touch_task_last_sign_up_time(self):
        self.dirty_fields.add('task_last_sign_up_time')
        self.__task_today_is_sign_up = None
        self.clear_task_today_is_sign_up()
        pass
    cdef public int __task_is_calc_sign_up_ts
    property task_is_calc_sign_up_ts:
        def __get__(self):
            return self.__task_is_calc_sign_up_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__task_is_calc_sign_up_ts:
                    self.__task_is_calc_sign_up_ts = value
                    if self._initialized:
                        self.touch_task_is_calc_sign_up_ts()

    cpdef touch_task_is_calc_sign_up_ts(self):
        self.dirty_fields.add('task_is_calc_sign_up_ts')
        pass
    cdef public object __task_is_calc_sign_up
    property task_is_calc_sign_up:
        def __get__(self):
            return self.__task_is_calc_sign_up
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__task_is_calc_sign_up:
                    self.__task_is_calc_sign_up = value
                    if self._initialized:
                        self.touch_task_is_calc_sign_up()

    cpdef touch_task_is_calc_sign_up(self):
        self.dirty_fields.add('task_is_calc_sign_up')
        pass
    cdef public int __task_sp_daily_receiveds_ts
    property task_sp_daily_receiveds_ts:
        def __get__(self):
            return self.__task_sp_daily_receiveds_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__task_sp_daily_receiveds_ts:
                    self.__task_sp_daily_receiveds_ts = value
                    if self._initialized:
                        self.touch_task_sp_daily_receiveds_ts()

    cpdef touch_task_sp_daily_receiveds_ts(self):
        self.dirty_fields.add('task_sp_daily_receiveds_ts')
        pass
    cdef public object __task_sp_daily_receiveds
    property task_sp_daily_receiveds:
        def __get__(self):
            return self.__task_sp_daily_receiveds
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'task_sp_daily_receiveds', self.touch_task_sp_daily_receiveds)
                if value != self.__task_sp_daily_receiveds:
                    self.__task_sp_daily_receiveds = value
                    if self._initialized:
                        self.touch_task_sp_daily_receiveds()

    cpdef touch_task_sp_daily_receiveds(self):
        self.dirty_fields.add('task_sp_daily_receiveds')
        self.__taskrewardscount1 = None
        self.__beg_flag = None
        self.clear_taskrewardscount1()
        self.clear_beg_flag()
        pass
    cdef public int __monthly_card_30
    property monthly_card_30:
        def __get__(self):
            return self.__monthly_card_30
        def __set__(self, value):
                value = int(value)
                if value != self.__monthly_card_30:
                    self.__monthly_card_30 = value
                    if self._initialized:
                        self.touch_monthly_card_30()

    cpdef touch_monthly_card_30(self):
        self.dirty_fields.add('monthly_card_30')
        pass
    cdef public int __reset_recharges_seq
    property reset_recharges_seq:
        def __get__(self):
            return self.__reset_recharges_seq
        def __set__(self, value):
                value = int(value)
                if value != self.__reset_recharges_seq:
                    self.__reset_recharges_seq = value
                    if self._initialized:
                        self.touch_reset_recharges_seq()

    cpdef touch_reset_recharges_seq(self):
        self.dirty_fields.add('reset_recharges_seq')
        pass
    cdef public object __bought_recharges
    property bought_recharges:
        def __get__(self):
            return self.__bought_recharges
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'bought_recharges', self.touch_bought_recharges)
                if value != self.__bought_recharges:
                    self.__bought_recharges = value
                    if self._initialized:
                        self.touch_bought_recharges()

    cpdef touch_bought_recharges(self):
        self.dirty_fields.add('bought_recharges')
        self.__first_recharge_recv = None
        self.clear_first_recharge_recv()
        pass
    cdef public object __offline_recharges
    property offline_recharges:
        def __get__(self):
            return self.__offline_recharges
        def __set__(self, value):
                value = ListContainer(value)
                value.init_entity(self, 'offline_recharges', self.touch_offline_recharges)
                if value != self.__offline_recharges:
                    self.__offline_recharges = value
                    if self._initialized:
                        self.touch_offline_recharges()

    cpdef touch_offline_recharges(self):
        self.dirty_fields.add('offline_recharges')
        pass
    cdef public int __limited_packs_used_count
    property limited_packs_used_count:
        def __get__(self):
            return self.__limited_packs_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__limited_packs_used_count:
                    self.__limited_packs_used_count = value
                    if self._initialized:
                        self.touch_limited_packs_used_count()

    cpdef touch_limited_packs_used_count(self):
        self.dirty_fields.add('limited_packs_used_count')
        self.__limited_packs_rest_count = None
        self.clear_limited_packs_rest_count()
        pass
    cdef public int __limited_packs_last_time
    property limited_packs_last_time:
        def __get__(self):
            return self.__limited_packs_last_time
        def __set__(self, value):
                value = int(value)
                if value != self.__limited_packs_last_time:
                    self.__limited_packs_last_time = value
                    if self._initialized:
                        self.touch_limited_packs_last_time()

    cpdef touch_limited_packs_last_time(self):
        self.dirty_fields.add('limited_packs_last_time')
        pass
    cdef public int __timelimited_packs_last_time
    property timelimited_packs_last_time:
        def __get__(self):
            return self.__timelimited_packs_last_time
        def __set__(self, value):
                value = int(value)
                if value != self.__timelimited_packs_last_time:
                    self.__timelimited_packs_last_time = value
                    if self._initialized:
                        self.touch_timelimited_packs_last_time()

    cpdef touch_timelimited_packs_last_time(self):
        self.dirty_fields.add('timelimited_packs_last_time')
        self.__timelimited_packs_rest_count = None
        self.clear_timelimited_packs_rest_count()
        pass
    cdef public int __trigger_packs_buy_count_ts
    property trigger_packs_buy_count_ts:
        def __get__(self):
            return self.__trigger_packs_buy_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__trigger_packs_buy_count_ts:
                    self.__trigger_packs_buy_count_ts = value
                    if self._initialized:
                        self.touch_trigger_packs_buy_count_ts()

    cpdef touch_trigger_packs_buy_count_ts(self):
        self.dirty_fields.add('trigger_packs_buy_count_ts')
        pass
    cdef public int __trigger_packs_buy_count
    property trigger_packs_buy_count:
        def __get__(self):
            return self.__trigger_packs_buy_count
        def __set__(self, value):
                value = int(value)
                if value != self.__trigger_packs_buy_count:
                    self.__trigger_packs_buy_count = value
                    if self._initialized:
                        self.touch_trigger_packs_buy_count()

    cpdef touch_trigger_packs_buy_count(self):
        self.dirty_fields.add('trigger_packs_buy_count')
        pass
    cdef public int __trigger_packs_flag_ts
    property trigger_packs_flag_ts:
        def __get__(self):
            return self.__trigger_packs_flag_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__trigger_packs_flag_ts:
                    self.__trigger_packs_flag_ts = value
                    if self._initialized:
                        self.touch_trigger_packs_flag_ts()

    cpdef touch_trigger_packs_flag_ts(self):
        self.dirty_fields.add('trigger_packs_flag_ts')
        pass
    cdef public object __trigger_packs_flag
    property trigger_packs_flag:
        def __get__(self):
            return self.__trigger_packs_flag
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__trigger_packs_flag:
                    self.__trigger_packs_flag = value
                    if self._initialized:
                        self.touch_trigger_packs_flag()

    cpdef touch_trigger_packs_flag(self):
        self.dirty_fields.add('trigger_packs_flag')
        pass
    cdef public int __totallogin_after_guide
    property totallogin_after_guide:
        def __get__(self):
            return self.__totallogin_after_guide
        def __set__(self, value):
                value = int(value)
                if value != self.__totallogin_after_guide:
                    self.__totallogin_after_guide = value
                    if self._initialized:
                        self.touch_totallogin_after_guide()

    cpdef touch_totallogin_after_guide(self):
        self.dirty_fields.add('totallogin_after_guide')
        pass
    cdef public int __seriallogin_after_guide
    property seriallogin_after_guide:
        def __get__(self):
            return self.__seriallogin_after_guide
        def __set__(self, value):
                value = int(value)
                if value != self.__seriallogin_after_guide:
                    self.__seriallogin_after_guide = value
                    if self._initialized:
                        self.touch_seriallogin_after_guide()

    cpdef touch_seriallogin_after_guide(self):
        self.dirty_fields.add('seriallogin_after_guide')
        pass
    cdef public object __first_recharge_flag
    property first_recharge_flag:
        def __get__(self):
            return self.__first_recharge_flag
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__first_recharge_flag:
                    self.__first_recharge_flag = value
                    if self._initialized:
                        self.touch_first_recharge_flag()

    cpdef touch_first_recharge_flag(self):
        self.dirty_fields.add('first_recharge_flag')
        self.sync_dirty_fields.add('first_recharge_flag')
        self.__first_recharge_recv = None
        self.clear_first_recharge_recv()
        pass
    cdef public int __first_recharge_numb
    property first_recharge_numb:
        def __get__(self):
            return self.__first_recharge_numb
        def __set__(self, value):
                value = int(value)
                if value != self.__first_recharge_numb:
                    self.__first_recharge_numb = value
                    if self._initialized:
                        self.touch_first_recharge_numb()

    cpdef touch_first_recharge_numb(self):
        self.dirty_fields.add('first_recharge_numb')
        pass
    cdef public object __first_recharge_patch
    property first_recharge_patch:
        def __get__(self):
            return self.__first_recharge_patch
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__first_recharge_patch:
                    self.__first_recharge_patch = value
                    if self._initialized:
                        self.touch_first_recharge_patch()

    cpdef touch_first_recharge_patch(self):
        self.dirty_fields.add('first_recharge_patch')
        pass
    cdef public int __cleanfb
    property cleanfb:
        def __get__(self):
            return self.__cleanfb
        def __set__(self, value):
                value = int(value)
                if value != self.__cleanfb:
                    self.__cleanfb = value
                    if self._initialized:
                        self.touch_cleanfb()

    cpdef touch_cleanfb(self):
        self.dirty_fields.add('cleanfb')
        self.sync_dirty_fields.add('cleanfb')
        pass
    cdef public object __lineups_defend
    property lineups_defend:
        def __get__(self):
            return self.__lineups_defend
        def __set__(self, value):
                value = ListContainer(value)
                value.init_entity(self, 'lineups_defend', self.touch_lineups_defend)
                if value != self.__lineups_defend:
                    self.__lineups_defend = value
                    if self._initialized:
                        self.touch_lineups_defend()

    cpdef touch_lineups_defend(self):
        self.dirty_fields.add('lineups_defend')
        pass
    cdef public int __on_lineup_defend
    property on_lineup_defend:
        def __get__(self):
            return self.__on_lineup_defend
        def __set__(self, value):
                value = int(value)
                if value != self.__on_lineup_defend:
                    self.__on_lineup_defend = value
                    if self._initialized:
                        self.touch_on_lineup_defend()

    cpdef touch_on_lineup_defend(self):
        self.dirty_fields.add('on_lineup_defend')
        self.sync_dirty_fields.add('on_lineup_defend')
        pass
    cdef public int __borderID
    property borderID:
        def __get__(self):
            return self.__borderID
        def __set__(self, value):
                value = int(value)
                if value != self.__borderID:
                    self.__borderID = value
                    if self._initialized:
                        self.touch_borderID()

    cpdef touch_borderID(self):
        self.dirty_fields.add('borderID')
        self.sync_dirty_fields.add('borderID')
        pass
    cdef public object __rank_detail_cache
    property rank_detail_cache:
        def __get__(self):
            return self.__rank_detail_cache
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'rank_detail_cache', self.touch_rank_detail_cache)
                if value != self.__rank_detail_cache:
                    self.__rank_detail_cache = value
                    if self._initialized:
                        self.touch_rank_detail_cache()

    cpdef touch_rank_detail_cache(self):
        self.dirty_fields.add('rank_detail_cache')
        pass
    cdef public int __rank_count
    property rank_count:
        def __get__(self):
            return self.__rank_count
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_count:
                    self.__rank_count = value
                    if self._initialized:
                        self.touch_rank_count()

    cpdef touch_rank_count(self):
        self.dirty_fields.add('rank_count')
        self.sync_dirty_fields.add('rank_count')
        pass
    cdef public int __rank_active_count
    property rank_active_count:
        def __get__(self):
            return self.__rank_active_count
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_active_count:
                    self.__rank_active_count = value
                    if self._initialized:
                        self.touch_rank_active_count()

    cpdef touch_rank_active_count(self):
        self.dirty_fields.add('rank_active_count')
        self.sync_dirty_fields.add('rank_active_count')
        pass
    cdef public int __rank_active_win_count
    property rank_active_win_count:
        def __get__(self):
            return self.__rank_active_win_count
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_active_win_count:
                    self.__rank_active_win_count = value
                    if self._initialized:
                        self.touch_rank_active_win_count()

    cpdef touch_rank_active_win_count(self):
        self.dirty_fields.add('rank_active_win_count')
        self.sync_dirty_fields.add('rank_active_win_count')
        pass
    cdef public int __rank_win_count
    property rank_win_count:
        def __get__(self):
            return self.__rank_win_count
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_win_count:
                    self.__rank_win_count = value
                    if self._initialized:
                        self.touch_rank_win_count()

    cpdef touch_rank_win_count(self):
        self.dirty_fields.add('rank_win_count')
        self.sync_dirty_fields.add('rank_win_count')
        pass
    cdef public int __rank_free_vs_ts
    property rank_free_vs_ts:
        def __get__(self):
            return self.__rank_free_vs_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_free_vs_ts:
                    self.__rank_free_vs_ts = value
                    if self._initialized:
                        self.touch_rank_free_vs_ts()

    cpdef touch_rank_free_vs_ts(self):
        self.dirty_fields.add('rank_free_vs_ts')
        pass
    cdef public int __rank_free_vs
    property rank_free_vs:
        def __get__(self):
            return self.__rank_free_vs
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_free_vs:
                    self.__rank_free_vs = value
                    if self._initialized:
                        self.touch_rank_free_vs()

    cpdef touch_rank_free_vs(self):
        self.dirty_fields.add('rank_free_vs')
        self.sync_dirty_fields.add('rank_free_vs')
        pass
    cdef public int __rank_cd
    property rank_cd:
        def __get__(self):
            return self.__rank_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_cd:
                    self.__rank_cd = value
                    if self._initialized:
                        self.touch_rank_cd()

    cpdef touch_rank_cd(self):
        self.dirty_fields.add('rank_cd')
        self.sync_dirty_fields.add('rank_cd')
        pass
    cdef public object __rank_history
    property rank_history:
        def __get__(self):
            return self.__rank_history
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_rank_history(self):
        pass
    cdef public object __rank_fight_history
    property rank_fight_history:
        def __get__(self):
            return self.__rank_fight_history
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_rank_fight_history(self):
        pass
    cdef public int __rank_passive_offline_count
    property rank_passive_offline_count:
        def __get__(self):
            return self.__rank_passive_offline_count
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_passive_offline_count:
                    self.__rank_passive_offline_count = value
                    if self._initialized:
                        self.touch_rank_passive_offline_count()

    cpdef touch_rank_passive_offline_count(self):
        self.dirty_fields.add('rank_passive_offline_count')
        self.sync_dirty_fields.add('rank_passive_offline_count')
        pass
    cdef public int __totalbp_on_logout
    property totalbp_on_logout:
        def __get__(self):
            return self.__totalbp_on_logout
        def __set__(self, value):
                value = int(value)
                if value != self.__totalbp_on_logout:
                    self.__totalbp_on_logout = value
                    if self._initialized:
                        self.touch_totalbp_on_logout()

    cpdef touch_totalbp_on_logout(self):
        self.dirty_fields.add('totalbp_on_logout')
        self.sync_dirty_fields.add('totalbp_on_logout')
        pass
    cdef public object __rank_targets
    property rank_targets:
        def __get__(self):
            return self.__rank_targets
        def __set__(self, value):
                value = ListContainer(value)
                value.init_entity(self, 'rank_targets', self.touch_rank_targets)
                if value != self.__rank_targets:
                    self.__rank_targets = value
                    if self._initialized:
                        self.touch_rank_targets()

    cpdef touch_rank_targets(self):
        self.dirty_fields.add('rank_targets')
        pass
    cdef public object __rank_defeated_targets
    property rank_defeated_targets:
        def __get__(self):
            return self.__rank_defeated_targets
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'rank_defeated_targets', self.touch_rank_defeated_targets)
                if value != self.__rank_defeated_targets:
                    self.__rank_defeated_targets = value
                    if self._initialized:
                        self.touch_rank_defeated_targets()

    cpdef touch_rank_defeated_targets(self):
        self.dirty_fields.add('rank_defeated_targets')
        pass
    cdef public int __rank_rest_count
    property rank_rest_count:
        def __get__(self):
            return self.__rank_rest_count
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_rest_count:
                    self.__rank_rest_count = value
                    if self._initialized:
                        self.touch_rank_rest_count()

    cpdef touch_rank_rest_count(self):
        self.dirty_fields.add('rank_rest_count')
        self.sync_dirty_fields.add('rank_rest_count')
        #self.sync_dirty_fields.add('rank_resume_rest_count_cd')
        pass
    cdef public int __rank_resume_rest_count_cd
    property rank_resume_rest_count_cd:
        def __get__(self):
            return self.__rank_resume_rest_count_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_resume_rest_count_cd:
                    self.__rank_resume_rest_count_cd = value
                    if self._initialized:
                        self.touch_rank_resume_rest_count_cd()

    cpdef touch_rank_resume_rest_count_cd(self):
        self.dirty_fields.add('rank_resume_rest_count_cd')
        self.sync_dirty_fields.add('rank_resume_rest_count_cd')
        pass
    cdef public int __rank_reset_used_count_ts
    property rank_reset_used_count_ts:
        def __get__(self):
            return self.__rank_reset_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_reset_used_count_ts:
                    self.__rank_reset_used_count_ts = value
                    if self._initialized:
                        self.touch_rank_reset_used_count_ts()

    cpdef touch_rank_reset_used_count_ts(self):
        self.dirty_fields.add('rank_reset_used_count_ts')
        pass
    cdef public int __rank_reset_used_count
    property rank_reset_used_count:
        def __get__(self):
            return self.__rank_reset_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_reset_used_count:
                    self.__rank_reset_used_count = value
                    if self._initialized:
                        self.touch_rank_reset_used_count()

    cpdef touch_rank_reset_used_count(self):
        self.dirty_fields.add('rank_reset_used_count')
        self.__rank_reset_rest_count = None
        self.__rank_reset_cost = None
        self.clear_rank_reset_rest_count()
        self.clear_rank_reset_cost()
        pass
    cdef public int __rank_refresh_cd
    property rank_refresh_cd:
        def __get__(self):
            return self.__rank_refresh_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_refresh_cd:
                    self.__rank_refresh_cd = value
                    if self._initialized:
                        self.touch_rank_refresh_cd()

    cpdef touch_rank_refresh_cd(self):
        self.dirty_fields.add('rank_refresh_cd')
        self.sync_dirty_fields.add('rank_refresh_cd')
        pass
    cdef public int __rank_refresh_used_count_ts
    property rank_refresh_used_count_ts:
        def __get__(self):
            return self.__rank_refresh_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_refresh_used_count_ts:
                    self.__rank_refresh_used_count_ts = value
                    if self._initialized:
                        self.touch_rank_refresh_used_count_ts()

    cpdef touch_rank_refresh_used_count_ts(self):
        self.dirty_fields.add('rank_refresh_used_count_ts')
        pass
    cdef public int __rank_refresh_used_count
    property rank_refresh_used_count:
        def __get__(self):
            return self.__rank_refresh_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_refresh_used_count:
                    self.__rank_refresh_used_count = value
                    if self._initialized:
                        self.touch_rank_refresh_used_count()

    cpdef touch_rank_refresh_used_count(self):
        self.dirty_fields.add('rank_refresh_used_count')
        self.__rank_refresh_cost = None
        self.clear_rank_refresh_cost()
        pass
    cdef public int __rank_serial_win_count
    property rank_serial_win_count:
        def __get__(self):
            return self.__rank_serial_win_count
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_serial_win_count:
                    self.__rank_serial_win_count = value
                    if self._initialized:
                        self.touch_rank_serial_win_count()

    cpdef touch_rank_serial_win_count(self):
        self.dirty_fields.add('rank_serial_win_count')
        self.sync_dirty_fields.add('rank_serial_win_count')
        pass
    cdef public int __rank_serial_win_count_cd
    property rank_serial_win_count_cd:
        def __get__(self):
            return self.__rank_serial_win_count_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__rank_serial_win_count_cd:
                    self.__rank_serial_win_count_cd = value
                    if self._initialized:
                        self.touch_rank_serial_win_count_cd()

    cpdef touch_rank_serial_win_count_cd(self):
        self.dirty_fields.add('rank_serial_win_count_cd')
        self.sync_dirty_fields.add('rank_serial_win_count_cd')
        pass
    cdef public object __npc_targets_cd
    property npc_targets_cd:
        def __get__(self):
            return self.__npc_targets_cd
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'npc_targets_cd', self.touch_npc_targets_cd)
                if value != self.__npc_targets_cd:
                    self.__npc_targets_cd = value
                    if self._initialized:
                        self.touch_npc_targets_cd()

    cpdef touch_npc_targets_cd(self):
        self.dirty_fields.add('npc_targets_cd')
        pass
    cdef public int __npc_target_cache
    property npc_target_cache:
        def __get__(self):
            return self.__npc_target_cache
        def __set__(self, value):
                value = int(value)
                if value != self.__npc_target_cache:
                    self.__npc_target_cache = value
                    if self._initialized:
                        self.touch_npc_target_cache()

    cpdef touch_npc_target_cache(self):
        self.dirty_fields.add('npc_target_cache')
        pass
    cdef public object __rank_revenged_targets
    property rank_revenged_targets:
        def __get__(self):
            return self.__rank_revenged_targets
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'rank_revenged_targets', self.touch_rank_revenged_targets)
                if value != self.__rank_revenged_targets:
                    self.__rank_revenged_targets = value
                    if self._initialized:
                        self.touch_rank_revenged_targets()

    cpdef touch_rank_revenged_targets(self):
        self.dirty_fields.add('rank_revenged_targets')
        pass
    cdef public object __hotpet_set
    property hotpet_set:
        def __get__(self):
            return self.__hotpet_set
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'hotpet_set', self.touch_hotpet_set)
                if value != self.__hotpet_set:
                    self.__hotpet_set = value
                    if self._initialized:
                        self.touch_hotpet_set()

    cpdef touch_hotpet_set(self):
        self.dirty_fields.add('hotpet_set')
        pass
    cdef public int __today_hotpet
    property today_hotpet:
        def __get__(self):
            return self.__today_hotpet
        def __set__(self, value):
                value = int(value)
                if value != self.__today_hotpet:
                    self.__today_hotpet = value
                    if self._initialized:
                        self.touch_today_hotpet()

    cpdef touch_today_hotpet(self):
        self.dirty_fields.add('today_hotpet')
        pass
    cdef public int __superhotpet
    property superhotpet:
        def __get__(self):
            return self.__superhotpet
        def __set__(self, value):
                value = int(value)
                if value != self.__superhotpet:
                    self.__superhotpet = value
                    if self._initialized:
                        self.touch_superhotpet()

    cpdef touch_superhotpet(self):
        self.dirty_fields.add('superhotpet')
        pass
    cdef public object __petpalt_time
    property petpalt_time:
        def __get__(self):
            return self.__petpalt_time
        def __set__(self, value):
                value = value
                if value != self.__petpalt_time:
                    self.__petpalt_time = value
                    if self._initialized:
                        self.touch_petpalt_time()

    cpdef touch_petpalt_time(self):
        self.dirty_fields.add('petpalt_time')
        pass
    cdef public object __mats
    property mats:
        def __get__(self):
            return self.__mats
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_mats(self):
        pass
    cdef public object __dirty_mats
    property dirty_mats:
        def __get__(self):
            return self.__dirty_mats
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'dirty_mats', self.touch_dirty_mats)
                if value != self.__dirty_mats:
                    self.__dirty_mats = value
                    if self._initialized:
                        self.touch_dirty_mats()

    cpdef touch_dirty_mats(self):
        pass
    cdef public int __fp
    property fp:
        def __get__(self):
            return self.__fp
        def __set__(self, value):
                value = int(value)
                if value != self.__fp:
                    self.__fp = value
                    if self._initialized:
                        self.touch_fp()

    cpdef touch_fp(self):
        self.dirty_fields.add('fp')
        self.sync_dirty_fields.add('fp')
        pass
    cdef public int __totalfp
    property totalfp:
        def __get__(self):
            return self.__totalfp
        def __set__(self, value):
                value = int(value)
                if value != self.__totalfp:
                    self.__totalfp = value
                    if self._initialized:
                        self.touch_totalfp()

    cpdef touch_totalfp(self):
        self.dirty_fields.add('totalfp')
        self.sync_dirty_fields.add('totalfp')
        pass
    cdef public int __todayfp_donate_ts
    property todayfp_donate_ts:
        def __get__(self):
            return self.__todayfp_donate_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__todayfp_donate_ts:
                    self.__todayfp_donate_ts = value
                    if self._initialized:
                        self.touch_todayfp_donate_ts()

    cpdef touch_todayfp_donate_ts(self):
        self.dirty_fields.add('todayfp_donate_ts')
        pass
    cdef public int __todayfp_donate
    property todayfp_donate:
        def __get__(self):
            return self.__todayfp_donate
        def __set__(self, value):
                value = int(value)
                if value != self.__todayfp_donate:
                    self.__todayfp_donate = value
                    if self._initialized:
                        self.touch_todayfp_donate()

    cpdef touch_todayfp_donate(self):
        self.dirty_fields.add('todayfp_donate')
        self.sync_dirty_fields.add('todayfp_donate')
        self.__todayfp = None
        self.clear_todayfp()
        pass
    cdef public int __dismissCD
    property dismissCD:
        def __get__(self):
            return self.__dismissCD
        def __set__(self, value):
                value = int(value)
                if value != self.__dismissCD:
                    self.__dismissCD = value
                    if self._initialized:
                        self.touch_dismissCD()

    cpdef touch_dismissCD(self):
        self.dirty_fields.add('dismissCD')
        self.sync_dirty_fields.add('dismissCD')
        pass
    cdef public int __todayfp_sp_ts
    property todayfp_sp_ts:
        def __get__(self):
            return self.__todayfp_sp_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__todayfp_sp_ts:
                    self.__todayfp_sp_ts = value
                    if self._initialized:
                        self.touch_todayfp_sp_ts()

    cpdef touch_todayfp_sp_ts(self):
        self.dirty_fields.add('todayfp_sp_ts')
        pass
    cdef public int __todayfp_sp
    property todayfp_sp:
        def __get__(self):
            return self.__todayfp_sp
        def __set__(self, value):
                value = int(value)
                if value != self.__todayfp_sp:
                    self.__todayfp_sp = value
                    if self._initialized:
                        self.touch_todayfp_sp()

    cpdef touch_todayfp_sp(self):
        self.dirty_fields.add('todayfp_sp')
        self.sync_dirty_fields.add('todayfp_sp')
        self.__todayfp = None
        self.clear_todayfp()
        pass
    cdef public int __faction_sp
    property faction_sp:
        def __get__(self):
            return self.__faction_sp
        def __set__(self, value):
                value = int(value)
                if value != self.__faction_sp:
                    self.__faction_sp = value
                    if self._initialized:
                        self.touch_faction_sp()

    cpdef touch_faction_sp(self):
        self.dirty_fields.add('faction_sp')
        pass
    cdef public int __todayfp_task_ts
    property todayfp_task_ts:
        def __get__(self):
            return self.__todayfp_task_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__todayfp_task_ts:
                    self.__todayfp_task_ts = value
                    if self._initialized:
                        self.touch_todayfp_task_ts()

    cpdef touch_todayfp_task_ts(self):
        self.dirty_fields.add('todayfp_task_ts')
        pass
    cdef public int __todayfp_task
    property todayfp_task:
        def __get__(self):
            return self.__todayfp_task
        def __set__(self, value):
                value = int(value)
                if value != self.__todayfp_task:
                    self.__todayfp_task = value
                    if self._initialized:
                        self.touch_todayfp_task()

    cpdef touch_todayfp_task(self):
        self.dirty_fields.add('todayfp_task')
        self.sync_dirty_fields.add('todayfp_task')
        self.__todayfp = None
        self.clear_todayfp()
        pass
    cdef public object __giftkeys
    property giftkeys:
        def __get__(self):
            return self.__giftkeys
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_giftkeys(self):
        pass
    cdef public object __equipset
    property equipset:
        def __get__(self):
            return self.__equipset
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'equipset', self.touch_equipset)
                if value != self.__equipset:
                    self.__equipset = value
                    if self._initialized:
                        self.touch_equipset()

    cpdef touch_equipset(self):
        self.dirty_fields.add('equipset')
        pass
    cdef public object __equips
    property equips:
        def __get__(self):
            return self.__equips
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'equips', self.touch_equips)
                if value != self.__equips:
                    self.__equips = value
                    if self._initialized:
                        self.touch_equips()

    cpdef touch_equips(self):
        pass
    cdef public object __equipeds
    property equipeds:
        def __get__(self):
            return self.__equipeds
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'equipeds', self.touch_equipeds)
                if value != self.__equipeds:
                    self.__equipeds = value
                    if self._initialized:
                        self.touch_equipeds()

    cpdef touch_equipeds(self):
        pass
    cdef public object __mine_rob_history_flag
    property mine_rob_history_flag:
        def __get__(self):
            return self.__mine_rob_history_flag
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__mine_rob_history_flag:
                    self.__mine_rob_history_flag = value
                    if self._initialized:
                        self.touch_mine_rob_history_flag()

    cpdef touch_mine_rob_history_flag(self):
        self.dirty_fields.add('mine_rob_history_flag')
        self.sync_dirty_fields.add('mine_rob_history_flag')
        pass
    cdef public int __mine_curr_target_cache
    property mine_curr_target_cache:
        def __get__(self):
            return self.__mine_curr_target_cache
        def __set__(self, value):
                value = int(value)
                if value != self.__mine_curr_target_cache:
                    self.__mine_curr_target_cache = value
                    if self._initialized:
                        self.touch_mine_curr_target_cache()

    cpdef touch_mine_curr_target_cache(self):
        self.dirty_fields.add('mine_curr_target_cache')
        pass
    cdef public int __mine_revenge_booty_cache
    property mine_revenge_booty_cache:
        def __get__(self):
            return self.__mine_revenge_booty_cache
        def __set__(self, value):
                value = int(value)
                if value != self.__mine_revenge_booty_cache:
                    self.__mine_revenge_booty_cache = value
                    if self._initialized:
                        self.touch_mine_revenge_booty_cache()

    cpdef touch_mine_revenge_booty_cache(self):
        self.dirty_fields.add('mine_revenge_booty_cache')
        pass
    cdef public object __mine_targets_detail_cache
    property mine_targets_detail_cache:
        def __get__(self):
            return self.__mine_targets_detail_cache
        def __set__(self, value):
                value = value
                if value != self.__mine_targets_detail_cache:
                    self.__mine_targets_detail_cache = value
                    if self._initialized:
                        self.touch_mine_targets_detail_cache()

    cpdef touch_mine_targets_detail_cache(self):
        self.dirty_fields.add('mine_targets_detail_cache')
        pass
    cdef public object __mine_rob_history
    property mine_rob_history:
        def __get__(self):
            return self.__mine_rob_history
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_mine_rob_history(self):
        pass
    cdef public int __mine_rob_count
    property mine_rob_count:
        def __get__(self):
            return self.__mine_rob_count
        def __set__(self, value):
                value = int(value)
                if value != self.__mine_rob_count:
                    self.__mine_rob_count = value
                    if self._initialized:
                        self.touch_mine_rob_count()

    cpdef touch_mine_rob_count(self):
        self.dirty_fields.add('mine_rob_count')
        self.sync_dirty_fields.add('mine_rob_count')
        #self.sync_dirty_fields.add('resume_mine_rob_count_cd')
        pass
    cdef public int __resume_mine_rob_count_cd
    property resume_mine_rob_count_cd:
        def __get__(self):
            return self.__resume_mine_rob_count_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__resume_mine_rob_count_cd:
                    self.__resume_mine_rob_count_cd = value
                    if self._initialized:
                        self.touch_resume_mine_rob_count_cd()

    cpdef touch_resume_mine_rob_count_cd(self):
        self.dirty_fields.add('resume_mine_rob_count_cd')
        self.sync_dirty_fields.add('resume_mine_rob_count_cd')
        pass
    cdef public int __mine_protect_time
    property mine_protect_time:
        def __get__(self):
            return self.__mine_protect_time
        def __set__(self, value):
                value = int(value)
                if value != self.__mine_protect_time:
                    self.__mine_protect_time = value
                    if self._initialized:
                        self.touch_mine_protect_time()

    cpdef touch_mine_protect_time(self):
        self.dirty_fields.add('mine_protect_time')
        self.sync_dirty_fields.add('mine_protect_time')
        pass
    cdef public int __mine_products1
    property mine_products1:
        def __get__(self):
            return self.__mine_products1
        def __set__(self, value):
                value = int(value)
                if value != self.__mine_products1:
                    self.__mine_products1 = value
                    if self._initialized:
                        self.touch_mine_products1()

    cpdef touch_mine_products1(self):
        self.dirty_fields.add('mine_products1')
        self.sync_dirty_fields.add('mine_products1')
        pass
    cdef public int __mine_productivity1
    property mine_productivity1:
        def __get__(self):
            return self.__mine_productivity1
        def __set__(self, value):
                value = int(value)
                if value != self.__mine_productivity1:
                    self.__mine_productivity1 = value
                    if self._initialized:
                        self.touch_mine_productivity1()

    cpdef touch_mine_productivity1(self):
        self.dirty_fields.add('mine_productivity1')
        self.sync_dirty_fields.add('mine_productivity1')
        pass
    cdef public int __mine_time1
    property mine_time1:
        def __get__(self):
            return self.__mine_time1
        def __set__(self, value):
                value = int(value)
                if value != self.__mine_time1:
                    self.__mine_time1 = value
                    if self._initialized:
                        self.touch_mine_time1()

    cpdef touch_mine_time1(self):
        self.dirty_fields.add('mine_time1')
        self.__mine_time_past1 = None
        self.clear_mine_time_past1()
        pass
    cdef public int __mine_free_collect_count1_ts
    property mine_free_collect_count1_ts:
        def __get__(self):
            return self.__mine_free_collect_count1_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__mine_free_collect_count1_ts:
                    self.__mine_free_collect_count1_ts = value
                    if self._initialized:
                        self.touch_mine_free_collect_count1_ts()

    cpdef touch_mine_free_collect_count1_ts(self):
        self.dirty_fields.add('mine_free_collect_count1_ts')
        pass
    cdef public int __mine_free_collect_count1
    property mine_free_collect_count1:
        def __get__(self):
            return self.__mine_free_collect_count1
        def __set__(self, value):
                value = int(value)
                if value != self.__mine_free_collect_count1:
                    self.__mine_free_collect_count1 = value
                    if self._initialized:
                        self.touch_mine_free_collect_count1()

    cpdef touch_mine_free_collect_count1(self):
        self.dirty_fields.add('mine_free_collect_count1')
        self.sync_dirty_fields.add('mine_free_collect_count1')
        pass
    cdef public object __mine_rob_by_date1
    property mine_rob_by_date1:
        def __get__(self):
            return self.__mine_rob_by_date1
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_mine_rob_by_date1(self):
        pass
    cdef public int __mine_products2
    property mine_products2:
        def __get__(self):
            return self.__mine_products2
        def __set__(self, value):
                value = int(value)
                if value != self.__mine_products2:
                    self.__mine_products2 = value
                    if self._initialized:
                        self.touch_mine_products2()

    cpdef touch_mine_products2(self):
        self.dirty_fields.add('mine_products2')
        self.sync_dirty_fields.add('mine_products2')
        pass
    cdef public int __mine_productivity2
    property mine_productivity2:
        def __get__(self):
            return self.__mine_productivity2
        def __set__(self, value):
                value = int(value)
                if value != self.__mine_productivity2:
                    self.__mine_productivity2 = value
                    if self._initialized:
                        self.touch_mine_productivity2()

    cpdef touch_mine_productivity2(self):
        self.dirty_fields.add('mine_productivity2')
        self.sync_dirty_fields.add('mine_productivity2')
        pass
    cdef public int __mine_time2
    property mine_time2:
        def __get__(self):
            return self.__mine_time2
        def __set__(self, value):
                value = int(value)
                if value != self.__mine_time2:
                    self.__mine_time2 = value
                    if self._initialized:
                        self.touch_mine_time2()

    cpdef touch_mine_time2(self):
        self.dirty_fields.add('mine_time2')
        self.__mine_time_past2 = None
        self.clear_mine_time_past2()
        pass
    cdef public int __mine_free_collect_count2_ts
    property mine_free_collect_count2_ts:
        def __get__(self):
            return self.__mine_free_collect_count2_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__mine_free_collect_count2_ts:
                    self.__mine_free_collect_count2_ts = value
                    if self._initialized:
                        self.touch_mine_free_collect_count2_ts()

    cpdef touch_mine_free_collect_count2_ts(self):
        self.dirty_fields.add('mine_free_collect_count2_ts')
        pass
    cdef public int __mine_free_collect_count2
    property mine_free_collect_count2:
        def __get__(self):
            return self.__mine_free_collect_count2
        def __set__(self, value):
                value = int(value)
                if value != self.__mine_free_collect_count2:
                    self.__mine_free_collect_count2 = value
                    if self._initialized:
                        self.touch_mine_free_collect_count2()

    cpdef touch_mine_free_collect_count2(self):
        self.dirty_fields.add('mine_free_collect_count2')
        self.sync_dirty_fields.add('mine_free_collect_count2')
        pass
    cdef public object __mine_rob_by_date2
    property mine_rob_by_date2:
        def __get__(self):
            return self.__mine_rob_by_date2
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_mine_rob_by_date2(self):
        pass
    cdef public object __uproar_targets_cache
    property uproar_targets_cache:
        def __get__(self):
            return self.__uproar_targets_cache
        def __set__(self, value):
                value = value
                if value != self.__uproar_targets_cache:
                    self.__uproar_targets_cache = value
                    if self._initialized:
                        self.touch_uproar_targets_cache()

    cpdef touch_uproar_targets_cache(self):
        self.dirty_fields.add('uproar_targets_cache')
        pass
    cdef public object __uproar_targets_done
    property uproar_targets_done:
        def __get__(self):
            return self.__uproar_targets_done
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'uproar_targets_done', self.touch_uproar_targets_done)
                if value != self.__uproar_targets_done:
                    self.__uproar_targets_done = value
                    if self._initialized:
                        self.touch_uproar_targets_done()

    cpdef touch_uproar_targets_done(self):
        self.dirty_fields.add('uproar_targets_done')
        self.__last_target = None
        self.clear_last_target()
        pass
    cdef public object __uproar_chests_done
    property uproar_chests_done:
        def __get__(self):
            return self.__uproar_chests_done
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'uproar_chests_done', self.touch_uproar_chests_done)
                if value != self.__uproar_chests_done:
                    self.__uproar_chests_done = value
                    if self._initialized:
                        self.touch_uproar_chests_done()

    cpdef touch_uproar_chests_done(self):
        self.dirty_fields.add('uproar_chests_done')
        self.__last_chest = None
        self.clear_last_chest()
        pass
    cdef public int __uproar_target_cache
    property uproar_target_cache:
        def __get__(self):
            return self.__uproar_target_cache
        def __set__(self, value):
                value = int(value)
                if value != self.__uproar_target_cache:
                    self.__uproar_target_cache = value
                    if self._initialized:
                        self.touch_uproar_target_cache()

    cpdef touch_uproar_target_cache(self):
        self.dirty_fields.add('uproar_target_cache')
        pass
    cdef public int __uproar_refresh_used_count_ts
    property uproar_refresh_used_count_ts:
        def __get__(self):
            return self.__uproar_refresh_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__uproar_refresh_used_count_ts:
                    self.__uproar_refresh_used_count_ts = value
                    if self._initialized:
                        self.touch_uproar_refresh_used_count_ts()

    cpdef touch_uproar_refresh_used_count_ts(self):
        self.dirty_fields.add('uproar_refresh_used_count_ts')
        pass
    cdef public int __uproar_refresh_used_count
    property uproar_refresh_used_count:
        def __get__(self):
            return self.__uproar_refresh_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__uproar_refresh_used_count:
                    self.__uproar_refresh_used_count = value
                    if self._initialized:
                        self.touch_uproar_refresh_used_count()

    cpdef touch_uproar_refresh_used_count(self):
        self.dirty_fields.add('uproar_refresh_used_count')
        self.__uproar_refresh_rest_count = None
        self.clear_uproar_refresh_rest_count()
        pass
    cdef public int __jiutian
    property jiutian:
        def __get__(self):
            return self.__jiutian
        def __set__(self, value):
                value = int(value)
                if value != self.__jiutian:
                    self.__jiutian = value
                    if self._initialized:
                        self.touch_jiutian()

    cpdef touch_jiutian(self):
        self.dirty_fields.add('jiutian')
        self.sync_dirty_fields.add('jiutian')
        pass
    cdef public object __uproar_targets_team
    property uproar_targets_team:
        def __get__(self):
            return self.__uproar_targets_team
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_uproar_targets_team(self):
        pass
    cdef public object __uproar_chests_cache
    property uproar_chests_cache:
        def __get__(self):
            return self.__uproar_chests_cache
        def __set__(self, value):
                value = value
                if value != self.__uproar_chests_cache:
                    self.__uproar_chests_cache = value
                    if self._initialized:
                        self.touch_uproar_chests_cache()

    cpdef touch_uproar_chests_cache(self):
        self.dirty_fields.add('uproar_chests_cache')
        pass
    cdef public object __uproar_details_cache
    property uproar_details_cache:
        def __get__(self):
            return self.__uproar_details_cache
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_uproar_details_cache(self):
        pass
    cdef public int __uproar_enemy_buff
    property uproar_enemy_buff:
        def __get__(self):
            return self.__uproar_enemy_buff
        def __set__(self, value):
                value = int(value)
                if value != self.__uproar_enemy_buff:
                    self.__uproar_enemy_buff = value
                    if self._initialized:
                        self.touch_uproar_enemy_buff()

    cpdef touch_uproar_enemy_buff(self):
        self.dirty_fields.add('uproar_enemy_buff')
        self.sync_dirty_fields.add('uproar_enemy_buff')
        pass
    cdef public int __uproar_enemy_min_power
    property uproar_enemy_min_power:
        def __get__(self):
            return self.__uproar_enemy_min_power
        def __set__(self, value):
                value = int(value)
                if value != self.__uproar_enemy_min_power:
                    self.__uproar_enemy_min_power = value
                    if self._initialized:
                        self.touch_uproar_enemy_min_power()

    cpdef touch_uproar_enemy_min_power(self):
        self.dirty_fields.add('uproar_enemy_min_power')
        pass
    cdef public object __uproar_targets
    property uproar_targets:
        def __get__(self):
            return self.__uproar_targets
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_uproar_targets(self):
        pass
    cdef public object __uproar_chests
    property uproar_chests:
        def __get__(self):
            return self.__uproar_chests
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_uproar_chests(self):
        pass
    cdef public int __loot_used_count_ts
    property loot_used_count_ts:
        def __get__(self):
            return self.__loot_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__loot_used_count_ts:
                    self.__loot_used_count_ts = value
                    if self._initialized:
                        self.touch_loot_used_count_ts()

    cpdef touch_loot_used_count_ts(self):
        self.dirty_fields.add('loot_used_count_ts')
        pass
    cdef public int __loot_used_count
    property loot_used_count:
        def __get__(self):
            return self.__loot_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__loot_used_count:
                    self.__loot_used_count = value
                    if self._initialized:
                        self.touch_loot_used_count()

    cpdef touch_loot_used_count(self):
        self.dirty_fields.add('loot_used_count')
        self.__loot_rest_count = None
        self.clear_loot_rest_count()
        pass
    cdef public int __loot_max_count
    property loot_max_count:
        def __get__(self):
            return self.__loot_max_count
        def __set__(self, value):
                value = int(value)
                if value != self.__loot_max_count:
                    self.__loot_max_count = value
                    if self._initialized:
                        self.touch_loot_max_count()

    cpdef touch_loot_max_count(self):
        self.__loot_rest_count = None
        self.clear_loot_rest_count()
        pass
    cdef public int __loot_last_resume_time
    property loot_last_resume_time:
        def __get__(self):
            return self.__loot_last_resume_time
        def __set__(self, value):
                value = int(value)
                if value != self.__loot_last_resume_time:
                    self.__loot_last_resume_time = value
                    if self._initialized:
                        self.touch_loot_last_resume_time()

    cpdef touch_loot_last_resume_time(self):
        self.dirty_fields.add('loot_last_resume_time')
        pass
    cdef public object __loot_temp_mats
    property loot_temp_mats:
        def __get__(self):
            return self.__loot_temp_mats
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_loot_temp_mats(self):
        pass
    cdef public object __loot_targets_cache
    property loot_targets_cache:
        def __get__(self):
            return self.__loot_targets_cache
        def __set__(self, value):
                value = value
                if value != self.__loot_targets_cache:
                    self.__loot_targets_cache = value
                    if self._initialized:
                        self.touch_loot_targets_cache()

    cpdef touch_loot_targets_cache(self):
        self.dirty_fields.add('loot_targets_cache')
        pass
    cdef public int __loot_current_target
    property loot_current_target:
        def __get__(self):
            return self.__loot_current_target
        def __set__(self, value):
                value = int(value)
                if value != self.__loot_current_target:
                    self.__loot_current_target = value
                    if self._initialized:
                        self.touch_loot_current_target()

    cpdef touch_loot_current_target(self):
        self.dirty_fields.add('loot_current_target')
        pass
    cdef public object __loot_history
    property loot_history:
        def __get__(self):
            return self.__loot_history
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_loot_history(self):
        pass
    cdef public int __loot_reset_count_ts
    property loot_reset_count_ts:
        def __get__(self):
            return self.__loot_reset_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__loot_reset_count_ts:
                    self.__loot_reset_count_ts = value
                    if self._initialized:
                        self.touch_loot_reset_count_ts()

    cpdef touch_loot_reset_count_ts(self):
        self.dirty_fields.add('loot_reset_count_ts')
        pass
    cdef public int __loot_reset_count
    property loot_reset_count:
        def __get__(self):
            return self.__loot_reset_count
        def __set__(self, value):
                value = int(value)
                if value != self.__loot_reset_count:
                    self.__loot_reset_count = value
                    if self._initialized:
                        self.touch_loot_reset_count()

    cpdef touch_loot_reset_count(self):
        self.dirty_fields.add('loot_reset_count')
        self.sync_dirty_fields.add('loot_reset_count')
        pass
    cdef public int __loot_reset_crit_count_ts
    property loot_reset_crit_count_ts:
        def __get__(self):
            return self.__loot_reset_crit_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__loot_reset_crit_count_ts:
                    self.__loot_reset_crit_count_ts = value
                    if self._initialized:
                        self.touch_loot_reset_crit_count_ts()

    cpdef touch_loot_reset_crit_count_ts(self):
        self.dirty_fields.add('loot_reset_crit_count_ts')
        pass
    cdef public int __loot_reset_crit_count
    property loot_reset_crit_count:
        def __get__(self):
            return self.__loot_reset_crit_count
        def __set__(self, value):
                value = int(value)
                if value != self.__loot_reset_crit_count:
                    self.__loot_reset_crit_count = value
                    if self._initialized:
                        self.touch_loot_reset_crit_count()

    cpdef touch_loot_reset_crit_count(self):
        self.dirty_fields.add('loot_reset_crit_count')
        pass
    cdef public int __loot_protect_time
    property loot_protect_time:
        def __get__(self):
            return self.__loot_protect_time
        def __set__(self, value):
                value = int(value)
                if value != self.__loot_protect_time:
                    self.__loot_protect_time = value
                    if self._initialized:
                        self.touch_loot_protect_time()

    cpdef touch_loot_protect_time(self):
        self.dirty_fields.add('loot_protect_time')
        pass
    cdef public int __pious_backup
    property pious_backup:
        def __get__(self):
            return self.__pious_backup
        def __set__(self, value):
                value = int(value)
                if value != self.__pious_backup:
                    self.__pious_backup = value
                    if self._initialized:
                        self.touch_pious_backup()

    cpdef touch_pious_backup(self):
        self.dirty_fields.add('pious_backup')
        pass
    cdef public int __visit_group
    property visit_group:
        def __get__(self):
            return self.__visit_group
        def __set__(self, value):
                value = int(value)
                if value != self.__visit_group:
                    self.__visit_group = value
                    if self._initialized:
                        self.touch_visit_group()

    cpdef touch_visit_group(self):
        self.dirty_fields.add('visit_group')
        pass
    cdef public int __visit_time
    property visit_time:
        def __get__(self):
            return self.__visit_time
        def __set__(self, value):
                value = int(value)
                if value != self.__visit_time:
                    self.__visit_time = value
                    if self._initialized:
                        self.touch_visit_time()

    cpdef touch_visit_time(self):
        self.dirty_fields.add('visit_time')
        pass
    cdef public int __dream
    property dream:
        def __get__(self):
            return self.__dream
        def __set__(self, value):
                value = int(value)
                if value != self.__dream:
                    self.__dream = value
                    if self._initialized:
                        self.touch_dream()

    cpdef touch_dream(self):
        self.dirty_fields.add('dream')
        self.sync_dirty_fields.add('dream')
        pass
    cdef public int __pious
    property pious:
        def __get__(self):
            return self.__pious
        def __set__(self, value):
                value = int(value)
                if value != self.__pious:
                    self.__pious = value
                    if self._initialized:
                        self.touch_pious()

    cpdef touch_pious(self):
        self.dirty_fields.add('pious')
        self.sync_dirty_fields.add('pious')
        pass
    cdef public int __visit_free_used_count_ts
    property visit_free_used_count_ts:
        def __get__(self):
            return self.__visit_free_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__visit_free_used_count_ts:
                    self.__visit_free_used_count_ts = value
                    if self._initialized:
                        self.touch_visit_free_used_count_ts()

    cpdef touch_visit_free_used_count_ts(self):
        self.dirty_fields.add('visit_free_used_count_ts')
        pass
    cdef public int __visit_free_used_count
    property visit_free_used_count:
        def __get__(self):
            return self.__visit_free_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__visit_free_used_count:
                    self.__visit_free_used_count = value
                    if self._initialized:
                        self.touch_visit_free_used_count()

    cpdef touch_visit_free_used_count(self):
        self.dirty_fields.add('visit_free_used_count')
        self.__visit_free_rest_count = None
        self.clear_visit_free_rest_count()
        pass
    cdef public int __visit_today_used_count_ts
    property visit_today_used_count_ts:
        def __get__(self):
            return self.__visit_today_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__visit_today_used_count_ts:
                    self.__visit_today_used_count_ts = value
                    if self._initialized:
                        self.touch_visit_today_used_count_ts()

    cpdef touch_visit_today_used_count_ts(self):
        self.dirty_fields.add('visit_today_used_count_ts')
        pass
    cdef public int __visit_today_used_count
    property visit_today_used_count:
        def __get__(self):
            return self.__visit_today_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__visit_today_used_count:
                    self.__visit_today_used_count = value
                    if self._initialized:
                        self.touch_visit_today_used_count()

    cpdef touch_visit_today_used_count(self):
        self.dirty_fields.add('visit_today_used_count')
        pass
    cdef public object __level_packs_done
    property level_packs_done:
        def __get__(self):
            return self.__level_packs_done
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'level_packs_done', self.touch_level_packs_done)
                if value != self.__level_packs_done:
                    self.__level_packs_done = value
                    if self._initialized:
                        self.touch_level_packs_done()

    cpdef touch_level_packs_done(self):
        self.dirty_fields.add('level_packs_done')
        self.__level_packs_flag = None
        self.__level_packs_done_count = None
        self.clear_level_packs_flag()
        self.clear_level_packs_done_count()
        pass
    cdef public object __level_packs_end
    property level_packs_end:
        def __get__(self):
            return self.__level_packs_end
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'level_packs_end', self.touch_level_packs_end)
                if value != self.__level_packs_end:
                    self.__level_packs_end = value
                    if self._initialized:
                        self.touch_level_packs_end()

    cpdef touch_level_packs_end(self):
        self.dirty_fields.add('level_packs_end')
        self.__level_packs_flag = None
        self.clear_level_packs_flag()
        pass
    cdef public object __power_packs_done
    property power_packs_done:
        def __get__(self):
            return self.__power_packs_done
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'power_packs_done', self.touch_power_packs_done)
                if value != self.__power_packs_done:
                    self.__power_packs_done = value
                    if self._initialized:
                        self.touch_power_packs_done()

    cpdef touch_power_packs_done(self):
        self.dirty_fields.add('power_packs_done')
        self.__power_packs_flag = None
        self.__power_packs_done_count = None
        self.clear_power_packs_flag()
        self.clear_power_packs_done_count()
        pass
    cdef public object __power_packs_end
    property power_packs_end:
        def __get__(self):
            return self.__power_packs_end
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'power_packs_end', self.touch_power_packs_end)
                if value != self.__power_packs_end:
                    self.__power_packs_end = value
                    if self._initialized:
                        self.touch_power_packs_end()

    cpdef touch_power_packs_end(self):
        self.dirty_fields.add('power_packs_end')
        self.__power_packs_flag = None
        self.clear_power_packs_flag()
        pass
    cdef public object __totallogin_end
    property totallogin_end:
        def __get__(self):
            return self.__totallogin_end
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'totallogin_end', self.touch_totallogin_end)
                if value != self.__totallogin_end:
                    self.__totallogin_end = value
                    if self._initialized:
                        self.touch_totallogin_end()

    cpdef touch_totallogin_end(self):
        self.dirty_fields.add('totallogin_end')
        self.__totallogin_flag = None
        self.clear_totallogin_flag()
        pass
    cdef public double __factionEVA
    property factionEVA:
        def __get__(self):
            return self.__factionEVA
        def __set__(self, value):
                value = float(value)
                if value != self.__factionEVA:
                    self.__factionEVA = value
                    if self._initialized:
                        self.touch_factionEVA()

    cpdef touch_factionEVA(self):
        self.__power = None
        self.__faction_power = None
        self.clear_power()
        self.clear_faction_power()
        pass
    cdef public int __max_power
    property max_power:
        def __get__(self):
            return self.__max_power
        def __set__(self, value):
                value = int(value)
                if value != self.__max_power:
                    self.__max_power = value
                    if self._initialized:
                        self.touch_max_power()

    cpdef touch_max_power(self):
        self.dirty_fields.add('max_power')
        self.sync_dirty_fields.add('max_power')
        pass
    cdef public int __power_cache
    property power_cache:
        def __get__(self):
            return self.__power_cache
        def __set__(self, value):
                value = int(value)
                if value != self.__power_cache:
                    self.__power_cache = value
                    if self._initialized:
                        self.touch_power_cache()

    cpdef touch_power_cache(self):
        self.dirty_fields.add('power_cache')
        pass
    cdef public object __star_packs_end
    property star_packs_end:
        def __get__(self):
            return self.__star_packs_end
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'star_packs_end', self.touch_star_packs_end)
                if value != self.__star_packs_end:
                    self.__star_packs_end = value
                    if self._initialized:
                        self.touch_star_packs_end()

    cpdef touch_star_packs_end(self):
        self.dirty_fields.add('star_packs_end')
        pass
    cdef public int __star_packs_version
    property star_packs_version:
        def __get__(self):
            return self.__star_packs_version
        def __set__(self, value):
                value = int(value)
                if value != self.__star_packs_version:
                    self.__star_packs_version = value
                    if self._initialized:
                        self.touch_star_packs_version()

    cpdef touch_star_packs_version(self):
        self.dirty_fields.add('star_packs_version')
        pass
    cdef public unicode __appid
    property appid:
        def __get__(self):
            return self.__appid
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__appid:
                    self.__appid = value
                    if self._initialized:
                        self.touch_appid()

    cpdef touch_appid(self):
        self.dirty_fields.add('appid')
        pass
    cdef public unicode __UDID
    property UDID:
        def __get__(self):
            return self.__UDID
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__UDID:
                    self.__UDID = value
                    if self._initialized:
                        self.touch_UDID()

    cpdef touch_UDID(self):
        self.dirty_fields.add('UDID')
        pass
    cdef public unicode __idfa
    property idfa:
        def __get__(self):
            return self.__idfa
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__idfa:
                    self.__idfa = value
                    if self._initialized:
                        self.touch_idfa()

    cpdef touch_idfa(self):
        self.dirty_fields.add('idfa')
        pass
    cdef public unicode __MAC
    property MAC:
        def __get__(self):
            return self.__MAC
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__MAC:
                    self.__MAC = value
                    if self._initialized:
                        self.touch_MAC()

    cpdef touch_MAC(self):
        self.dirty_fields.add('MAC')
        pass
    cdef public object __new_role
    property new_role:
        def __get__(self):
            return self.__new_role
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__new_role:
                    self.__new_role = value
                    if self._initialized:
                        self.touch_new_role()

    cpdef touch_new_role(self):
        self.sync_dirty_fields.add('new_role')
        pass
    cdef public object __autofight
    property autofight:
        def __get__(self):
            return self.__autofight
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__autofight:
                    self.__autofight = value
                    if self._initialized:
                        self.touch_autofight()

    cpdef touch_autofight(self):
        self.dirty_fields.add('autofight')
        self.sync_dirty_fields.add('autofight')
        pass
    cdef public object __speedUpfight
    property speedUpfight:
        def __get__(self):
            return self.__speedUpfight
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__speedUpfight:
                    self.__speedUpfight = value
                    if self._initialized:
                        self.touch_speedUpfight()

    cpdef touch_speedUpfight(self):
        self.dirty_fields.add('speedUpfight')
        self.sync_dirty_fields.add('speedUpfight')
        pass
    cdef public int __dongtian_cd
    property dongtian_cd:
        def __get__(self):
            return self.__dongtian_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__dongtian_cd:
                    self.__dongtian_cd = value
                    if self._initialized:
                        self.touch_dongtian_cd()

    cpdef touch_dongtian_cd(self):
        self.dirty_fields.add('dongtian_cd')
        self.sync_dirty_fields.add('dongtian_cd')
        pass
    cdef public int __fudi_cd
    property fudi_cd:
        def __get__(self):
            return self.__fudi_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__fudi_cd:
                    self.__fudi_cd = value
                    if self._initialized:
                        self.touch_fudi_cd()

    cpdef touch_fudi_cd(self):
        self.dirty_fields.add('fudi_cd')
        self.sync_dirty_fields.add('fudi_cd')
        pass
    cdef public int __treasure_type
    property treasure_type:
        def __get__(self):
            return self.__treasure_type
        def __set__(self, value):
                value = int(value)
                if value != self.__treasure_type:
                    self.__treasure_type = value
                    if self._initialized:
                        self.touch_treasure_type()

    cpdef touch_treasure_type(self):
        self.dirty_fields.add('treasure_type')
        self.sync_dirty_fields.add('treasure_type')
        self.__treasure_chest_gold = None
        self.clear_treasure_chest_gold()
        pass
    cdef public int __treasure_refresh_count
    property treasure_refresh_count:
        def __get__(self):
            return self.__treasure_refresh_count
        def __set__(self, value):
                value = int(value)
                if value != self.__treasure_refresh_count:
                    self.__treasure_refresh_count = value
                    if self._initialized:
                        self.touch_treasure_refresh_count()

    cpdef touch_treasure_refresh_count(self):
        self.dirty_fields.add('treasure_refresh_count')
        pass
    cdef public object __treasure_cache
    property treasure_cache:
        def __get__(self):
            return self.__treasure_cache
        def __set__(self, value):
                value = ListContainer(value)
                value.init_entity(self, 'treasure_cache', self.touch_treasure_cache)
                if value != self.__treasure_cache:
                    self.__treasure_cache = value
                    if self._initialized:
                        self.touch_treasure_cache()

    cpdef touch_treasure_cache(self):
        self.dirty_fields.add('treasure_cache')
        pass
    cdef public int __treasure_cd
    property treasure_cd:
        def __get__(self):
            return self.__treasure_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__treasure_cd:
                    self.__treasure_cd = value
                    if self._initialized:
                        self.touch_treasure_cd()

    cpdef touch_treasure_cd(self):
        self.dirty_fields.add('treasure_cd')
        self.sync_dirty_fields.add('treasure_cd')
        pass
    cdef public int __treasure_used_count_ts
    property treasure_used_count_ts:
        def __get__(self):
            return self.__treasure_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__treasure_used_count_ts:
                    self.__treasure_used_count_ts = value
                    if self._initialized:
                        self.touch_treasure_used_count_ts()

    cpdef touch_treasure_used_count_ts(self):
        self.dirty_fields.add('treasure_used_count_ts')
        pass
    cdef public int __treasure_used_count
    property treasure_used_count:
        def __get__(self):
            return self.__treasure_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__treasure_used_count:
                    self.__treasure_used_count = value
                    if self._initialized:
                        self.touch_treasure_used_count()

    cpdef touch_treasure_used_count(self):
        self.dirty_fields.add('treasure_used_count')
        self.__treasure_count = None
        self.clear_treasure_count()
        pass
    cdef public object __friend_messages
    property friend_messages:
        def __get__(self):
            return self.__friend_messages
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_friend_messages(self):
        self.__friend_messages_count = None
        self.clear_friend_messages_count()
        pass
    cdef public object __friendset
    property friendset:
        def __get__(self):
            return self.__friendset
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'friendset', self.touch_friendset)
                if value != self.__friendset:
                    self.__friendset = value
                    if self._initialized:
                        self.touch_friendset()

    cpdef touch_friendset(self):
        self.dirty_fields.add('friendset')
        self.__friend_count = None
        self.clear_friend_count()
        pass
    cdef public object __friend_applys
    property friend_applys:
        def __get__(self):
            return self.__friend_applys
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_friend_applys(self):
        self.__friend_applys_count = None
        self.clear_friend_applys_count()
        pass
    cdef public int __friend_gift_used_count_ts
    property friend_gift_used_count_ts:
        def __get__(self):
            return self.__friend_gift_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__friend_gift_used_count_ts:
                    self.__friend_gift_used_count_ts = value
                    if self._initialized:
                        self.touch_friend_gift_used_count_ts()

    cpdef touch_friend_gift_used_count_ts(self):
        self.dirty_fields.add('friend_gift_used_count_ts')
        pass
    cdef public int __friend_gift_used_count
    property friend_gift_used_count:
        def __get__(self):
            return self.__friend_gift_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__friend_gift_used_count:
                    self.__friend_gift_used_count = value
                    if self._initialized:
                        self.touch_friend_gift_used_count()

    cpdef touch_friend_gift_used_count(self):
        self.dirty_fields.add('friend_gift_used_count')
        self.sync_dirty_fields.add('friend_gift_used_count')
        pass
    cdef public int __friendgiftedset_ts
    property friendgiftedset_ts:
        def __get__(self):
            return self.__friendgiftedset_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__friendgiftedset_ts:
                    self.__friendgiftedset_ts = value
                    if self._initialized:
                        self.touch_friendgiftedset_ts()

    cpdef touch_friendgiftedset_ts(self):
        self.dirty_fields.add('friendgiftedset_ts')
        pass
    cdef public object __friendgiftedset
    property friendgiftedset:
        def __get__(self):
            return self.__friendgiftedset
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'friendgiftedset', self.touch_friendgiftedset)
                if value != self.__friendgiftedset:
                    self.__friendgiftedset = value
                    if self._initialized:
                        self.touch_friendgiftedset()

    cpdef touch_friendgiftedset(self):
        self.dirty_fields.add('friendgiftedset')
        pass
    cdef public object __tap_hurts
    property tap_hurts:
        def __get__(self):
            return self.__tap_hurts
        def __set__(self, value):
                value = ListContainer(value)
                value.init_entity(self, 'tap_hurts', self.touch_tap_hurts)
                if value != self.__tap_hurts:
                    self.__tap_hurts = value
                    if self._initialized:
                        self.touch_tap_hurts()

    cpdef touch_tap_hurts(self):
        self.dirty_fields.add('tap_hurts')
        pass
    cdef public int __tap_hurts_index
    property tap_hurts_index:
        def __get__(self):
            return self.__tap_hurts_index
        def __set__(self, value):
                value = int(value)
                if value != self.__tap_hurts_index:
                    self.__tap_hurts_index = value
                    if self._initialized:
                        self.touch_tap_hurts_index()

    cpdef touch_tap_hurts_index(self):
        self.dirty_fields.add('tap_hurts_index')
        pass
    cdef public int __tap_monster
    property tap_monster:
        def __get__(self):
            return self.__tap_monster
        def __set__(self, value):
                value = int(value)
                if value != self.__tap_monster:
                    self.__tap_monster = value
                    if self._initialized:
                        self.touch_tap_monster()

    cpdef touch_tap_monster(self):
        self.dirty_fields.add('tap_monster')
        pass
    cdef public int __tap_loop_count
    property tap_loop_count:
        def __get__(self):
            return self.__tap_loop_count
        def __set__(self, value):
                value = int(value)
                if value != self.__tap_loop_count:
                    self.__tap_loop_count = value
                    if self._initialized:
                        self.touch_tap_loop_count()

    cpdef touch_tap_loop_count(self):
        self.dirty_fields.add('tap_loop_count')
        pass
    cdef public int __tap_rest_count
    property tap_rest_count:
        def __get__(self):
            return self.__tap_rest_count
        def __set__(self, value):
                value = int(value)
                if value != self.__tap_rest_count:
                    self.__tap_rest_count = value
                    if self._initialized:
                        self.touch_tap_rest_count()

    cpdef touch_tap_rest_count(self):
        self.dirty_fields.add('tap_rest_count')
        self.sync_dirty_fields.add('tap_rest_count')
        #self.sync_dirty_fields.add('tap_rest_count_resume_cd')
        pass
    cdef public int __tap_rest_count_resume_cd
    property tap_rest_count_resume_cd:
        def __get__(self):
            return self.__tap_rest_count_resume_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__tap_rest_count_resume_cd:
                    self.__tap_rest_count_resume_cd = value
                    if self._initialized:
                        self.touch_tap_rest_count_resume_cd()

    cpdef touch_tap_rest_count_resume_cd(self):
        self.dirty_fields.add('tap_rest_count_resume_cd')
        self.sync_dirty_fields.add('tap_rest_count_resume_cd')
        pass
    cdef public int __tap_max_count
    property tap_max_count:
        def __get__(self):
            return self.__tap_max_count
        def __set__(self, value):
                value = int(value)
                if value != self.__tap_max_count:
                    self.__tap_max_count = value
                    if self._initialized:
                        self.touch_tap_max_count()

    cpdef touch_tap_max_count(self):
        self.sync_dirty_fields.add('tap_max_count')
        pass
    cdef public object __friendfb_list
    property friendfb_list:
        def __get__(self):
            return self.__friendfb_list
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_friendfb_list(self):
        pass
    cdef public int __friend_total_sp
    property friend_total_sp:
        def __get__(self):
            return self.__friend_total_sp
        def __set__(self, value):
                value = int(value)
                if value != self.__friend_total_sp:
                    self.__friend_total_sp = value
                    if self._initialized:
                        self.touch_friend_total_sp()

    cpdef touch_friend_total_sp(self):
        self.dirty_fields.add('friend_total_sp')
        pass
    cdef public unicode __cache_friendfbID
    property cache_friendfbID:
        def __get__(self):
            return self.__cache_friendfbID
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__cache_friendfbID:
                    self.__cache_friendfbID = value
                    if self._initialized:
                        self.touch_cache_friendfbID()

    cpdef touch_cache_friendfbID(self):
        self.dirty_fields.add('cache_friendfbID')
        pass
    cdef public int __friendfb_triggered_count
    property friendfb_triggered_count:
        def __get__(self):
            return self.__friendfb_triggered_count
        def __set__(self, value):
                value = int(value)
                if value != self.__friendfb_triggered_count:
                    self.__friendfb_triggered_count = value
                    if self._initialized:
                        self.touch_friendfb_triggered_count()

    cpdef touch_friendfb_triggered_count(self):
        self.dirty_fields.add('friendfb_triggered_count')
        pass
    cdef public int __friendfb_last_trigger_time
    property friendfb_last_trigger_time:
        def __get__(self):
            return self.__friendfb_last_trigger_time
        def __set__(self, value):
                value = int(value)
                if value != self.__friendfb_last_trigger_time:
                    self.__friendfb_last_trigger_time = value
                    if self._initialized:
                        self.touch_friendfb_last_trigger_time()

    cpdef touch_friendfb_last_trigger_time(self):
        self.dirty_fields.add('friendfb_last_trigger_time')
        pass
    cdef public int __friendfb_last_trigger_fbID
    property friendfb_last_trigger_fbID:
        def __get__(self):
            return self.__friendfb_last_trigger_fbID
        def __set__(self, value):
                value = int(value)
                if value != self.__friendfb_last_trigger_fbID:
                    self.__friendfb_last_trigger_fbID = value
                    if self._initialized:
                        self.touch_friendfb_last_trigger_fbID()

    cpdef touch_friendfb_last_trigger_fbID(self):
        self.dirty_fields.add('friendfb_last_trigger_fbID')
        pass
    cdef public int __friendfb_used_count_ts
    property friendfb_used_count_ts:
        def __get__(self):
            return self.__friendfb_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__friendfb_used_count_ts:
                    self.__friendfb_used_count_ts = value
                    if self._initialized:
                        self.touch_friendfb_used_count_ts()

    cpdef touch_friendfb_used_count_ts(self):
        self.dirty_fields.add('friendfb_used_count_ts')
        pass
    cdef public int __friendfb_used_count
    property friendfb_used_count:
        def __get__(self):
            return self.__friendfb_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__friendfb_used_count:
                    self.__friendfb_used_count = value
                    if self._initialized:
                        self.touch_friendfb_used_count()

    cpdef touch_friendfb_used_count(self):
        self.dirty_fields.add('friendfb_used_count')
        self.__friendfb_remain_count = None
        self.clear_friendfb_remain_count()
        pass
    cdef public int __friendfb_kill_count
    property friendfb_kill_count:
        def __get__(self):
            return self.__friendfb_kill_count
        def __set__(self, value):
                value = int(value)
                if value != self.__friendfb_kill_count:
                    if self._initialized:
                        for callback in type(self)._listeners_friendfb_kill_count:
                            callback(self, value)
                    self.__friendfb_kill_count = value
                    if self._initialized:
                        self.touch_friendfb_kill_count()

    cpdef touch_friendfb_kill_count(self):
        self.dirty_fields.add('friendfb_kill_count')
        if self._initialized:
            value = self.friendfb_kill_count
            for callback in type(self)._listeners_friendfb_kill_count:
                callback(self, value)
        pass
    cdef public object __friendfb_deads
    property friendfb_deads:
        def __get__(self):
            return self.__friendfb_deads
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_friendfb_deads(self):
        pass
    cdef public object __friendfb_reborn_counts
    property friendfb_reborn_counts:
        def __get__(self):
            return self.__friendfb_reborn_counts
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_friendfb_reborn_counts(self):
        pass
    cdef public object __friendfb_damages
    property friendfb_damages:
        def __get__(self):
            return self.__friendfb_damages
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_friendfb_damages(self):
        pass
    cdef public int __friendfb_buff
    property friendfb_buff:
        def __get__(self):
            return self.__friendfb_buff
        def __set__(self, value):
                value = int(value)
                if value != self.__friendfb_buff:
                    self.__friendfb_buff = value
                    if self._initialized:
                        self.touch_friendfb_buff()

    cpdef touch_friendfb_buff(self):
        self.dirty_fields.add('friendfb_buff')
        self.sync_dirty_fields.add('friendfb_buff')
        pass
    cdef public object __friendfb_deadtimes
    property friendfb_deadtimes:
        def __get__(self):
            return self.__friendfb_deadtimes
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_friendfb_deadtimes(self):
        pass
    cdef public object __malls
    property malls:
        def __get__(self):
            return self.__malls
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_malls(self):
        pass
    cdef public object __mall_times
    property mall_times:
        def __get__(self):
            return self.__mall_times
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_mall_times(self):
        pass
    cdef public object __mall_limits
    property mall_limits:
        def __get__(self):
            return self.__mall_limits
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'mall_limits', self.touch_mall_limits)
                if value != self.__mall_limits:
                    self.__mall_limits = value
                    if self._initialized:
                        self.touch_mall_limits()

    cpdef touch_mall_limits(self):
        self.dirty_fields.add('mall_limits')
        pass
    cdef public int __mall_refresh_times_ts
    property mall_refresh_times_ts:
        def __get__(self):
            return self.__mall_refresh_times_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__mall_refresh_times_ts:
                    self.__mall_refresh_times_ts = value
                    if self._initialized:
                        self.touch_mall_refresh_times_ts()

    cpdef touch_mall_refresh_times_ts(self):
        self.dirty_fields.add('mall_refresh_times_ts')
        pass
    cdef public object __mall_refresh_times
    property mall_refresh_times:
        def __get__(self):
            return self.__mall_refresh_times
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'mall_refresh_times', self.touch_mall_refresh_times)
                if value != self.__mall_refresh_times:
                    self.__mall_refresh_times = value
                    if self._initialized:
                        self.touch_mall_refresh_times()

    cpdef touch_mall_refresh_times(self):
        self.dirty_fields.add('mall_refresh_times')
        pass
    cdef public object __mall_last_refresh
    property mall_last_refresh:
        def __get__(self):
            return self.__mall_last_refresh
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'mall_last_refresh', self.touch_mall_last_refresh)
                if value != self.__mall_last_refresh:
                    self.__mall_last_refresh = value
                    if self._initialized:
                        self.touch_mall_last_refresh()

    cpdef touch_mall_last_refresh(self):
        self.dirty_fields.add('mall_last_refresh')
        pass
    cdef public object __mall_silver_opened
    property mall_silver_opened:
        def __get__(self):
            return self.__mall_silver_opened
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__mall_silver_opened:
                    self.__mall_silver_opened = value
                    if self._initialized:
                        self.touch_mall_silver_opened()

    cpdef touch_mall_silver_opened(self):
        self.dirty_fields.add('mall_silver_opened')
        self.sync_dirty_fields.add('mall_silver_opened')
        self.__mall_silver_open_cost = None
        self.clear_mall_silver_open_cost()
        pass
    cdef public int __mall_silver_open_remain
    property mall_silver_open_remain:
        def __get__(self):
            return self.__mall_silver_open_remain
        def __set__(self, value):
                value = int(value)
                if value != self.__mall_silver_open_remain:
                    self.__mall_silver_open_remain = value
                    if self._initialized:
                        self.touch_mall_silver_open_remain()

    cpdef touch_mall_silver_open_remain(self):
        self.dirty_fields.add('mall_silver_open_remain')
        self.sync_dirty_fields.add('mall_silver_open_remain')
        pass
    cdef public object __mall_golden_opened
    property mall_golden_opened:
        def __get__(self):
            return self.__mall_golden_opened
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__mall_golden_opened:
                    self.__mall_golden_opened = value
                    if self._initialized:
                        self.touch_mall_golden_opened()

    cpdef touch_mall_golden_opened(self):
        self.dirty_fields.add('mall_golden_opened')
        self.sync_dirty_fields.add('mall_golden_opened')
        self.__mall_golden_open_cost = None
        self.clear_mall_golden_open_cost()
        pass
    cdef public int __mall_golden_open_remain
    property mall_golden_open_remain:
        def __get__(self):
            return self.__mall_golden_open_remain
        def __set__(self, value):
                value = int(value)
                if value != self.__mall_golden_open_remain:
                    self.__mall_golden_open_remain = value
                    if self._initialized:
                        self.touch_mall_golden_open_remain()

    cpdef touch_mall_golden_open_remain(self):
        self.dirty_fields.add('mall_golden_open_remain')
        self.sync_dirty_fields.add('mall_golden_open_remain')
        pass
    cdef public int __shopping
    property shopping:
        def __get__(self):
            return self.__shopping
        def __set__(self, value):
                value = int(value)
                if value != self.__shopping:
                    self.__shopping = value
                    if self._initialized:
                        self.touch_shopping()

    cpdef touch_shopping(self):
        self.dirty_fields.add('shopping')
        self.sync_dirty_fields.add('shopping')
        pass
    cdef public object __vip_packs_limits
    property vip_packs_limits:
        def __get__(self):
            return self.__vip_packs_limits
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'vip_packs_limits', self.touch_vip_packs_limits)
                if value != self.__vip_packs_limits:
                    self.__vip_packs_limits = value
                    if self._initialized:
                        self.touch_vip_packs_limits()

    cpdef touch_vip_packs_limits(self):
        self.dirty_fields.add('vip_packs_limits')
        pass
    cdef public int __vip_packs_today_bought_count_ts
    property vip_packs_today_bought_count_ts:
        def __get__(self):
            return self.__vip_packs_today_bought_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__vip_packs_today_bought_count_ts:
                    self.__vip_packs_today_bought_count_ts = value
                    if self._initialized:
                        self.touch_vip_packs_today_bought_count_ts()

    cpdef touch_vip_packs_today_bought_count_ts(self):
        self.dirty_fields.add('vip_packs_today_bought_count_ts')
        pass
    cdef public int __vip_packs_today_bought_count
    property vip_packs_today_bought_count:
        def __get__(self):
            return self.__vip_packs_today_bought_count
        def __set__(self, value):
                value = int(value)
                if value != self.__vip_packs_today_bought_count:
                    self.__vip_packs_today_bought_count = value
                    if self._initialized:
                        self.touch_vip_packs_today_bought_count()

    cpdef touch_vip_packs_today_bought_count(self):
        self.dirty_fields.add('vip_packs_today_bought_count')
        self.__vip_packs_flag = None
        self.clear_vip_packs_flag()
        pass
    cdef public object __vip_packs_limits_reset_flag
    property vip_packs_limits_reset_flag:
        def __get__(self):
            return self.__vip_packs_limits_reset_flag
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__vip_packs_limits_reset_flag:
                    self.__vip_packs_limits_reset_flag = value
                    if self._initialized:
                        self.touch_vip_packs_limits_reset_flag()

    cpdef touch_vip_packs_limits_reset_flag(self):
        self.dirty_fields.add('vip_packs_limits_reset_flag')
        pass
    cdef public int __wish_used_count
    property wish_used_count:
        def __get__(self):
            return self.__wish_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__wish_used_count:
                    self.__wish_used_count = value
                    if self._initialized:
                        self.touch_wish_used_count()

    cpdef touch_wish_used_count(self):
        self.dirty_fields.add('wish_used_count')
        self.__wish_rest_count = None
        self.clear_wish_rest_count()
        pass
    cdef public int __wish_experience_time
    property wish_experience_time:
        def __get__(self):
            return self.__wish_experience_time
        def __set__(self, value):
                value = int(value)
                if value != self.__wish_experience_time:
                    self.__wish_experience_time = value
                    if self._initialized:
                        self.touch_wish_experience_time()

    cpdef touch_wish_experience_time(self):
        self.dirty_fields.add('wish_experience_time')
        self.sync_dirty_fields.add('wish_experience_time')
        pass
    cdef public int __wish_last_reset_time
    property wish_last_reset_time:
        def __get__(self):
            return self.__wish_last_reset_time
        def __set__(self, value):
                value = int(value)
                if value != self.__wish_last_reset_time:
                    self.__wish_last_reset_time = value
                    if self._initialized:
                        self.touch_wish_last_reset_time()

    cpdef touch_wish_last_reset_time(self):
        self.dirty_fields.add('wish_last_reset_time')
        pass
    cdef public int __weeks_acc_recharge_amount
    property weeks_acc_recharge_amount:
        def __get__(self):
            return self.__weeks_acc_recharge_amount
        def __set__(self, value):
                value = int(value)
                if value != self.__weeks_acc_recharge_amount:
                    self.__weeks_acc_recharge_amount = value
                    if self._initialized:
                        self.touch_weeks_acc_recharge_amount()

    cpdef touch_weeks_acc_recharge_amount(self):
        self.dirty_fields.add('weeks_acc_recharge_amount')
        self.sync_dirty_fields.add('weeks_acc_recharge_amount')
        pass
    cdef public int __weeks_acc_recharge_last_clean_time
    property weeks_acc_recharge_last_clean_time:
        def __get__(self):
            return self.__weeks_acc_recharge_last_clean_time
        def __set__(self, value):
                value = int(value)
                if value != self.__weeks_acc_recharge_last_clean_time:
                    self.__weeks_acc_recharge_last_clean_time = value
                    if self._initialized:
                        self.touch_weeks_acc_recharge_last_clean_time()

    cpdef touch_weeks_acc_recharge_last_clean_time(self):
        self.dirty_fields.add('weeks_acc_recharge_last_clean_time')
        pass
    cdef public int __daily_acc_recharge_amount_ts
    property daily_acc_recharge_amount_ts:
        def __get__(self):
            return self.__daily_acc_recharge_amount_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_acc_recharge_amount_ts:
                    self.__daily_acc_recharge_amount_ts = value
                    if self._initialized:
                        self.touch_daily_acc_recharge_amount_ts()

    cpdef touch_daily_acc_recharge_amount_ts(self):
        self.dirty_fields.add('daily_acc_recharge_amount_ts')
        pass
    cdef public int __daily_acc_recharge_amount
    property daily_acc_recharge_amount:
        def __get__(self):
            return self.__daily_acc_recharge_amount
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_acc_recharge_amount:
                    self.__daily_acc_recharge_amount = value
                    if self._initialized:
                        self.touch_daily_acc_recharge_amount()

    cpdef touch_daily_acc_recharge_amount(self):
        self.dirty_fields.add('daily_acc_recharge_amount')
        self.sync_dirty_fields.add('daily_acc_recharge_amount')
        pass
    cdef public int __cycle_acc_recharge_amount
    property cycle_acc_recharge_amount:
        def __get__(self):
            return self.__cycle_acc_recharge_amount
        def __set__(self, value):
                value = int(value)
                if value != self.__cycle_acc_recharge_amount:
                    self.__cycle_acc_recharge_amount = value
                    if self._initialized:
                        self.touch_cycle_acc_recharge_amount()

    cpdef touch_cycle_acc_recharge_amount(self):
        self.dirty_fields.add('cycle_acc_recharge_amount')
        self.sync_dirty_fields.add('cycle_acc_recharge_amount')
        pass
    cdef public int __cycle_acc_recharge_last_clean_time
    property cycle_acc_recharge_last_clean_time:
        def __get__(self):
            return self.__cycle_acc_recharge_last_clean_time
        def __set__(self, value):
                value = int(value)
                if value != self.__cycle_acc_recharge_last_clean_time:
                    self.__cycle_acc_recharge_last_clean_time = value
                    if self._initialized:
                        self.touch_cycle_acc_recharge_last_clean_time()

    cpdef touch_cycle_acc_recharge_last_clean_time(self):
        self.dirty_fields.add('cycle_acc_recharge_last_clean_time')
        pass
    cdef public int __daily_acc_recharge_rewards_ts
    property daily_acc_recharge_rewards_ts:
        def __get__(self):
            return self.__daily_acc_recharge_rewards_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_acc_recharge_rewards_ts:
                    self.__daily_acc_recharge_rewards_ts = value
                    if self._initialized:
                        self.touch_daily_acc_recharge_rewards_ts()

    cpdef touch_daily_acc_recharge_rewards_ts(self):
        self.dirty_fields.add('daily_acc_recharge_rewards_ts')
        pass
    cdef public object __daily_acc_recharge_rewards
    property daily_acc_recharge_rewards:
        def __get__(self):
            return self.__daily_acc_recharge_rewards
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'daily_acc_recharge_rewards', self.touch_daily_acc_recharge_rewards)
                if value != self.__daily_acc_recharge_rewards:
                    self.__daily_acc_recharge_rewards = value
                    if self._initialized:
                        self.touch_daily_acc_recharge_rewards()

    cpdef touch_daily_acc_recharge_rewards(self):
        self.dirty_fields.add('daily_acc_recharge_rewards')
        self.__daily_acc_recharge_can_receive = None
        self.clear_daily_acc_recharge_can_receive()
        pass
    cdef public object __cycle_acc_recharge_rewards
    property cycle_acc_recharge_rewards:
        def __get__(self):
            return self.__cycle_acc_recharge_rewards
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'cycle_acc_recharge_rewards', self.touch_cycle_acc_recharge_rewards)
                if value != self.__cycle_acc_recharge_rewards:
                    self.__cycle_acc_recharge_rewards = value
                    if self._initialized:
                        self.touch_cycle_acc_recharge_rewards()

    cpdef touch_cycle_acc_recharge_rewards(self):
        self.dirty_fields.add('cycle_acc_recharge_rewards')
        self.__cycle_acc_recharge_can_receive = None
        self.clear_cycle_acc_recharge_can_receive()
        pass
    cdef public object __weeks_acc_recharge_rewards
    property weeks_acc_recharge_rewards:
        def __get__(self):
            return self.__weeks_acc_recharge_rewards
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'weeks_acc_recharge_rewards', self.touch_weeks_acc_recharge_rewards)
                if value != self.__weeks_acc_recharge_rewards:
                    self.__weeks_acc_recharge_rewards = value
                    if self._initialized:
                        self.touch_weeks_acc_recharge_rewards()

    cpdef touch_weeks_acc_recharge_rewards(self):
        self.dirty_fields.add('weeks_acc_recharge_rewards')
        self.__weeks_acc_recharge_can_receive = None
        self.clear_weeks_acc_recharge_can_receive()
        pass
    cdef public object __month_acc_recharge_rewards
    property month_acc_recharge_rewards:
        def __get__(self):
            return self.__month_acc_recharge_rewards
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'month_acc_recharge_rewards', self.touch_month_acc_recharge_rewards)
                if value != self.__month_acc_recharge_rewards:
                    self.__month_acc_recharge_rewards = value
                    if self._initialized:
                        self.touch_month_acc_recharge_rewards()

    cpdef touch_month_acc_recharge_rewards(self):
        self.dirty_fields.add('month_acc_recharge_rewards')
        self.__month_acc_recharge_can_receive = None
        self.clear_month_acc_recharge_can_receive()
        pass
    cdef public int __month_acc_recharge_amount
    property month_acc_recharge_amount:
        def __get__(self):
            return self.__month_acc_recharge_amount
        def __set__(self, value):
                value = int(value)
                if value != self.__month_acc_recharge_amount:
                    self.__month_acc_recharge_amount = value
                    if self._initialized:
                        self.touch_month_acc_recharge_amount()

    cpdef touch_month_acc_recharge_amount(self):
        self.dirty_fields.add('month_acc_recharge_amount')
        self.sync_dirty_fields.add('month_acc_recharge_amount')
        pass
    cdef public int __month_acc_recharge_last_clean_time
    property month_acc_recharge_last_clean_time:
        def __get__(self):
            return self.__month_acc_recharge_last_clean_time
        def __set__(self, value):
                value = int(value)
                if value != self.__month_acc_recharge_last_clean_time:
                    self.__month_acc_recharge_last_clean_time = value
                    if self._initialized:
                        self.touch_month_acc_recharge_last_clean_time()

    cpdef touch_month_acc_recharge_last_clean_time(self):
        self.dirty_fields.add('month_acc_recharge_last_clean_time')
        pass
    cdef public object __fund_bought_flag
    property fund_bought_flag:
        def __get__(self):
            return self.__fund_bought_flag
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__fund_bought_flag:
                    self.__fund_bought_flag = value
                    if self._initialized:
                        self.touch_fund_bought_flag()

    cpdef touch_fund_bought_flag(self):
        self.dirty_fields.add('fund_bought_flag')
        self.sync_dirty_fields.add('fund_bought_flag')
        self.__fund_open_rewards_can_receive = None
        self.clear_fund_open_rewards_can_receive()
        pass
    cdef public object __fund_rewards_received
    property fund_rewards_received:
        def __get__(self):
            return self.__fund_rewards_received
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'fund_rewards_received', self.touch_fund_rewards_received)
                if value != self.__fund_rewards_received:
                    self.__fund_rewards_received = value
                    if self._initialized:
                        self.touch_fund_rewards_received()

    cpdef touch_fund_rewards_received(self):
        self.dirty_fields.add('fund_rewards_received')
        self.__fund_open_rewards_can_receive = None
        self.__fund_full_rewards_can_receive = None
        self.clear_fund_open_rewards_can_receive()
        self.clear_fund_full_rewards_can_receive()
        pass
    cdef public int __fund_reset_time
    property fund_reset_time:
        def __get__(self):
            return self.__fund_reset_time
        def __set__(self, value):
                value = int(value)
                if value != self.__fund_reset_time:
                    self.__fund_reset_time = value
                    if self._initialized:
                        self.touch_fund_reset_time()

    cpdef touch_fund_reset_time(self):
        self.dirty_fields.add('fund_reset_time')
        pass
    cdef public int __check_in_over_count
    property check_in_over_count:
        def __get__(self):
            return self.__check_in_over_count
        def __set__(self, value):
                value = int(value)
                if value != self.__check_in_over_count:
                    self.__check_in_over_count = value
                    if self._initialized:
                        self.touch_check_in_over_count()

    cpdef touch_check_in_over_count(self):
        self.dirty_fields.add('check_in_over_count')
        self.sync_dirty_fields.add('check_in_over_count')
        pass
    cdef public int __check_in_used_count
    property check_in_used_count:
        def __get__(self):
            return self.__check_in_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__check_in_used_count:
                    self.__check_in_used_count = value
                    if self._initialized:
                        self.touch_check_in_used_count()

    cpdef touch_check_in_used_count(self):
        self.dirty_fields.add('check_in_used_count')
        self.sync_dirty_fields.add('check_in_used_count')
        self.__check_in_rest_count = None
        self.clear_check_in_rest_count()
        pass
    cdef public int __check_in_today_ts
    property check_in_today_ts:
        def __get__(self):
            return self.__check_in_today_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__check_in_today_ts:
                    self.__check_in_today_ts = value
                    if self._initialized:
                        self.touch_check_in_today_ts()

    cpdef touch_check_in_today_ts(self):
        self.dirty_fields.add('check_in_today_ts')
        pass
    cdef public object __check_in_today
    property check_in_today:
        def __get__(self):
            return self.__check_in_today
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__check_in_today:
                    self.__check_in_today = value
                    if self._initialized:
                        self.touch_check_in_today()

    cpdef touch_check_in_today(self):
        self.dirty_fields.add('check_in_today')
        self.sync_dirty_fields.add('check_in_today')
        self.__check_in_rest_count = None
        self.clear_check_in_rest_count()
        pass
    cdef public object __check_in_last_time
    property check_in_last_time:
        def __get__(self):
            return self.__check_in_last_time
        def __set__(self, value):
                value = value
                if value != self.__check_in_last_time:
                    self.__check_in_last_time = value
                    if self._initialized:
                        self.touch_check_in_last_time()

    cpdef touch_check_in_last_time(self):
        self.dirty_fields.add('check_in_last_time')
        pass
    cdef public int __timed_store_cd
    property timed_store_cd:
        def __get__(self):
            return self.__timed_store_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__timed_store_cd:
                    self.__timed_store_cd = value
                    if self._initialized:
                        self.touch_timed_store_cd()

    cpdef touch_timed_store_cd(self):
        self.dirty_fields.add('timed_store_cd')
        self.sync_dirty_fields.add('timed_store_cd')
        pass
    cdef public int __timed_store_id
    property timed_store_id:
        def __get__(self):
            return self.__timed_store_id
        def __set__(self, value):
                value = int(value)
                if value != self.__timed_store_id:
                    self.__timed_store_id = value
                    if self._initialized:
                        self.touch_timed_store_id()

    cpdef touch_timed_store_id(self):
        self.dirty_fields.add('timed_store_id')
        pass
    cdef public int __trigger_event
    property trigger_event:
        def __get__(self):
            return self.__trigger_event
        def __set__(self, value):
                value = int(value)
                if value != self.__trigger_event:
                    self.__trigger_event = value
                    if self._initialized:
                        self.touch_trigger_event()

    cpdef touch_trigger_event(self):
        self.dirty_fields.add('trigger_event')
        pass
    cdef public int __trigger_event_sp
    property trigger_event_sp:
        def __get__(self):
            return self.__trigger_event_sp
        def __set__(self, value):
                value = int(value)
                if value != self.__trigger_event_sp:
                    self.__trigger_event_sp = value
                    if self._initialized:
                        self.touch_trigger_event_sp()

    cpdef touch_trigger_event_sp(self):
        self.dirty_fields.add('trigger_event_sp')
        pass
    cdef public object __trigger_chests
    property trigger_chests:
        def __get__(self):
            return self.__trigger_chests
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'trigger_chests', self.touch_trigger_chests)
                if value != self.__trigger_chests:
                    self.__trigger_chests = value
                    if self._initialized:
                        self.touch_trigger_chests()

    cpdef touch_trigger_chests(self):
        self.dirty_fields.add('trigger_chests')
        pass
    cdef public int __trigger_tasks_ts
    property trigger_tasks_ts:
        def __get__(self):
            return self.__trigger_tasks_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__trigger_tasks_ts:
                    self.__trigger_tasks_ts = value
                    if self._initialized:
                        self.touch_trigger_tasks_ts()

    cpdef touch_trigger_tasks_ts(self):
        self.dirty_fields.add('trigger_tasks_ts')
        pass
    cdef public object __trigger_tasks
    property trigger_tasks:
        def __get__(self):
            return self.__trigger_tasks
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'trigger_tasks', self.touch_trigger_tasks)
                if value != self.__trigger_tasks:
                    self.__trigger_tasks = value
                    if self._initialized:
                        self.touch_trigger_tasks()

    cpdef touch_trigger_tasks(self):
        self.dirty_fields.add('trigger_tasks')
        pass
    cdef public object __monthly_card_time
    property monthly_card_time:
        def __get__(self):
            return self.__monthly_card_time
        def __set__(self, value):
                value = value
                if value != self.__monthly_card_time:
                    self.__monthly_card_time = value
                    if self._initialized:
                        self.touch_monthly_card_time()

    cpdef touch_monthly_card_time(self):
        self.dirty_fields.add('monthly_card_time')
        self.__monthly_card = None
        self.clear_monthly_card()
        pass
    cdef public int __monthly_card_received_ts
    property monthly_card_received_ts:
        def __get__(self):
            return self.__monthly_card_received_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__monthly_card_received_ts:
                    self.__monthly_card_received_ts = value
                    if self._initialized:
                        self.touch_monthly_card_received_ts()

    cpdef touch_monthly_card_received_ts(self):
        self.dirty_fields.add('monthly_card_received_ts')
        pass
    cdef public object __monthly_card_received
    property monthly_card_received:
        def __get__(self):
            return self.__monthly_card_received
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__monthly_card_received:
                    self.__monthly_card_received = value
                    if self._initialized:
                        self.touch_monthly_card_received()

    cpdef touch_monthly_card_received(self):
        self.dirty_fields.add('monthly_card_received')
        self.sync_dirty_fields.add('monthly_card_received')
        self.__monthly_card = None
        self.clear_monthly_card()
        pass
    cdef public int __monthly_card_acc_amount
    property monthly_card_acc_amount:
        def __get__(self):
            return self.__monthly_card_acc_amount
        def __set__(self, value):
                value = int(value)
                if value != self.__monthly_card_acc_amount:
                    self.__monthly_card_acc_amount = value
                    if self._initialized:
                        self.touch_monthly_card_acc_amount()

    cpdef touch_monthly_card_acc_amount(self):
        self.dirty_fields.add('monthly_card_acc_amount')
        self.__monthly_card_remain_amount = None
        self.clear_monthly_card_remain_amount()
        pass
    cdef public object __skip_guide
    property skip_guide:
        def __get__(self):
            return self.__skip_guide
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__skip_guide:
                    self.__skip_guide = value
                    if self._initialized:
                        self.touch_skip_guide()

    cpdef touch_skip_guide(self):
        self.dirty_fields.add('skip_guide')
        self.sync_dirty_fields.add('skip_guide')
        pass
    cdef public object __spar_counts
    property spar_counts:
        def __get__(self):
            return self.__spar_counts
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'spar_counts', self.touch_spar_counts)
                if value != self.__spar_counts:
                    self.__spar_counts = value
                    if self._initialized:
                        self.touch_spar_counts()

    cpdef touch_spar_counts(self):
        self.dirty_fields.add('spar_counts')
        pass
    cdef public unicode __username_alias
    property username_alias:
        def __get__(self):
            return self.__username_alias
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__username_alias:
                    self.__username_alias = value
                    if self._initialized:
                        self.touch_username_alias()

    cpdef touch_username_alias(self):
        self.dirty_fields.add('username_alias')
        pass
    cdef public object __chat_blocked
    property chat_blocked:
        def __get__(self):
            return self.__chat_blocked
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__chat_blocked:
                    self.__chat_blocked = value
                    if self._initialized:
                        self.touch_chat_blocked()

    cpdef touch_chat_blocked(self):
        self.dirty_fields.add('chat_blocked')
        pass
    cdef public int __lock_level
    property lock_level:
        def __get__(self):
            return self.__lock_level
        def __set__(self, value):
                value = int(value)
                if value != self.__lock_level:
                    self.__lock_level = value
                    if self._initialized:
                        self.touch_lock_level()

    cpdef touch_lock_level(self):
        self.dirty_fields.add('lock_level')
        pass
    cdef public unicode __channel
    property channel:
        def __get__(self):
            return self.__channel
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__channel:
                    self.__channel = value
                    if self._initialized:
                        self.touch_channel()

    cpdef touch_channel(self):
        self.dirty_fields.add('channel')
        pass
    cdef public int __point
    property point:
        def __get__(self):
            return self.__point
        def __set__(self, value):
                value = int(value)
                if value != self.__point:
                    self.__point = value
                    if self._initialized:
                        self.touch_point()

    cpdef touch_point(self):
        self.dirty_fields.add('point')
        self.sync_dirty_fields.add('point')
        self.__power = None
        self.__point_power = None
        self.__point_addition = None
        self.__gems_power = None
        self.clear_power()
        self.clear_point_power()
        self.clear_point_addition()
        self.clear_gems_power()
        pass
    cdef public int __stone
    property stone:
        def __get__(self):
            return self.__stone
        def __set__(self, value):
                value = int(value)
                if value != self.__stone:
                    self.__stone = value
                    if self._initialized:
                        self.touch_stone()

    cpdef touch_stone(self):
        self.dirty_fields.add('stone')
        self.sync_dirty_fields.add('stone')
        pass
    cdef public int __enchant_free_used_count_ts
    property enchant_free_used_count_ts:
        def __get__(self):
            return self.__enchant_free_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__enchant_free_used_count_ts:
                    self.__enchant_free_used_count_ts = value
                    if self._initialized:
                        self.touch_enchant_free_used_count_ts()

    cpdef touch_enchant_free_used_count_ts(self):
        self.dirty_fields.add('enchant_free_used_count_ts')
        pass
    cdef public int __enchant_free_used_count
    property enchant_free_used_count:
        def __get__(self):
            return self.__enchant_free_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__enchant_free_used_count:
                    self.__enchant_free_used_count = value
                    if self._initialized:
                        self.touch_enchant_free_used_count()

    cpdef touch_enchant_free_used_count(self):
        self.dirty_fields.add('enchant_free_used_count')
        self.__enchant_free_rest_count = None
        self.clear_enchant_free_rest_count()
        pass
    cdef public object __dlc_progress
    property dlc_progress:
        def __get__(self):
            return self.__dlc_progress
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_dlc_progress(self):
        pass
    cdef public object __dlc_helpers
    property dlc_helpers:
        def __get__(self):
            return self.__dlc_helpers
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_dlc_helpers(self):
        pass
    cdef public object __dlc_dispatch
    property dlc_dispatch:
        def __get__(self):
            return self.__dlc_dispatch
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_dlc_dispatch(self):
        pass
    cdef public object __dlc_star_packs_end
    property dlc_star_packs_end:
        def __get__(self):
            return self.__dlc_star_packs_end
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'dlc_star_packs_end', self.touch_dlc_star_packs_end)
                if value != self.__dlc_star_packs_end:
                    self.__dlc_star_packs_end = value
                    if self._initialized:
                        self.touch_dlc_star_packs_end()

    cpdef touch_dlc_star_packs_end(self):
        self.dirty_fields.add('dlc_star_packs_end')
        pass
    cdef public object __dlc_tasks_cd
    property dlc_tasks_cd:
        def __get__(self):
            return self.__dlc_tasks_cd
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'dlc_tasks_cd', self.touch_dlc_tasks_cd)
                if value != self.__dlc_tasks_cd:
                    self.__dlc_tasks_cd = value
                    if self._initialized:
                        self.touch_dlc_tasks_cd()

    cpdef touch_dlc_tasks_cd(self):
        self.dirty_fields.add('dlc_tasks_cd')
        pass
    cdef public object __dlc_detail_cache
    property dlc_detail_cache:
        def __get__(self):
            return self.__dlc_detail_cache
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_dlc_detail_cache(self):
        pass
    cdef public int __count_down_time
    property count_down_time:
        def __get__(self):
            return self.__count_down_time
        def __set__(self, value):
                value = int(value)
                if value != self.__count_down_time:
                    self.__count_down_time = value
                    if self._initialized:
                        self.touch_count_down_time()

    cpdef touch_count_down_time(self):
        self.dirty_fields.add('count_down_time')
        pass
    cdef public int __count_down_index
    property count_down_index:
        def __get__(self):
            return self.__count_down_index
        def __set__(self, value):
                value = int(value)
                if value != self.__count_down_index:
                    self.__count_down_index = value
                    if self._initialized:
                        self.touch_count_down_index()

    cpdef touch_count_down_index(self):
        self.dirty_fields.add('count_down_index')
        self.__count_down_flag = None
        self.clear_count_down_flag()
        pass
    cdef public int __count_down_cd
    property count_down_cd:
        def __get__(self):
            return self.__count_down_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__count_down_cd:
                    self.__count_down_cd = value
                    if self._initialized:
                        self.touch_count_down_cd()

    cpdef touch_count_down_cd(self):
        self.dirty_fields.add('count_down_cd')
        self.sync_dirty_fields.add('count_down_cd')
        pass
    cdef public object __group_applys
    property group_applys:
        def __get__(self):
            return self.__group_applys
        def __set__(self, value):
                value = value
                if value != self.__group_applys:
                    self.__group_applys = value
                    if self._initialized:
                        self.touch_group_applys()

    cpdef touch_group_applys(self):
        self.__group_applys_count = None
        self.clear_group_applys_count()
        pass
    cdef public int __groupID
    property groupID:
        def __get__(self):
            return self.__groupID
        def __set__(self, value):
                value = int(value)
                if value != self.__groupID:
                    self.__groupID = value
                    if self._initialized:
                        self.touch_groupID()

    cpdef touch_groupID(self):
        self.dirty_fields.add('groupID')
        self.sync_dirty_fields.add('groupID')
        pass
    cdef public int __group_total_intimate
    property group_total_intimate:
        def __get__(self):
            return self.__group_total_intimate
        def __set__(self, value):
                value = int(value)
                if value != self.__group_total_intimate:
                    self.__group_total_intimate = value
                    if self._initialized:
                        self.touch_group_total_intimate()

    cpdef touch_group_total_intimate(self):
        self.dirty_fields.add('group_total_intimate')
        self.sync_dirty_fields.add('group_total_intimate')
        pass
    cdef public int __group_last_kicked_time
    property group_last_kicked_time:
        def __get__(self):
            return self.__group_last_kicked_time
        def __set__(self, value):
                value = int(value)
                if value != self.__group_last_kicked_time:
                    self.__group_last_kicked_time = value
                    if self._initialized:
                        self.touch_group_last_kicked_time()

    cpdef touch_group_last_kicked_time(self):
        self.dirty_fields.add('group_last_kicked_time')
        pass
    cdef public int __gve_damage
    property gve_damage:
        def __get__(self):
            return self.__gve_damage
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_damage:
                    self.__gve_damage = value
                    if self._initialized:
                        self.touch_gve_damage()

    cpdef touch_gve_damage(self):
        self.dirty_fields.add('gve_damage')
        self.sync_dirty_fields.add('gve_damage')
        pass
    cdef public int __gve_score
    property gve_score:
        def __get__(self):
            return self.__gve_score
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_score:
                    self.__gve_score = value
                    if self._initialized:
                        self.touch_gve_score()

    cpdef touch_gve_score(self):
        self.dirty_fields.add('gve_score')
        self.sync_dirty_fields.add('gve_score')
        pass
    cdef public int __gve_index
    property gve_index:
        def __get__(self):
            return self.__gve_index
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_index:
                    self.__gve_index = value
                    if self._initialized:
                        self.touch_gve_index()

    cpdef touch_gve_index(self):
        self.dirty_fields.add('gve_index')
        pass
    cdef public int __gve_target
    property gve_target:
        def __get__(self):
            return self.__gve_target
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_target:
                    self.__gve_target = value
                    if self._initialized:
                        self.touch_gve_target()

    cpdef touch_gve_target(self):
        self.dirty_fields.add('gve_target')
        pass
    cdef public int __gve_state
    property gve_state:
        def __get__(self):
            return self.__gve_state
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_state:
                    self.__gve_state = value
                    if self._initialized:
                        self.touch_gve_state()

    cpdef touch_gve_state(self):
        self.dirty_fields.add('gve_state')
        self.sync_dirty_fields.add('gve_state')
        pass
    cdef public int __gve_addition
    property gve_addition:
        def __get__(self):
            return self.__gve_addition
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_addition:
                    self.__gve_addition = value
                    if self._initialized:
                        self.touch_gve_addition()

    cpdef touch_gve_addition(self):
        self.dirty_fields.add('gve_addition')
        self.sync_dirty_fields.add('gve_addition')
        pass
    cdef public int __gve_groupdamage
    property gve_groupdamage:
        def __get__(self):
            return self.__gve_groupdamage
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_groupdamage:
                    self.__gve_groupdamage = value
                    if self._initialized:
                        self.touch_gve_groupdamage()

    cpdef touch_gve_groupdamage(self):
        self.dirty_fields.add('gve_groupdamage')
        self.sync_dirty_fields.add('gve_groupdamage')
        self.__gve_basereward = None
        self.clear_gve_basereward()
        pass
    cdef public int __gve_reborn_rest_count_ts
    property gve_reborn_rest_count_ts:
        def __get__(self):
            return self.__gve_reborn_rest_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_reborn_rest_count_ts:
                    self.__gve_reborn_rest_count_ts = value
                    if self._initialized:
                        self.touch_gve_reborn_rest_count_ts()

    cpdef touch_gve_reborn_rest_count_ts(self):
        self.dirty_fields.add('gve_reborn_rest_count_ts')
        pass
    cdef public int __gve_reborn_rest_count
    property gve_reborn_rest_count:
        def __get__(self):
            return self.__gve_reborn_rest_count
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_reborn_rest_count:
                    self.__gve_reborn_rest_count = value
                    if self._initialized:
                        self.touch_gve_reborn_rest_count()

    cpdef touch_gve_reborn_rest_count(self):
        self.dirty_fields.add('gve_reborn_rest_count')
        self.sync_dirty_fields.add('gve_reborn_rest_count')
        pass
    cdef public int __gve_last_reset_time
    property gve_last_reset_time:
        def __get__(self):
            return self.__gve_last_reset_time
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_last_reset_time:
                    self.__gve_last_reset_time = value
                    if self._initialized:
                        self.touch_gve_last_reset_time()

    cpdef touch_gve_last_reset_time(self):
        self.dirty_fields.add('gve_last_reset_time')
        pass
    cdef public int __gve_buff
    property gve_buff:
        def __get__(self):
            return self.__gve_buff
        def __set__(self, value):
                value = int(value)
                if value != self.__gve_buff:
                    self.__gve_buff = value
                    if self._initialized:
                        self.touch_gve_buff()

    cpdef touch_gve_buff(self):
        self.dirty_fields.add('gve_buff')
        self.sync_dirty_fields.add('gve_buff')
        pass
    cdef public object __gve_ranking_rewards
    property gve_ranking_rewards:
        def __get__(self):
            return self.__gve_ranking_rewards
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_gve_ranking_rewards(self):
        pass
    cdef public unicode __last_region_name
    property last_region_name:
        def __get__(self):
            return self.__last_region_name
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__last_region_name:
                    self.__last_region_name = value
                    if self._initialized:
                        self.touch_last_region_name()

    cpdef touch_last_region_name(self):
        self.dirty_fields.add('last_region_name')
        self.sync_dirty_fields.add('last_region_name')
        pass
    cdef public unicode __cache_fight_verify_code
    property cache_fight_verify_code:
        def __get__(self):
            return self.__cache_fight_verify_code
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__cache_fight_verify_code:
                    self.__cache_fight_verify_code = value
                    if self._initialized:
                        self.touch_cache_fight_verify_code()

    cpdef touch_cache_fight_verify_code(self):
        self.dirty_fields.add('cache_fight_verify_code')
        pass
    cdef public object __cache_fight_response
    property cache_fight_response:
        def __get__(self):
            return self.__cache_fight_response
        def __set__(self, value):
                value = value
                if value != self.__cache_fight_response:
                    self.__cache_fight_response = value
                    if self._initialized:
                        self.touch_cache_fight_response()

    cpdef touch_cache_fight_response(self):
        self.dirty_fields.add('cache_fight_response')
        pass
    cdef public object __boss_campaign_rewards
    property boss_campaign_rewards:
        def __get__(self):
            return self.__boss_campaign_rewards
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_boss_campaign_rewards(self):
        pass
    cdef public int __skillpoint
    property skillpoint:
        def __get__(self):
            return self.__skillpoint
        def __set__(self, value):
                value = int(value)
                if value != self.__skillpoint:
                    self.__skillpoint = value
                    if self._initialized:
                        self.touch_skillpoint()

    cpdef touch_skillpoint(self):
        self.dirty_fields.add('skillpoint')
        self.sync_dirty_fields.add('skillpoint')
        #self.sync_dirty_fields.add('skillpoint_cd')
        pass
    cdef public int __skillpoint_cd
    property skillpoint_cd:
        def __get__(self):
            return self.__skillpoint_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__skillpoint_cd:
                    self.__skillpoint_cd = value
                    if self._initialized:
                        self.touch_skillpoint_cd()

    cpdef touch_skillpoint_cd(self):
        self.dirty_fields.add('skillpoint_cd')
        self.sync_dirty_fields.add('skillpoint_cd')
        pass
    cdef public int __buy_used_skillpoint_count_ts
    property buy_used_skillpoint_count_ts:
        def __get__(self):
            return self.__buy_used_skillpoint_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__buy_used_skillpoint_count_ts:
                    self.__buy_used_skillpoint_count_ts = value
                    if self._initialized:
                        self.touch_buy_used_skillpoint_count_ts()

    cpdef touch_buy_used_skillpoint_count_ts(self):
        self.dirty_fields.add('buy_used_skillpoint_count_ts')
        pass
    cdef public int __buy_used_skillpoint_count
    property buy_used_skillpoint_count:
        def __get__(self):
            return self.__buy_used_skillpoint_count
        def __set__(self, value):
                value = int(value)
                if value != self.__buy_used_skillpoint_count:
                    self.__buy_used_skillpoint_count = value
                    if self._initialized:
                        self.touch_buy_used_skillpoint_count()

    cpdef touch_buy_used_skillpoint_count(self):
        self.dirty_fields.add('buy_used_skillpoint_count')
        self.__buy_rest_skillpoint_count = None
        self.__buy_skillpoint_cost = None
        self.__buy_skillpoint_gain = None
        self.clear_buy_rest_skillpoint_count()
        self.clear_buy_skillpoint_cost()
        self.clear_buy_skillpoint_gain()
        pass
    cdef public int __buy_used_soul_count_ts
    property buy_used_soul_count_ts:
        def __get__(self):
            return self.__buy_used_soul_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__buy_used_soul_count_ts:
                    self.__buy_used_soul_count_ts = value
                    if self._initialized:
                        self.touch_buy_used_soul_count_ts()

    cpdef touch_buy_used_soul_count_ts(self):
        self.dirty_fields.add('buy_used_soul_count_ts')
        pass
    cdef public int __buy_used_soul_count
    property buy_used_soul_count:
        def __get__(self):
            return self.__buy_used_soul_count
        def __set__(self, value):
                value = int(value)
                if value != self.__buy_used_soul_count:
                    self.__buy_used_soul_count = value
                    if self._initialized:
                        self.touch_buy_used_soul_count()

    cpdef touch_buy_used_soul_count(self):
        self.dirty_fields.add('buy_used_soul_count')
        self.__buy_rest_soul_count = None
        self.__buy_soul_cost = None
        self.__buy_soul_gain = None
        self.clear_buy_rest_soul_count()
        self.clear_buy_soul_cost()
        self.clear_buy_soul_gain()
        pass
    cdef public object __swap_targets
    property swap_targets:
        def __get__(self):
            return self.__swap_targets
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'swap_targets', self.touch_swap_targets)
                if value != self.__swap_targets:
                    self.__swap_targets = value
                    if self._initialized:
                        self.touch_swap_targets()

    cpdef touch_swap_targets(self):
        self.dirty_fields.add('swap_targets')
        pass
    cdef public int __swap_cd
    property swap_cd:
        def __get__(self):
            return self.__swap_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__swap_cd:
                    self.__swap_cd = value
                    if self._initialized:
                        self.touch_swap_cd()

    cpdef touch_swap_cd(self):
        self.dirty_fields.add('swap_cd')
        self.sync_dirty_fields.add('swap_cd')
        pass
    cdef public int __swap_used_count_ts
    property swap_used_count_ts:
        def __get__(self):
            return self.__swap_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__swap_used_count_ts:
                    self.__swap_used_count_ts = value
                    if self._initialized:
                        self.touch_swap_used_count_ts()

    cpdef touch_swap_used_count_ts(self):
        self.dirty_fields.add('swap_used_count_ts')
        pass
    cdef public int __swap_used_count
    property swap_used_count:
        def __get__(self):
            return self.__swap_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__swap_used_count:
                    self.__swap_used_count = value
                    if self._initialized:
                        self.touch_swap_used_count()

    cpdef touch_swap_used_count(self):
        self.dirty_fields.add('swap_used_count')
        self.__swap_rest_count = None
        self.clear_swap_rest_count()
        pass
    cdef public int __swap_used_reset_count_ts
    property swap_used_reset_count_ts:
        def __get__(self):
            return self.__swap_used_reset_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__swap_used_reset_count_ts:
                    self.__swap_used_reset_count_ts = value
                    if self._initialized:
                        self.touch_swap_used_reset_count_ts()

    cpdef touch_swap_used_reset_count_ts(self):
        self.dirty_fields.add('swap_used_reset_count_ts')
        pass
    cdef public int __swap_used_reset_count
    property swap_used_reset_count:
        def __get__(self):
            return self.__swap_used_reset_count
        def __set__(self, value):
                value = int(value)
                if value != self.__swap_used_reset_count:
                    self.__swap_used_reset_count = value
                    if self._initialized:
                        self.touch_swap_used_reset_count()

    cpdef touch_swap_used_reset_count(self):
        self.dirty_fields.add('swap_used_reset_count')
        self.__swap_rest_reset_count = None
        self.__swap_reset_count_cost = None
        self.clear_swap_rest_reset_count()
        self.clear_swap_reset_count_cost()
        pass
    cdef public int __swaprank
    property swaprank:
        def __get__(self):
            return self.__swaprank
        def __set__(self, value):
                value = int(value)
                if value != self.__swaprank:
                    self.__swaprank = value
                    if self._initialized:
                        self.touch_swaprank()

    cpdef touch_swaprank(self):
        self.dirty_fields.add('swaprank')
        self.sync_dirty_fields.add('swaprank')
        pass
    cdef public object __swap_history
    property swap_history:
        def __get__(self):
            return self.__swap_history
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_swap_history(self):
        pass
    cdef public object __swap_fight_history
    property swap_fight_history:
        def __get__(self):
            return self.__swap_fight_history
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_swap_fight_history(self):
        pass
    cdef public int __swap_win_count
    property swap_win_count:
        def __get__(self):
            return self.__swap_win_count
        def __set__(self, value):
                value = int(value)
                if value != self.__swap_win_count:
                    self.__swap_win_count = value
                    if self._initialized:
                        self.touch_swap_win_count()

    cpdef touch_swap_win_count(self):
        self.dirty_fields.add('swap_win_count')
        self.sync_dirty_fields.add('swap_win_count')
        pass
    cdef public int __swapmaxrank
    property swapmaxrank:
        def __get__(self):
            return self.__swapmaxrank
        def __set__(self, value):
                value = int(value)
                if value != self.__swapmaxrank:
                    self.__swapmaxrank = value
                    if self._initialized:
                        self.touch_swapmaxrank()

    cpdef touch_swapmaxrank(self):
        self.dirty_fields.add('swapmaxrank')
        pass
    cdef public int __swap_lock_cd
    property swap_lock_cd:
        def __get__(self):
            return self.__swap_lock_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__swap_lock_cd:
                    self.__swap_lock_cd = value
                    if self._initialized:
                        self.touch_swap_lock_cd()

    cpdef touch_swap_lock_cd(self):
        self.dirty_fields.add('swap_lock_cd')
        pass
    cdef public int __swap_register_time
    property swap_register_time:
        def __get__(self):
            return self.__swap_register_time
        def __set__(self, value):
                value = int(value)
                if value != self.__swap_register_time:
                    self.__swap_register_time = value
                    if self._initialized:
                        self.touch_swap_register_time()

    cpdef touch_swap_register_time(self):
        self.dirty_fields.add('swap_register_time')
        pass
    cdef public int __ball
    property ball:
        def __get__(self):
            return self.__ball
        def __set__(self, value):
                value = int(value)
                if value != self.__ball:
                    self.__ball = value
                    if self._initialized:
                        self.touch_ball()

    cpdef touch_ball(self):
        self.dirty_fields.add('ball')
        self.sync_dirty_fields.add('ball')
        pass
    cdef public int __maze_step_count
    property maze_step_count:
        def __get__(self):
            return self.__maze_step_count
        def __set__(self, value):
                value = int(value)
                if value != self.__maze_step_count:
                    self.__maze_step_count = value
                    if self._initialized:
                        self.touch_maze_step_count()

    cpdef touch_maze_step_count(self):
        self.dirty_fields.add('maze_step_count')
        self.sync_dirty_fields.add('maze_step_count')
        pass
    cdef public int __maze_rest_count
    property maze_rest_count:
        def __get__(self):
            return self.__maze_rest_count
        def __set__(self, value):
                value = int(value)
                if value != self.__maze_rest_count:
                    self.__maze_rest_count = value
                    if self._initialized:
                        self.touch_maze_rest_count()

    cpdef touch_maze_rest_count(self):
        self.dirty_fields.add('maze_rest_count')
        self.sync_dirty_fields.add('maze_rest_count')
        #self.sync_dirty_fields.add('maze_count_cd')
        pass
    cdef public int __maze_count_cd
    property maze_count_cd:
        def __get__(self):
            return self.__maze_count_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__maze_count_cd:
                    self.__maze_count_cd = value
                    if self._initialized:
                        self.touch_maze_count_cd()

    cpdef touch_maze_count_cd(self):
        self.dirty_fields.add('maze_count_cd')
        self.sync_dirty_fields.add('maze_count_cd')
        pass
    cdef public int __money_rest_pool
    property money_rest_pool:
        def __get__(self):
            return self.__money_rest_pool
        def __set__(self, value):
                value = int(value)
                if value != self.__money_rest_pool:
                    self.__money_rest_pool = value
                    if self._initialized:
                        self.touch_money_rest_pool()

    cpdef touch_money_rest_pool(self):
        self.dirty_fields.add('money_rest_pool')
        self.sync_dirty_fields.add('money_rest_pool')
        pass
    cdef public object __mazes
    property mazes:
        def __get__(self):
            return self.__mazes
        def __set__(self, value):
                value = value
                if value != self.__mazes:
                    self.__mazes = value
                    if self._initialized:
                        self.touch_mazes()

    cpdef touch_mazes(self):
        self.dirty_fields.add('mazes')
        self.__maze_time_flag = None
        self.clear_maze_time_flag()
        pass
    cdef public int __online_packs_cd
    property online_packs_cd:
        def __get__(self):
            return self.__online_packs_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__online_packs_cd:
                    self.__online_packs_cd = value
                    if self._initialized:
                        self.touch_online_packs_cd()

    cpdef touch_online_packs_cd(self):
        self.dirty_fields.add('online_packs_cd')
        self.sync_dirty_fields.add('online_packs_cd')
        pass
    cdef public int __online_packs_index
    property online_packs_index:
        def __get__(self):
            return self.__online_packs_index
        def __set__(self, value):
                value = int(value)
                if value != self.__online_packs_index:
                    self.__online_packs_index = value
                    if self._initialized:
                        self.touch_online_packs_index()

    cpdef touch_online_packs_index(self):
        self.dirty_fields.add('online_packs_index')
        pass
    cdef public int __online_packs_last_recv
    property online_packs_last_recv:
        def __get__(self):
            return self.__online_packs_last_recv
        def __set__(self, value):
                value = int(value)
                if value != self.__online_packs_last_recv:
                    self.__online_packs_last_recv = value
                    if self._initialized:
                        self.touch_online_packs_last_recv()

    cpdef touch_online_packs_last_recv(self):
        self.dirty_fields.add('online_packs_last_recv')
        pass
    cdef public int __online_packs_reset
    property online_packs_reset:
        def __get__(self):
            return self.__online_packs_reset
        def __set__(self, value):
                value = int(value)
                if value != self.__online_packs_reset:
                    self.__online_packs_reset = value
                    if self._initialized:
                        self.touch_online_packs_reset()

    cpdef touch_online_packs_reset(self):
        self.dirty_fields.add('online_packs_reset')
        pass
    cdef public object __online_packs_done
    property online_packs_done:
        def __get__(self):
            return self.__online_packs_done
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__online_packs_done:
                    self.__online_packs_done = value
                    if self._initialized:
                        self.touch_online_packs_done()

    cpdef touch_online_packs_done(self):
        self.dirty_fields.add('online_packs_done')
        self.__online_packs_flag = None
        self.clear_online_packs_flag()
        pass
    cdef public object __mail_reward_receiveds
    property mail_reward_receiveds:
        def __get__(self):
            return self.__mail_reward_receiveds
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_mail_reward_receiveds(self):
        pass
    cdef public int __refinery
    property refinery:
        def __get__(self):
            return self.__refinery
        def __set__(self, value):
                value = int(value)
                if value != self.__refinery:
                    self.__refinery = value
                    if self._initialized:
                        self.touch_refinery()

    cpdef touch_refinery(self):
        self.dirty_fields.add('refinery')
        self.sync_dirty_fields.add('refinery')
        pass
    cdef public int __daily_cache_targetID
    property daily_cache_targetID:
        def __get__(self):
            return self.__daily_cache_targetID
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_cache_targetID:
                    self.__daily_cache_targetID = value
                    if self._initialized:
                        self.touch_daily_cache_targetID()

    cpdef touch_daily_cache_targetID(self):
        self.dirty_fields.add('daily_cache_targetID')
        pass
    cdef public int __daily_dead_resume
    property daily_dead_resume:
        def __get__(self):
            return self.__daily_dead_resume
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_dead_resume:
                    self.__daily_dead_resume = value
                    if self._initialized:
                        self.touch_daily_dead_resume()

    cpdef touch_daily_dead_resume(self):
        self.dirty_fields.add('daily_dead_resume')
        pass
    cdef public int __daily_dead_cd
    property daily_dead_cd:
        def __get__(self):
            return self.__daily_dead_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_dead_cd:
                    self.__daily_dead_cd = value
                    if self._initialized:
                        self.touch_daily_dead_cd()

    cpdef touch_daily_dead_cd(self):
        self.dirty_fields.add('daily_dead_cd')
        self.sync_dirty_fields.add('daily_dead_cd')
        pass
    cdef public object __daily_rewards
    property daily_rewards:
        def __get__(self):
            return self.__daily_rewards
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'daily_rewards', self.touch_daily_rewards)
                if value != self.__daily_rewards:
                    self.__daily_rewards = value
                    if self._initialized:
                        self.touch_daily_rewards()

    cpdef touch_daily_rewards(self):
        self.dirty_fields.add('daily_rewards')
        pass
    cdef public int __daily_kill_count
    property daily_kill_count:
        def __get__(self):
            return self.__daily_kill_count
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_kill_count:
                    self.__daily_kill_count = value
                    if self._initialized:
                        self.touch_daily_kill_count()

    cpdef touch_daily_kill_count(self):
        self.dirty_fields.add('daily_kill_count')
        self.sync_dirty_fields.add('daily_kill_count')
        pass
    cdef public object __daily_registered
    property daily_registered:
        def __get__(self):
            return self.__daily_registered
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__daily_registered:
                    self.__daily_registered = value
                    if self._initialized:
                        self.touch_daily_registered()

    cpdef touch_daily_registered(self):
        self.dirty_fields.add('daily_registered')
        self.sync_dirty_fields.add('daily_registered')
        pass
    cdef public int __daily_count
    property daily_count:
        def __get__(self):
            return self.__daily_count
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_count:
                    self.__daily_count = value
                    if self._initialized:
                        self.touch_daily_count()

    cpdef touch_daily_count(self):
        self.dirty_fields.add('daily_count')
        self.sync_dirty_fields.add('daily_count')
        pass
    cdef public object __daily_histories
    property daily_histories:
        def __get__(self):
            return self.__daily_histories
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_daily_histories(self):
        pass
    cdef public object __daily_history_flag
    property daily_history_flag:
        def __get__(self):
            return self.__daily_history_flag
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__daily_history_flag:
                    self.__daily_history_flag = value
                    if self._initialized:
                        self.touch_daily_history_flag()

    cpdef touch_daily_history_flag(self):
        self.dirty_fields.add('daily_history_flag')
        self.sync_dirty_fields.add('daily_history_flag')
        pass
    cdef public int __daily_max_win_count
    property daily_max_win_count:
        def __get__(self):
            return self.__daily_max_win_count
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_max_win_count:
                    self.__daily_max_win_count = value
                    if self._initialized:
                        self.touch_daily_max_win_count()

    cpdef touch_daily_max_win_count(self):
        self.dirty_fields.add('daily_max_win_count')
        self.sync_dirty_fields.add('daily_max_win_count')
        pass
    cdef public int __daily_rank
    property daily_rank:
        def __get__(self):
            return self.__daily_rank
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_rank:
                    self.__daily_rank = value
                    if self._initialized:
                        self.touch_daily_rank()

    cpdef touch_daily_rank(self):
        self.dirty_fields.add('daily_rank')
        self.sync_dirty_fields.add('daily_rank')
        pass
    cdef public int __daily_reset_time
    property daily_reset_time:
        def __get__(self):
            return self.__daily_reset_time
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_reset_time:
                    self.__daily_reset_time = value
                    if self._initialized:
                        self.touch_daily_reset_time()

    cpdef touch_daily_reset_time(self):
        self.dirty_fields.add('daily_reset_time')
        pass
    cdef public int __daily_inspire_used_count
    property daily_inspire_used_count:
        def __get__(self):
            return self.__daily_inspire_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_inspire_used_count:
                    self.__daily_inspire_used_count = value
                    if self._initialized:
                        self.touch_daily_inspire_used_count()

    cpdef touch_daily_inspire_used_count(self):
        self.dirty_fields.add('daily_inspire_used_count')
        self.__daily_inspire_rest_count = None
        self.__daily_inspire_buff = None
        self.__daily_inspire_cost = None
        self.clear_daily_inspire_rest_count()
        self.clear_daily_inspire_buff()
        self.clear_daily_inspire_cost()
        pass
    cdef public int __daily_inspire_most_count
    property daily_inspire_most_count:
        def __get__(self):
            return self.__daily_inspire_most_count
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_inspire_most_count:
                    self.__daily_inspire_most_count = value
                    if self._initialized:
                        self.touch_daily_inspire_most_count()

    cpdef touch_daily_inspire_most_count(self):
        self.dirty_fields.add('daily_inspire_most_count')
        self.sync_dirty_fields.add('daily_inspire_most_count')
        self.__daily_inspire_rest_count = None
        self.clear_daily_inspire_rest_count()
        pass
    cdef public object __daily_end_panel
    property daily_end_panel:
        def __get__(self):
            return self.__daily_end_panel
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'daily_end_panel', self.touch_daily_end_panel)
                if value != self.__daily_end_panel:
                    self.__daily_end_panel = value
                    if self._initialized:
                        self.touch_daily_end_panel()

    cpdef touch_daily_end_panel(self):
        self.dirty_fields.add('daily_end_panel')
        self.__daily_end_panel_flag = None
        self.clear_daily_end_panel_flag()
        pass
    cdef public int __task_seven_cd
    property task_seven_cd:
        def __get__(self):
            return self.__task_seven_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__task_seven_cd:
                    self.__task_seven_cd = value
                    if self._initialized:
                        self.touch_task_seven_cd()

    cpdef touch_task_seven_cd(self):
        self.dirty_fields.add('task_seven_cd')
        self.sync_dirty_fields.add('task_seven_cd')
        pass
    cdef public object __guide_reward_flag
    property guide_reward_flag:
        def __get__(self):
            return self.__guide_reward_flag
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__guide_reward_flag:
                    self.__guide_reward_flag = value
                    if self._initialized:
                        self.touch_guide_reward_flag()

    cpdef touch_guide_reward_flag(self):
        self.dirty_fields.add('guide_reward_flag')
        self.sync_dirty_fields.add('guide_reward_flag')
        pass
    cdef public object __guide_defeat_flag
    property guide_defeat_flag:
        def __get__(self):
            return self.__guide_defeat_flag
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__guide_defeat_flag:
                    self.__guide_defeat_flag = value
                    if self._initialized:
                        self.touch_guide_defeat_flag()

    cpdef touch_guide_defeat_flag(self):
        self.dirty_fields.add('guide_defeat_flag')
        self.sync_dirty_fields.add('guide_defeat_flag')
        pass
    cdef public unicode __ambition
    property ambition:
        def __get__(self):
            return self.__ambition
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__ambition:
                    self.__ambition = value
                    if self._initialized:
                        self.touch_ambition()

    cpdef touch_ambition(self):
        self.dirty_fields.add('ambition')
        self.sync_dirty_fields.add('ambition')
        self.__power = None
        self.__ambition_power = None
        self.clear_power()
        self.clear_ambition_power()
        pass
    cdef public unicode __vip_ambition
    property vip_ambition:
        def __get__(self):
            return self.__vip_ambition
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__vip_ambition:
                    self.__vip_ambition = value
                    if self._initialized:
                        self.touch_vip_ambition()

    cpdef touch_vip_ambition(self):
        self.dirty_fields.add('vip_ambition')
        self.sync_dirty_fields.add('vip_ambition')
        self.__power = None
        self.__ambition_power = None
        self.clear_power()
        self.clear_ambition_power()
        pass
    cdef public int __ambition_count
    property ambition_count:
        def __get__(self):
            return self.__ambition_count
        def __set__(self, value):
                value = int(value)
                if value != self.__ambition_count:
                    if self._initialized:
                        for callback in type(self)._listeners_ambition_count:
                            callback(self, value)
                    self.__ambition_count = value
                    if self._initialized:
                        self.touch_ambition_count()

    cpdef touch_ambition_count(self):
        self.dirty_fields.add('ambition_count')
        if self._initialized:
            value = self.ambition_count
            for callback in type(self)._listeners_ambition_count:
                callback(self, value)
        pass
    cdef public int __player_equip1
    property player_equip1:
        def __get__(self):
            return self.__player_equip1
        def __set__(self, value):
                value = int(value)
                if value != self.__player_equip1:
                    self.__player_equip1 = value
                    if self._initialized:
                        self.touch_player_equip1()

    cpdef touch_player_equip1(self):
        self.dirty_fields.add('player_equip1')
        self.sync_dirty_fields.add('player_equip1')
        pass
    cdef public int __player_equip2
    property player_equip2:
        def __get__(self):
            return self.__player_equip2
        def __set__(self, value):
                value = int(value)
                if value != self.__player_equip2:
                    self.__player_equip2 = value
                    if self._initialized:
                        self.touch_player_equip2()

    cpdef touch_player_equip2(self):
        self.dirty_fields.add('player_equip2')
        self.sync_dirty_fields.add('player_equip2')
        pass
    cdef public int __player_equip3
    property player_equip3:
        def __get__(self):
            return self.__player_equip3
        def __set__(self, value):
                value = int(value)
                if value != self.__player_equip3:
                    self.__player_equip3 = value
                    if self._initialized:
                        self.touch_player_equip3()

    cpdef touch_player_equip3(self):
        self.dirty_fields.add('player_equip3')
        self.sync_dirty_fields.add('player_equip3')
        pass
    cdef public int __player_equip4
    property player_equip4:
        def __get__(self):
            return self.__player_equip4
        def __set__(self, value):
                value = int(value)
                if value != self.__player_equip4:
                    self.__player_equip4 = value
                    if self._initialized:
                        self.touch_player_equip4()

    cpdef touch_player_equip4(self):
        self.dirty_fields.add('player_equip4')
        self.sync_dirty_fields.add('player_equip4')
        pass
    cdef public int __player_equip5
    property player_equip5:
        def __get__(self):
            return self.__player_equip5
        def __set__(self, value):
                value = int(value)
                if value != self.__player_equip5:
                    self.__player_equip5 = value
                    if self._initialized:
                        self.touch_player_equip5()

    cpdef touch_player_equip5(self):
        self.dirty_fields.add('player_equip5')
        self.sync_dirty_fields.add('player_equip5')
        pass
    cdef public int __player_equip6
    property player_equip6:
        def __get__(self):
            return self.__player_equip6
        def __set__(self, value):
                value = int(value)
                if value != self.__player_equip6:
                    self.__player_equip6 = value
                    if self._initialized:
                        self.touch_player_equip6()

    cpdef touch_player_equip6(self):
        self.dirty_fields.add('player_equip6')
        self.sync_dirty_fields.add('player_equip6')
        pass
    cdef public object __consume_campaign_rewards
    property consume_campaign_rewards:
        def __get__(self):
            return self.__consume_campaign_rewards
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'consume_campaign_rewards', self.touch_consume_campaign_rewards)
                if value != self.__consume_campaign_rewards:
                    self.__consume_campaign_rewards = value
                    if self._initialized:
                        self.touch_consume_campaign_rewards()

    cpdef touch_consume_campaign_rewards(self):
        self.dirty_fields.add('consume_campaign_rewards')
        self.__consume_campaign_rewards_flag = None
        self.clear_consume_campaign_rewards_flag()
        pass
    cdef public int __consume_campaign_reset_time
    property consume_campaign_reset_time:
        def __get__(self):
            return self.__consume_campaign_reset_time
        def __set__(self, value):
                value = int(value)
                if value != self.__consume_campaign_reset_time:
                    self.__consume_campaign_reset_time = value
                    if self._initialized:
                        self.touch_consume_campaign_reset_time()

    cpdef touch_consume_campaign_reset_time(self):
        self.dirty_fields.add('consume_campaign_reset_time')
        pass
    cdef public int __consume_campaign_amount
    property consume_campaign_amount:
        def __get__(self):
            return self.__consume_campaign_amount
        def __set__(self, value):
                value = int(value)
                if value != self.__consume_campaign_amount:
                    self.__consume_campaign_amount = value
                    if self._initialized:
                        self.touch_consume_campaign_amount()

    cpdef touch_consume_campaign_amount(self):
        self.dirty_fields.add('consume_campaign_amount')
        self.sync_dirty_fields.add('consume_campaign_amount')
        pass
    cdef public object __login_campaign_rewards
    property login_campaign_rewards:
        def __get__(self):
            return self.__login_campaign_rewards
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'login_campaign_rewards', self.touch_login_campaign_rewards)
                if value != self.__login_campaign_rewards:
                    self.__login_campaign_rewards = value
                    if self._initialized:
                        self.touch_login_campaign_rewards()

    cpdef touch_login_campaign_rewards(self):
        self.dirty_fields.add('login_campaign_rewards')
        self.__login_campaign_rewards_flag = None
        self.clear_login_campaign_rewards_flag()
        pass
    cdef public int __login_campaign_reset_time
    property login_campaign_reset_time:
        def __get__(self):
            return self.__login_campaign_reset_time
        def __set__(self, value):
                value = int(value)
                if value != self.__login_campaign_reset_time:
                    self.__login_campaign_reset_time = value
                    if self._initialized:
                        self.touch_login_campaign_reset_time()

    cpdef touch_login_campaign_reset_time(self):
        self.dirty_fields.add('login_campaign_reset_time')
        pass
    cdef public int __login_campaign_amount
    property login_campaign_amount:
        def __get__(self):
            return self.__login_campaign_amount
        def __set__(self, value):
                value = int(value)
                if value != self.__login_campaign_amount:
                    self.__login_campaign_amount = value
                    if self._initialized:
                        self.touch_login_campaign_amount()

    cpdef touch_login_campaign_amount(self):
        self.dirty_fields.add('login_campaign_amount')
        self.sync_dirty_fields.add('login_campaign_amount')
        pass
    cdef public int __ranking_pet_count
    property ranking_pet_count:
        def __get__(self):
            return self.__ranking_pet_count
        def __set__(self, value):
                value = int(value)
                if value != self.__ranking_pet_count:
                    if self._initialized:
                        for callback in type(self)._listeners_ranking_pet_count:
                            callback(self, value)
                    self.__ranking_pet_count = value
                    if self._initialized:
                        self.touch_ranking_pet_count()

    cpdef touch_ranking_pet_count(self):
        self.dirty_fields.add('ranking_pet_count')
        if self._initialized:
            value = self.ranking_pet_count
            for callback in type(self)._listeners_ranking_pet_count:
                callback(self, value)
        pass
    cdef public int __ranking_pet_power
    property ranking_pet_power:
        def __get__(self):
            return self.__ranking_pet_power
        def __set__(self, value):
                value = int(value)
                if value != self.__ranking_pet_power:
                    if self._initialized:
                        for callback in type(self)._listeners_ranking_pet_power:
                            callback(self, value)
                    self.__ranking_pet_power = value
                    if self._initialized:
                        self.touch_ranking_pet_power()

    cpdef touch_ranking_pet_power(self):
        self.dirty_fields.add('ranking_pet_power')
        if self._initialized:
            value = self.ranking_pet_power
            for callback in type(self)._listeners_ranking_pet_power:
                callback(self, value)
        pass
    cdef public int __ranking_pet_power_entityID
    property ranking_pet_power_entityID:
        def __get__(self):
            return self.__ranking_pet_power_entityID
        def __set__(self, value):
                value = int(value)
                if value != self.__ranking_pet_power_entityID:
                    self.__ranking_pet_power_entityID = value
                    if self._initialized:
                        self.touch_ranking_pet_power_entityID()

    cpdef touch_ranking_pet_power_entityID(self):
        self.dirty_fields.add('ranking_pet_power_entityID')
        pass
    cdef public int __ranking_pet_power_prototypeID
    property ranking_pet_power_prototypeID:
        def __get__(self):
            return self.__ranking_pet_power_prototypeID
        def __set__(self, value):
                value = int(value)
                if value != self.__ranking_pet_power_prototypeID:
                    self.__ranking_pet_power_prototypeID = value
                    if self._initialized:
                        self.touch_ranking_pet_power_prototypeID()

    cpdef touch_ranking_pet_power_prototypeID(self):
        self.dirty_fields.add('ranking_pet_power_prototypeID')
        pass
    cdef public int __ranking_pet_power_breaklevel
    property ranking_pet_power_breaklevel:
        def __get__(self):
            return self.__ranking_pet_power_breaklevel
        def __set__(self, value):
                value = int(value)
                if value != self.__ranking_pet_power_breaklevel:
                    self.__ranking_pet_power_breaklevel = value
                    if self._initialized:
                        self.touch_ranking_pet_power_breaklevel()

    cpdef touch_ranking_pet_power_breaklevel(self):
        self.dirty_fields.add('ranking_pet_power_breaklevel')
        pass
    cdef public object __rankingreceiveds
    property rankingreceiveds:
        def __get__(self):
            return self.__rankingreceiveds
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'rankingreceiveds', self.touch_rankingreceiveds)
                if value != self.__rankingreceiveds:
                    self.__rankingreceiveds = value
                    if self._initialized:
                        self.touch_rankingreceiveds()

    cpdef touch_rankingreceiveds(self):
        self.dirty_fields.add('rankingreceiveds')
        pass
    cdef public object __ranking_receiveds
    property ranking_receiveds:
        def __get__(self):
            return self.__ranking_receiveds
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_ranking_receiveds(self):
        pass
    cdef public int __ranking_equip_power
    property ranking_equip_power:
        def __get__(self):
            return self.__ranking_equip_power
        def __set__(self, value):
                value = int(value)
                if value != self.__ranking_equip_power:
                    if self._initialized:
                        for callback in type(self)._listeners_ranking_equip_power:
                            callback(self, value)
                    self.__ranking_equip_power = value
                    if self._initialized:
                        self.touch_ranking_equip_power()

    cpdef touch_ranking_equip_power(self):
        self.dirty_fields.add('ranking_equip_power')
        if self._initialized:
            value = self.ranking_equip_power
            for callback in type(self)._listeners_ranking_equip_power:
                callback(self, value)
        pass
    cdef public int __ranking_equip_power_entityID
    property ranking_equip_power_entityID:
        def __get__(self):
            return self.__ranking_equip_power_entityID
        def __set__(self, value):
                value = int(value)
                if value != self.__ranking_equip_power_entityID:
                    self.__ranking_equip_power_entityID = value
                    if self._initialized:
                        self.touch_ranking_equip_power_entityID()

    cpdef touch_ranking_equip_power_entityID(self):
        self.dirty_fields.add('ranking_equip_power_entityID')
        pass
    cdef public int __ranking_equip_power_prototypeID
    property ranking_equip_power_prototypeID:
        def __get__(self):
            return self.__ranking_equip_power_prototypeID
        def __set__(self, value):
                value = int(value)
                if value != self.__ranking_equip_power_prototypeID:
                    self.__ranking_equip_power_prototypeID = value
                    if self._initialized:
                        self.touch_ranking_equip_power_prototypeID()

    cpdef touch_ranking_equip_power_prototypeID(self):
        self.dirty_fields.add('ranking_equip_power_prototypeID')
        pass
    cdef public int __ranking_equip_power_step
    property ranking_equip_power_step:
        def __get__(self):
            return self.__ranking_equip_power_step
        def __set__(self, value):
                value = int(value)
                if value != self.__ranking_equip_power_step:
                    self.__ranking_equip_power_step = value
                    if self._initialized:
                        self.touch_ranking_equip_power_step()

    cpdef touch_ranking_equip_power_step(self):
        self.dirty_fields.add('ranking_equip_power_step')
        pass
    cdef public int __ranking_equip_power_level
    property ranking_equip_power_level:
        def __get__(self):
            return self.__ranking_equip_power_level
        def __set__(self, value):
                value = int(value)
                if value != self.__ranking_equip_power_level:
                    self.__ranking_equip_power_level = value
                    if self._initialized:
                        self.touch_ranking_equip_power_level()

    cpdef touch_ranking_equip_power_level(self):
        self.dirty_fields.add('ranking_equip_power_level')
        pass
    cdef public int __daily_recharge_rewards_ts
    property daily_recharge_rewards_ts:
        def __get__(self):
            return self.__daily_recharge_rewards_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_recharge_rewards_ts:
                    self.__daily_recharge_rewards_ts = value
                    if self._initialized:
                        self.touch_daily_recharge_rewards_ts()

    cpdef touch_daily_recharge_rewards_ts(self):
        self.dirty_fields.add('daily_recharge_rewards_ts')
        pass
    cdef public object __daily_recharge_rewards
    property daily_recharge_rewards:
        def __get__(self):
            return self.__daily_recharge_rewards
        def __set__(self, value):
                value = value
                if value != self.__daily_recharge_rewards:
                    self.__daily_recharge_rewards = value
                    if self._initialized:
                        self.touch_daily_recharge_rewards()

    cpdef touch_daily_recharge_rewards(self):
        self.dirty_fields.add('daily_recharge_rewards')
        self.__daily_recharge_rewards_count = None
        self.clear_daily_recharge_rewards_count()
        pass
    cdef public int __daily_recharge_useds_ts
    property daily_recharge_useds_ts:
        def __get__(self):
            return self.__daily_recharge_useds_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__daily_recharge_useds_ts:
                    self.__daily_recharge_useds_ts = value
                    if self._initialized:
                        self.touch_daily_recharge_useds_ts()

    cpdef touch_daily_recharge_useds_ts(self):
        self.dirty_fields.add('daily_recharge_useds_ts')
        pass
    cdef public object __daily_recharge_useds
    property daily_recharge_useds:
        def __get__(self):
            return self.__daily_recharge_useds
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'daily_recharge_useds', self.touch_daily_recharge_useds)
                if value != self.__daily_recharge_useds:
                    self.__daily_recharge_useds = value
                    if self._initialized:
                        self.touch_daily_recharge_useds()

    cpdef touch_daily_recharge_useds(self):
        self.dirty_fields.add('daily_recharge_useds')
        pass
    cdef public object __scene_rewards
    property scene_rewards:
        def __get__(self):
            return self.__scene_rewards
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_scene_rewards(self):
        pass
    cdef public int __free_pet_exchange_ts
    property free_pet_exchange_ts:
        def __get__(self):
            return self.__free_pet_exchange_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__free_pet_exchange_ts:
                    self.__free_pet_exchange_ts = value
                    if self._initialized:
                        self.touch_free_pet_exchange_ts()

    cpdef touch_free_pet_exchange_ts(self):
        self.dirty_fields.add('free_pet_exchange_ts')
        pass
    cdef public int __free_pet_exchange
    property free_pet_exchange:
        def __get__(self):
            return self.__free_pet_exchange
        def __set__(self, value):
                value = int(value)
                if value != self.__free_pet_exchange:
                    self.__free_pet_exchange = value
                    if self._initialized:
                        self.touch_free_pet_exchange()

    cpdef touch_free_pet_exchange(self):
        self.dirty_fields.add('free_pet_exchange')
        self.sync_dirty_fields.add('free_pet_exchange')
        pass
    cdef public int __mat_exchange_limits_ts
    property mat_exchange_limits_ts:
        def __get__(self):
            return self.__mat_exchange_limits_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__mat_exchange_limits_ts:
                    self.__mat_exchange_limits_ts = value
                    if self._initialized:
                        self.touch_mat_exchange_limits_ts()

    cpdef touch_mat_exchange_limits_ts(self):
        self.dirty_fields.add('mat_exchange_limits_ts')
        pass
    cdef public object __mat_exchange_limits
    property mat_exchange_limits:
        def __get__(self):
            return self.__mat_exchange_limits
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'mat_exchange_limits', self.touch_mat_exchange_limits)
                if value != self.__mat_exchange_limits:
                    self.__mat_exchange_limits = value
                    if self._initialized:
                        self.touch_mat_exchange_limits()

    cpdef touch_mat_exchange_limits(self):
        self.dirty_fields.add('mat_exchange_limits')
        pass
    cdef public double __last_check_mail_time
    property last_check_mail_time:
        def __get__(self):
            return self.__last_check_mail_time
        def __set__(self, value):
                value = float(value)
                if value != self.__last_check_mail_time:
                    self.__last_check_mail_time = value
                    if self._initialized:
                        self.touch_last_check_mail_time()

    cpdef touch_last_check_mail_time(self):
        self.dirty_fields.add('last_check_mail_time')
        pass
    cdef public object __city_dungeon_mg_cache
    property city_dungeon_mg_cache:
        def __get__(self):
            return self.__city_dungeon_mg_cache
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'city_dungeon_mg_cache', self.touch_city_dungeon_mg_cache)
                if value != self.__city_dungeon_mg_cache:
                    self.__city_dungeon_mg_cache = value
                    if self._initialized:
                        self.touch_city_dungeon_mg_cache()

    cpdef touch_city_dungeon_mg_cache(self):
        self.dirty_fields.add('city_dungeon_mg_cache')
        pass
    cdef public int __city_dungeon_last_reset
    property city_dungeon_last_reset:
        def __get__(self):
            return self.__city_dungeon_last_reset
        def __set__(self, value):
                value = int(value)
                if value != self.__city_dungeon_last_reset:
                    self.__city_dungeon_last_reset = value
                    if self._initialized:
                        self.touch_city_dungeon_last_reset()

    cpdef touch_city_dungeon_last_reset(self):
        self.dirty_fields.add('city_dungeon_last_reset')
        pass
    cdef public object __city_dungeon_rewards
    property city_dungeon_rewards:
        def __get__(self):
            return self.__city_dungeon_rewards
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'city_dungeon_rewards', self.touch_city_dungeon_rewards)
                if value != self.__city_dungeon_rewards:
                    self.__city_dungeon_rewards = value
                    if self._initialized:
                        self.touch_city_dungeon_rewards()

    cpdef touch_city_dungeon_rewards(self):
        self.dirty_fields.add('city_dungeon_rewards')
        self.__city_dungeon_rewards_flag = None
        self.clear_city_dungeon_rewards_flag()
        pass
    cdef public object __city_rewards_recv
    property city_rewards_recv:
        def __get__(self):
            return self.__city_rewards_recv
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_city_rewards_recv(self):
        pass
    cdef public int __city_dungeon_kill_count
    property city_dungeon_kill_count:
        def __get__(self):
            return self.__city_dungeon_kill_count
        def __set__(self, value):
                value = int(value)
                if value != self.__city_dungeon_kill_count:
                    self.__city_dungeon_kill_count = value
                    if self._initialized:
                        self.touch_city_dungeon_kill_count()

    cpdef touch_city_dungeon_kill_count(self):
        self.dirty_fields.add('city_dungeon_kill_count')
        self.sync_dirty_fields.add('city_dungeon_kill_count')
        pass
    cdef public int __city_treasure_recv_flag_ts
    property city_treasure_recv_flag_ts:
        def __get__(self):
            return self.__city_treasure_recv_flag_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__city_treasure_recv_flag_ts:
                    self.__city_treasure_recv_flag_ts = value
                    if self._initialized:
                        self.touch_city_treasure_recv_flag_ts()

    cpdef touch_city_treasure_recv_flag_ts(self):
        self.dirty_fields.add('city_treasure_recv_flag_ts')
        pass
    cdef public object __city_treasure_recv_flag
    property city_treasure_recv_flag:
        def __get__(self):
            return self.__city_treasure_recv_flag
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__city_treasure_recv_flag:
                    self.__city_treasure_recv_flag = value
                    if self._initialized:
                        self.touch_city_treasure_recv_flag()

    cpdef touch_city_treasure_recv_flag(self):
        self.dirty_fields.add('city_treasure_recv_flag')
        self.sync_dirty_fields.add('city_treasure_recv_flag')
        pass
    cdef public object __city_contend_cache_target
    property city_contend_cache_target:
        def __get__(self):
            return self.__city_contend_cache_target
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'city_contend_cache_target', self.touch_city_contend_cache_target)
                if value != self.__city_contend_cache_target:
                    self.__city_contend_cache_target = value
                    if self._initialized:
                        self.touch_city_contend_cache_target()

    cpdef touch_city_contend_cache_target(self):
        self.dirty_fields.add('city_contend_cache_target')
        pass
    cdef public object __city_contend_rewards
    property city_contend_rewards:
        def __get__(self):
            return self.__city_contend_rewards
        def __set__(self, value):
                value = DictContainer(value)
                value.init_entity(self, 'city_contend_rewards', self.touch_city_contend_rewards)
                if value != self.__city_contend_rewards:
                    self.__city_contend_rewards = value
                    if self._initialized:
                        self.touch_city_contend_rewards()

    cpdef touch_city_contend_rewards(self):
        self.dirty_fields.add('city_contend_rewards')
        self.__city_contend_rewards_flag = None
        self.clear_city_contend_rewards_flag()
        pass
    cdef public int __city_contend_last_reset
    property city_contend_last_reset:
        def __get__(self):
            return self.__city_contend_last_reset
        def __set__(self, value):
                value = int(value)
                if value != self.__city_contend_last_reset:
                    self.__city_contend_last_reset = value
                    if self._initialized:
                        self.touch_city_contend_last_reset()

    cpdef touch_city_contend_last_reset(self):
        self.dirty_fields.add('city_contend_last_reset')
        pass
    cdef public int __city_contend_treasure
    property city_contend_treasure:
        def __get__(self):
            return self.__city_contend_treasure
        def __set__(self, value):
                value = int(value)
                if value != self.__city_contend_treasure:
                    self.__city_contend_treasure = value
                    if self._initialized:
                        self.touch_city_contend_treasure()

    cpdef touch_city_contend_treasure(self):
        self.dirty_fields.add('city_contend_treasure')
        self.sync_dirty_fields.add('city_contend_treasure')
        pass
    cdef public int __city_contend_step
    property city_contend_step:
        def __get__(self):
            return self.__city_contend_step
        def __set__(self, value):
                value = int(value)
                if value != self.__city_contend_step:
                    self.__city_contend_step = value
                    if self._initialized:
                        self.touch_city_contend_step()

    cpdef touch_city_contend_step(self):
        self.dirty_fields.add('city_contend_step')
        self.sync_dirty_fields.add('city_contend_step')
        pass
    cdef public int __city_contend_total_treasure
    property city_contend_total_treasure:
        def __get__(self):
            return self.__city_contend_total_treasure
        def __set__(self, value):
                value = int(value)
                if value != self.__city_contend_total_treasure:
                    self.__city_contend_total_treasure = value
                    if self._initialized:
                        self.touch_city_contend_total_treasure()

    cpdef touch_city_contend_total_treasure(self):
        self.dirty_fields.add('city_contend_total_treasure')
        self.sync_dirty_fields.add('city_contend_total_treasure')
        pass
    cdef public int __city_contend_count
    property city_contend_count:
        def __get__(self):
            return self.__city_contend_count
        def __set__(self, value):
                value = int(value)
                if value != self.__city_contend_count:
                    self.__city_contend_count = value
                    if self._initialized:
                        self.touch_city_contend_count()

    cpdef touch_city_contend_count(self):
        self.dirty_fields.add('city_contend_count')
        self.sync_dirty_fields.add('city_contend_count')
        pass
    cdef public object __city_contend_events
    property city_contend_events:
        def __get__(self):
            return self.__city_contend_events
        def __set__(self, value):
                value = ListContainer(value)
                value.init_entity(self, 'city_contend_events', self.touch_city_contend_events)
                if value != self.__city_contend_events:
                    self.__city_contend_events = value
                    if self._initialized:
                        self.touch_city_contend_events()

    cpdef touch_city_contend_events(self):
        self.dirty_fields.add('city_contend_events')
        pass
    cdef public int __city_contend_total_step
    property city_contend_total_step:
        def __get__(self):
            return self.__city_contend_total_step
        def __set__(self, value):
                value = int(value)
                if value != self.__city_contend_total_step:
                    self.__city_contend_total_step = value
                    if self._initialized:
                        self.touch_city_contend_total_step()

    cpdef touch_city_contend_total_step(self):
        self.dirty_fields.add('city_contend_total_step')
        pass
    cdef public int __city_contend_total_treasure_backup
    property city_contend_total_treasure_backup:
        def __get__(self):
            return self.__city_contend_total_treasure_backup
        def __set__(self, value):
                value = int(value)
                if value != self.__city_contend_total_treasure_backup:
                    self.__city_contend_total_treasure_backup = value
                    if self._initialized:
                        self.touch_city_contend_total_treasure_backup()

    cpdef touch_city_contend_total_treasure_backup(self):
        self.dirty_fields.add('city_contend_total_treasure_backup')
        pass
    cdef public int __city_contend_count_backup
    property city_contend_count_backup:
        def __get__(self):
            return self.__city_contend_count_backup
        def __set__(self, value):
                value = int(value)
                if value != self.__city_contend_count_backup:
                    self.__city_contend_count_backup = value
                    if self._initialized:
                        self.touch_city_contend_count_backup()

    cpdef touch_city_contend_count_backup(self):
        self.dirty_fields.add('city_contend_count_backup')
        pass
    cdef public int __monthcard1
    property monthcard1:
        def __get__(self):
            return self.__monthcard1
        def __set__(self, value):
                value = int(value)
                if value != self.__monthcard1:
                    self.__monthcard1 = value
                    if self._initialized:
                        self.touch_monthcard1()

    cpdef touch_monthcard1(self):
        self.dirty_fields.add('monthcard1')
        self.sync_dirty_fields.add('monthcard1')
        pass
    cdef public int __monthcard2
    property monthcard2:
        def __get__(self):
            return self.__monthcard2
        def __set__(self, value):
                value = int(value)
                if value != self.__monthcard2:
                    self.__monthcard2 = value
                    if self._initialized:
                        self.touch_monthcard2()

    cpdef touch_monthcard2(self):
        self.dirty_fields.add('monthcard2')
        self.sync_dirty_fields.add('monthcard2')
        pass
    cdef public int __monthcard_recv1_ts
    property monthcard_recv1_ts:
        def __get__(self):
            return self.__monthcard_recv1_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__monthcard_recv1_ts:
                    self.__monthcard_recv1_ts = value
                    if self._initialized:
                        self.touch_monthcard_recv1_ts()

    cpdef touch_monthcard_recv1_ts(self):
        self.dirty_fields.add('monthcard_recv1_ts')
        pass
    cdef public object __monthcard_recv1
    property monthcard_recv1:
        def __get__(self):
            return self.__monthcard_recv1
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__monthcard_recv1:
                    self.__monthcard_recv1 = value
                    if self._initialized:
                        self.touch_monthcard_recv1()

    cpdef touch_monthcard_recv1(self):
        self.dirty_fields.add('monthcard_recv1')
        self.sync_dirty_fields.add('monthcard_recv1')
        pass
    cdef public int __monthcard_recv2_ts
    property monthcard_recv2_ts:
        def __get__(self):
            return self.__monthcard_recv2_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__monthcard_recv2_ts:
                    self.__monthcard_recv2_ts = value
                    if self._initialized:
                        self.touch_monthcard_recv2_ts()

    cpdef touch_monthcard_recv2_ts(self):
        self.dirty_fields.add('monthcard_recv2_ts')
        pass
    cdef public object __monthcard_recv2
    property monthcard_recv2:
        def __get__(self):
            return self.__monthcard_recv2
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__monthcard_recv2:
                    self.__monthcard_recv2 = value
                    if self._initialized:
                        self.touch_monthcard_recv2()

    cpdef touch_monthcard_recv2(self):
        self.dirty_fields.add('monthcard_recv2')
        self.sync_dirty_fields.add('monthcard_recv2')
        pass
    cdef public int __weekscard1
    property weekscard1:
        def __get__(self):
            return self.__weekscard1
        def __set__(self, value):
                value = int(value)
                if value != self.__weekscard1:
                    self.__weekscard1 = value
                    if self._initialized:
                        self.touch_weekscard1()

    cpdef touch_weekscard1(self):
        self.dirty_fields.add('weekscard1')
        self.sync_dirty_fields.add('weekscard1')
        pass
    cdef public int __weekscard2
    property weekscard2:
        def __get__(self):
            return self.__weekscard2
        def __set__(self, value):
                value = int(value)
                if value != self.__weekscard2:
                    self.__weekscard2 = value
                    if self._initialized:
                        self.touch_weekscard2()

    cpdef touch_weekscard2(self):
        self.dirty_fields.add('weekscard2')
        self.sync_dirty_fields.add('weekscard2')
        pass
    cdef public int __weekscard_recv1_ts
    property weekscard_recv1_ts:
        def __get__(self):
            return self.__weekscard_recv1_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__weekscard_recv1_ts:
                    self.__weekscard_recv1_ts = value
                    if self._initialized:
                        self.touch_weekscard_recv1_ts()

    cpdef touch_weekscard_recv1_ts(self):
        self.dirty_fields.add('weekscard_recv1_ts')
        pass
    cdef public object __weekscard_recv1
    property weekscard_recv1:
        def __get__(self):
            return self.__weekscard_recv1
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__weekscard_recv1:
                    self.__weekscard_recv1 = value
                    if self._initialized:
                        self.touch_weekscard_recv1()

    cpdef touch_weekscard_recv1(self):
        self.dirty_fields.add('weekscard_recv1')
        self.sync_dirty_fields.add('weekscard_recv1')
        pass
    cdef public int __weekscard_recv2_ts
    property weekscard_recv2_ts:
        def __get__(self):
            return self.__weekscard_recv2_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__weekscard_recv2_ts:
                    self.__weekscard_recv2_ts = value
                    if self._initialized:
                        self.touch_weekscard_recv2_ts()

    cpdef touch_weekscard_recv2_ts(self):
        self.dirty_fields.add('weekscard_recv2_ts')
        pass
    cdef public object __weekscard_recv2
    property weekscard_recv2:
        def __get__(self):
            return self.__weekscard_recv2
        def __set__(self, value):
                value = convert_bool(value)
                if value != self.__weekscard_recv2:
                    self.__weekscard_recv2 = value
                    if self._initialized:
                        self.touch_weekscard_recv2()

    cpdef touch_weekscard_recv2(self):
        self.dirty_fields.add('weekscard_recv2')
        self.sync_dirty_fields.add('weekscard_recv2')
        pass
    cdef public int __exchange_campaign_counter
    property exchange_campaign_counter:
        def __get__(self):
            return self.__exchange_campaign_counter
        def __set__(self, value):
                value = int(value)
                if value != self.__exchange_campaign_counter:
                    self.__exchange_campaign_counter = value
                    if self._initialized:
                        self.touch_exchange_campaign_counter()

    cpdef touch_exchange_campaign_counter(self):
        self.dirty_fields.add('exchange_campaign_counter')
        pass
    cdef public int __exchange_campaign_last_time
    property exchange_campaign_last_time:
        def __get__(self):
            return self.__exchange_campaign_last_time
        def __set__(self, value):
                value = int(value)
                if value != self.__exchange_campaign_last_time:
                    self.__exchange_campaign_last_time = value
                    if self._initialized:
                        self.touch_exchange_campaign_last_time()

    cpdef touch_exchange_campaign_last_time(self):
        self.dirty_fields.add('exchange_campaign_last_time')
        pass
    cdef public int __refresh_store_campaign_counter
    property refresh_store_campaign_counter:
        def __get__(self):
            return self.__refresh_store_campaign_counter
        def __set__(self, value):
                value = int(value)
                if value != self.__refresh_store_campaign_counter:
                    self.__refresh_store_campaign_counter = value
                    if self._initialized:
                        self.touch_refresh_store_campaign_counter()

    cpdef touch_refresh_store_campaign_counter(self):
        self.dirty_fields.add('refresh_store_campaign_counter')
        self.sync_dirty_fields.add('refresh_store_campaign_counter')
        pass
    cdef public int __refresh_store_campaign_last_time
    property refresh_store_campaign_last_time:
        def __get__(self):
            return self.__refresh_store_campaign_last_time
        def __set__(self, value):
                value = int(value)
                if value != self.__refresh_store_campaign_last_time:
                    self.__refresh_store_campaign_last_time = value
                    if self._initialized:
                        self.touch_refresh_store_campaign_last_time()

    cpdef touch_refresh_store_campaign_last_time(self):
        self.dirty_fields.add('refresh_store_campaign_last_time')
        pass
    cdef public object __refresh_reward_done
    property refresh_reward_done:
        def __get__(self):
            return self.__refresh_reward_done
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'refresh_reward_done', self.touch_refresh_reward_done)
                if value != self.__refresh_reward_done:
                    self.__refresh_reward_done = value
                    if self._initialized:
                        self.touch_refresh_reward_done()

    cpdef touch_refresh_reward_done(self):
        self.dirty_fields.add('refresh_reward_done')
        self.__refresh_reward_done_count = None
        self.clear_refresh_reward_done_count()
        pass
    cdef public object __refresh_reward_end
    property refresh_reward_end:
        def __get__(self):
            return self.__refresh_reward_end
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'refresh_reward_end', self.touch_refresh_reward_end)
                if value != self.__refresh_reward_end:
                    self.__refresh_reward_end = value
                    if self._initialized:
                        self.touch_refresh_reward_end()

    cpdef touch_refresh_reward_end(self):
        self.dirty_fields.add('refresh_reward_end')
        pass
    cdef public int __shake_tree_used_count_ts
    property shake_tree_used_count_ts:
        def __get__(self):
            return self.__shake_tree_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__shake_tree_used_count_ts:
                    self.__shake_tree_used_count_ts = value
                    if self._initialized:
                        self.touch_shake_tree_used_count_ts()

    cpdef touch_shake_tree_used_count_ts(self):
        self.dirty_fields.add('shake_tree_used_count_ts')
        pass
    cdef public int __shake_tree_used_count
    property shake_tree_used_count:
        def __get__(self):
            return self.__shake_tree_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__shake_tree_used_count:
                    self.__shake_tree_used_count = value
                    if self._initialized:
                        self.touch_shake_tree_used_count()

    cpdef touch_shake_tree_used_count(self):
        self.dirty_fields.add('shake_tree_used_count')
        self.sync_dirty_fields.add('shake_tree_used_count')
        pass
    cdef public int __seed_state
    property seed_state:
        def __get__(self):
            return self.__seed_state
        def __set__(self, value):
                value = int(value)
                if value != self.__seed_state:
                    self.__seed_state = value
                    if self._initialized:
                        self.touch_seed_state()

    cpdef touch_seed_state(self):
        self.dirty_fields.add('seed_state')
        self.sync_dirty_fields.add('seed_state')
        pass
    cdef public int __seed_id
    property seed_id:
        def __get__(self):
            return self.__seed_id
        def __set__(self, value):
                value = int(value)
                if value != self.__seed_id:
                    self.__seed_id = value
                    if self._initialized:
                        self.touch_seed_id()

    cpdef touch_seed_id(self):
        self.dirty_fields.add('seed_id')
        self.sync_dirty_fields.add('seed_id')
        pass
    cdef public int __seed_state_last_change_time
    property seed_state_last_change_time:
        def __get__(self):
            return self.__seed_state_last_change_time
        def __set__(self, value):
                value = int(value)
                if value != self.__seed_state_last_change_time:
                    self.__seed_state_last_change_time = value
                    if self._initialized:
                        self.touch_seed_state_last_change_time()

    cpdef touch_seed_state_last_change_time(self):
        self.dirty_fields.add('seed_state_last_change_time')
        pass
    cdef public int __seed_state_next_change_time
    property seed_state_next_change_time:
        def __get__(self):
            return self.__seed_state_next_change_time
        def __set__(self, value):
                value = int(value)
                if value != self.__seed_state_next_change_time:
                    self.__seed_state_next_change_time = value
                    if self._initialized:
                        self.touch_seed_state_next_change_time()

    cpdef touch_seed_state_next_change_time(self):
        self.dirty_fields.add('seed_state_next_change_time')
        self.sync_dirty_fields.add('seed_state_next_change_time')
        pass
    cdef public int __seed_state_plant_time
    property seed_state_plant_time:
        def __get__(self):
            return self.__seed_state_plant_time
        def __set__(self, value):
                value = int(value)
                if value != self.__seed_state_plant_time:
                    self.__seed_state_plant_time = value
                    if self._initialized:
                        self.touch_seed_state_plant_time()

    cpdef touch_seed_state_plant_time(self):
        self.dirty_fields.add('seed_state_plant_time')
        pass
    cdef public int __seed_state_ripening_time
    property seed_state_ripening_time:
        def __get__(self):
            return self.__seed_state_ripening_time
        def __set__(self, value):
                value = int(value)
                if value != self.__seed_state_ripening_time:
                    self.__seed_state_ripening_time = value
                    if self._initialized:
                        self.touch_seed_state_ripening_time()

    cpdef touch_seed_state_ripening_time(self):
        self.dirty_fields.add('seed_state_ripening_time')
        self.sync_dirty_fields.add('seed_state_ripening_time')
        pass
    cdef public int __watering_used_count_ts
    property watering_used_count_ts:
        def __get__(self):
            return self.__watering_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__watering_used_count_ts:
                    self.__watering_used_count_ts = value
                    if self._initialized:
                        self.touch_watering_used_count_ts()

    cpdef touch_watering_used_count_ts(self):
        self.dirty_fields.add('watering_used_count_ts')
        pass
    cdef public int __watering_used_count
    property watering_used_count:
        def __get__(self):
            return self.__watering_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__watering_used_count:
                    self.__watering_used_count = value
                    if self._initialized:
                        self.touch_watering_used_count()

    cpdef touch_watering_used_count(self):
        self.dirty_fields.add('watering_used_count')
        self.sync_dirty_fields.add('watering_used_count')
        pass
    cdef public int __watering_time
    property watering_time:
        def __get__(self):
            return self.__watering_time
        def __set__(self, value):
                value = int(value)
                if value != self.__watering_time:
                    self.__watering_time = value
                    if self._initialized:
                        self.touch_watering_time()

    cpdef touch_watering_time(self):
        self.dirty_fields.add('watering_time')
        self.sync_dirty_fields.add('watering_time')
        pass
    cdef public int __worming_used_count_ts
    property worming_used_count_ts:
        def __get__(self):
            return self.__worming_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__worming_used_count_ts:
                    self.__worming_used_count_ts = value
                    if self._initialized:
                        self.touch_worming_used_count_ts()

    cpdef touch_worming_used_count_ts(self):
        self.dirty_fields.add('worming_used_count_ts')
        pass
    cdef public int __worming_used_count
    property worming_used_count:
        def __get__(self):
            return self.__worming_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__worming_used_count:
                    self.__worming_used_count = value
                    if self._initialized:
                        self.touch_worming_used_count()

    cpdef touch_worming_used_count(self):
        self.dirty_fields.add('worming_used_count')
        self.sync_dirty_fields.add('worming_used_count')
        pass
    cdef public int __worming_time
    property worming_time:
        def __get__(self):
            return self.__worming_time
        def __set__(self, value):
                value = int(value)
                if value != self.__worming_time:
                    self.__worming_time = value
                    if self._initialized:
                        self.touch_worming_time()

    cpdef touch_worming_time(self):
        self.dirty_fields.add('worming_time')
        self.sync_dirty_fields.add('worming_time')
        pass
    cdef public int __clean_reward_index
    property clean_reward_index:
        def __get__(self):
            return self.__clean_reward_index
        def __set__(self, value):
                value = int(value)
                if value != self.__clean_reward_index:
                    self.__clean_reward_index = value
                    if self._initialized:
                        self.touch_clean_reward_index()

    cpdef touch_clean_reward_index(self):
        self.dirty_fields.add('clean_reward_index')
        pass
    cdef public unicode __seed_reward_index
    property seed_reward_index:
        def __get__(self):
            return self.__seed_reward_index
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__seed_reward_index:
                    self.__seed_reward_index = value
                    if self._initialized:
                        self.touch_seed_reward_index()

    cpdef touch_seed_reward_index(self):
        self.dirty_fields.add('seed_reward_index')
        self.sync_dirty_fields.add('seed_reward_index')
        pass
    cdef public int __seal_seed_prob_id
    property seal_seed_prob_id:
        def __get__(self):
            return self.__seal_seed_prob_id
        def __set__(self, value):
                value = int(value)
                if value != self.__seal_seed_prob_id:
                    self.__seal_seed_prob_id = value
                    if self._initialized:
                        self.touch_seal_seed_prob_id()

    cpdef touch_seal_seed_prob_id(self):
        self.dirty_fields.add('seal_seed_prob_id')
        pass
    cdef public int __seal_seed_prob_campaign_last_time
    property seal_seed_prob_campaign_last_time:
        def __get__(self):
            return self.__seal_seed_prob_campaign_last_time
        def __set__(self, value):
                value = int(value)
                if value != self.__seal_seed_prob_campaign_last_time:
                    self.__seal_seed_prob_campaign_last_time = value
                    if self._initialized:
                        self.touch_seal_seed_prob_campaign_last_time()

    cpdef touch_seal_seed_prob_campaign_last_time(self):
        self.dirty_fields.add('seal_seed_prob_campaign_last_time')
        pass
    cdef public int __seal_seed_reward_next_index
    property seal_seed_reward_next_index:
        def __get__(self):
            return self.__seal_seed_reward_next_index
        def __set__(self, value):
                value = int(value)
                if value != self.__seal_seed_reward_next_index:
                    self.__seal_seed_reward_next_index = value
                    if self._initialized:
                        self.touch_seal_seed_reward_next_index()

    cpdef touch_seal_seed_reward_next_index(self):
        self.dirty_fields.add('seal_seed_reward_next_index')
        pass
    cdef public int __shake_tree_prob_id
    property shake_tree_prob_id:
        def __get__(self):
            return self.__shake_tree_prob_id
        def __set__(self, value):
                value = int(value)
                if value != self.__shake_tree_prob_id:
                    self.__shake_tree_prob_id = value
                    if self._initialized:
                        self.touch_shake_tree_prob_id()

    cpdef touch_shake_tree_prob_id(self):
        self.dirty_fields.add('shake_tree_prob_id')
        pass
    cdef public int __shake_tree_reward_free_next_index
    property shake_tree_reward_free_next_index:
        def __get__(self):
            return self.__shake_tree_reward_free_next_index
        def __set__(self, value):
                value = int(value)
                if value != self.__shake_tree_reward_free_next_index:
                    self.__shake_tree_reward_free_next_index = value
                    if self._initialized:
                        self.touch_shake_tree_reward_free_next_index()

    cpdef touch_shake_tree_reward_free_next_index(self):
        self.dirty_fields.add('shake_tree_reward_free_next_index')
        pass
    cdef public int __shake_tree_prob_campaign_last_time
    property shake_tree_prob_campaign_last_time:
        def __get__(self):
            return self.__shake_tree_prob_campaign_last_time
        def __set__(self, value):
                value = int(value)
                if value != self.__shake_tree_prob_campaign_last_time:
                    self.__shake_tree_prob_campaign_last_time = value
                    if self._initialized:
                        self.touch_shake_tree_prob_campaign_last_time()

    cpdef touch_shake_tree_prob_campaign_last_time(self):
        self.dirty_fields.add('shake_tree_prob_campaign_last_time')
        pass
    cdef public int __shake_tree_reward_pay_next_index
    property shake_tree_reward_pay_next_index:
        def __get__(self):
            return self.__shake_tree_reward_pay_next_index
        def __set__(self, value):
                value = int(value)
                if value != self.__shake_tree_reward_pay_next_index:
                    self.__shake_tree_reward_pay_next_index = value
                    if self._initialized:
                        self.touch_shake_tree_reward_pay_next_index()

    cpdef touch_shake_tree_reward_pay_next_index(self):
        self.dirty_fields.add('shake_tree_reward_pay_next_index')
        pass
    cdef public int __handsel_campaign_counter
    property handsel_campaign_counter:
        def __get__(self):
            return self.__handsel_campaign_counter
        def __set__(self, value):
                value = int(value)
                if value != self.__handsel_campaign_counter:
                    self.__handsel_campaign_counter = value
                    if self._initialized:
                        self.touch_handsel_campaign_counter()

    cpdef touch_handsel_campaign_counter(self):
        self.dirty_fields.add('handsel_campaign_counter')
        pass
    cdef public int __handsel_campaign_last_time
    property handsel_campaign_last_time:
        def __get__(self):
            return self.__handsel_campaign_last_time
        def __set__(self, value):
                value = int(value)
                if value != self.__handsel_campaign_last_time:
                    self.__handsel_campaign_last_time = value
                    if self._initialized:
                        self.touch_handsel_campaign_last_time()

    cpdef touch_handsel_campaign_last_time(self):
        self.dirty_fields.add('handsel_campaign_last_time')
        pass
    cdef public unicode __campaign_honor_point
    property campaign_honor_point:
        def __get__(self):
            return self.__campaign_honor_point
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__campaign_honor_point:
                    self.__campaign_honor_point = value
                    if self._initialized:
                        self.touch_campaign_honor_point()

    cpdef touch_campaign_honor_point(self):
        self.dirty_fields.add('campaign_honor_point')
        self.sync_dirty_fields.add('campaign_honor_point')
        pass
    cdef public int __flower_boss_campaign_total_hurt
    property flower_boss_campaign_total_hurt:
        def __get__(self):
            return self.__flower_boss_campaign_total_hurt
        def __set__(self, value):
                value = int(value)
                if value != self.__flower_boss_campaign_total_hurt:
                    self.__flower_boss_campaign_total_hurt = value
                    if self._initialized:
                        self.touch_flower_boss_campaign_total_hurt()

    cpdef touch_flower_boss_campaign_total_hurt(self):
        self.dirty_fields.add('flower_boss_campaign_total_hurt')
        self.sync_dirty_fields.add('flower_boss_campaign_total_hurt')
        pass
    cdef public int __flower_boss_campaign_last_time
    property flower_boss_campaign_last_time:
        def __get__(self):
            return self.__flower_boss_campaign_last_time
        def __set__(self, value):
                value = int(value)
                if value != self.__flower_boss_campaign_last_time:
                    self.__flower_boss_campaign_last_time = value
                    if self._initialized:
                        self.touch_flower_boss_campaign_last_time()

    cpdef touch_flower_boss_campaign_last_time(self):
        self.dirty_fields.add('flower_boss_campaign_last_time')
        pass
    cdef public int __climb_tower_max_floor
    property climb_tower_max_floor:
        def __get__(self):
            return self.__climb_tower_max_floor
        def __set__(self, value):
                value = int(value)
                if value != self.__climb_tower_max_floor:
                    self.__climb_tower_max_floor = value
                    if self._initialized:
                        self.touch_climb_tower_max_floor()

    cpdef touch_climb_tower_max_floor(self):
        self.dirty_fields.add('climb_tower_max_floor')
        self.sync_dirty_fields.add('climb_tower_max_floor')
        pass
    cdef public int __climb_tower_floor
    property climb_tower_floor:
        def __get__(self):
            return self.__climb_tower_floor
        def __set__(self, value):
                value = int(value)
                if value != self.__climb_tower_floor:
                    self.__climb_tower_floor = value
                    if self._initialized:
                        self.touch_climb_tower_floor()

    cpdef touch_climb_tower_floor(self):
        self.dirty_fields.add('climb_tower_floor')
        self.sync_dirty_fields.add('climb_tower_floor')
        pass
    cdef public object __climb_tower_tip_floors
    property climb_tower_tip_floors:
        def __get__(self):
            return self.__climb_tower_tip_floors
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'climb_tower_tip_floors', self.touch_climb_tower_tip_floors)
                if value != self.__climb_tower_tip_floors:
                    self.__climb_tower_tip_floors = value
                    if self._initialized:
                        self.touch_climb_tower_tip_floors()

    cpdef touch_climb_tower_tip_floors(self):
        self.dirty_fields.add('climb_tower_tip_floors')
        pass
    cdef public int __climb_tower_used_count_ts
    property climb_tower_used_count_ts:
        def __get__(self):
            return self.__climb_tower_used_count_ts
        def __set__(self, value):
                value = int(value)
                if value != self.__climb_tower_used_count_ts:
                    self.__climb_tower_used_count_ts = value
                    if self._initialized:
                        self.touch_climb_tower_used_count_ts()

    cpdef touch_climb_tower_used_count_ts(self):
        self.dirty_fields.add('climb_tower_used_count_ts')
        pass
    cdef public int __climb_tower_used_count
    property climb_tower_used_count:
        def __get__(self):
            return self.__climb_tower_used_count
        def __set__(self, value):
                value = int(value)
                if value != self.__climb_tower_used_count:
                    self.__climb_tower_used_count = value
                    if self._initialized:
                        self.touch_climb_tower_used_count()

    cpdef touch_climb_tower_used_count(self):
        self.dirty_fields.add('climb_tower_used_count')
        self.sync_dirty_fields.add('climb_tower_used_count')
        pass
    cdef public object __climb_tower_chests
    property climb_tower_chests:
        def __get__(self):
            return self.__climb_tower_chests
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'climb_tower_chests', self.touch_climb_tower_chests)
                if value != self.__climb_tower_chests:
                    self.__climb_tower_chests = value
                    if self._initialized:
                        self.touch_climb_tower_chests()

    cpdef touch_climb_tower_chests(self):
        self.dirty_fields.add('climb_tower_chests')
        pass
    cdef public object __climb_tower_history
    property climb_tower_history:
        def __get__(self):
            return self.__climb_tower_history
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_climb_tower_history(self):
        pass
    cdef public object __climb_tower_fight_history
    property climb_tower_fight_history:
        def __get__(self):
            return self.__climb_tower_fight_history
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_climb_tower_fight_history(self):
        pass
    cdef public int __climb_tower_accredit_floor
    property climb_tower_accredit_floor:
        def __get__(self):
            return self.__climb_tower_accredit_floor
        def __set__(self, value):
                value = int(value)
                if value != self.__climb_tower_accredit_floor:
                    self.__climb_tower_accredit_floor = value
                    if self._initialized:
                        self.touch_climb_tower_accredit_floor()

    cpdef touch_climb_tower_accredit_floor(self):
        self.dirty_fields.add('climb_tower_accredit_floor')
        self.sync_dirty_fields.add('climb_tower_accredit_floor')
        pass
    cdef public int __climb_tower_accredit_protect_time
    property climb_tower_accredit_protect_time:
        def __get__(self):
            return self.__climb_tower_accredit_protect_time
        def __set__(self, value):
                value = int(value)
                if value != self.__climb_tower_accredit_protect_time:
                    self.__climb_tower_accredit_protect_time = value
                    if self._initialized:
                        self.touch_climb_tower_accredit_protect_time()

    cpdef touch_climb_tower_accredit_protect_time(self):
        self.dirty_fields.add('climb_tower_accredit_protect_time')
        pass
    cdef public int __climb_tower_accredit_stash_time
    property climb_tower_accredit_stash_time:
        def __get__(self):
            return self.__climb_tower_accredit_stash_time
        def __set__(self, value):
                value = int(value)
                if value != self.__climb_tower_accredit_stash_time:
                    self.__climb_tower_accredit_stash_time = value
                    if self._initialized:
                        self.touch_climb_tower_accredit_stash_time()

    cpdef touch_climb_tower_accredit_stash_time(self):
        self.dirty_fields.add('climb_tower_accredit_stash_time')
        pass
    cdef public int __climb_tower_accredit_cd
    property climb_tower_accredit_cd:
        def __get__(self):
            return self.__climb_tower_accredit_cd
        def __set__(self, value):
                value = int(value)
                if value != self.__climb_tower_accredit_cd:
                    self.__climb_tower_accredit_cd = value
                    if self._initialized:
                        self.touch_climb_tower_accredit_cd()

    cpdef touch_climb_tower_accredit_cd(self):
        self.dirty_fields.add('climb_tower_accredit_cd')
        self.sync_dirty_fields.add('climb_tower_accredit_cd')
        self.__climb_tower_accredit_lineup = None
        self.clear_climb_tower_accredit_lineup()
        pass
    cdef public int __climb_tower_accredit_stash_earnings
    property climb_tower_accredit_stash_earnings:
        def __get__(self):
            return self.__climb_tower_accredit_stash_earnings
        def __set__(self, value):
                value = int(value)
                if value != self.__climb_tower_accredit_stash_earnings:
                    self.__climb_tower_accredit_stash_earnings = value
                    if self._initialized:
                        self.touch_climb_tower_accredit_stash_earnings()

    cpdef touch_climb_tower_accredit_stash_earnings(self):
        self.dirty_fields.add('climb_tower_accredit_stash_earnings')
        pass
    cdef public int __phantom
    property phantom:
        def __get__(self):
            return self.__phantom
        def __set__(self, value):
                value = int(value)
                if value != self.__phantom:
                    self.__phantom = value
                    if self._initialized:
                        self.touch_phantom()

    cpdef touch_phantom(self):
        self.dirty_fields.add('phantom')
        self.sync_dirty_fields.add('phantom')
        pass
    cdef public int __climb_tower_last_target
    property climb_tower_last_target:
        def __get__(self):
            return self.__climb_tower_last_target
        def __set__(self, value):
                value = int(value)
                if value != self.__climb_tower_last_target:
                    self.__climb_tower_last_target = value
                    if self._initialized:
                        self.touch_climb_tower_last_target()

    cpdef touch_climb_tower_last_target(self):
        self.dirty_fields.add('climb_tower_last_target')
        pass
    cdef public unicode __climb_tower_verify_code
    property climb_tower_verify_code:
        def __get__(self):
            return self.__climb_tower_verify_code
        def __set__(self, value):
                if isinstance(value, str):
                    value = value.decode('utf-8')
                value = value
                if value != self.__climb_tower_verify_code:
                    self.__climb_tower_verify_code = value
                    if self._initialized:
                        self.touch_climb_tower_verify_code()

    cpdef touch_climb_tower_verify_code(self):
        self.dirty_fields.add('climb_tower_verify_code')
        pass
    cdef public object __gems
    property gems:
        def __get__(self):
            return self.__gems
        def __set__(self, value):
            raise AttributeError('stored container types don\'t support __setattr__')

    cpdef touch_gems(self):
        pass
    cdef public object __dirty_gems
    property dirty_gems:
        def __get__(self):
            return self.__dirty_gems
        def __set__(self, value):
                value = SetContainer(value)
                value.init_entity(self, 'dirty_gems', self.touch_dirty_gems)
                if value != self.__dirty_gems:
                    self.__dirty_gems = value
                    if self._initialized:
                        self.touch_dirty_gems()

    cpdef touch_dirty_gems(self):
        pass
    cdef public int __inlay1
    property inlay1:
        def __get__(self):
            return self.__inlay1
        def __set__(self, value):
                value = int(value)
                if value != self.__inlay1:
                    self.__inlay1 = value
                    if self._initialized:
                        self.touch_inlay1()

    cpdef touch_inlay1(self):
        self.dirty_fields.add('inlay1')
        self.sync_dirty_fields.add('inlay1')
        pass
    cdef public int __inlay2
    property inlay2:
        def __get__(self):
            return self.__inlay2
        def __set__(self, value):
                value = int(value)
                if value != self.__inlay2:
                    self.__inlay2 = value
                    if self._initialized:
                        self.touch_inlay2()

    cpdef touch_inlay2(self):
        self.dirty_fields.add('inlay2')
        self.sync_dirty_fields.add('inlay2')
        pass
    cdef public int __inlay3
    property inlay3:
        def __get__(self):
            return self.__inlay3
        def __set__(self, value):
                value = int(value)
                if value != self.__inlay3:
                    self.__inlay3 = value
                    if self._initialized:
                        self.touch_inlay3()

    cpdef touch_inlay3(self):
        self.dirty_fields.add('inlay3')
        self.sync_dirty_fields.add('inlay3')
        pass
    cdef public int __inlay4
    property inlay4:
        def __get__(self):
            return self.__inlay4
        def __set__(self, value):
                value = int(value)
                if value != self.__inlay4:
                    self.__inlay4 = value
                    if self._initialized:
                        self.touch_inlay4()

    cpdef touch_inlay4(self):
        self.dirty_fields.add('inlay4')
        self.sync_dirty_fields.add('inlay4')
        pass
    cdef public int __inlay5
    property inlay5:
        def __get__(self):
            return self.__inlay5
        def __set__(self, value):
                value = int(value)
                if value != self.__inlay5:
                    self.__inlay5 = value
                    if self._initialized:
                        self.touch_inlay5()

    cpdef touch_inlay5(self):
        self.dirty_fields.add('inlay5')
        self.sync_dirty_fields.add('inlay5')
        pass
    cdef public int __inlay6
    property inlay6:
        def __get__(self):
            return self.__inlay6
        def __set__(self, value):
                value = int(value)
                if value != self.__inlay6:
                    self.__inlay6 = value
                    if self._initialized:
                        self.touch_inlay6()

    cpdef touch_inlay6(self):
        self.dirty_fields.add('inlay6')
        self.sync_dirty_fields.add('inlay6')
        pass

    # formula fields
    cdef public object __power
    property power:
        def __get__(self):
            if self.__power is None:
                value = fn.get_power(self.entityID, self.base_power, self.equip_power, self.faction_power, self.ambition_power, self.point_power, self.gems_power, self.honor_power)
                self.__power = int(value)
            return self.__power
        def __set__(self, value):
            assert self.__power is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__power = value
    cpdef clear_power(self):
        self.__power = None
        self.set_sync_dirty('power')
    cdef public object __newmailcount
    property newmailcount:
        def __get__(self):
            if self.__newmailcount is None:
                value = fn.get_newmailcount(self.mails)
                self.__newmailcount = int(value)
            return self.__newmailcount
        def __set__(self, value):
            assert self.__newmailcount is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__newmailcount = value
    cpdef clear_newmailcount(self):
        self.__newmailcount = None
        self.set_sync_dirty('newmailcount')
    cdef public object __expmax
    property expmax:
        def __get__(self):
            if self.__expmax is None:
                value = fn.get_max_exp(self.level)
                self.__expmax = int(value)
            return self.__expmax
        def __set__(self, value):
            assert self.__expmax is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__expmax = value
    cpdef clear_expmax(self):
        self.__expmax = None
        self.set_sync_dirty('expmax')
    cdef public object __expnxt
    property expnxt:
        def __get__(self):
            if self.__expnxt is None:
                value = fn.get_next_exp(self.level)
                self.__expnxt = int(value)
            return self.__expnxt
        def __set__(self, value):
            assert self.__expnxt is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__expnxt = value
    cpdef clear_expnxt(self):
        self.__expnxt = None
        self.set_sync_dirty('expnxt')
    cdef public object __loterry_hero_cost_A
    property loterry_hero_cost_A:
        def __get__(self):
            if self.__loterry_hero_cost_A is None:
                value = fn.get_loterry_hero_cost_A()
                self.__loterry_hero_cost_A = int(value)
            return self.__loterry_hero_cost_A
        def __set__(self, value):
            assert self.__loterry_hero_cost_A is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__loterry_hero_cost_A = value
    cpdef clear_loterry_hero_cost_A(self):
        self.__loterry_hero_cost_A = None
        self.set_sync_dirty('loterry_hero_cost_A')
    cdef public object __loterry_hero_cost_B
    property loterry_hero_cost_B:
        def __get__(self):
            if self.__loterry_hero_cost_B is None:
                value = fn.get_loterry_hero_cost_B()
                self.__loterry_hero_cost_B = int(value)
            return self.__loterry_hero_cost_B
        def __set__(self, value):
            assert self.__loterry_hero_cost_B is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__loterry_hero_cost_B = value
    cpdef clear_loterry_hero_cost_B(self):
        self.__loterry_hero_cost_B = None
        self.set_sync_dirty('loterry_hero_cost_B')
    cdef public object __loterry_hero_cost_C
    property loterry_hero_cost_C:
        def __get__(self):
            if self.__loterry_hero_cost_C is None:
                value = fn.get_loterry_hero_cost_C()
                self.__loterry_hero_cost_C = int(value)
            return self.__loterry_hero_cost_C
        def __set__(self, value):
            assert self.__loterry_hero_cost_C is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__loterry_hero_cost_C = value
    cpdef clear_loterry_hero_cost_C(self):
        self.__loterry_hero_cost_C = None
        self.set_sync_dirty('loterry_hero_cost_C')
    cdef public object __loterry_hero_rest_free_count_A
    property loterry_hero_rest_free_count_A:
        def __get__(self):
            if self.__loterry_hero_rest_free_count_A is None:
                value = fn.get_loterry_hero_rest_free_count_A(self.loterry_hero_used_free_count_A)
                self.__loterry_hero_rest_free_count_A = int(value)
            return self.__loterry_hero_rest_free_count_A
        def __set__(self, value):
            assert self.__loterry_hero_rest_free_count_A is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__loterry_hero_rest_free_count_A = value
    cpdef clear_loterry_hero_rest_free_count_A(self):
        self.__loterry_hero_rest_free_count_A = None
        self.set_sync_dirty('loterry_hero_rest_free_count_A')
    cdef public object __loterry_hero_rest_free_count_B
    property loterry_hero_rest_free_count_B:
        def __get__(self):
            if self.__loterry_hero_rest_free_count_B is None:
                value = fn.get_loterry_hero_rest_free_count_B(self.loterry_hero_used_free_count_B)
                self.__loterry_hero_rest_free_count_B = int(value)
            return self.__loterry_hero_rest_free_count_B
        def __set__(self, value):
            assert self.__loterry_hero_rest_free_count_B is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__loterry_hero_rest_free_count_B = value
    cpdef clear_loterry_hero_rest_free_count_B(self):
        self.__loterry_hero_rest_free_count_B = None
        self.set_sync_dirty('loterry_hero_rest_free_count_B')
    cdef public object __loterry_hero_rest_free_count_C
    property loterry_hero_rest_free_count_C:
        def __get__(self):
            if self.__loterry_hero_rest_free_count_C is None:
                value = fn.get_loterry_hero_rest_free_count_C(self.loterry_hero_used_free_count_C)
                self.__loterry_hero_rest_free_count_C = int(value)
            return self.__loterry_hero_rest_free_count_C
        def __set__(self, value):
            assert self.__loterry_hero_rest_free_count_C is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__loterry_hero_rest_free_count_C = value
    cpdef clear_loterry_hero_rest_free_count_C(self):
        self.__loterry_hero_rest_free_count_C = None
        self.set_sync_dirty('loterry_hero_rest_free_count_C')
    cdef public object __loterry_hero_rest_free_count_D
    property loterry_hero_rest_free_count_D:
        def __get__(self):
            if self.__loterry_hero_rest_free_count_D is None:
                value = fn.get_loterry_hero_rest_free_count_D(self.loterry_hero_used_free_count_D)
                self.__loterry_hero_rest_free_count_D = int(value)
            return self.__loterry_hero_rest_free_count_D
        def __set__(self, value):
            assert self.__loterry_hero_rest_free_count_D is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__loterry_hero_rest_free_count_D = value
    cpdef clear_loterry_hero_rest_free_count_D(self):
        self.__loterry_hero_rest_free_count_D = None
        self.set_sync_dirty('loterry_hero_rest_free_count_D')
    cdef public object __loterry_hero_tips_A
    property loterry_hero_tips_A:
        def __get__(self):
            if self.__loterry_hero_tips_A is None:
                value = fn.get_loterry_hero_tips_A(self.loterry_hero_count_A, self.lottery_money_accumulating)
                self.__loterry_hero_tips_A = value
            return self.__loterry_hero_tips_A
        def __set__(self, value):
            assert self.__loterry_hero_tips_A is None, 'can only set formula attribute when initialize'
            if isinstance(value, str):
                value = value.decode('utf-8')
            value = value
            self.__loterry_hero_tips_A = value
    cpdef clear_loterry_hero_tips_A(self):
        self.__loterry_hero_tips_A = None
        self.set_sync_dirty('loterry_hero_tips_A')
    cdef public object __loterry_hero_tips_B
    property loterry_hero_tips_B:
        def __get__(self):
            if self.__loterry_hero_tips_B is None:
                value = fn.get_loterry_hero_tips_B(self.loterry_hero_count_B, self.lottery_money_accumulating10)
                self.__loterry_hero_tips_B = value
            return self.__loterry_hero_tips_B
        def __set__(self, value):
            assert self.__loterry_hero_tips_B is None, 'can only set formula attribute when initialize'
            if isinstance(value, str):
                value = value.decode('utf-8')
            value = value
            self.__loterry_hero_tips_B = value
    cpdef clear_loterry_hero_tips_B(self):
        self.__loterry_hero_tips_B = None
        self.set_sync_dirty('loterry_hero_tips_B')
    cdef public object __loterry_hero_tips_C
    property loterry_hero_tips_C:
        def __get__(self):
            if self.__loterry_hero_tips_C is None:
                value = fn.get_loterry_hero_tips_C(self.loterry_hero_count_C, self.lottery_gold_accumulating)
                self.__loterry_hero_tips_C = value
            return self.__loterry_hero_tips_C
        def __set__(self, value):
            assert self.__loterry_hero_tips_C is None, 'can only set formula attribute when initialize'
            if isinstance(value, str):
                value = value.decode('utf-8')
            value = value
            self.__loterry_hero_tips_C = value
    cpdef clear_loterry_hero_tips_C(self):
        self.__loterry_hero_tips_C = None
        self.set_sync_dirty('loterry_hero_tips_C')
    cdef public object __loterry_hero_tips_D
    property loterry_hero_tips_D:
        def __get__(self):
            if self.__loterry_hero_tips_D is None:
                value = fn.get_loterry_hero_tips_D(self.loterry_hero_count_D, self.lottery_gold_accumulating10)
                self.__loterry_hero_tips_D = value
            return self.__loterry_hero_tips_D
        def __set__(self, value):
            assert self.__loterry_hero_tips_D is None, 'can only set formula attribute when initialize'
            if isinstance(value, str):
                value = value.decode('utf-8')
            value = value
            self.__loterry_hero_tips_D = value
    cpdef clear_loterry_hero_tips_D(self):
        self.__loterry_hero_tips_D = None
        self.set_sync_dirty('loterry_hero_tips_D')
    cdef public object __loterry_hero_cost_D
    property loterry_hero_cost_D:
        def __get__(self):
            if self.__loterry_hero_cost_D is None:
                value = fn.get_loterry_hero_cost_D()
                self.__loterry_hero_cost_D = int(value)
            return self.__loterry_hero_cost_D
        def __set__(self, value):
            assert self.__loterry_hero_cost_D is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__loterry_hero_cost_D = value
    cpdef clear_loterry_hero_cost_D(self):
        self.__loterry_hero_cost_D = None
        self.set_sync_dirty('loterry_hero_cost_D')
    cdef public object __resolvegold_level
    property resolvegold_level:
        def __get__(self):
            if self.__resolvegold_level is None:
                value = fn.resolvegold_level()
                self.__resolvegold_level = int(value)
            return self.__resolvegold_level
        def __set__(self, value):
            assert self.__resolvegold_level is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__resolvegold_level = value
    cpdef clear_resolvegold_level(self):
        self.__resolvegold_level = None
        self.set_sync_dirty('resolvegold_level')
    cdef public object __pvprankcount
    property pvprankcount:
        def __get__(self):
            if self.__pvprankcount is None:
                value = fn.get_pvprankcount()
                self.__pvprankcount = int(value)
            return self.__pvprankcount
        def __set__(self, value):
            assert self.__pvprankcount is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__pvprankcount = value
    cpdef clear_pvprankcount(self):
        self.__pvprankcount = None
        self.set_sync_dirty('pvprankcount')
    cdef public object __pvpseasonrewardreceived
    property pvpseasonrewardreceived:
        def __get__(self):
            if self.__pvpseasonrewardreceived is None:
                value = bool(self.pvpseasonreward)
                self.__pvpseasonrewardreceived = convert_bool(value)
            return self.__pvpseasonrewardreceived
        def __set__(self, value):
            assert self.__pvpseasonrewardreceived is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__pvpseasonrewardreceived = value
    cpdef clear_pvpseasonrewardreceived(self):
        self.__pvpseasonrewardreceived = None
        self.set_sync_dirty('pvpseasonrewardreceived')
    cdef public object __pvpstarttime
    property pvpstarttime:
        def __get__(self):
            if self.__pvpstarttime is None:
                value = fn.get_pvp_start_time(self.pvpopenflag)
                self.__pvpstarttime = int(value)
            return self.__pvpstarttime
        def __set__(self, value):
            assert self.__pvpstarttime is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__pvpstarttime = value
    cpdef clear_pvpstarttime(self):
        self.__pvpstarttime = None
        self.set_sync_dirty('pvpstarttime')
    cdef public object __pvpfinaltime
    property pvpfinaltime:
        def __get__(self):
            if self.__pvpfinaltime is None:
                value = fn.get_pvp_final_time(self.pvpopenflag)
                self.__pvpfinaltime = int(value)
            return self.__pvpfinaltime
        def __set__(self, value):
            assert self.__pvpfinaltime is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__pvpfinaltime = value
    cpdef clear_pvpfinaltime(self):
        self.__pvpfinaltime = None
        self.set_sync_dirty('pvpfinaltime')
    cdef public object __pvpopen
    property pvpopen:
        def __get__(self):
            if self.__pvpopen is None:
                value = fn.get_pvp_is_open(self.pvpopenflag)
                self.__pvpopen = convert_bool(value)
            return self.__pvpopen
        def __set__(self, value):
            assert self.__pvpopen is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__pvpopen = value
    cpdef clear_pvpopen(self):
        self.__pvpopen = None
        self.set_sync_dirty('pvpopen')
    cdef public object __slatelen
    property slatelen:
        def __get__(self):
            if self.__slatelen is None:
                value = fn.get_slatelen(self.slatereward_getedset)
                self.__slatelen = int(value)
            return self.__slatelen
        def __set__(self, value):
            assert self.__slatelen is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__slatelen = value
    cpdef clear_slatelen(self):
        self.__slatelen = None
        self.set_sync_dirty('slatelen')
    cdef public object __faction_level_rewards_count
    property faction_level_rewards_count:
        def __get__(self):
            if self.__faction_level_rewards_count is None:
                value = fn.get_faction_level_rewards_count(self.faction_level_rewards_received, self.faction_level)
                self.__faction_level_rewards_count = int(value)
            return self.__faction_level_rewards_count
        def __set__(self, value):
            assert self.__faction_level_rewards_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__faction_level_rewards_count = value
    cpdef clear_faction_level_rewards_count(self):
        self.__faction_level_rewards_count = None
        self.set_sync_dirty('faction_level_rewards_count')
    cdef public object __inviteFactionCount
    property inviteFactionCount:
        def __get__(self):
            if self.__inviteFactionCount is None:
                value = fn.get_invite_faction_count(self.inviteFactionSet)
                self.__inviteFactionCount = int(value)
            return self.__inviteFactionCount
        def __set__(self, value):
            assert self.__inviteFactionCount is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__inviteFactionCount = value
    cpdef clear_inviteFactionCount(self):
        self.__inviteFactionCount = None
        self.set_sync_dirty('inviteFactionCount')
    cdef public object __applyMemberCount
    property applyMemberCount:
        def __get__(self):
            if self.__applyMemberCount is None:
                value = fn.get_apply_member_count(self.applyMemberSet)
                self.__applyMemberCount = int(value)
            return self.__applyMemberCount
        def __set__(self, value):
            assert self.__applyMemberCount is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__applyMemberCount = value
    cpdef clear_applyMemberCount(self):
        self.__applyMemberCount = None
        self.set_sync_dirty('applyMemberCount')
    cdef public object __buy_sp_rest_count
    property buy_sp_rest_count:
        def __get__(self):
            if self.__buy_sp_rest_count is None:
                value = fn.get_vip_buy_sp_rest_count(self.vip, self.buy_sp_used_count)
                self.__buy_sp_rest_count = int(value)
            return self.__buy_sp_rest_count
        def __set__(self, value):
            assert self.__buy_sp_rest_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__buy_sp_rest_count = value
    cpdef clear_buy_sp_rest_count(self):
        self.__buy_sp_rest_count = None
        self.set_sync_dirty('buy_sp_rest_count')
    cdef public object __buy_sp_cost
    property buy_sp_cost:
        def __get__(self):
            if self.__buy_sp_cost is None:
                value = fn.get_buy_sp_cost(self.buy_sp_used_count)
                self.__buy_sp_cost = int(value)
            return self.__buy_sp_cost
        def __set__(self, value):
            assert self.__buy_sp_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__buy_sp_cost = value
    cpdef clear_buy_sp_cost(self):
        self.__buy_sp_cost = None
        self.set_sync_dirty('buy_sp_cost')
    cdef public object __vip
    property vip:
        def __get__(self):
            if self.__vip is None:
                value = fn.get_vip(self.credits)
                self.__vip = int(value)
            return self.__vip
        def __set__(self, value):
            assert self.__vip is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__vip = value
    cpdef clear_vip(self):
        self.__vip = None
        self.set_sync_dirty('vip')
    cdef public object __vip_refresh_fb_max_count
    property vip_refresh_fb_max_count:
        def __get__(self):
            if self.__vip_refresh_fb_max_count is None:
                value = fn.get_vip_refresh_fb_max_count(self.vip)
                self.__vip_refresh_fb_max_count = int(value)
            return self.__vip_refresh_fb_max_count
        def __set__(self, value):
            assert self.__vip_refresh_fb_max_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__vip_refresh_fb_max_count = value
    cpdef clear_vip_refresh_fb_max_count(self):
        self.__vip_refresh_fb_max_count = None
        self.set_sync_dirty('vip_refresh_fb_max_count')
    cdef public object __task_rest_patch_sign_up_count
    property task_rest_patch_sign_up_count:
        def __get__(self):
            if self.__task_rest_patch_sign_up_count is None:
                value = max(self.task_max_patch_sign_up_count - self.task_used_patch_sign_up_count, 0)
                self.__task_rest_patch_sign_up_count = int(value)
            return self.__task_rest_patch_sign_up_count
        def __set__(self, value):
            assert self.__task_rest_patch_sign_up_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__task_rest_patch_sign_up_count = value
    cpdef clear_task_rest_patch_sign_up_count(self):
        self.__task_rest_patch_sign_up_count = None
        self.set_sync_dirty('task_rest_patch_sign_up_count')
    cdef public object __task_today_is_sign_up
    property task_today_is_sign_up:
        def __get__(self):
            if self.__task_today_is_sign_up is None:
                value = fn.get_task_today_is_sign_up(self.task_last_sign_up_time)
                self.__task_today_is_sign_up = convert_bool(value)
            return self.__task_today_is_sign_up
        def __set__(self, value):
            assert self.__task_today_is_sign_up is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__task_today_is_sign_up = value
    cpdef clear_task_today_is_sign_up(self):
        self.__task_today_is_sign_up = None
        self.set_sync_dirty('task_today_is_sign_up')
    cdef public object __taskrewardscount1
    property taskrewardscount1:
        def __get__(self):
            if self.__taskrewardscount1 is None:
                value = fn.get_taskrewardscount1(self.taskrewards, self.task_sp_daily_receiveds)
                self.__taskrewardscount1 = int(value)
            return self.__taskrewardscount1
        def __set__(self, value):
            assert self.__taskrewardscount1 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardscount1 = value
    cpdef clear_taskrewardscount1(self):
        self.__taskrewardscount1 = None
        self.set_sync_dirty('taskrewardscount1')
    cdef public object __taskrewardscount2
    property taskrewardscount2:
        def __get__(self):
            if self.__taskrewardscount2 is None:
                value = fn.get_taskrewardscount2(self.taskrewards)
                self.__taskrewardscount2 = int(value)
            return self.__taskrewardscount2
        def __set__(self, value):
            assert self.__taskrewardscount2 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardscount2 = value
    cpdef clear_taskrewardscount2(self):
        self.__taskrewardscount2 = None
        self.set_sync_dirty('taskrewardscount2')
    cdef public object __taskrewardscount3
    property taskrewardscount3:
        def __get__(self):
            if self.__taskrewardscount3 is None:
                value = fn.get_taskrewardscount3(self.taskrewards)
                self.__taskrewardscount3 = int(value)
            return self.__taskrewardscount3
        def __set__(self, value):
            assert self.__taskrewardscount3 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardscount3 = value
    cpdef clear_taskrewardscount3(self):
        self.__taskrewardscount3 = None
        self.set_sync_dirty('taskrewardscount3')
    cdef public object __taskrewardscount4
    property taskrewardscount4:
        def __get__(self):
            if self.__taskrewardscount4 is None:
                value = fn.get_taskrewardscount4(self.taskrewards)
                self.__taskrewardscount4 = int(value)
            return self.__taskrewardscount4
        def __set__(self, value):
            assert self.__taskrewardscount4 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardscount4 = value
    cpdef clear_taskrewardscount4(self):
        self.__taskrewardscount4 = None
        self.set_sync_dirty('taskrewardscount4')
    cdef public object __taskrewardscountnew
    property taskrewardscountnew:
        def __get__(self):
            if self.__taskrewardscountnew is None:
                value = fn.get_taskrewardscountnew(self.taskrewards)
                self.__taskrewardscountnew = int(value)
            return self.__taskrewardscountnew
        def __set__(self, value):
            assert self.__taskrewardscountnew is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardscountnew = value
    cpdef clear_taskrewardscountnew(self):
        self.__taskrewardscountnew = None
        self.set_sync_dirty('taskrewardscountnew')
    cdef public object __taskrewardscount5
    property taskrewardscount5:
        def __get__(self):
            if self.__taskrewardscount5 is None:
                value = fn.get_taskrewardscount5(self.taskrewards)
                self.__taskrewardscount5 = int(value)
            return self.__taskrewardscount5
        def __set__(self, value):
            assert self.__taskrewardscount5 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardscount5 = value
    cpdef clear_taskrewardscount5(self):
        self.__taskrewardscount5 = None
        self.set_sync_dirty('taskrewardscount5')
    cdef public object __task_noob_flag
    property task_noob_flag:
        def __get__(self):
            if self.__task_noob_flag is None:
                value = fn.get_task_noob_flag(self.entityID, self.taskrewards)
                self.__task_noob_flag = convert_bool(value)
            return self.__task_noob_flag
        def __set__(self, value):
            assert self.__task_noob_flag is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__task_noob_flag = value
    cpdef clear_task_noob_flag(self):
        self.__task_noob_flag = None
        self.set_sync_dirty('task_noob_flag')
    cdef public object __task_noob_undo
    property task_noob_undo:
        def __get__(self):
            if self.__task_noob_undo is None:
                value = fn.get_task_noob_undo(self.entityID, self.taskrewards)
                self.__task_noob_undo = convert_bool(value)
            return self.__task_noob_undo
        def __set__(self, value):
            assert self.__task_noob_undo is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__task_noob_undo = value
    cpdef clear_task_noob_undo(self):
        self.__task_noob_undo = None
        self.set_sync_dirty('task_noob_undo')
    cdef public object __taskrewardscount6
    property taskrewardscount6:
        def __get__(self):
            if self.__taskrewardscount6 is None:
                value = fn.get_taskrewardscount6(self.taskrewards)
                self.__taskrewardscount6 = int(value)
            return self.__taskrewardscount6
        def __set__(self, value):
            assert self.__taskrewardscount6 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardscount6 = value
    cpdef clear_taskrewardscount6(self):
        self.__taskrewardscount6 = None
        self.set_sync_dirty('taskrewardscount6')
    cdef public object __taskrewardscount7
    property taskrewardscount7:
        def __get__(self):
            if self.__taskrewardscount7 is None:
                value = fn.get_taskrewardscount7(self.taskrewards)
                self.__taskrewardscount7 = int(value)
            return self.__taskrewardscount7
        def __set__(self, value):
            assert self.__taskrewardscount7 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardscount7 = value
    cpdef clear_taskrewardscount7(self):
        self.__taskrewardscount7 = None
        self.set_sync_dirty('taskrewardscount7')
    cdef public object __taskrewardscountsubtype1
    property taskrewardscountsubtype1:
        def __get__(self):
            if self.__taskrewardscountsubtype1 is None:
                value = fn.get_taskrewardscountsubtype1(self.taskrewards)
                self.__taskrewardscountsubtype1 = int(value)
            return self.__taskrewardscountsubtype1
        def __set__(self, value):
            assert self.__taskrewardscountsubtype1 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardscountsubtype1 = value
    cpdef clear_taskrewardscountsubtype1(self):
        self.__taskrewardscountsubtype1 = None
        self.set_sync_dirty('taskrewardscountsubtype1')
    cdef public object __taskrewardscountsubtype2
    property taskrewardscountsubtype2:
        def __get__(self):
            if self.__taskrewardscountsubtype2 is None:
                value = fn.get_taskrewardscountsubtype2(self.taskrewards)
                self.__taskrewardscountsubtype2 = int(value)
            return self.__taskrewardscountsubtype2
        def __set__(self, value):
            assert self.__taskrewardscountsubtype2 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardscountsubtype2 = value
    cpdef clear_taskrewardscountsubtype2(self):
        self.__taskrewardscountsubtype2 = None
        self.set_sync_dirty('taskrewardscountsubtype2')
    cdef public object __taskrewardscountsubtype3
    property taskrewardscountsubtype3:
        def __get__(self):
            if self.__taskrewardscountsubtype3 is None:
                value = fn.get_taskrewardscountsubtype3(self.taskrewards)
                self.__taskrewardscountsubtype3 = int(value)
            return self.__taskrewardscountsubtype3
        def __set__(self, value):
            assert self.__taskrewardscountsubtype3 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardscountsubtype3 = value
    cpdef clear_taskrewardscountsubtype3(self):
        self.__taskrewardscountsubtype3 = None
        self.set_sync_dirty('taskrewardscountsubtype3')
    cdef public object __taskrewardscountsubtype4
    property taskrewardscountsubtype4:
        def __get__(self):
            if self.__taskrewardscountsubtype4 is None:
                value = fn.get_taskrewardscountsubtype4(self.taskrewards)
                self.__taskrewardscountsubtype4 = int(value)
            return self.__taskrewardscountsubtype4
        def __set__(self, value):
            assert self.__taskrewardscountsubtype4 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardscountsubtype4 = value
    cpdef clear_taskrewardscountsubtype4(self):
        self.__taskrewardscountsubtype4 = None
        self.set_sync_dirty('taskrewardscountsubtype4')
    cdef public object __taskrewardscount12
    property taskrewardscount12:
        def __get__(self):
            if self.__taskrewardscount12 is None:
                value = fn.get_taskrewardscount12(self.taskrewards)
                self.__taskrewardscount12 = int(value)
            return self.__taskrewardscount12
        def __set__(self, value):
            assert self.__taskrewardscount12 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardscount12 = value
    cpdef clear_taskrewardscount12(self):
        self.__taskrewardscount12 = None
        self.set_sync_dirty('taskrewardscount12')
    cdef public object __taskrewardscount13
    property taskrewardscount13:
        def __get__(self):
            if self.__taskrewardscount13 is None:
                value = fn.get_taskrewardscount13(self.taskrewards)
                self.__taskrewardscount13 = int(value)
            return self.__taskrewardscount13
        def __set__(self, value):
            assert self.__taskrewardscount13 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardscount13 = value
    cpdef clear_taskrewardscount13(self):
        self.__taskrewardscount13 = None
        self.set_sync_dirty('taskrewardscount13')
    cdef public object __taskrewardscount14
    property taskrewardscount14:
        def __get__(self):
            if self.__taskrewardscount14 is None:
                value = fn.get_taskrewardscount14(self.taskrewards)
                self.__taskrewardscount14 = int(value)
            return self.__taskrewardscount14
        def __set__(self, value):
            assert self.__taskrewardscount14 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardscount14 = value
    cpdef clear_taskrewardscount14(self):
        self.__taskrewardscount14 = None
        self.set_sync_dirty('taskrewardscount14')
    cdef public object __taskrewardsdone14
    property taskrewardsdone14:
        def __get__(self):
            if self.__taskrewardsdone14 is None:
                value = fn.get_taskrewardsdone14(self.entityID, self.tasks, self.taskrewards)
                self.__taskrewardsdone14 = int(value)
            return self.__taskrewardsdone14
        def __set__(self, value):
            assert self.__taskrewardsdone14 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__taskrewardsdone14 = value
    cpdef clear_taskrewardsdone14(self):
        self.__taskrewardsdone14 = None
        self.set_sync_dirty('taskrewardsdone14')
    cdef public object __limited_packs_flag
    property limited_packs_flag:
        def __get__(self):
            if self.__limited_packs_flag is None:
                value = fn.get_limited_packs_flag()
                self.__limited_packs_flag = convert_bool(value)
            return self.__limited_packs_flag
        def __set__(self, value):
            assert self.__limited_packs_flag is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__limited_packs_flag = value
    cpdef clear_limited_packs_flag(self):
        self.__limited_packs_flag = None
        self.set_sync_dirty('limited_packs_flag')
    cdef public object __limited_packs_rest_count
    property limited_packs_rest_count:
        def __get__(self):
            if self.__limited_packs_rest_count is None:
                value = fn.get_limited_packs_rest_count(self.limited_packs_used_count)
                self.__limited_packs_rest_count = int(value)
            return self.__limited_packs_rest_count
        def __set__(self, value):
            assert self.__limited_packs_rest_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__limited_packs_rest_count = value
    cpdef clear_limited_packs_rest_count(self):
        self.__limited_packs_rest_count = None
        self.set_sync_dirty('limited_packs_rest_count')
    cdef public object __timelimited_packs_rest_time
    property timelimited_packs_rest_time:
        def __get__(self):
            if self.__timelimited_packs_rest_time is None:
                value = fn.get_timelimited_packs_rest_time()
                self.__timelimited_packs_rest_time = int(value)
            return self.__timelimited_packs_rest_time
        def __set__(self, value):
            assert self.__timelimited_packs_rest_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__timelimited_packs_rest_time = value
    cpdef clear_timelimited_packs_rest_time(self):
        self.__timelimited_packs_rest_time = None
        self.set_sync_dirty('timelimited_packs_rest_time')
    cdef public object __timelimited_packs_rest_count
    property timelimited_packs_rest_count:
        def __get__(self):
            if self.__timelimited_packs_rest_count is None:
                value = fn.get_timelimited_packs_rest_count(self.timelimited_packs_last_time)
                self.__timelimited_packs_rest_count = int(value)
            return self.__timelimited_packs_rest_count
        def __set__(self, value):
            assert self.__timelimited_packs_rest_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__timelimited_packs_rest_count = value
    cpdef clear_timelimited_packs_rest_count(self):
        self.__timelimited_packs_rest_count = None
        self.set_sync_dirty('timelimited_packs_rest_count')
    cdef public object __first_recharge_recv
    property first_recharge_recv:
        def __get__(self):
            if self.__first_recharge_recv is None:
                value = fn.get_first_recharge_recv(self.bought_recharges, self.first_recharge_flag)
                self.__first_recharge_recv = convert_bool(value)
            return self.__first_recharge_recv
        def __set__(self, value):
            assert self.__first_recharge_recv is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__first_recharge_recv = value
    cpdef clear_first_recharge_recv(self):
        self.__first_recharge_recv = None
        self.set_sync_dirty('first_recharge_recv')
    cdef public object __clean_campaign_vip
    property clean_campaign_vip:
        def __get__(self):
            if self.__clean_campaign_vip is None:
                value = fn.get_clean_campaign_vip(self.vip)
                self.__clean_campaign_vip = int(value)
            return self.__clean_campaign_vip
        def __set__(self, value):
            assert self.__clean_campaign_vip is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__clean_campaign_vip = value
    cpdef clear_clean_campaign_vip(self):
        self.__clean_campaign_vip = None
        self.set_sync_dirty('clean_campaign_vip')
    cdef public object __rank_reset_rest_count
    property rank_reset_rest_count:
        def __get__(self):
            if self.__rank_reset_rest_count is None:
                value = fn.get_rank_reset_rest_count(self.vip, self.rank_reset_used_count)
                self.__rank_reset_rest_count = int(value)
            return self.__rank_reset_rest_count
        def __set__(self, value):
            assert self.__rank_reset_rest_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__rank_reset_rest_count = value
    cpdef clear_rank_reset_rest_count(self):
        self.__rank_reset_rest_count = None
        self.set_sync_dirty('rank_reset_rest_count')
    cdef public object __rank_reset_cost
    property rank_reset_cost:
        def __get__(self):
            if self.__rank_reset_cost is None:
                value = fn.get_rank_reset_cost(self.rank_reset_used_count)
                self.__rank_reset_cost = int(value)
            return self.__rank_reset_cost
        def __set__(self, value):
            assert self.__rank_reset_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__rank_reset_cost = value
    cpdef clear_rank_reset_cost(self):
        self.__rank_reset_cost = None
        self.set_sync_dirty('rank_reset_cost')
    cdef public object __rank_refresh_cost
    property rank_refresh_cost:
        def __get__(self):
            if self.__rank_refresh_cost is None:
                value = fn.get_rank_refresh_cost(self.rank_refresh_used_count)
                self.__rank_refresh_cost = int(value)
            return self.__rank_refresh_cost
        def __set__(self, value):
            assert self.__rank_refresh_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__rank_refresh_cost = value
    cpdef clear_rank_refresh_cost(self):
        self.__rank_refresh_cost = None
        self.set_sync_dirty('rank_refresh_cost')
    cdef public object __todayfp_sp_max
    property todayfp_sp_max:
        def __get__(self):
            if self.__todayfp_sp_max is None:
                value = fn.get_todayfp_sp_max()
                self.__todayfp_sp_max = int(value)
            return self.__todayfp_sp_max
        def __set__(self, value):
            assert self.__todayfp_sp_max is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__todayfp_sp_max = value
    cpdef clear_todayfp_sp_max(self):
        self.__todayfp_sp_max = None
        self.set_sync_dirty('todayfp_sp_max')
    cdef public object __todayfp_donate_max
    property todayfp_donate_max:
        def __get__(self):
            if self.__todayfp_donate_max is None:
                value = fn.get_todayfp_donate_max()
                self.__todayfp_donate_max = int(value)
            return self.__todayfp_donate_max
        def __set__(self, value):
            assert self.__todayfp_donate_max is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__todayfp_donate_max = value
    cpdef clear_todayfp_donate_max(self):
        self.__todayfp_donate_max = None
        self.set_sync_dirty('todayfp_donate_max')
    cdef public object __todayfp
    property todayfp:
        def __get__(self):
            if self.__todayfp is None:
                value = self.todayfp_sp + self.todayfp_donate + self.todayfp_task
                self.__todayfp = int(value)
            return self.__todayfp
        def __set__(self, value):
            assert self.__todayfp is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__todayfp = value
    cpdef clear_todayfp(self):
        self.__todayfp = None
        self.set_sync_dirty('todayfp')
    cdef public object __mine_rob_max_count
    property mine_rob_max_count:
        def __get__(self):
            if self.__mine_rob_max_count is None:
                value = fn.get_mine_rob_max_count(self.vip)
                self.__mine_rob_max_count = int(value)
            return self.__mine_rob_max_count
        def __set__(self, value):
            assert self.__mine_rob_max_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mine_rob_max_count = value
    cpdef clear_mine_rob_max_count(self):
        self.__mine_rob_max_count = None
        self.set_sync_dirty('mine_rob_max_count')
    cdef public object __mine_safety1
    property mine_safety1:
        def __get__(self):
            if self.__mine_safety1 is None:
                value = fn.get_mine_safety(1, self.mine_level1)
                self.__mine_safety1 = int(value)
            return self.__mine_safety1
        def __set__(self, value):
            assert self.__mine_safety1 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mine_safety1 = value
    cpdef clear_mine_safety1(self):
        self.__mine_safety1 = None
        self.set_sync_dirty('mine_safety1')
    cdef public object __mine_time_past1
    property mine_time_past1:
        def __get__(self):
            if self.__mine_time_past1 is None:
                value = fn.get_past_time(self.mine_time1)
                self.__mine_time_past1 = int(value)
            return self.__mine_time_past1
        def __set__(self, value):
            assert self.__mine_time_past1 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mine_time_past1 = value
    cpdef clear_mine_time_past1(self):
        self.__mine_time_past1 = None
        self.set_sync_dirty('mine_time_past1')
    cdef public object __mine_maximum1
    property mine_maximum1:
        def __get__(self):
            if self.__mine_maximum1 is None:
                value = fn.get_mine_maximum(1, self.mine_level1)
                self.__mine_maximum1 = int(value)
            return self.__mine_maximum1
        def __set__(self, value):
            assert self.__mine_maximum1 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mine_maximum1 = value
    cpdef clear_mine_maximum1(self):
        self.__mine_maximum1 = None
        self.set_sync_dirty('mine_maximum1')
    cdef public object __mine_level1
    property mine_level1:
        def __get__(self):
            if self.__mine_level1 is None:
                value = fn.get_mine_level(1, self.level)
                self.__mine_level1 = int(value)
            return self.__mine_level1
        def __set__(self, value):
            assert self.__mine_level1 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mine_level1 = value
    cpdef clear_mine_level1(self):
        self.__mine_level1 = None
        self.set_sync_dirty('mine_level1')
    cdef public object __mine_safety2
    property mine_safety2:
        def __get__(self):
            if self.__mine_safety2 is None:
                value = fn.get_mine_safety(2, self.mine_level2)
                self.__mine_safety2 = int(value)
            return self.__mine_safety2
        def __set__(self, value):
            assert self.__mine_safety2 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mine_safety2 = value
    cpdef clear_mine_safety2(self):
        self.__mine_safety2 = None
        self.set_sync_dirty('mine_safety2')
    cdef public object __mine_time_past2
    property mine_time_past2:
        def __get__(self):
            if self.__mine_time_past2 is None:
                value = fn.get_past_time(self.mine_time2)
                self.__mine_time_past2 = int(value)
            return self.__mine_time_past2
        def __set__(self, value):
            assert self.__mine_time_past2 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mine_time_past2 = value
    cpdef clear_mine_time_past2(self):
        self.__mine_time_past2 = None
        self.set_sync_dirty('mine_time_past2')
    cdef public object __mine_maximum2
    property mine_maximum2:
        def __get__(self):
            if self.__mine_maximum2 is None:
                value = fn.get_mine_maximum(2, self.mine_level2)
                self.__mine_maximum2 = int(value)
            return self.__mine_maximum2
        def __set__(self, value):
            assert self.__mine_maximum2 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mine_maximum2 = value
    cpdef clear_mine_maximum2(self):
        self.__mine_maximum2 = None
        self.set_sync_dirty('mine_maximum2')
    cdef public object __mine_level2
    property mine_level2:
        def __get__(self):
            if self.__mine_level2 is None:
                value = fn.get_mine_level(2, self.level)
                self.__mine_level2 = int(value)
            return self.__mine_level2
        def __set__(self, value):
            assert self.__mine_level2 is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mine_level2 = value
    cpdef clear_mine_level2(self):
        self.__mine_level2 = None
        self.set_sync_dirty('mine_level2')
    cdef public object __uproar_refresh_rest_count
    property uproar_refresh_rest_count:
        def __get__(self):
            if self.__uproar_refresh_rest_count is None:
                value = self.uproar_refresh_max_count - self.uproar_refresh_used_count
                self.__uproar_refresh_rest_count = int(value)
            return self.__uproar_refresh_rest_count
        def __set__(self, value):
            assert self.__uproar_refresh_rest_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__uproar_refresh_rest_count = value
    cpdef clear_uproar_refresh_rest_count(self):
        self.__uproar_refresh_rest_count = None
        self.set_sync_dirty('uproar_refresh_rest_count')
    cdef public object __uproar_refresh_max_count
    property uproar_refresh_max_count:
        def __get__(self):
            if self.__uproar_refresh_max_count is None:
                value = fn.get_uproar_refresh_max_count(self.vip)
                self.__uproar_refresh_max_count = int(value)
            return self.__uproar_refresh_max_count
        def __set__(self, value):
            assert self.__uproar_refresh_max_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__uproar_refresh_max_count = value
    cpdef clear_uproar_refresh_max_count(self):
        self.__uproar_refresh_max_count = None
    cdef public object __last_target
    property last_target:
        def __get__(self):
            if self.__last_target is None:
                value = fn.get_uproar_last_target(self.uproar_targets_done)
                self.__last_target = int(value)
            return self.__last_target
        def __set__(self, value):
            assert self.__last_target is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__last_target = value
    cpdef clear_last_target(self):
        self.__last_target = None
        self.set_sync_dirty('last_target')
    cdef public object __last_chest
    property last_chest:
        def __get__(self):
            if self.__last_chest is None:
                value = fn.get_uproar_last_chest(self.uproar_chests_done)
                self.__last_chest = int(value)
            return self.__last_chest
        def __set__(self, value):
            assert self.__last_chest is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__last_chest = value
    cpdef clear_last_chest(self):
        self.__last_chest = None
        self.set_sync_dirty('last_chest')
    cdef public object __loot_rest_count
    property loot_rest_count:
        def __get__(self):
            if self.__loot_rest_count is None:
                value = self.loot_max_count - self.loot_used_count
                self.__loot_rest_count = int(value)
            return self.__loot_rest_count
        def __set__(self, value):
            assert self.__loot_rest_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__loot_rest_count = value
    cpdef clear_loot_rest_count(self):
        self.__loot_rest_count = None
        self.set_sync_dirty('loot_rest_count')
    cdef public object __reward_campaign_opened
    property reward_campaign_opened:
        def __get__(self):
            if self.__reward_campaign_opened is None:
                value = fn.get_reward_campaign_opened()
                self.__reward_campaign_opened = convert_bool(value)
            return self.__reward_campaign_opened
        def __set__(self, value):
            assert self.__reward_campaign_opened is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__reward_campaign_opened = value
    cpdef clear_reward_campaign_opened(self):
        self.__reward_campaign_opened = None
        self.set_sync_dirty('reward_campaign_opened')
    cdef public object __visit_free_rest_count
    property visit_free_rest_count:
        def __get__(self):
            if self.__visit_free_rest_count is None:
                value = fn.get_visit_free_rest_count(self.visit_free_used_count)
                self.__visit_free_rest_count = int(value)
            return self.__visit_free_rest_count
        def __set__(self, value):
            assert self.__visit_free_rest_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__visit_free_rest_count = value
    cpdef clear_visit_free_rest_count(self):
        self.__visit_free_rest_count = None
        self.set_sync_dirty('visit_free_rest_count')
    cdef public object __visit_cost
    property visit_cost:
        def __get__(self):
            if self.__visit_cost is None:
                value = fn.get_visit_cost()
                self.__visit_cost = int(value)
            return self.__visit_cost
        def __set__(self, value):
            assert self.__visit_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__visit_cost = value
    cpdef clear_visit_cost(self):
        self.__visit_cost = None
        self.set_sync_dirty('visit_cost')
    cdef public object __beg_flag
    property beg_flag:
        def __get__(self):
            if self.__beg_flag is None:
                value = fn.get_beg_flag(self.taskrewards, self.task_sp_daily_receiveds)
                self.__beg_flag = convert_bool(value)
            return self.__beg_flag
        def __set__(self, value):
            assert self.__beg_flag is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__beg_flag = value
    cpdef clear_beg_flag(self):
        self.__beg_flag = None
        self.set_sync_dirty('beg_flag')
    cdef public object __level_packs_flag
    property level_packs_flag:
        def __get__(self):
            if self.__level_packs_flag is None:
                value = fn.get_level_packs_flag(self.level_packs_done, self.level_packs_end)
                self.__level_packs_flag = convert_bool(value)
            return self.__level_packs_flag
        def __set__(self, value):
            assert self.__level_packs_flag is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__level_packs_flag = value
    cpdef clear_level_packs_flag(self):
        self.__level_packs_flag = None
        self.set_sync_dirty('level_packs_flag')
    cdef public object __level_packs_done_count
    property level_packs_done_count:
        def __get__(self):
            if self.__level_packs_done_count is None:
                value = len(self.level_packs_done)
                self.__level_packs_done_count = int(value)
            return self.__level_packs_done_count
        def __set__(self, value):
            assert self.__level_packs_done_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__level_packs_done_count = value
    cpdef clear_level_packs_done_count(self):
        self.__level_packs_done_count = None
        self.set_sync_dirty('level_packs_done_count')
    cdef public object __power_packs_flag
    property power_packs_flag:
        def __get__(self):
            if self.__power_packs_flag is None:
                value = fn.get_power_packs_flag(self.power_packs_done, self.power_packs_end)
                self.__power_packs_flag = convert_bool(value)
            return self.__power_packs_flag
        def __set__(self, value):
            assert self.__power_packs_flag is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__power_packs_flag = value
    cpdef clear_power_packs_flag(self):
        self.__power_packs_flag = None
        self.set_sync_dirty('power_packs_flag')
    cdef public object __power_packs_done_count
    property power_packs_done_count:
        def __get__(self):
            if self.__power_packs_done_count is None:
                value = len(self.power_packs_done)
                self.__power_packs_done_count = int(value)
            return self.__power_packs_done_count
        def __set__(self, value):
            assert self.__power_packs_done_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__power_packs_done_count = value
    cpdef clear_power_packs_done_count(self):
        self.__power_packs_done_count = None
        self.set_sync_dirty('power_packs_done_count')
    cdef public object __totallogin_flag
    property totallogin_flag:
        def __get__(self):
            if self.__totallogin_flag is None:
                value = fn.get_totallogin_flag(self.totallogin_end)
                self.__totallogin_flag = convert_bool(value)
            return self.__totallogin_flag
        def __set__(self, value):
            assert self.__totallogin_flag is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__totallogin_flag = value
    cpdef clear_totallogin_flag(self):
        self.__totallogin_flag = None
        self.set_sync_dirty('totallogin_flag')
    cdef public object __factionHP
    property factionHP:
        def __get__(self):
            if self.__factionHP is None:
                value = fn.get_faction_hp(self.strengthen_hp_level)
                self.__factionHP = float(value)
            return self.__factionHP
        def __set__(self, value):
            assert self.__factionHP is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__factionHP = value
    cpdef clear_factionHP(self):
        self.__factionHP = None
    cdef public object __factionATK
    property factionATK:
        def __get__(self):
            if self.__factionATK is None:
                value = fn.get_faction_atk(self.strengthen_at_level)
                self.__factionATK = float(value)
            return self.__factionATK
        def __set__(self, value):
            assert self.__factionATK is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__factionATK = value
    cpdef clear_factionATK(self):
        self.__factionATK = None
    cdef public object __factionDEF
    property factionDEF:
        def __get__(self):
            if self.__factionDEF is None:
                value = fn.get_faction_def(self.strengthen_df_level)
                self.__factionDEF = float(value)
            return self.__factionDEF
        def __set__(self, value):
            assert self.__factionDEF is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__factionDEF = value
    cpdef clear_factionDEF(self):
        self.__factionDEF = None
    cdef public object __factionCRI
    property factionCRI:
        def __get__(self):
            if self.__factionCRI is None:
                value = fn.get_faction_crit(self.strengthen_ct_level)
                self.__factionCRI = float(value)
            return self.__factionCRI
        def __set__(self, value):
            assert self.__factionCRI is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__factionCRI = value
    cpdef clear_factionCRI(self):
        self.__factionCRI = None
    cdef public object __base_power
    property base_power:
        def __get__(self):
            if self.__base_power is None:
                value = fn.get_base_power(self.entityID, self.lineups)
                self.__base_power = float(value)
            return self.__base_power
        def __set__(self, value):
            assert self.__base_power is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__base_power = value
    cpdef clear_base_power(self):
        self.__base_power = None
    cdef public object __equip_power
    property equip_power:
        def __get__(self):
            if self.__equip_power is None:
                value = fn.get_equip_power(self.entityID, self.lineups)
                self.__equip_power = float(value)
            return self.__equip_power
        def __set__(self, value):
            assert self.__equip_power is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__equip_power = value
    cpdef clear_equip_power(self):
        self.__equip_power = None
    cdef public object __faction_power
    property faction_power:
        def __get__(self):
            if self.__faction_power is None:
                value = fn.get_faction_power(self.factionHP, self.factionATK, self.factionDEF, self.factionCRI, self.factionEVA)
                self.__faction_power = float(value)
            return self.__faction_power
        def __set__(self, value):
            assert self.__faction_power is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__faction_power = value
    cpdef clear_faction_power(self):
        self.__faction_power = None
    cdef public object __treasure_count
    property treasure_count:
        def __get__(self):
            if self.__treasure_count is None:
                value = max(self.treasure_max_count - self.treasure_used_count, 0)
                self.__treasure_count = int(value)
            return self.__treasure_count
        def __set__(self, value):
            assert self.__treasure_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__treasure_count = value
    cpdef clear_treasure_count(self):
        self.__treasure_count = None
        self.set_sync_dirty('treasure_count')
    cdef public object __treasure_max_count
    property treasure_max_count:
        def __get__(self):
            if self.__treasure_max_count is None:
                value = fn.get_treasure_max_count(self.vip)
                self.__treasure_max_count = int(value)
            return self.__treasure_max_count
        def __set__(self, value):
            assert self.__treasure_max_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__treasure_max_count = value
    cpdef clear_treasure_max_count(self):
        self.__treasure_max_count = None
        self.set_sync_dirty('treasure_max_count')
    cdef public object __treasure_chest_gold
    property treasure_chest_gold:
        def __get__(self):
            if self.__treasure_chest_gold is None:
                value = fn.get_treasure_chest_gold(self.treasure_type)
                self.__treasure_chest_gold = int(value)
            return self.__treasure_chest_gold
        def __set__(self, value):
            assert self.__treasure_chest_gold is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__treasure_chest_gold = value
    cpdef clear_treasure_chest_gold(self):
        self.__treasure_chest_gold = None
        self.set_sync_dirty('treasure_chest_gold')
    cdef public object __friend_messages_count
    property friend_messages_count:
        def __get__(self):
            if self.__friend_messages_count is None:
                value = fn.get_friend_messages_count(self.friend_messages)
                self.__friend_messages_count = int(value)
            return self.__friend_messages_count
        def __set__(self, value):
            assert self.__friend_messages_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__friend_messages_count = value
    cpdef clear_friend_messages_count(self):
        self.__friend_messages_count = None
        self.set_sync_dirty('friend_messages_count')
    cdef public object __friend_count
    property friend_count:
        def __get__(self):
            if self.__friend_count is None:
                value = len(self.friendset)
                self.__friend_count = int(value)
            return self.__friend_count
        def __set__(self, value):
            assert self.__friend_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__friend_count = value
    cpdef clear_friend_count(self):
        self.__friend_count = None
        self.set_sync_dirty('friend_count')
    cdef public object __friend_max_count
    property friend_max_count:
        def __get__(self):
            if self.__friend_max_count is None:
                value = fn. get_friend_max_count(self.level)
                self.__friend_max_count = int(value)
            return self.__friend_max_count
        def __set__(self, value):
            assert self.__friend_max_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__friend_max_count = value
    cpdef clear_friend_max_count(self):
        self.__friend_max_count = None
        self.set_sync_dirty('friend_max_count')
    cdef public object __friend_applys_count
    property friend_applys_count:
        def __get__(self):
            if self.__friend_applys_count is None:
                value = len(self.friend_applys)
                self.__friend_applys_count = int(value)
            return self.__friend_applys_count
        def __set__(self, value):
            assert self.__friend_applys_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__friend_applys_count = value
    cpdef clear_friend_applys_count(self):
        self.__friend_applys_count = None
        self.set_sync_dirty('friend_applys_count')
    cdef public object __friend_gift_max_count
    property friend_gift_max_count:
        def __get__(self):
            if self.__friend_gift_max_count is None:
                value = fn.get_friend_gift_max_count(self.level)
                self.__friend_gift_max_count = int(value)
            return self.__friend_gift_max_count
        def __set__(self, value):
            assert self.__friend_gift_max_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__friend_gift_max_count = value
    cpdef clear_friend_gift_max_count(self):
        self.__friend_gift_max_count = None
        self.set_sync_dirty('friend_gift_max_count')
    cdef public object __tap_onekey
    property tap_onekey:
        def __get__(self):
            if self.__tap_onekey is None:
                value = fn.get_tap_onekey(self.vip)
                self.__tap_onekey = int(value)
            return self.__tap_onekey
        def __set__(self, value):
            assert self.__tap_onekey is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__tap_onekey = value
    cpdef clear_tap_onekey(self):
        self.__tap_onekey = None
        self.set_sync_dirty('tap_onekey')
    cdef public object __friendfb_remain_count
    property friendfb_remain_count:
        def __get__(self):
            if self.__friendfb_remain_count is None:
                value = fn.get_friendfb_remain_count(self.friendfb_used_count)
                self.__friendfb_remain_count = int(value)
            return self.__friendfb_remain_count
        def __set__(self, value):
            assert self.__friendfb_remain_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__friendfb_remain_count = value
    cpdef clear_friendfb_remain_count(self):
        self.__friendfb_remain_count = None
        self.set_sync_dirty('friendfb_remain_count')
    cdef public object __mall_silver_open_cost
    property mall_silver_open_cost:
        def __get__(self):
            if self.__mall_silver_open_cost is None:
                value = fn.get_mall_silver_open_cost(self.vip, self.level, self.mall_silver_opened)
                self.__mall_silver_open_cost = int(value)
            return self.__mall_silver_open_cost
        def __set__(self, value):
            assert self.__mall_silver_open_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mall_silver_open_cost = value
    cpdef clear_mall_silver_open_cost(self):
        self.__mall_silver_open_cost = None
        self.set_sync_dirty('mall_silver_open_cost')
    cdef public object __mall_silver_open_vip
    property mall_silver_open_vip:
        def __get__(self):
            if self.__mall_silver_open_vip is None:
                value = fn.get_mall_silver_open_vip()
                self.__mall_silver_open_vip = int(value)
            return self.__mall_silver_open_vip
        def __set__(self, value):
            assert self.__mall_silver_open_vip is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mall_silver_open_vip = value
    cpdef clear_mall_silver_open_vip(self):
        self.__mall_silver_open_vip = None
        self.set_sync_dirty('mall_silver_open_vip')
    cdef public object __mall_golden_open_cost
    property mall_golden_open_cost:
        def __get__(self):
            if self.__mall_golden_open_cost is None:
                value = fn.get_mall_golden_open_cost(self.vip, self.level, self.mall_golden_opened)
                self.__mall_golden_open_cost = int(value)
            return self.__mall_golden_open_cost
        def __set__(self, value):
            assert self.__mall_golden_open_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mall_golden_open_cost = value
    cpdef clear_mall_golden_open_cost(self):
        self.__mall_golden_open_cost = None
        self.set_sync_dirty('mall_golden_open_cost')
    cdef public object __mall_golden_open_vip
    property mall_golden_open_vip:
        def __get__(self):
            if self.__mall_golden_open_vip is None:
                value = fn.get_mall_golden_open_vip()
                self.__mall_golden_open_vip = int(value)
            return self.__mall_golden_open_vip
        def __set__(self, value):
            assert self.__mall_golden_open_vip is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mall_golden_open_vip = value
    cpdef clear_mall_golden_open_vip(self):
        self.__mall_golden_open_vip = None
        self.set_sync_dirty('mall_golden_open_vip')
    cdef public object __mailcount
    property mailcount:
        def __get__(self):
            if self.__mailcount is None:
                value = len(self.mails)
                self.__mailcount = int(value)
            return self.__mailcount
        def __set__(self, value):
            assert self.__mailcount is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mailcount = value
    cpdef clear_mailcount(self):
        self.__mailcount = None
        self.set_sync_dirty('mailcount')
    cdef public object __vip_packs_flag
    property vip_packs_flag:
        def __get__(self):
            if self.__vip_packs_flag is None:
                value = fn.get_vip_packs_flag(self.vip, self.vip_packs_today_bought_count)
                self.__vip_packs_flag = convert_bool(value)
            return self.__vip_packs_flag
        def __set__(self, value):
            assert self.__vip_packs_flag is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__vip_packs_flag = value
    cpdef clear_vip_packs_flag(self):
        self.__vip_packs_flag = None
        self.set_sync_dirty('vip_packs_flag')
    cdef public object __wish_rest_count
    property wish_rest_count:
        def __get__(self):
            if self.__wish_rest_count is None:
                value = fn.get_wish_rest_count(self.wish_used_count)
                self.__wish_rest_count = int(value)
            return self.__wish_rest_count
        def __set__(self, value):
            assert self.__wish_rest_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__wish_rest_count = value
    cpdef clear_wish_rest_count(self):
        self.__wish_rest_count = None
        self.set_sync_dirty('wish_rest_count')
    cdef public object __wish_remain_time
    property wish_remain_time:
        def __get__(self):
            if self.__wish_remain_time is None:
                value = fn.get_wish_remain_time()
                self.__wish_remain_time = int(value)
            return self.__wish_remain_time
        def __set__(self, value):
            assert self.__wish_remain_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__wish_remain_time = value
    cpdef clear_wish_remain_time(self):
        self.__wish_remain_time = None
        self.set_sync_dirty('wish_remain_time')
    cdef public object __weeks_acc_recharge_remain_time
    property weeks_acc_recharge_remain_time:
        def __get__(self):
            if self.__weeks_acc_recharge_remain_time is None:
                value = fn.get_weeks_acc_recharge_remain_time()
                self.__weeks_acc_recharge_remain_time = int(value)
            return self.__weeks_acc_recharge_remain_time
        def __set__(self, value):
            assert self.__weeks_acc_recharge_remain_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__weeks_acc_recharge_remain_time = value
    cpdef clear_weeks_acc_recharge_remain_time(self):
        self.__weeks_acc_recharge_remain_time = None
        self.set_sync_dirty('weeks_acc_recharge_remain_time')
    cdef public object __weeks_acc_recharge_can_receive
    property weeks_acc_recharge_can_receive:
        def __get__(self):
            if self.__weeks_acc_recharge_can_receive is None:
                value = fn.get_weeks_acc_recharge_can_receive(self.weeks_acc_recharge_rewards)
                self.__weeks_acc_recharge_can_receive = convert_bool(value)
            return self.__weeks_acc_recharge_can_receive
        def __set__(self, value):
            assert self.__weeks_acc_recharge_can_receive is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__weeks_acc_recharge_can_receive = value
    cpdef clear_weeks_acc_recharge_can_receive(self):
        self.__weeks_acc_recharge_can_receive = None
        self.set_sync_dirty('weeks_acc_recharge_can_receive')
    cdef public object __daily_acc_recharge_remain_time
    property daily_acc_recharge_remain_time:
        def __get__(self):
            if self.__daily_acc_recharge_remain_time is None:
                value = fn.get_daily_acc_recharge_remain_time()
                self.__daily_acc_recharge_remain_time = int(value)
            return self.__daily_acc_recharge_remain_time
        def __set__(self, value):
            assert self.__daily_acc_recharge_remain_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__daily_acc_recharge_remain_time = value
    cpdef clear_daily_acc_recharge_remain_time(self):
        self.__daily_acc_recharge_remain_time = None
        self.set_sync_dirty('daily_acc_recharge_remain_time')
    cdef public object __daily_acc_recharge_can_receive
    property daily_acc_recharge_can_receive:
        def __get__(self):
            if self.__daily_acc_recharge_can_receive is None:
                value = fn.get_daily_acc_recharge_can_receive(self.daily_acc_recharge_rewards)
                self.__daily_acc_recharge_can_receive = convert_bool(value)
            return self.__daily_acc_recharge_can_receive
        def __set__(self, value):
            assert self.__daily_acc_recharge_can_receive is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__daily_acc_recharge_can_receive = value
    cpdef clear_daily_acc_recharge_can_receive(self):
        self.__daily_acc_recharge_can_receive = None
        self.set_sync_dirty('daily_acc_recharge_can_receive')
    cdef public object __cycle_acc_recharge_remain_time
    property cycle_acc_recharge_remain_time:
        def __get__(self):
            if self.__cycle_acc_recharge_remain_time is None:
                value = fn.get_cycle_acc_recharge_remain_time()
                self.__cycle_acc_recharge_remain_time = int(value)
            return self.__cycle_acc_recharge_remain_time
        def __set__(self, value):
            assert self.__cycle_acc_recharge_remain_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__cycle_acc_recharge_remain_time = value
    cpdef clear_cycle_acc_recharge_remain_time(self):
        self.__cycle_acc_recharge_remain_time = None
        self.set_sync_dirty('cycle_acc_recharge_remain_time')
    cdef public object __cycle_acc_recharge_can_receive
    property cycle_acc_recharge_can_receive:
        def __get__(self):
            if self.__cycle_acc_recharge_can_receive is None:
                value = fn.get_cycle_acc_recharge_can_receive(self.cycle_acc_recharge_rewards)
                self.__cycle_acc_recharge_can_receive = convert_bool(value)
            return self.__cycle_acc_recharge_can_receive
        def __set__(self, value):
            assert self.__cycle_acc_recharge_can_receive is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__cycle_acc_recharge_can_receive = value
    cpdef clear_cycle_acc_recharge_can_receive(self):
        self.__cycle_acc_recharge_can_receive = None
        self.set_sync_dirty('cycle_acc_recharge_can_receive')
    cdef public object __month_acc_recharge_remain_time
    property month_acc_recharge_remain_time:
        def __get__(self):
            if self.__month_acc_recharge_remain_time is None:
                value = fn.get_month_acc_recharge_remain_time()
                self.__month_acc_recharge_remain_time = int(value)
            return self.__month_acc_recharge_remain_time
        def __set__(self, value):
            assert self.__month_acc_recharge_remain_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__month_acc_recharge_remain_time = value
    cpdef clear_month_acc_recharge_remain_time(self):
        self.__month_acc_recharge_remain_time = None
        self.set_sync_dirty('month_acc_recharge_remain_time')
    cdef public object __month_acc_recharge_can_receive
    property month_acc_recharge_can_receive:
        def __get__(self):
            if self.__month_acc_recharge_can_receive is None:
                value = fn.get_month_acc_recharge_can_receive(self.month_acc_recharge_rewards)
                self.__month_acc_recharge_can_receive = convert_bool(value)
            return self.__month_acc_recharge_can_receive
        def __set__(self, value):
            assert self.__month_acc_recharge_can_receive is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__month_acc_recharge_can_receive = value
    cpdef clear_month_acc_recharge_can_receive(self):
        self.__month_acc_recharge_can_receive = None
        self.set_sync_dirty('month_acc_recharge_can_receive')
    cdef public object __fund_open_rewards_can_receive
    property fund_open_rewards_can_receive:
        def __get__(self):
            if self.__fund_open_rewards_can_receive is None:
                value = fn.get_fund_open_rewards_can_receive(self.fund_bought_flag, self.fund_rewards_received, self.level)
                self.__fund_open_rewards_can_receive = convert_bool(value)
            return self.__fund_open_rewards_can_receive
        def __set__(self, value):
            assert self.__fund_open_rewards_can_receive is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__fund_open_rewards_can_receive = value
    cpdef clear_fund_open_rewards_can_receive(self):
        self.__fund_open_rewards_can_receive = None
        self.set_sync_dirty('fund_open_rewards_can_receive')
    cdef public object __fund_full_rewards_can_receive
    property fund_full_rewards_can_receive:
        def __get__(self):
            if self.__fund_full_rewards_can_receive is None:
                value = fn.get_fund_full_rewards_can_receive(self.fund_rewards_received)
                self.__fund_full_rewards_can_receive = convert_bool(value)
            return self.__fund_full_rewards_can_receive
        def __set__(self, value):
            assert self.__fund_full_rewards_can_receive is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__fund_full_rewards_can_receive = value
    cpdef clear_fund_full_rewards_can_receive(self):
        self.__fund_full_rewards_can_receive = None
        self.set_sync_dirty('fund_full_rewards_can_receive')
    cdef public object __check_in_rest_count
    property check_in_rest_count:
        def __get__(self):
            if self.__check_in_rest_count is None:
                value = fn.get_check_in_rest_count(self.createtime, self.check_in_used_count, self.check_in_today)
                self.__check_in_rest_count = int(value)
            return self.__check_in_rest_count
        def __set__(self, value):
            assert self.__check_in_rest_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__check_in_rest_count = value
    cpdef clear_check_in_rest_count(self):
        self.__check_in_rest_count = None
        self.set_sync_dirty('check_in_rest_count')
    cdef public object __monthly_card
    property monthly_card:
        def __get__(self):
            if self.__monthly_card is None:
                value = fn.get_monthly_card(self.monthly_card_time, self.monthly_card_received)
                self.__monthly_card = int(value)
            return self.__monthly_card
        def __set__(self, value):
            assert self.__monthly_card is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__monthly_card = value
    cpdef clear_monthly_card(self):
        self.__monthly_card = None
        self.set_sync_dirty('monthly_card')
    cdef public object __monthly_card_remain_amount
    property monthly_card_remain_amount:
        def __get__(self):
            if self.__monthly_card_remain_amount is None:
                value = fn.get_monthly_card_remain_amount(self.monthly_card_acc_amount)
                self.__monthly_card_remain_amount = int(value)
            return self.__monthly_card_remain_amount
        def __set__(self, value):
            assert self.__monthly_card_remain_amount is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__monthly_card_remain_amount = value
    cpdef clear_monthly_card_remain_amount(self):
        self.__monthly_card_remain_amount = None
        self.set_sync_dirty('monthly_card_remain_amount')
    cdef public object __point_power
    property point_power:
        def __get__(self):
            if self.__point_power is None:
                value = fn.get_point_power(self.entityID, self.point, self.lineups)
                self.__point_power = float(value)
            return self.__point_power
        def __set__(self, value):
            assert self.__point_power is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__point_power = value
    cpdef clear_point_power(self):
        self.__point_power = None
    cdef public object __point_addition
    property point_addition:
        def __get__(self):
            if self.__point_addition is None:
                value = fn.get_point_addition(self.point)
                self.__point_addition = int(value)
            return self.__point_addition
        def __set__(self, value):
            assert self.__point_addition is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__point_addition = value
    cpdef clear_point_addition(self):
        self.__point_addition = None
        self.set_sync_dirty('point_addition')
    cdef public object __enchant_stone_cost
    property enchant_stone_cost:
        def __get__(self):
            if self.__enchant_stone_cost is None:
                value = fn.get_enchant_stone_cost()
                self.__enchant_stone_cost = int(value)
            return self.__enchant_stone_cost
        def __set__(self, value):
            assert self.__enchant_stone_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__enchant_stone_cost = value
    cpdef clear_enchant_stone_cost(self):
        self.__enchant_stone_cost = None
        self.set_sync_dirty('enchant_stone_cost')
    cdef public object __enchant_ex_stone_cost
    property enchant_ex_stone_cost:
        def __get__(self):
            if self.__enchant_ex_stone_cost is None:
                value = fn.get_ex_enchant_stone_cost()
                self.__enchant_ex_stone_cost = int(value)
            return self.__enchant_ex_stone_cost
        def __set__(self, value):
            assert self.__enchant_ex_stone_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__enchant_ex_stone_cost = value
    cpdef clear_enchant_ex_stone_cost(self):
        self.__enchant_ex_stone_cost = None
        self.set_sync_dirty('enchant_ex_stone_cost')
    cdef public object __enchant_stone_to_gold
    property enchant_stone_to_gold:
        def __get__(self):
            if self.__enchant_stone_to_gold is None:
                value = fn.get_enchant_stone_to_gold()
                self.__enchant_stone_to_gold = int(value)
            return self.__enchant_stone_to_gold
        def __set__(self, value):
            assert self.__enchant_stone_to_gold is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__enchant_stone_to_gold = value
    cpdef clear_enchant_stone_to_gold(self):
        self.__enchant_stone_to_gold = None
        self.set_sync_dirty('enchant_stone_to_gold')
    cdef public object __enchant_free_rest_count
    property enchant_free_rest_count:
        def __get__(self):
            if self.__enchant_free_rest_count is None:
                value = fn.get_enchant_free_rest_count(self.enchant_free_used_count)
                self.__enchant_free_rest_count = int(value)
            return self.__enchant_free_rest_count
        def __set__(self, value):
            assert self.__enchant_free_rest_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__enchant_free_rest_count = value
    cpdef clear_enchant_free_rest_count(self):
        self.__enchant_free_rest_count = None
        self.set_sync_dirty('enchant_free_rest_count')
    cdef public object __sames
    property sames:
        def __get__(self):
            if self.__sames is None:
                value = fn.get_sames(self.pets)
                self.__sames = DictContainer(value)
            return self.__sames
        def __set__(self, value):
            assert self.__sames is None, 'can only set formula attribute when initialize'
            value = DictContainer(value)
            self.__sames = value
    cpdef clear_sames(self):
        self.__sames = None
    cdef public object __dlc_tasks
    property dlc_tasks:
        def __get__(self):
            if self.__dlc_tasks is None:
                value = fn.get_dlc_tasks()
                self.__dlc_tasks = DictContainer(value)
            return self.__dlc_tasks
        def __set__(self, value):
            assert self.__dlc_tasks is None, 'can only set formula attribute when initialize'
            value = DictContainer(value)
            self.__dlc_tasks = value
    cpdef clear_dlc_tasks(self):
        self.__dlc_tasks = None
    cdef public object __dlc_opened
    property dlc_opened:
        def __get__(self):
            if self.__dlc_opened is None:
                value = fn.get_dlc_opened()
                self.__dlc_opened = convert_bool(value)
            return self.__dlc_opened
        def __set__(self, value):
            assert self.__dlc_opened is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__dlc_opened = value
    cpdef clear_dlc_opened(self):
        self.__dlc_opened = None
        self.set_sync_dirty('dlc_opened')
    cdef public object __count_down_flag
    property count_down_flag:
        def __get__(self):
            if self.__count_down_flag is None:
                value = fn.get_count_down_flag(self.entityID, self.level, self.count_down_index)
                self.__count_down_flag = convert_bool(value)
            return self.__count_down_flag
        def __set__(self, value):
            assert self.__count_down_flag is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__count_down_flag = value
    cpdef clear_count_down_flag(self):
        self.__count_down_flag = None
        self.set_sync_dirty('count_down_flag')
    cdef public object __group_applys_count
    property group_applys_count:
        def __get__(self):
            if self.__group_applys_count is None:
                value = len(self.group_applys or {})
                self.__group_applys_count = int(value)
            return self.__group_applys_count
        def __set__(self, value):
            assert self.__group_applys_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__group_applys_count = value
    cpdef clear_group_applys_count(self):
        self.__group_applys_count = None
        self.set_sync_dirty('group_applys_count')
    cdef public object __gve_basereward
    property gve_basereward:
        def __get__(self):
            if self.__gve_basereward is None:
                value = fn.get_basereward(self.gve_groupdamage)
                self.__gve_basereward = value
            return self.__gve_basereward
        def __set__(self, value):
            assert self.__gve_basereward is None, 'can only set formula attribute when initialize'
            if isinstance(value, str):
                value = value.decode('utf-8')
            value = value
            self.__gve_basereward = value
    cpdef clear_gve_basereward(self):
        self.__gve_basereward = None
        self.set_sync_dirty('gve_basereward')
    cdef public object __gve_start_time
    property gve_start_time:
        def __get__(self):
            if self.__gve_start_time is None:
                value = fn.get_gve_start_time()
                self.__gve_start_time = int(value)
            return self.__gve_start_time
        def __set__(self, value):
            assert self.__gve_start_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__gve_start_time = value
    cpdef clear_gve_start_time(self):
        self.__gve_start_time = None
        self.set_sync_dirty('gve_start_time')
    cdef public object __gve_end_time
    property gve_end_time:
        def __get__(self):
            if self.__gve_end_time is None:
                value = fn.get_gve_end_time()
                self.__gve_end_time = int(value)
            return self.__gve_end_time
        def __set__(self, value):
            assert self.__gve_end_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__gve_end_time = value
    cpdef clear_gve_end_time(self):
        self.__gve_end_time = None
        self.set_sync_dirty('gve_end_time')
    cdef public object __gve_reborn_cost
    property gve_reborn_cost:
        def __get__(self):
            if self.__gve_reborn_cost is None:
                value = fn.get_gve_reborn_cost()
                self.__gve_reborn_cost = int(value)
            return self.__gve_reborn_cost
        def __set__(self, value):
            assert self.__gve_reborn_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__gve_reborn_cost = value
    cpdef clear_gve_reborn_cost(self):
        self.__gve_reborn_cost = None
        self.set_sync_dirty('gve_reborn_cost')
    cdef public object __gve_buff_addition
    property gve_buff_addition:
        def __get__(self):
            if self.__gve_buff_addition is None:
                value = fn.get_gve_buff_addition()
                self.__gve_buff_addition = int(value)
            return self.__gve_buff_addition
        def __set__(self, value):
            assert self.__gve_buff_addition is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__gve_buff_addition = value
    cpdef clear_gve_buff_addition(self):
        self.__gve_buff_addition = None
        self.set_sync_dirty('gve_buff_addition')
    cdef public object __boss_campaign_opened
    property boss_campaign_opened:
        def __get__(self):
            if self.__boss_campaign_opened is None:
                value = fn.get_boss_campaign_opened()
                self.__boss_campaign_opened = convert_bool(value)
            return self.__boss_campaign_opened
        def __set__(self, value):
            assert self.__boss_campaign_opened is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__boss_campaign_opened = value
    cpdef clear_boss_campaign_opened(self):
        self.__boss_campaign_opened = None
        self.set_sync_dirty('boss_campaign_opened')
    cdef public object __skillpoint_max
    property skillpoint_max:
        def __get__(self):
            if self.__skillpoint_max is None:
                value = fn.get_skillpoint_max(self.vip)
                self.__skillpoint_max = int(value)
            return self.__skillpoint_max
        def __set__(self, value):
            assert self.__skillpoint_max is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__skillpoint_max = value
    cpdef clear_skillpoint_max(self):
        self.__skillpoint_max = None
        self.set_sync_dirty('skillpoint_max')
    cdef public object __buy_rest_skillpoint_count
    property buy_rest_skillpoint_count:
        def __get__(self):
            if self.__buy_rest_skillpoint_count is None:
                value = fn.get_buy_rest_skillpoint_count(self.vip, self.buy_used_skillpoint_count)
                self.__buy_rest_skillpoint_count = int(value)
            return self.__buy_rest_skillpoint_count
        def __set__(self, value):
            assert self.__buy_rest_skillpoint_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__buy_rest_skillpoint_count = value
    cpdef clear_buy_rest_skillpoint_count(self):
        self.__buy_rest_skillpoint_count = None
        self.set_sync_dirty('buy_rest_skillpoint_count')
    cdef public object __buy_skillpoint_cost
    property buy_skillpoint_cost:
        def __get__(self):
            if self.__buy_skillpoint_cost is None:
                value = fn.get_buy_skillpoint_cost(self.buy_used_skillpoint_count)
                self.__buy_skillpoint_cost = int(value)
            return self.__buy_skillpoint_cost
        def __set__(self, value):
            assert self.__buy_skillpoint_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__buy_skillpoint_cost = value
    cpdef clear_buy_skillpoint_cost(self):
        self.__buy_skillpoint_cost = None
        self.set_sync_dirty('buy_skillpoint_cost')
    cdef public object __buy_skillpoint_gain
    property buy_skillpoint_gain:
        def __get__(self):
            if self.__buy_skillpoint_gain is None:
                value = fn.get_buy_skillpoint_gain(self.buy_used_skillpoint_count)
                self.__buy_skillpoint_gain = int(value)
            return self.__buy_skillpoint_gain
        def __set__(self, value):
            assert self.__buy_skillpoint_gain is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__buy_skillpoint_gain = value
    cpdef clear_buy_skillpoint_gain(self):
        self.__buy_skillpoint_gain = None
        self.set_sync_dirty('buy_skillpoint_gain')
    cdef public object __buy_rest_soul_count
    property buy_rest_soul_count:
        def __get__(self):
            if self.__buy_rest_soul_count is None:
                value = fn.get_buy_rest_soul_count(self.vip, self.buy_used_soul_count)
                self.__buy_rest_soul_count = int(value)
            return self.__buy_rest_soul_count
        def __set__(self, value):
            assert self.__buy_rest_soul_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__buy_rest_soul_count = value
    cpdef clear_buy_rest_soul_count(self):
        self.__buy_rest_soul_count = None
        self.set_sync_dirty('buy_rest_soul_count')
    cdef public object __buy_soul_cost
    property buy_soul_cost:
        def __get__(self):
            if self.__buy_soul_cost is None:
                value = fn.get_soul_cost(self.buy_used_soul_count)
                self.__buy_soul_cost = int(value)
            return self.__buy_soul_cost
        def __set__(self, value):
            assert self.__buy_soul_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__buy_soul_cost = value
    cpdef clear_buy_soul_cost(self):
        self.__buy_soul_cost = None
        self.set_sync_dirty('buy_soul_cost')
    cdef public object __buy_soul_gain
    property buy_soul_gain:
        def __get__(self):
            if self.__buy_soul_gain is None:
                value = fn.get_soul_gain(self.buy_used_soul_count)
                self.__buy_soul_gain = int(value)
            return self.__buy_soul_gain
        def __set__(self, value):
            assert self.__buy_soul_gain is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__buy_soul_gain = value
    cpdef clear_buy_soul_gain(self):
        self.__buy_soul_gain = None
        self.set_sync_dirty('buy_soul_gain')
    cdef public object __swap_refresh_cd_cost
    property swap_refresh_cd_cost:
        def __get__(self):
            if self.__swap_refresh_cd_cost is None:
                value = fn.get_swap_refresh_cd_cost()
                self.__swap_refresh_cd_cost = int(value)
            return self.__swap_refresh_cd_cost
        def __set__(self, value):
            assert self.__swap_refresh_cd_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__swap_refresh_cd_cost = value
    cpdef clear_swap_refresh_cd_cost(self):
        self.__swap_refresh_cd_cost = None
        self.set_sync_dirty('swap_refresh_cd_cost')
    cdef public object __swap_rest_count
    property swap_rest_count:
        def __get__(self):
            if self.__swap_rest_count is None:
                value = fn.get_swap_rest_count(self.swap_most_count, self.swap_used_count)
                self.__swap_rest_count = int(value)
            return self.__swap_rest_count
        def __set__(self, value):
            assert self.__swap_rest_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__swap_rest_count = value
    cpdef clear_swap_rest_count(self):
        self.__swap_rest_count = None
        self.set_sync_dirty('swap_rest_count')
    cdef public object __swap_most_count
    property swap_most_count:
        def __get__(self):
            if self.__swap_most_count is None:
                value = fn.get_swap_most_count()
                self.__swap_most_count = int(value)
            return self.__swap_most_count
        def __set__(self, value):
            assert self.__swap_most_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__swap_most_count = value
    cpdef clear_swap_most_count(self):
        self.__swap_most_count = None
        self.set_sync_dirty('swap_most_count')
    cdef public object __swap_rest_reset_count
    property swap_rest_reset_count:
        def __get__(self):
            if self.__swap_rest_reset_count is None:
                value = fn.get_swap_rest_reset_count(self.swap_most_reset_count, self.swap_used_reset_count)
                self.__swap_rest_reset_count = int(value)
            return self.__swap_rest_reset_count
        def __set__(self, value):
            assert self.__swap_rest_reset_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__swap_rest_reset_count = value
    cpdef clear_swap_rest_reset_count(self):
        self.__swap_rest_reset_count = None
        self.set_sync_dirty('swap_rest_reset_count')
    cdef public object __swap_most_reset_count
    property swap_most_reset_count:
        def __get__(self):
            if self.__swap_most_reset_count is None:
                value = fn.get_swap_most_reset_count(self.vip)
                self.__swap_most_reset_count = int(value)
            return self.__swap_most_reset_count
        def __set__(self, value):
            assert self.__swap_most_reset_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__swap_most_reset_count = value
    cpdef clear_swap_most_reset_count(self):
        self.__swap_most_reset_count = None
    cdef public object __swap_reset_count_cost
    property swap_reset_count_cost:
        def __get__(self):
            if self.__swap_reset_count_cost is None:
                value = fn.get_swap_reset_count_cost(self.swap_used_reset_count)
                self.__swap_reset_count_cost = int(value)
            return self.__swap_reset_count_cost
        def __set__(self, value):
            assert self.__swap_reset_count_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__swap_reset_count_cost = value
    cpdef clear_swap_reset_count_cost(self):
        self.__swap_reset_count_cost = None
        self.set_sync_dirty('swap_reset_count_cost')
    cdef public object __maze_most_count
    property maze_most_count:
        def __get__(self):
            if self.__maze_most_count is None:
                value = fn.get_maze_most_count()
                self.__maze_most_count = int(value)
            return self.__maze_most_count
        def __set__(self, value):
            assert self.__maze_most_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__maze_most_count = value
    cpdef clear_maze_most_count(self):
        self.__maze_most_count = None
        self.set_sync_dirty('maze_most_count')
    cdef public object __money_most_pool
    property money_most_pool:
        def __get__(self):
            if self.__money_most_pool is None:
                value = self.level * 5000
                self.__money_most_pool = int(value)
            return self.__money_most_pool
        def __set__(self, value):
            assert self.__money_most_pool is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__money_most_pool = value
    cpdef clear_money_most_pool(self):
        self.__money_most_pool = None
        self.set_sync_dirty('money_most_pool')
    cdef public object __maze_time_flag
    property maze_time_flag:
        def __get__(self):
            if self.__maze_time_flag is None:
                value = fn.get_maze_time_flag(self.mazes)
                self.__maze_time_flag = int(value)
            return self.__maze_time_flag
        def __set__(self, value):
            assert self.__maze_time_flag is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__maze_time_flag = value
    cpdef clear_maze_time_flag(self):
        self.__maze_time_flag = None
        self.set_sync_dirty('maze_time_flag')
    cdef public object __maze_case_cost
    property maze_case_cost:
        def __get__(self):
            if self.__maze_case_cost is None:
                value = fn.get_maze_case_cost()
                self.__maze_case_cost = int(value)
            return self.__maze_case_cost
        def __set__(self, value):
            assert self.__maze_case_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__maze_case_cost = value
    cpdef clear_maze_case_cost(self):
        self.__maze_case_cost = None
        self.set_sync_dirty('maze_case_cost')
    cdef public object __maze_onekey_vip
    property maze_onekey_vip:
        def __get__(self):
            if self.__maze_onekey_vip is None:
                value = fn.get_maze_onekey_vip()
                self.__maze_onekey_vip = int(value)
            return self.__maze_onekey_vip
        def __set__(self, value):
            assert self.__maze_onekey_vip is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__maze_onekey_vip = value
    cpdef clear_maze_onekey_vip(self):
        self.__maze_onekey_vip = None
        self.set_sync_dirty('maze_onekey_vip')
    cdef public object __maze_onekey_point
    property maze_onekey_point:
        def __get__(self):
            if self.__maze_onekey_point is None:
                value = fn.get_maze_onekey_point()
                self.__maze_onekey_point = int(value)
            return self.__maze_onekey_point
        def __set__(self, value):
            assert self.__maze_onekey_point is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__maze_onekey_point = value
    cpdef clear_maze_onekey_point(self):
        self.__maze_onekey_point = None
        self.set_sync_dirty('maze_onekey_point')
    cdef public object __online_packs_flag
    property online_packs_flag:
        def __get__(self):
            if self.__online_packs_flag is None:
                value = fn.get_online_packs_flag(self.level, self.online_packs_done)
                self.__online_packs_flag = convert_bool(value)
            return self.__online_packs_flag
        def __set__(self, value):
            assert self.__online_packs_flag is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__online_packs_flag = value
    cpdef clear_online_packs_flag(self):
        self.__online_packs_flag = None
        self.set_sync_dirty('online_packs_flag')
    cdef public object __daily_start_time
    property daily_start_time:
        def __get__(self):
            if self.__daily_start_time is None:
                value = fn.get_daily_start_time()
                self.__daily_start_time = int(value)
            return self.__daily_start_time
        def __set__(self, value):
            assert self.__daily_start_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__daily_start_time = value
    cpdef clear_daily_start_time(self):
        self.__daily_start_time = None
        self.set_sync_dirty('daily_start_time')
    cdef public object __daily_final_time
    property daily_final_time:
        def __get__(self):
            if self.__daily_final_time is None:
                value = fn.get_daily_final_time()
                self.__daily_final_time = int(value)
            return self.__daily_final_time
        def __set__(self, value):
            assert self.__daily_final_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__daily_final_time = value
    cpdef clear_daily_final_time(self):
        self.__daily_final_time = None
        self.set_sync_dirty('daily_final_time')
    cdef public object __daily_reborn_cost
    property daily_reborn_cost:
        def __get__(self):
            if self.__daily_reborn_cost is None:
                value = fn.get_daily_reborn_cost()
                self.__daily_reborn_cost = int(value)
            return self.__daily_reborn_cost
        def __set__(self, value):
            assert self.__daily_reborn_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__daily_reborn_cost = value
    cpdef clear_daily_reborn_cost(self):
        self.__daily_reborn_cost = None
        self.set_sync_dirty('daily_reborn_cost')
    cdef public object __daily_dead
    property daily_dead:
        def __get__(self):
            if self.__daily_dead is None:
                value = fn.get_daily_dead(self.entityID)
                self.__daily_dead = convert_bool(value)
            return self.__daily_dead
        def __set__(self, value):
            assert self.__daily_dead is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__daily_dead = value
    cpdef clear_daily_dead(self):
        self.__daily_dead = None
        self.set_sync_dirty('daily_dead')
    cdef public object __daily_win_count
    property daily_win_count:
        def __get__(self):
            if self.__daily_win_count is None:
                value = fn.get_daily_win_count(self.entityID)
                self.__daily_win_count = int(value)
            return self.__daily_win_count
        def __set__(self, value):
            assert self.__daily_win_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__daily_win_count = value
    cpdef clear_daily_win_count(self):
        self.__daily_win_count = None
        self.set_sync_dirty('daily_win_count')
    cdef public object __daily_inspire_rest_count
    property daily_inspire_rest_count:
        def __get__(self):
            if self.__daily_inspire_rest_count is None:
                value = self.daily_inspire_most_count - self.daily_inspire_used_count
                self.__daily_inspire_rest_count = int(value)
            return self.__daily_inspire_rest_count
        def __set__(self, value):
            assert self.__daily_inspire_rest_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__daily_inspire_rest_count = value
    cpdef clear_daily_inspire_rest_count(self):
        self.__daily_inspire_rest_count = None
        self.set_sync_dirty('daily_inspire_rest_count')
    cdef public object __daily_inspire_buff
    property daily_inspire_buff:
        def __get__(self):
            if self.__daily_inspire_buff is None:
                value = self.daily_inspire_used_count * 2
                self.__daily_inspire_buff = int(value)
            return self.__daily_inspire_buff
        def __set__(self, value):
            assert self.__daily_inspire_buff is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__daily_inspire_buff = value
    cpdef clear_daily_inspire_buff(self):
        self.__daily_inspire_buff = None
        self.set_sync_dirty('daily_inspire_buff')
    cdef public object __daily_inspire_cost
    property daily_inspire_cost:
        def __get__(self):
            if self.__daily_inspire_cost is None:
                value = (self.daily_inspire_used_count + 1) * 10
                self.__daily_inspire_cost = int(value)
            return self.__daily_inspire_cost
        def __set__(self, value):
            assert self.__daily_inspire_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__daily_inspire_cost = value
    cpdef clear_daily_inspire_cost(self):
        self.__daily_inspire_cost = None
        self.set_sync_dirty('daily_inspire_cost')
    cdef public object __daily_end_panel_flag
    property daily_end_panel_flag:
        def __get__(self):
            if self.__daily_end_panel_flag is None:
                value = bool(self.daily_end_panel)
                self.__daily_end_panel_flag = convert_bool(value)
            return self.__daily_end_panel_flag
        def __set__(self, value):
            assert self.__daily_end_panel_flag is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__daily_end_panel_flag = value
    cpdef clear_daily_end_panel_flag(self):
        self.__daily_end_panel_flag = None
        self.set_sync_dirty('daily_end_panel_flag')
    cdef public object __ambition_power
    property ambition_power:
        def __get__(self):
            if self.__ambition_power is None:
                value = fn.get_ambition_power(self.ambition, self.vip_ambition)
                self.__ambition_power = float(value)
            return self.__ambition_power
        def __set__(self, value):
            assert self.__ambition_power is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__ambition_power = value
    cpdef clear_ambition_power(self):
        self.__ambition_power = None
    cdef public object __ambition_cost
    property ambition_cost:
        def __get__(self):
            if self.__ambition_cost is None:
                value = fn.get_ambition_cost()
                self.__ambition_cost = int(value)
            return self.__ambition_cost
        def __set__(self, value):
            assert self.__ambition_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__ambition_cost = value
    cpdef clear_ambition_cost(self):
        self.__ambition_cost = None
        self.set_sync_dirty('ambition_cost')
    cdef public object __ambition_gold_cost
    property ambition_gold_cost:
        def __get__(self):
            if self.__ambition_gold_cost is None:
                value = fn.get_ambition_gold_cost()
                self.__ambition_gold_cost = int(value)
            return self.__ambition_gold_cost
        def __set__(self, value):
            assert self.__ambition_gold_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__ambition_gold_cost = value
    cpdef clear_ambition_gold_cost(self):
        self.__ambition_gold_cost = None
        self.set_sync_dirty('ambition_gold_cost')
    cdef public object __consume_campaign_rest_time
    property consume_campaign_rest_time:
        def __get__(self):
            if self.__consume_campaign_rest_time is None:
                value = fn.get_consume_campaign_rest_time()
                self.__consume_campaign_rest_time = int(value)
            return self.__consume_campaign_rest_time
        def __set__(self, value):
            assert self.__consume_campaign_rest_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__consume_campaign_rest_time = value
    cpdef clear_consume_campaign_rest_time(self):
        self.__consume_campaign_rest_time = None
        self.set_sync_dirty('consume_campaign_rest_time')
    cdef public object __consume_campaign_rewards_flag
    property consume_campaign_rewards_flag:
        def __get__(self):
            if self.__consume_campaign_rewards_flag is None:
                value = len(self.consume_campaign_rewards or [])
                self.__consume_campaign_rewards_flag = convert_bool(value)
            return self.__consume_campaign_rewards_flag
        def __set__(self, value):
            assert self.__consume_campaign_rewards_flag is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__consume_campaign_rewards_flag = value
    cpdef clear_consume_campaign_rewards_flag(self):
        self.__consume_campaign_rewards_flag = None
        self.set_sync_dirty('consume_campaign_rewards_flag')
    cdef public object __login_campaign_rest_time
    property login_campaign_rest_time:
        def __get__(self):
            if self.__login_campaign_rest_time is None:
                value = fn.get_login_campaign_rest_time()
                self.__login_campaign_rest_time = int(value)
            return self.__login_campaign_rest_time
        def __set__(self, value):
            assert self.__login_campaign_rest_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__login_campaign_rest_time = value
    cpdef clear_login_campaign_rest_time(self):
        self.__login_campaign_rest_time = None
        self.set_sync_dirty('login_campaign_rest_time')
    cdef public object __login_campaign_rewards_flag
    property login_campaign_rewards_flag:
        def __get__(self):
            if self.__login_campaign_rewards_flag is None:
                value = len(self.login_campaign_rewards or [])
                self.__login_campaign_rewards_flag = convert_bool(value)
            return self.__login_campaign_rewards_flag
        def __set__(self, value):
            assert self.__login_campaign_rewards_flag is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__login_campaign_rewards_flag = value
    cpdef clear_login_campaign_rewards_flag(self):
        self.__login_campaign_rewards_flag = None
        self.set_sync_dirty('login_campaign_rewards_flag')
    cdef public object __daily_recharge_remain_time
    property daily_recharge_remain_time:
        def __get__(self):
            if self.__daily_recharge_remain_time is None:
                value = fn.get_daily_recharge_remain_time()
                self.__daily_recharge_remain_time = int(value)
            return self.__daily_recharge_remain_time
        def __set__(self, value):
            assert self.__daily_recharge_remain_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__daily_recharge_remain_time = value
    cpdef clear_daily_recharge_remain_time(self):
        self.__daily_recharge_remain_time = None
        self.set_sync_dirty('daily_recharge_remain_time')
    cdef public object __daily_recharge_rewards_count
    property daily_recharge_rewards_count:
        def __get__(self):
            if self.__daily_recharge_rewards_count is None:
                value = len(self.daily_recharge_rewards or [])
                self.__daily_recharge_rewards_count = int(value)
            return self.__daily_recharge_rewards_count
        def __set__(self, value):
            assert self.__daily_recharge_rewards_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__daily_recharge_rewards_count = value
    cpdef clear_daily_recharge_rewards_count(self):
        self.__daily_recharge_rewards_count = None
        self.set_sync_dirty('daily_recharge_rewards_count')
    cdef public object __pet_exchange_cd
    property pet_exchange_cd:
        def __get__(self):
            if self.__pet_exchange_cd is None:
                value = fn.get_pet_exchange_cd()
                self.__pet_exchange_cd = int(value)
            return self.__pet_exchange_cd
        def __set__(self, value):
            assert self.__pet_exchange_cd is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__pet_exchange_cd = value
    cpdef clear_pet_exchange_cd(self):
        self.__pet_exchange_cd = None
        self.set_sync_dirty('pet_exchange_cd')
    cdef public object __lottery_campaign_cd
    property lottery_campaign_cd:
        def __get__(self):
            if self.__lottery_campaign_cd is None:
                value = fn.get_lottery_campaign_cd()
                self.__lottery_campaign_cd = int(value)
            return self.__lottery_campaign_cd
        def __set__(self, value):
            assert self.__lottery_campaign_cd is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__lottery_campaign_cd = value
    cpdef clear_lottery_campaign_cd(self):
        self.__lottery_campaign_cd = None
        self.set_sync_dirty('lottery_campaign_cd')
    cdef public object __lottery_campaign_discount
    property lottery_campaign_discount:
        def __get__(self):
            if self.__lottery_campaign_discount is None:
                value = fn.get_lottery_campaign_discount()
                self.__lottery_campaign_discount = int(value)
            return self.__lottery_campaign_discount
        def __set__(self, value):
            assert self.__lottery_campaign_discount is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__lottery_campaign_discount = value
    cpdef clear_lottery_campaign_discount(self):
        self.__lottery_campaign_discount = None
        self.set_sync_dirty('lottery_campaign_discount')
    cdef public object __lottery_campaign_hot
    property lottery_campaign_hot:
        def __get__(self):
            if self.__lottery_campaign_hot is None:
                value = fn.get_lottery_campaign_hot()
                self.__lottery_campaign_hot = value
            return self.__lottery_campaign_hot
        def __set__(self, value):
            assert self.__lottery_campaign_hot is None, 'can only set formula attribute when initialize'
            if isinstance(value, str):
                value = value.decode('utf-8')
            value = value
            self.__lottery_campaign_hot = value
    cpdef clear_lottery_campaign_hot(self):
        self.__lottery_campaign_hot = None
        self.set_sync_dirty('lottery_campaign_hot')
    cdef public object __lottery_campaign_hot_cd
    property lottery_campaign_hot_cd:
        def __get__(self):
            if self.__lottery_campaign_hot_cd is None:
                value = fn.get_lottery_campaign_hot_cd()
                self.__lottery_campaign_hot_cd = int(value)
            return self.__lottery_campaign_hot_cd
        def __set__(self, value):
            assert self.__lottery_campaign_hot_cd is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__lottery_campaign_hot_cd = value
    cpdef clear_lottery_campaign_hot_cd(self):
        self.__lottery_campaign_hot_cd = None
        self.set_sync_dirty('lottery_campaign_hot_cd')
    cdef public object __mat_exchange_campaign_cd
    property mat_exchange_campaign_cd:
        def __get__(self):
            if self.__mat_exchange_campaign_cd is None:
                value = fn.get_mat_exchange_campaign_cd()
                self.__mat_exchange_campaign_cd = int(value)
            return self.__mat_exchange_campaign_cd
        def __set__(self, value):
            assert self.__mat_exchange_campaign_cd is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__mat_exchange_campaign_cd = value
    cpdef clear_mat_exchange_campaign_cd(self):
        self.__mat_exchange_campaign_cd = None
        self.set_sync_dirty('mat_exchange_campaign_cd')
    cdef public object __city_dungeon_start_time
    property city_dungeon_start_time:
        def __get__(self):
            if self.__city_dungeon_start_time is None:
                value = fn.get_city_dungeon_start_time()
                self.__city_dungeon_start_time = int(value)
            return self.__city_dungeon_start_time
        def __set__(self, value):
            assert self.__city_dungeon_start_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__city_dungeon_start_time = value
    cpdef clear_city_dungeon_start_time(self):
        self.__city_dungeon_start_time = None
        self.set_sync_dirty('city_dungeon_start_time')
    cdef public object __city_dungeon_final_time
    property city_dungeon_final_time:
        def __get__(self):
            if self.__city_dungeon_final_time is None:
                value = fn.get_city_dungeon_final_time()
                self.__city_dungeon_final_time = int(value)
            return self.__city_dungeon_final_time
        def __set__(self, value):
            assert self.__city_dungeon_final_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__city_dungeon_final_time = value
    cpdef clear_city_dungeon_final_time(self):
        self.__city_dungeon_final_time = None
        self.set_sync_dirty('city_dungeon_final_time')
    cdef public object __city_dungeon_rewards_flag
    property city_dungeon_rewards_flag:
        def __get__(self):
            if self.__city_dungeon_rewards_flag is None:
                value = bool(self.city_dungeon_rewards)
                self.__city_dungeon_rewards_flag = convert_bool(value)
            return self.__city_dungeon_rewards_flag
        def __set__(self, value):
            assert self.__city_dungeon_rewards_flag is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__city_dungeon_rewards_flag = value
    cpdef clear_city_dungeon_rewards_flag(self):
        self.__city_dungeon_rewards_flag = None
        self.set_sync_dirty('city_dungeon_rewards_flag')
    cdef public object __city_contend_rewards_flag
    property city_contend_rewards_flag:
        def __get__(self):
            if self.__city_contend_rewards_flag is None:
                value = bool(self.city_contend_rewards)
                self.__city_contend_rewards_flag = convert_bool(value)
            return self.__city_contend_rewards_flag
        def __set__(self, value):
            assert self.__city_contend_rewards_flag is None, 'can only set formula attribute when initialize'
            value = convert_bool(value)
            self.__city_contend_rewards_flag = value
    cpdef clear_city_contend_rewards_flag(self):
        self.__city_contend_rewards_flag = None
        self.set_sync_dirty('city_contend_rewards_flag')
    cdef public object __city_contend_start_time
    property city_contend_start_time:
        def __get__(self):
            if self.__city_contend_start_time is None:
                value = fn.get_city_contend_start_time()
                self.__city_contend_start_time = int(value)
            return self.__city_contend_start_time
        def __set__(self, value):
            assert self.__city_contend_start_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__city_contend_start_time = value
    cpdef clear_city_contend_start_time(self):
        self.__city_contend_start_time = None
        self.set_sync_dirty('city_contend_start_time')
    cdef public object __city_contend_final_time
    property city_contend_final_time:
        def __get__(self):
            if self.__city_contend_final_time is None:
                value = fn.get_city_contend_final_time()
                self.__city_contend_final_time = int(value)
            return self.__city_contend_final_time
        def __set__(self, value):
            assert self.__city_contend_final_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__city_contend_final_time = value
    cpdef clear_city_contend_final_time(self):
        self.__city_contend_final_time = None
        self.set_sync_dirty('city_contend_final_time')
    cdef public object __exchange_campaign_remain_time
    property exchange_campaign_remain_time:
        def __get__(self):
            if self.__exchange_campaign_remain_time is None:
                value = fn.get_exchange_campaign_remain_time()
                self.__exchange_campaign_remain_time = int(value)
            return self.__exchange_campaign_remain_time
        def __set__(self, value):
            assert self.__exchange_campaign_remain_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__exchange_campaign_remain_time = value
    cpdef clear_exchange_campaign_remain_time(self):
        self.__exchange_campaign_remain_time = None
        self.set_sync_dirty('exchange_campaign_remain_time')
    cdef public object __refresh_store_campaign_remain_time
    property refresh_store_campaign_remain_time:
        def __get__(self):
            if self.__refresh_store_campaign_remain_time is None:
                value = fn.get_refresh_store_campaign_remain_time()
                self.__refresh_store_campaign_remain_time = int(value)
            return self.__refresh_store_campaign_remain_time
        def __set__(self, value):
            assert self.__refresh_store_campaign_remain_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__refresh_store_campaign_remain_time = value
    cpdef clear_refresh_store_campaign_remain_time(self):
        self.__refresh_store_campaign_remain_time = None
        self.set_sync_dirty('refresh_store_campaign_remain_time')
    cdef public object __refresh_reward_done_count
    property refresh_reward_done_count:
        def __get__(self):
            if self.__refresh_reward_done_count is None:
                value = len(self.refresh_reward_done or [])
                self.__refresh_reward_done_count = int(value)
            return self.__refresh_reward_done_count
        def __set__(self, value):
            assert self.__refresh_reward_done_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__refresh_reward_done_count = value
    cpdef clear_refresh_reward_done_count(self):
        self.__refresh_reward_done_count = None
        self.set_sync_dirty('refresh_reward_done_count')
    cdef public object __arbor_day_campaign_remain_time
    property arbor_day_campaign_remain_time:
        def __get__(self):
            if self.__arbor_day_campaign_remain_time is None:
                value = fn.get_arbor_day_campaign_remain_time()
                self.__arbor_day_campaign_remain_time = int(value)
            return self.__arbor_day_campaign_remain_time
        def __set__(self, value):
            assert self.__arbor_day_campaign_remain_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__arbor_day_campaign_remain_time = value
    cpdef clear_arbor_day_campaign_remain_time(self):
        self.__arbor_day_campaign_remain_time = None
        self.set_sync_dirty('arbor_day_campaign_remain_time')
    cdef public object __shake_tree_free_count
    property shake_tree_free_count:
        def __get__(self):
            if self.__shake_tree_free_count is None:
                value = fn.get_shake_tree_free_count()
                self.__shake_tree_free_count = int(value)
            return self.__shake_tree_free_count
        def __set__(self, value):
            assert self.__shake_tree_free_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__shake_tree_free_count = value
    cpdef clear_shake_tree_free_count(self):
        self.__shake_tree_free_count = None
        self.set_sync_dirty('shake_tree_free_count')
    cdef public object __shake_tree_max_count
    property shake_tree_max_count:
        def __get__(self):
            if self.__shake_tree_max_count is None:
                value = fn.get_shake_tree_max_count()
                self.__shake_tree_max_count = int(value)
            return self.__shake_tree_max_count
        def __set__(self, value):
            assert self.__shake_tree_max_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__shake_tree_max_count = value
    cpdef clear_shake_tree_max_count(self):
        self.__shake_tree_max_count = None
        self.set_sync_dirty('shake_tree_max_count')
    cdef public object __shake_tree_cost
    property shake_tree_cost:
        def __get__(self):
            if self.__shake_tree_cost is None:
                value = fn.get_shake_tree_cost()
                self.__shake_tree_cost = int(value)
            return self.__shake_tree_cost
        def __set__(self, value):
            assert self.__shake_tree_cost is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__shake_tree_cost = value
    cpdef clear_shake_tree_cost(self):
        self.__shake_tree_cost = None
        self.set_sync_dirty('shake_tree_cost')
    cdef public object __seed_campaign_remain_time
    property seed_campaign_remain_time:
        def __get__(self):
            if self.__seed_campaign_remain_time is None:
                value = fn.get_seed_campaign_remain_time()
                self.__seed_campaign_remain_time = int(value)
            return self.__seed_campaign_remain_time
        def __set__(self, value):
            assert self.__seed_campaign_remain_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__seed_campaign_remain_time = value
    cpdef clear_seed_campaign_remain_time(self):
        self.__seed_campaign_remain_time = None
        self.set_sync_dirty('seed_campaign_remain_time')
    cdef public object __watering_max_count
    property watering_max_count:
        def __get__(self):
            if self.__watering_max_count is None:
                value = fn.get_watering_max_count()
                self.__watering_max_count = int(value)
            return self.__watering_max_count
        def __set__(self, value):
            assert self.__watering_max_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__watering_max_count = value
    cpdef clear_watering_max_count(self):
        self.__watering_max_count = None
        self.set_sync_dirty('watering_max_count')
    cdef public object __worming_max_count
    property worming_max_count:
        def __get__(self):
            if self.__worming_max_count is None:
                value = fn.get_worming_max_count()
                self.__worming_max_count = int(value)
            return self.__worming_max_count
        def __set__(self, value):
            assert self.__worming_max_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__worming_max_count = value
    cpdef clear_worming_max_count(self):
        self.__worming_max_count = None
        self.set_sync_dirty('worming_max_count')
    cdef public object __handsel_campaign_remain_time
    property handsel_campaign_remain_time:
        def __get__(self):
            if self.__handsel_campaign_remain_time is None:
                value = fn.get_handsel_campaign_remain_time()
                self.__handsel_campaign_remain_time = int(value)
            return self.__handsel_campaign_remain_time
        def __set__(self, value):
            assert self.__handsel_campaign_remain_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__handsel_campaign_remain_time = value
    cpdef clear_handsel_campaign_remain_time(self):
        self.__handsel_campaign_remain_time = None
        self.set_sync_dirty('handsel_campaign_remain_time')
    cdef public object __flower_boss_campaign_remain_time
    property flower_boss_campaign_remain_time:
        def __get__(self):
            if self.__flower_boss_campaign_remain_time is None:
                value = fn.get_flower_boss_campaign_remain_time()
                self.__flower_boss_campaign_remain_time = int(value)
            return self.__flower_boss_campaign_remain_time
        def __set__(self, value):
            assert self.__flower_boss_campaign_remain_time is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__flower_boss_campaign_remain_time = value
    cpdef clear_flower_boss_campaign_remain_time(self):
        self.__flower_boss_campaign_remain_time = None
        self.set_sync_dirty('flower_boss_campaign_remain_time')
    cdef public object __honor_power
    property honor_power:
        def __get__(self):
            if self.__honor_power is None:
                value = fn.get_honor_power(self.entityID)
                self.__honor_power = float(value)
            return self.__honor_power
        def __set__(self, value):
            assert self.__honor_power is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__honor_power = value
    cpdef clear_honor_power(self):
        self.__honor_power = None
    cdef public object __climb_tower_max_count
    property climb_tower_max_count:
        def __get__(self):
            if self.__climb_tower_max_count is None:
                value = fn.get_climb_tower_max_count(self.vip)
                self.__climb_tower_max_count = int(value)
            return self.__climb_tower_max_count
        def __set__(self, value):
            assert self.__climb_tower_max_count is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__climb_tower_max_count = value
    cpdef clear_climb_tower_max_count(self):
        self.__climb_tower_max_count = None
        self.set_dirty('climb_tower_max_count')
        self.set_sync_dirty('climb_tower_max_count')
    cdef public object __climb_tower_accredit_lineup
    property climb_tower_accredit_lineup:
        def __get__(self):
            if self.__climb_tower_accredit_lineup is None:
                value = fn.get_climb_tower_accredit_raw_lineup(self.entityID, self.lineups, self.climb_tower_accredit_cd)
                self.__climb_tower_accredit_lineup = value
            return self.__climb_tower_accredit_lineup
        def __set__(self, value):
            assert self.__climb_tower_accredit_lineup is None, 'can only set formula attribute when initialize'
            if isinstance(value, str):
                value = value.decode('utf-8')
            value = value
            self.__climb_tower_accredit_lineup = value
    cpdef clear_climb_tower_accredit_lineup(self):
        self.__climb_tower_accredit_lineup = None
        self.set_sync_dirty('climb_tower_accredit_lineup')
    property climb_tower_accredit_earnings:
        def __get__(self):
            value = fn.get_climb_tower_accredit_earnings(self.climb_tower_accredit_stash_time, self.climb_tower_accredit_cd, self.climb_tower_accredit_floor)
            return int(value)
    property climb_tower_accredit_acc_earnings:
        def __get__(self):
            value = self.climb_tower_accredit_stash_earnings + self.climb_tower_accredit_earnings
            return int(value)
    cdef public object __climb_tower_total_floor
    property climb_tower_total_floor:
        def __get__(self):
            if self.__climb_tower_total_floor is None:
                value = fn.get_climb_tower_total_floor()
                self.__climb_tower_total_floor = int(value)
            return self.__climb_tower_total_floor
        def __set__(self, value):
            assert self.__climb_tower_total_floor is None, 'can only set formula attribute when initialize'
            value = int(value)
            self.__climb_tower_total_floor = value
    cpdef clear_climb_tower_total_floor(self):
        self.__climb_tower_total_floor = None
        self.set_sync_dirty('climb_tower_total_floor')
    cdef public object __gems_power
    property gems_power:
        def __get__(self):
            if self.__gems_power is None:
                value = fn.get_gems_power(self.entityID, self.point, self.lineups)
                self.__gems_power = float(value)
            return self.__gems_power
        def __set__(self, value):
            assert self.__gems_power is None, 'can only set formula attribute when initialize'
            value = float(value)
            self.__gems_power = value
    cpdef clear_gems_power(self):
        self.__gems_power = None

    cpdef has_dirty(self):
        return bool(self.dirty_fields)

    cpdef set_dirty(self, name):
        self.dirty_fields.add(name)

    cpdef set get_dirty(self):
        return self.dirty_fields

    cpdef set pop_dirty(self):
        cdef set fs = self.dirty_fields
        self.dirty_fields = set()
        return fs

    cpdef is_dirty(self, name):
        return name in self.dirty_fields

    cpdef remove_dirty(self, fields):
        for f in fields:
            try:
                self.dirty_fields.remove(f)
            except KeyError:
                pass
    cpdef has_sync_dirty(self):
        return bool(self.sync_dirty_fields)

    cpdef set_sync_dirty(self, name):
        self.sync_dirty_fields.add(name)

    cpdef set get_sync_dirty(self):
        return self.sync_dirty_fields

    cpdef set pop_sync_dirty(self):
        cdef set fs = self.sync_dirty_fields
        self.sync_dirty_fields = set()
        return fs

    cpdef is_sync_dirty(self, name):
        return name in self.sync_dirty_fields

    cpdef remove_sync_dirty(self, fields):
        for f in fields:
            try:
                self.sync_dirty_fields.remove(f)
            except KeyError:
                pass

    cpdef list pop_dirty_values(self):
        cdef list result = []
        cdef dict fields = type(self).fields
        for name in self.pop_dirty():
            try:
                f = fields[name]
            except KeyError:
                continue
            value = getattr(self, name)
            if f.encoder is not None:
                value = f.encoder(value)
            result.append((name, value))
        return result

    cpdef list pop_sync_dirty_values(self):
        cdef dict fields = self.fields
        cdef list result = []
        cdef int now = 0
        for name in self.pop_sync_dirty():
            value = getattr(self, name)
            f = fields[name]
            if f.syncTimeout:
                if now == 0:
                    now = time()
                value = value - now
            elif f.encoder is not None:
                value = f.encoder(value)
            result.append((name, value))
        return result

    cycle = cycle

    @classmethod
    def getAttributeByID(cls, id):
        return cls.fields_ids_map[id]

    @classmethod
    def getAttributeIDByName(cls, name):
        return cls.fields[name].id

    @classmethod
    def expend_fields(cls, fields):
        result = set()
        for name in fields:
            f = cls.fields[name]
            if f.formula and not f.save:
                for ff in f.depend_set_save:
                    result.add(ff.name)
            else:
                result.add(name)
        return result
