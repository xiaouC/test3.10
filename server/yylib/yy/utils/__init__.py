# coding: utf-8
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from .orderedset import OrderedSet

try:
    from logging.config import dictConfig
except ImportError:
    from dictconfig import dictConfig
import os
import gc
import random
import base64
import hashlib
import binascii
import operator
import struct
import string
import itertools
from math import ceil, floor
from collections import defaultdict
from bitarray import bitarray
from yy.cutils import constant_time_compare

import warnings
try:
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    warnings.warn('A secure pseudo-random number generator is not available '
                  'on your system. Falling back to Mersenne Twister.')
    using_sysrandom = False

def profile(func, *args, **kwargs):
    import cProfile, pstats
    def _inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        ps = pstats.Stats(pr)
        ps.sort_stats('time').print_stats()
        return result
    return _inner

def singleton(cls):
    '''
    class decorator for singleton class.

    >>> @singleton
    ... class PlayerManager:
    ...     def __init__(self):
    ...         self.a = 1
    >>> PlayerManager.instance().a = 2
    >>> PlayerManager.instance().a
    2
    >>> PlayerManager.getInstance().a =1

    '''
    def _get_instance(cls):
        inst = getattr(cls, '_instance', None)
        if not inst:
            inst = cls()
            cls._instance = inst
        return inst
    setattr(cls, 'instance', classmethod(_get_instance))
    setattr(cls, 'getInstance', classmethod(_get_instance))
    
    return cls

class DictObject(dict):
    def __getattr__(self,name):
        return self.get(name)
    
    def __setattr__(self,k,v):
        self[k] = v   

def load_settings():
    import os, sys
    settings_module = os.environ.get("POEM_SETTINGS", "local_settings")
    if 'settings' in sys.modules:
        return
    settings = sys.modules['settings'] = __import__(settings_module)
    if hasattr(settings, 'LOG'):
        from . import dictConfig
        dictConfig(settings.LOG)

    # init redis
    from yy.db.redismanager import create_pool
    for k, v in settings.REDISES.items():
        settings.REDISES[k] = create_pool(v)

def reset_remote_server():
    import settings
    settings._REMOTE_SERVER = settings.REMOTE_SERVER
    settings.REMOTE_SERVER = None

def round_and_int(value):
    return int(round(value))

def floor_and_int(value):
    return int(floor(value))

def ceil_and_int(value):
    return int(ceil(value))

def guess(n):
    return random.random() < float(n)

def choice_one(seq):
    try:
        one = random.choice(seq)
    except IndexError:
        one = None
    return one

def make_weighted_random(lst, key_func):
    wtotal = sum([key_func(x) for x in lst])
    def weighted_random():
        n = random.uniform(0, wtotal)
        for item in lst:
            weight = key_func(item)
            if n < weight:
                break
            n = n - weight
        return item
    return weighted_random

def iteritems(d):
    """Return an iterator over the (key, value) pairs of a dictionary."""
    return iter(getattr(d, _iteritems)())

