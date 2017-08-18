def diff_snapshot(st1, st2):
    diff = {}
    keys = set(st1.keys())
    for k in st2:
        keys.add(k)
    for k in keys:
        s1 = st1.get(k, set())
        s2 = st2.get(k, set())
        df = s2.difference(s1)
        if df:
            diff[k] = df
    return diff

def print_snapshot(d):
    for k, v in sorted(d.items(), key=lambda (a,b):b, reverse=True):
        print k, '\t', len(v)
        for e in v:
            print '\tid:', e

def gc_snapshot():
    import gc
    from collections import defaultdict
    gc.collect()
    objs = gc.get_objects()
    stats = defaultdict(set)
    for o in objs:
        if o in stats.values():
            continue
        stats[str(type(o))].add(id(o))
    return stats

def take_snapshot():
    import __main__
    stats = gc_snapshot()
    if getattr(__main__, '__last_stats', None):
        print_snapshot(diff_snapshot(__main__.__last_stats, stats))
        clean_snapshot()
    __main__.__last_stats = stats

def clean_snapshot():
    import gc
    import __main__
    del __main__.__last_stats
    gc.collect()

def objects_by_id(id_):
    import gc
    for obj in gc.get_objects():
        if id(obj) == id_:
            return obj
    raise Exception("No found")

take_snapshot()
print 'ok'
