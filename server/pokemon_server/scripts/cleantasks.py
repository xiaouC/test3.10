#coding:utf-8

from yy.utils import load_settings
load_settings()
import settings

def main(key):
    pool = settings.REDISES['entity']
    if not key:
        keys = pool.execute('keys', "p{*}")
    else:
        keys = [key]
    cmds = []
    for k in keys:
        key = k.lstrip('p{').rstrip('}')
        for f in ('taskrewards', 
                  'task_max_patch_sign_up_count', 
                  'task_used_patch_sign_up_count', 
                  'task_last_sign_up_time',
                  'task_is_calc_sign_up',
                  'task_sp_daily_receiveds',
                  'monthly_card_30',
                  ):
            cmds.append(['hdel', 'p{%s}'%key, f])
        cmds.append(['del', 'tasks_p{%s}'%key])
        print cmds
    pool.execute_pipeline(*cmds)

if __name__ == '__main__':
    import sys
    try:
        main(sys.argv[1])
    except IndexError:
        main(None)
