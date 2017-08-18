# coding: utf-8
import pyximport; pyximport.install()

import json
import time
import datetime
from nose.tools import raises, assert_raises
from nose.plugins.attrib import attr
from time import sleep

from yy.entity.storage import EntityStoreMixin
from yy.entity.base import EntityExistsException
from yy.ranking import NaturalRanking, SwapRanking, NaturalRankingWithJoinOrder
from yy.entity import UniqueIndexing, DuplicateIndexException, BitmapIndexing, SortedIndexing
from yy.entity.formulas import register_formula

import settings

from c_player import c_PlayerBase as PlayerBase
from tests.test_identity_generators import g_identity

class Player(PlayerBase, EntityStoreMixin):
    pool = settings.REDISES['default']

test_cluster_pool = settings.REDISES['cluster']

Player.set_identity_generator(g_identity)

natural_ranking = NaturalRanking.init_entity(Player, 'natural_score')
natural_ranking2 = NaturalRankingWithJoinOrder.init_entity(Player, 'natural_score2', 'join_time')

swap_ranking = SwapRanking(Player, 'rank')
swap_ranking2 = SwapRanking(Player, 'rank2', register_on_create=False, pool=test_cluster_pool)
player_name_index = UniqueIndexing('idx_p_name', pool=settings.REDISES['player_name_index'])
worldid_index = BitmapIndexing('idx_p_worldID', pool=Player.pool)
createtime_sorted_index = SortedIndexing('index_p_createtime', pool=Player.pool)

@register_formula
def get_challenge_rank(entityID):
    return natural_ranking.get_rank(entityID)

@register_formula
def get_challenge_rank2(entityID):
    return natural_ranking2.get_rank(entityID)

def on_formula3_changed(p, _):
    p.depend_on_formula3 = p.formula3 + 1
Player.listen_formula3(on_formula3_changed)

def test_reflection():
    p = Player()
    for f in ['plain', 'persistent', 'formula1', 'sp', 'sp_update_time']:
        assert p.getAttributeByID(p.getAttributeIDByName(f)).name == f

def test_persistent():
    p = Player()
    p.persistent = 1
    assert p.is_dirty('persistent')
    assert p.is_sync_dirty('persistent')
    p.pop_dirty()
    p.pop_sync_dirty()
    p.sp += 1
    assert p.is_dirty('sp')

def test_formula():
    p = Player()
    p.plain = 1
    assert p.formula1 == 2
    assert p.formula2 == 3
    assert p.formula3 == 5
    p.plain = 11
    assert p.formula1 == 12
    assert p.formula2 == 13
    assert p.formula3 == 15

    # clear will add dirty
    p.clear_formula1()
    assert p.is_sync_dirty('formula1')
    p.clear_formula2()
    assert p.is_dirty('formula2')

def test_persist_formula():
    p = Player.create()
    p.plain = 1
    p.save()
    p = Player.simple_load(p.entityID, ['formula2'])
    assert p.formula2 == 3
    assert p.formula3 == 5
    assert not p.is_dirty('formula2')
    assert not p.is_sync_dirty('formula2')

def test_default():
    p = Player()
    assert p.sp_max == 10

def test_cycle():
    p = Player()
    p.cycle()
    p.sp += 1
    assert p.sp == 1
    p.left_count -= 1
    assert p.left_count == 9

    p.sp_update_time = 100.0
    p.left_count_update_time = 100.0
    p.cycle()
    assert p.sp == p.sp_max
    assert p.left_count == 10

    # cycle 不能减少属性
    p.sp = 40
    p.cycle()
    assert p.sp == 40

def test_auto_convert():
    p = Player()
    p.sp = '5'
    assert p.sp == 5
    p.sp = 5.4
    assert p.sp == 5

    p.sp_max = 5.4
    assert p.sp_max == 5

    p.float_value = '5.5'
    assert p.float_value == 5.5

def test_store():
    p = Player.create()
    p.sp = 5
    p.save()
    p2 = Player.load(p.entityID)
    assert p2.sp == p.sp, '%s != %s' % (p2.sp, p.sp)

def test_touch():
    p = Player()
    p.touch_persistent()
    assert p.is_dirty('persistent')
    assert p.is_sync_dirty('persistent')