class SortedDict(dict):
    """
    A dictionary that keeps its keys in the order in which they're inserted.
    """
    def __new__(cls, *args, **kwargs):
        instance = super(SortedDict, cls).__new__(cls, *args, **kwargs)
        instance.keyOrder = []
        return instance

    def __init__(self, data=None):
        if data is None or isinstance(data, dict):
            data = data or []
            super(SortedDict, self).__init__(data)
            self.keyOrder = list(data) if data else []
        else:
            super(SortedDict, self).__init__()
            super_set = super(SortedDict, self).__setitem__
            for key, value in data:
                # Take the ordering from first key
                if key not in self:
                    self.keyOrder.append(key)
                # But override with last value in data (dict() does this)
                super_set(key, value)

    def __deepcopy__(self, memo):
        return self.__class__([(key, copy.deepcopy(value, memo))
                               for key, value in self.items()])

    def __copy__(self):
        # The Python's default copy implementation will alter the state
        # of self. The reason for this seems complex but is likely related to
        # subclassing dict.
        return self.copy()

    def __setitem__(self, key, value):
        if key not in self:
            self.keyOrder.append(key)
        super(SortedDict, self).__setitem__(key, value)

    def __delitem__(self, key):
        super(SortedDict, self).__delitem__(key)
        self.keyOrder.remove(key)

    def __iter__(self):
        return iter(self.keyOrder)

    def __reversed__(self):
        return reversed(self.keyOrder)

    def pop(self, k, *args):
        result = super(SortedDict, self).pop(k, *args)
        try:
            self.keyOrder.remove(k)
        except ValueError:
            # Key wasn't in the dictionary in the first place. No problem.
            pass
        return result

    def popitem(self):
        result = super(SortedDict, self).popitem()
        self.keyOrder.remove(result[0])
        return result

    def _iteritems(self):
        for key in self.keyOrder:
            yield key, self[key]

    def _iterkeys(self):
        for key in self.keyOrder:
            yield key

    def _itervalues(self):
        for key in self.keyOrder:
            yield self[key]

    iteritems = _iteritems
    iterkeys = _iterkeys
    itervalues = _itervalues

    def items(self):
        return [(k, self[k]) for k in self.keyOrder]

    def keys(self):
        return self.keyOrder[:]

    def values(self):
        return [self[k] for k in self.keyOrder]

    def update(self, dict_):
        for k, v in iteritems(dict_):
            self[k] = v

    def setdefault(self, key, default):
        if key not in self:
            self.keyOrder.append(key)
        return super(SortedDict, self).setdefault(key, default)

    def value_for_index(self, index):
        """Returns the value of the item at the given zero-based index."""
        # This, and insert() are deprecated because they cannot be implemented
        # using collections.OrderedDict (Python 2.7 and up), which we'll
        # eventually switch to
        warnings.warn(
            "SortedDict.value_for_index is deprecated", DeprecationWarning,
            stacklevel=2
        )
        return self[self.keyOrder[index]]

    def insert(self, index, key, value):
        """Inserts the key, value pair before the item with the given index."""
        warnings.warn(
            "SortedDict.insert is deprecated", DeprecationWarning,
            stacklevel=2
        )
        if key in self.keyOrder:
            n = self.keyOrder.index(key)
            del self.keyOrder[n]
            if n < index:
                index -= 1
        self.keyOrder.insert(index, key)
        super(SortedDict, self).__setitem__(key, value)

    def copy(self):
        """Returns a copy of this object."""
        # This way of initializing the copy means it works for subclasses, too.
        return self.__class__(self)

    def __repr__(self):
        """
        Replaces the normal dict.__repr__ with a version that returns the keys
        in their sorted order.
        """
        return '{%s}' % ', '.join(['%r: %r' % (k, v) for k, v in iteritems(self)])

    def clear(self):
        super(SortedDict, self).clear()
        self.keyOrder = []

#def make_password(s):
#    '生成加密密码'
#    # TODO
#    return s

_trans_5c = bytearray([(x ^ 0x5C) for x in xrange(256)])
_trans_36 = bytearray([(x ^ 0x36) for x in xrange(256)])

def _bin_to_long(x):
    """
    Convert a binary string into a long integer

    This is a clever optimization for fast xor vector math
    """
    return int(binascii.hexlify(x), 16)

def _fast_hmac(key, msg, digest):
    """
    A trimmed down version of Python's HMAC implementation.

    This function operates on bytes.
    """
    dig1, dig2 = digest(), digest()
    if len(key) > dig1.block_size:
        key = digest(key).digest()
    key += b'\x00' * (dig1.block_size - len(key))
    dig1.update(key.translate(_trans_36))
    dig1.update(msg)
    dig2.update(key.translate(_trans_5c))
    dig2.update(dig1.digest())
    return dig2

def _long_to_bin(x, hex_format_string):
    """
    Convert a long integer into a binary string.
    hex_format_string is like "%020x" for padding 10 characters.
    """
    return binascii.unhexlify((hex_format_string % x).encode('ascii'))

