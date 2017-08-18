from yy.db.redismanager import create_pool
from yy.entity.identity import RedisIdentityGenerator
import settings

g_identity = RedisIdentityGenerator(pool=settings.REDISES['identity'])

def test_redis_identity_generator():
    g = g_identity
    next_id = g.view()

    new_id = g.gen()
    assert new_id >= next_id
    next_id = new_id + 1

    new_id = g.gen()
    assert new_id >= next_id
    next_id = new_id + 1

    new_id = g.gen()
    assert new_id >= next_id
    next_id = new_id + 1
