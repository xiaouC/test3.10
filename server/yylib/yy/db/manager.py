# coding: utf-8
import logging
logger = logging.getLogger('db')

from time import time
import traceback
from gevent import queue, event, Greenlet, monkey

monkey.patch_socket()
# monkey patch socket for umysql
import socket
import umysql

SQLError = umysql.SQLError

class Query(object):
    def __init__(self, query, args=(), isprocedure=False, db='game', argnames=None):
        assert db, 'Unknown db tag'
        self.query = query
        self.args = args
        self.isprocedure = isprocedure
        self.dbtag = db
        self.argnames = argnames

    def __str__(self):
        return '[%s]%s %s(%s)'%(self.dbtag, self.isprocedure and 'procedure' or 'sql', self.query, self.args)

class Pool(object):
    def __init__(self, tag, manager, queue, extra):
        self.tag = tag
        self.manager = manager
        self.queue = queue
        self.extra = extra
        self.threads = []

    def get_count(self):
        return len(self.get_live_thread())

    def get_dead_thread(self):
        return [t for t in self.threads if not t.isactived()]

    def get_live_thread(self):
        return [t for t in self.threads if t.isactived()]

    def set_count(self, v):
        if v != self.count:
            if v < self.count:
                #stop
                for t in self.get_live_thread()[:self.count-v]:
                    self.stop_thread(t)
            else:
                #start
                for i in range(v-self.count):
                    self.start_thread()

    count = property(get_count, set_count)

    def start_thread(self):
        #print self.count
        thread = Thread(self, self.tag, self.manager, self.queue, self.count, self.extra)
        thread.run()
        self.threads.append(thread)
        return thread

    def stop_thread(self, thread):
        thread.stop = True

    def restart_thread(self, thread):
        thread.stop = False
        thread.run()

    def release_thread(self, thread):
        self.threads.remove(thread)

class Thread(object):
    def __init__(self, pool, tag, manager, queue, key, extra):
        self.pool = pool
        self.tag = tag
        self.manager = manager
        self.queue = queue
        self.extra = extra
        self.key = key
        self.runner = None
        self.stop = False

    def isactived(self):
        if self.runner is not None:
            return self.runner.started and not self.stop
        return False

    def handler(self):
        conn = umysql.Connection()
        #umysql_args = host, port, user, passwd, name, autocommit
        umysql_args = self.extra.get('host', '127.0.0.1'), self.extra.get('port', 3306),\
                      self.extra.get('user', 'poem'), self.extra.get('passwd', 'poem'),\
                      self.extra.get('name', None), self.extra.get('autocommit', True)
        conn.connect(*umysql_args)
        while True:
            if self.stop:
                break
            query, callback, err_callback = self.queue.get()
            #print '[*] current thread is [%d]'%self.key
            try:
                if query==None:
                    rs = None
                    if callback:
                        callback(rs)
                    break

                if query.isprocedure:
                    qry = None

                    if len(query.args):
                        qry = 'call %s(@returnvalue, @returndesc, %s)' % (query.query, ','.join(['%s']*len(query.args)))
                    else:
                        qry = 'call %s(@returnvalue, @returndesc)'% (query.query)
                    rs = conn.query(qry, query.args)
                    # fetch multiple result set
                    sets = [rs]
                    while True:
                        ds = conn.nextset()
                        if ds==None or isinstance(ds, tuple):
                            break
                        sets.append(ds)

                    rs1 = conn.query('select @returnvalue, @returndesc')
                    if rs1.rows[0][0]!=0:
                        #logger.error('return value error %s' % rs1.rows)
                        pass
                    rs = len(sets)>1 and sets or rs
                else:
                    rs = conn.query(query.query, query.args)

            except RuntimeError as e:
                logger.error('reconnect database for runtime error %s', e)
                self.queue.put((query, callback, err_callback))
                conn.close()
                conn.connect(*umysql_args)
            except (socket.error, IOError) as e:
                # io error
                logger.error('reconnect database for runtime error %s', e)
                self.queue.put((query, callback, err_callback))
                conn.close()
                conn.connect(*umysql_args)
            except Exception as e:
                logger.error('execute query exception %s %s' % (query, e))
                if err_callback:
                    err_callback(e)
                else:
                    logger.error(traceback.format_exc())
            else:
                if callback:
                    callback(rs)
        conn.close()

    def on_thread_dead(self, runner):
        #print 'thread dead'
        self.pool.release_thread(self)

    def run(self):
        self.runner = Greenlet.spawn(self.handler)
        self.runner.link(self.on_thread_dead)

class Manager(object):
    def __init__(self, config, start=True):
        self.config = dict(config)
        self.workers = {}
        if start:
            self.start_all()

    def ensure_worker(self, tag):
        if tag not in self.workers:
            logger.info('starting db worker %s', tag)
            q = queue.Queue()
            cfg = self.config[tag]
            client = cfg.pop('client', 'mysql')
            pool_size = cfg.get('pool_size', 1)
            pool = Pool(tag, self, q, self.config[tag])
            if client=='mysql':
                for i in range(pool_size):
                    thread = pool.start_thread()
                #thread.link(lambda: self.on_worker_dead(tag))
                self.workers[tag] = (q, pool)
            else:
                raise NotImplementedError
        return self.workers[tag]

    def on_worker_dead(self, tag):
        logger.info('db worker dead %s', tag)
        del manager.workers[tag]

    def start_all(self):
        for tag in dict(self.config):
            if isinstance(self.config[tag], (list, tuple, set)):
                config = self.config.pop(tag)
                for each in config:
                    self.config[each['name']] = each
        for tag in self.config:
            self.ensure_worker(tag)

    def async_execute(self, query, callback=None, err_callback=None):
        q, _ = self.ensure_worker(query.dbtag)
        q.put((query, callback, err_callback))
        logger.debug('[async][%s]%s %s'%(query.dbtag, query.query, tuple(query.args)))

    def execute(self, query):
        q, _ = self.ensure_worker(query.dbtag)
        aresult = event.AsyncResult()
        begin = time()
        q.put((query, aresult.set, aresult.set_exception))
        r = aresult.get()
        cost = time() - begin
        logger.debug('[%f][%s]%s %s'%(cost, query.dbtag, query.query, tuple(query.args)))
        return r

    def stop_one(self, tag):
        try:
            q, _ = self.workers[tag]
        except KeyError:
            return
        aresult = event.AsyncResult()
        q.put((None, aresult.set, aresult.set_exception))
        aresult.get()

    def wait_stop(self):
        for dbtag in self.workers:
            self.stop_one(dbtag)

g_dbmanager = None
def start_dbmanager(config=None):
    global g_dbmanager
    if g_dbmanager!=None:
        return

    if config==None:
        import settings
        config = settings.DATABASES

    g_dbmanager = Manager(config)

def execute(query):
    return g_dbmanager.execute(query)

def async_execute(query, callback=None, err_callback=None):
    return g_dbmanager.async_execute(query, callback)

def executeSQL(sql, args, **kwargs):
    return execute(Query(sql, args, **kwargs))

def async_executeSQL(sql, args, **kwargs):
    return async_execute(Query(sql, args, **kwargs))

if __name__ == '__main__':
    from common.utils import load_settings
    load_settings()
    start_dbmanager()
    rs = execute(Query('select * from user', db='user'))
    for r in rs.rows:
        print r[1], r[2]
