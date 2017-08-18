# coding: utf-8
'''
属性公式上下文
>>> from entity.actor.base import PlayerBase as Player
>>> ctx = AttributeContext(Player())
>>> f = 'EntityUtils.getLevelMaxExpValue( exp, 1 )'
>>> compile(f)(ctx)
154
'''

class AttributeContext(object):
    def __init__(self, role):
        self.role = role
    def __call__(self, name):
        if name=='role':
            return self.role
        else:
            r = getattr(self.role, name)
            if r==None:
                raise Exception('attribute %s is None'%name)
            return r
