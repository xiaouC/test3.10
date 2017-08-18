# coding: utf-8
import time
from yy.db.redisscripts import g_scripts
from yy.entity.storage.redis import make_key
from yy.utils import group_list_by_two


def safe_int(v):
    return int(float(v))


class NaturalRanking(object):
    '自然排序，排序索引从1开始，默认降序排列，sorted set'
    def __init__(self, key, pool, default=0, desc=True):
        '''
        name: 对应积分属性的名字
        desc: 是否降序排列
        '''
        self.key = key
        self.pool = pool
        self.default = default
        self.desc = desc
        self._range_cmd = self.desc and 'ZREVRANGE' or 'ZRANGE'
        self._rank_cmd = self.desc and 'ZREVRANK' or 'ZRANK'
        self._range_by_score_cmd = self.desc and 'ZREVRANGEBYSCORE' or 'ZRANGEBYSCORE'

    @classmethod
    def init_entity_base(cls, entity_class, name, desc=True, pool=None, key=None):
        key = key or 'rank_%s_%s' % (entity_class.store_tag, name)
        field = entity_class.fields[name]
        default = field.default
        pool = pool or entity_class.pool

        return cls(key, pool, default, desc)

    @classmethod
    def init_entity(cls, entity_class, name, desc=True, pool=None, key=None):
        self = cls.init_entity_base(entity_class, name, desc, pool, key)

        self.sync_player = self.player_syncer(name)
        entity_class.listen_on_load(self.sync_player)
        entity_class.listen_on_create(self.sync_player)

        return self

    @classmethod
    def init_entity_reverse(cls, entity_class, name, desc=True, pool=None, key=None):
        assert entity_class.fields[name].event, 'attribute need to be event'
        self = cls.init_entity_base(entity_class, name, desc, pool, key)

        self.sync_player_reverse = self.player_syncer_reverse(name)
        entity_class.listen_on_load(self.sync_player_reverse)
        entity_class.listen_on_create(self.sync_player_reverse)
        getattr(entity_class, 'listen_'+name)(self.sync_player_reverse)

        return self

    def update_score(self, entityID, value):
        return self.pool.execute('ZADD', self.key, value, entityID)

    def incr_score(self, entityID, value):
        with self.pool.ctx() as conn:
            if conn.execute('ZSCORE', self.key, entityID) == None:
                value += self.default
                conn.execute('ZADD', self.key, value, entityID)
                return value
            else:
                return conn.execute('ZINCRBY', self.key, value, entityID)

    def player_syncer(self, name):
        private_name = '__'+name
        def sync_player(p):
            setattr(p, private_name, self.get_score(p.entityID))
            getattr(p, 'touch_'+name)()
        return sync_player

    def player_syncer_reverse(self, name):
        def sync_player(p, value=None):
            self.update_score(p.entityID, value if value is not None else getattr(p, name))
        return sync_player

    def get_by_rank(self, rank):
        try:
            return self.get_by_range(rank, rank)[0]
        except IndexError:
            return

    def get_by_range(self, begin, end):
        if begin > 0:
            begin -= 1
        if end > 0:
            end -= 1
        return map(lambda rsp:safe_int(rsp) if rsp else 0, self.pool.execute(self._range_cmd, self.key, begin, end))

    def get_range_by_score(self, begin, end, offset=None, count=None, withscores=False):
        cmd = [self._range_by_score_cmd, self.key]
        cmd.extend([begin, end][::(-1 if self.desc else None)])
        if withscores:
            cmd.append('WITHSCORES')
        if offset != None or count != None:
            cmd.extend(['LIMIT', offset or 0, count or -1])
        return map(lambda rsp:safe_int(rsp) if rsp else 0, self.pool.execute(*cmd))

    def get_by_ranks(self, ranks):
        cmds = ((self._range_cmd, self.key, rank-1, rank-1) for rank in ranks)
        return map(lambda rsp:safe_int(rsp[0]) if rsp else 0, self.pool.execute_pipeline(*cmds))

    def get_rank(self, entityID):
        rsp = self.pool.execute(self._rank_cmd, self.key, entityID)
        if rsp is not None:
            return int(rsp) + 1
        else:
            return 0

    def del_key(self, entityID):
        return self.pool.execute('ZREM', self.key, entityID)

    def get_ranks(self, entityIDs):
        cmds = [(self._rank_cmd, self.key, entityID) for entityID in entityIDs]
        return map(lambda rsp: int(rsp)+1 if rsp is not None else 0, self.pool.execute_pipeline(*cmds))

    def get_score(self, entityID):
        return safe_int(self.pool.execute('ZSCORE', self.key, entityID) or self.default)

    def get_scores(self, entityIDs):
        cmds = [('ZSCORE', self.key, entityID) for entityID in entityIDs]
        return [safe_int(rsp) if rsp is not None else self.default for rsp in self.pool.execute_pipeline(*cmds)]

    def count(self):
        return int(self.pool.execute('ZCARD', self.key))

    def get_by_score_range(self, min, max, desc=False, limit=None):
        if desc:
            cmd = ('ZREVRANGEBYSCORE', self.key, max, min, 'withscores')
            rsps = self.pool.execute('ZREVRANGEBYSCORE', self.key, max, min, 'withscores')
        else:
            cmd = ('ZRANGEBYSCORE', self.key, min, max, 'withscores')

        if limit is not None:
            cmd += ('limit', 0, limit)

        rsps = self.pool.execute(*cmd)
        return map(lambda (a,b): (safe_int(a), safe_int(b)), group_list_by_two(rsps))

    def clear_raw(self):
        '危险！ 清理排行榜，只清数据库，不处理在线玩家内存数据'
        self.pool.execute('DEL', self.key)

