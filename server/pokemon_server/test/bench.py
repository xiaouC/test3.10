from utils import ensure_login, auto_enter, ExpectException, ensure_http_login, auto_http_enter, rand_sleep
from gevent import sleep

device_id_tpl = 'test_robot_%d'

def create_accounts(names):
    for name in names:
        ensure_http_login(name)

def work(name):
    out = open('bench/%s.txt'%name, 'w')
    return subprocess.call(['python', '-m', 'test.task', name], stdout=out, shell=False)

def processes(names):
    import multiprocessing
    import subprocess
    #create_accounts(names)
    cmds = ['python -m test.task %s'%name for name in names]
    pool = multiprocessing.Pool(processes=count)
    pool.map(work, names)

def one(name, fn):
    sock = auto_http_enter(name)
    try:
        fn(sock)
    except ExpectException as e:
        print 'error message:', e
    finally:
        sock.close()

def threads(names, step=None):
    from gevent import spawn, joinall
    if step == 'fb':
        from yzzh.fb import main
    elif step == 'rank':
        from yzzh.rank import main
    elif step == 'create':
        from yzzh.faction import create as main
    elif step == 'apply':
        from yzzh.faction import apply as main
    else:
        from empty import empty_main as main
    ths = [spawn(one, name, main) for name in names]
    joinall(ths)

if __name__ == '__main__':
    count = 300
    step = None
    import sys
    if sys.argv[1:]:
        count = int(sys.argv[1])
        step = sys.argv[2]
    names = [device_id_tpl%i for i in range(count, count + 5000)]
    #create_accounts(names)
    threads(names, step)
