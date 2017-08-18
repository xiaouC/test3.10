#coding:utf-8
from test.utils import *
from test.bench import device_id_tpl, create_accounts
from test.yzzh.faction import *
from gevent import spawn, joinall

def main(count):
    leader = device_id_tpl % 0
    create_accounts([leader])
    sock = auto_enter(leader)
    create(sock)
    names = [device_id_tpl % i for i in range(1, count)]
    create_accounts(names)
    ths = [spawn(lambda n,f:f(1, auto_enter(n)), name, apply_faction) for name in names]
    joinall(ths)

if __name__ == '__main__':
    count = 300
    import sys
    if sys.argv[1:]:
        count = int(sys.argv[1])
    main(count)
