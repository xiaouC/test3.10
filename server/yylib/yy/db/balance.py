#coding:utf-8
import logging
logger = logging.getLogger('db')

dbs = {}

def incr_loads(db):
    dbs[db] += 1

def select_db():
    db = ''
    loads = None
    for k, v in dbs.items():
        if loads is not None:
            if v < loads:
                db = k
                loads = v
        else:
            db = k
            loads = v
    incr_loads(db)
    logger.debug('select db %s', db)
    return db

def reload_db_loads():
    global dbs
    dbs = {}
    import settings
    configs = settings.DATABASES['game']
    if isinstance(configs, (list, tuple, set)):
        for config in configs:
                dbs[config['name']] = 0
    else:
        dbs['game'] = 0
    from .redismanager import execute
    from .utils import compress_hgetall
    rs = execute('HGETALL', 'DatabaseStat')
    rs = compress_hgetall(rs)
    for dbtag, count in rs.items():
        if dbtag and dbtag in dbs:
            dbs[dbtag] = int(count)
