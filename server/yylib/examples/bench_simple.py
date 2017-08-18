import pyximport; pyximport.install()

from yy.entity import create_class, define, init_fields
from tests.entity import player_fields, PlayerBase
from tests.c_player import c_PlayerBase

class RawPlayer(object):
    def __init__(self):
        self.formula3 = 0

class Player(PlayerBase):
    pass

class CPlayer(c_PlayerBase):
    pass

rp = RawPlayer()
p = Player()
cp = CPlayer()

def set_and_get(p):
    #p.userID = 1
    #return p.userID
    return p.formula3

if __name__ == '__main__':
    import timeit, cProfile
    timeit.main(['-s', 'from __main__ import set_and_get, rp',
                '-n', '10000', 'set_and_get(rp)'])
    timeit.main(['-s', 'from __main__ import set_and_get, p',
                '-n', '10000', 'set_and_get(p)'])
    timeit.main(['-s', 'from __main__ import set_and_get, cp',
                '-n', '10000', 'set_and_get(cp)'])

    cProfile.run('for i in xrange(10000): set_and_get(cp)',
                 sort='time')
    cProfile.run('for i in xrange(10000): set_and_get(p)',
                 sort='time')
