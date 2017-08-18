from yy.utils import get_random_string
from yy.utils import get_rand_string
import random

def get_random_string2(count):
    allowed_chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    l = []
    for i in range(count):
        l.append(random.choice(allowed_chars))
    return ''.join(l)

def test():
    for i in range(100):
        print get_random_string2(12)
        print get_rand_string(12)

test()

import timeit
timeit.main(['-s', 'from __main__ import get_rand_string',
            '-n', '10000', 'get_rand_string(12)'])
timeit.main(['-s', 'from __main__ import get_random_string',
            '-n', '10000', 'get_random_string(12)'])
timeit.main(['-s', 'from __main__ import get_random_string2',
            '-n', '10000', 'get_random_string2(12)'])
