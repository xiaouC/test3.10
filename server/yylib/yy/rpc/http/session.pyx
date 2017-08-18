import time
import msgpack
import traceback
import string
import hashlib
from datetime import datetime
from exceptions import SuspiciousOperation
from yy.cutils import constant_time_compare
from yy.utils import get_rand_string as get_random_string

class CreateError(Exception):
    """
    Used internally as a consistent exception type to catch from save (see the
    docstring for SessionBase.save() for details).
    """
    pass

cdef pool_execute(pool, tuple args):
    with pool.ctx() as conn:
        return conn.execute(*args)

cdef class SessionStore(object):
    """
    Base class for all Session classes.
    """

    cdef public bint accessed
    cdef public bint modified
    cdef public int cookie_age 
    cdef public bytes secret_key
    cdef bytes _session_key_prefix
    cdef bytes _session_key
    cdef dict _session_cache
    cdef public object pool

    def __init__(self, pool, session_key=None, cookie_age=24*60*60, secret_key='', session_key_prefix='sid'):
        self._session_key = session_key
        self.cookie_age = cookie_age
        self.secret_key = secret_key
        self._session_key_prefix = session_key_prefix
        self.accessed = False
        self.modified = False
        self.pool = pool

    def __contains__(self, key):
        return key in self._get_session()

    def __getitem__(self, key):
        return self._get_session()[key]

    def __setitem__(self, key, value):
        self._get_session()[key] = value
        self.modified = True

    def __delitem__(self, key):
        del self._get_session()[key]
        self.modified = True

    cpdef get(self, key, default=None):
        return self._get_session().get(key, default)

    def pop(self, key, *args):
        self.modified = self.modified or key in self._get_session()
        return self._get_session().pop(key, *args)

    def setdefault(self, key, value):
        if key in self._get_session():
            return self._get_session()[key]
        else:
            self.modified = True
            self._get_session()[key] = value
            return value

    cdef _hash(self, value):
        return hashlib.md5(self.secret_key + value).hexdigest()

    cpdef encode(self, session_dict):
        "Returns the given session dictionary pickled and encoded as a string."
        pickled = msgpack.dumps(session_dict)
        hash = self._hash(pickled)
        return hash.encode() + b":" + pickled

    cpdef decode(self, session_data):
        encoded_data = session_data
        try:
            # could produce ValueError if there is no ':'
            hash, pickled = encoded_data.split(b':', 1)
            expected_hash = self._hash(pickled)
            if not constant_time_compare(hash, expected_hash):
                raise SuspiciousOperation("Session data corrupted")
            else:
                return msgpack.loads(pickled)
        except Exception:
            traceback.print_exc()
            # ValueError, SuspiciousOperation, unpickling exceptions. If any of
            # these happen, just return an empty dictionary (an empty session).
            return {}

    def update(self, dict_):
        self._get_session().update(dict_)
        self.modified = True

    def has_key(self, key):
        return key in self._get_session()

    def keys(self):
        return self._get_session().keys()

    def values(self):
        return self._get_session().values()

    def items(self):
        return self._get_session().items()

    def iterkeys(self):
        return self._get_session().iterkeys()

    def itervalues(self):
        return self._get_session().itervalues()

    def iteritems(self):
        return self._get_session().iteritems()

    def clear(self):
        # To avoid unnecessary persistent storage accesses, we set up the
        # internals directly (loading data wastes time, since we are going to
        # set it to an empty dict anyway).
        self._session_cache = {}
        self.accessed = True
        self.modified = True

    cdef _get_new_session_key(self):
        "Returns session key that isn't being used."
        while True:
            session_key = get_random_string(32)
            if not self.exists(session_key):
                break
        return session_key

    cdef _get_or_create_session_key(self):
        if self._session_key is None:
            self._session_key = self._get_new_session_key()
        return self._session_key

    property session_key:
        def __get__(self):
            return self._session_key

    cdef dict _get_session(self, no_load=False):
        """
        Lazily loads session from storage (unless "no_load" is True, when only
        an empty dict is stored) and stores it in the current instance.
        """
        self.accessed = True
        if self._session_cache is None:
            if no_load:
                self._session_cache = {}
            else:
                self._session_cache = self.load()
        return self._session_cache

    def flush(self):
        """
        Removes the current session data from the database and regenerates the
        key.
        """
        self.clear()
        self.delete()
        self.create()

    def cycle_key(self):
        """
        Creates a new session key, whilst retaining the current session data.
        """
        data = self._session_cache
        key = self.session_key
        self.create()
        self._session_cache = data
        self.delete(key)

    cdef get_real_stored_key(self, session_key):
        """Return the real key name in redis storage
        @return string
        """
        return ':'.join([self._session_key_prefix, session_key])

    cpdef load(self):
        key = self.get_real_stored_key(self._get_or_create_session_key())
        session_data = pool_execute(self.pool, ('GET', key))
        if session_data is not None:
            return self.decode(session_data)
        else:
            self.create()
            return {}

    cpdef exists(self, session_key):
        return pool_execute(self.pool, ('EXISTS', self.get_real_stored_key(session_key)))

    #cpdef create(self):
    #    while True:
    #        self._session_key = self._get_new_session_key()
    #        try:
    #            self.save(must_create=True)
    #        except CreateError as e:
    #            continue
    #        self.modified = True
    #        return

    cpdef create(self):
        self.save()
        self.modified = True
        return

    cpdef save(self, bint must_create=False):
        key = self._get_or_create_session_key()
        if must_create and self.exists(key):
            raise CreateError
        data = self.encode(self._get_session(no_load=True))
        real_key = self.get_real_stored_key(key)
        pool_execute(self.pool, ('SETEX',
            real_key,
            self.cookie_age,
            data
        ))

    cpdef delete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        pool_execute(self.pool, ('DEL', self.get_real_stored_key(session_key)))