def test_list():
    p = Player()
    assert len(p.list_value) == 0
    p.list_value.append(1)
    assert p.is_dirty('list_value')
    assert p.is_sync_dirty('list_value')
    p.pop_dirty()
    p.list_value.insert(0, 1)
    assert p.is_dirty('list_value')
    assert p.is_sync_dirty('list_value')
    p.pop_dirty()
    p.list_value.remove(1)
    assert p.is_dirty('list_value')
    assert p.is_sync_dirty('list_value')
    p.pop_dirty()

    # test reset container value
    p.list_value = [4,5,6]
    p.pop_dirty()
    p.list_value.append(7)
    assert p.is_dirty('list_value')

def test_dict():
    p = Player()
    assert len(p.dict_value) == 0
    p.dict_value['a'] = 1
    p.dict_value['b'] = 1
    assert p.is_dirty('dict_value')
    assert p.is_sync_dirty('dict_value')
    p.pop_dirty()
    p.dict_value.pop('a')
    assert p.is_dirty('dict_value')
    assert p.is_sync_dirty('dict_value')
    p.pop_dirty()
    del p.dict_value['b']
    assert p.is_dirty('dict_value')
    assert p.is_sync_dirty('dict_value')
    p.pop_dirty()

def test_set():
    p = Player()
    assert len(p.set_value) == 0
    p.set_value.add(1)
    assert p.is_dirty('set_value')
    assert p.is_sync_dirty('set_value')
    p.pop_dirty()
    p.set_value.remove(1)
    assert p.is_dirty('set_value')
    assert p.is_sync_dirty('set_value')
    p.pop_dirty()

def test_string():
    p = Player()
    p.string_value = u'123'
    p.string_value = 'abc'

def test_encoder_decoder():
    p = Player.create()
    p.list_value.append(1)
    p.save()
    p = Player.load(p.entityID)
    assert p.list_value[-1] == 1

def test_sync_timeout():
    p = Player()
    now = int(time.time())
    p.some_cd_value = now + 10
    assert dict(p.pop_sync_dirty_values())['some_cd_value'] == 10

def test_constructor():
    p = Player(entityID=100)
    assert p.entityID == 100

def test_datetime():
    p = Player.create()
    now = datetime.datetime.now()
    p.datetime_value = now
    p.save()
    p = Player.load(p.entityID)
    # 精度损失，1秒以内
    assert (now - p.datetime_value).total_seconds() < 1

def test_reset_default_value():
    p = Player()
    p.cycle()
    p.list_value.append(1)
    p.list_value.append(2)
    p.list_value.append(3)
    p.list_value_ts = 100.0
    p.cycle()
    assert len(p.list_value) == 0, str(p.list_value)

def test_load_fields():
    p = Player.create()
    p.persistent = 1
    p.list_value.append(1)
    p.save()
    p = Player.simple_load(p.entityID, fields=['list_value'])
    assert p.list_value[0] == 1
    assert p.persistent == 0

@raises(EntityExistsException)
def test_create():
    p = Player.create()
    p.persistent = 1
    p.save()
    p = Player.create(entityID=p.entityID)

def test_natural_ranking():
    '排位赛积分风格的排行榜'
    natural_ranking.clear_raw()

    p1 = Player.create()
    assert p1.natural_score == 10
    p1.natural_score += 1
    natural_ranking.update_score(p1.entityID, p1.natural_score)
    assert p1.natural_score == 11, p1.natural_score
    p1.save()
    assert p1.natural_ranking == 1, p1.natural_ranking

    p2 = Player.create()
    natural_ranking.update_score(p2.entityID, natural_ranking.default)
    p2.natural_score = natural_ranking.incr_score(p2.entityID, 2)
    p2.save()
    assert p2.natural_ranking == 1
    p1.clear_natural_ranking()
    assert p1.natural_ranking == 2

    assert natural_ranking.get_by_rank(1) == p2.entityID
    assert tuple(natural_ranking.get_by_ranks([1,2])) == (p2.entityID, p1.entityID)
    assert tuple(natural_ranking.get_by_range(1,2)) == (p2.entityID, p1.entityID)
    assert tuple(natural_ranking.get_ranks([p1.entityID,p2.entityID])) == (2,1)
    assert natural_ranking.get_range_by_score('-inf', '+inf', count=1, withscores=True) == [p2.entityID, 12]

