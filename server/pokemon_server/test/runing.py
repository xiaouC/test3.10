from utils import *

device_id_tpl = 'test_robot_%d'

def one(name):
    rand_sleep(10,10)
    from move import move1
    sock = auto_enter(name)
    expect_me()
    move1(sock)

if __name__ == '__main__':
    threads = [spawn(one, device_id_tpl%i) for i in range(20)]
    joinall(threads)
