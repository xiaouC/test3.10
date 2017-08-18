# coding:utf-8
import settings
from UserString import UserString
from string import Template


class IndexString(UserString):
    SERVER_INFO = {
        "regionID": settings.REGION["ID"],
        "sessionID": settings.SESSION["ID"],
    }

    def render(self, **info):
        if not info:
            info = self.SERVER_INFO
        return Template(self.data).substitute(**info)

# 前缀RANK对应ordered set，INDEX对应hash map，SET对应set，INT为string，LIST为LIST
# player
RANK_TOTALBP = IndexString('rank_p_totalbp{$regionID}')
RANK_LEVEL = IndexString('rank_p_level{$regionID}')
RANK_POWER = IndexString('rank_p_power{$regionID}')
RANK_MAXPOWER = IndexString('rank_p_maxpower{$regionID}')
RANK_SWAPRANK = IndexString('rank_p_swaprank{$regionID}')
RANK_DAILYRANK = IndexString('rank_p_dailyrank{$regionID}')
INT_SWAPRANKFLAG = IndexString('SWAPRANKFLAG{$regionID}')
INDEX_NAME = IndexString('index_p_name{$regionID}')
SET_FRIEND_RECOMMEND = IndexString('index_p_friendrecommend{$regionID}')
SET_FRIEND_RECOMMEND_ONLINE = IndexString(
    'index_p_friendrecommendonline{$regionID}')
SET_DUPLICATE_NAMES = IndexString('index_p_duplicate_names{$regionID}')
# faction
RANK_FACTION_LEVEL = IndexString('rank_f_level{$regionID}')
RANK_FACTION_SKILL = IndexString('rank_f_skill{$regionID}')
INDEX_FACTION_NAME = IndexString('index_f_name{$regionID}')
SET_FACTION_RECOMMEND = IndexString('index_f_recommended{$regionID}')
# group
SET_GROUP_RECOMMEND = IndexString('index_g_recommended{$regionID}')
INDEX_GROUP_NAME = IndexString('index_g_name{$regionID}')
# campaign
INT_FUND_BOUGHT_COUNT = IndexString("FUND_BOUGHT_COUNT{$sessionID}{$regionID}")
# friend
LIST_FRIEND_FB_BY_TIME = IndexString(
    "friendfb_by_time{$regionID}_{$sessionID}")
INDEX_BOSS_REWARD = IndexString('BOSS_REWARD{$sessionID}{$regionID}')
RANK_AMBITION = IndexString('RANKING_AMBITION{$regionID}')
RANK_PETCOUNT = IndexString('RANKING_PETCOUNT{$regionID}')
RANK_EQUIPMAXPOWER = IndexString('RANKING_EQUIPMAXPOWER{$regionID}')
RANK_PETMAXPOWER = IndexString('RANKING_PETMAXPOWER{$regionID}')
RANK_STAR = IndexString('RANKING_STAR{$regionID}')
RANK_ADVANCED = IndexString('RANKING_ADVANCED{$regionID}')
RANK_PROGRESS = IndexString('RANKING_PROGRESS{$regionID}')
RANK_BOSSKILL = IndexString('RANKING_BOSSKILL{$regionID}')
RANK_ROBMINE1 = IndexString('RANKING_ROBMINE1{$regionID}')
RANK_ROBMINE2 = IndexString('RANKING_ROBMINE2{$regionID}')
RANK_CLIMB_TOWER = IndexString('RANKING_CLIMB_TOWER{$regionID}')