def force_bytes(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_bytes, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    if strings_only and (s is None or isinstance(s, int)):
        return s
    if not isinstance(s, basestring):
        try:
            return bytes(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return b' '.join([force_bytes(arg, encoding, strings_only,
                        errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    else:
        return s.encode(encoding, errors)


def pbkdf2(password, salt, iterations, dklen=0, digest=None):
    """
    Implements PBKDF2 as defined in RFC 2898, section 5.2

    HMAC+SHA256 is used as the default pseudo random function.

    Right now 10,000 iterations is the recommended default which takes
    100ms on a 2.2Ghz Core 2 Duo.  This is probably the bare minimum
    for security given 1000 iterations was recommended in 2001. This
    code is very well optimized for CPython and is only four times
    slower than openssl's implementation.
    """
    assert iterations > 0
    if not digest:
        digest = hashlib.sha256
    password = force_bytes(password)
    salt = force_bytes(salt)
    hlen = digest().digest_size
    if not dklen:
        dklen = hlen
    if dklen > (2 ** 32 - 1) * hlen:
        raise OverflowError('dklen too big')
    l = -(-dklen // hlen)
    r = dklen - (l - 1) * hlen

    hex_format_string = "%%0%ix" % (hlen * 2)

    def F(i):
        def U():
            u = salt + struct.pack(b'>I', i)
            for j in xrange(int(iterations)):
                u = _fast_hmac(password, u, digest).digest()
                yield _bin_to_long(u)
        return _long_to_bin(reduce(operator.xor, U()), hex_format_string)

    T = [F(x) for x in range(1, l + 1)]
    return b''.join(T[:-1]) + T[-1][:r]

def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """
    Returns a securely generated random string.

    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit value. log_2((26+26+10)^12) =~ 71 bits
    """
    if not using_sysrandom:
        # This is ugly, and a hack, but it makes things better than
        # the alternative of predictability. This re-seeds the PRNG
        # using a value that is hard for an attacker to predict, every
        # time a random string is required. This may change the
        # properties of the chosen random sequence slightly, but this
        # is better than absolute predictability.
        random.seed(
            hashlib.sha256(
                "%s%s%s" % (
                    random.getstate(),
                    time.time(),
                    settings.SECRET_KEY)
                ).digest())
    return ''.join([random.choice(allowed_chars) for i in range(length)])

class BasePasswordHasher(object):
    """
    Abstract base class for password hashers

    When creating your own hasher, you need to override algorithm,
    verify(), encode() and safe_summary().

    PasswordHasher objects are immutable.
    """
    algorithm = None
    library = None

    def _load_library(self):
        if self.library is not None:
            if isinstance(self.library, (tuple, list)):
                name, mod_path = self.library
            else:
                name = mod_path = self.library
            try:
                module = importlib.import_module(mod_path)
            except ImportError:
                raise ValueError("Couldn't load %s password algorithm "
                                 "library" % name)
            return module
        raise ValueError("Hasher '%s' doesn't specify a library attribute" %
                         self.__class__)

    def salt(self):
        """
        Generates a cryptographically secure nonce salt in ascii
        """
        return get_random_string()

    def verify(self, password, encoded):
        """
        Checks if the given password is correct
        """
        raise NotImplementedError()

    def encode(self, password, salt):
        """
        Creates an encoded database value

        The result is normally formatted as "algorithm$salt$hash" and
        must be fewer than 128 characters.
        """
        raise NotImplementedError()

    def safe_summary(self, encoded):
        """
        Returns a summary of safe values

        The result is a dictionary and will be used where the password field
        must be displayed to construct a safe representation of the password.
        """
        raise NotImplementedError()

def mask_hash(hash, show=6, char="*"):
    """
    Returns the given hash, with only the first ``show`` number shown. The
    rest are masked with ``char`` for security reasons.
    """
    masked = hash[:show]
    masked += char * len(hash[show:])
    return masked


class PBKDF2PasswordHasher(BasePasswordHasher):
    """
    Secure password hashing using the PBKDF2 algorithm (recommended)

    Configured to use PBKDF2 + HMAC + SHA256 with 10000 iterations.
    The result is a 64 byte binary string.  Iterations may be changed
    safely but you must rename the algorithm if you change SHA256.
    """
    algorithm = "pbkdf2_sha256"
    iterations = 10000
    digest = hashlib.sha256

    def encode(self, password, salt, iterations=None):
        assert password
        assert salt and '$' not in salt
        if not iterations:
            iterations = self.iterations
        hash = pbkdf2(password, salt, iterations, digest=self.digest)
        hash = base64.b64encode(hash).decode('ascii').strip()
        return "%s$%d$%s$%s" % (self.algorithm, iterations, salt, hash)

    def verify(self, password, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt, int(iterations))
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        return SortedDict([
            (_('algorithm'), algorithm),
            (_('iterations'), iterations),
            (_('salt'), mask_hash(salt)),
            (_('hash'), mask_hash(hash)),
        ])


class MD5PasswordHasher(BasePasswordHasher):
    """
    The Salted MD5 password hashing algorithm (not recommended)
    """
    algorithm = "md5"

    def encode(self, password, salt):
        assert password is not None
        assert salt and '$' not in salt
        hash = hashlib.md5(force_bytes(salt + password)).hexdigest()
        return "%s$%s$%s" % (self.algorithm, salt, hash)

    def verify(self, password, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt)
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        return OrderedDict([
            (_('algorithm'), algorithm),
            (_('salt'), mask_hash(salt, show=2)),
            (_('hash'), mask_hash(hash)),
        ])

old_hasher = PBKDF2PasswordHasher()
hasher = MD5PasswordHasher()


def make_password(password, salt=None):
    if password == 'dummy':
        return password
    assert password, 'password is none'
    if not salt:
        salt = hasher.salt()
    return hasher.encode(password, salt)

def check_password(password, encoded):
    if not password or encoded == 'dummy':
        return False
    return hasher.verify(password, encoded)

#def check_password(s, hashed):
#    '验证密码'
#    # TODO
#    return s==hashed

def md5_to_path(md5, f):
    ext = os.path.splitext(f)[1]
    return os.path.join(md5[:2], md5[2:]) + ext

def copyto(f, target, overwrite=False):
    import shutil
    if not overwrite and os.path.exists(target):
        return
    d = os.path.dirname(target)
    if not os.path.exists(d):
        os.makedirs(d)
    shutil.copyfile(f, target)

def file_md5_size(f):
    import md5
    c = open(f, 'rb').read()
    return md5.md5(c).hexdigest(), len(c)

def db_args(host='127.0.0.1', port=3306, user='poem', passwd='poem', name=None, autocommit=True, **kwargs):
    return host, port, user, passwd, name, autocommit

def db_conn(name):
    import umysql
    import settings
    conn = umysql.Connection()
    conn.connect(*db_args(**settings.DATABASES[name]))
    return conn

def weight_random(sequence, relative_odds, length, unique=True):
    table = [ z for x, y in zip(sequence, relative_odds) for z in [x]*y ]
    result = set()
    while len(result) < length:
        result.add(random.choice(table))
    return result

def smart_str(s):
    if isinstance(s, unicode):
        return s.encode('utf-8')
    return s

def mysql_ping(dbname=None):
    """MySQL ping"""
    from db.manager import executeSQL
    if not dbname:
        from db.manager import g_dbmanager
        for dbname, (_, _) in g_dbmanager.workers.items():
            executeSQL('SELECT 1', [dbname], db=dbname)
    else:
        executeSQL('SELECT 1', [dbname], db=dbname)


def print_traceback(sig, frame):
    logger.error('current stack:\n' + ''.join(traceback.format_stack(frame)))
    from greenlet import greenlet
    for obj in gc.get_objects():
        if isinstance(obj, greenlet):
            logger.error('greenlet stack:\n' + ''.join(traceback.format_stack(obj.gr_frame)))

def diff_snapshot(st1, st2):
    diff = {}
    keys = set(st1.keys())
    for k in st2:
        keys.add(k)
    for k in keys:
        v = st2.get(k, 0)
        d = v-st1.get(k, 0)
        if d!=0:
            diff[k] = d
    return diff

def print_snapshot(d):
    for k, v in sorted(d.items(), key=lambda (a,b):b, reverse=True):
        print k, '\t', v

def gc_snapshot():
    gc.collect()
    objs = gc.get_objects()
    stats = defaultdict(int)
    for o in objs:
        stats[str(type(o))] += 1
    return stats

last_stats = None
def take_snapshot():
    global last_stats
    stats = gc_snapshot()
    if last_stats:
        print_snapshot(diff_snapshot(last_stats, stats))
    last_stats = stats

def clean_snapshot():
    last_stats = None

def clean_dead_thread():
    from greenlet import greenlet
    from gevent import sleep
    count = 0
    for o in gc.get_objects():
        if count > 1000:
            count = 0
            sleep(0)
        if isinstance(o, greenlet):
            try:
                if o._run.im_self.closed:
                    print 'kill dead thread'
                    o.kill()
                    count += 1
            except AttributeError:
                pass

def get_maxrss():
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

def objects_by_id(id_):
    for obj in gc.get_objects():
        if id(obj) == id_:
            return obj
    raise Exception("No found")

def objects_by_type(type_):
    objs = []
    for obj in gc.get_objects():
        if type(obj) == type_:
            objs.append(obj)
    return objs

def is_instance_method(obj):
    """Checks if an object is a bound method on an instance."""
    import types
    if not isinstance(obj, types.MethodType):
        return False # Not a method
    if obj.im_self is None:
        return False # Method is not bound
    if issubclass(obj.im_class, type) or obj.im_class is types.ClassType:
        return False # Method is a classmethod
    return True

def weighted_random1(weights):
    '''
    [odd, odd...]
    return index
    '''
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i
    return i

def weighted_random2(values):
    '''
    [[val,odd],[val,odd],[val,odd]...]
    return val
    '''
    rnd = random.random() * sum([o for _,o in values])
    for v, o in values:
        rnd -= o
        if rnd <= 0:
            return v
    return v

def weighted_random2_multi(values, count=1):
    '''
    [[val,odd],[val,odd],[val,odd]...]
    return [val]
    '''
    result = []
    values = values[:]
    while count>0:
        rnd = random.random() * sum([o for _,o in values])
        for i, (v, o) in enumerate(values):
            rnd -= o
            if rnd <= 0:
                break

        result.append(v)
        values[i] = (v, 0)
        count -= 1

    return result

def weighted_random3(values, odds):
    '''
    [val,...], [odd,...]
    return val
    '''
    idx = weighted_random1(odds)
    return values[idx]

def weighted_random3_multi(values, odds, count=1):
    '''
    [val,...], [odd,...]
    return [val]
    '''
    result = []
    while count>0:
        idx = weighted_random1(odds)
        result.append(values[idx])
        odds[idx] = 0
        count -= 1
    return result

def translator(frm='', to='', delete='', keep=None):
    allchars = string.maketrans('','')
    if len(to) == 1:
        to = to * len(frm)
    trans = string.maketrans(frm, to)
    if keep is not None:
        delete = allchars.translate(allchars, keep.translate(allchars, delete))
    return lambda s:s.translate(trans, delete)

def getitem(d, k, *args):
    try:
        v = operator.getitem(d, k)
    except KeyError as e:
        if not args:
            raise e
        else:
            v = args[0]
    return v


try:
    # python2
    from urllib import unquote
    from urlparse import urlparse
    from urlparse import parse_qsl
except ImportError:
    # python3
    from urllib.parse import unquote
    from urllib.parse import urlparse
    from cgi import parse_qsl  # noqa


def _parse_url(url):
    scheme = urlparse(url).scheme
    schemeless = url[len(scheme) + 3:]
    # parse with HTTP URL semantics
    parts = urlparse('http://' + schemeless)

    # The first pymongo.Connection() argument (host) can be
    # a mongodb connection URI. If this is the case, don't
    # use port but let pymongo get the port(s) from the URI instead.
    # This enables the use of replica sets and sharding.
    # See pymongo.Connection() for more info.
    port = scheme != 'mongodb' and parts.port or None
    hostname = schemeless if scheme == 'mongodb' else parts.hostname
    path = parts.path or ''
    path = path[1:] if path and path[0] == '/' else path
    return (scheme, unquote(hostname or '') or None, port,
            unquote(parts.username or '') or None,
            unquote(parts.password or '') or None,
            unquote(path or '') or None,
            dict(parse_qsl(parts.query)))


def parse_redis_url(url):
    scheme, host, port, user, password, db, query = _parse_url(url)
    assert scheme == 'redis'
    return dict(host=host, port=port, password=password, db=db, **query)

def parse_storage_url(url):
    schema, host, port, user, password, db, query = _parse_url(url)
    return dict(schema=schema, host=host, port=port, password=password, db=db, **query)

def group_list_by_two(l):
    it = iter(l)
    return itertools.izip_longest(it, it)

def convert_list_to_dict(l, dictcls=dict):
    return dictcls(group_list_by_two(l))

def convert_dict_to_list(d):
    for k,v in d.items():
        yield k
        yield v

def gen_bitmap(entityIDs):
    assert isinstance(entityIDs, (set, list))
    max_entityID = max(entityIDs)
    ba = bitarray(((max_entityID+1+7)/8)*8)
    ba.setall(False)
    for entityID in entityIDs:
        ba[entityID] = True
    return ba.tobytes()

def iter_bitmap(bm):
    ba = bitarray()
    ba.frombytes(bm)
    for idx, v in enumerate(ba):
        if v :
            yield idx

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def execute_big_pipeline(pool, cmds):
    for chunk in chunks(cmds, 1000):
        rsps = pool.execute_pipeline(*chunk)
        for rsp in rsps:
            yield rsp

def get_rand_string(length, allowed_chars=(string.ascii_lowercase + string.digits)):
    l = []
    choice = random.choice
    for i in xrange(length):
        l.append(choice(allowed_chars))
    return ''.join(l)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    b = DictObject()
    b.a =1
    print b
    print bool(b)
