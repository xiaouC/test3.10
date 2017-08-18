class NamedList(object):
    def __init__(self, *args, **kwargs):
        for idx, name in enumerate(self.__slots__):
            if idx<len(args):
                setattr(self, name, args[idx])
            else:
                setattr(self, name, kwargs.get(name))

    def items(self):
        return [(field_name, getattr(self, field_name)) for field_name in self.__slots__]

    def __iter__(self):
        "iterate over fields tuple/list style"
        for field_name in self.__slots__:
            yield getattr(self, field_name)

    def __getitem__(self, index):
        return getattr(self, self.__slots__[index])

    def __setitem__(self, index, value):
        return setattr(self, self.__slots__[index], value)

    def __repr__(self):
        return '%s(%s)'%(self.__class__.__name__, ','.join('%s=%s'%(name, getattr(self, name)) for name in self.__slots__))

def namedlist(name, fields):
    return type(name, (NamedList,), {'__slots__': fields})

if __name__ == '__main__':
    Test = namedlist('Test', ('a', 'b', 'c'))
    t = Test(1,b=2,c=3)
    print t