@attr('slow')
def test_natural_ranking_with_join_order():
    '带加入时间的排行榜'
    natural_ranking2.clear_raw()

    p1 = Player.create()
    p1.natural_score2 = natural_ranking2.incr_score(p1.entityID, 10)
    p1.save()

    sleep(1)

    p2 = Player.create()
    p2.natural_score2 = natural_ranking2.incr_score(p2.entityID, 10)
    p2.save()

    assert p1.natural_ranking2 == 1, p1.natural_ranking2
    assert p2.natural_ranking2 == 2, p2.natural_ranking2

    p2.natural_score2 = natural_ranking2.incr_score(p2.entityID, 10)

    p2.clear_natural_ranking2()
    p1.clear_natural_ranking2()
    assert p2.natural_ranking2 == 1, p2.natural_ranking2
    assert p1.natural_ranking2 == 2, p1.natural_ranking2

    p2.natural_score2 = natural_ranking2.incr_score(p2.entityID, 10)

    p2.clear_natural_ranking2()
    p1.clear_natural_ranking2()
    assert p2.natural_ranking2 == 1, p2.natural_ranking2
    assert p1.natural_ranking2 == 2, p1.natural_ranking2

@attr('slow')
def test_natural_ranking_with_join_order2():
    '带加入时间的排行榜'
    natural_ranking2.clear_raw()

    p1 = Player.create()
    p1.natural_score2 = natural_ranking2.incr_score(p1.entityID, 5)
    p1.save()

    sleep(1)

    p2 = Player.create()
    p2.natural_score2 = natural_ranking2.incr_score(p2.entityID, 10)
    p2.save()

    assert p1.natural_ranking2 == 2, p1.natural_ranking2
    assert p2.natural_ranking2 == 1, p2.natural_ranking2

    sleep(1)

    p1.natural_score2 = natural_ranking2.incr_score(p1.entityID, 5)

    p2.clear_natural_ranking2()
    p1.clear_natural_ranking2()
    assert p1.natural_ranking2 == 2, p1.natural_ranking2
    assert p2.natural_ranking2 == 1, p2.natural_ranking2

def test_swap_ranking():
    '争夺战(圣将竞技场)风格的排行榜'
    swap_ranking.clear_raw()
    swap_ranking2.clear_raw()

    p1 = Player.create()
    # 玩家创建时自动注册到竞技场
    assert p1.rank == 1 
    assert swap_ranking.validate(p1.entityID)

    p2 = Player.create()
    assert p2.rank == 2
    assert swap_ranking.validate(p2.entityID)

    assert swap_ranking.get_by_rank(1) == p1.entityID
    assert swap_ranking.get_by_rank(2) == p2.entityID

    # 交换排名
    swap_ranking.swap(p1, p2)
    assert p1.rank == 2
    assert p2.rank == 1

    assert swap_ranking.get_by_rank(2) == p1.entityID
    assert swap_ranking.get_by_rank(1) == p2.entityID

    assert tuple(swap_ranking.get_by_ranks([1,2])) == (p2.entityID, p1.entityID)
    assert tuple(swap_ranking.get_by_range(1,2)) == (p2.entityID, p1.entityID)
    assert tuple(swap_ranking.get_ranks([p1.entityID, p2.entityID])) == (2,1)

    p1.save()
    p2.save()

    # 重新加载，排名不变
    p1 = Player.load(entityID=p1.entityID)
    assert p1.rank == 2

    p2 = Player.load(entityID=p2.entityID)
    assert p2.rank == 1

    # rank2 设置了不自动注册到竞技场，比如需要某些条件满足才能进入竞技场
    assert p1.rank2 == 0
    swap_ranking2.register(p1)
    p1.rank2 == 1

    assert p2.rank2 == 0
    swap_ranking2.register(p2)
    p2.rank2 == 2

    eid = swap_ranking2.get_by_rank(2)
    assert swap_ranking2.get_by_rank(2) == p2.entityID, eid
    assert swap_ranking2.get_by_rank(1) == p1.entityID

    assert tuple(swap_ranking2.get_by_ranks([1,2])) == (p1.entityID, p2.entityID)
    assert tuple(swap_ranking2.get_by_ranks([1,2,3])) == (p1.entityID, p2.entityID, 0)
    assert tuple(swap_ranking2.get_by_range(1,3)) == (p1.entityID, p2.entityID)
    assert tuple(swap_ranking2.get_ranks([p1.entityID, p2.entityID])) == (1,2)

    assert tuple(swap_ranking2.get_ranks([p1.entityID, p2.entityID, -1])) == (1,2,0)

