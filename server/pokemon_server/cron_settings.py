# coding: utf-8
# import time
from yy.cron import reset_jobs, Job
from gm.app import *  # NOQA
from task.manager import check_daily_sp_state
from entity.manager import check_over_day, reset_on_zero
from pvp.loot import boardcast_loot_count
from pvp.rank import update_pvprankcount
# from group.manager import give_ranking_reward
from pvp.swap import g_swapManager
from pvp.uproar import cleanup_ranking

# from ranking.manager import do_ranking, RANKING_HOUR
# from ranking.manager import backup_rankings

reset_jobs([
    Job(reset_on_zero,                  minute='0', second='0', hour='0'),
    Job(check_over_day,                 minute='0', second='0', hour='0'),
    Job(lambda:clear_fb_count('all'),   minute='0', second='0', hour='0'),
    # Job(backup_rankings,                minute='0', second='0', hour='0'),
    Job(check_daily_sp_state,           hour='*/1'),
    Job(boardcast_loot_count,           minute="0", second="1", hour="12"),
    Job(boardcast_loot_count,           minute="0", second="1", hour="18"),
    Job(update_pvprankcount,            hour='*/1'),
    # Job(do_ranking,                     hour=str(RANKING_HOUR)),
    # Job(give_ranking_reward,            minute="50", hour="21"),
    Job(g_swapManager.backup,           hour="21"),  # 竞技场截榜
    Job(g_swapManager.give_reward,      hour="5"),   # 竞技场发奖
    Job(g_swapManager.cleanup,          hour="6"),   # 清理过期竞技场数据
    Job(cleanup_ranking,                hour="6"),   # 清理过期UPROAR数据
    # Job(give_maxpower_campaign_rewards, hour="0"),
])
