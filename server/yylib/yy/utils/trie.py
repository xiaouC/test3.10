# coding: utf-8
u'''
>>> tr = trie_create([u'法轮功', u'法轮大法'])
>>> trie_match(tr, u'法轮功大法sdf')
3
>>> trie_match(tr, u'法轮大功sdf')
-1
>>> trie_match(tr, u'法轮大法功sdf')
4
>>> trie_match(tr, u'测试法轮功sdf')
-1
>>> trie_match(tr, u'法轮')
-1
>>> trie_search(tr, u'测试法轮功测试')
(2, 3)
>>> trie_search(tr, u'法轮')
(-1, -1)
>>> trie_contains(tr, u'测试法轮功测试')
True
>>> print trie_replace(tr, u'测试法轮功测试法轮大法测试', u'*')
测试***测试****测试
'''

LEAF_KEY = '__leaf__'

def trie_empty():
    return {}

def trie_leaf():
    return {LEAF_KEY: True}

def trie_clear(tr):
    tr.clear()

def trie_add(tr, u):
    c = u[0]
    tr1 = tr.setdefault(c, trie_empty())
    u1 = u[1:]
    if u1:
        trie_add(tr1, u1)
    else:
        # leaf
        tr1[LEAF_KEY] = True

def trie_append(tr, strs):
    for s in strs:
        trie_add(tr, s)

def trie_create(strs):
    tr = trie_empty()
    trie_append(tr, strs)
    return tr

def trie_isleaf(tr):
    return LEAF_KEY in tr

def trie_match(tr, u, depth=1):
    if not tr:
        return -1
    if not u:
        return -1
    c = u[0]
    u1 = u[1:]
    if c not in tr:
        return -1
    else:
        tr1 = tr[c]
        if trie_isleaf(tr1):
            return depth
        else:
            return trie_match(tr1, u1, depth+1)

def tails(u):
    for i in range(len(u)):
        yield i, u[i:]

def trie_search(tr, u):
    for i, uu in tails(u):
        pos = trie_match(tr, uu)
        if pos>0:
            return i, pos
    return -1, -1

def trie_contains(tr, u):
    return trie_search(tr, u)[0]>=0

def _trie_replace(tr, l, rc):
    idx = 0
    maxlen = len(l)
    while idx<maxlen:
        pos = trie_match(tr, l[idx:])
        if pos>0:
            for j in range(idx, idx+pos):
                l[j] = rc
            idx += pos
        else:
            idx += 1
    return l

def trie_replace(tr, u, rc):
    return ''.join(_trie_replace(tr, list(u), rc))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