def test_formula_event():
    p = Player()
    p.plain = 1
    assert p.depend_on_formula3 == 6
    assert p.formula3 == 5, p.formula3

def test_sync_containers():
    p = Player()
    p.list_value.append(1)
    d = dict(p.pop_sync_dirty_values())
    assert json.loads(d['list_value'])[0] == 1

def test_stored_dict():
    p = Player.create()
    p.pack[1] = 1
    try:
        p.pack[2] += 1
    except KeyError:
        p.pack[2] = 1
    p.save()
    p = Player.load(p.entityID)
    assert p.pack[1] == 1
    assert p.pack[2] == 1

def test_stored_set():
    p = Player.create()
    p.rewards.add(1)
    p.rewards.add(2)
    p.save()
    p = Player.load(p.entityID)
    assert 1 in p.rewards
    assert 2 in p.rewards
    p.rewards.remove(1)
    p.save()
    p = Player.load(p.entityID)
    assert 2 in p.rewards
    assert 1 not in p.rewards

def test_expend_fields():
    fs1 = Player.expend_fields(['plain', 'persist_formula2'])
    assert set(fs1) == set(['persistent', 'plain'])
    fs2 = Player.expend_fields(['formula3'])
    assert set(fs2) == set(['formula2'])

    p = Player.create()
    p.persistent = 1
    p.plain = 1
    p.save()
    assert p.persist_formula2 == 3
    assert p.formula3 == 5
    assert p.formula2 == 3

    p = Player.simple_load(p.entityID, fs1)
    assert p.persist_formula2 == 3
    assert p.formula3 == 4

    p = Player.simple_load(p.entityID, fs2)
    assert p.formula3 == 5

def test_formula_return_type():
    p = Player()
    p.plain = 10
    assert type(p.integer_formula) == int

def test_stored_dict_encode():
    p = Player.create()
    p.fbs[1] = {'count':1}
    p.fbs.update({2:{'count':1}})
    p.save()
    p = Player.load(p.entityID)
    assert p.fbs[1]['count'] == 1
    assert p.fbs[2]['count'] == 1

def test_player_name_index():
    player_name_index.clear_raw()

    p = Player.create()
    p.name = 'test'
    player_name_index.register(p.entityID, p.name)
    assert player_name_index.exists('test')
    p.save()
    p1 = Player.load(player_name_index.get_pk('test'))
    assert p1.entityID == p.entityID, (p1.entityID, p.entityID)

    p2 = Player.create()
    p2.name = 'test'
    assert_raises(DuplicateIndexException, lambda:player_name_index.register(p2.entityID, 'test'))

    assert player_name_index.get_pk('test') == p.entityID

def test_bitmap_index():
    p = Player.create()
    p.worldID = 101
    worldid_index.register(p.entityID, p.worldID)
    p.save()
    assert worldid_index.check(p.entityID, p.worldID)

def test_entity_not_exists():
    p = Player.create()
    p.save()
    assert Player.get(p.entityID + 1) == None

def test_boolean_persistent():
    p = Player.create()
    p.bool_value = True
    p.save()
    p = Player.load(p.entityID)
    assert p.bool_value == True
    p.bool_value = False
    p.save()
    p = Player.load(p.entityID)
    assert p.bool_value == False

def test_sync_timestamp():
    p = Player.create()
    p.sp = 10
    p.cycle()
    assert p.is_dirty('sp_update_time')
    assert p.is_sync_dirty('sp_update_time')

def test_batch_attributes():
    p1 = Player.create()
    p1.persistent = 1
    p1.plain = 1
    p1.save()
    p2 = Player.create()
    p2.persistent = 2
    p2.plain = 2
    p2.save()

    fields = Player.expend_fields(['persistent', 'formula3'])
    l = Player.batch_load([p1.entityID, p2.entityID, p2.entityID+1], fields)
    assert l[0].persistent == p1.persistent
    assert l[0].formula3 == p1.formula3, (l[0].formula3, p1.formula3)
    assert l[1].persistent == p2.persistent
    assert l[1].formula3 == p2.formula3
    assert l[2] == None, l[2]