class NaturalRankingWithJoinOrder(NaturalRanking):
    '带加入时间的自然排序'
    def __init__(self, key, pool, default=0, desc=True, precision=10):
        super(NaturalRankingWithJoinOrder, self).__init__(key, pool, default, desc)
        self.precision = precision
        self.pow_precision = 10**precision

    def to_score(self, v, t):
        return '%d.%0*d'%(v, self.precision, t)

    def from_score_and_index(self, v):
        score = int(v)
        index = int((v-score) * self.pow_precision)
        return score, index

    def from_score(self, v):
        return int(v)

    def get_secondary_score(self):
        t = int(time.time())
        return self.pow_precision - t % self.pow_precision - 1

    def update_score(self, entityID, value):
        return self.pool.execute('ZADD',
                self.key,
                self.to_score(value, self.get_secondary_score()),
                entityID)

    def incr_score(self, entityID, value):
        with self.pool.ctx() as conn:
            rsp = conn.execute('ZSCORE', self.key, entityID)
            if rsp == None:
                value += self.default
            else:
                value += self.from_score(float(rsp))
            score = self.to_score(value, self.get_secondary_score())
            conn.execute('ZADD', self.key, score, entityID)
            return value

    def get_score(self, entityID):
        return self.from_score(float(self.pool.execute('ZSCORE', self.key, entityID) or self.default))

    def get_scores(self, entityIDs):
        cmds = [('ZSCORE', self.key, entityID) for entityID in entityIDs]
        return [self.from_score(float(rsp)) if rsp is not None else self.default for rsp in self.pool.execute_pipeline(*cmds)]

    def get_score_and_index(self, entityID):
        return self.from_score_and_index(float(self.pool.execute('ZSCORE', self.key, entityID) or self.default))

class SwapRanking(object):
    '竞技场基本操作'
    def __init__(self, entity_class, name, register_on_create=True, pool=None, key=None):
        self.entity_class = entity_class
        self.key = key or 'challenge_%s_%s' % (entity_class.store_tag, name)
        self.name = name

        if register_on_create:
            entity_class.listen_on_load(self.sync_player)
            entity_class.listen_on_create(self.register)

        self.pool = pool or entity_class.pool

    def get_rank(self, entityID):
        '获取玩家的排名'
        rsp = self.pool.execute('ZRANK', self.key, entityID)
        if rsp is not None:
            return int(rsp) + 1
        else:
            return 0

    def get_ranks(self, entityIDs):
        cmds = [('ZRANK', self.key, entityID) for entityID in entityIDs]
        return map(lambda o: int(o)+1 if o is not None else 0, self.pool.execute_pipeline(*cmds))

    def get_by_rank(self, rank):
        '根据排名取玩家ID'
        try:
            return int(self.pool.execute('ZRANGE', self.key, rank-1, rank-1)[0])
        except IndexError:
            return 0

    def get_by_ranks(self, ranks):
        '根据排名取玩家ID'
        cmds = (('ZRANGE', self.key, rank-1, rank-1) for rank in ranks)
        return map(lambda rsp:int(rsp[0]) if rsp else 0, self.pool.execute_pipeline(*cmds))

    def get_by_range(self, begin, end):
        # 1开始转换成0开始
        if begin > 0:
            begin = begin-1
        if end > 0:
            end = end-1
        return map(lambda rsp:safe_int(rsp) if rsp else 0, self.pool.execute('ZRANGE', self.key, begin, end))

    def count(self):
        return int(self.pool.execute('ZCARD', self.key))

    def view_next_rank(self):
        '查看下个排名'
        return self.count() + 1

    def register_raw(self, entityID):
        '注册新人'
        return g_scripts['challenge_register']((self.key,), (entityID,), pool=self.pool)

    def register(self, p):
        assert isinstance(p, self.entity_class)
        if isinstance(p, int):
            return self.register_raw(p)
        else:
            setattr(p, self.name, self.register_raw(p.entityID))

    def swap_raw(self, entityID1, entityID2):
        '''
        交换排名
        '''
        v1, v2 = g_scripts['challenge_swap']((self.key,), (entityID1,entityID2), pool=self.pool)
        return int(v1), int(v2)

    def swap(self, p1, p2):
        if isinstance(p1, int):
            e1 = p1
        else:
            e1 = p1.entityID

        if isinstance(p2, (int, long)):
            e2 = p2
        else:
            e2 = p2.entityID

        r1, r2 = self.swap_raw(e1, e2)

        if not isinstance(p1, (int, long)):
            setattr(p1, self.name, r1)
        if not isinstance(p2, (int, long)):
            setattr(p2, self.name, r2)

        return r1, r2

    def validate(self, entityID):
        return self.get_by_rank(self.get_rank(entityID)) == entityID

    def clear_raw(self):
        '清理排行榜，只清数据库，不处理在线玩家内存数据'
        self.pool.execute('DEL', self.key, 0, -1)

    def sync_player(self, p):
        setattr(p, self.name, self.get_rank(p.entityID))

    def remove_member(self, m):
        return self.pool.execute('ZREM', self.key, m)

    def raw_update(self, entityID, value):
        return self.pool.execute('ZADD', self.key, value, entityID)
