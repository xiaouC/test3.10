import random
from nose.plugins.attrib import attr
from yy.utils import iter_bitmap, gen_bitmap

def validate_bm(entityIDs):
    s1 = set(iter_bitmap(gen_bitmap(entityIDs)))
    s2 = set(entityIDs)
    assert s1 == s2

@attr('slow')
def test_bitmap():
    l = range(1000000)
    for i in range(100):
        validate_bm(random.sample(l, 1000))
        validate_bm(random.sample(l, 1000))