def test_sorted_index():
    p = Player.create()
    p.createtime = int(time.time())
    createtime_sorted_index.register(p.entityID, p.createtime)
    p2 = Player.create()
    p2.createtime = int(time.time()) + 86400
    createtime_sorted_index.register(p2.entityID, p2.createtime)
    assert createtime_sorted_index.get_by_range() == [p.entityID, p2.entityID]
    assert createtime_sorted_index.get_by_range(p.createtime, p2.createtime) == [p.entityID, p2.entityID]
    createtime_sorted_index.unregister(p2.entityID)
    assert createtime_sorted_index.get_by_range() == [p.entityID]
test_sorted_index.teardown = lambda : createtime_sorted_index.clear_raw()

def test_cycle_resume():
    p = Player.create()
    now = int(time.time())
    p.cycle(now=now)
    sp = p.fields['sp']
    assert p.sp_update_time == now + sp.resume    #sp_update_time is the next resume time
    cost = sp.default // 2
    print 'p.sp', p.sp, 'cost', cost
    p.sp -= cost #cost sp
    print 'p.sp', p.sp
    p.cycle(now=now + sp.resume)         #one cycle after
    print 'p.sp', p.sp
    print sp.default
    assert p.sp == sp.default - cost + 1 #cycle one unit

    #reset
    p2 = Player.create()
    now = int(time.time())
    p2.cycle(now=now)
    p2.sp -= cost
    rest = p2.sp
    p2.cycle(now=now + sp.resume // 2)    #half cycle after
    assert p2.sp == rest                  #no change

    #rest
    p3 = Player.create()
    now = int(time.time())
    p3.cycle(now=now)
    p3.sp -= cost
    p3.cycle(now=now + sp.resume * 2 + sp.resume // 2) #two and half cycles after
    assert p3.sp == sp.default - cost + 2 * 1
    assert p3.sp_update_time == now + sp.resume * 3             #next cycle time

    #rest
    p4 = Player.create()
    now = int(time.time())
    p4.cycle(now=now + sp.resume)
    assert p4.sp_update_time == now + sp.resume + sp.resume      #but change next resume time
    count = max(getattr(p4, sp.max) - p4.sp, 0) // 1 #恢复到max需要多少个周期
    p4.cycle(now=now+sp.resume * (count + 2)) #多加几个周期
    assert p4.sp == getattr(p4, sp.max) #can not over max

def test_cycle_reset():
    p = Player.create()
    now = int(time.time())
    from datetime import date as datedate, timedelta
    tomorrow = int(time.mktime((datedate.fromtimestamp(now) + timedelta(days=1)).timetuple()))
    p.cycle(now=now)
    used = p.fields['usedcount']
    assert p.usedcount == used.default
    assert p.usedcount_ts == tomorrow
    p.usedcount += 1
    assert p.usedcount != used.default
    p.cycle(now=tomorrow)
    assert p.usedcount == used.default
    p.usedcount += 1
    assert p.usedcount != used.default
    p.cycle(now=tomorrow + 86400 * 2)
    assert p.usedcount == used.default

def test_sorted_set_encoding():
    p = Player.create()
    p.fbrewards.add(('hashable', ))
    p.fbrewards.remove(('hashable', ))
    p.fbrewards.add(('hashable', ))
    p.save()
    p = Player.load(p.entityID)
    assert p.fbrewards == {('hashable', )}

def test_sorted_list_encoding():
    p = Player.create()
    print p.mylist
    p.mylist.append(['a'])
    p.mylist.append(['b'])
    p.mylist.extend((['c'], ['d']))
    assert p.mylist == [['a'], ['b'], ['c'], ['d']]
    assert p.mylist.lpop() == ['a']
    assert p.mylist.rpop() == ['d']
    p.mylist.remove(['b'])
    assert p.mylist == [['c']]
    p.mylist.appendleft(['d'])
    p.mylist.ltrim(1, -1)
    p.save()
    p = Player.load(p.entityID)
    assert p.mylist == [['c']]
    p.mylist.clear()
    p.save()
    assert p.mylist == []
    p = Player.load(p.entityID)
    assert p.mylist == [], "{}".format(p.mylist)
    p.mylist.appendleft(['d'])
    assert p.mylist == [['d']]

